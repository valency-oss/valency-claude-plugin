# Open Issues

## 1. Auto-connect MCP server on plugin install

**Status:** Deferred until public launch

Currently the plugin assumes users have the Valency MCP connector already configured (via Claude.ai connectors). Before going public, we should declare the MCP server in the plugin manifest so that installing the plugin auto-connects to `https://labs.valency.io/mcp`. This will require modifying the plugin manifest and potentially the skill files that reference MCP tools by connector name.

## 2. Submit to official Claude marketplace

**Status:** Blocked on public repo

Submit the plugin via [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit) to get listed at `claude.com/plugins/valency`. Requires the repo to be public first. Before submitting, update `marketplace.json` source from `"./"` to `{"source": "url", "url": "https://github.com/valencyio/valency-plugin.git"}`.

## 3. Automated smoke tests for skills

**Status:** Deferred to v0.2

v0.1 uses manual smoke tests (run each command, visually verify output). For v0.2, add a test script that invokes each skill programmatically via `claude -p` and checks that the output contains expected sections (e.g., "## Summary", "## Top Papers", "## Trend Data"). This catches prompt regressions without the brittleness of golden-file tests.

## 4. `get_publication_trends_batch` times out

**Status:** Workaround in place

The `get_publication_trends_batch` MCP tool consistently times out, even for small category pairs. The trends skill now calls `get_publication_trends` individually per category instead. If the batch tool is fixed server-side, the skill can be reverted to use it for better efficiency.

## 5. `identify_prolific_authors` times out on large categories

**Status:** Workaround in place

The `identify_prolific_authors` tool times out for large categories like cs.LG. The landscape skill now handles this gracefully by skipping the top-authors section when a timeout occurs. No server-side fix needed unless the tool's performance improves.

## 6. Optional recency window for `reading-list`

**Status:** Deferred (scope question, not a bug)

PR valencyio/valency-mcp-server#343 added `start_date`/`end_date` to `find_similar_papers`. The `reading-list` skill's Step 5 currently returns all-time similars for each seed, which is the right default for a bibliography. We could add an optional recency window — e.g., "reading list for David Hogg since 2023" — that threads `start_date` through to the `find_similar_papers` calls.

Open questions before implementing:
- How should the user surface it? A positional `since <YYYY>` argument on `/valency:reading-list`, a natural-language trigger, or both?
- Should the window apply per-thread or globally across all seeds?
- What happens if a thread returns too few results after date filtering — fall back to all-time, or show the sparse thread as-is?

Brainstorm these before touching the skill.
