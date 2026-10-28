from __future__ import annotations

import asyncio
import unittest

from burp_mcp.server import mcp

EXPECTED_TOOLS = {
    "send_http_request",
    "send_http_requests",
    "get_proxy_history",
    "get_proxy_entry",
    "get_websocket_history",
    "start_active_scan",
    "passive_scan",
    "start_crawl",
    "scan_status",
    "stop_scan",
    "get_scanner_issues",
    "generate_report",
    "fuzz",
    "send_to_repeater",
    "send_to_intruder",
    "send_to_organizer",
    "send_to_comparer",
    "scope_check",
    "scope_add",
    "scope_remove",
    "sitemap_query",
    "generate_collaborator_payload",
    "get_collaborator_interactions",
    "import_bcheck",
    "set_intercept",
    "set_task_engine",
    "transform",
    "random_string",
    "export_burp_config",
    "import_burp_config",
    "list_burp_tools",
    "call_burp_tool",
    "transform_text",
    "scan_results_workflow",
}


class ToolRegistrationTests(unittest.TestCase):
    def test_all_expected_tools_register_once_with_kotlin_property_types(self) -> None:
        tools = asyncio.run(mcp.list_tools())
        names = [tool.name for tool in tools]
        self.assertEqual(len(names), 34)
        self.assertEqual(len(set(names)), 34)
        self.assertEqual(set(names), EXPECTED_TOOLS)

        by_name = {tool.name: tool for tool in tools}
        self.assertEqual(by_name["transform"].input_schema["required"], ["op", "input"])
        self.assertEqual(
            by_name["transform_text"].input_schema["required"], ["text", "operation"]
        )
        for tool_name, field, expected_type in (
            ("send_http_request", "url", "string"),
            ("send_http_request", "headers", "array"),
            ("fuzz", "host", "string"),
            ("fuzz", "payload_sets", "array"),
            ("start_active_scan", "index", "integer"),
        ):
            schema = by_name[tool_name].input_schema["properties"][field]
            self.assertEqual(schema["type"], expected_type)
            self.assertNotIn("anyOf", schema)


if __name__ == "__main__":
    unittest.main()
