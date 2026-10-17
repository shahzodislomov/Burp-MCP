from __future__ import annotations

import asyncio
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from mcp.server.mcpserver.exceptions import UnexpectedToolError

from burp_mcp.server import mcp
from burp_mcp.tools import (
    burp_utility_tools,
    collaborator_tools,
    config_tools,
    control_tools,
    fuzz_tools,
    http_tools,
    scan_tools,
    scope_tools,
    send_to_tools,
)

CALLS = {
    "send_http_request": {
        "url": "https://scope.test/",
        "method": "POST",
        "headers": ["X-Test: yes"],
        "body": "payload",
        "follow_redirects": True,
        "max_body": 1200,
    },
    "send_http_requests": {"requests": [{"url": "https://scope.test/"}]},
    "get_proxy_history": {},
    "get_proxy_entry": {"index": 2},
    "get_websocket_history": {},
    "start_active_scan": {"url": "https://scope.test/"},
    "passive_scan": {"url": "https://scope.test/"},
    "start_crawl": {"url": "https://scope.test/"},
    "scan_status": {},
    "stop_scan": {"scan_id": "scan-1"},
    "get_scanner_issues": {},
    "generate_report": {"path": "/tmp/report.html"},
    "fuzz": {
        "host": "scope.test",
        "port": 443,
        "template": "GET /FUZZ HTTP/1.1\r\n\r\n",
        "payloads": ["one", "two"],
        "concurrency": 2,
        "filter_status": [200],
    },
    "send_to_repeater": {"url": "https://scope.test/"},
    "send_to_intruder": {"url": "https://scope.test/"},
    "send_to_organizer": {"url": "https://scope.test/"},
    "send_to_comparer": {"a": "left", "b": "right"},
    "scope_check": {"url": "https://scope.test/"},
    "scope_add": {"url": "https://scope.test/"},
    "scope_remove": {"url": "https://scope.test/"},
    "sitemap_query": {},
    "generate_collaborator_payload": {},
    "get_collaborator_interactions": {},
    "import_bcheck": {"script": "BCHECK test"},
    "set_intercept": {"enabled": False},
    "set_task_engine": {"state": "paused"},
    "transform": {"op": "base64_encode", "input": "test"},
    "random_string": {"length": 8},
    "export_burp_config": {},
    "import_burp_config": {"json": "{}"},
}

TOOL_MODULES = (
    burp_utility_tools,
    collaborator_tools,
    config_tools,
    control_tools,
    fuzz_tools,
    http_tools,
    scan_tools,
    scope_tools,
    send_to_tools,
)


class FakeBurpProxy:
    calls: list[tuple[str, dict]] = []
    error: Exception | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info):
        return None

    async def call_tool(self, name: str, arguments: dict):
        self.calls.append((name, arguments))
        if self.error:
            raise self.error
        return f"result:{name}"


class ToolWrapperTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        FakeBurpProxy.calls = []
        FakeBurpProxy.error = None
        self.stack = ExitStack()
        for module in TOOL_MODULES:
            self.stack.enter_context(patch.object(module, "BurpProxy", FakeBurpProxy))

    async def asyncTearDown(self) -> None:
        self.stack.close()

    async def test_every_kotlin_wrapper_forwards_arguments_and_result(self) -> None:
        for name, arguments in CALLS.items():
            with self.subTest(tool=name):
                result = await mcp.call_tool(name, arguments)
                self.assertEqual(FakeBurpProxy.calls[-1], (name, arguments))
                self.assertEqual(result.content[0].text, f"result:{name}")

    async def test_wrapper_propagates_upstream_errors(self) -> None:
        FakeBurpProxy.error = RuntimeError("upstream failed")
        with self.assertRaises(UnexpectedToolError):
            await mcp.call_tool("scope_check", {"url": "https://scope.test/"})


if __name__ == "__main__":
    unittest.main()
