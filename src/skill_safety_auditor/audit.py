from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re

TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".ps1",
    ".json", ".toml", ".yml", ".yaml", ".ini", ".cfg"
}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
MAX_FILE_BYTES = 1_000_000

SEVERITY_ORDER = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "BLOCK": 3}

@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    evidence: str
    explanation: str

@dataclass
class AuditReport:
    root: str
    risk: str
    skill_name: str | None
    description_present: bool
    license_present: bool
    files_scanned: int
    findings: list[Finding]

    def to_json(self) -> str:
        return json.dumps(
            {
                **asdict(self),
                "findings": [asdict(item) for item in self.findings],
            },
            ensure_ascii=False,
            indent=2,
        )

    def to_markdown(self) -> str:
        lines = [
            "# Agent Skill Safety Audit",
            "",
            f"- **Risk:** {self.risk}",
            f"- **Skill:** {self.skill_name or 'unknown'}",
            f"- **Files scanned:** {self.files_scanned}",
            f"- **Description present:** {'yes' if self.description_present else 'no'}",
            f"- **License present:** {'yes' if self.license_present else 'no'}",
            "",
            "## Findings",
            "",
        ]
        if not self.findings:
            lines.append("No heuristic findings were detected. This is not a guarantee of safety.")
        else:
            lines.extend([
                "| Severity | File | Line | Finding | Evidence |",
                "| --- | --- | ---: | --- | --- |",
            ])
            for item in self.findings:
                evidence = item.evidence.replace("|", "\\|")
                lines.append(
                    f"| {item.severity} | `{item.path}` | {item.line} | "
                    f"{item.explanation} | `{evidence}` |"
                )
        lines.extend([
            "",
            "## Interpretation",
            "",
            "This report is a static heuristic review. Inspect flagged files in context before deciding whether to install or run a skill.",
            "Popularity, stars, author reputation, or a clean scan are not security guarantees.",
        ])
        return "\n".join(lines) + "\n"


PATTERNS: tuple[tuple[str, str, re.Pattern[str], str], ...] = (
    (
        "HIGH",
        "remote-pipe-shell",
        re.compile(r"(?:curl|wget)\b.{0,160}\|\s*(?:sh|bash|zsh)\b", re.I),
        "Remote content appears to be piped directly into a shell.",
    ),
    (
        "HIGH",
        "powershell-remote-exec",
        re.compile(
            r"(?:Invoke-WebRequest|Invoke-RestMethod|\biwr\b|\birm\b).{0,180}"
            r"(?:Invoke-Expression|\biex\b)",
            re.I,
        ),
        "Downloaded content appears to be passed to PowerShell expression execution.",
    ),
    (
        "HIGH",
        "credential-path",
        re.compile(r"(?:\.ssh[\\/]|id_rsa\b|id_ed25519\b|(?:AppData|Library).{0,100}(?:Login Data|Cookies))", re.I),
        "The file references a sensitive credential or browser-data location.",
    ),
    (
        "HIGH",
        "destructive-recursive-delete",
        re.compile(
            r"(?:rm\s+-rf\b|Remove-Item\b.{0,100}-Recurse.{0,100}-Force|"
            r"shutil\.rmtree\s*\(|\bdel\s+/s\s+/q\b)",
            re.I,
        ),
        "The file contains a recursive destructive-delete pattern.",
    ),
    (
        "HIGH",
        "dynamic-code-execution",
        re.compile(r"(?:\beval\s*\(|\bexec\s*\(|Invoke-Expression|\biex\b)", re.I),
        "Dynamic code or expression execution is present and needs manual review.",
    ),
    (
        "MODERATE",
        "shell-or-process",
        re.compile(
            r"(?:subprocess\.|os\.system\s*\(|shell\s*=\s*True|"
            r"child_process|execFile\s*\(|spawn\s*\()",
            re.I,
        ),
        "The skill can start local processes or shell commands.",
    ),
    (
        "MODERATE",
        "network-access",
        re.compile(
            r"(?:requests\.|httpx\.|urllib\.request|\bfetch\s*\(|axios\.|"
            r"Invoke-RestMethod\s+|Invoke-WebRequest\s+|\bcurl\s+(?:-|https?://)|\bwget\s+(?:-|https?://))",
            re.I,
        ),
        "Network access is present and should match the advertised job.",
    ),
    (
        "MODERATE",
        "environment-read",
        re.compile(r"(?:os\.environ|os\.getenv\s*\(|process\.env|\$env:)", re.I),
        "Environment-variable access is present; verify which values are required.",
    ),
    (
        "MODERATE",
        "encoded-payload",
        re.compile(r"(?:base64\.(?:b64decode|decodebytes)|atob\s*\()", re.I),
        "Encoded data is decoded at runtime and should be inspected in context.",
    ),
)

