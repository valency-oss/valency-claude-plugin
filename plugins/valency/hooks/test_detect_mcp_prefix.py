"""Tests for the SessionStart MCP prefix detection hook."""

from __future__ import annotations

import json
from pathlib import Path

from detect_mcp_prefix import (
    build_context,
    display_name_to_prefix,
    find_valency_prefix,
    find_valency_prefix_in_mcp_list,
)


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


def test_display_name_passes_through_simple_cli_name() -> None:
    assert display_name_to_prefix("valency-mcp") == "mcp__valency-mcp__"


def test_display_name_collapses_dot_and_space() -> None:
    assert display_name_to_prefix("claude.ai Slack") == "mcp__claude_ai_Slack__"


def test_display_name_collapses_colon_space_runs() -> None:
    assert (
        display_name_to_prefix("claude.ai Moxn: Roll For Vibes")
        == "mcp__claude_ai_Moxn_Roll_For_Vibes__"
    )


def test_display_name_handles_valency_systems_inc() -> None:
    assert (
        display_name_to_prefix("claude.ai Valency Systems Inc")
        == "mcp__claude_ai_Valency_Systems_Inc__"
    )


MCP_LIST_SAMPLE = """\
Checking MCP server health…

claude.ai Slack: https://mcp.slack.com/mcp - ✓ Connected
claude.ai Google Drive: https://drivemcp.googleapis.com/mcp/v1 - ! Needs authentication
valency-mcp: https://labs.valency.io/mcp - ✓ Connected
"""


def test_finds_cli_valency_in_mcp_list_output() -> None:
    assert find_valency_prefix_in_mcp_list(MCP_LIST_SAMPLE) == "mcp__valency-mcp__"


def test_finds_claude_ai_valency_in_mcp_list_output() -> None:
    output = (
        "claude.ai Valency Systems Inc: https://api.valency.io/mcp - ✓ Connected\n"
    )
    assert (
        find_valency_prefix_in_mcp_list(output)
        == "mcp__claude_ai_Valency_Systems_Inc__"
    )


def test_returns_none_when_mcp_list_has_no_valency_entry() -> None:
    output = "claude.ai Slack: https://mcp.slack.com/mcp - ✓ Connected\n"
    assert find_valency_prefix_in_mcp_list(output) is None


def test_returns_none_for_empty_mcp_list_output() -> None:
    assert find_valency_prefix_in_mcp_list("") is None


def test_ignores_lines_without_url() -> None:
    output = "Checking MCP server health…\n\nsome other diagnostic line\n"
    assert find_valency_prefix_in_mcp_list(output) is None
