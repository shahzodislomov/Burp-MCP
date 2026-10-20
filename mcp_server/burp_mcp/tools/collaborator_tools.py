"""Typed wrappers for Burp Collaborator.

Burp owns the Collaborator context. Don't poll an external Collaborator
service from Python -- just forward to the extension.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import present

async def _call(_name: str, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))
    
def register(mcp) -> None:
    @mcp.tool()
    async def generate_collaborator_payload():
        """Generate a new Burp Collaborator payload (domain) to use in a test."""
        return await _call("generate_collaborator_payload")
    
    @mcp.tool()
    async def get_collaborator_interactions():
        """Return interactions (DNS/HTTP/SMTP) seen by the current Collaborator context."""
        return await _call("get_collaborator_interactions")