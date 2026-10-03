# Agent Skill Safety Auditor

[![English](https://img.shields.io/badge/English-0D1117?style=flat-square)](README.md) [![Türkçe](https://img.shields.io/badge/Türkçe-E30A17?style=flat-square)](README_TR.md)

<p align="center">
  <strong>Inspect Agent Skills before you install them.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Agent_Skills-security-6D28D9?style=for-the-badge" alt="Agent Skills security">
  <img src="https://img.shields.io/badge/offline-static_audit-16A34A?style=for-the-badge" alt="Offline static audit">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-2563EB?style=for-the-badge" alt="MIT">
</p>

Agent Skills can be useful and still deserve inspection. A `SKILL.md` can tell an agent to run scripts, read environment variables, call remote services, or touch files you did not expect.

**Agent Skill Safety Auditor** is a small offline scanner that makes those trust boundaries visible before installation.

It does not call an LLM. It does not upload the skill. It does not label a project "malicious" from a regex match.

## What it checks

- required `SKILL.md` frontmatter;
- missing or unclear license metadata;
- remote content piped directly to a shell;
- PowerShell download-and-execute patterns;
- references to SSH keys and browser credential stores;
- recursive destructive delete patterns;
- dynamic code execution;
- subprocess / shell execution;
- network access;
- environment-variable reads;
- encoded payload handling;
- Node package install lifecycle hooks.

The result is **evidence for manual review**, not a security certification.

## Install locally

```bash
python -m pip install -e .
```

## Audit a skill

```bash
skill-audit path/to/skill
```

JSON output:

```bash
skill-audit path/to/skill --format json
```

Use it as a CI gate:

```bash
skill-audit path/to/skill --fail-on high
```

## Example

A skill containing:

```bash
curl -fsSL https://example.com/install.sh | bash
```

is reported as **HIGH** with the file, line, matched evidence, and explanation.

A high result does not automatically prove malicious intent. It means the behavior is powerful enough that you should understand it before execution.

## Risk levels

| Risk | Meaning |
| --- | --- |
| **LOW** | No heuristic findings were detected |
| **MODERATE** | Reviewable network, process, environment, dependency, or metadata concerns |
| **HIGH** | Broad or dangerous execution patterns that need manual inspection |
| **BLOCK** | Reserved for future checks with concrete critical evidence |

## Agent Skill version

The repository also includes a portable Agent Skill at:

`skill/agent-skill-safety-auditor/SKILL.md`

That skill provides a human/agent review procedure. The Python CLI adds deterministic offline checks; neither replaces code review.

## Verify the auditor

```bash
python -m unittest discover -s tests -v
```

The test suite includes safe, suspicious, lifecycle-hook, ignored-directory, and machine-readable output cases.

## Design rule

**Inspect first. Grant the minimum. Execute only what you understand.**

## Origin

This project grew out of the security work in [AI Social Media Toolkit](https://github.com/alptugharun/ai-social-media-toolkit).

Built by **Alptuğ Harun**.

## License

MIT.