def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data

def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md":
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path

def _finding(severity: str, code: str, path: Path, root: Path, line: int, evidence: str, explanation: str):
    return Finding(
        severity=severity,
        code=code,
        path=path.relative_to(root).as_posix(),
        line=line,
        evidence=" ".join(evidence.strip().split())[:220],
        explanation=explanation,
    )

def audit_directory(root: Path) -> AuditReport:
    root = root.resolve()
    skill_file = root / "SKILL.md"
    findings: list[Finding] = []
    skill_name = None
    description_present = False
    license_present = False

    if not skill_file.is_file():
        findings.append(
            Finding(
                severity="MODERATE",
                code="missing-skill-file",
                path="SKILL.md",
                line=1,
                evidence="SKILL.md not found",
                explanation="A standalone Agent Skill should expose an inspectable SKILL.md entry point.",
            )
        )
    else:
        skill_text = skill_file.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(skill_text)
        skill_name = meta.get("name") or None
        description_present = bool(meta.get("description"))
        license_present = bool(meta.get("license"))
        if not skill_name:
            findings.append(
                Finding("MODERATE", "missing-name", "SKILL.md", 1, "name missing", "Frontmatter is missing a skill name.")
            )
        if not description_present:
            findings.append(
                Finding(
                    "MODERATE",
                    "missing-description",
                    "SKILL.md",
                    1,
                    "description missing",
                    "Frontmatter is missing a description of what the skill does and when to use it.",
                )
            )
        if not license_present:
            findings.append(
                Finding(
                    "MODERATE",
                    "missing-license",
                    "SKILL.md",
                    1,
                    "license missing",
                    "No license field was found in SKILL.md frontmatter; reuse rights may be unclear.",
                )
            )

    files_scanned = 0
    for path in iter_text_files(root):
        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for severity, code, pattern, explanation in PATTERNS:
                if pattern.search(line):
                    findings.append(
                        _finding(severity, code, path, root, line_no, line, explanation)
                    )

    package_json = root / "package.json"
    if package_json.is_file():
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
            scripts = payload.get("scripts") if isinstance(payload, dict) else None
            if isinstance(scripts, dict):
                for name in ("preinstall", "install", "postinstall", "prepare"):
                    if name in scripts:
                        findings.append(
                            Finding(
                                "MODERATE",
                                "package-lifecycle-hook",
                                "package.json",
                                1,
                                f"{name}: {scripts[name]}",
                                "A package lifecycle hook executes automatically during common install flows.",
                            )
                        )
        except (OSError, json.JSONDecodeError):
            findings.append(
                Finding(
                    "MODERATE",
                    "invalid-package-json",
                    "package.json",
                    1,
                    "package.json could not be parsed",
                    "Dependency and lifecycle-hook review is incomplete until the manifest parses.",
                )
            )

    risk = "LOW"
    for item in findings:
        if SEVERITY_ORDER[item.severity] > SEVERITY_ORDER[risk]:
            risk = item.severity

    return AuditReport(
        root=str(root),
        risk=risk,
        skill_name=skill_name,
        description_present=description_present,
        license_present=license_present,
        files_scanned=files_scanned,
        findings=findings,
    )
