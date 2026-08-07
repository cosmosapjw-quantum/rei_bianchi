from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

SCRIPT = Path(__file__).parents[1] / "analysis" / "build_owner_split_preflight.py"
spec = importlib.util.spec_from_file_location("build_owner_split_preflight", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_piecewise_pchip_integral_is_refinement_additive():
    x = 0.5 * (1.0 - np.cos(np.arange(17) * np.pi / 16.0))
    y = np.exp(5.0 * x) * (1.0 + 0.2 * np.sin(9.0 * x))
    whole = module.integrate_positive_pchip(x, y, 0.0, 1.0)
    for refinement in (2, 4, 8, 16):
        pieces = sum(
            module.integrate_positive_pchip(
                x, y, i / refinement, (i + 1) / refinement
            )
            for i in range(refinement)
        )
        assert pieces == pytest.approx(whole, rel=1e-13, abs=1e-15)
