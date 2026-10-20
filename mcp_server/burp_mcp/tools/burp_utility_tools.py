"""Typed wrappers for Burp's own utility tools: `transform` and `random_string`.

These talk to Burp via BurpProxy. Note the deliberate name clash avoidance:
the pure-Python encoder in transform_tool.py is `transform_text`; this
`transform` is Burp's utility (its full operation set). Keep both.
"""
from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import present


async def _call(_name: str, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def transform(op: str, input: str):
        """Run Burp's transform `op` on `input` (Burp's encode/decode/hash set)."""
        return await _call("transform", op=op, input=input)

    @mcp.tool()
    async def random_string(length: int):
        """Generate a random string of `length` characters via Burp."""
        return await _call("random_string", length=length)