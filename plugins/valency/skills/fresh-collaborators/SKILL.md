---
name: fresh-collaborators
description: "Use when the user asks who a researcher should be talking to that they aren't already, wants to find new potential collaborators outside an existing network, asks 'who else is doing this work', 'who should X meet', 'who are the new faces in this field', or wants to expand a researcher's collaboration network beyond their current circle. Triggers on requests to find recent, relevant researchers who are NOT in an author's existing coauthor list. Also invokable as /valency:fresh-collaborators <author_name>."
---

# Fresh Collaborators

Find researchers doing recent (last 12–18 months), thematically relevant work who are **not** in the focal author's existing coauthor network. Useful for expanding a researcher's collaborator pool, suggesting first-author candidates for new projects, or surfacing people for an upcoming conference / visit.

## Input

The user provides an author name (e.g., "David W. Hogg", "Karl Friston").

Optional: a number of months for the recency window. If not specified, default to **18 months**.

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.
- Date filters (`start_date`, `end_date`) and recency sorts operate on `datestamp`. A strict first-submission recency claim requires a supported preprint source and a usable `first_submitted` value.
- Define one `comparison_key(name)` for every local author comparison: normalize `"Last, First"` to `"First Last"`, Unicode case-fold, transliterate common Latin ligatures, NFKD-fold diacritics, delete apostrophes and periods, then trim and collapse whitespace. Preserve returned names for display.

## Tool Chain

**Date discipline:** Compute the cutoff date as `today - <window_months>`, formatted as `YYYY-MM-DD`. Use this cutoff consistently in Steps 4–6.

### Step 1: Resolve the focal researcher

Call `get_author_identity` with:
- `author` (string): the author name

Inspect `warnings`, `career_metrics`, `resolved_name`, and `candidates`. If candidates are returned, select a lone ORCID-collision candidate only when its `confidence` is at least 0.95. Otherwise present the candidate evidence, ask the user to choose, and re-call with the chosen candidate's returned stable author identifier (or an ORCID or identifying paper when that identifier is null). If the identity remains unverifiable, explain that an identity-safe collaborator search cannot be completed and stop.

Use non-null `career_metrics.display_name` as the display name. For researcher calls, use the strongest available key: ORCID, then the stable author identifier returned in `career_metrics`, then the resolved name plus a user-supplied paper hint.

Call `get_author_profile` with the selected display name and resolved ORCID when present. Record its `resolved_name`, `stats_source`, warnings, corpus paper count, and source-specific categories.

This step is complete when one focal identity and one corpus name bucket are explicit and no candidate list remains unresolved.

### Step 2: Build the exclusion set (existing coauthor network)

If the profile `resolved_name` is null, explain that no corpus name bucket is available for the coauthor exclusion and stop.

Call `find_coauthors` with:
- `author` (string): the profile `resolved_name` from Step 1
- `limit` (integer): 100
- `exclude_mega_collaborations` (boolean): true

Build the **exclusion set** from `comparison_key(coauthor_norm)` for every returned row, plus the keys of the input name, identity `resolved_name`, non-null canonical display names, and profile `resolved_name`.

This endpoint returns at most the strongest 100 coauthor name buckets for one focal normalized-name bucket and excludes collaborations with more than 100 authors. Record the returned count. The exclusion is bounded weak-tie evidence, not a complete identity-resolved collaboration history.

### Step 3: Pull the focal author's recent papers (current themes)

Call `find_papers_by_researcher` with the strongest key from Step 1:
- ORCID, the tool's stable-author-identifier parameter, or `author`
- `limit` (integer): 20
- `sort_by` (string): "recency"

Inspect `candidates`, `disambiguation_status`, `warnings`, and every paper's `match_type`. Resolve reappearing candidates before continuing; stop on an unverifiable result. `"recency"` orders papers by `datestamp`, so pass all returned papers to Step 4 for the requested freshness check. Abstracts are included because Step 4 reads them.

### Step 4: Identify 2–4 current themes

A focal paper is usable for current themes only when it comes from arXiv, bioRxiv, or medRxiv and has a usable `first_submitted` satisfying `cutoff <= first_submitted <= today`. From the usable papers, identify **2 to 4 distinct themes** that characterize the author's in-window work. A theme is a short natural-language phrase (5–12 words) suitable as a semantic search query, not a category code.

Construct themes from substantive titles and abstracts. Every theme must be supported by at least two usable focal papers. If fewer than two usable papers remain, report that no in-window focal activity grounds current themes and stop. If only two defensible themes exist, use two.

Examples of well-formed themes:
- "Bayesian experimental design for cosmological survey forecasting"
- "Equivariant neural networks for stellar abundance prediction"
- "Metacognitive uncertainty in human and machine inference"

