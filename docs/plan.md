# Valency Claude Code Plugin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin with five slash commands that give researchers direct access to Valency's 36M+ paper corpus through opinionated research workflows.

**Architecture:** Each command maps to a skill (`skills/<name>/SKILL.md`) containing a detailed prompt that orchestrates Valency MCP tools. No code, no hooks — just markdown prompts, a plugin manifest, and a README.

**Tech Stack:** Claude Code plugin format (`.claude-plugin/plugin.json`, `skills/`, `CLAUDE.md`), Valency MCP server tools via Claude.ai connector.

---

## File Structure

```
valency-plugin/
  .claude-plugin/
    plugin.json              # Plugin manifest
  skills/
    profile/SKILL.md         # /valency:profile
    landscape/SKILL.md       # /valency:landscape
    similar/SKILL.md         # /valency:similar
    trends/SKILL.md          # /valency:trends
    network/SKILL.md         # /valency:network
  CLAUDE.md                  # Plugin-level instructions
  README.md                  # User-facing documentation
  ISSUES.md                  # Already exists — open issues tracker
  package.json               # npm-style metadata
```

Every file is new except `ISSUES.md` (already exists) and `prd.md` (untouched).

---

### Task 1: Plugin scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `package.json`
- Create: `CLAUDE.md`

- [ ] **Step 1: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "valency",
  "description": "Search, profile, and analyze 36M+ research papers across arXiv, PubMed, bioRxiv, and medRxiv with semantic embeddings.",
  "version": "0.1.0",
  "author": {
    "name": "Valency Systems Inc"
  },
  "homepage": "https://valency.io",
  "license": "MIT",
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

- [ ] **Step 2: Create `package.json`**

```json
{
  "name": "valency",
  "version": "0.1.0",
  "type": "module"
}
```

- [ ] **Step 3: Create `CLAUDE.md`**

```markdown
# Valency Plugin

This plugin provides research corpus tools via the Valency MCP connector.

## Prerequisites

The Valency MCP connector must be configured in the user's Claude.ai account.
All data retrieval goes through MCP tools prefixed with `mcp__claude_ai_Valency_Systems_Inc__`.

## Rules

- Never fabricate paper titles, authors, abstracts, or metadata. All paper data must come from MCP tool results.
- If an MCP tool returns no results, say so plainly and suggest the user try a different query.
- Produce clean, scannable output with consistent markdown formatting.
- When suggesting follow-up commands, use the `/valency:<command>` format.
```

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json package.json CLAUDE.md
git commit -m "feat: scaffold plugin manifest, package.json, and CLAUDE.md"
```

---

### Task 2: /valency:profile skill

**Files:**
- Create: `skills/profile/SKILL.md`

- [ ] **Step 1: Create `skills/profile/SKILL.md`**

```markdown
---
name: profile
description: "Build a comprehensive researcher profile — publication history, research domains, top papers, and collaborators. Usage: /valency:profile <author_name>"
---

# Researcher Profile

Build a comprehensive profile for the given researcher.

## Input

The user provides an author name (e.g., "Yoshua Bengio", "Y. LeCun", "Sara Walker").

## Tool Chain

Execute these steps in order. Use the full MCP tool names shown below.

### Step 1: Get author profile

Call `mcp__claude_ai_Valency_Systems_Inc__get_author_profile` with:
- `author`: the author name provided by the user

This returns summary stats including top categories, publication timeline, co-author count, and total papers.

If no results are found, tell the user the author was not found and suggest checking the spelling or trying a partial name. Stop here.

### Step 2: Get full publication list

Call `mcp__claude_ai_Valency_Systems_Inc__search_by_author` with:
- `author`: the author name
- `limit`: 10
- `sort_by`: "citations"
- `strict_mode`: "fuzzy"

This returns the author's top papers sorted by citation count.

### Step 3: Get research domain distribution

Call `mcp__claude_ai_Valency_Systems_Inc__batch_author_categories` with:
- `authors`: an array containing the author name
- `max_categories`: 10

This returns the category distribution for the author's publications.

