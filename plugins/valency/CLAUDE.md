# Valency Plugin

This plugin provides research corpus tools via the Valency MCP connector.

## Prerequisites

The Valency MCP connector must be configured in the user's Claude.ai account.
All data retrieval goes through the Valency MCP server tools.

## Tool Names

Skills use short tool names (e.g., `get_author_profile`). Prepend the Valency MCP prefix to every call. If no prefix is available, surface the setup notice instead of attempting calls.

## Rules

- Never fabricate paper titles, authors, abstracts, or metadata. All paper data must come from MCP tool results.
- If an MCP tool returns no results, say so plainly and suggest the user try a different query.
- Produce clean, scannable output with consistent markdown formatting.
- When suggesting follow-up commands, use the `/valency:<command>` format.
