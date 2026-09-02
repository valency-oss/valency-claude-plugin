---
name: profile
description: "Use when the user asks about a researcher's work, publications, research areas, collaborators, or academic profile. Triggers on questions like 'who is X', 'what does X work on', 'show me X's papers', or 'tell me about X' in a research context. Also invokable as /valency:profile <author_name>."
---

# Researcher Profile

Build a comprehensive profile for the given researcher.

## Input

The user provides an author name (e.g., "Yoshua Bengio", "Y. LeCun", "Sara Walker").

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.
- This skill does not display abstracts, so pass `include_abstract: false` on search calls.

## Tool Chain

Execute these steps in order.

### Step 1: Get author profile

Call `get_author_profile` with:
- `author` (string): the author name provided by the user

This returns `resolved_name`, a `summary` (papers in corpus, first and last paper dates, unique coauthor count), a `categories` list of `{category, count}` pairs, a year-by-year `timeline`, and `career_metrics` from the upstream citation graph: `display_name`, `orcid`, `h_index`, `works_count`, `cited_by_count`, `affiliations`, and `current_institution`. `career_metrics` may be absent for authors the graph does not know.

If no results are found, tell the user the author was not found and suggest checking the spelling or trying a partial name. Stop here.

**Fragmented names.** Counts in this response are keyed to one exact name string. If `warnings` mentions fragmentation across name variants and `career_metrics.orcid` is present, take the ORCID path in Step 2 so the paper list covers every variant.

### Step 2: Get top papers

If Step 1 flagged fragmentation and returned an ORCID, call `find_papers_by_researcher` with:
- `orcid` (string): the ORCID from `career_metrics`
- `limit` (integer): 10
- `sort_by` (string): "citations"

Otherwise call `search_by_author` with:
- `author` (string): the author name
- `limit` (integer): 10
- `sort_by` (string): "citations"
- `strict_mode` (string): "fuzzy"
- `include_abstract` (boolean): false

Either call returns the author's top papers sorted by citation count.

### Step 3: Get top collaborators

Call `find_coauthors` with:
- `author` (string): the author name
- `limit` (integer): 10
- `exclude_mega_collaborations` (boolean): true

This returns the author's most frequent collaborators with co-publication counts. Excluding papers with more than 100 authors keeps survey and consortium rosters from crowding out real collaborators.

## Output Format

Present the results in this structure:

### Summary

A brief block:
- **Name**: `career_metrics.display_name` if present, otherwise the name as it appears in the corpus
- **Institution**: `career_metrics.current_institution` (omit if absent)
- **ORCID**: from `career_metrics` (omit if absent)
- **h-index**: from `career_metrics` (omit if absent)
- **Papers in corpus**: `summary.total_papers`. When `career_metrics.works_count` is present, add "of N works upstream" so the reader can see how much of the career the corpus covers.
- **Observed paper activity**: `summary.first_paper` to `summary.last_paper`, labeled as corpus activity with the mixed first-submission/record-date caveat
- **Primary domains**: top 3 categories from Step 1

### Research Domains

A table of the top 5 categories from Step 1:

| Category | Papers |
|----------|--------|
| cs.LG    | 42     |
| ...      | ...    |

### Top Papers

A numbered list of up to 10 papers from Step 2. For each paper show:
- [Title](url) (paper ID)
- Source-aware date label
- Citations (`citation_count`; omit if null)
- Categories

### Top Collaborators

A table of up to 5 collaborators from Step 3:

| Collaborator | Co-authored papers |
|--------------|-------------------|
| Name         | 15                |
| ...          | ...               |

### Suggested Follow-ups

- `/valency:network <author_name>` — map their collaboration network
- `/valency:reading-list <author_name>` — a curated bibliography around their work
- `/valency:similar <paper_id>` — find papers similar to their top work (use the ID of their most-cited paper)
