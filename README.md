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

## Usage

The plugin works two ways: slash commands for explicit invocation, or natural language that triggers the right skill automatically.

### Profile — researcher overview

```
/valency:profile Yoshua Bengio
```

Or just ask naturally:

```
Who is Yoshua Bengio?
What does Sara Walker work on?
Show me Daphne Koller's publications
```

### Landscape — field overview

```
/valency:landscape cs.LG
/valency:landscape protein folding
```

Or:

```
What's happening in machine learning?
Give me an overview of single cell RNA sequencing
Who are the top authors in cs.AI?
```

### Similar — find related papers

```
/valency:similar 1706.03762
/valency:similar Attention Is All You Need
```

Or:

```
Find papers similar to Attention Is All You Need
What's related to 2301.07041?
```

### Trends — topic evolution over time

```
/valency:trends cs.AI
/valency:trends CRISPR
/valency:trends cs.LG, cs.CL
```

Or:

```
Is cs.AI growing?
When did CRISPR research take off?
Compare machine learning vs natural language processing trends
```

### Network — collaboration mapping

```
/valency:network Yoshua Bengio
```

Or:

```
Who does Yoshua Bengio collaborate with?
Show me Jennifer Doudna's research network
Find connections between researchers in protein folding
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
