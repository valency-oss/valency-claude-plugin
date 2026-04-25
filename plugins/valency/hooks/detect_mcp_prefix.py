#!/usr/bin/env python3
"""SessionStart hook: detect the Valency MCP prefix and inject it as context.

Plugin skills reference Valency tools by short name (e.g., `get_author_profile`).
The actual tool name in a session depends on what the user named the MCP server
when they ran `claude mcp add`. This hook walks Claude Code's config files at
session start, finds the entry pointing at the Valency MCP, and reports the
prefix so skills can call tools deterministically.

If no Valency MCP is configured, the hook tells the model to surface a setup
notice pointing at https://docs.valency.io/.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

DOCS_URL = "https://docs.valency.io/"
VALENCY_DOMAIN = "valency.io"
MCP_LIST_TIMEOUT_SECONDS = 10.0
_NAME_SEPARATOR_RE = re.compile(r"[ .:]+")
_MCP_LIST_LINE_RE = re.compile(r"^(?P<name>[^:]+?):\s+(?P<url>https?://\S+)")


def _walk_mcp_servers(obj: Any) -> Iterator[dict[str, Any]]:
    """Yield every dict found at key `mcpServers` anywhere in the structure."""
    if isinstance(obj, dict):
        servers = obj.get("mcpServers")
        if isinstance(servers, dict):
            yield servers
        for value in obj.values():
            yield from _walk_mcp_servers(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_mcp_servers(item)


def find_valency_prefix(*config_paths: Path) -> str | None:
    """Return `mcp__<name>__` for the configured Valency MCP, or None."""
    for path in config_paths:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        for servers in _walk_mcp_servers(data):
            for name, config in servers.items():
                if not isinstance(config, dict):
                    continue
                url = config.get("url") or ""
                if isinstance(url, str) and VALENCY_DOMAIN in url:
                    return f"mcp__{name}__"
    return None


def claude_ai_integrations_might_exist(claude_json_path: Path) -> bool:
    """Return True if the user has ever connected a Claude.ai-managed MCP.

    Used to gate the slow `claude mcp list` fallback: skipping it when the user
    has never used a web integration avoids a per-session health-check stall
    for the (common) CLI-only setup.
    """
    try:
        data = json.loads(claude_json_path.read_text())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return False
    return isinstance(data, dict) and data.get("claudeAiMcpEverConnected") is True


def display_name_to_prefix(name: str) -> str:
    """Convert an MCP server display name (as shown by `claude mcp list`) to the
    `mcp__<sanitized>__` prefix Claude Code uses internally for that server."""
    sanitized = _NAME_SEPARATOR_RE.sub("_", name).strip("_")
    return f"mcp__{sanitized}__"


def find_valency_prefix_in_mcp_list(output: str) -> str | None:
    """Search `claude mcp list` stdout for an entry pointing at valency.io.

    Returns the matching prefix or None. This covers both CLI-configured servers
    (whose names map straight through) and Claude.ai web integrations (whose
    names like `claude.ai Valency Systems Inc` need sanitizing).
    """
    for line in output.splitlines():
        match = _MCP_LIST_LINE_RE.match(line.strip())
        if match is None:
            continue
        url = match.group("url")
        if VALENCY_DOMAIN not in url:
            continue
        return display_name_to_prefix(match.group("name").strip())
    return None


def _run_mcp_list(timeout: float = MCP_LIST_TIMEOUT_SECONDS) -> str | None:
    """Run `claude mcp list` and return its combined output, or None on failure."""
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    return (result.stdout or "") + (result.stderr or "")


def build_context(prefix: str | None) -> str:
    if prefix is not None:
        return (
            f"Valency MCP detected. The tool prefix in this session is `{prefix}`. "
            f"When a Valency skill instructs you to call a tool by its short name "
            f"(e.g., `get_author_profile`), prepend this prefix to get the actual "
            f"tool name (e.g., `{prefix}get_author_profile`)."
        )
    return (
        "The Valency plugin is installed but the Valency MCP server is not "
        "configured in this session, so its skills will not be able to retrieve "
        f"data. Tell the user to set it up: see {DOCS_URL} for instructions."
    )


def _read_hook_input() -> dict[str, Any]:
    if sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def main() -> int:
    hook_input = _read_hook_input()
    home = Path.home()
    cwd = Path(hook_input.get("cwd") or os.getcwd())
    paths = [home / ".claude.json", cwd / ".mcp.json"]

    prefix = find_valency_prefix(*paths)
    if prefix is None and claude_ai_integrations_might_exist(home / ".claude.json"):
        mcp_list_output = _run_mcp_list()
        if mcp_list_output is not None:
            prefix = find_valency_prefix_in_mcp_list(mcp_list_output)
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(prefix),
        }
    }
    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
