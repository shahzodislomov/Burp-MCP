"""A pure custom tool with no dependency on Burp -- a decode/encode utility.

This is the pattern for anything you want to add that's just Python: no
burp_proxy involved, no network call, just logic. Good reference for
tools you pull in from other GitHub MCP repos too, when they don't talk
to Burp at all (e.g. a JWT decoder, a hashing tool).
"""

from __future__ import annotations

import base64
import binascii
import urllib.parse


def register(mcp) -> None:
    @mcp.tool()
    def transform_text(text: str, operation: str) -> str:
        """Encode or decode a string. Handy for mangling payloads by hand.

        Args:
            text: Input string.
            operation: One of "base64_encode", "base64_decode", "url_encode",
                "url_decode", "hex_encode", "hex_decode".
        """
        if operation == "base64_encode":
            return base64.b64encode(text.encode()).decode()
        if operation == "base64_decode":
            return base64.b64decode(text).decode(errors="replace")
        if operation == "url_encode":
            return urllib.parse.quote(text)
        if operation == "url_decode":
            return urllib.parse.unquote(text)
        if operation == "hex_encode":
            return text.encode().hex()
        if operation == "hex_decode":
            try:
                return binascii.unhexlify(text).decode(errors="replace")
            except binascii.Error as exc:
                raise ValueError(f"Invalid hex input: {exc}") from exc
        raise ValueError(
            f"Unknown operation '{operation}'. Expected one of: base64_encode, "
            "base64_decode, url_encode, url_decode, hex_encode, hex_decode."
        )
