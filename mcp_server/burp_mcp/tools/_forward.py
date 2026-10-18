"""Shared plumbing for the typed Kotlin-wrapper tools.

Every wrapper in this package does the same three things:

1. Declare a Python function whose parameters mirror one Kotlin tool's
   inputSchema (names + types). The MCP SDK turns that signature into the
   JSON schema Claude sees, so the types have to match Kotlin's.
2. Drop the arguments the caller didn't pass, so we forward to Kotlin
   *exactly* what we were handed -- no implicit defaults sneaking in.
3. Open a BurpProxy session and call the matching Kotlin tool by name.

`UNSET` is the sentinel default for every optional parameter. We can't use
`None` for that, because `x: str | None = None` makes the published schema
`anyOf: [string, null]`, and we want a clean `{"type": "string"}`. So the
annotation stays `str`/`int`/`list`/... and the default is this sentinel;
`present()` then strips anything still equal to it before forwarding.

Each wrapper module imports `BurpProxy` into *its own* namespace (not here)
so tests can patch it per module with a fake proxy.
"""

from __future__ import annotations

import warnings
from typing import Any

# Pydantic warns that this sentinel isn't JSON-serializable when it builds the
# schema. That's expected -- the default is deliberately excluded from the
# schema -- so quiet just that one message.
warnings.filterwarnings(
    "ignore", message="Default value .* is not JSON serializable"
)

# Unique object: no real argument value can equal it, so "did the caller pass
# this?" is just `value is not UNSET`.
UNSET: Any = object()


def present(**kwargs: Any) -> dict[str, Any]:
    """Keep only the arguments the caller actually supplied.

    Any parameter still holding the UNSET sentinel was not passed, so it's
    dropped. The result is the exact arguments object we forward to Kotlin.
    """
    return {name: value for name, value in kwargs.items() if value is not UNSET}
