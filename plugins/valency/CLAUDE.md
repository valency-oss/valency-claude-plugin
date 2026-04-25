# Valency Plugin

This plugin provides research corpus tools via the Valency MCP connector.

## Prerequisites

The Valency MCP connector must be configured in the user's Claude.ai account.
All data retrieval goes through the Valency MCP server tools.

## Tool Names

Skills reference Valency tools by short name (e.g., `get_author_profile`). The actual MCP tool prefix depends on what the user named the server when they ran `claude mcp add`, so it is detected at session start by the plugin's SessionStart hook and reported via injected context. Use that prefix (e.g., `mcp__valency-mcp__get_author_profile`) for every tool call.

If the session-start context says the Valency MCP is not configured, do not attempt to call Valency tools — surface the setup notice to the user instead.

## Rules

- Never fabricate paper titles, authors, abstracts, or metadata. All paper data must come from MCP tool results.
- If an MCP tool returns no results, say so plainly and suggest the user try a different query.
- Produce clean, scannable output with consistent markdown formatting.
- When suggesting follow-up commands, use the `/valency:<command>` format.
