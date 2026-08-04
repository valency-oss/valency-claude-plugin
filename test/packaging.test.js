import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));

const marketplace = readJson(".claude-plugin/marketplace.json");
const plugin = readJson("plugins/valency/.claude-plugin/plugin.json");
const packageManifest = readJson("package.json");

test("the plugin bundles the canonical Valency MCP server", () => {
  assert.equal(plugin.mcpServers, "./.mcp.json");

  const mcp = readJson("plugins/valency/.mcp.json");
  assert.deepEqual(mcp, {
    mcpServers: {
      valency: {
        type: "http",
        url: "https://labs.valency.io/mcp/",
        oauth: { callbackPort: 33418 },
      },
    },
  });

  const serverName = Object.keys(mcp.mcpServers)[0];
  assert.equal(
    `mcp__plugin_${plugin.name}_${serverName}__<tool>`,
    "mcp__plugin_valency_valency__<tool>",
  );
});

test("distribution metadata uses one repository identity and version", () => {
  const entry = marketplace.plugins.find(({ name }) => name === plugin.name);
  assert.ok(entry, "marketplace must list the valency plugin");

  assert.equal(marketplace.name, "valency-claude-plugin");
  assert.equal(packageManifest.name, "valency-claude-plugin");
  assert.equal(entry.source, "./plugins/valency");
  assert.equal(plugin.repository, "https://github.com/valency-oss/valency-claude-plugin");
  assert.equal(
    packageManifest.repository.url,
    "https://github.com/valency-oss/valency-claude-plugin.git",
  );
  assert.equal(
    packageManifest.bugs.url,
    "https://github.com/valency-oss/valency-claude-plugin/issues",
  );
  assert.equal(plugin.version, "0.3.0");
  assert.equal(entry.version, plugin.version);
  assert.equal(packageManifest.version, plugin.version);
});

test("obsolete runtime prefix discovery is not packaged or documented", () => {
  assert.equal(existsSync("plugins/valency/CLAUDE.md"), false);
  assert.equal(existsSync("plugins/valency/hooks/hooks.json"), false);
  assert.equal(existsSync("plugins/valency/hooks/detect_mcp_prefix.py"), false);
  assert.equal(existsSync("plugins/valency/hooks/test_detect_mcp_prefix.py"), false);

  const distributedText = [
    readFileSync("README.md", "utf8"),
    ...[
      "fresh-collaborators",
      "landscape",
      "network",
      "profile",
      "reading-list",
      "similar",
      "trends",
    ].map((name) => readFileSync(`plugins/valency/skills/${name}/SKILL.md`, "utf8")),
  ].join("\n");

  assert.doesNotMatch(distributedText, /detect_mcp_prefix|mcp__valency-mcp__|mcp__claude_ai_/);
  assert.doesNotMatch(distributedText, /claude mcp add --transport http/);
});
