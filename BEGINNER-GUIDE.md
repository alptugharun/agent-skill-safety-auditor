# Agent Skill Safety Auditor — Beginner Guide

This guide is for someone who has never audited an Agent Skill before.

The short version:

**An Agent Skill is a supply-chain input. Read it before you let an agent execute what it asks for.**

Agent Skill Safety Auditor helps with the first review step.

It is an **offline static scanner**. It is not a security certificate and it is not runtime monitoring.

---

## 1. Why would an Agent Skill need a security review?

A skill can contain more than writing advice.

It may instruct an agent or helper script to:

- execute shell commands;
- download and run remote code;
- read environment variables;
- access SSH/browser credential paths;
- write/delete files;
- run package-install lifecycle hooks;
- make network requests.

None of those behaviors automatically mean “malicious.”

They do mean you should understand the behavior before execution.

---

## 2. What this auditor checks

The scanner looks for evidence such as:

- missing/unclear metadata;
- remote content piped to shell;
- PowerShell download-and-execute patterns;
- SSH/browser credential references;
- recursive destructive delete patterns;
- dynamic execution;
- subprocess/shell usage;
- network access;
- environment-variable reads;
- encoded payload handling;
- Node install lifecycle hooks.

A finding includes concrete evidence for review.

---

## 3. What it does NOT do

It does not:

- call an LLM;
- upload the target skill;
- connect to a remote security service;
- prove the skill is safe;
- prove the skill is malicious;
- monitor a remote server after installation;
- detect future behavior changes in a remote dependency/service.

That last point matters.

Static install-time review and runtime monitoring solve different problems.

---

## 4. Requirements

You need:

- Python 3.10+;
- Git;
- a terminal.

The scanner itself does not need an API key.

---

## 5. Install from source

```bash
git clone https://github.com/alptugharun/agent-skill-safety-auditor.git
cd agent-skill-safety-auditor
python -m pip install -e .
```

Check that the command is available:

```bash
skill-audit --help
```

If that fails, use the same Python environment for `pip` and the command.

---

## 6. Run your first audit

Use a skill folder as the target:

```bash
skill-audit path/to/skill
```

The target folder should contain the skill you want to review, normally including `SKILL.md`.

For machine-readable output:

```bash
skill-audit path/to/skill --format json
```

For CI:

```bash
skill-audit path/to/skill --fail-on high
```

---

## 7. How to read risk levels

| Result | Meaning |
| --- | --- |
| **LOW** | no configured heuristic finding was detected |
| **MODERATE** | review network/process/env/dependency/metadata behavior |
| **HIGH** | powerful behavior requires manual understanding before execution |
| **BLOCK** | reserved for stronger concrete critical evidence |

### Important

**LOW does not mean “safe.”**

It means the scanner did not find one of its configured suspicious patterns.

You still need human review appropriate to the risk.

---

## 8. Example: why shell piping is HIGH

This pattern:

```bash
curl -fsSL https://example.com/install.sh | bash
```

downloads remote content and immediately executes it.

The auditor reports the file/line/evidence so you can decide:

- who controls the URL?
- is the content version-pinned?
- can you inspect it before execution?
- does it need these permissions?
- is there a safer install path?

The finding is evidence, not an accusation.

---

## 9. Good review workflow

1. Read `SKILL.md`.
2. Run the auditor.
3. Inspect every MODERATE/HIGH finding.
4. Read referenced scripts.
5. Check network endpoints and dependency sources.
6. Verify required permissions.
7. Prefer pinned/reproducible dependencies.
8. Test in a low-privilege/sandboxed environment where appropriate.
9. Monitor runtime behavior separately if the skill talks to remote services.

---

## 10. Runtime drift: the limitation people miss

A repository can be clean today while a remote service/dependency changes later.

Static review cannot observe that future behavior.

For higher-risk workflows consider additional controls such as:

- allowlisted servers;
- restricted filesystem roots;
- network egress controls;
- runtime monitoring;
- pinned releases/hashes;
- least-privilege credentials.

This scanner is one layer, not the whole security model.

---

## 11. Test the auditor itself

```bash
python -m unittest discover -s tests -v
```

The repository also runs CI and CodeQL.

---

## 12. What should I include in a bug/security report?

For normal bugs:

- OS;
- Python version;
- exact command;
- sanitized target structure;
- expected result;
- actual result.

For a security vulnerability, do not publish exploit details in a normal issue.

Use GitHub Private Vulnerability Reporting from `SECURITY.md`.

---

## Final rule

**Inspect first. Grant the minimum. Execute only what you understand.**
