import numpy as np
import pytest
from wu088_hh.r31n import provider_plan, interpolate_pair_costs, jvp_assemble, od_finalize


def fake_d():
    s=np.zeros((12,8),float);p=np.zeros((12,8),float)
    for j in range(8):
        s[j,j]=1.0;p[j,j]=1.0
    return {'v':np.array(2.0),'s_C':s,'p_C':p,'phase_E':np.arange(49,dtype=float)/10}


def test_provider_plan_reuses_cp4_and_requests_only_missing_nodes():
    plan=provider_plan(
        anchors=[0,16,32,48,64],
        od_nodes={0},
        jvp_nodes={0,16,32,64},
        ionic_nodes={0,16,32,48,64},
    )
    assert plan['missing_od']==[16,32,48,64]
    assert plan['missing_jvp']==[48]
    assert plan['missing_ionic']==[]


def test_pair_cost_interpolation_is_pointwise_and_rejects_key_drift():
    lo={(0,0):2.0,(0,1):4.0};hi={(0,0):6.0,(0,1):8.0}
    assert interpolate_pair_costs(lo,hi,0.5)=={(0,0):4.0,(0,1):6.0}
    with pytest.raises(ValueError,match='keys'):
        interpolate_pair_costs(lo,{(0,0):6.0},0.5)


def test_jvp_assemble_product_rule_for_simple_channel():
    d=fake_d();raw=np.zeros((2,2,3,12,12),np.clongdouble)
    # channel 0 is active=0,j=0, angle=0; coefficients select primitive (0,0)
    raw[0,0,0,0,0]=3+2j
    raw[0,1,0,0,0]=5-1j
    O,dot=jvp_assemble(raw,d,z=0.0)
    v=np.longdouble(2.0);de=np.longdouble(d['phase_E'][0]-d['phase_E'][47])
    expected_O=3+2j
    expected_dot=v*(5-1j)+1j*(v*v/2+de)*expected_O
    assert O[0,0]==expected_O
    assert np.allclose(dot[0,0],expected_dot,rtol=0,atol=1e-18)


def test_od_finalize_uses_frozen_connection_formula():
    d=fake_d();comp=np.zeros((3,47,2),np.clongdouble)
    comp[0,0,0]=2+1j;comp[1,0,0]=3-2j;comp[2,0,0]=-1+4j
    out=od_finalize(comp,d,z=0.0)
    v=np.longdouble(2);kc=v/2;ka=v/2;kb=-v/2
    O=2+1j;G1=3-2j;G2=-1+4j
    expected_col=kc*(G1+G2)+1j*(kc*(2*kc-ka-kb)-np.longdouble(d['phase_E'][47]))*O
    expected_row=-ka*G1.conjugate()-kb*G2.conjugate()-1j*np.longdouble(d['phase_E'][0])*O.conjugate()
    assert np.allclose(out['D_col'][0,0],expected_col,rtol=0,atol=1e-18)
    assert np.allclose(out['D_row'][0,0],expected_row,rtol=0,atol=1e-18)


def test_cp4_source_audit_binds_exact_provider_family(tmp_path):
    import hashlib
    import wu088_hh.r31n as r31n
    assert callable(getattr(r31n,'audit_cp4_root',None)), 'audit_cp4_root must exist'
    files={
      'completion/mixed_derivative/jvp.cpp':'jvp',
      'completion/mixed_h/od_run.py':'od',
      'completion/ionic/ionic.py':'ionic',
    }
    expected={}
    for rel,text in files.items():
        p=tmp_path/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        expected[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
    out=r31n.audit_cp4_root(tmp_path,expected)
    assert out['all_match'] is True
    (tmp_path/'completion/ionic/ionic.py').write_text('changed')
    with pytest.raises(ValueError,match='CP4 source identity'):
        r31n.audit_cp4_root(tmp_path,expected)


def test_cost_order_keeps_all_pairs_and_descends():
    import wu088_hh.r31n as r31n
    assert callable(getattr(r31n,'order_pairs_by_cost',None)), 'order_pairs_by_cost must exist'
    costs={(0,0):1.0,(0,1):3.0,(1,0):2.0}
    assert r31n.order_pairs_by_cost(costs)==[(0,1),(1,0),(0,0)]


def test_od_contract_reproduces_component_contraction_for_simple_channel():
    import wu088_hh.r31n as r31n
    assert callable(getattr(r31n,'od_contract',None)), 'od_contract must exist'
    d=fake_d();raw=np.zeros((2,3,3,12,12),np.clongdouble);sa=np.zeros(raw.shape,np.longdouble)
    raw[0,0,0,0,0]=2+3j; raw[0,1,0,0,0]=4+5j; raw[0,2,0,0,0]=6+7j
    sa[0,:,0,0,0]=[2,4,6]
    comp,summed=r31n.od_contract(raw,sa,d,z=0.0)
    assert comp[0,0,0]==2+3j
    assert comp[1,0,0]==4+5j
    assert comp[2,0,0]==6+7j
    assert np.array_equal(summed[:,0,0],np.array([2,4,6],dtype=np.longdouble))


def test_jvp_initializer_sanitizes_dynamic_loader_environment_before_native_build(tmp_path, monkeypatch):
    import importlib.util
    import os
    import types
    from pathlib import Path

    script=Path(__file__).resolve().parents[1]/'scripts'/'r31n_provider_fill.py'
    spec=importlib.util.spec_from_file_location('r31n_provider_fill_under_test',script)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    monkeypatch.setattr(mod,'_worker_slot',lambda *args,**kwargs: None)
    monkeypatch.setenv('LD_LIBRARY_PATH','/tmp/forbidden-lib')
    monkeypatch.setenv('LD_PRELOAD','/tmp/forbidden-preload.so')

    class FakeNative:
        def __init__(self):
            assert os.environ.get('LD_LIBRARY_PATH') is None
            assert os.environ.get('LD_PRELOAD') is None

    monkeypatch.setattr(mod.importlib,'import_module',lambda name: types.SimpleNamespace(Native=FakeNative))
    grid=tmp_path/'cont2c'/'convergence';grid.mkdir(parents=True)
    np.savez(grid/'frozen_grid_n192.npz',dummy=np.array([1]))
    mod.init_jvp(str(tmp_path),48,[],None,None,None)
