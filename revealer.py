#!/usr/bin/env python3
"""Backward-compatible entry point for the VS Code *Run on save* workflow.

The Revealer logic now lives in the importable :mod:`revealer` package under
``src/``. This thin shim keeps the historical invocation working::

    python3 /path/to/Revealer/revealer.py '/path/to/presentation.pres'

For day-to-day use, prefer installing the CLI (``pipx install .``) and running
``revealer build`` / ``revealer select``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from revealer.build import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