### Step 4: Get top collaborators

Call `mcp__claude_ai_Valency_Systems_Inc__find_coauthors` with:
- `author`: the author name
- `limit`: 10

This returns the author's most frequent collaborators with co-publication counts.

## Output Format

Present the results in this structure:

### Summary

A brief block with:
- **Name**: full name as it appears in the corpus
- **Total papers**: count from Step 1
- **Active years**: first paper year to last paper year
- **Primary domains**: top 3 categories from Step 3

### Research Domains

A table of the top 5 categories from Step 3:

| Category | Papers |
|----------|--------|
| cs.LG    | 42     |
| ...      | ...    |

### Top Papers

A numbered list of up to 10 papers from Step 2. For each paper show:
- Title (with paper ID)
- Year
- Categories

### Top Collaborators

A table of up to 5 collaborators from Step 4:

| Collaborator | Co-authored papers |
|--------------|-------------------|
| Name         | 15                |
| ...          | ...               |

### Suggested Follow-ups

- `/valency:network <author_name>` — map their collaboration network
- `/valency:similar <paper_id>` — find papers similar to their top work (use the ID of their most-cited paper)
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 skills/profile/SKILL.md`
Expected: YAML frontmatter with `name: profile` and `description:` on the first lines.

- [ ] **Step 3: Commit**

```bash
git add skills/profile/SKILL.md
git commit -m "feat: add /valency:profile skill"
```

---

### Task 3: /valency:landscape skill

**Files:**
- Create: `skills/landscape/SKILL.md`

- [ ] **Step 1: Create `skills/landscape/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 skills/landscape/SKILL.md`
Expected: YAML frontmatter with `name: landscape`.

- [ ] **Step 3: Commit**

```bash
git add skills/landscape/SKILL.md
git commit -m "feat: add /valency:landscape skill"
```

---

### Task 4: /valency:similar skill

**Files:**
- Create: `skills/similar/SKILL.md`

- [ ] **Step 1: Create `skills/similar/SKILL.md`**

```markdown
---
name: similar
description: "Find semantically similar papers using neural embeddings. Usage: /valency:similar <paper_id_or_title>"
---

# Similar Papers

Find papers semantically similar to a given paper.

## Input

The user provides either:
- A paper identifier (arXiv ID like `2301.07041`, DOI, or other structured ID — recognized by the absence of spaces and presence of numbers/dots/slashes)
- A paper title (contains spaces, reads as natural language)

## Tool Chain

### Step 1: Resolve paper ID (if needed)

**If the input looks like a paper ID** (no spaces, contains numbers/dots):

Call `mcp__claude_ai_Valency_Systems_Inc__get_paper_by_id` with:
- `paper_id`: the provided ID

If no paper is found, tell the user the ID was not recognized and suggest searching by title instead. Stop here.

**If the input looks like a title** (contains spaces):

Call `mcp__claude_ai_Valency_Systems_Inc__search_by_title` with:
- `query`: the provided title
- `limit`: 5

Present the top matches and ask the user to confirm which paper they mean, unless only one result is returned or the top result is a near-exact title match. Use the confirmed paper's ID for the next step.

If no results are found, suggest the user check the title or try keywords from it. Stop here.

### Step 2: Find similar papers

Call `mcp__claude_ai_Valency_Systems_Inc__find_similar_papers` with:
- `paper_id`: the resolved paper ID
- `limit`: 10

If the paper has no embedding and returns an error, tell the user that semantic similarity is not available for this paper and suggest trying `semantic_search_papers` with keywords from its abstract instead. Stop here.

### Step 3: Enrich results (if needed)

The results from Step 2 already include metadata (title, authors, abstract, categories). If any result is missing abstract or author data, call `mcp__claude_ai_Valency_Systems_Inc__get_paper_by_id` for those papers.

## Output Format

### Source Paper

Display the seed paper's details:
- **Title**: full title
- **Authors**: first 5, then "et al." if more
- **Year**: publication year
- **Source**: which server (arXiv, bioRxiv, etc.)
- **Abstract**: first 2-3 sentences

