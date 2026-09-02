---
name: trends
description: "Use when the user asks how a research topic has changed over time, wants publication volume trends, asks 'is X growing', 'when did X take off', or wants to compare the trajectories of two fields. Triggers on trend, growth, or timeline questions about research areas. Also invokable as /valency:trends <keyword_or_category>."
---

# Publication Trends

Show how a topic or category has evolved over time.

## Input

The user provides one of:
- An arXiv category code (e.g., `cs.LG`) — recognized by the short-prefix-dot-suffix pattern
- A keyword or phrase (e.g., "transformer", "CRISPR")
- Multiple categories or keywords separated by commas or "vs" (e.g., "cs.LG, cs.CL" or "transformers vs RNNs") — for comparison

Optionally, a source name (pubmed, arxiv, biorxiv, medrxiv, psyarxiv, socarxiv, eartharxiv). Category trends are arXiv-only by construction. Keyword trends span all seven sources unless a source is given, and PubMed dominates those counts. If the user names a source, pass `source` on every call below.

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.
- This skill does not display abstracts or citation counts, so pass `include_abstract: false` and `enrich_citations: false` on search calls.

## Tool Chain

### Step 1: Get trend data

**If the input is a single category code:**

Call `get_publication_trends` with:
- `category` (string): the category code
- `granularity` (string): "year"
- `format` (string): "compact"

**If the input is a single keyword/phrase:**

Call `get_keyword_trends` with:
- `query` (string): the keyword
- `granularity` (string): "year"
- `format` (string): "compact"

**If the input contains multiple categories** (comma-separated or "vs"):

Call `get_publication_trends_batch` once with:
- `categories` (array of strings): all category codes, e.g. `["cs.LG", "cs.CL"]`
- `granularity` (string): "year"
- `format` (string): "compact"

The response holds one entry per category under `data`. If `too_broad_categories` lists any of them, call `get_publication_trends` individually for those with the same `granularity` and `format`.

**If the input contains multiple keywords** (comma-separated or "vs"):

Call `get_keyword_trends` once per keyword with:
- `query` (string): each keyword
- `granularity` (string): "year"
- `format` (string): "compact"

### Step 2: Get recent representative papers

**For a category code**, call `search_by_category` with:
- `category` (string): the category code (the first one, for comparisons)
- `limit` (integer): 5
- `include_abstract` (boolean): false
- `enrich_citations` (boolean): false

Results are ordered by `datestamp`, most recent first. Preserve that record-recency order and label each paper's date with the source-aware convention.

**For a keyword**, call `search_by_abstract` with:
- `query` (string): the keyword (the first one, for comparisons)
- `limit` (integer): 5
- `include_abstract` (boolean): false
- `enrich_citations` (boolean): false

If the keyword has unrelated meanings in other fields (e.g., "transformer" in electrical engineering), add `phrase_mode: true` for multi-word phrases, or `exclude_categories` (array of strings) to drop the unrelated domains.

## Output Format

### Trend Data

**For single input:** a year-by-year table:

| Year | Papers |
|------|--------|
| 2018 | 500    |
| ...  | ...    |

**For comparisons:** a side-by-side table:

| Year | cs.LG  | cs.CL  |
|------|--------|--------|
| 2018 | 500    | 300    |
| ...  | ...    | ...    |

### Narrative Summary

A 3-5 sentence narrative covering:
- Which sources the counts cover (arXiv for categories; all sources, or the one named, for keywords)
- When the field or topic first appeared in the corpus
- Key inflection points (years where volume jumped or dropped significantly)
- Current trajectory (accelerating, plateauing, declining). The current year is partial, so do not read a lower count for it as a decline.
- For comparisons: which topic is growing faster and when they diverged

### Representative Recent Papers

A numbered list of 3-5 papers from Step 2. For each:
- [Title](url) (paper ID)
- Authors (first 3, then "et al.")
- Source-aware date label

### Suggested Follow-ups

- `/valency:landscape <category>` — for a broader overview of the field
- `/valency:profile <author>` — for authors driving the trend
- `/valency:trends <other_keyword>` — to compare with related topics
