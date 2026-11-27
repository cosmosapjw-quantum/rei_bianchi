import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def setup_fake(tmp):
    folder=tmp/'state';folder.mkdir()
    code='''from pathlib import Path
import hashlib,json,os,time
import numpy as np
ROOT=Path(os.environ['FAKE_ROOT']);MIXED=ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def provider_gate(): return {'status':'TEST_FIXTURE'}
def folder_for(*args):return ROOT
class Hybrid12:
 identity={}
def configuration(*args):return {},np.ones(1),np.ones(1),np.ones(1),np.ones(1),1.
def build_identity_for_orchestrator(*args):return {'driver':'a'*64,'model_sha256':'b'*64}
def init(*args):pass
def pair(task):
 ia,ib,path=task;np.savez(path,ia=ia,ib=ib,value=100*ia+ib)
 return dict(ia=ia,ib=ib,sha256=sha(path),wall_seconds=.001,cpu_seconds=.001)
def assemble(*args):raise AssertionError('completed scientific assembly must not be repeated')
'''
    legacy=tmp/'fake_legacy.py';legacy.write_text(code)
    profile=dict(schema='WU088_PAIR_COST_PROFILE_V1', scientific_driver_sha256='a'*64,
                 model_sha256='b'*64,g=80,gamma_scale='unit',states=[dict(n=160,z=16,costs=[[i,j,(i+1)*(j+1)] for i in range(12) for j in range(12)])])
    p=tmp/'cost.json';p.write_text(json.dumps(profile))
    env=dict(os.environ,FAKE_ROOT=str(folder))
    cmd=[sys.executable,str(ROOT/'scripts/wide_hybrid_orchestrator_cost.py'),
         '--n','160','--z','16','--workers','1','--max-new-pairs','2',
         '--execution-lane','local','--legacy-runner',str(legacy),'--cost-profile',str(p)]
    return folder,cmd,env


def test_actual_executor_uses_cost_order_and_stops_at_budget(tmp_path):
    folder,cmd,env=setup_fake(tmp_path)
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    rows=[json.loads(l) for l in (folder/'events.jsonl').read_text().splitlines()]
    assert [(x['ia'],x['ib']) for x in rows]==[(11,11),(10,11)]
    assert len(list(folder.glob('pair_*.npz')))==2
    q=[json.loads(l) for l in (folder/'DURABLE_UPLOAD_QUEUE.jsonl').read_text().splitlines()]
    assert len(q)==1
    before=(folder/'events.jsonl').read_bytes()
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==74
    assert (folder/'events.jsonl').read_bytes()==before
    assert 'BLOCKED_PENDING_DUAL_BACKUP_ACK' in r.stdout


