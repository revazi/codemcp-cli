# Contributing to codemcp-cli

Thank you for contributing to `codemcp-cli`. Changes should preserve its typed interfaces, lazy MCP lifecycle, and sandbox boundary.

[`yolonir`](https://github.com/yolonir) created [`pi-codemcp`](https://github.com/yolonir/pi-codemcp) and its internal sidecar. While working from that codebase, [Revaz Zakalashvili](https://github.com/revazi) rewrote the sidecar as this CLI and extracted it for use outside the Pi coding agent. The canonical project has not adopted this package; changes should preserve the possibility of a future integration without describing that integration as current behavior.

## Development setup

Requirements:

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)

Clone the repository and create the locked development environment:

```bash
uv sync --locked --all-groups
```

Run the complete local check before opening a pull request:

```bash
just check
```

This checks the lockfile, formatting, linting, mypy and ty, tests and coverage, and built package contents and metadata.

## Making changes

- Source code belongs under `src/codemcp_cli`.
- Python tests belong under `tests/python`.
- Fixture MCP servers belong under `tests/fixtures`.
- Keep the public executable named `codemcp-cli`.
- Keep the Python import package named `codemcp_cli`.
- Prefer focused changes with tests that demonstrate the expected behavior.
- Keep public models strict and typed.

Use Ruff for safe formatting and automatic fixes:

```bash
just format
```

Run a focused test while developing, then run the full check:

```bash
uv run pytest tests/python/test_executor.py -q
just check
```

## Security boundaries

Agent-authored code must remain inside Pydantic Monty's sandbox. Do not expose raw subprocess, filesystem, environment, or network access to sandboxed execution.

Keep MCP transports, OAuth, and remote MCP behavior in FastMCP. Validate tool arguments and declared structured results at runtime, and preserve execution timeout, memory, call-count, recursion-depth, and result-size limits.

Changes affecting the sandbox, authentication, environment forwarding, file permissions, or remote transports need explicit security-focused tests.

## Dependency changes

Use uv and commit the resulting `uv.lock` update. Do not switch dependency tooling.

Add dependencies to the narrowest applicable group:

- Runtime requirements: `[project].dependencies`
- Lint and type-check tools: `lint`
- Test and coverage tools: `test`
- Distribution validation tools: `package`
- General local tooling: `dev`

After changing dependencies, run:

```bash
uv lock
just check
```

Avoid adding a runtime dependency when the standard library or an existing dependency is sufficient.

## Package changes

The distribution and executable use a hyphen, while Python imports use an underscore:

- Distribution: `codemcp-cli`
- Executable: `codemcp-cli`
- Import package: `codemcp_cli`

For packaging changes, verify the wheel and source distribution locally:

```bash
just package-check
```

The wheel must include `py.typed`, expose only the intended `codemcp_cli` package, and install the `codemcp-cli` command.

## Commits and pull requests

Use concise imperative commit subjects. Conventional Commit prefixes are encouraged, for example:

```text
feat: add saved-chain inspection
fix: preserve declared string outputs
ci: validate installed wheel
```

A pull request should:

1. Explain the problem and chosen approach.
2. Include or update tests for behavior changes.
3. Update documentation for public CLI, API, configuration, or path changes.
4. Include `uv.lock` when dependencies change.
5. Pass all required GitHub Actions checks.
6. Call out breaking changes, migrations, and security implications.

Do not publish a release or rewrite repository history as part of a contribution unless the maintainer explicitly requests it.

## Reporting security issues

Do not disclose exploitable sandbox, authentication, or secret-handling issues in a public issue. Use GitHub's private vulnerability reporting for the repository when available, or contact the maintainer privately before sharing details publicly.
