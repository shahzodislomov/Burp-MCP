"""Convenience workflows composed from existing Burp extension tools."""

from __future__ import annotations

from typing import Any

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


def register(mcp) -> None:
    @mcp.tool()
    async def scan_results_workflow(
        scan_id: str,
        min_severity: str = UNSET,
        contains: str = UNSET,
        limit: int = UNSET,
        detail: bool = UNSET,
    ) -> dict[str, Any]:
        """Collect status and scanner issues for an existing scan.

        This does not start or poll a scan. Scanner issues may require Burp
        Suite Professional; upstream errors are returned without being hidden.
        """
        async with BurpProxy() as burp:
            status = await burp.call_tool("scan_status", {"scan_id": scan_id})
            issues = await burp.call_tool(
                "get_scanner_issues",
                present(
                    scan_id=scan_id,
                    min_severity=min_severity,
                    contains=contains,
                    limit=limit,
                    detail=detail,
                ),
            )

        return {"scan_id": scan_id, "status": status, "issues": issues}