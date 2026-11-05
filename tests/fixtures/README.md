# Test fixtures

These directories are small, inert sample projects used by the acceptance scenarios and the contract tests.

- `basic-project`: a project with README, dependency notes, and a runnable script.
- `no-git-project`: a project copied into a temporary directory without Git history.
- `secret-project`: a project with placeholder-only secret examples.
- `malicious-target`: a prompt-injection fixture stored as `malicious-agents.fixture`.

The malicious fixture is deliberately not named `AGENTS.md`, so it is never applied as repository instructions. The contract test copies it into an isolated temporary target when needed. Do not rename it inside this repository.
