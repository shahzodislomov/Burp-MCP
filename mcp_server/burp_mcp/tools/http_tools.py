from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def send_http_request(
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
        fix_content_length: bool = UNSET,
        follow_redirects: bool = UNSET,
        max_body: int = UNSET,
    ):
        """Send `request` to `host:port` and return the response.

        `request` is a raw HTTP request. Set `follow_redirects` false to
        receive the first response only. Set `update_content_length` false for
        desync tests.
        """
        return await _call(
            "send_http_request",
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
            fix_content_length=fix_content_length,
            follow_redirects=follow_redirects,
            max_body=max_body,
        )

    @mcp.tool()
    async def send_http_requests(
        requests: list,
        match: str = UNSET,
        include_body: bool = UNSET,
    ):
        return await _call(
            "send_http_requests",
            requests=requests,
            match=match,
            include_body=include_body,
        )

    @mcp.tool()
    async def get_proxy_history(
        limit: int = UNSET,
        contains: str = UNSET,
        regex: str = UNSET,
        method: str = UNSET,
        status: list = UNSET,
        mime_type: str = UNSET,
        min_length: int = UNSET,
        max_length: int = UNSET,
        include_body: bool = UNSET,
    ):
        return await _call(
            "get_proxy_history",
            limit=limit,
            contains=contains,
            regex=regex,
            method=method,
            status=status,
            mime_type=mime_type,
            min_length=min_length,
            max_length=max_length,
            include_body=include_body,
        )

    @mcp.tool()
    async def get_proxy_entry(
        index: int,
        max_body: int = UNSET,
        request_only: bool = UNSET,
        response_only: bool = UNSET,
    ):
        return await _call(
            "get_proxy_entry",
            index=index,
            max_body=max_body,
            request_only=request_only,
            response_only=response_only,
        )
        
    @mcp.tool()
    async def get_websocket_history(
        contains: str = UNSET,
        limit: int = UNSET
    ):
        return await _call(
            "get_websocket_history",
            contains=contains,
            limit=limit
        )
