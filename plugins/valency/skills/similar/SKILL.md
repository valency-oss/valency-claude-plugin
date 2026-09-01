---
name: similar
description: "Use when the user wants to find papers similar to a specific paper, asks 'what's related to this paper', 'find me more like this', or wants to explore the neighborhood around a known paper. Triggers on paper IDs, arXiv IDs, DOIs, or paper titles followed by a similarity request. Also invokable as /valency:similar <paper_id_or_title>."
---

# Similar Papers

Find papers semantically similar to a given paper, and the most-cited work that builds on it.

## Input

The user provides either:
- A paper identifier — one of:
  - arXiv ID (e.g., `2301.07041` or `2301.07041v3`)
  - DOI (e.g., `10.1101/2024.01.15.575423` or any `10.xxxx/...` pattern)
  - PubMed ID / PMID (digits only, e.g., `26360422`)
  - PubMed Central ID (e.g., `PMC3855844`, case-insensitive)
- A paper title (contains spaces, reads as natural language)

**Identifier detection rules:**
- If the input is digits only → treat as PMID
- If the input is `PMC` followed by digits → treat as a PMC ID
- If the input matches `10.xxxx/...` → treat as DOI (covers bioRxiv, medRxiv, and other DOI-minted sources)
- If the input matches a numeric pattern with dots like `NNNN.NNNNN` (optionally with `vN` suffix) → treat as arXiv ID
- Otherwise → treat as a title and resolve via search

Do not assume all bioRxiv records use the `10.1101/...` prefix. Newer records may use other DOI prefixes.

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Report a paper's year from `first_submitted`, never `datestamp`.
- PubMed papers carry MeSH headings in `categories` rather than category codes. Show them as-is.

## Tool Chain

### Step 1: Resolve paper ID (if needed)

**If the input is a paper ID** (arXiv ID, DOI, PMID, or PMC ID):

Call `get_paper_by_id` with:
- `paper_id` (string): the provided ID

If no paper is found, tell the user the ID was not recognized and suggest searching by title instead. Stop here.

**If the input looks like a title** (contains spaces):

Call `search_by_title` with:
- `query` (string): the provided title
- `limit` (integer): 5

Present the top matches and ask the user to confirm which paper they mean, unless only one result is returned or the top result is a near-exact title match. Use the confirmed paper's ID for the next step.

If no results are found, suggest the user check the title or try keywords from it. Stop here.

### Step 2: Find similar papers

Call `find_similar_papers` with:
- `paper_id` (string): the resolved paper ID
- `limit` (integer): 10

If the user asked for similar work on a specific source (e.g., "on bioRxiv"), add `result_source` (string) with that source name. Otherwise omit it so results span all sources.

If the paper has no embedding and returns an error, tell the user that semantic similarity is not available for this paper and suggest trying `semantic_search_papers` with keywords from its abstract instead. Still run Step 3; forward citations do not need an embedding.

### Step 3: Find the most-cited papers that cite it

Call `get_citing_papers` with:
- `paper_id` (string): the resolved paper ID
- `limit` (integer): 5
- `sort_by` (string): "citations"

If `openalex_work_id` is null or `results` is empty, the paper is not yet in the citation graph. Omit the Cited By section.

### Step 4: Enrich results (if needed)

The results from Step 2 already include metadata (title, authors, abstract, categories). If any result is missing abstract or author data, call `get_paper_by_id` for those papers.

## Output Format

### Source Paper

Display the seed paper's details:
- **Title**: [Title](url) (paper ID)
- **Authors**: first 5, then "et al." if more
- **Year**: from `first_submitted`
- **Source**: which server (arXiv, bioRxiv, PubMed, etc.)
- **Abstract**: first 2-3 sentences

### Similar Papers

A numbered list ranked by similarity. For each paper:
- [Title](url) (paper ID)
- **Authors**: first 3, then "et al." if more
- **Year**: from `first_submitted`
- **Category**
- **Abstract summary**: one sentence capturing the paper's contribution

### Cited By

Omit if Step 3 returned nothing. Otherwise state `total_citing_papers`, then list the 5 results:
- **Title** — first 3 authors, `publication_year`, `cited_by_count` citations
- If `in_corpus` is true, append the `valency_paper_id` so the user can explore it

### Suggested Follow-ups

- `/valency:profile <author>` — for any author that appears in multiple similar papers
- `/valency:similar <paper_id>` — to continue exploring from any listed paper, including any in-corpus citing paper
