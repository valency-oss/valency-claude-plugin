# Valency — Research Corpus Plugin for Claude Code

The Valency plugin adds seven research skills and a bundled connection to the Valency MCP server. Installing the plugin is enough to register `https://labs.valency.io/mcp/`; users do not need to run `claude mcp add`.

The MCP server is registered as `plugin:valency:valency`. Its tools use the stable `mcp__plugin_valency_valency__<tool>` namespace.

## Requirements

- Claude Code. This release was validated with Claude Code 2.1.220.
- A browser for the interactive Valency sign-in.
- Local TCP port `33418` available while OAuth completes. The fixed port is required by the currently registered Valency OAuth client.

## Installation

Add the repository marketplace and install the plugin at user scope:

```bash
claude plugin marketplace add valency-oss/valency-claude-plugin --scope user
claude plugin install valency@valency-claude-plugin --scope user
```

Both commands are qualified for scripting. Repeating them targets the same records: Claude reports the marketplace and plugin as already configured instead of creating duplicates. Use the update commands below when you want to refresh an existing installation.

Start or restart Claude Code after installation. When Claude reports that the Valency server needs authentication, open `/mcp` and authenticate `plugin:valency:valency`. You can start the same interactive browser flow from a terminal:

```bash
claude mcp login plugin:valency:valency
```

If authentication reports that port `33418` is unavailable or already in use, identify the local process holding it, stop that process if it is safe to do so, and retry. On macOS or Linux:

```bash
lsof -nP -iTCP:33418 -sTCP:LISTEN
```

On Windows PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 33418 -State Listen
```

Do not change the callback port in the plugin: Valency currently requires `http://localhost:33418/callback`.

### Migrating an existing manual Valency MCP connection

Installing the plugin never deletes MCP configuration that you created. Before migrating, list existing servers:

```bash
claude mcp list
```

If a server might be a manually configured Valency connection, inspect it by its existing name and confirm its URL:

```bash
claude mcp get <existing-server-name>
```

Install and authenticate the plugin first, then confirm that `plugin:valency:valency` works. Keeping the manual connection is safe, but Claude may display two sets of Valency tools. If you choose to remove the old entry, use the name and scope reported by Claude:

```bash
claude mcp remove <existing-server-name> --scope <local|project|user>
```

That removal is an explicit, optional user action. The plugin does not remove or modify manual MCP entries.

### Permissions

Claude Code prompts before MCP tool calls unless your settings allow a specific tool. Review Valency tools individually before adding them to an allow list. Do not allow `mcp__plugin_valency_valency__*` as a wildcard: the server includes the write-capable `submit_feedback` tool, which should remain subject to explicit user authorization.

## Updating

Refresh the marketplace and update the installed plugin:

```bash
claude plugin marketplace update valency-claude-plugin
claude plugin update valency@valency-claude-plugin --scope user
```

Restart Claude Code or run `/reload-plugins` to use the updated MCP configuration in an existing session.

## Uninstalling

Remove the user-scoped plugin:

```bash
claude plugin uninstall valency@valency-claude-plugin --scope user
```

Uninstalling removes the plugin-owned `plugin:valency:valency` registration. It does not disturb unrelated servers or a manually configured Valency server. To remove the marketplace record too:

```bash
claude plugin marketplace remove valency-claude-plugin --scope user
```

## One-off development session

To load a checkout without installing it:

```bash
git clone https://github.com/valency-oss/valency-claude-plugin.git
claude --plugin-dir ./valency-claude-plugin/plugins/valency
```

## Usage

Claude can select these skills from natural-language questions, or you can invoke one directly.

### Researcher profile

```text
/valency:profile Yoshua Bengio
```

Summarizes a researcher's domains, papers, and collaborators.

### Field landscape

```text
/valency:landscape cs.LG
/valency:landscape protein folding
```

Provides an overview of a category or research topic.

### Similar papers

```text
/valency:similar 1706.03762
/valency:similar Attention Is All You Need
```

Finds research related to a paper ID or title.

### Publication trends

```text
/valency:trends cs.AI
/valency:trends CRISPR
```

Shows how a topic or category has changed over time.

### Collaboration network

```text
/valency:network Yoshua Bengio
```

Maps direct and second-degree collaborators and analyzes research divergence.

### Researcher reading list

```text
/valency:reading-list David W. Hogg
```

Builds a bibliography around a researcher's influential and recent work.

### Fresh collaborators

```text
/valency:fresh-collaborators David W. Hogg
```

Finds researchers outside an author's established coauthor network who are publishing relevant recent work.

## Development and validation

Run the repository tests and both strict Claude validators:

```bash
npm test
claude plugin validate . --strict
claude plugin validate plugins/valency --strict
```

Then inspect the component inventory:

```bash
claude --plugin-dir plugins/valency plugin details valency
```

The repository is prepared for submission to Anthropic's reviewed community marketplace. Submission and acceptance are separate processes and are not implied by this repository.

## License

This repository and the packaged plugin are MIT-licensed. See [LICENSE](./LICENSE).

Organization-wide contribution, trademark, and security policies for `valency-oss` are maintained at [valency-oss/.github](https://github.com/valency-oss/.github).
