"""Typed wrappers that change Burp state: BCheck import, intercept, task engine.

These alter Burp's running state and are guarded by the extension. Keep
descriptions accurate and preserve the extension's validation.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present

async def _call(_name, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name,present(**kwargs))
    
def register(mcp) -> None:
    @mcp.tool()
    async def import_bcheck(script: str = UNSET, path: str = UNSET):
        """Import a BCheck script from `script` text or a file `path`."""
        return await _call("import_bcheck", script=script, path=path)
    
    @mcp.tool()
    async def set_intercept(enabled: bool):
        """Turn Burp Proxy interception on (`true`) or off (`false`)."""
        return await _call("set_intercept", enabled=enabled)
    
    @mcp.tool()
    async def set_task_engine(state: str):
        """Set Burp's task engine `state` (e.g. paused / running)."""
        return await _call("set_task_engine", state=state)