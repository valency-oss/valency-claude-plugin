---
name: reading-list
description: "Use when the user asks what a researcher should be reading, wants a curated bibliography for a researcher's interests, asks 'what should X read', 'find me adjacent work to X's research', or wants to know what literature surrounds an author's body of work. Triggers on reading-list, bibliography, or 'what should I read next' style requests anchored on a specific researcher. Also invokable as /valency:reading-list <author_name>."
---

# Researcher Reading List

Build a curated reading list for a researcher, organized by intellectual thread, by triangulating off their most representative recent and most-cited work.

## Input

The user provides an author name (e.g., "David W. Hogg", "Yoshua Bengio", "Jennifer Doudna").

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.
- Date filters (`start_date`, `end_date`) and recency sorts operate on `datestamp`; describe those results as record-date filtered or record-recent.
- Define one `comparison_key(name)` for every local author comparison: normalize `"Last, First"` to `"First Last"`, Unicode case-fold, transliterate common Latin ligatures, NFKD-fold diacritics, delete apostrophes and periods, then trim and collapse whitespace. Preserve returned names for display.

## Tool Chain

### Step 1: Resolve the focal researcher

Call `get_author_identity` with:
- `author` (string): the author name provided by the user

Inspect `status`, `resolved`, `person`, `warnings`, `candidates`, and `next_action`. Continue with person-specific analysis only when `status: resolved` and `person.author_id` are present. Otherwise present returned candidates or spelling suggestions, ask the user to choose, and re-call with `author_id`, a corrected `author`, or an ORCID or identifying paper as directed by `next_action`. For a candidate without an ID, use its ORCID or `recent_paper_id` plus `recent_source` as `paper_id` plus `source`, retaining the candidate name as `author`. Stop if the researcher remains unresolved; `name_only` does not identify one person.

When an author-tool response is `degraded` and requests `retry_unchanged`, retry once. If it remains degraded, preserve available data and warnings, and label missing data unavailable rather than zero. Use `person.display_name` for display when present and `person.author_id` as `author_id` in subsequent researcher calls.

`get_author_identity` returns the same profile as `get_author_profile`; reuse its `person`, `career`, `corpus`, and `coverage_note`. Corpus counts and categories come from `corpus.corpus_papers` and `corpus.top_categories`; whole-career metrics come from `career`. Missing blocks or null metrics are unavailable, not zero.

Build a focal alias-key set with `comparison_key` applied to the input name and non-null `person.display_name`.

This step is complete when one researcher has been selected and available profile data is scoped to corpus or career.

### Step 2: Get citation-ranked papers (career anchors)

Call `find_papers_by_researcher` with:
- `author_id` (string): `person.author_id` from Step 1
- `limit` (integer): 5
- `sort_by` (string): "citations"

Inspect `status`, `degraded`, `next_action`, `warnings`, `returned_count`, and citation coverage. Handle unresolved or degraded results as in Step 1; use only resolved results and exclude papers marked `identity_confirmed: false` from the focal seed pool. Treat the first result as the highest citation-ranked paper returned, not definitively the researcher's most-cited work when coverage is incomplete.

### Step 3: Get record-recent papers (current corpus direction)

Call `find_papers_by_researcher` with:
- `author_id` (string): the same `person.author_id`
- `limit` (integer): 15
- `sort_by` (string): "recency"

Inspect the same attribution fields as Step 2. `"recency"` orders papers by `datestamp`; keep the first 5 and describe them as the researcher's record-recent corpus work, not publication chronology.

### Step 4: Select 3–5 representative seed papers

From the combined Step 2 + Step 3 results, select 3 to 5 **seed papers** that best represent the author's distinct intellectual threads:

- Always include the highest citation-ranked returned paper, with its coverage qualification.
- Always include the first record-recent paper with a substantive abstract.
- Fill the remaining slots with papers whose titles, substantive abstracts, and source-specific categories establish distinct intellectual threads.

If two papers have nearly identical category lists and similar topics, pick only one.

### Step 5: Find similar papers for each seed

For each seed paper from Step 4, call `find_similar_papers` with:
- `paper_id` (string): the seed paper's ID
- `limit` (integer): 10
- `include_abstract` (boolean): true
- `max_authors` (integer): 500

A seed without an embedding returns a successful response with `count: 0`, `papers: []`, and a warning. Mark that seed as skipped and continue. Treat a genuine tool error separately and retain successful sibling threads.

### Step 6: Aggregate and clean

After all `find_similar_papers` calls complete:

1. **Tag each result** with the seed paper and its seed-specific similarity score.
2. **Deduplicate by paper family** using `(source, base_id ?? id)`, retaining every seed-specific score and provenance.
3. **Exclude known focal work** — drop selected seeds and papers appearing in either returned focal-researcher pool.
4. **Filter self-authorship** — compute `comparison_key` for every author and drop a paper if any key appears in the focal alias-key set.
5. **Reject unverifiable bylines** — drop papers whose `authors` list is empty or whose `authors_truncated` remains true after requesting 500.
6. **Group by seed** — partition the cleaned results by seed provenance and order each thread by that seed's own similarity score.

This step is complete when every retained recommendation has a complete returned byline, no known focal alias match, and all seed-specific provenance preserved.

### Step 7: Ground recommendation explanations

Explain each connection using the seed and recommendation titles, substantive abstracts, and source-specific categories. If an abstract is missing despite the explicit request, either label the narrower title/category basis or omit the explanation.

This step is complete when every recommendation explanation names the returned evidence that supports it.

## Output Format

### Researcher Summary

A short block:
- **Name**: selected display name
- **Identity**: ORCID when present; otherwise `person.author_id`
- **Papers in corpus**: `corpus.corpus_papers`, with `coverage_note` when available
- **Primary domains**: top 3 entries in `corpus.top_categories`

### Reading List by Thread

For each seed paper from Step 4, produce a thread section:

#### Thread N: <one-line characterization of the thread>

Anchored by the seed paper:
- **Seed**: [Title](url) (paper ID), source-aware date label, categories

Recommended reading (5–8 papers per thread, ordered by similarity score):

1. [Title](url) (paper ID) — first 3 authors, source-aware date label, category — one abstract-grounded sentence explaining why it matters here
2. ...

If a seed paper was skipped because it had no embedding, add a note under that thread: *"This seed had no embedding; no similar papers could be retrieved."*

### Cross-Thread Highlights

If any paper appeared as similar to **multiple** seeds, highlight it as a cross-thread find — these are often the most interesting recommendations because they sit at the intersection of the author's threads:

- [Title](url) (paper ID) — surfaced by Seed A *and* Seed C — abstract-grounded explanation of the intersection

If no cross-thread papers were found, omit this section.

### Suggested Follow-ups

- `/valency:profile <author>` — for any author that appears across multiple recommendations
- `/valency:similar <paper_id>` — to dig deeper into any specific recommendation
- `/valency:fresh-collaborators <author>` — if the user is interested in *who* (not what) to engage with next
