# Python MCP Server

The Python process serves MCP over stdio and connects to the Kotlin Burp
extension over SSE. The extension remains responsible for Burp/Montoya work,
scope checks, and the ROE guard.

## Tools

The server exposes 34 unique tools: all 30 Kotlin tools under their individual
names, `list_burp_tools` and `call_burp_tool` as generic discovery/fallbacks,
`transform_text` as a standalone Python utility, and `scan_results_workflow`
for collecting status and issues for an existing scan. The Kotlin-backed
`transform` name is distinct from `transform_text`.

The wrappers are grouped in `burp_mcp/tools/` by HTTP/history, scanning,
fuzzing, Burp destinations, scope, Collaborator, controls, configuration, and
Burp utilities. Each wrapper forwards to its matching extension tool through
`BurpProxy`; new Burp behavior belongs in Kotlin, not duplicated here.

## Run

```bash
cd mcp_server
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
python3 start_server.py
```

`start_server.py` finds the project's virtual environment and sets the correct
working directory, so it can also be started from outside `mcp_server/`. The
server speaks MCP over stdio; stdout is reserved for protocol messages. When
run manually, stop it with Ctrl+C.

## Configure a Client

Register the launcher by absolute path so the MCP client does not depend on an
activated shell or a particular working directory:

```bash
claude mcp add wenaco -- python3 /absolute/path/to/burp-mcp/mcp_server/start_server.py
```

Reload Claude Code and approve the server if prompted. The client starts and
stops the Python process automatically. Other clients should use the same stdio
command and argument, adding custom environment variables in their MCP server
configuration. Do not configure this Python path and the direct Burp SSE path
under the same server name in one client.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BURP_MCP_URL` | `http://127.0.0.1:9262/` | Kotlin extension SSE endpoint |
| `BURP_MCP_TOKEN` | unset | Bearer token matching Burp's `-Dburpmcp.token=...` |

Set these in the MCP client's server environment when using a non-default URL
or token. Do not commit a real token to the repository. Starting Python does
not start Burp: load the extension in Burp before calling Burp-backed tools.

## Tests

The tests use fake proxies and do not send requests to a target:

```bash
cd mcp_server
.venv/bin/python -m unittest discover -s tests -v
```
