"""Load the metadata script as an importable module.

The script is a standalone PEP 723 file rather than a package, so it is loaded
by path. Registering it in ``sys.modules`` before execution is required: without
it, ``@dataclass`` cannot resolve ``__module__`` and raises AttributeError.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_metadata.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("update_metadata", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def um() -> ModuleType:
    return _load()
