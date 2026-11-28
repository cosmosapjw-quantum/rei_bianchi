"""Focused non-native tests for the opt-in R31V path."""
import importlib
import json
import math
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))

def api():
    assert (Path(__file__).parent/'controls.py').exists(), 'R31V implementation absent'
    return importlib.import_module('controls')

PAIRS = [(i, i+1) for i in range(12)]

def live(**overrides):
    d = dict(allowed_cpus=list(range(64)), cpu_budget=64, boot_id='test-boot',
             memory_available_bytes=128*2**30, cgroup_path='/sys/fs/cgroup/job')
    d.update(overrides)
    return d

def grant(**overrides):
    d = dict(schema='WU088_R31V_GRANT_V1', epoch_id='test-epoch',
             mode='BENCHMARK_EXCLUSIVE', cpus=list(range(32)), boot_id='test-boot',
             expires_unix=2000, memory_reserve_bytes=2**30,
             fixed_workload_132_approved=True, idle_census_confirmed=True)
    d.update(overrides)
    return d

def arrays():
    return {k:np.arange(6, dtype=np.float64).reshape(2,3).astype(np.complex128)*(1+2j)
            for k in ('H0','H0_sumabs','foreign','foreign_sumabs')}

def test_balanced_work_is_layout_independent():
    c=api(); tasks=c.balanced_workload(PAIRS)
    assert len(tasks)==132 and all(tasks.count(p)==11 for p in PAIRS)
    assert c.workload_identity(tasks)==c.workload_identity(list(tasks))

@pytest.mark.parametrize('pairs',[[],PAIRS[:11],PAIRS+[PAIRS[0]],[(True,1)]+PAIRS[1:],[(0,-1)]+PAIRS[1:]])
def test_bad_pairs_rejected(pairs):
    with pytest.raises(ValueError): api().balanced_workload(pairs)

def test_workload_identity_binds_order():
    c=api();a=c.balanced_workload(PAIRS)
    assert c.workload_identity(a)!=c.workload_identity(a[::-1])

@pytest.mark.parametrize('text,expected',[('max 100000',math.inf),('3200000 100000',32.0),('150000 100000',1.5)])
def test_quota(text,expected): assert api().parse_cpu_max(text)==expected

@pytest.mark.parametrize('text',['0 100000','-1 100000','10 0','max','max nan','NaN 1','10 10 10'])
def test_invalid_quota(text):
    with pytest.raises(ValueError): api().parse_cpu_max(text)

def test_grant_not_host_count():
    c=api();a=c.validate_grant(grant(),live(),[(16,2),(32,1)],now=1000)
    assert a['budget']==32 and a['cpus']==list(range(32))

@pytest.mark.parametrize('change',[
    {'boot_id':'other'},{'expires_unix':999},{'expires_unix':float('nan')},
    {'cpus':[0,0]},{'cpus':[True,2]}, {'memory_reserve_bytes':-1},
    {'mode':'SHARED'},{'idle_census_confirmed':False},{'fixed_workload_132_approved':False}])
def test_invalid_grant(change):
    with pytest.raises(ValueError):api().validate_grant(grant(**change),live(),[(1,1)],now=1000)

@pytest.mark.parametrize('actual',[
    live(allowed_cpus=list(range(16))),live(cpu_budget=15),
    live(memory_available_bytes=2**29)])
def test_live_restrictions_not_saved_probe(actual):
    with pytest.raises(ValueError):api().validate_grant(grant(),actual,[(16,2)],now=1000)

def test_layout_rejected_before_science():
    with pytest.raises(ValueError):api().validate_grant(grant(),live(),[(64,1)],now=1000)

@pytest.mark.parametrize('layouts',[[],[(1,1),(1,1)],[(0,1)],[(True,1)],[(1,-1)]])
def test_bad_layouts(layouts):
    with pytest.raises(ValueError):api().validate_grant(grant(),live(),layouts,now=1000)

