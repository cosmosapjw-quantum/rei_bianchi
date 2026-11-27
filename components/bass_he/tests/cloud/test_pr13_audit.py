"""Regression cases for the independent PR 13 runner audit."""
import hashlib
from pathlib import Path

import pytest

from bass_he.cloud.resources import HostInventory, inventory, worker_limit


GIB = 1024**3


def test_hard_headroom_uses_current_usage_and_preserves_buffers():
    current = int(.649 * 128 * GIB)
    host = HostInventory(64, 64, 128 * GIB, current, True, ())
    profile = {'workers': 64, 'controller_reserve_bytes': GIB,
               'memory_buffer_bytes': 2 * GIB}
    allowed = worker_limit(profile, host, 42, 4 * GIB)
    assert allowed > 0
    assert current + allowed * 4 * GIB + 3 * GIB <= int(.75 * 128 * GIB)
    active = worker_limit(profile, host, 42, 4 * GIB, active_count=2)
    assert active == allowed + 2


def test_cgroup_root_limits_are_included(tmp_path, monkeypatch):
    import os
    proc = tmp_path / 'proc'; (proc / 'self').mkdir(parents=True)
    (proc / 'meminfo').write_text('MemTotal: 1024000 kB\n')
    (proc / 'self' / 'cgroup').write_text('0::/job\n')
    root = tmp_path / 'cg'; job = root / 'job'; job.mkdir(parents=True)
    (root / 'cpu.max').write_text('100000 100000')
    (root / 'memory.max').write_text('500000000')
    (job / 'cpu.max').write_text('max 100000')
    (job / 'memory.max').write_text('max')
    (job / 'memory.current').write_text('1000')
    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0, 1, 2, 3})
    host = inventory(tmp_path, proc_root=proc, cgroup_root=root)
    assert host.quota_cpus == 1 and host.effective_memory == 500000000


def test_scientific_identity_changes_only_with_numerical_closure(tmp_path):
    from bass_he.cloud.runtime import scientific_source_identity, SCIENCE_FILES
    for name in SCIENCE_FILES:
        path = tmp_path / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(name.encode())
    original = scientific_source_identity(tmp_path)
    (tmp_path / 'src/bass_he/cloud/store.py').write_text('runner change')
    (tmp_path / 'docs.md').write_text('docs change')
    assert scientific_source_identity(tmp_path) == original
    for name in ('src/bass_he/spectral.py', 'src/bass_he/sturm_anchor.py',
                 'src/bass_he/replay_contract.py'):
        path = tmp_path / name; before = path.read_bytes()
        path.write_bytes(before + b'changed')
        assert scientific_source_identity(tmp_path) != original
        path.write_bytes(before)


def test_calibration_receipt_rejects_tamper_and_binding_drift():
    from bass_he.cloud.calibration import make_worker_receipt, admit_calibrated_workers
    receipt = make_worker_receipt(40, 'binding-a', {'OPENBLAS_NUM_THREADS': '1'}, 'rss-a')
    assert admit_calibrated_workers(40, receipt, 'binding-a', {'OPENBLAS_NUM_THREADS': '1'}, 'rss-a')
    with pytest.raises(ValueError):
        admit_calibrated_workers(40, {**receipt, 'selected': 64}, 'binding-a', {'OPENBLAS_NUM_THREADS': '1'}, 'rss-a')
    with pytest.raises(ValueError):
        admit_calibrated_workers(40, receipt, 'binding-b', {'OPENBLAS_NUM_THREADS': '1'}, 'rss-a')
    with pytest.raises(ValueError):
        admit_calibrated_workers(40, receipt, 'binding-a', {'OPENBLAS_NUM_THREADS': '2'}, 'rss-a')


def test_calibrated_admission_requires_three_valid_perf_repeats(tmp_path):
    import json
    from bass_he.cloud.calibration import make_worker_receipt,verify_sweep_evidence
    path=tmp_path/'WORKER_SWEEP.json'
    report={'binding':'binding-a','thread_policy':{'OPENBLAS_NUM_THREADS':'1'},
        'memory_receipt_sha256':'rss-a','selected':40,'namespace':'PERF_NOT_SCIENCE',
        'observations':[{'workers':40,'repeat':r,'valid':True} for r in range(3)]}
    path.write_text(json.dumps(report))
    receipt=make_worker_receipt(40,'binding-a',report['thread_policy'],'rss-a',
        hashlib.sha256(path.read_bytes()).hexdigest())
    assert verify_sweep_evidence(tmp_path/'ADMISSION_RECEIPT.json',receipt)
    report['observations'][2]['valid']=False;path.write_text(json.dumps(report))
    receipt=make_worker_receipt(40,'binding-a',report['thread_policy'],'rss-a',
        hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError,match='three valid'):
        verify_sweep_evidence(tmp_path/'ADMISSION_RECEIPT.json',receipt)


