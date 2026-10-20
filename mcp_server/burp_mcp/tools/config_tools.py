"""Typed wrappers for Burp configuration export / import.

Importing config changes Burp state and is guarded by the extension. Don't
bypass that guard or write Burp config directly from Python.
"""

from __future__ import annotations

from burp_mcp.burp_proxy import BurpProxy
from burp_mcp.tools._forward import UNSET, present


async def _call(_name, **kwargs):
    async with BurpProxy() as burp:
        return await burp.call_tool(_name, present(**kwargs))


def register(mcp) -> None:
    @mcp.tool()
    async def export_burp_config(
        scope: str = UNSET, path: str = UNSET, keys: str = UNSET
    ):
        """Export Burp configuration.

        `scope` selects which settings, `path` writes to a file (otherwise
        returned inline), `keys` narrows to specific config keys.
        """
        return await _call("export_burp_config", scope=scope, path=path, keys=keys)

    @mcp.tool()
    async def import_burp_config(
        scope: str = UNSET,
        json: str = UNSET,
        path: str = UNSET,
    ):
        """Import Burp configuration from `json` text or a file `path`.

        `scope` selects which settings are applied.
        """
        return await _call("import_burp_config", scope=scope, json=json, path=path)
