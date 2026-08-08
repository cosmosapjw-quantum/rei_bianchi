from __future__ import annotations
import importlib.util,sys
from pathlib import Path

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
