"""Control-flow integration tests using an explicitly synthetic batch backend."""
from pathlib import Path
import importlib
import sys
import pytest
sys.path.insert(0,str(Path(__file__).parent))

def api():
    assert (Path(__file__).parent/'m3_postidle.py').exists(), 'opt-in driver absent'
    return importlib.import_module('m3_postidle')

def sample():
    return dict(all_exact=True, active_worker_count=32, worker_cpu_parallelism=20,
                nr_throttled_delta=0, effective_cpu_parallelism=21,
                tasks_completed=132, unique_pair_count=12,
                batch_wall_seconds=10., steady_state_pairs_per_second=13.2,
                throttled_usec_delta=0, swap_before=0, swap_after=0,
                memory_events_delta={'high':0,'max':0,'oom':0,'oom_kill':0},
                ancestor_cpu_deltas={'/synthetic':{'nr_throttled':0,'throttled_usec':0}})

def test_three_measured_calls_not_memoized():
    count=[];checks=[];emitted=[]
    def measured():count.append(1);return sample()
    rows=api().perform_measured_batches(measured,lambda:checks.append(1),emitted.append,32)
    assert len(count)==3 and len(checks)==6 and len(emitted)==3 and len(rows)==3

def test_readonly_precheck_blocks_before_batch():
    def reject():raise ValueError('grant drift')
    def forbidden():raise AssertionError('native work called before admission')
    with pytest.raises(ValueError):api().perform_measured_batches(forbidden,reject,lambda x:None,32)

def test_exactness_failure_is_not_pass():
    events=[]
    def wrong():return dict(sample(),all_exact=False)
    with pytest.raises(RuntimeError):api().perform_measured_batches(wrong,lambda:None,events.append,32)
    assert len(events)==1 and events[0]['measurement_status']=='EXACTNESS_OR_THROTTLING_FAILED'

def test_throttled_sample_rejected():
    events=[]
    def throttled():return dict(sample(),nr_throttled_delta=1)
    with pytest.raises(RuntimeError):api().perform_measured_batches(throttled,lambda:None,events.append,32)
    assert len(events)==1 and events[0]['measurement_status']=='EXACTNESS_OR_THROTTLING_FAILED'


def test_postcheck_failure_keeps_completed_measurement():
    events=[]; checks=[]
    def recheck():
        checks.append(1)
        if len(checks)==2:raise ValueError('allocation changed')
    with pytest.raises(ValueError):api().perform_measured_batches(sample,recheck,events.append,32)
    assert len(events)==1 and events[0]['measurement_status']=='POSTCHECK_FAILED'


def test_malformed_layout_preserves_preflight_failure(tmp_path, monkeypatch):
    m = api()
    monkeypatch.setattr(m, '_runtime', lambda: (_ for _ in ()).throw(
        AssertionError('native runtime must not load')))
    out = tmp_path/'attempt.json'
    missing = tmp_path/'unused.json'
    args = ['--phase', 'benchmark', '--configs', '64x1,bad']
    for name in ('build', 'h0-cache', 'grant', 'reference-cache', 'exactness', 'pilot'):
        args.extend(('--'+name, str(missing)))
    args.extend(('--out', str(out)))
    with pytest.raises(ValueError):
        m.main(args)
    import json
    saved = json.loads(out.read_text())
    assert saved['status'] == 'BLOCKED'
    assert saved['failure_stage'] == 'preflight'
    assert saved['failure']['type'] == 'ValueError'
    assert saved['new_scientific_nodes'] == 0

def test_failed_second_batch_leaves_first_checkpoint():
    events=[];calls=[]
    def batch():
        calls.append(1)
        if len(calls)==2:raise RuntimeError('interruption')
        return sample()
    with pytest.raises(RuntimeError):api().perform_measured_batches(batch,lambda:None,events.append,32)
    assert len(events)==1 and len(calls)==2

def test_numeric_context_is_path_independent(tmp_path):
    import types
    import numpy as np
    import controls
    m=api();a=tmp_path/'a';b=tmp_path/'b';a.mkdir();b.mkdir()
    for folder in (a,b):
        (folder/'seed.py').write_text('# same source\n')
        (folder/'ref.so').write_bytes(b'reference');(folder/'cand.so').write_bytes(b'candidate')
    h0=types.SimpleNamespace(manifest={'binary_sha256':'123','spec':{'flags':['strict']}})
    h0mod=types.SimpleNamespace(verify_sources=lambda:{'input':'456'})
    def context(folder):
        built={'libraries':{'reference':{'path':str(folder/'ref.so')},'candidate':{'path':str(folder/'cand.so')}}}
        return m._numeric_context(controls,types.SimpleNamespace(np=np),h0mod,h0,
            types.SimpleNamespace(__file__=str(folder/'seed.py')),built,(np.eye(2),))
    assert context(a)==context(b)
    (b/'cand.so').write_bytes(b'changed')
    assert context(a)!=context(b)