def test_completed_state_not_reassembled(tmp_path):
    folder,cmd,env=setup_fake(tmp_path)
    ident={'driver':'a'*64,'model_sha256':'b'*64}
    ip=folder/'IDENTITY.json';ip.write_text(json.dumps(ident))
    rows=[]
    for i in range(12):
        for j in range(12):
            p=folder/f'pair_{i:02}_{j:02}.npz';np.savez(p,ia=i,ib=j,value=i*100+j)
            rows.append(dict(ia=i,ib=j,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (folder/'events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    assembled=folder/'ASSEMBLED.npz';np.savez(assembled,H=np.ones((47,2)))
    result=dict(sha256=hashlib.sha256(assembled.read_bytes()).hexdigest(),identity_sha256=hashlib.sha256(ip.read_bytes()).hexdigest())
    (folder/'RESULTS.json').write_text(json.dumps(result))
    before=assembled.read_bytes()
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    assert 'SOURCE_COMPLETE_REUSED_NOT_REASSEMBLED' in r.stdout
    assert assembled.read_bytes()==before


def test_checkpoint_wave_reuses_one_process_pool(tmp_path):
    folder=tmp_path/'state';folder.mkdir()
    legacy=tmp_path/'fake_pool_legacy.py'
    legacy.write_text('''from pathlib import Path\nimport hashlib,json,os,time\nimport numpy as np\nROOT=Path(os.environ["FAKE_ROOT"]);MIXED=ROOT\nsha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()\ndef provider_gate(): return {"status":"TEST_FIXTURE"}\ndef folder_for(*args):return ROOT\nclass Hybrid12: identity={}\ndef configuration(*args):return {},np.ones(1),np.ones(1),np.ones(1),np.ones(1),1.\ndef build_identity_for_orchestrator(*args):return {"driver":"a"*64,"model_sha256":"b"*64}\ndef init(*args):\n p=ROOT/"init.log"\n fd=os.open(p,os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o644)\n os.write(fd,(str(os.getpid())+"\\n").encode());os.close(fd)\ndef pair(task):\n ia,ib,path=task;time.sleep(.01);np.savez(path,ia=ia,ib=ib,value=100*ia+ib)\n return dict(ia=ia,ib=ib,sha256=sha(path),wall_seconds=.01,cpu_seconds=.001)\ndef assemble(*args):raise AssertionError("not complete")\n''')
    profile=dict(schema='WU088_PAIR_COST_PROFILE_V1', scientific_driver_sha256='a'*64,
                 model_sha256='b'*64,g=80,gamma_scale='unit',states=[dict(n=160,z=16,costs=[[i,j,(i+1)*(j+1)] for i in range(12) for j in range(12)])])
    prof=tmp_path/'cost.json';prof.write_text(json.dumps(profile))
    env=dict(os.environ,FAKE_ROOT=str(folder))
    cmd=[sys.executable,str(ROOT/'scripts/wide_hybrid_orchestrator_cost.py'),
         '--n','160','--z','16','--workers','2','--max-new-pairs','6',
         '--execution-lane','local','--legacy-runner',str(legacy),'--cost-profile',str(prof)]
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    # One persistent 2-worker pool should initialize exactly two workers for the six-pair checkpoint wave.
    pids=(folder/'init.log').read_text().splitlines()
    assert len(pids)==2,pids
    assert len(set(pids))==2,pids
    rows=[json.loads(l) for l in (folder/'events.jsonl').read_text().splitlines()]
    assert len(rows)==6


def test_tuning_profile_controls_worker_and_smt_policy(tmp_path):
    from wu088_hh.autotune import host_profile_key
    from wu088_hh.hardware import inspect_host
    folder,cmd,env=setup_fake(tmp_path)
    hw=inspect_host(use_smt=True)
    budget=hw['effective_cpu_budget']
    threads=2 if budget>=4 else 1
    processes=2 if budget>=4 else 1
    build='test-build'
    profile={
      'schema':'WU088_HOST_TUNING_PROFILE_V1',
      'host_build_key':host_profile_key(hw,build),
      'source_report_sha256':'c'*64,
      'selected':{'processes':processes,'kernel_threads':threads,'use_smt':True,'repetitions':3,
                  'median_wall_s':1.0,'fastest_median_wall_s':1.0,'median_pair_cpu_s':1.0,
                  'cross_l3_workers':0,'selection_reason':'TEST','locality_tie_fraction':0.02},
      'numerical_contract':'EXACT_ARRAY_EQUALITY_REQUIRED_FOR_ALL_SELECTED_SAMPLES',
      'promotion_scope':'HOST_TUNING_ONLY__NATIVE_PROVIDER_NOT_AUTOMATICALLY_PROMOTED'}
    pp=tmp_path/'tuning.json';pp.write_text(json.dumps(profile))
    env['WU088_R31M_BUILD_KEY']=build
    base=[x for i,x in enumerate(cmd) if not (i>0 and cmd[i-1]=='--workers') and x!='--workers']
    tuned=base+['--tuning-profile',str(pp),'--describe']
    r=subprocess.run(tuned,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    d=json.loads(r.stdout)
    assert d['tuning_profile_active'] is True
    assert d['effective_workers']==processes
    assert d['kernel_threads']==threads
    assert d['hardware']['smt_requested'] is True


def test_tuned_route_passes_disjoint_affinity_groups_to_worker_initializer(tmp_path):
    from wu088_hh.autotune import host_profile_key
    from wu088_hh.hardware import inspect_host
    folder=tmp_path/'state';folder.mkdir()
    legacy=tmp_path/'fake_tuned_legacy.py'
    legacy.write_text('''from pathlib import Path\nimport hashlib,json,os,time\nimport numpy as np\nROOT=Path(os.environ["FAKE_ROOT"]);MIXED=ROOT\nsha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()\ndef provider_gate(): return {"status":"TEST_FIXTURE"}\ndef folder_for(*args):return ROOT\nclass Hybrid12: identity={}\ndef configuration(*args):return {},np.ones(1),np.ones(1),np.ones(1),np.ones(1),1.\ndef build_identity_for_orchestrator(*args):return {"driver":"a"*64,"model_sha256":"b"*64}\ndef init(*args): raise AssertionError("untuned init must not be used")\ndef tuned_init(n,g,z,scale,groups,counter,lock,barrier):\n with lock:\n  idx=counter.value;counter.value+=1\n cpus=set(groups[idx]);os.sched_setaffinity(0,cpus)\n p=ROOT/"affinity.log";fd=os.open(p,os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o644);os.write(fd,((",".join(map(str,sorted(cpus))))+"\\n").encode());os.close(fd)\n barrier.wait()\ndef pair(task):\n ia,ib,path=task;time.sleep(.01);np.savez(path,ia=ia,ib=ib,value=100*ia+ib)\n return dict(ia=ia,ib=ib,sha256=sha(path),wall_seconds=.01,cpu_seconds=.001)\ndef assemble(*args):raise AssertionError("not complete")\n''')
    cost=dict(schema='WU088_PAIR_COST_PROFILE_V1',scientific_driver_sha256='a'*64,model_sha256='b'*64,g=80,gamma_scale='unit',
              states=[dict(n=160,z=16,costs=[[i,j,(i+1)*(j+1)] for i in range(12) for j in range(12)])])
    cp=tmp_path/'cost.json';cp.write_text(json.dumps(cost))
    hw=inspect_host(use_smt=True);budget=hw['effective_cpu_budget'];threads=2 if budget>=4 else 1;processes=2 if budget>=4 else 1;build='test-build'
    profile={'schema':'WU088_HOST_TUNING_PROFILE_V1','host_build_key':host_profile_key(hw,build),'source_report_sha256':'c'*64,
             'selected':{'processes':processes,'kernel_threads':threads,'use_smt':True,'repetitions':3,'median_wall_s':1.,'fastest_median_wall_s':1.,'median_pair_cpu_s':1.,'cross_l3_workers':0,'selection_reason':'TEST','locality_tie_fraction':.02},
             'numerical_contract':'EXACT_ARRAY_EQUALITY_REQUIRED_FOR_ALL_SELECTED_SAMPLES','promotion_scope':'HOST_TUNING_ONLY__NATIVE_PROVIDER_NOT_AUTOMATICALLY_PROMOTED'}
    pp=tmp_path/'tuning.json';pp.write_text(json.dumps(profile))
    env=dict(os.environ,FAKE_ROOT=str(folder),WU088_R31M_BUILD_KEY=build)
    cmd=[sys.executable,str(ROOT/'scripts/wide_hybrid_orchestrator_cost.py'),'--n','160','--z','16','--max-new-pairs','4','--execution-lane','local',
         '--legacy-runner',str(legacy),'--cost-profile',str(cp),'--tuning-profile',str(pp)]
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    groups=[tuple(map(int,x.split(','))) for x in (folder/'affinity.log').read_text().splitlines()]
    assert len(groups)==processes
    assert len({c for g in groups for c in g})==sum(map(len,groups))
    assert all(len(g)==threads for g in groups)
