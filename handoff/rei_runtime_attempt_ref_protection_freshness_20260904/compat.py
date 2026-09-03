#!/usr/bin/env python3
"""Load the sealed PR #47 authority package without importing REI physics."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
OLD_PACKAGE = (
    ROOT / "handoff" / "rei_runtime_prelease_import_firewall_green_20260903"
)
if not OLD_PACKAGE.is_dir():
    raise RuntimeError("AUTHORITY_SOURCE_PACKAGE_UNAVAILABLE")
if str(OLD_PACKAGE) not in sys.path:
    sys.path.insert(0, str(OLD_PACKAGE))

import common_v2 as old_common  # type: ignore  # noqa: E402


def load_old_module(filename: str, module_name: str) -> ModuleType:
    path = OLD_PACKAGE / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"AUTHORITY_SOURCE_MODULE_UNAVAILABLE:{filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_old_controller() -> ModuleType:
    return load_old_module(
        "successor_runtime_controller.py",
        "rei_pr47_successor_runtime_controller",
    )


def load_old_worker() -> ModuleType:
    return load_old_module(
        "native_runtime_worker.py",
        "rei_pr47_native_runtime_worker",
    )
