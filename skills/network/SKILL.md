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