### Similar Papers

A numbered list ranked by similarity. For each paper:
- **Title** (with paper ID)
- **Authors**: first 3, then "et al." if more
- **Year**
- **Category**
- **Abstract summary**: one sentence capturing the paper's contribution

### Suggested Follow-ups

- `/valency:profile <author>` — for any author that appears in multiple similar papers
- `/valency:similar <paper_id>` — to continue exploring from any listed paper
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 skills/similar/SKILL.md`
Expected: YAML frontmatter with `name: similar`.

- [ ] **Step 3: Commit**

```bash
git add skills/similar/SKILL.md
git commit -m "feat: add /valency:similar skill"
```

---

### Task 5: /valency:trends skill

**Files:**
- Create: `skills/trends/SKILL.md`

- [ ] **Step 1: Create `skills/trends/SKILL.md`**

```markdown
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
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 skills/trends/SKILL.md`
Expected: YAML frontmatter with `name: trends`.

- [ ] **Step 3: Commit**

```bash
git add skills/trends/SKILL.md
git commit -m "feat: add /valency:trends skill"
```

---

### Task 6: /valency:network skill

**Files:**
- Create: `skills/network/SKILL.md`

- [ ] **Step 1: Create `skills/network/SKILL.md`**

```markdown
---
name: network
description: "Map a researcher's collaboration network — direct collaborators, second-degree connections, and cross-domain bridges. Usage: /valency:network <author_name>"
---

# Collaboration Network

Map a researcher's collaboration network.

## Input

The user provides an author name (e.g., "Yoshua Bengio").

## Tool Chain

### Step 1: Get author baseline

Call `mcp__claude_ai_Valency_Systems_Inc__get_author_profile` with:
- `author`: the author name

If no results are found, tell the user the author was not found and suggest checking the spelling. Stop here.

Note the author's top categories from this result — you'll need them to identify cross-domain bridges.

### Step 2: Get direct collaborators

Call `mcp__claude_ai_Valency_Systems_Inc__find_coauthors` with:
- `author`: the author name
- `limit`: 20

This returns collaborators ranked by co-publication count. Note the top 5 collaborators for the next step. Use the `coauthor_norm` field (normalized name) when passing names to subsequent tool calls.

### Step 3: Get second-degree connections

For each of the top 5 collaborators from Step 2, call `mcp__claude_ai_Valency_Systems_Inc__find_coauthors` with:
- `author`: the collaborator's normalized name (`coauthor_norm`)
- `limit`: 10

Collect all second-degree collaborators. Remove any that are already direct collaborators of the focal author (from Step 2) or the focal author themselves.

### Step 4: Compare focal author with top collaborators

Call `mcp__claude_ai_Valency_Systems_Inc__compare_authors` with:
- `authors`: array containing the focal author name and up to 4 of their top collaborators (max 5 total, tool requires 2-10)

This returns side-by-side profiles with category overlap information.

## Output Format

### Network Summary

A brief paragraph:
- Author name and total direct collaborators count
- Primary research domains (from Step 1)

### Direct Collaborators

A table of collaborators from Step 2 (top 10):

| Collaborator | Co-authored papers | Primary domain |
|--------------|-------------------|----------------|
| Name         | 15                | cs.LG          |
| ...          | ...               | ...            |

The "Primary domain" column comes from Step 4 comparison data for the top collaborators. For collaborators not included in the comparison, omit the domain or mark as "—".

### Second-Degree Connections

A list of notable second-degree connections from Step 3 — people who collaborate with the focal author's collaborators but not directly with the focal author. Show up to 10, prioritizing those who appear via multiple collaborators:

- **Name** (connected through: Collaborator A, Collaborator B) — primary domain if known

### Cross-Domain Bridges

Highlight collaborators from Step 2 whose primary domain (from Step 4) differs from the focal author's primary domain. These represent interdisciplinary connections:

- **Name** (domain: q-bio.BM) — bridges to computational biology

If no cross-domain collaborators are found, note that the author's network is concentrated within their primary domain.

### Suggested Follow-ups

