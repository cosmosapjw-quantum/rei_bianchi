from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]


def load_map():
    path=STAGE/'analysis/interval_discrete_map.py'
    spec=importlib.util.spec_from_file_location('crosssite_evidence_map_test',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def read(name):
    return json.loads((STAGE/'data'/name).read_text())


def test_exact_structural_ledger_validator_is_zero():
    data=read('EXACT_SYMBOLIC_VALIDATION.json')
    assert data['passed']
    identities=data['identities']
    assert identities['cascade_photon_identity']=='0'
    assert identities['owner_simplex_residual']=='0'
    assert identities['group_photon_owner_residual']=='0'
    assert identities['augmented_energy_residual']=='0'
    assert set(identities['mprk_column_sum_residuals'])=={'0'}
    assert set(identities['hydrogen_stoichiometric_residuals'])=={'0'}
    assert set(identities['helium_stoichiometric_residuals'])=={'0'}


def test_three_lane_public_widths_and_raw_ledgers_pass():
    data=read('THREE_LANE_INTERVAL_MAP.json')
    assert data['all_certified']
    assert len(data['rows'])==3
    assert max(data['max_widths'].values()) < 2.0e-3
    for row in data['rows']:
        assert row['classification']=='PASS'
        assert not row['table_event']['any_event']
        for lo,hi in row['set_ledgers'].values():
            assert lo <= 0.0 <= hi


def test_partition_refinement_widths_decrease():
    data=read('PARTITION_SENSITIVITY.json')
    assert data['all_maps_enclosed']
    assert data['acceptance_pattern']=={'1024':False,'2048':True,'4096':True}
    assert data['load_bearing_partition_2048_pass']
    assert data['monotone_local_error']
    assert all(data['monotone_widths'].values())
    assert [r['partition'] for r in data['rows']]==[1024,2048,4096]
    assert data['rows'][0]['classification']=='VALIDATED_LOCAL_ERROR_GATE_FAILURE'
    assert data['rows'][1]['maximum_validated_local_error'] < 2.0e-4


def test_direct_containment_includes_stagewise_and_interior_evidence():
    data=read('CONTAINMENT_AUDIT.json')
    assert data['all_contained']
    for row in data['rows']:
        assert row['direct_stagewise_endpoint']['outside_count']==0
        assert row['static_lower']['outside_count']==0
        assert row['static_upper']['outside_count']==0
        assert all(x['outside_count']==0 for x in row['primary_interior'])


def test_transactional_table_event_restart_audit_passes():
    data=read('TABLE_EVENT_RESTART_AUDIT.json')
    assert data['passed']
    assert data['between_site_crossing_detected']
    assert not data['safe_path_event']
    assert data['increasing_localization']['parent_unchanged']
    assert data['decreasing_localization']['parent_unchanged']


def test_primary_lane_recomputes_validated_map():
    m=load_map()
    result=m.run_lane(REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY',partition=2048)
    assert result.certified, result.classification
    assert result.classification=='PASS'
    assert max(result.public_widths.values()) < 2.0e-3
    assert result.diagnostics['maximum_validated_local_error'] < 2.0e-4
    assert not result.table_event['any_event']
    assert not result.diagnostics['failed_ledgers']


def test_independent_stage_validator_receipt_passes():
    data=read('INDEPENDENT_STAGE_VALIDATION.json')
    assert data['passed']
    assert data['failures']==[]
    assert data['partition_acceptance']=={'1024':False,'2048':True,'4096':True}
    assert data['stagewise_containment']
    assert data['event_restart']
    assert data['structural_exact_ledgers']


def test_invalid_attempts_are_preserved_and_non_load_bearing():
    names=(
        'ATTEMPT_1_MARGIN_ONLY_CONTAINMENT.json',
        'ATTEMPT_2_THERMAL_SECANT_FALSE_DERIVATIVE_BOUND.json',
        'ATTEMPT_3_FIXED_BISECTION_ORCHESTRATION_TIMEOUT.json',
        'ATTEMPT_4_CONSTRUCTION_TUBE_TRACE_CONE_FALSE_FAILURE.json',
    )
    for name in names:
        data=json.loads((STAGE/'state'/name).read_text())
        assert not data.get('load_bearing', False)
