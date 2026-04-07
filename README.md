# Valency — Research Corpus Plugin for Claude Code

Search, profile, and analyze 36M+ research papers across arXiv, PubMed, bioRxiv, and medRxiv directly from Claude Code.

## Prerequisites

You need the Valency MCP connector configured in your Claude.ai account. Add it at [claude.ai/settings/connectors](https://claude.ai/settings/connectors) using the URL `https://labs.valency.io/mcp`.

For detailed setup instructions, see the [Valency + Claude guide](https://docs.valency.io/guides/claude/).

## Installation

Add the Valency marketplace and install the plugin:

```bash
claude plugin marketplace add valencyio/valency-plugin
claude plugin install valency
```

Then restart Claude Code. The plugin persists across sessions.

### Auto-approve MCP tool calls (recommended)

By default, Claude Code will prompt you to approve each Valency tool call. Since these are read-only queries, you can auto-approve them by adding to the permissions allow list in your global settings (`~/.claude/settings.json`):

```json
{
  "permissions": {
    "allow": [
      "mcp__claude_ai_Valency_Systems_Inc__*"
    ]
  }
}
```

### Alternative: one-off session

To try the plugin without installing:

```bash
git clone https://github.com/valencyio/valency-plugin.git
claude --plugin-dir ./valency-plugin
```

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
How has David Hogg's work diverged from his coauthors?
```

The network skill also produces a Divergence Analysis section showing how each top collaborator's research focus has drifted from the focal author's — useful for understanding how a researcher's intellectual position has shifted relative to their closest peers.

### Reading list — curated bibliography for a researcher

```
/valency:reading-list David W. Hogg
```

Or:

```
What should David Hogg be reading next?
Build me a reading list for Yoshua Bengio
Find adjacent literature for Sara Walker's research
```

Triangulates off the author's most-cited and most-recent papers to surface 5–8 recommendations per intellectual thread, with cross-thread papers (those that connect multiple threads of the author's work) highlighted separately.

### Fresh collaborators — expand a researcher's network

```
/valency:fresh-collaborators David W. Hogg
```

Or:

```
Who should David Hogg be talking to that he isn't already?
Find new potential collaborators for Yoshua Bengio
Who are the new faces working on stellar dynamics that Jo Bovy doesn't know yet?
```

Returns researchers doing recent (last 12–18 months) thematically relevant work who are **not** in the focal author's existing top-100 coauthor network. Each candidate is tagged junior/senior and attributed to the theme(s) that surfaced them.

## Data Sources

| Source | Papers |
|--------|--------|
| arXiv  | 4.6M   |
| PubMed | 31.1M  |
| bioRxiv| 402K   |
| medRxiv| 100K   |

## License

MIT
