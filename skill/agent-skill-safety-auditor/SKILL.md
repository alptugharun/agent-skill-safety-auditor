---
name: agent-skill-safety-auditor
description: Audits third-party Agent Skills and installable AI-agent instructions before installation. Use when deciding whether to install, fork, adapt, or trust a skill for Claude Code, Codex, Gemini CLI, Cursor, or another Agent Skills-compatible runtime.
license: MIT
metadata:
  version: 0.1.0
  author: Alptuğ Harun
---

# Agent Skill Safety Auditor

Inspect an Agent Skill before trusting it.

A skill can instruct an agent to execute scripts, access files, call external services, or request credentials. Popularity is not proof of safety.

## Audit order

1. **Provenance** — confirm the exact repository, ref, release, owner, license and install source.
2. **Instructions** — read SKILL.md and supporting instruction files completely.
3. **Executable surface** — inspect scripts, shell commands, network calls, writes, dynamic execution and lifecycle hooks.
4. **Dependencies** — identify direct dependencies, registries and install hooks.
5. **Permission fit** — ask whether filesystem, shell, network, credential, browser or MCP access is necessary for the advertised job.
6. **License and reuse** — verify redistribution and modification rights.

## Flag for review

Pay special attention to:

- curl/wget or PowerShell downloaders that execute remote content;
- eval, exec, encoded payloads or obfuscated commands;
- recursive delete or overwrite operations;
- writes outside the documented project/config directory;
- subprocess or shell execution;
- package install hooks;
- unexpected network destinations;
- environment-variable or credential reads;
- browser cookies, SSH keys or unrelated account data;
- instructions that disable validation or hide actions.

Do not execute suspicious code merely to learn what it does.

## Risk labels

- **LOW** — narrow, inspectable behavior and no unexplained executable surface.
- **MODERATE** — scripts, network, environment access or dependencies exist and need contextual review.
- **HIGH** — broad privileges, unsafe install patterns, destructive behavior or opaque execution.
- **BLOCK** — use only for concrete critical evidence such as confirmed credential exfiltration or malicious persistence.

Explain the evidence behind the label. Do not call a project malicious from a regex match or reputation signal alone.

## Output

Return:

- audited repository/ref;
- risk label and confidence;
- findings table with file, line/evidence, why it matters and safer action;
- permissions required;
- license/reuse notes;
- a safe installation plan when installation is reasonable.

## Core principle

**Inspect first. Grant the minimum. Execute only what you understand.**
