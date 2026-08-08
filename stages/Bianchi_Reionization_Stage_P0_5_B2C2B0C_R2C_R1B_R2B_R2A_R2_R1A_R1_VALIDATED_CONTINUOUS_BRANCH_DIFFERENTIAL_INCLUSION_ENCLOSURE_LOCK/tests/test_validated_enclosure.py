from pathlib import Path
import importlib.util
import sys

import numpy as np

HERE = Path(__file__).resolve().parents[1] / "analysis"
REPO = Path(__file__).resolve().parents[3]


def load(name):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_scalar_linear_picard_enclosure_contains_exact_endpoint():
    mod = load("validated_enclosure")
    result = mod.scalar_linear_demo(rate=-0.5, initial=1.0, duration=0.2)
    exact = np.exp(-0.1)
    assert result["certified"] is True
    assert result["endpoint_lower"] <= exact <= result["endpoint_upper"]


def test_project_audit_is_fail_closed_not_physical_no_go():
    mod = load("validated_enclosure")
    result = mod.run_project_audit(REPO, partitions=(16,))
    assert result["continuous_parameter_certified"] is False
    assert result["production_history_authorized"] is False
    assert result["physical_nonexistence_claimed"] is False
    assert result["partition_audits"][0]["classification"] in {
        "BOX_PICARD_WRAPPING_FAILURE",
        "BOX_PICARD_CONE_EXIT",
        "BOX_PICARD_INCLUSION_FAILURE",
        "TABLE_TOPOLOGY_EVENT_UNLOCALIZED",
    }
