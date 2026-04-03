---
name: trends
description: "Show how a research topic or category has evolved over time — publication volumes, inflection points, and representative papers. Usage: /valency:trends <keyword_or_category>"
---

# Publication Trends

Show how a topic or category has evolved over time.

## Input

The user provides one of:
- An arXiv category code (e.g., `cs.LG`) — recognized by the short-prefix-dot-suffix pattern
- A keyword or phrase (e.g., "transformer", "CRISPR")
- Multiple categories or keywords separated by commas or "vs" (e.g., "cs.LG, cs.CL" or "transformers vs RNNs") — for comparison

## Tool Chain

### Step 1: Get trend data

**If the input is a single category code:**

Call `mcp__claude_ai_Valency_Systems_Inc__get_publication_trends` with:
- `category`: the category code
- `granularity`: "year"
- `format`: "compact"

**If the input is a single keyword/phrase:**

Call `mcp__claude_ai_Valency_Systems_Inc__get_keyword_trends` with:
- `query`: the keyword
- `granularity`: "year"
- `format`: "compact"

**If the input contains multiple categories** (comma-separated or "vs"):

Call `mcp__claude_ai_Valency_Systems_Inc__get_publication_trends_batch` with:
- `categories`: array of the category codes
- `granularity`: "year"
- `format`: "compact"

**If the input contains multiple keywords** (comma-separated or "vs"):

Call `mcp__claude_ai_Valency_Systems_Inc__get_keyword_trends` once per keyword with:
- `query`: each keyword
- `granularity`: "year"
- `format`: "compact"

### Step 2: Get recent representative papers

Call `mcp__claude_ai_Valency_Systems_Inc__search_by_abstract` with:
- `query`: the keyword or category name (use the human-readable name for categories, e.g., "machine learning" for cs.LG)
- `limit`: 5
- `sort_by`: "relevance"

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
- When the field or topic first appeared in the corpus
- Key inflection points (years where volume jumped or dropped significantly)
- Current trajectory (accelerating, plateauing, declining)
- For comparisons: which topic is growing faster and when they diverged

### Representative Recent Papers

A numbered list of 3-5 papers from Step 2. For each:
- Title (with paper ID)
- Authors (first 3, then "et al.")
- Year

### Suggested Follow-ups

- `/valency:landscape <category>` — for a broader overview of the field
- `/valency:profile <author>` — for authors driving the trend
- `/valency:trends <other_keyword>` — to compare with related topics
