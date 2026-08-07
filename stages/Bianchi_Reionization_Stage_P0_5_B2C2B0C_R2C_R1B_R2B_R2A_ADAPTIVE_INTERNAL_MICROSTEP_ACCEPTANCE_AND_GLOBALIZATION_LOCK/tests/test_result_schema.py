from __future__ import annotations
import json
from pathlib import Path

STAGE=Path(__file__).resolve().parents[1]
LANES={'LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR'}


def test_stage_results_cover_all_lanes_and_gates():
    results=json.loads((STAGE/'results.json').read_text())
    assert set(results['lanes']) == LANES
    required={'fixed_point','positivity','H_nuclei','He_nuclei','photon','resolved_thermal','unresolved_energy','commit_once','rollback','restart'}
    for lane in LANES:
        assert set(results['lanes'][lane]['gates']) >= required


def test_thermal_backend_metadata_handles_numpy_oracle():
    import importlib.util, sys
    module_path=STAGE/'analysis/run_stage.py'
    spec=importlib.util.spec_from_file_location('r2b_r2a_result_metadata',module_path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    class Backend:
        name='NUMPY_ARRAY_ORACLE'
    assert module.thermal_backend_metadata(Backend()) == {
        'thermal_backend':'NUMPY_ARRAY_ORACLE',
        'thermal_root_iterations':None,
    }
