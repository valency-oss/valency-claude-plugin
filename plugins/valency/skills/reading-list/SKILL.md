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
- Author strings may be "First Last" (arXiv) or "Last, First" (PubMed). Before comparing names, lowercase both and convert "last, first" to "first last".

## Tool Chain

### Step 1: Resolve the focal researcher

Call `get_author_identity` with:
- `author` (string): the author name provided by the user

Inspect `warnings`, `career_metrics`, `resolved_name`, and `candidates`. If candidates are returned, select a lone ORCID-collision candidate only when its `confidence` is at least 0.95. Otherwise present the candidate evidence, ask the user to choose, and re-call with the chosen candidate's returned stable author identifier (or an ORCID or identifying paper when that identifier is null). Stop if the identity remains unverifiable.

Use non-null `career_metrics.display_name` as the display name. For researcher calls, use the strongest available key: ORCID, then the stable author identifier returned in `career_metrics`, then the resolved name plus a user-supplied paper hint.

Call `get_author_profile` with the selected display name and the resolved ORCID when present. Record `resolved_name`, `stats_source`, warnings, corpus paper count, and source-specific categories.

This step is complete when one researcher has been selected, no candidate list remains unresolved, and the corpus profile's provenance is recorded.

### Step 2: Get citation-ranked papers (career anchors)

Call `find_papers_by_researcher` with the strongest key from Step 1 and:
- `limit` (integer): 5
- `sort_by` (string): "citations"

Inspect `candidates`, `disambiguation_status`, `warnings`, `returned_count`, and citation coverage. Resolve any reappearing candidates before using the papers. Treat the first result as the highest citation-ranked paper returned, not definitively the researcher's most-cited work when coverage is incomplete.

### Step 3: Get record-recent papers (current corpus direction)

Call `find_papers_by_researcher` with the same identity and:
- `limit` (integer): 15
- `sort_by` (string): "recency"

Inspect the same attribution fields as Step 2. `"recency"` orders papers by `datestamp`; keep the first 5 and describe them as the researcher's record-recent corpus work, not publication chronology.

### Step 4: Select 3–5 representative seed papers

From the combined Step 2 + Step 3 results, select 3 to 5 **seed papers** that best represent the author's distinct intellectual threads:

- Always include the highest citation-ranked returned paper, with its coverage qualification.
- Always include the first record-recent paper with a substantive abstract.
- Fill the remaining slots by picking papers whose category lists differ — i.e. cover different threads of the author's work, not five papers in the same subfield.

If two papers have nearly identical category lists and similar topics, pick only one.

### Step 5: Find similar papers for each seed

For each seed paper from Step 4, call `find_similar_papers` with:
- `paper_id` (string): the seed paper's ID
- `limit` (integer): 10
- `include_abstract` (boolean): false

If a seed paper has no embedding and the call returns an error, skip that seed and continue with the others. Note the skip in the output.

### Step 6: Aggregate and clean

After all `find_similar_papers` calls complete:

1. **Tag each result** with the seed paper that surfaced it.
2. **Deduplicate** — if a paper appears in multiple seeds' similar lists, keep the entry with the highest similarity score and merge the seed tags.
3. **Filter out self-citations** — drop any paper whose author list contains the focal author. Normalize names as described in Conventions, then match against `resolved_name` and, if present, `career_metrics.display_name`.
4. **Group by seed** — partition the cleaned results by which seed paper(s) surfaced them. This grouping defines the reading-list "threads."

## Output Format

### Researcher Summary

A short block:
- **Name**: selected display name
- **Identity**: ORCID when present; otherwise the returned disambiguation qualification
- **Papers in corpus**: from the Step 1 profile, labeled with `stats_source`
- **Primary domains**: top 3 source-specific categories from the Step 1 profile

### Reading List by Thread

For each seed paper from Step 4, produce a thread section:

#### Thread N: <one-line characterization of the thread>

Anchored by the seed paper:
- **Seed**: [Title](url) (paper ID), source-aware date label, categories

Recommended reading (5–8 papers per thread, ordered by similarity score):

1. [Title](url) (paper ID) — first 3 authors, source-aware date label, category — one-sentence reason it matters here
2. ...

If a seed paper was skipped because it had no embedding, add a note under that thread: *"This seed had no embedding; no similar papers could be retrieved."*

### Cross-Thread Highlights

If any paper appeared as similar to **multiple** seeds, highlight it as a cross-thread find — these are often the most interesting recommendations because they sit at the intersection of the author's threads:

- [Title](url) (paper ID) — surfaced by Seed A *and* Seed C — why this matters

If no cross-thread papers were found, omit this section.

### Suggested Follow-ups

- `/valency:profile <author>` — for any author that appears across multiple recommendations
- `/valency:similar <paper_id>` — to dig deeper into any specific recommendation
- `/valency:fresh-collaborators <author>` — if the user is interested in *who* (not what) to engage with next
