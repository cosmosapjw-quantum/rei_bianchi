"""Changed dependency tests, not a rerun of atomic or cosmology suites."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest
ROOT = Path(__file__).resolve().parents[1]

def tool():
    spec = importlib.util.spec_from_file_location('owner_scope_intake', ROOT/'owner_scope_intake.py')
    assert spec is not None and spec.loader is not None and (ROOT/'owner_scope_intake.py').exists(), 'owner-scope intake not implemented'
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def inputs():
    return [json.loads((ROOT/'inputs/rei_f00'/n).read_text()) for n in
      ['rei_model_lock.json','closure_process_decision.json','parent_and_lane_applicability.json']]

def test_baseline_exclusion_is_not_zero_atomic_source():
    x = tool().assess(*inputs())
    assert x['baseline_disposition']=='RCT_EXCLUDED_BY_OWNER_SCOPE'
    assert x['baseline_source_dependency']=='NOT_REQUIRED_WHILE_EXCLUDED'
    assert x['selected_atomic_source_id'] is None and x['atomic_rate_coefficient'] is None
    assert x['atomic_evaluator_calls']==0 and x['consumer_mutations']==0
    assert x['implementation_acceptance'] is True and x['physical_source_admission'] is False

def test_scope_missing_blocker_is_retracted_without_inclusion_admission():
    x=tool().assess(*inputs())
    assert x['REI_SCOPE_LOCK']=='RECOVERED_AND_BOUND'
    assert x['actual_RCT_binding_accepted'] is False
    assert x['optional_RCT_state']=='WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT'
    assert x['optional_REI_F09_cancelled'] is False

def test_old_temperature_guard_not_inherited():
    x=tool().assess(*inputs())
    assert x['temperature_domain_K'] is None
    assert x['source_domain_assessment']=='NOT_EVALUATED_FOR_EXCLUDED_PROCESS'
    assert x['previous_FT03_guard_applies'] is False

def test_no_energy_closure_or_absorption_inferred():
    x=tool().assess(*inputs())
    assert all(x[k] is None for k in ['RCT_photon_energy_eV','RCT_prompt_heat_eV','RCT_recoil_eV','RCT_closure_id'])
    assert x['recombination_escape_is_RCT_closure'] is False

@pytest.mark.parametrize('value',[True,0,None,'false'])
def test_changed_or_ambiguous_RCT_flag_fails_closed(value):
    m=tool(); a,b,c=inputs(); b['processes']['He2_H_CX_RCT']=value
    with pytest.raises(m.ContractError): m.assess(a,b,c)

def test_omitted_RCT_flag_is_not_exclusion():
    m=tool();a,b,c=inputs();del b['processes']['He2_H_CX_RCT']
    with pytest.raises(m.ContractError):m.assess(a,b,c)

@pytest.mark.parametrize('index',[0,1,2])
def test_mixed_model_identity_rejected(index):
    m=tool(); xs=inputs();xs[index]['model_id']='REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1'
    with pytest.raises(m.ContractError):m.assess(*xs)

@pytest.mark.parametrize('value',[1e-14,False,None])
def test_synthetic_zero_must_be_explicit_and_consistent(value):
    m=tool();a,b,c=inputs();a['coefficients']['He2_H_CX_cm3_s']=value
    with pytest.raises(m.ContractError):m.assess(a,b,c)

def test_new_energy_coordinates_not_old_eV_per_H():
    x=tool().assess(*inputs())
    assert x['consumer_energy_coordinate']=='u_th erg cm^-3'
    assert x['consumer_photon_coordinate']=='proper cm^-3'
    a,b,c=inputs();a['units']['thermal_state']='eV/H'
    m=tool()
    with pytest.raises(m.ContractError):m.assess(a,b,c)

def test_gates_not_promoted_and_old_node_history_not_inherited():
    x=tool().assess(*inputs())
    assert x['historical_gate_transfer'] is False and x['full_physical_interval_verified'] is False
    a,b,c=inputs();a['provider_selection']['physical_admitted']=True
    m=tool()
    with pytest.raises(m.ContractError):m.assess(a,b,c)

def test_inputs_unmodified_and_no_density_execution():
    xs=inputs();old=copy.deepcopy(xs);x=tool().assess(*xs)
    assert xs==old and x['density_product_applied'] is False

def test_snapshot_hash_guard(tmp_path):
    m=tool(); assert len(m.load_verified(ROOT))==3
    import shutil
    shutil.copytree(ROOT/'inputs',tmp_path/'inputs')
    shutil.copyfile(ROOT/'INPUT_LOCK.json',tmp_path/'INPUT_LOCK.json')
    p=tmp_path/'inputs/rei_f00/rei_model_lock.json';p.write_bytes(p.read_bytes()+b' ')
    with pytest.raises(m.ContractError,match='IDENTITY'):m.load_verified(tmp_path)

def test_cli_create_only_and_no_admission_exit(tmp_path):
    tool();p=tmp_path/'state.json'
    cmd=[sys.executable,'-W','error','-B',str(ROOT/'owner_scope_intake.py'),'--root',str(ROOT),'--out',str(p)]
    z=subprocess.run(cmd,capture_output=True,text=True)
    assert z.returncode==0,z.stderr
    b=p.read_bytes(); assert json.loads(b)['actual_RCT_binding_accepted'] is False
    assert subprocess.run(cmd,capture_output=True).returncode==2
    assert p.read_bytes()==b