Bad themes (too narrow or too broad):
- "stars" (too broad)
- "Section 4 of the 2025 paper on REACH 21cm calibration" (too narrow / not a search query)

This step is complete when every search theme cites at least two in-window focal papers as evidence.

### Step 5: Search for recent work in each theme

For each theme from Step 4, call `semantic_search_papers` with:
- `query` (string): the theme phrase
- `start_date` (string): the cutoff date computed in the Date discipline section, `YYYY-MM-DD`
- `limit` (integer): 25
- `sort_by` (string): "relevance"
- `include_abstract` (boolean): false
- `enrich_citations` (boolean): false
- `max_authors` (integer): 500

`start_date` is only a server-side `datestamp` prefilter. Step 6 applies the supported-source `first_submitted` check. Requesting 500 authors minimizes unverifiable truncated bylines.

If a theme returns fewer than 5 papers, that theme is too narrow or the corpus is too sparse for the recency window. Note this in the output but do not stop.

### Step 6: Filter against the exclusion set

First, keep strict first-submission candidates only from arXiv, bioRxiv, or medRxiv with a usable `first_submitted` satisfying `cutoff <= first_submitted <= today`. Drop other sources and missing or out-of-window values from this freshness workflow. Count these exclusions separately for the coverage notes.

Then reject a paper when `authors` is empty. For each non-empty byline, compute `comparison_key` for every author and reject the paper if any key intersects the Step 2 exclusion set.

Also reject any paper with `authors_truncated: true`. Its byline remains incomplete even after requesting 500 authors, so exclusion cannot be verified. Count empty and truncated bylines separately for the coverage notes.

The remaining evidence supports only this statement: no returned byline author matches the focal or returned top-100 coauthor name buckets under the uniform comparison key.

### Step 7: Rank and categorize the fresh faces

For each remaining paper, identify the **first author** as the primary "fresh face" candidate (other authors are noted but secondary). For each unique first author across all surviving papers:

1. **Theme attribution.** Tag each candidate with which theme(s) surfaced them. Candidates surfaced by multiple themes are stronger matches and should be ranked higher.

2. **Deduplicate after identity resolution.** Keep same-name candidates separate until Step 8 returns a stable identity. Merge only entries established as the same identity; otherwise retain each author-paper pair.

3. **Junior/senior heuristic.** Without additional tool calls, infer junior vs senior from signals in the paper records: number of papers in the result set (1 = likely junior; many = likely established), and seniority cues from coauthors. Tag each candidate `[junior]`, `[senior]`, or `[unclear]`.

### Step 8: Verify the top candidates

For each of the top 5 candidates after ranking, call `get_author_identity` with:
- `author` (string): the candidate's name as it appears on the paper
- `paper_id` (string): the ID of one surfacing paper

The `paper_id` hint pins the lookup to that paper's author list. When `career_metrics` comes back, record `h_index`, `works_count`, and `current_institution`. They give a firmer read than the Step 7 heuristic: a handful of works suggests early career, a long record suggests established. Update the tag accordingly. If candidates remain unresolved, label the entry as an unverified byline name and keep it separate from every other same-name entry.

## Output Format

### Author Summary

A short block:
- **Focal author**: name (resolved), institution if known, total papers, primary domains
- **Returned coauthor exclusion set**: number of top coauthor name buckets returned, capped at 100 and excluding mega-collaboration edges
- **Recency window**: e.g. "Last 18 months (cutoff: 2024-10-07)"
- **Themes searched**: bullet list of the 2–4 themes from Step 4

### Fresh Faces

A ranked list of fresh-face candidates. Rank by: (a) number of distinct themes that surfaced them, then (b) similarity scores of their surfacing papers.

For each candidate:

#### N. Author Name `[junior|senior|unclear]`

- **Institution / h-index**: from Step 8 when available
- **Surfaced by themes**: theme A; theme B (if multiple)
- **Surfacing paper(s)**: [Title](url) (paper ID), source-aware date label, category
- **Why fresh**: no returned byline author matched the focal or returned top-100 coauthor name buckets under `comparison_key`; state that this is bounded weak-tie evidence
- **Why interesting**: one sentence on the connection to the focal author's current work

Show the top 10 candidates. If fewer than 10 survived, show all of them.

### Theme Coverage Notes

For each theme from Step 4, report the number of papers returned by the record-date-prefiltered search, supported-source papers inside the first-submission window, papers rejected for empty bylines, papers rejected for truncated bylines, and papers surviving the bounded top-100 exclusion. Sparse results mean only that this query and window produced little usable evidence.

### Suggested Follow-ups

- `/valency:profile <fresh_face_name>` — for a deeper look at any candidate
- `/valency:similar <surfacing_paper_id>` — to find more work in that vein
- `/valency:reading-list <focal_author>` — for the *what* to read alongside the *who* to meet
