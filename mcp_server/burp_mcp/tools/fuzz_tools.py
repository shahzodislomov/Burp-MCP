"""Typed wrapper for the Burp extension's native fuzzer.

Burp builds the requests, applies its scope guard, and runs the fuzz. Do
not implement a second fuzzer or send payloads from Python. Keep the
parameters aligned with the live Kotlin schema (sniper/clusterbomb/pitchfork
modes, payload sets, markers, concurrency, filters).
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def fuzz(
        host: str,
        port: int,
        template: str,
        tls: bool = UNSET,
        mode: str = UNSET,
        marker: str = UNSET,
        payloads: list = UNSET,
        wordlist: str = UNSET,
        markers: list = UNSET,
        payload_sets: list = UNSET,
        concurrency: int = UNSET,
        max: int = UNSET,
        match: str = UNSET,
        filter_status: list = UNSET,
        extract: str = UNSET,
        update_content_length: bool = UNSET,
    ):
        """Run Burp's fuzzer against `template` on `host:port`. Scope-enforced.

        `template` is a raw request with marker(s). `mode` is
        sniper|clusterbomb|pitchfork. Supply payloads via `payloads`
        (+ `marker`), `wordlist`, or `payload_sets` (+ `markers`).
        `concurrency`, `max`, `match`, `filter_status`, and `extract` shape
        the run and the output. Set `update_content_length` false for desync
        tests.
        """
        return await _call(
            "fuzz",
            host=host,
            port=port,
            template=template,
            tls=tls,
            mode=mode,
            marker=marker,
            payloads=payloads,
            wordlist=wordlist,
            markers=markers,
            payload_sets=payload_sets,
            concurrency=concurrency,
            max=max,
            match=match,
            filter_status=filter_status,
            extract=extract,
            update_content_length=update_content_length,
        )
