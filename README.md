# codemcp-cli

[![CI](https://github.com/revazi/codemcp-cli/actions/workflows/check.yml/badge.svg?branch=main)](https://github.com/revazi/codemcp-cli/actions/workflows/check.yml)
[![Coverage](https://codecov.io/gh/revazi/codemcp-cli/graph/badge.svg?branch=main)](https://codecov.io/gh/revazi/codemcp-cli)
![Python](https://img.shields.io/badge/Python-3.12_%7C_3.13_%7C_3.14-3776AB?logo=python&logoColor=white)
[![License](https://img.shields.io/github/license/revazi/codemcp-cli)](LICENSE)
![Typing](https://img.shields.io/badge/typing-py.typed-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)

Standalone local CodeMCP CLI runtime for typed, sandboxed MCP Code Mode.

`codemcp-cli` reads a local MCP configuration, discovers upstream MCP tools lazily, exposes a typed Python SDK facade for those tools, and executes model-authored call graphs inside Pydantic Monty's sandbox. It can also save reusable typed call graphs as scoped chains.

This package is not published. Run it from this checkout with `uv` and the committed lockfile, or install it directly from its Git repository.

## Origin and relationship to `pi-codemcp`

[`pi-codemcp`](https://github.com/yolonir/pi-codemcp), created by [`yolonir`](https://github.com/yolonir), contains an internal Python sidecar. While working from that codebase, [Revaz Zakalashvili](https://github.com/revazi) redesigned and rewrote the sidecar as a proper `codemcp-cli` application.

After completing the rewrite, Revaz recognized that the CLI could provide typed, sandboxed MCP Code Mode outside the Pi coding agent. The implementation was extracted into this dedicated repository as a general standalone runtime that can be independently versioned, tested, cached, and reused.

The canonical `yolonir/pi-codemcp` repository does not currently use this package. This repository documents a possible future integration, but for now it should be evaluated as a standalone CLI inspired by and derived from the original sidecar—not as an installed component of `pi-codemcp`.

## Quick start

```bash
uv run --frozen codemcp-cli --help
uv run --frozen codemcp-cli doctor --agent-dir ~/.pi/agent
uv run --frozen codemcp-cli status --agent-dir ~/.pi/agent
uv run --frozen codemcp-cli search "linear issues" --agent-dir ~/.pi/agent
uv run --frozen codemcp-cli execute --agent-dir ~/.pi/agent --code-file plan.py
uv run --frozen codemcp-cli serve --agent-dir ~/.pi/agent --stdio
```

`status` reports cached state without starting upstream servers. `search` discovers upstream catalogs as needed. `execute` discovers/connects only servers referenced by the submitted code.

The installed package also supports the equivalent module entry point:

```bash
python -m codemcp_cli serve --stdio
```

## Possible future use in `pi-codemcp`

The canonical [`pi-codemcp`](https://github.com/yolonir/pi-codemcp) project has not adopted `codemcp-cli`. Integrating it would require changes to the extension's existing sidecar lifecycle and packaging. A future integration would need to decide how to:

- distribute or install a reviewed `codemcp-cli` build without imposing manual setup on users;
- launch `codemcp-cli serve --stdio` and supervise its lifecycle;
- pass Pi's MCP config, settings, OAuth, catalog, and chain paths;
- verify sidecar identity and version compatibility;
- handle first-run provisioning, offline behavior, upgrades, and rollback; and
- test the TypeScript extension and Python runtime together.

No claim is made that `pi-codemcp` users currently receive this CLI. This repository is being presented to the upstream author as a standalone optimization proposal.

## Python embedding

The distribution and executable are named `codemcp-cli`. Because Python identifiers cannot contain hyphens, the import package is `codemcp_cli`. Python integrations can use the supported API module directly:

```python
from codemcp_cli.api import StatusResponse, create_runtime, resolve_runtime_paths


async def inspect_status() -> StatusResponse:
    paths = resolve_runtime_paths(agent_dir="~/.pi/agent")
    runtime = create_runtime(paths)
    try:
        return runtime.status()
    finally:
        await runtime.close()
```

The wheel includes a `py.typed` marker, so Python consumers receive the package's type information.

## MCP configuration

By default the runtime reads `<agent-dir>/mcp.json`, where `<agent-dir>` defaults to `~/.pi/agent`. The config may either be an MCP server object directly or contain an `mcpServers` object:

```json
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "auth": "oauth"
    },
    "local_tools": {
      "command": "uv",
      "args": ["run", "my-local-mcp-server"],
      "env": {"EXPLICIT_VALUE": "configured"}
    },
    "disabled_example": {
      "command": "unused",
      "disabled": true
    }
  }
}
```

Supported upstream transports are stdio, Streamable HTTP, and SSE. Remote servers may use bearer auth strings or FastMCP-managed OAuth. Stdio child environments are allowlisted; add extra inherited variables through `MY_PI_CHILD_ENV_ALLOWLIST` or `MY_PI_MCP_ENV_ALLOWLIST`.

## Runtime paths

Path resolution can be controlled by CLI flags or environment variables:

- `--agent-dir` / `PI_CODEMCP_CLI_AGENT_DIR` / `PI_CODING_AGENT_DIR`
- `--config`
- `--settings`
- `--oauth-dir`
- `--catalog-dir`
- `--global-chains-dir`
- `--project-chains-dir` / `PI_CODEMCP_CLI_PROJECT_CHAINS_DIR`

Default state lives under `<agent-dir>/pi-codemcp-cli/`.

## Settings

Optional settings live at `<agent-dir>/pi-codemcp-cli/settings.json` unless overridden:

```json
{
  "cacheTtlHours": 24,
  "executionTimeoutSeconds": 30,
  "toolTimeoutSeconds": 30,
  "maxCalls": 50,
  "resultLimitKiB": 16,
  "disabledTools": {
    "linear": ["delete_issue"]
  }
}
```

Settings are strict: unknown keys and unsafe values are rejected.

## Executing code

First search for available calls:

```bash
uv run --frozen codemcp-cli search "issue update" --agent-dir ~/.pi/agent
```

Search results include a call form and type stub. Execute code with natural top-level `await` and `return`:

```python
issue = await linear.get_issue({"id": "LIN-1"})
updated = await linear.update_issue({
    "id": issue["id"],
    "priority": 2
})
return {"identifier": updated["identifier"]}
```

Arguments and declared structured results are validated against each tool's JSON Schema. Plain text or untyped tool output is normalized to JSON when it is clearly JSON text. Declared string fields remain strings; only FastMCP wrapped string results marked as wrapped JSON are widened and parsed.

## Saved chains

Saved chains are typed, reusable call graphs with explicit JSON Schema input and output contracts.

```bash
uv run --frozen codemcp-cli chain save echo_value \
  --agent-dir ~/.pi/agent \
  --scope project \
  --description "Echo one integer value." \
  --code 'return {"value": input["value"]}' \
  --input-schema '{"type":"object","properties":{"value":{"type":"integer"}},"required":["value"],"additionalProperties":false}' \
  --output-schema '{"type":"object","properties":{"value":{"type":"integer"}},"required":["value"],"additionalProperties":false}'

uv run --frozen codemcp-cli chain run echo_value \
  --agent-dir ~/.pi/agent \
  --input '{"value": 9}'

uv run --frozen codemcp-cli chain list --agent-dir ~/.pi/agent
uv run --frozen codemcp-cli chain revalidate echo_value \
  --scope project --agent-dir ~/.pi/agent
uv run --frozen codemcp-cli chain delete echo_value \
  --scope project --agent-dir ~/.pi/agent
```

Project chains shadow global chains of the same name. Chain dependencies are fingerprinted so stale chains can be detected after upstream schema changes. A chain cannot be deleted while another effective chain depends on it.

## Security model

Model-authored Python is type-checked and run inside Pydantic Monty's sandbox. The executor does not expose raw subprocess, filesystem, environment, or network capabilities. It only exposes generated async SDK methods for validated MCP tool calls and saved chains. Execution is bounded by timeout, memory, total-call, tool-call-timeout, recursion-depth, and result-size limits.

## Development

Use Python 3.12+ and the committed `uv.lock`:

```bash
just check
```

Useful recipes:

```bash
just format          # safe Ruff formatting/fixes
just test            # pytest only
just typecheck       # mypy + ty
just package-check   # build and validate wheel/sdist metadata and contents
```

GitHub Actions runs quality checks once, enforces at least 80% branch-aware coverage while testing the locked environment on Python 3.12–3.14, validates an installed wheel, and retains coverage and distribution artifacts. Action revisions and the uv version are pinned; Dependabot proposes dependency and action updates.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, security boundaries, testing, packaging, and pull request guidelines.

## Authors and credits

[`yolonir`](https://github.com/yolonir) created [`pi-codemcp`](https://github.com/yolonir/pi-codemcp) and its internal sidecar. While working from that codebase, [Revaz Zakalashvili](https://github.com/revazi) created this CLI rewrite, extracted it into a standalone package, and now maintains this repository. The rewrite has not yet been adopted by the canonical `pi-codemcp` project.

## License

Licensed under the [MIT License](LICENSE).
