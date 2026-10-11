# Security Policy

Agent Skill Safety Auditor is an offline static scanner. It inspects local Agent Skill files for evidence of powerful or risky behavior.

## Security boundary

Potential vulnerabilities include, for example:

- the auditor executing or importing untrusted target code while scanning;
- unexpected network access;
- credential/private-file access;
- path traversal outside the target;
- unsafe temporary-file handling;
- malicious output injection that becomes executable;
- a bypass that hides a documented HIGH-risk pattern;
- dependency/release compromise.

A false positive or false negative is normally a quality bug unless it creates a concrete security impact.

## Private vulnerability reporting

Do **not** publish exploit details, credentials, private skill contents or sensitive paths in a normal issue.

Use GitHub Private Vulnerability Reporting:

https://github.com/alptugharun/agent-skill-safety-auditor/security/advisories/new

Please include:

- affected version/commit;
- OS and Python version;
- minimal synthetic reproducer when possible;
- expected vs actual behavior;
- security impact;
- sanitized output/logs;
- suggested mitigation if known.

## Coordinated disclosure

The maintainer aims to acknowledge a private vulnerability report within **7 days**.

For confirmed vulnerabilities, coordinated disclosure after a fix/mitigation is preferred. A **90-day** remediation/disclosure target is a goal for ordinary cases, not a guarantee; severity and coordination may change the timeline.

Please avoid public disclosure of an unpatched vulnerability before coordination unless there is an overriding safety reason.

## Important limitation

A clean static scan is **not** a security certification.

This project cannot prove that a remote service, dependency or runtime will not change behavior after installation. Runtime monitoring, network controls, sandboxing and least privilege remain separate defenses.

## Maintainer rule

Security fixes should add regression coverage when practical and must not weaken a check merely to improve a score.
