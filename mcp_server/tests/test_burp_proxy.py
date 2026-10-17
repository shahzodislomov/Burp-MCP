from __future__ import annotations

import os
import unittest
from contextlib import asynccontextmanager
from unittest.mock import patch

from mcp.types import CallToolResult, TextContent
from mcp.types import Tool as MCPTool

from burp_mcp.burp_proxy import BurpProxy, BurpProxyError


class FakeSession:
    def __init__(self, *_args):
        self.closed = False
        self.call_result = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info):
        self.closed = True

    async def initialize(self):
        return None

    async def call_tool(self, _name, _arguments):
        return self.call_result


class BurpProxyTests(unittest.IsolatedAsyncioTestCase):
    async def test_default_and_overridden_url(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(BurpProxy().url, "http://127.0.0.1:9262/")
        with patch.dict(os.environ, {"BURP_MCP_URL": "http://localhost:9999/"}):
            self.assertEqual(BurpProxy().url, "http://localhost:9999/")

    async def test_token_uses_supported_sse_headers_without_logging_it(self) -> None:
        captured = {}

        @asynccontextmanager
        async def fake_sse(_url, headers=None):
            captured.update(headers or {})
            yield object(), object()

        with patch.dict(os.environ, {"BURP_MCP_TOKEN": "test-token-value"}), patch(
            "burp_mcp.burp_proxy.sse_client", fake_sse
        ), patch("burp_mcp.burp_proxy.ClientSession", FakeSession):
            async with BurpProxy() as burp:
                self.assertIsNotNone(burp.session)
        self.assertEqual(captured, {"Authorization": "Bearer test-token-value"})

    async def test_failed_initialization_closes_stack_and_clears_state(self) -> None:
        @asynccontextmanager
        async def failed_sse(_url, headers=None):
            raise ConnectionError("connection refused")
            yield None, None

        proxy = BurpProxy()
        with patch("burp_mcp.burp_proxy.sse_client", failed_sse):
            with self.assertRaises(BurpProxyError):
                await proxy.__aenter__()
        self.assertIsNone(proxy._stack)
        self.assertIsNone(proxy.session)

    async def test_structured_content_is_preserved_with_existing_content(self) -> None:
        proxy = BurpProxy()
        proxy.session = FakeSession()
        proxy.session.call_result = CallToolResult(
            content=[TextContent(type="text", text="text")],
            structured_content={"items": []},
            is_error=False,
        )
        self.assertEqual(
            await proxy.call_tool("scan_status", {}),
            {
                "content": [TextContent(type="text", text="text")],
                "structuredContent": {"items": []},
            },
        )

    async def test_tool_error_is_raised(self) -> None:
        proxy = BurpProxy()
        proxy.session = FakeSession()
        proxy.session.call_result = CallToolResult(
            content=[TextContent(type="text", text="failure")],
            is_error=True,
        )
        with self.assertRaisesRegex(BurpProxyError, "scan_status.*failure"):
            await proxy.call_tool("scan_status", {})

    async def test_list_tools_translates_schema_attribute_without_schema_loss(
        self,
    ) -> None:
        proxy = BurpProxy()
        proxy.session = FakeSession()

        async def list_tools():
            return type(
                "Result",
                (),
                {"tools": [MCPTool(name="sample", input_schema={"type": "object"})]},
            )()

        proxy.session.list_tools = list_tools
        self.assertEqual(
            await proxy.list_tools(),
            [
                {
                    "name": "sample",
                    "description": None,
                    "inputSchema": {"type": "object"},
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