def test_explicit_import_is_labeled_and_science_mismatch_rejected(tmp_path):
    import json
    from bass_he.cloud.contracts import (Attempt, CaseSpec, CaseOutcome,
        ExecutionBinding, outcome_document, task_id)
    from bass_he.cloud.store import ResultStore
    from bass_he.cloud.import_evidence import import_completed
    old = ExecutionBinding('old', 'tree', 'runner-a', 'python', {}, 'cpu', {},
                           scientific_source_id='science-a')
    new = ExecutionBinding('new', 'tree', 'runner-b', 'python', {}, 'cpu', {},
                           scientific_source_id='science-a')
    spec = CaseSpec('wrong_pair_check', {'source':'science-a','backend':'python',
        'depth':1,'pair':[[1,0,0],[2,0,0]],'seed':{'complex':[1.,2.]}})
    source = ResultStore(tmp_path/'source', old);source.begin_epoch()
    att = source.claim(spec);path = source.attempt_path(att)
    path.write_text(json.dumps(outcome_document(spec, CaseOutcome('WRONG_PAIR',{},
        {'reason':'pair membership rejected'}),old,att))+'\n')
    source.commit(att,path);source.close()
    target = ResultStore(tmp_path/'target',new)
    try:
        assert import_completed(source.root,target)==1
        doc=json.loads((target.root/'results'/task_id(spec)/'result.json').read_text())
        assert doc['provenance']['classification']=='IMPORTED_EVIDENCE'
        assert target.load(task_id(spec)).status=='WRONG_PAIR'
    finally:target.close()
    wrong = ExecutionBinding('new', 'tree', 'runner-b', 'python', {}, 'cpu', {},
                             scientific_source_id='science-b')
    other = ResultStore(tmp_path/'other',wrong)
    try:
        with pytest.raises(ValueError,match='scientific'):
            import_completed(source.root,other)
    finally:other.close()


def test_legacy_binding_hashes_resolve_to_same_science_identity():
    from bass_he.cloud.runtime import binding,scientific_source_identity
    from bass_he.cloud.contracts import ExecutionBinding
    from bass_he.cloud.import_evidence import _old_science_id
    repo=Path(__file__).resolve().parents[2]
    current=binding(repo)
    legacy=ExecutionBinding(current.source_commit,current.source_tree,current.runner_sha256,
        current.python,current.packages,current.machine,current.thread_policy)
    assert _old_science_id(legacy)==scientific_source_identity(repo)


def test_memory_receipt_rejects_guess_and_tamper(tmp_path):
    from bass_he.cloud.memory_calibration import _write_receipt,verify_memory_receipt
    from bass_he.cloud.contracts import ExecutionBinding
    bind=ExecutionBinding('c','t','r','python',{},'cpu',{},scientific_source_id='science')
    body={'status':'PASS','binding':bind.identity(),'scientific_source_id':'science',
          'thread_policy':{},'worker_rss_p95_bytes':4096}
    path=tmp_path/'receipt.json';_write_receipt(path,body)
    assert verify_memory_receipt(path,bind)['worker_rss_p95_bytes']==4096
    changed=__import__('json').loads(path.read_text());changed['worker_rss_p95_bytes']=8192
    path.write_text(__import__('json').dumps(changed))
    with pytest.raises(RuntimeError,match='BLOCKED_MEMORY_CALIBRATION'):
        verify_memory_receipt(path,bind)


def test_checkpoint_receipt_directory_is_fsynced(tmp_path,monkeypatch):
    import os
    from bass_he.cloud.contracts import ExecutionBinding
    from bass_he.cloud.export import export_checkpoint
    from bass_he.cloud.store import ResultStore
    bind=ExecutionBinding('c','t','r','python',{},'cpu',{})
    store=ResultStore(tmp_path/'run',bind);dest=tmp_path/'exports';seen=[]
    real=os.fsync
    def fsync(fd):
        seen.append(Path(os.readlink(f'/proc/self/fd/{fd}')))
        return real(fd)
    monkeypatch.setattr(os,'fsync',fsync)
    try:
        export_checkpoint(store,dest)
        assert seen.count(dest)>=2 # archive publication and receipt publication
    finally:store.close()