- `/valency:profile <collaborator>` — for any interesting collaborator
- `/valency:network <collaborator>` — to explore a collaborator's own network
- `/valency:similar <paper_id>` — for co-authored papers of interest
```

- [ ] **Step 2: Verify the skill file is valid**

Run: `head -5 skills/network/SKILL.md`
Expected: YAML frontmatter with `name: network`.

- [ ] **Step 3: Commit**

```bash
git add skills/network/SKILL.md
git commit -m "feat: add /valency:network skill"
```

---

### Task 7: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# Valency — Research Corpus Plugin for Claude Code

Search, profile, and analyze 36M+ research papers across arXiv, PubMed, bioRxiv, and medRxiv directly from Claude Code.

## Prerequisites

You need the Valency MCP connector configured in your Claude.ai account. Add it at [claude.ai/settings/connectors](https://claude.ai/settings/connectors) using the URL `https://labs.valency.io/mcp`.

## Installation

```bash
claude plugin install valency
```

## Commands

### /valency:profile \<author_name\>

Build a comprehensive researcher profile: publication history, research domains, top papers, and collaborators.

```
/valency:profile Yoshua Bengio
```

### /valency:landscape \<topic_or_category\>

Generate a landscape overview of a research field: publication trends, top authors, subdomains, and notable papers.

```
/valency:landscape cs.LG
/valency:landscape protein folding
```

### /valency:similar \<paper_id_or_title\>

Find semantically similar papers using neural embeddings.

```
/valency:similar 1706.03762
/valency:similar Attention Is All You Need
```

### /valency:trends \<keyword_or_category\>

Show how a topic or category has evolved over time: publication volumes, inflection points, and representative papers. Supports comparisons with comma-separated inputs.

```
/valency:trends cs.AI
/valency:trends CRISPR
/valency:trends cs.LG, cs.CL
```

### /valency:network \<author_name\>

Map a researcher's collaboration network: direct collaborators, second-degree connections, and cross-domain bridges.

```
/valency:network Yoshua Bengio
```

## Data Sources

| Source | Papers |
|--------|--------|
| arXiv  | 4.6M   |
| PubMed | 31.1M  |
| bioRxiv| 402K   |
| medRxiv| 100K   |

## License

MIT
```

- [ ] **Step 2: Verify the README renders correctly**

Run: `head -20 README.md`
Expected: Title, description, and prerequisites section visible.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "feat: add README with command documentation"
```

---

### Task 8: Smoke test all commands

This task verifies each skill works end-to-end by running each command once.

- [ ] **Step 1: Test /valency:profile**

Run: `/valency:profile Yoshua Bengio`
Expected: Formatted profile with summary, domains, papers, collaborators, and follow-up suggestions.

- [ ] **Step 2: Test /valency:landscape with category**

Run: `/valency:landscape cs.LG`
Expected: Field summary, trend table, top authors, subdomains, notable papers, observations.

- [ ] **Step 3: Test /valency:landscape with free text**

Run: `/valency:landscape protein folding`
Expected: Same structure as above, using semantic search instead of category search.

- [ ] **Step 4: Test /valency:similar with paper ID**

Run: `/valency:similar 1706.03762`
Expected: Source paper details (Attention Is All You Need) and 10 similar papers.

- [ ] **Step 5: Test /valency:similar with title**

Run: `/valency:similar Attention Is All You Need`
Expected: Title resolution, then similar papers list.

- [ ] **Step 6: Test /valency:trends with category**

Run: `/valency:trends cs.AI`
Expected: Year-by-year table, narrative summary, representative papers.

- [ ] **Step 7: Test /valency:trends with comparison**

Run: `/valency:trends cs.LG, cs.CL`
Expected: Side-by-side table comparing both categories.

- [ ] **Step 8: Test /valency:network**

Run: `/valency:network Yoshua Bengio`
Expected: Direct collaborators, second-degree connections, cross-domain bridges.

- [ ] **Step 9: Final commit**

```bash
git add -A
git commit -m "chore: finalize v0.1.0"
```
