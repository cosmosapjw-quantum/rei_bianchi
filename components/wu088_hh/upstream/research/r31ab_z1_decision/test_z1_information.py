from pathlib import Path
import importlib.util
import pytest
HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent

def api():
    spec=importlib.util.spec_from_file_location('r31ab',HERE/'z1_information.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def result():
    return api().analyze(HERE/'inputs/EXISTING_METRIC_INPUTS.npz',RESEARCH/'r31z_source_bound/source_bound.py',RESEARCH/'r31aa_validation/local_candidate.py')

def test_z1_primary_model_separation_is_large():
    r=result();s=r['model_separation']
    assert s['K']==pytest.approx(0.2165779475378074,rel=1e-12)
    assert s['Dmax']==pytest.approx(0.21927766897126583,rel=1e-12)
    assert r['information_verdict']=='HIGH_DISCRIMINATION_EXPECTED'

def test_truth_independent_half_gap():
    r=result();b=r['truth_independent_half_gap_lower_bound']
    assert b['K']==pytest.approx(0.1082889737689037,rel=1e-12)
    assert b['Dmax']==pytest.approx(0.10963883448563291,rel=1e-12)

def test_does_not_claim_winner_or_execute_node():
    r=result()
    assert r['new_scientific_node_executed'] is False
    assert r['execution_authorized_here'] is False
    assert 'no prediction' in r['claim_ceiling']
