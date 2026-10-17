"""Generic passthrough to every tool the Burp extension in ../../extension exposes.

That extension ships 30
tools: send_http_request, send_http_requests, get_proxy_history,
get_proxy_entry, get_websocket_history, start_active_scan, passive_scan,
start_crawl, scan_status, stop_scan, get_scanner_issues, generate_report,
fuzz, send_to_repeater, send_to_intruder, send_to_organizer,
send_to_comparer, scope_check, scope_add, scope_remove, sitemap_query,
generate_collaborator_payload, get_collaborator_interactions,
import_bcheck, set_intercept, set_task_engine, transform, random_string,
export_burp_config, import_burp_config.

Why generic instead of one @mcp.tool() per Burp tool: the MCP Python SDK
builds each tool's JSON schema from a Python function's type hints. Burp's
extension hands us its tools' schemas already built (as raw JSON schema),
and there's no clean way to turn an arbitrary JSON schema into a Python
function signature on the fly. So instead of faking that, we expose two
tools that just forward to Burp directly:

  - list_burp_tools  -> see what's available and its real argument schema
  - call_burp_tool   -> invoke any of them by name

This also means any tool you add to the extension later shows up here
automatically, with zero changes to this file.

If you want a *specific* tool to show up to Claude with its own name,
description and typed arguments (nicer UX, same as any @mcp.tool()), write
a thin wrapper by hand -- the arguments are whatever that tool's Kotlin
source expects (src/main/kotlin/me/wenaco/burpmcp/tools/<Tool>.kt in
../../extension), confirmed against list_burp_tools' live output.
"""
from __future__ import annotations

from typing import Any

from burp_mcp.burp_proxy import BurpProxy


def register(mcp) -> None:
    @mcp.tool()
    async def list_burp_tools() -> list[dict]:
        """List every tool exposed by the Burp MCP extension, with its argument schema.

        Call this once to see what's available -- HTTP send/batch-send,
        proxy history, active scan/crawl, the fuzzer, Collaborator,
        send-to-Repeater/Intruder/Organizer/Comparer, scope control, and
        more. Then use call_burp_tool to actually run one.
        """
        async with BurpProxy() as burp:
            return await burp.list_tools()

    @mcp.tool()
    async def call_burp_tool(name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool exposed by the Burp MCP extension by name.

        Args:
            name: Tool name, exactly as returned by list_burp_tools.
            arguments: Arguments object matching that tool's inputSchema.
        """
        async with BurpProxy() as burp:
            return await burp.call_tool(name, arguments)
