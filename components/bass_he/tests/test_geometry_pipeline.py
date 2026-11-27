import importlib,json
import numpy as np
import pytest


def api():
    assert importlib.util.find_spec('bass_he.geometry') is not None,'audited geometry pipeline missing'
    return importlib.import_module('bass_he.geometry')


def test_geometry_has_no_energy_or_exponent_input():
    import inspect
    mod=api()
    names=inspect.signature(mod.contour_geometry).parameters
    assert 'energy' not in names and 'exponent_factor' not in names


def test_q12_regularized_simpson_matches_published_action():
    mod=api()
    from bass_he.spectral import find_exceptional_point
    ep=find_exceptional_point((1,0,0),(2,1,0),1.212587527786+1.363819821336j,depth=64)
    r=mod.contour_geometry(ep,0.,panels=32)
    assert abs(r['delta']-1.42615)<8e-5
    assert r['max_spectral_residual']<5e-9
    assert r['minimum_normalized_sheet_gap']>1e-4
    assert r['endpoint_assumption']=='SIMPLE_FOLD_CERTIFICATE_REQUIRED'


def test_cutoff_quadrature_exact_piecewise_constant():
    mod=api();r,w=mod.radial_quadrature([0.,1.,2.],order=2)
    p=np.where(r<1,.2,.7)
    assert abs(np.sum(w*p)-np.pi*(.2+3*.7))<1e-13


def test_atomic_evidence_record_roundtrip_and_corruption(tmp_path):
    mod=api(); key={'source':'f00','rho':.2,'panels':32}; store=mod.EvidenceCache(tmp_path)
    store.put(key,{'delta':1.2})
    assert store.get(key)=={'delta':1.2}
    assert store.get({**key,'panels':64}) is None
    p=next(tmp_path.glob('*.json'));obj=json.loads(p.read_text());obj['payload']['delta']=5
    p.write_text(json.dumps(obj))
    with pytest.raises(ValueError,match='hash'):store.get(key)


def test_parallel_cache_same_key_is_immutable(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    mod=api();store=mod.EvidenceCache(tmp_path);barrier=threading.Barrier(8)
    def writer(i):
        barrier.wait()
        try:
            store.put({'source':'fixed'}, {'delta':i,'padding':'x'*200000})
            return True
        except ValueError:return False
    with ThreadPoolExecutor(max_workers=8) as pool: result=list(pool.map(writer,range(8)))
    assert sum(result)==1
