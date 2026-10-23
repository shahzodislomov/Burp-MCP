"""Typed wrappers for the Burp extension's scan / crawl / report tools.

Scanner operations need Burp Suite Professional; if the extension returns
an error (e.g. Community edition), it surfaces as-is -- don't swallow it.
Burp enforces scope on every scan target.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name: str, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def start_active_scan(
        url: str = UNSET,
        raw: str = UNSET,
        host: str = UNSET,
        port: int = UNSET,
        tls: bool = UNSET,
        method: str = UNSET,
        path: str = UNSET,
        headers: list = UNSET,
        cookies: str = UNSET,
        cookie_file: str = UNSET,
        use_cookie_jar: bool = UNSET,
        body: str = UNSET,
        index: int = UNSET,
    ):
        """Start an active audit (Burp Pro). Scope-enforced.

        Give a target as `url`, as `raw` request text (+ host/port/tls), or
        as a Proxy history `index` (from get_proxy_history). Returns a scan
        id you can poll with scan_status.
        """
        return await _call(
            "start_active_scan",
            url=url,
            raw=raw,
            host=host,
            port=port,
            tls=tls,
            method=method,
            path=path,
            headers=headers,
            cookies=cookies,
            cookie_file=cookie_file,
            use_cookie_jar=use_cookie_jar,
            body=body,
            index=index,
        )

    @mcp.tool()
    async def passive_scan(url: str):
        """Passively audit `url` (no new attack traffic). Scope-enforced."""
        return await _call("passive_scan", url=url)

    @mcp.tool()
    async def start_crawl(url: str):
        """Start a crawl from the seed `url`. Scope-enforced."""
        return await _call("start_crawl", url=url)

    @mcp.tool()
    async def scan_status(scan_id: str = UNSET):
        """Return the status of one scan by `scan_id`, or all scans if omitted."""
        return await _call("scan_status", scan_id=scan_id)

    @mcp.tool()
    async def stop_scan(scan_id: str):
        """Stop the scan identified by `scan_id`."""
        return await _call("stop_scan", scan_id=scan_id)

    @mcp.tool()
    async def get_scanner_issues(
        scan_id: str = UNSET,
        min_severity: str = UNSET,
        contains: str = UNSET,
        limit: int = UNSET,
        detail: bool = UNSET,
    ):
        """Return scanner findings.

        Filter by `scan_id`, `min_severity`, `contains` (substring), and
        `limit`. `detail` includes full issue detail.
        """
        return await _call(
            "get_scanner_issues",
            scan_id=scan_id,
            min_severity=min_severity,
            contains=contains,
            limit=limit,
            detail=detail,
        )

    @mcp.tool()
    async def generate_report(
        path: str,
        format: str = UNSET,
        scan_id: str = UNSET,
    ):
        """Write a Burp Scanner report to `path`.

        `format` is HTML or XML. `scan_id` limits the report to one scan.
        This is Burp's native report, not a Python-formatted one.
        """
        return await _call(
            "generate_report",
            path=path,
            format=format,
            scan_id=scan_id,
        )
