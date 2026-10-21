from pathlib import Path
import shutil,json,hashlib,sys,importlib.util,os
import run_borrowed as r
T=r.T;O=r.O;P=T/'patch_files';F=T/'delivery_source';F.mkdir();old=Path('/workspace/scratch/6af5e9e6c737/resume_20261020/restored_c10/REI_LRS_V14_VIGILODE_C10_20261019T141050Z/repo_payload/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019');inputroot=old.parents[1]
for name in ['VIGILODE_PIN.json','VIGILODE_SOURCE_MANIFEST.json','BASE_NATIVE_MANIFEST.json','Cargo.toml','Cargo.lock']:
 shutil.copy2(old/name,F/name)
shutil.copytree(r.W/'adapter/src',F/'src');shutil.copytree(r.W/'adapter/tests',F/'tests');shutil.copy2(P/'prepare_and_run.py',F/'prepare_and_run.py');(F/'native_additions').mkdir();shutil.copy2(P/'native_additions/axbi_native_rhs.rs',F/'native_additions/axbi_native_rhs.rs');shutil.copy2(old/'native_additions/transport_hook.txt',F/'native_additions/transport_hook.txt')
# Exact existing hook is immutable and already exports NativeCellCache.
shutil.copy2(O/'patch_files/native_additions/transport_hook.txt',F/'native_additions/transport_hook.txt')
R=T/'fresh_restored'
r.run('fresh_prepare_only',[sys.executable,F/'prepare_and_run.py','--input-root',inputroot,'--ssprk-restore',inputroot/'v14/time_centered_ssprk2_20261019/restore_ssprk2_native.py','--output-root',R,'--vigilode-source',r.W/'vigilode','--offline','--prepare-only'],90)
checks={};bad=[]
for label,base,got in [('native',r.W/'native_owner/rust/rei_microphysics',R/'native_owner/rust/rei_microphysics'),('adapter',r.W/'adapter',R/'adapter'),('vigilode',r.W/'vigilode',R/'vigilode')]:
 files=[p for p in base.rglob('*') if p.is_file() and not any(x in ['__pycache__','target'] for x in p.relative_to(base).parts)]
 checks[label]={str(p.relative_to(base)):r.sha(p)==r.sha(got/p.relative_to(base)) for p in files}
 bad += [label+'/'+k for k,v in checks[label].items() if not v]
assert not bad,bad
# Forbidden source surfaces remain unchanged, checked against frozen byte identities.
manifest=json.loads((old/'BASE_NATIVE_MANIFEST.json').read_text());hook=(F/'native_additions/transport_hook.txt').read_bytes();unchanged=[]
for name,sha in manifest.items():
 b=(r.W/'native_owner/rust/rei_microphysics'/name).read_bytes()
 if name=='src/axbi_covariant_transport.rs':b=b[:-len(hook)]
 assert hashlib.sha256(b).hexdigest()==sha,name
 unchanged.append(name)
assert (T.parent/'immutable_baseline/axbi_covariant_transport.rs').read_bytes()==(r.W/'native_owner/rust/rei_microphysics/src/axbi_covariant_transport.rs').read_bytes()
for name in ['Cargo.toml','Cargo.lock']:assert (T.parent/'immutable_baseline/adapter'/name).read_bytes()==(r.W/'adapter'/name).read_bytes()
result={'all_restored_sources_equal_compiled_source':True,'counts':{k:len(v) for k,v in checks.items()},'native_baseline_original_files_unchanged':len(unchanged),'hook_and_native_parent_unchanged':True,'vigilode_files_unchanged':len(checks['vigilode']),'Cargo_toml_lock_unchanged':True,'files':checks,'candidate_sha256':r.sha(r.BIN),'prepare_receipt':json.loads((R/'evidence/PREPARE_RECEIPT.json').read_text())};(r.E/'SOURCE_DELIVERY_EQUALITY.json').write_text(json.dumps(result,indent=2))
assert (T/'patch_files/prepare_and_run.py').read_bytes()==(T.parent/'patch_files/prepare_and_run.py').read_bytes()
(r.E/'PYTHON_RUNNER_REUSE.json').write_text(json.dumps({'source_unchanged':True,'four_passed_tests_receipt':str(T.parent/'evidence/python_runner_regression/outcome.json')},indent=2))
spec=importlib.util.spec_from_file_location('new_runner',F/'prepare_and_run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);os.sched_setaffinity(0,{0});code=m.run_cases(T/'forwarding_smoke',[r.BIN],[('fixed','radau','2')],total_budget_s=40,case_timeout_s=40,case_args=('--native-eval','cell-borrowed'))
raw=json.loads((T/'forwarding_smoke/fixed_radau_n2/raw.json').read_text());ref=json.loads((O/'experiments/matrix_fixed_radau_2/raw.json').read_text());r.check(ref,raw,'forwarding_smoke');assert raw['native_evaluation']['mode']=='CellBorrowed';assert code==0
(r.E/'FORWARDING_RESULT.json').write_text(json.dumps({'exit':code,'mode':raw['native_evaluation']['mode'],'raw':str(T/'forwarding_smoke/fixed_radau_n2/raw.json'),'all_physical_and_original_work_equal':True},indent=2))
# Optional single attribution pair; not included in profile-off timing samples.
profile=[]
for variant in ['cell-cache','cell-borrowed']:
 raw=r.case('profile_'+variant,'fixed','radau',16,variant,True);r.check(json.loads((O/'experiments/matrix_fixed_radau_16/raw.json').read_text()),raw,'profile_'+variant);profile.append({'mode':variant,'wall_s':raw['wall_s'],'profile':raw['native_evaluation']['profile']})
(r.E/'PROFILE_ATTRIBUTION.json').write_text(json.dumps(profile,indent=2));print(json.dumps(profile,indent=2));print('Delivery source, frozen identities, forwarding and optional single profile pair complete')
