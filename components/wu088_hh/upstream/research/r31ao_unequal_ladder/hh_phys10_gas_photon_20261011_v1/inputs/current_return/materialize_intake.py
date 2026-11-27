from pathlib import Path
import json, hashlib, datetime

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parents[1]
def readj(p): return json.loads(p.read_text())
def h(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def writej(p,o):
    with p.open('x',encoding='utf-8') as f: json.dump(o,f,indent=2,ensure_ascii=False); f.write('\n')
payload=readj(ROOT/'FETCHED_TEXT_PAYLOAD.json')
extra=readj(ROOT/'FETCHED_EXTRA_PAYLOAD.json')
manifest=[]
for entry in payload['files']+extra['files']:
    b=entry['content'].encode('utf-8')
    assert len(b)==entry['size'],(entry['key'],len(b),entry['size'])
    assert blob(b)==entry['sha'],(entry['key'],blob(b),entry['sha'])
    dst=ROOT/'files'/entry['key']
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('xb') as f: f.write(b)
    manifest.append({'path':str(dst.relative_to(ROOT)),'repository_path':('/'.join(x for x in ['research/r31ao_unequal_ladder' if entry['prefix'] else '',entry['prefix'],entry['path']] if x)),'ref':entry['ref'],'url':entry['url'],'bytes':len(b),'git_blob_sha':blob(b),'sha256':h(b),'git_blob_and_size_verified':True})

reuse=[]
for lane,runpath,pack in [('PHYS09','files/ncp09/NCP_RUN.json','HH_PHYS09_20261011_v1'),('PHYS08','files/ncp08/hh_phys08_weighted_first/NCP_RUN.json','HH_PHYS08_20261011_v1')]:
    run=readj(ROOT/runpath)
    before,after=run['source_inputs_before'],run['source_inputs_after']
    assert before==after and run['source_inputs_unchanged'] is True
    for item in before:
        relative=item.get('relative_path') or item['path'].split('/'+pack+'/',1)[1]
        p=WORK/pack/relative
        b=p.read_bytes()
        assert len(b)==item['bytes'] and h(b)==item['sha256'],str(p)
        reuse.append({'lane':lane,'local_path':str(p),'relative_path':relative,'bytes':len(b),'sha256':h(b),'remote_run_path':runpath,'matches_before_after':True})

n09=readj(ROOT/'files/ncp09/NCP_RETURN.json')
review=readj(ROOT/'files/ncp09/review/DECISION.json')
oracle=readj(ROOT/'files/ncp09/ORACLE_CHECK.json')
runtime=readj(ROOT/'files/ncp09/REUSE_EXECUTION_SUMMARY.json')
archive=WORK/'PHYS09_delivery_20261011/WU088_HH_PHYS09_PROJECTED_ENERGY_NCP_HANDOFF_20261011_v1_sha_810192192496.zip'
archive_bytes=archive.read_bytes()
assert len(archive_bytes)==1718264 and h(archive_bytes)==n09['source_archive_sha256']
coremanifest=WORK/'HH_PHYS09_20261011_v1/MANIFEST.json'
assert h(coremanifest.read_bytes())==n09['core_manifest_sha256']
summary={
 'schema':'WU088_HH_PHYS10_CURRENT_RETURN_INTAKE_V1',
 'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'NCP08_AND_NCP09_COMPLETE_RETURN_OBSERVED_REUSABLE',
 'repository':'cosmosapjw-quantum/WU088_HH',
 'research09':{'commit':'2367504729026abc0d43eaba28703592e885dea4','tree':'a2338634a0af42b25d85ed9a93d1098930867397','core_commit':'3e409503c40a7899033126a458b1cb06b227978a','core_tree':'afdef4725df9fdb084038d291343ac371ef96196','PR':40},
 'ncp08':{'commit':'5288fd50148755f5ed37391e3dcb612d8d51f130','tree':'e623ce7410b79741a4b43d1e5f5bb9b8cd07458c','return_subtree':'c16c63e8d10b23eafc1817807523219aad9262cf','PR':41,'decision':'PASS_SCOPED_T07','input_bindings_reused':10,'minsubnormal_signed':'UNRESOLVED_PRESERVED'},
 'ncp09':{'commit':'e6a72c3df5803b5b23f9a38918dad6a1eba7e1f7','tree':'6bf0e678f4e98787ffbe6b6f5ef9a3ce2d7abd94','return_core_commit':'4b815f00579b9d70f21fa7a30f82f1dd9796741e','return_subtree':'8848dd72bf8483b65d1e52c5aaca734468445542','delivery_subtree':'48230738f516fce52b39159d20c9133d61cd05be','PR':42,'decision':review['decision'],'input_bindings_reused':13,'original_compiler':'rustc 1.94.1','original_execution_records':runtime['records'],'saved_result':review['independent_verification']['exact_saved_interval_comparison'],'native_authority':False,'actual_native':n09['actual_native']},
 'recent_PR_scope':extra['summary'],
 'read_only_intake':{'new_science_runs':0,'new_compiler_runs':0,'new_gate_runs':0,'new_oracle_consumer_runs':0,'remote_mutations':0,'fetched_text_files':len(manifest),'git_sha_size_matches':len(manifest),'local_source_bindings_reused':len(reuse),'binary_downloaded':False,'whole_archive_redownloaded':False,'new_independent_review':False},
 'source_identity':{'archive_bytes':len(archive_bytes),'archive_sha256':h(archive_bytes),'manifest_sha256':h(coremanifest.read_bytes())},
 'limits':['Return independent review and exact-output checks are reused; this intake did not rerun them.','Original compiler proxy hash does not attest underlying rustc payload.','Original execution host affinity 0..23, CPU model not recorded; no 64-core speed or scaling measurement.','Prior review transport failure is preserved separately from exit-zero scientific processes.','Remote restore is a claim in the fetched NCP delivery receipt; no new remote restore here.'],
 'routing_observation':'Observed PHYS08 and PHYS09 executions took seconds or less and are already complete; no repeat NCP queue is justified. Current user directs lightweight execution here and only measured genuinely heavy parallel work to NCP.',
 'current_AGENTS':'files/repo/AGENTS.md',
 'harness':{'host_label':'GPT-6 Astra Pro','router_status':'MODEL_UNRESOLVED_PRO_ALIAS_ABSENT','model_independent_work_selection':'existing verified Astra v4','model_switch':False},
 'scientific_open':['carried second_half','full/two-half paired defect','time/continuum remainder','full49/production','PHYS07 reference energy','NCP07 node32 per-node predicate']
}
writej(ROOT/'FETCHED_FILE_IDENTITY_MANIFEST.json',{'schema':'PHYS10_GIT_TEXT_IDENTITY_V1','files':manifest})
writej(ROOT/'LOCAL_REUSE_MANIFEST.json',{'schema':'PHYS10_LOCAL_REUSE_V1','files':reuse})
writej(ROOT/'SOURCE_INTAKE_SUMMARY.json',summary)
print(json.dumps({'status':summary['status'],'fetched_files':len(manifest),'local_reused':len(reuse),'manifest':str(ROOT/'FETCHED_FILE_IDENTITY_MANIFEST.json'),'summary':str(ROOT/'SOURCE_INTAKE_SUMMARY.json')},ensure_ascii=False))
