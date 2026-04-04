# Open Issues

## 1. Auto-connect MCP server on plugin install

**Status:** Deferred until public launch

Currently the plugin assumes users have the Valency MCP connector already configured (via Claude.ai connectors). Before going public, we should declare the MCP server in the plugin manifest so that installing the plugin auto-connects to `https://labs.valency.io/mcp`. This will require modifying the plugin manifest and potentially the skill files that reference MCP tools by connector name.

## 2. Automated smoke tests for skills

**Status:** Deferred to v0.2

v0.1 uses manual smoke tests (run each command, visually verify output). For v0.2, add a test script that invokes each skill programmatically via `claude -p` and checks that the output contains expected sections (e.g., "## Summary", "## Top Papers", "## Trend Data"). This catches prompt regressions without the brittleness of golden-file tests.
