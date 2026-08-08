from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ANALYSIS=HERE.parent/'analysis'

def load_module():
    spec=importlib.util.spec_from_file_location('uncertainty_policy',ANALYSIS/'uncertainty_policy.py')
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def synthetic_envelope():
    return {
        'v_cell_lower':np.array([0.285,0.0,0.325]),
        'v_cell_upper':np.array([0.305,1.0,0.35]),
        'v_adapter_central':np.array([0.295,0.285,0.337]),
        'table_domain':np.array([1,0,1],dtype=np.uint8),
        'below_table':np.array([0,1,0],dtype=np.uint8),
        'above_table':np.zeros(3,dtype=np.uint8),
    }

def test_registry_has_eight_branch_policies_and_no_fake_energy_axis():
    m=load_module(); policies=m.policy_registry()
    assert len(policies)==8
    assert len({p.policy_id for p in policies})==8
    assert {p.v_policy for p in policies}==set(m.V_POLICIES)
    assert {p.f_value for p in policies}=={0.1,1.0}
    assert all(not hasattr(p,'energy_policy') for p in policies)

def test_only_source_safe_cell_corners_are_load_bearing():
    m=load_module(); policies=m.policy_registry()
    load=[p for p in policies if p.load_bearing]
    audit=[p for p in policies if not p.load_bearing]
    assert len(load)==4 and len(audit)==4
    assert {p.v_policy for p in load}=={'CELL_LOWER_STRICT','CELL_UPPER_STRICT'}
    assert {p.v_policy for p in audit}=={'ADAPTER_TABLE_LOW_STRICT','ADAPTER_TABLE_HIGH_STRICT'}

def test_strict_fields_do_not_extrapolate_below_table():
    m=load_module(); env=synthetic_envelope()
    assert np.array_equal(m.build_v_field('CELL_LOWER_STRICT',env),np.array([0.285,0.0,0.325]))
    assert np.array_equal(m.build_v_field('CELL_UPPER_STRICT',env),np.array([0.305,1.0,0.35]))
    assert np.array_equal(m.build_v_field('ADAPTER_TABLE_LOW_STRICT',env),np.array([0.295,0.0,0.337]))
    assert np.array_equal(m.build_v_field('ADAPTER_TABLE_HIGH_STRICT',env),np.array([0.295,1.0,0.337]))

def test_above_table_domain_fails_closed():
    m=load_module(); env=synthetic_envelope(); env['above_table'][2]=1
    try: m.build_v_field('CELL_LOWER_STRICT',env)
    except ValueError as exc: assert 'above-table' in str(exc)
    else: raise AssertionError('above-table source extrapolation must fail')

def test_fields_are_bounded_and_f_is_exact_endpoint():
    m=load_module(); env=synthetic_envelope()
    for policy in m.policy_registry():
        v=m.build_v_field(policy.v_policy,env)
        f=m.build_f_field(policy.f_value,len(v))
        assert np.all((v>=0)&(v<=1))
        assert np.all(f==policy.f_value)
        assert not v.flags.writeable and not f.flags.writeable

def test_temperature_driven_policy_uses_table_cells_and_strict_subtable_bounds():
    m=load_module()
    T=np.array([5000.0,10000.0,15000.0,10**4.5,70000.0])
    low=m.build_v_field_from_temperature('CELL_LOWER_STRICT',T)
    high=m.build_v_field_from_temperature('CELL_UPPER_STRICT',T)
    adapter=m.build_v_field_from_temperature('ADAPTER_TABLE_LOW_STRICT',T)
    assert low[0]==0.0 and high[0]==1.0 and adapter[0]==0.0
    assert low[1]==high[1]==adapter[1]==0.285
    assert low[2]==0.285 and high[2]==0.305
    assert 0.285<adapter[2]<0.305
    assert low[3]==high[3]==adapter[3]==0.325
    assert low[4]==0.35 and high[4]==0.375

def test_temperature_above_source_table_fails_closed():
    m=load_module()
    try: m.build_v_field_from_temperature('CELL_UPPER_STRICT',np.array([100001.0]))
    except ValueError as exc: assert 'above-table' in str(exc)
    else: raise AssertionError('above-table temperature must fail')
