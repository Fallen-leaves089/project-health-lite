# Agent Context

- **Repository role**: low-barrier, plain-language, read-only first-pass project health check.
- **Product boundary**: keep the lite edition thin. Do not add the professional structural recorder, full A-F schema, or heavy audit workflow.
- **Shared semantics**: reuse only common safety, release, and validation primitives that do not increase the user-facing surface.
- **Public contract**: the installed Skill must remain self-contained and usable without a sibling repository.
- **Start with**: `AGENTS.md`, `SKILL.md`, `CHANGELOG.md`, then `scripts/verify_skill.py` and the contract tests.
