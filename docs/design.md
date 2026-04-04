# Valency Claude Code Plugin — Design Spec

## What This Is

A Claude Code plugin that gives researchers direct access to Valency's research corpus (36M+ papers across arXiv, PubMed, bioRxiv, and medRxiv) through five slash commands. Each command chains multiple MCP tools into an opinionated research workflow and produces structured, readable output.

## Architecture

### Plugin Format

Follows the standard Claude Code plugin format:

```
valency-plugin/
  .claude-plugin/
    plugin.json            # Plugin manifest (name, version, description)
  skills/
    profile/SKILL.md       # /valency:profile <author_name>
    landscape/SKILL.md     # /valency:landscape <topic_or_category>
    similar/SKILL.md       # /valency:similar <paper_id_or_title>
    trends/SKILL.md        # /valency:trends <keyword_or_category>
    network/SKILL.md       # /valency:network <author_name>
  CLAUDE.md                # Plugin-level instructions for Claude
  ISSUES.md                # Open issues tracker
  README.md                # User-facing documentation
  package.json             # npm-style metadata
```

### MCP Server Connection

The plugin requires the Valency MCP connector to be configured in the user's Claude.ai account. Skills reference MCP tools by their full connector name: `mcp__claude_ai_Valency_Systems_Inc__<tool_name>`.

A future version will declare the MCP server in the plugin manifest for auto-connection on install (see ISSUES.md #1).

### How Skills Work

Each skill is a detailed prompt in a `SKILL.md` file. The prompt tells Claude which MCP tools to call, in what order, how to interpret results, and how to format output. Claude orchestrates the tool chain at runtime. No code, no hooks, no scripts.

Skills have YAML frontmatter (name, description) used by Claude Code for discovery and help text.

## Plugin Manifest

**.claude-plugin/plugin.json:**

```json
{
  "name": "valency",
  "description": "Search, profile, and analyze 36M+ research papers across arXiv, PubMed, bioRxiv, and medRxiv with semantic embeddings.",
  "version": "0.1.0",
  "author": {
    "name": "Valency Systems Inc"
  },
  "homepage": "https://valency.io",
  "keywords": [
    "research",
    "papers",
    "arxiv",
    "pubmed",
    "biorxiv",
    "medrxiv",
    "literature-review",
    "semantic-search"
  ]
}
```

## Skills

### /valency:profile <author_name>

Build a comprehensive researcher profile.

**MCP tool chain:**

1. `get_author_profile` — summary stats, h-index proxy, top papers
2. `search_by_author` — full publication list (paginated if needed)
3. `batch_author_categories` — research domain distribution
4. `find_coauthors` — top collaborators

**Output format:**

- Summary block: name, paper count, primary domains, active years
- Research domain breakdown (top 5 categories with counts)
- Top 10 papers by recency or citation count (title, year, venue, category)
- Top 5 collaborators with co-publication counts
- Suggested follow-ups: `/valency:network <author>`, `/valency:similar <paper_id>`

### /valency:landscape <topic_or_category>

Generate a landscape overview of a research field.

**Input handling:** If input matches an arXiv category pattern (e.g., `cs.LG`, `q-bio.BM`), use `search_by_category`. Otherwise, treat as free text and use `semantic_search_papers`.

**MCP tool chain:**

1. `search_by_category` or `semantic_search_papers` — find papers in the field
2. `get_publication_trends` — publication volume over time
3. `identify_prolific_authors` — top contributors
4. `identify_research_domains` — subdomain breakdown
5. `analyze_corpus_metrics` — corpus-level stats for the filtered set

**Output format:**

- Field summary: total papers, date range, growth trajectory
- Publication trend as a year-by-year table
- Top 10 authors by publication count
- Subdomain/category breakdown
- 5 recent notable papers (title, authors, year)
- Brief observations (e.g., "volume doubled since 2022", "concentrated in 2-3 subdomains")

### /valency:similar <paper_id_or_title>

Find semantically similar papers using neural embeddings.

**Input handling:** Detect identifier type: digits only = PMID, `10.xxxx/...` = DOI (covers bioRxiv, medRxiv — do not assume all bioRxiv records use `10.1101/...`), `NNNN.NNNNN` with optional `vN` suffix = arXiv ID, otherwise treat as title and resolve via `search_by_title`.

**MCP tool chain:**

1. (If title) `search_by_title` — resolve to paper ID
2. `find_similar_papers` — nearest neighbors by embedding similarity
3. `get_paper_by_id` — fetch metadata for each similar paper

**Output format:**

- Source paper: title, authors, year, abstract snippet
- Similar papers list (ranked by similarity): title, authors, year, category, one-line abstract summary
- Suggested follow-up: `/valency:profile <author>` for listed authors

### /valency:trends <keyword_or_category>

Show how a topic or category evolved over time.

**Input handling:** If input matches an arXiv category, use `get_publication_trends`. If free text or keyword, use `get_keyword_trends`. If input contains commas or "vs" (e.g., "cs.LG, cs.CL"), use `get_publication_trends_batch` for comparison.

**MCP tool chain:**

1. `get_keyword_trends` or `get_publication_trends` — time series data
2. (If comparing) `get_publication_trends_batch` — side-by-side data
3. `search_by_abstract` — sample recent papers to characterize current state

**Output format:**

- Year-by-year table with counts
- Narrative summary: when the field emerged, inflection points, current trajectory
- 3-5 recent representative papers
- If comparing multiple categories: side-by-side table

### /valency:network <author_name>

Map a researcher's collaboration network.

**MCP tool chain:**

1. `get_author_profile` — baseline info
2. `find_coauthors` — direct collaborators with counts
3. For top 5 coauthors: `find_coauthors` again — second-degree connections
4. `compare_authors` — compare focal author with top collaborators

**Output format:**

- Ego network summary: author at center, direct collaborators with co-publication counts and primary domains
- Second-degree connections (collaborators of collaborators who are not direct collaborators)
- Cross-domain bridges: collaborators whose primary domain differs from the focal author
- Suggested follow-up: `/valency:profile <collaborator>` for interesting connections

## Error Handling

Each skill handles common edge cases through prompt instructions:

- **Author not found:** Tell the user, suggest checking spelling or trying a partial name.
- **No results:** Suggest broadening the query or trying related terms.
- **Paper ID not found:** Suggest searching by title instead.
- **Ambiguous input:** For `/valency:landscape`, try category lookup first, fall back to semantic search.

No retry logic. If an MCP tool returns empty results, say so and suggest alternatives.

## CLAUDE.md

The plugin's `CLAUDE.md` instructs Claude that:

- All data retrieval goes through Valency MCP tools. Never fabricate paper titles, authors, or metadata.
- The Valency MCP connector must be configured in the user's Claude.ai account.
- Skills should produce clean, scannable output with consistent formatting.

## Non-Goals (v0.1)

- No caching layer
- No user authentication or usage tracking
- No write operations (no annotations, no paper submission)
- No visualization (text and tables only)
- No composability or piping between commands
- No auto-connection of MCP server (deferred to future version)

## Data Sources

The corpus spans four preprint/publication servers:

| Source | Papers | With Embeddings |
|--------|--------|-----------------|
| arXiv | 4.6M | 4.56M |
| PubMed | 31.1M | 17.6K |
| bioRxiv | 402K | 388K |
| medRxiv | 100K | 100K |

Embedding coverage varies by source. Skills work with whatever the MCP server returns without special-casing any source.
