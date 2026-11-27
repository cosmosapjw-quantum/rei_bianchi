"""R1 non-science orchestration. No run/worker/consume/dispatch entry points."""
from pathlib import Path
import sys,json,os,subprocess,shutil,traceback
from bootstrap import R,E,OLD,sha,write,run
from observe import observation
from proposal import seal_proposal
REPO=OLD/'w3/recovered/repo';L=REPO/'research/r31ao_unequal_ladder';NODE=L/'w3_coverage_contract_20261002_v1'
sys.path.insert(0,str(NODE));import runtime_adapter as a
c=a.c
import bootstrap
E=R/'evidence/gate_v3';E.mkdir(exist_ok=False);bootstrap.E=E
OUT=R/'backend';HOST=OLD/'runtime_work/host';PILOT=OLD/'runtime_work/pilot';WORKER=R/'worker'
PREP='0e06c0f959684e808f1ef1f6d8465e00079e0b6401eba311b804e458bac0f3a0'
def ref(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def registry_check(scope):
 hits=[]
 for base in (OLD,Path('/root/WU088_HH')):
  for folder,dirs,files in os.walk(base,followlinks=False):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__')]
   if Path(folder).name=='run_registry' and scope+'.json' in files:hits.append(str(Path(folder)/(scope+'.json')))
 forbidden=[PILOT/'RUN_STARTED.json',PILOT/'EXECUTION_BINDING.json',PILOT/'RETURN.json']
 hits += [str(p) for p in forbidden if p.exists()]
 if hits:raise ValueError('existing scope consumption: '+str(hits))
 return dict(exact_scope_registry_hits=hits,scope_consumed=False,pilot_raw_files=[str(p) for p in (PILOT/'raw').rglob('*') if p.is_file()])

def main():
 inside=observation();write('UID_CAPABILITY_OBSERVATION.json',inside)
 assert all('0000000000000000' in next(x for x in inside['status'].splitlines() if x.startswith(k+':')) for k in ('CapPrm','CapEff','CapBnd','CapAmb'))
 assert 'NoNewPrivs:\t1' in inside['status']
 admission=a.resources();p=a.load_prepared(PILOT,PREP);reg=registry_check(p['scope']['scope_sha256']);assert not reg['pilot_raw_files']
 host=a.host(REPO,HOST);probe=a.probe_host(host)
 with (E/'launcher_child.stdout.log').open('xb') as so,(E/'launcher_child.stderr.log').open('xb') as se:
  child=host._launch(['/usr/bin/python3','-B',str(R/'observe.py'),'child'],stdout=so,stderr=se,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},memory_mib=128,cpu_seconds=5,nofork=True)
  rc=child.wait(timeout=10)
 assert rc==0
 co=json.loads((E/'launcher_child.stdout.log').read_text());assert co['membership']==inside['membership'] and co['namespace']==inside['namespace']
 assert co['ancestors'][0]['memory.max']=='34359738368\n' and co['ancestors'][0]['cpu.max']=='400000 100000\n'
 write('HOST_PROBE.json',dict(probe=probe,child=co,exit_status=rc,HH_dispatch=0))
 outside=json.loads((R/'evidence/HOST_CGROUP_ANCESTORS_v3.json').read_text())
 assert outside['ppid']==inside['pid'];assert outside['namespace']['mnt']!=inside['namespace']['mnt']
 write('CGROUP_BINDING.json',dict(status='REAL_KERNEL_PATH_AND_MEMBERSHIP_VERIFIED',original_adapter_unmodified=True,resource_admission=admission,host_ancestors=ref(R/'evidence/HOST_CGROUP_ANCESTORS_v3.json'),inside_observation=ref(E/'UID_CAPABILITY_OBSERVATION.json'),launcher_child=ref(E/'launcher_child.stdout.log'),memory_limit_is_reservation=False,private_readonly_cgroup2_mount=True,host_global_mount_changed=False,limitations=['UID remains 0 in initial user namespace; capabilities zero and NoNewPrivs=1','No exhaustive cgroup escape or lifecycle-race proof','Namespace/PID/usage identities must be reobserved immediately before any future authorized run']))
 fast=c.module(L/'ncp64_acceleration_20261001_v1/backend_build/build_fast.py','r1_pinned_fast')
 prior,gate,hp=fast.modules();pre=prior.preflight(REPO/'backend_sources',OUT)
 makeinfo=R/'tooling/bin/makeinfo';pre['tools']['makeinfo']=str(makeinfo);pre['tool_identities']['makeinfo']=ref(makeinfo)
 pre['additional_toolchain_identity']={'wrapper':ref(makeinfo),'real_texi2any':ref(R/'tooling/local/usr/bin/texi2any'),'packages':ref(R/'evidence/TEXINFO_PACKAGES.json'),'orchestration':ref(Path(__file__))}
 rp=hp.plan(hp.detect());cfg=fast.configuration(prior,rp,2)
 env=prior.clean_environment(OUT,OUT/'prefix',pre['tools'],cfg)
 assert shutil.which('makeinfo',path=env['PATH'])==str(makeinfo)
 # Exact clean_environment, not ambient shell PATH. Temporary directories are workspace-local smoke data only.
 for name in ('smoke-home','smoke-tmp'):(R/'tooling'/name).mkdir()
 for label,argv in [('clean_makeinfo_version',['makeinfo','--version']),('clean_makeinfo_conversion',['makeinfo','-o',str(R/'tooling/clean.info'),str(R/'tooling/smoke.texi')])]:
  with (E/(label+'.stdout.log')).open('xb') as so,(E/(label+'.stderr.log')).open('xb') as se:
   cp=subprocess.run(argv,env=env,stdout=so,stderr=se,timeout=30)
  assert cp.returncode==0,label
 assert (R/'tooling/clean.info').stat().st_size>0
 version=(E/'clean_makeinfo_version.stdout.log').read_text();assert 'GNU texinfo' in version and '7.1' in version
 write('TOOLCHAIN_READINESS.json',dict(status='GENUINE_MAKEINFO_IN_ACTUAL_CLEAN_PATH_VERIFIED',identity=pre['additional_toolchain_identity'],version=version,clean_environment=env,makeinfo_resolved=str(makeinfo),smoke_input=ref(R/'tooling/smoke.texi'),smoke_output=ref(R/'tooling/clean.info'),exit_statuses=[0,0],global_install=False))
 plan=dict(schema='WU088_NONSCIENCE_BACKEND_CONTINUATION_PLAN_R1',preflight=pre,resource_plan=rp,configuration=cfg,steps=fast.steps(prior,OUT,pre['tools'],cfg),resource_admission=admission,old_failed_tree=str(OLD/'runtime_work/backend'),attempts=1,no_auto_retry=True,science_dispatch_count=0,source_bound_modules={**fast.PINS,'build_fast.py':sha(Path(fast.__file__))},orchestration=ref(Path(__file__)),makeinfo=pre['additional_toolchain_identity'],flint_check_scope='Selected arb acb acb_hypgeom acb_calc modules; not full upstream suite')
 write('CONTINUATION_PLAN.json',plan)
 write('BUILD_ATTEMPT.json',dict(plan=ref(E/'CONTINUATION_PLAN.json'),attempt=1,science_dispatch_count=0))
 result=fast.execute(prior,gate,pre,rp,cfg);write('BACKEND_RESULT.json',result)
 supplements=[]
 for stage in sorted((OUT/'logs').glob('*/STAGE.json')):
  supplements.append(dict(stage=ref(stage),makeinfo=pre['additional_toolchain_identity'],actual_clean_PATH=env['PATH']))
 write('BUILD_ORCHESTRATION_PROVENANCE.json',dict(original_backend_provenance=ref(OUT/'BACKEND_BUILD_PROVENANCE.json'),toolchain=ref(E/'TOOLCHAIN_READINESS.json'),stage_identity_supplements=supplements,original_stage_receipts_unmodified=True,pipeline_identity_is_new=True))
 d=a.driver(REPO);m=d.build(Path(p['input_npz']),OUT/'prefix',OUT/'BACKEND_BUILD_PROVENANCE.json',WORKER,callback_mode='cached')
 verified=a.validate_build(REPO,WORKER,m['manifest_sha256']);write('WORKER_ABI_VERIFICATION.json',dict(status='COMPILE_LINK_SOURCE_AND_PINNED_BACKEND_ABI_VERIFIED',manifest=ref(WORKER/'BUILD.json'),manifest_sha256=m['manifest_sha256'],linkage=verified['linkage'],primitive_executed=False))
 reg=registry_check(p['scope']['scope_sha256'])
 proposal=seal_proposal(dict(verified=True,scope_consumed=False,prepared_sha256=PREP,prepared_file=ref(PILOT/'PREPARED.json'),scope_sha256=p['scope']['scope_sha256'],local_plans=p['local_plans'],prepared_payloads=p['files'],runtime_code_identity=a.code_identity(),source=m['source'],input_npz=ref(Path(p['input_npz'])),build_dir=str(WORKER),build_sha256=m['manifest_sha256'],build_file=ref(WORKER/'BUILD.json'),backend_provenance=ref(OUT/'BACKEND_BUILD_PROVENANCE.json'),orchestration_provenance=ref(E/'BUILD_ORCHESTRATION_PROVENANCE.json'),host_build_dir=str(HOST),host_identity=host.identity(),synthetic_probe=probe,resource_admission=admission,cgroup_binding=ref(E/'CGROUP_BINDING.json'),execution_identity=ref(E/'UID_CAPABILITY_OBSERVATION.json'),limits=c.LIMITS,registry=reg,current_execution_command=['systemd-run','--user','--unit=wu088-prep-r1-build','--wait','--pipe','--property=MemoryMax=34359738368','--property=CPUQuota=400%',str(R/'namespace_entry.sh')],future_run_requirement='Separate exact human authorization and immediate identity/resource/registry revalidation. Original run is not invoked by this helper.',not_issued_execution_command=dict(adapter=str(NODE/'runtime_adapter.py'),action='run',root=str(PILOT),expected=PREP,build=str(WORKER),build_sha=m['manifest_sha256'],host_build=str(HOST)),**c.CLAIMS))
 write('BINDING_PROPOSAL.json',proposal)
 write('PIPELINE_RESULT.json',dict(status='READY_FOR_EXACT_SCIENCE_AUTHORIZATION',proposal_sha256=proposal['proposal_sha256'],proposal_file=ref(E/'BINDING_PROPOSAL.json'),science_dispatch_count=0,scope_consumed=False))
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  traceback.print_exc()
  write('PIPELINE_RESULT.json',dict(status='PREPARATION_BLOCKED',error=str(exc),error_type=type(exc).__name__,science_dispatch_count=0,scope_consumed=False,auto_retry=False))
  raise
