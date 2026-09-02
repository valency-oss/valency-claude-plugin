---
name: landscape
description: "Use when the user asks for an overview of a research field, wants to understand a domain's key players, or asks 'what's happening in X' or 'give me a landscape of X'. Triggers on requests for field summaries, top authors in an area, or subdomain breakdowns. Also invokable as /valency:landscape <topic_or_category>."
---

# Field Landscape

Generate a landscape overview of a research field or topic.

## Input

The user provides either:
- An arXiv category code (e.g., `cs.LG`, `q-bio.BM`, `astro-ph.CO`) — recognized by the pattern of a short prefix, a dot, and a short suffix
- Free text describing a research area (e.g., "protein folding", "large language models")

The corpus spans seven sources (pubmed, arxiv, biorxiv, medrxiv, psyarxiv, socarxiv, eartharxiv) and PubMed holds most papers. An arXiv category code restricts every call to arXiv. Free text searches all sources.

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.
- This skill does not display abstracts, so pass `include_abstract: false` on search calls.

## Tool Chain

### Step 1: Find papers in the field

**If the input matches an arXiv category pattern** (e.g., `cs.LG`):

Call `search_by_category` with:
- `category` (string): the category code
- `limit` (integer): 10
- `sort_by` (string): "citations"
- `include_abstract` (boolean): false

Sorting a large category by citations can take several seconds. Wait for it.

**If the input is free text:**

Call `semantic_search_papers` with:
- `query` (string): the user's input
- `limit` (integer): 10
- `sort_by` (string): "citations"
- `include_abstract` (boolean): false

If no results are found, tell the user and suggest trying different terms or checking category codes with a broader search. Stop here.

Every paper carries a `source` field. For free-text input, note the **dominant source** among the results (the source with the most papers). Step 4 uses it.

### Step 2: Measure record activity

**If the input is a category code:**

Call `get_publication_trends` with:
- `category` (string): the category code
- `granularity` (string): "year"
- `format` (string): "compact"

**If the input is free text:**

Call `get_keyword_trends` with:
- `query` (string): the user's input
- `granularity` (string): "year"
- `format` (string): "compact"

Keyword counts span all sources. Sum the yearly counts to get the total matching records.

Category trends count latest records in the resolved hierarchical category. Keyword trends count records whose abstract full-text index lexically matches the query. Both group by `datestamp`, so describe them as record activity rather than publication counts.

### Step 3: Identify top authors

**Category input only.** If the input was free text, skip this step and note that top-author ranking requires a category code.

Call `identify_prolific_authors` with:
- `category` (string): the category code
- `limit` (integer): 20

Rows are author-name strings, not disambiguated people. Each row carries `disambiguation_status`. Drop rows with status `likely_aggregation` or `severe_aggregation` (a common name covering many researchers), then keep the first 10 that remain. Mark rows with status `ambiguous` as "(name may cover several researchers)". Requesting 20 leaves room to backfill after filtering.

### Step 4: Identify subdomains

Call `identify_research_domains` with:
- `limit` (integer): 10
- `source` (string): "arxiv" if the input was a category code; otherwise the dominant source from Step 1

This returns source-wide domain rankings, not rankings within the field. Passing `source` matters: without it the ranking interleaves category vocabularies from every source (arXiv codes, PubMed MeSH headings, bioRxiv labels) on different percentage bases. With it, the result is a coherent ranking within one vocabulary that contextualizes where this field sits among its source's domains.

### Step 5: Get corpus metrics

**Category input only.** Call `analyze_corpus_metrics` with:
- `category` (string): the category code

For free text, skip this step. The Step 2 sum stands in for the total.

## Output Format

### Field Summary

A brief paragraph covering:
- Total category records from Step 5, or total abstract-keyword matches from the Step 2 sum for free text
- Which sources are covered (arXiv only for a category; all sources for free text, naming the dominant one)
- Source record/update date range
- Record-activity trajectory from Step 2

### Record Activity

A year-by-year table from Step 2:

| Year | Matching records |
|------|--------|
| 2020 | 1,234  |
| ...  | ...    |

### Top Authors

**Category input only.** A numbered list of up to 10 authors from Step 3 with their paper counts. Note how many rows were dropped as name-collision aggregates.

### Subdomain Breakdown

A table of the top research domains from Step 4, labelled with the source they were ranked within.

### Notable Papers

List 5 of the most-cited papers from Step 1. For each:
- [Title](url) (paper ID)
- Authors (first 3, then "et al." if more)
- Source-aware date label
- Citations
- Category

### Observations

2-3 brief observations drawn from the data. Examples:
- "Matching-record activity has doubled since 2021"
- "The field is concentrated in 2-3 subdomain categories"
- "Author X dominates with 3x more papers than the next most prolific"

### Suggested Follow-ups

- `/valency:profile <author>` — for any top author listed
- `/valency:trends <category>` — for deeper trend analysis
- `/valency:similar <paper_id>` — for any notable paper listed
