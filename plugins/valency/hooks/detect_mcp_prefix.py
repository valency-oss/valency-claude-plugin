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
import tempfile
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

DOCS_URL = "https://docs.valency.io/"
VALENCY_DOMAIN = "valency.io"
MCP_LIST_TIMEOUT_SECONDS = 10.0
_NAME_SEPARATOR_RE = re.compile(r"[ .:]+")
_MCP_LIST_LINE_RE = re.compile(r"^(?P<name>.+?):\s+(?P<url>https?://\S+)")
_SESSION_ID_SAFE_RE = re.compile(r"[^A-Za-z0-9_-]")


def _is_valency_url(url: str) -> bool:
    """Return True iff the URL's hostname is `valency.io` or a subdomain.

    Tighter than a substring match — `notvalency.io` and
    `valency.io.attacker.example` correctly fail.
    """
    if not isinstance(url, str):
        return False
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host == VALENCY_DOMAIN or host.endswith("." + VALENCY_DOMAIN)


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
                if _is_valency_url(url):
                    return f"mcp__{name}__"
    return None


def cache_path_for_session(session_id: str | None, base_dir: Path) -> Path | None:
    """Return a session-scoped cache file path, or None if session_id is missing.

    The cache lets us avoid re-running `claude mcp list` (which does network
    health checks) on every `clear`/`compact` event within the same session.
    """
    if not isinstance(session_id, str) or not session_id:
        return None
    safe = _SESSION_ID_SAFE_RE.sub("_", session_id)[:64]
    return base_dir / f"valency-prefix-{safe}"


def read_cached_prefix(path: Path) -> tuple[bool, str | None]:
    """Return (cache_hit, prefix). cache_hit=True means detection should be skipped.

    Empty file means a previous run completed and found no Valency MCP — that
    negative result is cached too so we don't re-stall on subsequent events.
    """
    if not path.exists():
        return False, None
    try:
        content = path.read_text().strip()
    except OSError:
        return False, None
    return True, (content or None)


def write_cached_prefix(path: Path, prefix: str | None) -> None:
    """Persist the detection result so later events in the session reuse it."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prefix or "")
    except OSError:
        pass


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
        if not _is_valency_url(match.group("url")):
            continue
        return display_name_to_prefix(match.group("name").strip())
    return None


def _run_mcp_list(timeout: float = MCP_LIST_TIMEOUT_SECONDS) -> str | None:
    """Run `claude mcp list` and return stdout, or None on failure.

    stderr carries health-check diagnostics that aren't part of the server list,
    so we ignore it to avoid feeding noise into the line parser.
    """
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
    return result.stdout or ""


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


def _detect_prefix(paths: list[Path]) -> str | None:
    prefix = find_valency_prefix(*paths)
    if prefix is not None:
        return prefix
    mcp_list_output = _run_mcp_list()
    if mcp_list_output is None:
        return None
    return find_valency_prefix_in_mcp_list(mcp_list_output)


def main() -> int:
    hook_input = _read_hook_input()
    home = Path.home()
    cwd = Path(hook_input.get("cwd") or os.getcwd())
    paths = [home / ".claude.json", cwd / ".mcp.json"]

    cache = cache_path_for_session(
        hook_input.get("session_id"), Path(tempfile.gettempdir())
    )
    if cache is not None:
        cache_hit, cached_prefix = read_cached_prefix(cache)
        if cache_hit:
            prefix: str | None = cached_prefix
        else:
            prefix = _detect_prefix(paths)
            write_cached_prefix(cache, prefix)
    else:
        prefix = _detect_prefix(paths)

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
