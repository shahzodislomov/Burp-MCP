"""Typed wrappers that stage a request in a Burp tool.

These hand a request to Repeater/Intruder/Organizer/Comparer. Staging a
request in Intruder is NOT launching an attack -- it just loads it (with
payload positions marked). Burp enforces scope.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name: str, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def send_to_repeater(
        url: str = UNSET,
        raw: str = UNSET,
        host: str = UNSET,
        port: int = UNSET,
        tls: bool = UNSET,
        tab: str = UNSET,
    ):
        """Load a request into a new Repeater tab (named `tab` if given)."""
        return await _call(
            "send_to_repeater",
            url=url,
            raw=raw,
            host=host,
            port=port,
            tls=tls,
            tab=tab,
        )

    @mcp.tool()
    async def send_to_intruder(
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
        tab: str = UNSET,
        marker: str = UNSET,
    ):
        """Load a request into Intruder (does not start an attack).

        Same request-building fields as send_http_request. `marker` wraps
        each payload position (default '§'); omit for no positions.
        """
        return await _call(
            "send_to_intruder",
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
            tab=tab,
            marker=marker,
        )

    @mcp.tool()
    async def send_to_organizer(
        url: str = UNSET,
        raw: str = UNSET,
        host: str = UNSET,
        port: int = UNSET,
        tls: bool = UNSET,
    ):
        """Store a request in Burp's Organizer."""
        return await _call(
            "send_to_organizer",
            url=url,
            raw=raw,
            host=host,
            port=port,
            tls=tls,
        )

    @mcp.tool()
    async def send_to_comparer(a: str, b: str):
        """Load two items `a` and `b` into Comparer for diffing."""
        return await _call("send_to_comparer", a=a, b=b)
