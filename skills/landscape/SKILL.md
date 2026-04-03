---
name: landscape
description: "Generate a landscape overview of a research field — publication trends, top authors, subdomains, and notable papers. Usage: /valency:landscape <topic_or_category>"
---

# Field Landscape

Generate a landscape overview of a research field or topic.

## Input

The user provides either:
- An arXiv category code (e.g., `cs.LG`, `q-bio.BM`, `astro-ph.CO`) — recognized by the pattern of a short prefix, a dot, and a short suffix
- Free text describing a research area (e.g., "protein folding", "large language models")

## Tool Chain

### Step 1: Find papers in the field

**If the input matches an arXiv category pattern** (e.g., `cs.LG`):

Call `mcp__claude_ai_Valency_Systems_Inc__search_by_category` with:
- `category`: the category code
- `limit`: 10
- `sort_by`: "citations"

**If the input is free text:**

Call `mcp__claude_ai_Valency_Systems_Inc__semantic_search_papers` with:
- `query`: the user's input
- `limit`: 10
- `sort_by`: "citations"

If no results are found, tell the user and suggest trying different terms or checking category codes with a broader search. Stop here.

### Step 2: Get publication trends

**If the input is a category code:**

Call `mcp__claude_ai_Valency_Systems_Inc__get_publication_trends` with:
- `category`: the category code
- `granularity`: "year"
- `format`: "compact"

**If the input is free text:**

Call `mcp__claude_ai_Valency_Systems_Inc__get_keyword_trends` with:
- `query`: the user's input
- `granularity`: "year"
- `format`: "compact"

### Step 3: Identify top authors

Call `mcp__claude_ai_Valency_Systems_Inc__identify_prolific_authors` with:
- `category`: the category code (if input was a category), otherwise omit
- `limit`: 10

Note: if the input was free text and no category was identified, skip this step and note that top-author ranking requires a category code.

### Step 4: Identify subdomains

Call `mcp__claude_ai_Valency_Systems_Inc__identify_research_domains` with:
- `limit`: 10

Note: this returns corpus-wide domain rankings. If the input was a category, the results contextualize where this category sits within the broader landscape.

### Step 5: Get corpus metrics

Call `mcp__claude_ai_Valency_Systems_Inc__analyze_corpus_metrics` with:
- `category`: the category code (if input was a category), otherwise omit

## Output Format

### Field Summary

A brief paragraph covering:
- Total papers found (from Step 5 or Step 1 result count)
- Date range of publications
- Growth trajectory (from Step 2 — is volume increasing, stable, or declining?)

### Publication Trends

A year-by-year table from Step 2:

| Year | Papers |
|------|--------|
| 2020 | 1,234  |
| ...  | ...    |

### Top Authors

A numbered list of the top 10 authors from Step 3 with their paper counts.

### Subdomain Breakdown

A table of the top research domains from Step 4, giving context for how this field relates to the broader corpus.

### Notable Recent Papers

List 5 papers from Step 1 (the most-cited papers found). For each:
- Title (with paper ID)
- Authors (first 3, then "et al." if more)
- Year
- Category

### Observations

2-3 brief observations drawn from the data. Examples:
- "Publication volume has doubled since 2021"
- "The field is concentrated in 2-3 subdomain categories"
- "Author X dominates with 3x more papers than the next most prolific"

### Suggested Follow-ups

- `/valency:profile <author>` — for any top author listed
- `/valency:trends <category>` — for deeper trend analysis
- `/valency:similar <paper_id>` — for any notable paper listed
