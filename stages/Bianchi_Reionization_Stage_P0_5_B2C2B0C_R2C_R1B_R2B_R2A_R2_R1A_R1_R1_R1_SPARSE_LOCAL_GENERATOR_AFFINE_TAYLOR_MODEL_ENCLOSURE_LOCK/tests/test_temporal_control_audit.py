from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_stagewise_branch_schedule_is_admissible_but_escapes_static_corner_hull() -> None:
    mod = _load("sparse_temporal_control", STAGE / "analysis/temporal_control_audit.py")
    audit = mod.run_temporal_control_audit(REPO, lane="LOCAL_NEUTRAL_HAZARD_PRIMARY")
    assert audit.full_converged and audit.first_half_converged and audit.second_half_converged
    assert len(audit.endpoint_sha256) == 64
    assert audit.all_trial_hard_gates_pass
    assert audit.local_error < 2.0e-4
    assert audit.maximum_hydrogen_residual < 1.0e-11
    assert audit.maximum_helium_residual < 1.0e-11
    assert audit.maximum_owner_residual < 1.0e-11
    assert audit.maximum_photon_residual < 1.0e-8
    assert audit.maximum_thermal_residual < 1.0e-10
    assert audit.maximum_ots_energy_residual < 1.0e-10
    assert audit.outside_coordinate == "x_HeIII"
    assert audit.outside_node_count > 5000
    assert audit.maximum_outside_absolute > 1.0e-12
    assert audit.maximum_outside_fraction_of_static_width > 0.02
    assert audit.static_parameter_enclosure_certified is False
    assert audit.stagewise_control_generators_required is True
    assert len(audit.maximum_outside_by_coordinate) == 4
    assert audit.maximum_outside_by_coordinate[2] > 1.0e-12
    assert max(audit.maximum_outside_by_coordinate[0], audit.maximum_outside_by_coordinate[1], audit.maximum_outside_by_coordinate[3]) < 1.0e-14
    assert audit.outside_node_count_by_coordinate[2] > 5000
