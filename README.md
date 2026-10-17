# burp-mcp

Your own MCP server for Burp Suite: a Kotlin Burp extension you own and
can modify, plus a Python MCP server you write and extend.

## Architecture

```
Claude ──MCP (stdio)──> mcp_server/ (Python, yours to extend) ──MCP (SSE)──> extension/ (Kotlin, yours to extend) ──> Burp
```

## Setup

### 1. Build the extension (one-time)

```bash
cd extension
./gradlew shadowJar   # -> build/libs/burp-mcp-wenaco-<version>.jar
```

Needs network access to Maven Central -- build it on your own machine,
not in a sandboxed environment with restricted egress.

In Burp: Extensions tab -> Add -> Extension Type: Java -> pick that jar.
  Output tab should print `BurpMCP ready -> http://127.0.0.1:9262/
(30 tools)`, and a **BurpMCP** tab appears in Burp.

### 2. Run the Python server

```bash
cd mcp_server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m burp_mcp.server
```

Point your MCP client at it, e.g. for Claude Code (run from `mcp_server/`
with the venv active):

```bash
claude mcp add wenaco -- python -m burp_mcp.server
```

## Python tool interface

The Python stdio server registers 33 unique tools: all 30 existing Kotlin Burp
tools by name, `list_burp_tools` / `call_burp_tool` as generic fallbacks, and
the standalone `transform_text` utility. Burp operations remain in the Kotlin
extension and continue to use its scope and ROE protections. See
[`mcp_server/README.md`](mcp_server/README.md) for configuration and tests.

Run the offline Python suite with `mcp_server/.venv/bin/python -m unittest
discover -s mcp_server/tests -v` after installing `mcp_server/requirements.txt`.

## Next steps to make this actually yours

The extension is a reskin right now -- renamed, not rewritten. Real
ownership starts when you change what a tool *does*. Ideas, roughly
easiest to hardest:

1. Add a new tool to `extension/src/main/kotlin/me/wenaco/burpmcp/tools/`
   -- copy an existing one (e.g. `RandomStringTool.kt`) as a template,
   change its logic, register it in `BurpMcpExtension.kt`.
2. Change scope-guard behavior in `safety/RoeGuard.kt` to match how you
   actually want to use this (e.g. different default, extra checks for
   your training-platform use case).
3. Add a tool specific to what you do -- e.g. something that formats
   findings in your CTF flag format, or talks to your training platform's
   API.

See `extension/README.md` for the full rename mapping and tool list, and
`mcp_server/README.md` for how the Python side's tool-registration
pattern works and how to merge in tools from other repos.

## Config

| Var             | Default                     | Meaning                               |
|------------------|------------------------------|----------------------------------------|
| `BURP_MCP_URL`   | `http://127.0.0.1:9262/`    | the extension's SSE endpoint            |
