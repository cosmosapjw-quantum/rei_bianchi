"""R2 fixed non-science preparation only. No adapter run/worker/consume calls."""
from pathlib import Path
import sys,json,os,subprocess,traceback,time
from support import R,E,OLD,REPO,L,REVIEW,sha,ref,write,run
from cheap_gates import a,c,fast,prior,gate,hp,extract,make_environment
from backend_r2 import execute_r2
from observe import observation
PREP='0e06c0f959684e808f1ef1f6d8465e00079e0b6401eba311b804e458bac0f3a0';PILOT=OLD/'runtime_work/pilot';HOST=OLD/'runtime_work/host';OUT=R/'backend';WORKER=R/'worker'
def registry_check(scope):
 hits=[]
 for base in (OLD,Path('/root/WU088_HH')):
  for folder,dirs,files in os.walk(base,followlinks=False):
   dirs[:]=[d for d in dirs if d not in ('.git','__pycache__')]
   if Path(folder).name=='run_registry' and scope+'.json' in files:hits.append(str(Path(folder)/(scope+'.json')))
 markers=[str(PILOT/n) for n in ('RUN_STARTED.json','EXECUTION_BINDING.json','RETURN.json') if (PILOT/n).exists()]
 if hits or markers:raise ValueError('Consumed scope or recovery markers; no new preparation bypass')
 raw=[str(p) for p in (PILOT/'raw').rglob('*') if p.is_file()];assert not raw
 return dict(scope_consumed=False,exact_scope=scope,registry_hits=hits,run_markers=markers,pilot_raw_files=raw)
