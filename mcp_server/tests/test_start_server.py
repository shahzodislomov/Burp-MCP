from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import start_server


class StartServerTests(unittest.TestCase):
    def test_uses_project_virtualenv_and_server_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            server_dir = Path(temporary_directory)
            python = start_server.venv_python(server_dir)
            python.parent.mkdir(parents=True)
            python.touch()

            with (
                patch.object(start_server, "SERVER_DIR", server_dir),
                patch.object(os, "chdir") as chdir,
                patch.object(os, "execv") as execv,
            ):
                start_server.main()

            chdir.assert_called_once_with(server_dir)
            execv.assert_called_once_with(
                str(python), [str(python), "-m", "burp_mcp.server"]
            )


if __name__ == "__main__":
    unittest.main()
