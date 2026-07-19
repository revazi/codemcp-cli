from __future__ import annotations

from .chains import (
    ChainEnabledChange,
    ChainListResponse,
    ChainScope,
    ChainStatusView,
    SaveChainResponse,
)
from .executor import ExecutionResponse
from .gateway import GatewayRuntime, ManagerApplyResponse
from .models import SearchResponse, StatusResponse
from .runtime_paths import RuntimePaths, resolve_runtime_paths
from .settings import CodeMcpCliSettings

__all__ = [
    "ChainEnabledChange",
    "ChainListResponse",
    "ChainScope",
    "ChainStatusView",
    "CodeMcpCliSettings",
    "ExecutionResponse",
    "GatewayRuntime",
    "ManagerApplyResponse",
    "RuntimePaths",
    "SaveChainResponse",
    "SearchResponse",
    "StatusResponse",
    "create_runtime",
    "resolve_runtime_paths",
]


def create_runtime(paths: RuntimePaths | None = None) -> GatewayRuntime:
    """Create an embeddable runtime from resolved paths without starting an MCP transport."""
    resolved = paths or resolve_runtime_paths()
    return GatewayRuntime.create(
        config_path=resolved.config_path,
        oauth_storage_dir=resolved.oauth_dir,
        catalog_cache_dir=resolved.catalog_dir,
        settings_path=resolved.settings_path,
        global_chain_dir=resolved.global_chains_dir,
        project_chain_dir=resolved.project_chains_dir,
    )
