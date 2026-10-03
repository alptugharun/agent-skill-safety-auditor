# Contributing

Focused improvements are welcome.

Useful contributions include:

- a reproducible false positive or false negative;
- a new narrowly defined detection pattern;
- parser hardening;
- safer report wording;
- tests for an Agent Skill layout seen in the wild;
- documentation corrections.

Before a PR:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Do not add a rule that calls a project malicious based only on popularity, authorship, keywords, or one ambiguous line. Findings should describe observable behavior and leave room for context.
