# Connecting BurpMCP to MCP clients

The Kotlin extension exposes the **MCP SSE transport** at:

```
http://127.0.0.1:9262/          <-- note: root path "/", NOT "/sse"
```

- Loopback only. Optional bearer token: start Burp with `-Dburpmcp.token=SECRET`,
  then send header `Authorization: Bearer SECRET`.
- Transport is classic **SSE**. Clients that only speak stdio use the
  `mcp-remote` bridge (shown below). Clients that speak SSE/HTTP connect by URL.

You can connect clients directly to this SSE endpoint, or use the Python stdio
server in `mcp_server/`. The direct path exposes 30 Kotlin tools; the Python
path exposes those same 30 tools individually, the two generic passthroughs,
`transform_text`, and `scan_results_workflow` (34 tools total). Choose one path
per client configuration. For the Python path, install its requirements once,
then configure the client to launch `python3` with the absolute path to
`mcp_server/start_server.py`. The launcher selects the project's venv, so no
shell activation or working-directory setting is needed. Set `BURP_MCP_URL` if
the extension uses a non-default port and `BURP_MCP_TOKEN` when Burp requires a
bearer token in the client's MCP server environment.

Load the extension in Burp first (Extensions > Add > Java > the jar). When the
Output tab shows `ready -> http://127.0.0.1:9262/`, connect a client:

## Claude Code (CLI) — native SSE

```bash
claude mcp add --transport sse wenaco http://127.0.0.1:9262/
# with a token:
claude mcp add --transport sse wenaco http://127.0.0.1:9262/ --header "Authorization: Bearer SECRET"
# scope: add --scope user | project | local  (project writes ./.mcp.json and needs approval)
```

Or edit the config directly (`~/.claude.json`, or project `.mcp.json`):

```json
{ "mcpServers": { "wenaco": { "type": "sse", "url": "http://127.0.0.1:9262/" } } }
```

Approve it (`/mcp` or restart), then the `mcp__wenaco__*` tools appear.

## Cursor — native SSE (v0.48+)

`~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```json
{ "mcpServers": { "wenaco": { "url": "http://127.0.0.1:9262/" } } }
```

## Cline (VS Code) — native SSE

`cline_mcp_settings.json` (Cline pane > MCP Servers > Configure):

```json
{ "mcpServers": { "wenaco": { "url": "http://127.0.0.1:9262/", "transportType": "sse" } } }
```

## Windsurf — native SSE

`~/.codeium/windsurf/mcp_config.json`:

```json
{ "mcpServers": { "wenaco": { "serverUrl": "http://127.0.0.1:9262/" } } }
```

## OpenCode — remote server

`opencode.json` (project root overrides global `~/.config/opencode/opencode.json`):

```json
{ "mcp": { "wenaco": { "type": "remote", "url": "http://127.0.0.1:9262/", "enabled": true } } }
```

Note: OpenCode prefers HTTP-streamable transport and has reported quirks with
SSE. If it will not connect, use the `mcp-remote` bridge below as a `type:"local"`
command server instead.

## Claude Desktop & any stdio-only client — via `mcp-remote`

Claude Desktop (and older clients) speak stdio only, so bridge with `mcp-remote`.
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "wenaco": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:9262/"]
    }
  }
}
```

With a token, append to `args`: `"--header", "Authorization: Bearer SECRET"`.
Restart the app; a successful connection shows the tool/hammer indicator.

The same `command`/`args` block works for OpenCode (`type: "local"`), or any
client that only supports local/stdio MCP servers.

## Verify

Any direct SSE client: after connecting, list tools — you should see 30, e.g.
`send_http_request`, `fuzz`, `start_active_scan`. A quick no-target check is
`random_string` (length 8) or `transform` (base64_encode).

The Python stdio server should list 34 tools, including the same Burp tool names,
`transform_text`, and `scan_results_workflow`. Register it with the absolute
launcher path, for example:

```bash
claude mcp add wenaco -- python3 /absolute/path/to/burp-mcp/mcp_server/start_server.py
```

Raw check without a client (proves the server is up):

```bash
curl -sN http://127.0.0.1:9262/    # emits: event: endpoint / data: ?sessionId=...
```