def test_cache_roundtrip_and_missing_readonly(tmp_path):
    c=api();store=c.ReferenceCache(tmp_path,{'schema':'test','model_sha':'abc'})
    with pytest.raises(FileNotFoundError):store.read((1,2))
    store.write((1,2),arrays());out=store.read((1,2))
    for k,v in arrays().items():
        assert out[k].dtype==v.dtype and out[k].shape==v.shape and out[k].tobytes()==v.tobytes()

def test_cache_context_separation(tmp_path):
    c=api();a=c.ReferenceCache(tmp_path,{'model':'a'});b=c.ReferenceCache(tmp_path,{'model':'b'})
    a.write((1,2),arrays())
    with pytest.raises(FileNotFoundError):b.read((1,2))

def test_cache_rejects_tamper(tmp_path):
    c=api();s=c.ReferenceCache(tmp_path,{'model':'a'});s.write((1,2),arrays());p=s.path((1,2))
    d=json.loads(p.read_text());d['arrays']['H0']['hex']='00'+d['arrays']['H0']['hex'][2:]
    # Force a byte change even when the first source byte was already zero.
    d['arrays']['H0']['hex']='ff'+d['arrays']['H0']['hex'][2:]
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError):s.read((1,2))

def test_cache_dtype_shape_checked_even_with_valid_payload_hash(tmp_path):
    c=api();s=c.ReferenceCache(tmp_path,{});s.write((1,2),arrays());p=s.path((1,2))
    d=json.loads(p.read_text());d['arrays']['H0']['shape']=[99,99]
    d['payload_sha256']=c.digest_json(d['arrays']);p.write_text(json.dumps(d))
    with pytest.raises(ValueError):s.read((1,2))

def test_cache_nonfinite_and_object_rejected(tmp_path):
    c=api();s=c.ReferenceCache(tmp_path,{});a=arrays();a['H0'][0,0]=np.nan
    with pytest.raises(ValueError):s.write((1,2),a)
    a=arrays();a['H0']=np.array([object()],dtype=object)
    with pytest.raises(ValueError):s.write((1,2),a)

def test_cache_create_only(tmp_path):
    c=api();s=c.ReferenceCache(tmp_path,{});s.write((1,2),arrays())
    with pytest.raises(FileExistsError):s.write((1,2),arrays())
    assert not list(tmp_path.rglob('*.tmp'))

def test_cache_rejects_pair_and_context_tamper(tmp_path):
    c=api();s=c.ReferenceCache(tmp_path,{});s.write((1,2),arrays());p=s.path((1,2))
    d=json.loads(p.read_text());d['pair']=[2,1];p.write_text(json.dumps(d))
    with pytest.raises(ValueError):s.read((1,2))

def test_nan_context_rejected(tmp_path):
    with pytest.raises(ValueError):api().ReferenceCache(tmp_path,{'x':float('nan')})

def test_cache_has_no_compute_fallback(tmp_path):
    s=api().ReferenceCache(tmp_path,{})
    assert not hasattr(s,'compute') and not hasattr(s,'get_or_compute')

def test_ancestor_limits_are_combined(tmp_path):
    c=api();root=tmp_path/'cg';leaf=root/'a'/'b';leaf.mkdir(parents=True)
    for p,q,mem in [(root,'max 100000',('max','0')),(root/'a','150000 100000',('1000','400')),(leaf,'3200000 100000',('2000','200'))]:
        (p/'cpu.max').write_text(q);(p/'memory.max').write_text(mem[0]);(p/'memory.current').write_text(mem[1])
    limits=c.hierarchy_limits(root,leaf,64,10000)
    assert limits['cpu_budget']==1 and limits['memory_available_bytes']==600

def test_incomplete_ancestor_fails_closed(tmp_path):
    c=api();root=tmp_path/'cg';leaf=root/'job';leaf.mkdir(parents=True)
    with pytest.raises(ValueError):c.hierarchy_limits(root,leaf,64,10000)
