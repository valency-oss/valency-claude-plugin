---
name: network
description: "Use when the user asks about a researcher's collaborators, co-authors, research network, wants to map who works with whom, or wants to see how a researcher's focus has diverged from their collaborators. Triggers on questions like 'who does X collaborate with', 'show me X's network', 'find connections between researchers', or 'how has X's work drifted from their coauthors'. Also invokable as /valency:network <author_name>."
---

# Collaboration Network

Map a researcher's collaboration network.

## Input

The user provides an author name (e.g., "Yoshua Bengio").

## Conventions

- Link every paper as `[Title](url)` using the paper's `url` field, followed by its ID.
- Use source-aware date labels. `datestamp` is the source record/update date. For arXiv, bioRxiv, and medRxiv, non-null `first_submitted` is a first-submission estimate; for every other or unknown source, it is a record-derived month estimate. None is a publication date or year.

## Tool Chain

### Step 1: Resolve the focal researcher and baseline

Call `get_author_identity` with `author` set to the author name.

Inspect `status`, `resolved`, `person`, `warnings`, `candidates`, and `next_action`. Continue with person-specific analysis only when `status: resolved` and `person.author_id` are present. Otherwise present returned candidates or spelling suggestions, ask the user to choose, and re-call with `author_id`, a corrected `author`, or an ORCID or identifying paper as directed by `next_action`. For a candidate without an ID, use its ORCID or `recent_paper_id` plus `recent_source` as `paper_id` plus `source`, retaining the candidate name as `author`. Stop if the researcher remains unresolved; `name_only` does not identify one person.

When an author-tool response is `degraded` and requests `retry_unchanged`, retry once. If it remains degraded, preserve available data and warnings, and label missing data unavailable rather than zero. Use `person.display_name` for display when present and `person.author_id` as `author_id` in subsequent researcher calls.

`get_author_identity` returns the same profile as `get_author_profile`; reuse its `person`, `career`, `corpus`, and `coverage_note`. Corpus counts and categories come from `corpus.corpus_papers` and `corpus.top_categories`; whole-career metrics come from `career`. Missing blocks or null metrics are unavailable, not zero.

This step is complete when one focal researcher has been identified.

### Step 2: Get direct collaborators

Call `find_coauthors` with:
- `author_id` (string): `person.author_id` from Step 1
- `limit` (integer): 20
- `include_mega_collaborations` (boolean): false

Handle unresolved or degraded results as in Step 1. This returns identity-linked collaborators ranked by shared corpus paper count, ignoring papers with more than 50 authors. Note the top 5 collaborators for the next step. Use `coauthor_id` for subsequent calls and `coauthor` for display, falling back to the ID when the name is unavailable.

### Step 3: Get second-degree connections

For each of the top 5 collaborators from Step 2, call `find_coauthors` with:
- `author_id` (string): the collaborator's `coauthor_id`
- `limit` (integer): 10
- `include_mega_collaborations` (boolean): false

Handle each result as in Step 1 and collect available second-degree collaborators. Deduplicate and remove direct collaborators or the focal author by `coauthor_id` / `person.author_id`. Describe connections as absent from the returned direct list, not proven absent from the complete network.

### Step 4: Compare collaborator profiles

Call `compare_authors` with `authors` containing the focal researcher and up to 4 top collaborators from Step 2, each as `{"author_id": "<returned ID>"}`. Skip the comparison if no collaborator was returned.

Inspect top-level warnings and each profile's `status`, `degraded`, `next_action`, `person`, `career`, and `corpus`. Handle unresolved or degraded entries as in Step 1 and compute comparisons only from available resolved data.

This step is complete when every comparison is tied to the returned researcher IDs and its corpus or career scope is explicit.

### Step 5: Compute divergence (no tool call)

For each top collaborator from Step 4, compute a **divergence characterization** from the `compare_authors` result. For each collaborator, determine:

- **Concentration delta**: convert each author's `corpus.top_categories` counts to percentages of their total, then identify the top 1–2 categories where the collaborator's percentage exceeds the focal author's by ≥ 10 percentage points (collaborator is *more concentrated* there) and the top 1–2 categories where the focal author's percentage exceeds the collaborator's by ≥ 10 points (focal author is *more concentrated* there).
- **Productivity ratio**: collaborator's total works ÷ focal author's total works. Use `career.career_works` for both when present, since corpus counts cover only part of a career; otherwise use `corpus.corpus_papers`. Note when this is dramatically above (>2x) or below (<0.5x) parity.
- **Career-phase signal**: compare `corpus.papers_per_year`. Note when the collaborator's observed corpus activity has accelerated, decelerated, or shifted relative to the focal author over the last 3 years. Do not describe these mixed-source buckets as publication chronology.

Synthesize these into a one-sentence characterization per collaborator. Examples:
- *"More concentrated on astro-ph.GA (57% vs 41%); 2× the productivity; output accelerating in the Gaia era while focal author's has held steady."*
- *"Pivoted toward cs.CL after 2022; less methodological output than focal author; collaboration appears to have cooled since the pivot."*

## Output Format

### Network Summary

A brief paragraph:
- Selected author, current institution (if known), and number of direct collaborators returned
- Primary source-specific research categories from `corpus.top_categories` in Step 1

### Direct Collaborators

A table of collaborators from Step 2 (top 10):

| Collaborator | Co-authored papers | Primary domain |
|--------------|-------------------|----------------|
| Name         | 15                | cs.LG          |
| ...          | ...               | ...            |

The "Primary domain" column comes from Step 4 comparison data for the top collaborators. For collaborators not included in the comparison, omit the domain or mark as "—".

### Second-Degree Connections

A list of notable second-degree connections from Step 3 — people who collaborate with the focal author's collaborators but were absent from the returned direct-collaborator list. Show up to 10, prioritizing those who appear via multiple collaborators:

- **Name** (connected through: Collaborator A, Collaborator B) — primary domain if known

### Cross-Domain Bridges

Highlight collaborators from Step 2 whose primary domain (from Step 4) differs from the focal author's primary domain. These represent interdisciplinary connections:

- **Name** (domain: q-bio.BM) — bridges to computational biology

If no cross-domain collaborators are found, note that the author's network is concentrated within their primary domain.

### Divergence Analysis

For each top collaborator compared in Step 4, present the divergence characterization computed in Step 5. Use this format:

**Collaborator Name** (N shared papers)
- *Characterization*: the one-sentence synthesis from Step 5
- *Concentration delta*: which categories each is more concentrated in (numbers in percentage points)
- *Productivity*: works ratio vs focal author (upstream works when available, corpus papers otherwise)
- *Trajectory*: career-phase signal over the last ~3 years

If all top collaborators have nearly-identical category distributions and timelines, note that the network is intellectually homogeneous and divergence analysis is uninformative — but still show the table for completeness.

The point of this section is to make visible *how the focal author's intellectual position has drifted relative to their closest collaborators*. Lead with the most divergent collaborator, not the most-collaborated-with one.

### Suggested Follow-ups

- `/valency:profile <collaborator>` — for any interesting collaborator
- `/valency:network <collaborator>` — to explore a collaborator's own network
- `/valency:similar <paper_id>` — for co-authored papers of interest
