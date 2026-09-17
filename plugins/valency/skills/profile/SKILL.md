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

### Step 1: Resolve the researcher

Call `get_author_identity` with:
- `author` (string): the author name provided by the user

Inspect `status`, `resolved`, `person`, `warnings`, `candidates`, and `next_action`. Continue with person-specific analysis only when `status: resolved` and `person.author_id` are present. Otherwise present returned candidates or spelling suggestions, ask the user to choose, and re-call with `author_id`, a corrected `author`, or an ORCID or identifying paper as directed by `next_action`. For a candidate without an ID, use its ORCID or `recent_paper_id` plus `recent_source` as `paper_id` plus `source`, retaining the candidate name as `author`. Stop if the researcher remains unresolved; `name_only` does not identify one person.

When an author-tool response is `degraded` and requests `retry_unchanged`, retry once. If it remains degraded, preserve available data and warnings, and label missing data unavailable rather than zero. Use `person.display_name` for display when present and `person.author_id` as `author_id` in subsequent researcher calls.

This step is complete when one researcher has been selected.

### Step 2: Read the corpus profile

`get_author_identity` returns the same profile as `get_author_profile`; reuse its `person`, `career`, `corpus`, and `coverage_note`. Corpus counts and categories come from `corpus.corpus_papers` and `corpus.top_categories`; whole-career metrics come from `career`. Missing blocks or null metrics are unavailable, not zero.

This step is complete when each profile claim has its corpus or career scope and material warnings attached.

### Step 3: Get citation-ranked papers

Call `find_papers_by_researcher` with:
- `author_id` (string): `person.author_id` from Step 1
- `limit` (integer): 10
- `sort_by` (string): "citations"

Inspect `status`, `degraded`, `next_action`, `warnings`, `returned_count`, and citation coverage. Handle unresolved or degraded results as in Step 1. Papers marked `identity_confirmed: false` are name-only matches, not established work of the selected researcher. Describe the first result as the highest citation-ranked paper returned, not definitively the researcher's most-cited paper when citation counts are incomplete.

This step is complete when every returned paper is attributed to the selected identity or carries its explicit attribution qualification.

### Step 4: Get top collaborators

Call `find_coauthors` with:
- `author_id` (string): `person.author_id` from Step 1
- `limit` (integer): 10
- `include_mega_collaborations` (boolean): false

Handle unresolved or degraded results as in Step 1. Rows contain `coauthor`, `coauthor_id`, and `shared_papers`. Display `coauthor` when available, otherwise `coauthor_id`. This is a top-N list of identity-linked collaborators in this corpus, excluding papers with more than 50 authors, not a complete collaboration history.

## Output Format

Present the results in this structure:

### Summary

A brief block:
- **Name**: selected display name
- **Identity**: ORCID when present; otherwise `person.author_id`
- **Institution**: `career.current_institution.institution` (omit if absent)
- **h-index**: `career.h_index` (omit if absent)
- **Papers in corpus**: `corpus.corpus_papers`. When `career.career_works` is present, add the separately scoped whole-career works count and preserve `coverage_note`.
- **Observed paper activity**: `corpus.first_paper` to `corpus.last_paper`, labeled as corpus activity with the mixed first-submission/record-date caveat
- **Primary domains**: top 3 entries in `corpus.top_categories`

### Research Domains

A table of the top 5 entries in `corpus.top_categories`:

| Category | Papers |
|----------|--------|
| cs.LG    | 42     |
| ...      | ...    |

### Top Papers

A numbered list of up to 10 papers from Step 3. State `returned_count`, `status`, citation coverage, and material warnings. For each paper show:
- [Title](url) (paper ID)
- Source-aware date label
- Citations (`citation_count`; omit if null)
- Categories

### Top Collaborators

A table of up to 5 collaborators from Step 4:

| Collaborator | Co-authored papers |
|--------------|-------------------|
| Name         | 15                |
| ...          | ...               |

### Suggested Follow-ups

- `/valency:network <author_name>` — map their collaboration network
- `/valency:reading-list <author_name>` — a curated bibliography around their work
- `/valency:similar <paper_id>` — continue from the highest citation-ranked returned paper
