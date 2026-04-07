# Valency Plugin

This plugin provides research corpus tools via the Valency MCP connector.

## Prerequisites

The Valency MCP connector must be configured in the user's Claude.ai account.
All data retrieval goes through the Valency MCP server tools.

## Tool Names

Skills reference Valency tools by short name (e.g., `get_author_profile`). Match these to the actual Valency MCP tools available in your session — they may be prefixed with a connector namespace like `mcp__claude_ai_Valency_Systems_Inc__` or similar depending on how the MCP server is connected.

## Rules

- Never fabricate paper titles, authors, abstracts, or metadata. All paper data must come from MCP tool results.
- If an MCP tool returns no results, say so plainly and suggest the user try a different query.
- Produce clean, scannable output with consistent markdown formatting.
- When suggesting follow-up commands, use the `/valency:<command>` format.
