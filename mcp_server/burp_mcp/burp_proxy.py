"""Client for the Burp extension in ../../extension (see its README).

me.wenaco.burpmcp / BurpMcpExtension, loaded into Burp as a jar. It runs
an MCP server inside Burp's JVM over SSE, default http://127.0.0.1:9262/.
This module connects to it as an MCP *client* and gives the rest of this
codebase a simple async API:

    async with BurpProxy() as burp:
        tools = await burp.list_tools()
        result = await burp.call_tool("send_http_request", {...})

All the Burp-specific work (sending requests, reading proxy history,
scope checks, active scan, fuzzing, Collaborator, etc.) happens inside
the extension in Kotlin -- this file's only job is the SSE connection and
exposing it as a context manager so each tool call gets a fresh session.

Also works unmodified against PortSwigger's
official extension (port 9876) if you ever point BURP_MCP_URL elsewhere --
the protocol is the same either way.
"""

from __future__ import annotations

import os
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client


class BurpProxyError(RuntimeError):
    """Raised when the upstream Burp MCP extension can't be reached or errors."""


class BurpProxy:
    def __init__(self, url: str | None = None) -> None:
        # Matches what ../../extension prints on startup:
        # "BurpMCP-Wenaco ready -> http://127.0.0.1:9262/ (30 tools)".
        # Override with BURP_MCP_URL if you changed -Dburpmcp.port.
        self.url = url or os.environ.get("BURP_MCP_URL", "http://127.0.0.1:9262/")
        self.token = os.environ.get("BURP_MCP_TOKEN")
        self._stack: AsyncExitStack | None = None
        self.session: ClientSession | None = None

    async def __aenter__(self) -> "BurpProxy":
        self._stack = AsyncExitStack()
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else None
            read, write = await self._stack.enter_async_context(
                sse_client(self.url, headers=headers)
            )
            self.session = await self._stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.session.initialize()
        except Exception as exc:  # connection refused, timeout, handshake failure, etc.
            await self._stack.aclose()
            self._stack = None
            raise BurpProxyError(
                f"Can't reach the Burp MCP extension at {self.url}. "
                "Checklist: Burp is running, the built jar from ../../extension "
                "(Extensions tab -> Java -> burp-mcp-wenaco-*.jar) is loaded, and "
                "its Output sub-tab printed a 'ready -> ...' line."
            ) from exc
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._stack is not None:
            await self._stack.aclose()
            self._stack = None
            self.session = None

    async def list_tools(self) -> list[dict]:
        assert self.session is not None, "BurpProxy used outside 'async with'"
        result = await self.session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": getattr(
                    t, "inputSchema", getattr(t, "input_schema", {})
                ),
            }
            for t in result.tools
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        assert self.session is not None, "BurpProxy used outside 'async with'"
        result = await self.session.call_tool(name, arguments)
        if getattr(result, "isError", getattr(result, "is_error", False)):
            raise BurpProxyError(
                f"Burp tool '{name}' returned an error: {result.content}"
            )
        structured = getattr(
            result, "structuredContent", getattr(result, "structured_content", None)
        )
        if structured is not None:
            return {"content": result.content, "structuredContent": structured}
        return result.content
