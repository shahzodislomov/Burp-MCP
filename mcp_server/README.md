# Python MCP Server

The Python process serves MCP over stdio and connects to the Kotlin Burp
extension over SSE. The extension remains responsible for Burp/Montoya work,
scope checks, and the ROE guard.

## Tools

The server exposes 33 unique tools: all 30 Kotlin tools under their individual
names, `list_burp_tools` and `call_burp_tool` as generic discovery/fallbacks,
and `transform_text` as a standalone Python utility. The Kotlin-backed
`transform` name is distinct from `transform_text`.

The wrappers are grouped in `burp_mcp/tools/` by HTTP/history, scanning,
fuzzing, Burp destinations, scope, Collaborator, controls, configuration, and
Burp utilities. Each wrapper forwards to its matching extension tool through
`BurpProxy`; new Burp behavior belongs in Kotlin, not duplicated here.

## Run

```bash
cd mcp_server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m burp_mcp.server
```

Configure an MCP client for the stdio process, for example Claude Code from
`mcp_server/` with the virtual environment active:

```bash
claude mcp add wenaco -- python -m burp_mcp.server
```

The Python path is an alternative to connecting directly to Burp over SSE.
Do not configure both with the same MCP server name in one client.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BURP_MCP_URL` | `http://127.0.0.1:9262/` | Kotlin extension SSE endpoint |
| `BURP_MCP_TOKEN` | unset | Bearer token matching Burp's `-Dburpmcp.token=...` |

## Tests

The tests use fake proxies and do not send requests to a target:

```bash
cd mcp_server
.venv/bin/python -m unittest discover -s tests -v
```
