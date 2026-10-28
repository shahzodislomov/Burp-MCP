"""Entry point for Burp MCP server.

Architecture: this process is an MCP server to Claude (stdio), and an MCP
*client* to the Burp extension in ../../extension (SSE, running inside
Burp). It re-exposes that extension's tools and adds your own on top.
See README.md for the full picture.

Run it:
    python -m burp_mcp.server

Configure where the Burp extension's SSE endpoint is (only needed if you
changed -Dburpmcp.port):
    BURP_MCP_URL   default http://127.0.0.1:9262/
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from burp_mcp.tools import (
    burp_passthrough,
    burp_utility_tools,
    collaborator_tools,
    config_tools,
    control_tools,
    fuzz_tools,
    http_tools,
    scan_tools,
    scope_tools,
    send_to_tools,
    transform_tool,
    workflow_tools,
)

mcp = MCPServer(
    name="wenaco",
    instructions=(
        "Tools for working with a running Burp Suite instance. "
        "Provides typed tools for the Burp extension, plus list_burp_tools and "
        "call_burp_tool as generic fallbacks. Traffic-producing tools run through "
        "the extension's scope and ROE protections. Also includes transform_text, "
        "a standalone Python encoding utility. Requires the extension to be loaded in Burp."
    ),
)

burp_passthrough.register(mcp)
http_tools.register(mcp)
scan_tools.register(mcp)
fuzz_tools.register(mcp)
send_to_tools.register(mcp)
scope_tools.register(mcp)
collaborator_tools.register(mcp)
control_tools.register(mcp)
config_tools.register(mcp)
burp_utility_tools.register(mcp)
transform_tool.register(mcp)
workflow_tools.register(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
