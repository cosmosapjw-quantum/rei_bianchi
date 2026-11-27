#!/usr/bin/env python3
"""One bounded evaluator invocation with an immutable pre-run and real accounting."""
import datetime,hashlib,json,pathlib,resource,subprocess,sys,time
root=pathlib.Path(__file__).resolve().parents[2]
parent=root.parent/'HH_PHYS15_THEORY_20261012_v1'
code=root/'src/application/correlated_endpoint_application.py'
run_name=sys.argv[1] if len(sys.argv)>1 else 'run01'
folder=root/'checks/application'/run_name
folder.mkdir(exist_ok=False)
cmd=[sys.executable,str(code),'--parent',str(parent),'--output',str(folder/'results')]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
pre={'schema':'WU088_HH_PHYS16_APPLICATION_PRE_RUN_V1','started_utc':start,'command':cmd,
 'code_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
 'scientific_question':'Uniform same-COMMON factored residual and finite endpoint/observable inclusion using inherited source/root certificates.',
 'planned_measurements':['r','g2-g1','componentwise d','finite DeltaT/e/w/ne','sector temperatures','kwHe cooling-cone bound','actual photon secant and guards'],
 'expected_budget':{'wall_seconds':30,'memory_MiB':256,'new_root_solves':0,'source_kernel_invocations':0,'history_replays':0},
 'arithmetic':'unchanged PHYS14 exact rational/directed 256-bit dyadic interval helper; exact 4x4 majorant solve',
 'acceptance':['one linked COMMON/rho,b,lambda graph before outward arithmetic','original C,B,q,S paired','positive denominators and internal source hull','all 35 photon/guard components','candidate run only pending independent scientific review']}
(folder/'PRE_RUN.json').write_text(json.dumps(pre,indent=2)+'\n')
t=time.perf_counter();a=resource.getrusage(resource.RUSAGE_CHILDREN)
with (folder/'stdout.txt').open('w') as so,(folder/'stderr.txt').open('w') as se:
 p=subprocess.run(cmd,stdout=so,stderr=se,timeout=30)
b=resource.getrusage(resource.RUSAGE_CHILDREN)
record={'schema':'WU088_HH_PHYS16_APPLICATION_RUN_RECORD_V1','started_utc':start,
 'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'exit_code':p.returncode,
 'wall_seconds':time.perf_counter()-t,'user_cpu_seconds':b.ru_utime-a.ru_utime,'system_cpu_seconds':b.ru_stime-a.ru_stime,
 'peak_RSS_KiB':b.ru_maxrss,'code_sha256':pre['code_sha256'],
 'classification':'completed bounded interval application' if p.returncode==0 else 'implementation/runtime failure; see stderr',
 'new_root_solves':0,'source_kernel_invocations':0,'history_replays':0,'outputs':[]}
for f in sorted(folder.rglob('*')):
 if f.is_file():record['outputs'].append({'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(folder/'RUN_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
sys.exit(p.returncode)
