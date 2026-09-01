# Valency Plugin

This plugin provides research corpus tools via the Valency MCP connector.

Claude Code does not load this file as context (`claude plugin validate` warns about it). It documents the conventions for contributors. Each SKILL.md repeats the conventions it needs, so skills stay self-contained.

## Prerequisites

The Valency MCP server (`https://mcp.valency.io`) must be connected, either as a claude.ai connector or via `claude mcp add`. All data retrieval goes through the Valency MCP server tools.

## Tool Names

Skills use short tool names (e.g., `get_author_profile`). Prepend the Valency MCP prefix to every call. If no prefix is available, surface the setup notice instead of attempting calls.

## Corpus

The corpus spans seven sources: pubmed, arxiv, biorxiv, medrxiv, psyarxiv, socarxiv, eartharxiv. PubMed holds roughly 90% of papers. Category codes are source-specific: arXiv uses dotted codes (`cs.LG`), bioRxiv and medRxiv use plain-English labels (`genetics`), PubMed uses MeSH headings, and the OSF servers use Title-Case disciplines (`Sociology`). Passing an arXiv code without `source` still restricts results to arXiv.

## Conventions

Every skill follows these. They are repeated in each SKILL.md so each skill is self-contained.

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Report a paper's year from `first_submitted`. `datestamp` is a source-record update date and can be years later.
- Date filters (`start_date`, `end_date`) and recency sorts operate on `datestamp`. When recency matters, re-filter and re-sort on `first_submitted` yourself.
- Author strings may be "First Last" (arXiv) or "Last, First" (PubMed). Before comparing names, lowercase both and convert "last, first" to "first last".
- Pass `include_abstract: false` unless the abstract is displayed or read. Pass `enrich_citations: false` unless citation counts are displayed or used for ranking.

## Rules

- Never fabricate paper titles, authors, abstracts, or metadata. All paper data must come from MCP tool results.
- If an MCP tool returns no results, say so plainly and suggest the user try a different query.
- Produce clean, scannable output with consistent markdown formatting.
- When suggesting follow-up commands, use the `/valency:<command>` format.
