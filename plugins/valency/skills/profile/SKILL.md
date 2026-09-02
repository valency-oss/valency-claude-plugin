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

Inspect `warnings`, `career_metrics`, `resolved_name`, and `candidates`. A non-null `resolved_name` alone identifies a corpus name bucket, not necessarily one human.

If `candidates` is non-empty, select a lone ORCID-collision candidate only when its `confidence` is at least 0.95. Otherwise present the candidates' display names, institutions, and sample recent titles, ask the user to choose, and re-call with the chosen candidate's returned stable author identifier (or an ORCID or identifying paper when that identifier is null). Do not continue while candidates remain unresolved.

If no usable identity or name bucket is returned, tell the user the researcher could not be resolved and stop. Use non-null `career_metrics.display_name` as the display name. For later researcher calls, use the strongest available key: ORCID, then the stable author identifier returned in `career_metrics`, then the resolved name plus a user-supplied paper hint.

This step is complete when one researcher has been selected and no unresolved candidate list remains.

### Step 2: Get the corpus profile

Call `get_author_profile` with:
- `author` (string): the selected display name
- `orcid` (string): the resolved ORCID, when present

Without an ORCID, use the identity result's `resolved_name` as `author`. Record `stats_source`: `orcid_keyed` is identity-linked, while `name_keyed` remains a potentially fragmented name-bucket aggregate. The result supplies corpus `summary`, `categories`, `timeline`, and nullable identity-provider `career_metrics`.

This step is complete when each profile claim has its corpus or identity-provider provenance and material warnings attached.

### Step 3: Get citation-ranked papers

Call `find_papers_by_researcher` with the strongest key from Step 1:
- ORCID, the tool's stable-author-identifier parameter, or `author`
- `limit` (integer): 10
- `sort_by` (string): "citations"

Inspect `candidates`, `disambiguation_status`, `warnings`, `returned_count`, each paper's `match_type`, and citation coverage. Resolve any reappearing candidates before continuing. Describe the first result as the highest citation-ranked paper returned, not definitively the researcher's most-cited paper when citation counts are incomplete.

This step is complete when every returned paper is attributed to the selected identity or carries its explicit attribution qualification.

### Step 4: Get top coauthor name buckets

If Step 2 returned a non-null `resolved_name`, call `find_coauthors` with:
- `author` (string): that `resolved_name`
- `limit` (integer): 10
- `exclude_mega_collaborations` (boolean): true

Otherwise skip this step and state that no corpus name key was available. The result is a top-N list of coauthor name buckets, not a complete identity-resolved collaboration graph.

## Output Format

Present the results in this structure:

### Summary

A brief block:
- **Name**: selected display name
- **Identity**: ORCID when present; otherwise the returned disambiguation qualification
- **Institution**: `career_metrics.current_institution.institution` (omit if absent)
- **h-index**: from identity-provider `career_metrics` (omit if absent)
- **Papers in corpus**: `summary.total_papers`, labeled with `stats_source`. When `career_metrics.works_count` is present, add the separately sourced upstream works count.
- **Observed paper activity**: `summary.first_paper` to `summary.last_paper`, labeled as corpus activity with the mixed first-submission/record-date caveat
- **Primary domains**: top 3 categories from Step 2

### Research Domains

A table of the top 5 categories from Step 2:

| Category | Papers |
|----------|--------|
| cs.LG    | 42     |
| ...      | ...    |

### Top Papers

A numbered list of up to 10 papers from Step 3. State `returned_count`, `disambiguation_status`, citation coverage, and material warnings. For each paper show:
- [Title](url) (paper ID)
- Source-aware date label
- Citations (`citation_count`; omit if null)
- Categories

### Top Collaborators

A table of up to 5 coauthor name buckets from Step 4:

| Collaborator | Co-authored papers |
|--------------|-------------------|
| Name         | 15                |
| ...          | ...               |

### Suggested Follow-ups

- `/valency:network <author_name>` — map their collaboration network
- `/valency:reading-list <author_name>` — a curated bibliography around their work
- `/valency:similar <paper_id>` — continue from the highest citation-ranked returned paper
