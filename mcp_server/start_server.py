#!/usr/bin/env python3
"""Start the MCP server with this project's virtual environment."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent


def venv_python(server_dir: Path = SERVER_DIR) -> Path:
    if os.name == "nt":
        return server_dir / ".venv" / "Scripts" / "python.exe"
    return server_dir / ".venv" / "bin" / "python"


def main() -> None:
    python = venv_python(SERVER_DIR)
    if not python.is_file():
        print(
            "Python virtual environment not found. Set it up first with:\n"
            f"  cd {SERVER_DIR}\n"
            "  python3 -m venv .venv\n"
            "  .venv/bin/python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(1)

    os.chdir(SERVER_DIR)
    os.execv(str(python), [str(python), "-m", "burp_mcp.server"])


if __name__ == "__main__":
    main()
