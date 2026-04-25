"""Tests for the SessionStart MCP prefix detection hook."""

from __future__ import annotations

import json
from pathlib import Path

from detect_mcp_prefix import build_context, find_valency_prefix


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def test_finds_valency_in_top_level_mcp_servers(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config,
        {
            "mcpServers": {
                "valency-mcp": {"type": "http", "url": "https://labs.valency.io/mcp"},
                "notion": {"type": "http", "url": "https://mcp.notion.com/mcp"},
            }
        },
    )
    assert find_valency_prefix(config) == "mcp__valency-mcp__"


def test_finds_valency_in_nested_project_section(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config,
        {
            "projects": {
                "/some/path": {
                    "mcpServers": {
                        "val": {"type": "http", "url": "https://labs.valency.io/mcp"}
                    }
                }
            }
        },
    )
    assert find_valency_prefix(config) == "mcp__val__"


def test_finds_valency_in_project_mcp_json(tmp_path: Path) -> None:
    home = tmp_path / "claude.json"
    _write_json(home, {"mcpServers": {}})
    project = tmp_path / ".mcp.json"
    _write_json(
        project,
        {
            "mcpServers": {
                "valency-mcp": {"type": "http", "url": "https://labs.valency.io/mcp"}
            }
        },
    )
    assert find_valency_prefix(home, project) == "mcp__valency-mcp__"


def test_preserves_arbitrary_user_chosen_name(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config,
        {
            "mcpServers": {
                "my-research-stuff": {
                    "type": "http",
                    "url": "https://labs.valency.io/mcp",
                }
            }
        },
    )
    assert find_valency_prefix(config) == "mcp__my-research-stuff__"


def test_returns_none_when_no_valency_server(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config,
        {"mcpServers": {"notion": {"type": "http", "url": "https://mcp.notion.com/mcp"}}},
    )
    assert find_valency_prefix(config) is None


def test_returns_none_when_config_missing(tmp_path: Path) -> None:
    assert find_valency_prefix(tmp_path / "missing.json") is None


def test_returns_none_when_config_malformed(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    config.write_text("not json{{")
    assert find_valency_prefix(config) is None


def test_ignores_non_dict_server_entries(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config, {"mcpServers": {"weird": "https://labs.valency.io/mcp"}}
    )
    assert find_valency_prefix(config) is None


def test_ignores_servers_without_url(tmp_path: Path) -> None:
    config = tmp_path / "claude.json"
    _write_json(
        config,
        {
            "mcpServers": {
                "stdio-thing": {"type": "stdio", "command": "valency-cli"}
            }
        },
    )
    assert find_valency_prefix(config) is None


def test_build_context_with_prefix_mentions_prefix_and_example() -> None:
    ctx = build_context("mcp__valency-mcp__")
    assert "mcp__valency-mcp__" in ctx
    assert "get_author_profile" in ctx


def test_build_context_without_prefix_warns_and_links_docs() -> None:
    ctx = build_context(None)
    assert "https://docs.valency.io/" in ctx
    assert "not configured" in ctx.lower()
