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
import sys
from pathlib import Path
from typing import Any, Iterator

DOCS_URL = "https://docs.valency.io/"
VALENCY_DOMAIN = "valency.io"


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