def main():
 inside=observation();write('UID_CAPABILITY_OBSERVATION.json',inside)
 assert all('0000000000000000' in next(x for x in inside['status'].splitlines() if x.startswith(k+':')) for k in ('CapPrm','CapEff','CapBnd','CapAmb'))
 assert 'NoNewPrivs:\t1' in inside['status']
 admission=a.resources();assert admission['memory_max_bytes']==34359738368 and admission['cpu_quota']==400000
 outside=json.loads((E/'HOST_CGROUP_ANCESTORS.json').read_text());assert outside['ppid']==inside['pid'] and outside['namespace']['mnt']!=inside['namespace']['mnt']
 p=a.load_prepared(PILOT,PREP);registry=registry_check(p['scope']['scope_sha256'])
 h=a.host(REPO,HOST);probe=a.probe_host(h)
 with (E/'launcher_child.stdout.log').open('xb') as so,(E/'launcher_child.stderr.log').open('xb') as se:
  child=h._launch(['/usr/bin/python3','-B',str(R/'observe.py'),'child'],stdout=so,stderr=se,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},memory_mib=128,cpu_seconds=5,nofork=True)
  rc=child.wait(timeout=10)
 assert rc==0
 co=json.loads((E/'launcher_child.stdout.log').read_text());assert co['membership']==inside['membership'] and co['namespace']==inside['namespace']
 assert co['ancestors'][0]['memory.max']=='34359738368\n' and co['ancestors'][0]['cpu.max']=='400000 100000\n'
 write('HOST_PROBE.json',dict(probe=probe,child=co,exit_status=rc,science_dispatch_count=0))
 write('CGROUP_BINDING.json',dict(status='LIVE_RESOURCE_PATH_MEMBERSHIP_AND_CHILD_VERIFIED',adapter_identity=ref(Path(a.__file__)),admission=admission,host_ancestors=ref(E/'HOST_CGROUP_ANCESTORS.json'),inside=ref(E/'UID_CAPABILITY_OBSERVATION.json'),native_child=ref(E/'launcher_child.stdout.log'),private_readonly_cgroup2_mount=True,global_mount_changed=False,limit_is_RAM_reservation=False,nonroot_UID_validation=False,capabilities_zero=True,NoNewPrivs=1,live_observed_before_backend=True,future_namespace_requires_recreation_and_revalidation=True))
 pre,rp,cfg,env=make_environment()
 expected=json.loads((OLD/'prep_r1/backend/FAST_BUILD_CONFIG.json').read_text());assert cfg==expected
 assert json.loads((E/'MPFR_DEPENDENCY_QUERY.json').read_text())['queries']==[{'target':'Makefile.in','exit_status':0},{'target':'configure','exit_status':0}]
 assert json.loads((E/'TOOLCHAIN_SAMPLE.json').read_text())['workspace_local_new_Automake_Autoconf_needed'] is False
 # Execute the generator sample once under the newly observed capabilities/namespace.
 env_smoke=env.copy();env_smoke['TMPDIR']=str(R/'backend-smoke-tmp');env_smoke['WU088_BUILD_HOME']=str(R/'backend-smoke-home')
 assert run('bound_toolchain_autoreconf',[pre['tools']['autoreconf'],'-i','-v','-Wall'],cwd=R/'toolchain_sample',timeout=180,env=env_smoke)==0
 assert run('bound_toolchain_configure',[pre['tools']['sh'],'./configure'],cwd=R/'toolchain_sample',timeout=180,env=env_smoke)==0
 toolchain=json.loads((E/'TOOLCHAIN_CLOSURE.json').read_text())
 for item in toolchain['data_files']:
  if 'sha256' in item:assert sha(Path(item['path']))==item['sha256']
 pre['r2_pipeline_identity']=dict(extractor=ref(REVIEW/'release_extract.py'),extractor_review_source_lock=ref(REVIEW/'SOURCE_LOCK.json'),candidate_payload_manifest=ref(REVIEW/'DELIVERY_MANIFEST.json'),orchestration=ref(R/'backend_r2.py'),coordinator=ref(Path(__file__)),toolchain=ref(E/'TOOLCHAIN_CLOSURE.json'),extraction_preflight=ref(E/'EXTRACTION_METADATA_FIDELITY.json'),original_modules=fast.PINS,original_fast=ref(Path(fast.__file__)),original_pipeline_unchanged=False,numeric_source_changed=False)
 plan=c.seal(dict(schema='WU088_NCP_PREP_R2_CONTINUATION_PLAN',preflight=pre,configuration=cfg,host_resource_plan=rp,resource_admission=admission,steps=fast.steps(prior,OUT,pre['tools'],cfg),clean_environment=env,source_input_prepared=ref(PILOT/'PREPARED.json'),source_INPUT=ref(Path(p['input_npz'])),scope_sha256=p['scope']['scope_sha256'],pipeline_identity=pre['r2_pipeline_identity'],live_cgroup_binding=ref(E/'CGROUP_BINDING.json'),archive_mode_policy='Original 0644/0755 normalization retained; exact archive content and recorded member mtime restored',backend_attempt_max=1,no_auto_retry=True,science_dispatch_count=0,scope_consumed=False,FLINT_check='arb acb acb_hypgeom acb_calc selected modules; not full upstream suite'), 'plan_sha256')
 write('CONTINUATION_PLAN_R2.json',plan);write('BUILD_ATTEMPT.json',dict(plan_self_sha256=plan['plan_sha256'],plan_byte_identity=ref(E/'CONTINUATION_PLAN_R2.json'),attempt=1,science_dispatch_count=0))
 result=execute_r2(prior,gate,pre,rp,cfg,extract);write('BACKEND_RESULT.json',result)
 backend=gate.verify_backend(OUT/'BACKEND_BUILD_PROVENANCE.json',OUT/'prefix')
 write('BACKEND_PROVENANCE_SUPPLEMENT.json',dict(status='NEW_EXTRACTION_ORCHESTRATION_IDENTITY_EXPLICIT__BYTE_CHAIN_VERIFIED',pipeline=pre['r2_pipeline_identity'],backend_provenance=ref(OUT/'BACKEND_BUILD_PROVENANCE.json'),backend_verification=backend['verification'],actual_extraction=ref(OUT/'EXTRACTION_METADATA_FIDELITY.json'),plan=ref(E/'CONTINUATION_PLAN_R2.json'),resource_enclosure=ref(E/'CGROUP_BINDING.json'),independent_science_review=False,scientific_admission=False))
 d=a.driver(REPO);m=d.build(Path(p['input_npz']),OUT/'prefix',OUT/'BACKEND_BUILD_PROVENANCE.json',WORKER,callback_mode='cached')
 verified=a.validate_build(REPO,WORKER,m['manifest_sha256']);write('WORKER_ABI_VERIFICATION.json',dict(status='COMPILE_LINK_SOURCE_INPUT_AND_PINNED_BACKEND_ABI_VERIFIED',build=ref(WORKER/'BUILD.json'),build_self_sha256=m['manifest_sha256'],linkage=verified['linkage'],primitive_executed=False))
 registry=registry_check(p['scope']['scope_sha256'])
 sealing=c.module(OLD/'prep_r1/proposal.py','r2_inherited_proposal_seal')
 proposal=sealing.seal_proposal(dict(verified=True,scope_consumed=False,prepared_sha256=PREP,prepared_file=ref(PILOT/'PREPARED.json'),scope_sha256=p['scope']['scope_sha256'],local_plans=p['local_plans'],prepared_payloads=p['files'],runtime_code_identity=a.code_identity(),native_source=m['source'],input_npz=ref(Path(p['input_npz'])),build_dir=str(WORKER),build_sha256=m['manifest_sha256'],build_file=ref(WORKER/'BUILD.json'),backend_provenance=ref(OUT/'BACKEND_BUILD_PROVENANCE.json'),backend_supplement=ref(E/'BACKEND_PROVENANCE_SUPPLEMENT.json'),pipeline_identity=pre['r2_pipeline_identity'],host_build_dir=str(HOST),host_identity=h.identity(),synthetic_probe=probe,resource_admission=admission,cgroup_binding=ref(E/'CGROUP_BINDING.json'),execution_identity=ref(E/'UID_CAPABILITY_OBSERVATION.json'),limits=c.LIMITS,registry=registry,actual_preparation_command=['systemd-run','--user','--unit=wu088-prep-r2','--wait','--pipe','--property=MemoryMax=34359738368','--property=CPUQuota=400%',str(R/'namespace_entry.sh')],future_execution_path=dict(adapter=str(Path(a.__file__)),action='run',root=str(PILOT),expected=PREP,build=str(WORKER),build_sha=m['manifest_sha256'],host_build=str(HOST),namespace_setup='Same private remount and capability/no-new-privileges policy; recreate/reobserve task before exact authorization/run'),future_conditions=['Separate human exact science authorization covering this proposal/source/input/build/plan/runtime','Fresh PID/namespace/cgroup membership/ancestor/usage observations and comparison of static identities and resource policy','Original one-shot registry checked and preserved; original runtime_adapter run only'],**c.CLAIMS))
 write('BINDING_PROPOSAL.json',proposal)
 write('PIPELINE_RESULT.json',dict(status='READY_FOR_EXACT_SCIENCE_AUTHORIZATION',proposal_self_sha256=proposal['proposal_sha256'],proposal_byte_identity=ref(E/'BINDING_PROPOSAL.json'),science_dispatch_count=0,scope_consumed=False,backend_attempts=1))
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  traceback.print_exc()
  write('PIPELINE_RESULT.json',dict(status='PREPARATION_BLOCKED',domain='METADATA_TOOLCHAIN_OR_RUNTIME_PREPARATION',error=str(exc),error_type=type(exc).__name__,science_dispatch_count=0,scope_consumed=False,backend_attempts=1 if (E/'BUILD_ATTEMPT.json').exists() else 0,auto_retry=False))
  raise
