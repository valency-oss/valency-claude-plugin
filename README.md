# Valency — Research Corpus Plugin for Claude Code

Search, profile, and analyze 36M+ research papers across arXiv, PubMed, bioRxiv, and medRxiv directly from Claude Code.

## Prerequisites

You need the Valency MCP connector configured in your Claude.ai account. Add it at [claude.ai/settings/connectors](https://claude.ai/settings/connectors) using the URL `https://labs.valency.io/mcp`.

For detailed setup instructions, see the [Valency + Claude guide](https://docs.valency.io/guides/claude/).

## Installation

Clone the repo and load it as a local plugin:

```bash
git clone https://github.com/valencyio/valency-plugin.git
claude --plugin-dir ./valency-plugin
```

To pick up changes without restarting, run `/reload-plugins` inside your session.

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
