"""Typed wrappers for Burp Target scope + site map.

Burp's Target scope is authoritative. Do not build a separate Python scope
model -- these just read and edit Burp's own scope, and the extension's
ROE guard still governs every traffic-producing tool.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name: str, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def scope_check(url: str):
        """Ask Burp whether `url` is in its Target scope."""
        return await _call("scope_check", url=url)

    @mcp.tool()
    async def scope_add(url: str):
        """Add a URL prefix (e.g. https://example.com/) to Burp Target scope."""
        return await _call("scope_add", url=url)

    @mcp.tool()
    async def scope_remove(url: str):
        """Remove a URL prefix from Burp Target scope."""
        return await _call("scope_remove", url=url)

    @mcp.tool()
    async def sitemap_query(
        contains: str = UNSET,
        regex: str = UNSET,
        method: str = UNSET,
        status: list = UNSET,
        mime_type: str = UNSET,
        min_length: int = UNSET,
        max_length: int = UNSET,
        limit: int = UNSET,
    ):
        """Query Burp's site map.

        Filter by `contains` (URL substring), `regex`, `method`, `status`
        (ints), `mime_type`, `min_length`/`max_length` (response body bytes).
        `limit` caps the rows.
        """
        return await _call(
            "sitemap_query",
            contains=contains,
            regex=regex,
            method=method,
            status=status,
            mime_type=mime_type,
            min_length=min_length,
            max_length=max_length,
            limit=limit,
        )