def test_existing_h0_cache_uses_authority_compiler_identity(tmp_path):
    import hashlib
    import json
    import shutil
    import subprocess
    import types
    m=api()
    compiler=shutil.which('g++')
    spec={'sources':{'source':'sha'}, 'flags':['-fno-fast-math'],
          'compiler_version':subprocess.run([str(Path(compiler).resolve()),'--version'],
                                          capture_output=True,text=True,check=True).stdout}
    key=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()
    folder=tmp_path/key
    folder.mkdir()
    (folder/'h0.so').write_bytes(b'binary')
    (folder/'BUILD.json').write_text(json.dumps({'spec':spec}))
    h0=types.SimpleNamespace(verify_sources=lambda:spec['sources'],FLAGS=spec['flags'])
    m._require_existing_h0_cache(h0,tmp_path)


def test_foreign_build_rejects_binary_drift(tmp_path, monkeypatch):
    import controls
    m=api()
    monkeypatch.setattr(m,'ROOT',tmp_path)
    source=tmp_path/'native/reference/source.cpp'
    source.parent.mkdir(parents=True)
    source.write_bytes(b'source')
    library=tmp_path/'reference.so'
    library.write_bytes(b'binary')
    built={'identity':{'sources':{'reference/source.cpp':controls.sha256(source)}},
           'libraries':{'reference':{'path':str(library),'sha256':controls.sha256(library)},
                        'candidate':{'path':str(library),'sha256':controls.sha256(library)}}}
    m._verify_foreign_build(controls,built)
    library.write_bytes(b'changed')
    with pytest.raises(RuntimeError,match='binary drift'):
        m._verify_foreign_build(controls,built)

def valid_pilot():
    return {
        'stage':'pilot','n':192,'g':80,'z':2.0,
        'status':'PASS_BOUNDED_PERSISTENT_WORKER_SCREEN',
        'pilot_private_worker_bytes':32454656,
        'configurations':[{
            'processes':1,'threads_per_process':1,
            'status':'PASS_EXACT_RESOURCE_GATES','memory_gate_pass':True,
            'private_worker_bytes':31553536,
            'warmup':{'all_exact':True,'sum_pss_bytes':32454656},
        }],
    }


def test_pilot_receipt_bound_to_b192_g80_z2_and_observed_memory():
    m=api()
    assert m._validate_pilot_receipt(valid_pilot())==32454656
    for key,value in [('n',160),('g',79),('z',1.0)]:
        bad=valid_pilot();bad[key]=value
        with pytest.raises(ValueError):m._validate_pilot_receipt(bad)
    bad=valid_pilot();bad['configurations'][0]['warmup']['sum_pss_bytes']=32454657
    with pytest.raises(ValueError):m._validate_pilot_receipt(bad)
    bad=valid_pilot();bad['configurations'][0]['processes']=2
    with pytest.raises(ValueError):m._validate_pilot_receipt(bad)
    bad=valid_pilot();bad['configurations'][0]['warmup']['all_exact']=False
    with pytest.raises(ValueError):m._validate_pilot_receipt(bad)


def valid_exactness():
    d = {
        'status':'PASS_SAME_HOST_FULL_PAIR_EXACT_NOT_PRODUCTION',
        'all_exact':True,
        'h0_binary_sha256':'h0',
        'h0_source_sha256':{'source':'sha'},
        'foreign_build_key':'build',
        'grid_seed_sha256':'seed',
        'rows':[
            {'n':160,'g':80,'z':2.0,'pair':[3,7],'all_exact':True},
            {'n':192,'g':80,'z':2.0,'pair':[10,11],'all_exact':True},
        ],
    }
    for row in d['rows']:
        row['components'] = {
            name: {'exact': True, 'max_abs_delta': 0., 'dtype': dtype, 'shape': shape}
            for name, dtype, shape in (
                ('H0','complex256',[2,7,3]), ('H0_sumabs','float128',[2,7,3]),
                ('foreign','complex256',[2,2,3]), ('foreign_sumabs','float128',[2,2,3]))}
    return d


def test_exactness_receipt_requires_fixed_geometry_rows():
    m=api()
    context={'h0_binary_sha256':'h0','authority_sources':{'source':'sha'},
             'seed_sha256':'seed'}
    built={'build_key':'build'}
    samples={160:[(3,7)],192:[(10,11)]}
    m._validate_exactness_receipt(valid_exactness(),context,built,samples)
    for key,value in [('g',81),('z',4.0)]:
        bad=valid_exactness();bad['rows'][1][key]=value
        with pytest.raises(RuntimeError,match='lacks required n/g/z'):
            m._validate_exactness_receipt(bad,context,built,samples)
