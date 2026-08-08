from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def load_module():
    path=STAGE/'analysis/run_four_corner_preflight.py'
    spec=importlib.util.spec_from_file_location('run_four_corner_preflight',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module


def test_wide_corner_enclosure_is_a_robust_fail_closed_result():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':3e-3,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=False,
    )
    assert decision['classification']=='SOURCE_EXTENSION_CALIBRATION_REQUIRED_WIDE_ENCLOSURE'
    assert not decision['production_authorized']


def test_narrow_corners_do_not_certify_the_continuous_nonlinear_family():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':1e-5,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=False,
    )
    assert decision['classification']=='CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED'
    assert not decision['production_authorized']


def test_only_narrow_certified_enclosure_can_authorize():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':1e-5,'x_HeII':1e-5,'x_HeIII':1e-5,'log_T':1e-5},
        all_numerical_gates_pass=True,
        continuous_parameter_certified=True,
    )
    assert decision['classification']=='UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED'
    assert decision['production_authorized']


def test_numerical_failure_precedes_uncertainty_classification():
    m=load_module()
    decision=m.classify_enclosure(
        widths={'x_HII':0.0,'x_HeII':0.0,'x_HeIII':0.0,'log_T':0.0},
        all_numerical_gates_pass=False,
        continuous_parameter_certified=True,
    )
    assert decision['classification']=='HARD_GATE_FAILURE'
    assert not decision['production_authorized']


def test_policy_csv_schema_accepts_locked_local_error_gate(tmp_path):
    m=load_module()
    row={
        'lane':'LOCAL_NEUTRAL_HAZARD_PRIMARY',
        'policy_id':'CELL_LOWER_STRICT_F010',
        'v_policy':'CELL_LOWER_STRICT',
        'f_value':0.1,
        'load_bearing':True,
        'full_converged':True,
        'first_half_converged':True,
        'second_half_converged':True,
        'local_error':1.0e-5,
        'local_error_gate':m.LOCAL_ERROR_GATE,
        'hard_gates_pass':True,
        'max_H_residual':0.0,
        'max_He_residual':0.0,
        'max_owner_residual':0.0,
        'max_photon_residual':0.0,
        'max_thermal_residual':0.0,
        'max_PDS_residual':0.0,
        'max_OTS_energy_residual':0.0,
        'minimum_species':1.0,
        'elapsed_s':0.1,
        'endpoint_sha256':'0'*64,
        'failure_classifications':[],
    }
    target=tmp_path/'policy.csv'
    m._write_csv(target,[row])
    assert 'local_error_gate' in target.read_text(encoding='utf-8').splitlines()[0]
    assert b'\r\n' not in target.read_bytes()


def test_numerical_and_source_uncertainty_gates_are_distinct():
    m=load_module()
    assert m.LOCAL_ERROR_GATE==2e-4
    assert m.UNCERTAINTY_GATE==2e-3
    assert m.LOCAL_ERROR_GATE < m.UNCERTAINTY_GATE


def test_csv_schema_includes_every_run_policy_field(tmp_path):
    m=load_module()
    assert 'local_error_gate' in m.CSV_FIELDS
    row={name: '' for name in m.CSV_FIELDS}
    row['lane']='TEST';row['local_error_gate']=m.LOCAL_ERROR_GATE
    row['failure_classifications']=[]
    output=tmp_path/'rows.csv'
    m._write_csv(output,[row])
    header=output.read_text(encoding='utf-8').splitlines()[0].split(',')
    assert tuple(header)==m.CSV_FIELDS


def test_lane_worker_artifacts_round_trip(tmp_path):
    m=load_module()
    lane=m.LANES[0]
    payload={'lane':lane,'rows':[{'policy_id':'P'}],'widths':{'x_HII':1e-4},'endpoint_hashes':{}}
    arrays={'x_HII_lower':np.array([0.1,0.2]),'x_HII_upper':np.array([0.2,0.3])}
    hashes=m.write_lane_worker_artifacts(output_dir=tmp_path,lane=lane,payload=payload,arrays=arrays)
    loaded,loaded_arrays=m.read_lane_worker_artifacts(output_dir=tmp_path,lane=lane)
    assert loaded==payload
    assert np.array_equal(loaded_arrays['x_HII_lower'],arrays['x_HII_lower'])
    assert set(hashes)=={'json','npz'}
    assert all(len(value)==64 for value in hashes.values())


def test_lane_workers_pin_process_and_blas_state():
    m=load_module();env=m._worker_environment()
    assert env['PYTHONUNBUFFERED']=='1'
    assert env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']=='1'
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
        assert env[name]=='1'


def test_merge_mode_rejects_incomplete_lane_artifact(tmp_path):
    m=load_module();lane=m.LANES[0]
    payload={'lane':lane,'rows':[],'widths':{},'endpoint_hashes':{},'strict_endpoint_count':0}
    m.write_lane_worker_artifacts(output_dir=tmp_path,lane=lane,payload=payload,arrays={})
    loaded,_=m.read_lane_worker_artifacts(output_dir=tmp_path,lane=lane)
    expected={policy.policy_id for policy in m.policy_mod.policy_registry()}
    observed={str(row['policy_id']) for row in loaded['rows']}
    assert observed!=expected
    assert loaded['strict_endpoint_count']!=4


def test_independent_validator_replays_locked_result():
    path=STAGE/'analysis/validate_preflight.py'
    spec=importlib.util.spec_from_file_location('validate_preflight',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    receipt=module.validate()
    assert receipt['status']=='PASS'
    assert receipt['policy_row_count']==24
    assert receipt['load_bearing_row_count']==12
    assert receipt['unique_endpoint_count']==8
    assert receipt['all_hard_gates_pass'] is True
    assert receipt['continuous_parameter_certificate_present'] is False
