from __future__ import annotations

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_module = importlib.import_module("scripts.iceccme2026.plot_figure1_system_workflow")
globals().update({name: getattr(_module, name) for name in dir(_module) if not name.startswith("_")})

if __name__ == "__main__":
    _module.main()
