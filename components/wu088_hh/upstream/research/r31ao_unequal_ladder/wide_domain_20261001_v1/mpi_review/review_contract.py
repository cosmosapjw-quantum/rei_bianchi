"""Independent adversarial admission checks; no MPI or numerical execution.

Uses real immutable native input/build authorities for preparation. Only copied
review-owned metadata is mutated. cgroup containment is not emulated or claimed.
"""
import hashlib
import importlib.util
import json
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
HOST = HERE.parent / 'mpi_native_host'
OLD = HERE.parent.parent / 'native_execution_20261001_v1'
sys.path.insert(0, str(HOST))
import launcher as h


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p): return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-name',default='contract_run')
    a=parser.parse_args()
    if not a.output_name.replace('_','').isalnum(): raise ValueError('simple review output name required')
    out = HERE / a.output_name
    out.mkdir()
    before = {str(p.relative_to(HOST)): sha(p) for p in HOST.glob('*.py')}
    sys.path.insert(0, str(OLD / 'mpi_native_tasks'))
    prepare = load('review_prepare', OLD / 'mpi_native_tasks/prepare.py')
    old = json.loads((OLD / 'mpi_native_tasks/readback_bundle_cached_strict/MANIFEST.json').read_text())
    bundle = out / 'bundle'
    prepare.prepare(old['files']['input_npz']['path'], old['files']['plan']['path'],
        old['plan_sha256'], str(Path(old['files']['build']['path']).parent), old['build_sha256'],
        old['files']['limits']['path'], [0], bundle)
    prep = bundle / 'PREPARATION.json'
    original = {name:(bundle/name).read_bytes() for name in ('PREPARATION.json','WORKLIST.txt','bound_worker.py')}
    results = []

    def test(name, fn, expect_refusal=False):
        try:
            fn()
        except (ValueError, OSError, KeyError, TypeError) as exc:
            if not expect_refusal: raise
            results.append({'case':name,'status':'PASS','observed_refusal':str(exc)})
        else:
            if expect_refusal: raise AssertionError('unexpected acceptance: '+name)
            results.append({'case':name,'status':'PASS'})

    def verify(): return h.bundle_check(str(prep), sha(prep))
    def restore():
        for name, data in original.items(): (bundle/name).write_bytes(data)
    def reseal(key, name, data):
        (bundle/name).write_bytes(data)
        p=json.loads(prep.read_text()); p[key]=record(bundle/name)
        prep.write_bytes(h.canonical(p)+b'\n')

    test('real_native_preparation_identity_and_empty_output', verify)
    test('wrong_external_preparation_sha', lambda:h.bundle_check(str(prep),'0'*64),True)
    reseal('worklist','WORKLIST.txt',b'1\n1 40\n')
    test('resealed_wrong_task_worklist',verify,True); restore()
    reseal('bound_worker','bound_worker.py',b'raise SystemExit(0)\n')
    test('resealed_arbitrary_bound_worker',verify,True); restore()
    stale=bundle/'results'/'primitive_0000.json.claim'; stale.write_bytes(b'')
    test('stale_claim_prevents_dispatch',verify,True); stale.unlink()
    stale=bundle/'results'/'primitive_0000.json'; stale.write_bytes(b'{}\n')
    test('stale_output_prevents_dispatch',verify,True); stale.unlink()
    def root_refusal():
        with patch.object(h.os,'getuid',return_value=0), patch.object(h,'parent_check') as parent:
            try: h.run(SimpleNamespace())
            finally: parent.assert_not_called()
    test('root_refuses_before_plan_or_cgroup_access',root_refusal,True)
    test('ordinary_directory_cannot_impersonate_cgroup2',lambda:h.parent_check(out),True)
    test('review_bundle_restored_after_mutations',verify)
    large_limits=out/'limits_2048.json'
    value=dict(old['native_limits']); value['memory_mib']=2048
    large_limits.write_bytes(h.canonical(value)+b'\n')
    large=out/'bundle_2048'
    prepare.prepare(old['files']['input_npz']['path'],old['files']['plan']['path'],
        old['plan_sha256'],str(Path(old['files']['build']['path']).parent),old['build_sha256'],
        str(large_limits),[0],large)
    def larger_limit():
        p=large/'PREPARATION.json'
        h.prepare_plan(SimpleNamespace(preparation=str(p),preparation_sha256=sha(p)))
    test('valid_2048_mib_preparation_refused_before_mpi_admission',larger_limit,True)
    def target_limits():
        # Ordinary files model kernel values; this is not a cgroup runtime test.
        planner=h.module('_review_planner',h.PLANNER)
        mount=out/'mock_cgroup_mount'; parent=mount/'delegated'; parent.mkdir(parents=True)
        GiB=1024**3
        for path,cpu,mem,current in [(mount,'2 1',4*GiB,GiB//2),(parent,'1 1',2*GiB,GiB//4)]:
            for name,value in [('cpu.max',cpu),('memory.max',mem),('memory.current',current)]:
                (path/name).write_text(str(value)+'\n')
        (parent/'cpuset.cpus.effective').write_text('2-3\n')
        original_read=Path.read_text
        def read_text(path,*args,**kwargs):
            if str(path)=='/proc/self/mountinfo':
                return '1 0 0:1 / '+str(mount)+' rw - cgroup2 cgroup rw\n'
            return original_read(path,*args,**kwargs)
        host={'affinity_os_cpus':list(range(8)),
            'cpus':[{'os_cpu':i,'package':0,'core':i} for i in range(8)],
            'cgroup':{'ancestors':[],'errors':[]},'errors':[],
            'memory_available_bytes':8*GiB,'memory_total_bytes':8*GiB}
        with patch.object(Path,'read_text',read_text):
            merged=h.target_resources(planner,host,parent)
        assert merged['affinity_os_cpus']==[2,3]
        assert len(merged['target_cgroup_ancestors'])==2
        rejected=planner.plan(merged,reserve_bytes=GiB//4,requested_ranks=2)
        admitted=planner.plan(merged,reserve_bytes=GiB//4,requested_ranks=1)
        assert rejected['status']=='BLOCKED' and rejected['cpu_budget']==1
        assert admitted['status']=='PLAN_READY' and admitted['rank_os_cpus']==[2]
        assert admitted['observed_available_memory_bytes']==7*GiB//4
    test('mock_target_ancestor_limits_and_cpuset_bound_rank_admission',target_limits)
    def root_probe():
        probe=h.module('_review_containment_probe',HOST/'containment_probe.py')
        p=out/'must_not_create'
        with patch.object(probe.os,'getuid',return_value=0):
            try: probe.probe('/sys/fs/cgroup',p,[0])
            finally: assert not p.exists()
    test('probe_imports_and_refuses_root_without_creating_output',root_probe,True)
    after = {str(p.relative_to(HOST)): sha(p) for p in HOST.glob('*.py')}
    assert before == after, 'host source changed during independent review'
    receipt={'schema':'WU088_MPI_HOST_INDEPENDENT_ADMISSION_REVIEW_V1','status':'PASS',
        'cases':results,'case_count':len(results),'source_pins':before,
        'real_input_bindings_checked':True,'native_HH_runs':0,'MPI_runs':0,
        'actual_cgroup_execution':False,'root_bypass':False,
        'mock_kernel_values_used_only_for_target_resource_policy_test':True,
        'scope':'source and real native bundle authority checks; no containment/runtime certification'}
    (out/'REVIEW_RUN.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__': main()
