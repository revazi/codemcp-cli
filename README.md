# codemcp

Standalone local CodeMCP CLI/runtime for typed, sandboxed MCP Code Mode.

`codemcp` reads a local MCP configuration, discovers upstream MCP tools lazily, exposes a typed Python SDK facade for those tools, and executes model-authored call graphs inside Pydantic Monty's sandbox. It can also save reusable typed call graphs as scoped chains.

This package is not published. Run it from this checkout with `uv` and the committed lockfile, or install it directly from its Git repository.

## Quick start

```bash
uv run --frozen codemcp --help
uv run --frozen codemcp doctor --agent-dir ~/.pi/agent
uv run --frozen codemcp status --agent-dir ~/.pi/agent
uv run --frozen codemcp search "linear issues" --agent-dir ~/.pi/agent
uv run --frozen codemcp execute --agent-dir ~/.pi/agent --code-file plan.py
uv run --frozen codemcp serve --agent-dir ~/.pi/agent --stdio
```

`status` reports cached state without starting upstream servers. `search` discovers upstream catalogs as needed. `execute` discovers/connects only servers referenced by the submitted code.

The installed package also supports the equivalent module entry point:

```bash
python -m codemcp serve --stdio
```

## Using this repository from `pi-codemcp`

The repository name may be `codemcp-cli`; its Python distribution and import package remain `codemcp`, and its stable executable remains `codemcp`.

For a Python `pi-codemcp` project managed by uv, use a tagged Git dependency:

```toml
[project]
dependencies = ["codemcp"]

[tool.uv.sources]
codemcp = { git = "https://github.com/your-org/codemcp-cli.git", tag = "v0.1.0" }
```

During local development, point uv at a sibling checkout instead:

```toml
[tool.uv.sources]
codemcp = { path = "../codemcp-cli", editable = true }
```

Python integrations should use the supported API module rather than internal modules:

```python
from codemcp.api import StatusResponse, create_runtime, resolve_runtime_paths


async def inspect_status() -> StatusResponse:
    paths = resolve_runtime_paths(agent_dir="~/.pi/agent")
    runtime = create_runtime(paths)
    try:
        return runtime.status()
    finally:
        await runtime.close()
```

If `pi-codemcp` is a TypeScript/JavaScript extension, it cannot directly import the Python package. Install or resolve the `codemcp` executable and run it as an MCP stdio sidecar:

```bash
uvx --from git+https://github.com/your-org/codemcp-cli.git@v0.1.0 \
  codemcp serve --stdio --agent-dir ~/.pi/agent
```

Pin integrations to a release tag or commit instead of a moving branch. The wheel includes a `py.typed` marker, so Python consumers receive the package's type information.

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

- `--agent-dir` / `PI_CODEMCP_AGENT_DIR` / `PI_CODING_AGENT_DIR`
- `--config`
- `--settings`
- `--oauth-dir`
- `--catalog-dir`
- `--global-chains-dir`
- `--project-chains-dir` / `PI_CODEMCP_PROJECT_CHAINS_DIR`

Default state lives under `<agent-dir>/pi-codemcp/`.

## Settings

Optional settings live at `<agent-dir>/pi-codemcp/settings.json` unless overridden:

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
uv run --frozen codemcp search "issue update" --agent-dir ~/.pi/agent
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
uv run --frozen codemcp chain save echo_value \
  --agent-dir ~/.pi/agent \
  --scope project \
  --description "Echo one integer value." \
  --code 'return {"value": input["value"]}' \
  --input-schema '{"type":"object","properties":{"value":{"type":"integer"}},"required":["value"],"additionalProperties":false}' \
  --output-schema '{"type":"object","properties":{"value":{"type":"integer"}},"required":["value"],"additionalProperties":false}'

uv run --frozen codemcp chain run echo_value \
  --agent-dir ~/.pi/agent \
  --input '{"value": 9}'

uv run --frozen codemcp chain list --agent-dir ~/.pi/agent
uv run --frozen codemcp chain revalidate echo_value \
  --scope project --agent-dir ~/.pi/agent
uv run --frozen codemcp chain delete echo_value \
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
just format      # safe Ruff formatting/fixes
just test        # pytest only
just typecheck   # mypy + ty
```
