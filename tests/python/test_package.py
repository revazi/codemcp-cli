from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import pytest

import codemcp_cli
from codemcp_cli.api import GatewayRuntime, create_runtime, resolve_runtime_paths


def test_distribution_exposes_version_and_typing_marker() -> None:
    assert codemcp_cli.__version__ == version("codemcp-cli")
    assert codemcp_cli.__file__ is not None
    assert Path(codemcp_cli.__file__).with_name("py.typed").is_file()


@pytest.mark.asyncio
async def test_public_api_creates_embeddable_runtime(tmp_path: Path) -> None:
    (tmp_path / "mcp.json").write_text('{"mcpServers": {}}', encoding="utf-8")
    paths = resolve_runtime_paths(agent_dir=tmp_path)

    runtime = create_runtime(paths)
    try:
        assert isinstance(runtime, GatewayRuntime)
        assert runtime.status().config_path == str(tmp_path / "mcp.json")
    finally:
        await runtime.close()
