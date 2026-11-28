#!/usr/bin/env python3
"""Pre-register and run the independent frozen-data audit once per run id."""
import datetime,hashlib,json,os,pathlib,platform,resource,subprocess,sys,time
home=pathlib.Path(__file__).resolve().parent
run_name=sys.argv[1] if len(sys.argv)>1 else 'run01'
folder=home/run_name;folder.mkdir(exist_ok=False)
code=home/'independent_fraction_review.py';snapshot=folder/'EXECUTED_CODE.py'
snapshot.write_bytes(code.read_bytes())
base=home.parent/'phys18';p19=base/'HH_PHYS19_THEORY_20261013_v1'
files=[code,snapshot,home/'record_and_run.py',home.parent/'phys19_derivation/PURE_CURVATURE_INDEPENDENT_DERIVATION_KO.md',
    p19/'contracts/ADOPTED_CURVATURE_CONTRACT.json',p19/'src/curvature_application.py',p19/'src/curvature_geometry.py',
    p19/'checks/application/run01/results/CURVATURE_RESULTS.json',p19/'checks/application/run01/results/SUMMARY.json',
    p19/'checks/application/readout02/results/CURVATURE_GEOMETRY.json']
def identity(p):
    data=p.read_bytes();return {'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
command=[sys.executable,'-B',str(snapshot),'--base',str(base),'--output',str(folder/'results')]
pre={'schema':'PHYS19_INDEPENDENT_AUDIT_PRE_RUN_V1','recorded_before_execution':True,
    'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,
    'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
        'implementation':platform.python_implementation(),'cwd':str(home)},
    'budget':{'wall_seconds':60,'cpu_soft_seconds':52,'cpu_hard_seconds':56,'address_space_bytes':1610612736,
        'scientific_runs':1,'source_calls':0,'root_solves':0,'history_replays':0},
    'input_identities':[identity(p) for p in files],
    'constraints':'Independent exact Fraction calculations on saved enclosures only; no producer import or callback, root solve, history, or previous suite replay.'}
(folder/'PRE_RUN.json').write_text(json.dumps(pre,indent=2)+'\n')
def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(52,56));resource.setrlimit(resource.RLIMIT_AS,(1610612736,1610612736))
t=time.perf_counter();result={'status':'running'}
with (folder/'STDOUT.log').open('w') as stdout,(folder/'STDERR.log').open('w') as stderr:
    try:
        process=subprocess.run(command,stdout=stdout,stderr=stderr,cwd=home,timeout=60,preexec_fn=limits)
        result.update({'exit_code':process.returncode,'status':'completed' if process.returncode==0 else 'failed'})
    except subprocess.TimeoutExpired:
        result.update({'status':'budget_timeout','exit_code':None})
result.update({'schema':'PHYS19_INDEPENDENT_AUDIT_RUN_V1','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'elapsed_wall_seconds':time.perf_counter()-t,'pre_run_sha256':identity(folder/'PRE_RUN.json')['sha256'],
    'executed_code_sha256':identity(snapshot)['sha256'],
    'stdout':identity(folder/'STDOUT.log'),'stderr':identity(folder/'STDERR.log'),
    'source_calls':0,'root_solves':0,'history_replays':0})
artifact=folder/'results/INDEPENDENT_FRACTION_AUDIT.json'
if artifact.exists():result['result']=identity(artifact)
(folder/'RUN.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if result['status']!='completed':print((folder/'STDERR.log').read_text()[-5000:])
