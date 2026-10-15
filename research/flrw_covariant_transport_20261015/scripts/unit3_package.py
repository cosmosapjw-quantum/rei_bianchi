from pathlib import Path
import json,hashlib,zipfile,re,datetime
W=Path('/home/cosmosapjw/REI_UNIT3_CLOSEOUT_20261015_001');S=W/'source';P=S/'research/flrw_covariant_transport_20261015'
D=Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912')
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
strict=json.loads((P/'raw/ncp003_first3_readback.json').read_text());done=strict['strict_terminal_summaries']
assert len(done)==3 and all(x['native_completion_proof'] and x['source_config_binary_bindings_match'] and x['ledger_failure_rows']==0 for x in done)
status={'status':'FIRST3_COMPLETE_TIME_AND_ANGLE_PENDING','completed':[{'case':x['case'],'zbar':x['endpoint_metrics']['zbar'],'accepted':int(x['native_return']['accepted']),'wall_s':float(x['native_return']['wall_s']),'ledger_failure_rows':x['ledger_failure_rows'],'source_config_binary_bindings_match':x['source_config_binary_bindings_match']} for x in done],'pending':['FLRW_HPC_Q512_TIME_001','FLRW_HPC_Q512_ANGLE_001'],'strict_readback':'raw/ncp003_first3_readback.json','compact_terminal':'raw/ncp003_first3_terminal','full_screen':'PENDING_ALL5_AND_INDEPENDENT_REVIEW','full_history_admission':'NOT_OPENED'}
r=json.loads((P/'HPC_RESULT.json').read_text());r['first3_terminal']=status;r['fivecase_execution']['status']=status['status'];r['fivecase_execution']['running_at_477s_is_historical_snapshot']=True;write('HPC_RESULT.json',r)
h=json.loads((P/'HANDOFF.json').read_text());h['current_pilot']=status;h['current_unit']['fivecase']=status['status'];h['status']='UNIT3_PARITY_PASS_FIRST3_COMPLETE_TIME_ANGLE_PENDING_CPU_ADEQUACY_OPEN';write('HANDOFF.json',h)
c=json.loads((P/'CODING_LOOP.json').read_text());c['hpc_prepare_pool'][9]['observed_fact']='Ownerisolatedsource/benchmark restored from verifiedarchive. First3energycases actually completez19.8 with strict source/6arrays/ledger readback. Time/angle remainpending; fullgateclosed; source004cacheexcluded.';write('CODING_LOOP.json',c)
n=json.loads((P/'NEXT_DAG.json').read_text());n['current_next_executable']='Read time/angle actual endpoints, complete5case empiricalscreen and independentreview; first3energycasescomplete. CPUadequacyOPEN;004cachetheorynotimplemented.';n['current_pilot']=status
for t in n['tasks']:
 if t.get('id')=='ACTUAL_FIVECASE_REFINEMENT':t['status']=status['status']
write('NEXT_DAG.json',n)
for name in ['README_KO.md','CODEX_HANDOFF_KO.md','PR_PLAN.md']:
 f=P/name;f.write_text(f.read_text()+'\nLatest durable terminal update: Q128/Q256/Q512 all COMPLETE_REPRESENTED_INTERVAL atz19.8; strict source/config/binarybinding,6arrays and zeroFAILledgers verified. Time/angle remainpending; no full5case screen/fullhistoryPASS. See raw/ncp003_first3_readback.json and compactterminaldirectory.\n')
# Exact source identity and source archive members, not changed documentation.
for line in (S/'SOURCE_SHA256SUMS.txt').read_text().splitlines():
 if not line.strip():continue
 digest,name=line.split(None,1);name=name.lstrip('* ').strip();assert sha((S/name).read_bytes())==digest,name
driver=S/'rust/rei_microphysics/src/axbi_driver.rs'
section=driver.read_text().split('pub fn compiled_identity() -> String {',1)[1].split('fn ledger_values',1)[0]
inputs=[(driver.parent/x).resolve() for x in re.findall(r'include_str!\(\s*"([^"]+)"',section)]
identity='\nAXBI_SOURCE_BOUNDARY\n'.join(x.read_text() for x in inputs)
assert sha(identity.encode())=='63899f056e57de9a9bcfe0e33ef0d61e73434e080f31c2838f8950025ba83529'
assert identity==(P/'raw/ncp003_benchmark001/source_identity.txt').read_text()
assert (P/'HPC_REVIEW_SUPPLEMENTAL.json').is_file()
with zipfile.ZipFile(D/'REI_FLRW_COVARIANT_UNIT2_20261015.zip') as old: baseline={n:sha(old.read(n)) for n in old.namelist() if not n.endswith('/')}
allowed={'.rs','.py','.md','.json','.jsonl','.cfg','.txt','.log','.diff','.wl','.toml','.lock','.csv','.svg','.pdf','.png'}
generated={'UNIT3_SELECTION.json','GITHUB_UNIT3_PATHS.txt','UNIT3_PACKAGE_RECEIPT.json','GITHUB_UNIT3_CHUNKS.json'}
def include(p):
 rel=p.relative_to(S)
 if any(x in rel.parts for x in ['target','__pycache__','.git']):return False
 if p.suffix not in allowed or p.name in generated:return False
 return True
files=sorted(p for p in S.rglob('*') if p.is_file() and include(p))
git=[];excluded=[]
safe_code={'rust/rei_microphysics/src/axbi_parallel.rs','rust/rei_microphysics/src/axbi_driver.rs','rust/rei_microphysics/src/axbi_covariant_transport.rs','rust/rei_microphysics/src/lib.rs','rust/rei_microphysics/tests/axbi_transport_parallel.rs','rust/rei_microphysics/examples/axbi_hpc_scaling.rs'}
for p in files:
 rel=str(p.relative_to(S));content=p.read_bytes()
 if baseline.get(rel)==sha(content):continue
 if not(rel in safe_code or rel.startswith('research/flrw_covariant_transport_20261015/')):continue
 if '/raw/ncp003_benchmark001/' in rel and p.name not in {'summary.json','benchmark_receipt.json','benchmark_binding.json','benchmark_telemetry.jsonl','build_receipt.json','benchmark.log'}:
  excluded.append({'path':rel,'reason':'Complete benchmark fixture/state/traces retained in ZIP and durable benchmarkarchive; compact Git evidence only.'});continue
 if p.name in {'source_identity.txt','checkpoint.txt'} or p.stat().st_size>4*1024**2:
  excluded.append({'path':rel,'reason':'Large exact snapshot retained in ZIP, compact receipt in Git.'});continue
 try:content.decode('utf8')
 except UnicodeDecodeError:
  excluded.append({'path':rel,'reason':'Binary retained ZIP only.'});continue
 git.append(p)
row=lambda p:{'path':str(p.relative_to(S)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
selection={'schema':'rei.covariant.unit3_owner_recovery_selection.v1','base_commit':'54dd5352672127e77970eb06f3dda027f2aee275','base_tree':'56e3a0ae24c1b109966ded5cb4559f0c9b05eb1d','status':'FINAL_SOURCE003_SCOPED_DOCS_FREEZE','compiled_identity_sha256':sha(identity.encode()),'git_publish_files':[row(p) for p in git],'zip_files':[row(p) for p in files],'excluded_from_git':excluded,'trace_exception':'Four complete4235511B tracefiles included ZIP, excluded Git.','future_source004_included':False,'missing_original_local_raw':'HPC_LOCAL_EVIDENCE_GAP.json','supplemental_review':'HPC_REVIEW_SUPPLEMENTAL.json','production_source_mutations':0,'git_mutations':0,'numerical_runs':0}
write('UNIT3_SELECTION.json',selection)
git.extend([P/'UNIT3_SELECTION.json',P/'GITHUB_UNIT3_PATHS.txt'])
(P/'GITHUB_UNIT3_PATHS.txt').write_text('\n'.join(str(p.relative_to(S)) for p in git)+'\n')
out=W/'github_payload';out.mkdir(exist_ok=True)
records=[];chunk=[];chunkbytes=0
def flush():
 global chunk,chunkbytes
 if not chunk:return
 name='tree_'+str(len(records)+1).zfill(3)+'.json';data={'tree_elements':chunk,'path_sha256':[{'path':x['path'],'sha256':sha(x['content'].encode())} for x in chunk]};payload=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n';(out/name).write_text(payload);records.append({'file':str(out/name),'bytes':len(payload.encode()),'sha256':sha(payload.encode()),'paths':[x['path'] for x in chunk]});chunk=[];chunkbytes=0
for p in git:
 entry={'path':str(p.relative_to(S)),'mode':'100644','type':'blob','content':p.read_text()};size=len(json.dumps(entry,ensure_ascii=False).encode())
 if chunk and chunkbytes+size>45000:flush()
 chunk.append(entry);chunkbytes+=size
 if chunkbytes>45000:flush()
flush()
(W/'GITHUB_UNIT3_CHUNKS.json').write_text(json.dumps({'base_commit':selection['base_commit'],'base_tree':selection['base_tree'],'chunks':records,'selected_path_sha256':[row(p) for p in git],'large_single_file_chunks_allowed':True,'Git_mutations':0},ensure_ascii=False,indent=2)+'\n')
entries={str(p.relative_to(S)):p.read_bytes() for p in files}
for p in [P/'UNIT3_SELECTION.json',P/'GITHUB_UNIT3_PATHS.txt']:entries[str(p.relative_to(S))]=p.read_bytes()
entries['README_KO.md']=(P/'UNIT3_RUN_KO.md').read_bytes()
archive=D/'REI_FLRW_COVARIANT_UNIT3_HPC_20261015.zip'
assert not archive.exists()
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for name,data in sorted(entries.items()):
  info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.external_attr=0o100644<<16;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,data in entries.items():assert sha(z.read(name))==sha(data),name
receipt={'schema':'rei.covariant.unit3_owner_package_receipt.v1','status':'OWNER_ZIP_CREATED_AND_MEMBER_READBACK_PASS_CLOUD_UPLOAD_NOT_YET_CLAIMED','archive_path':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive.read_bytes()),'members':len(entries),'uncompressed_bytes':sum(map(len,entries.values())),'trace_files_complete':4,'compiled_identity_sha256':sha(identity.encode()),'Git_payload_manifest':str(W/'GITHUB_UNIT3_CHUNKS.json'),'payload_chunks':len(records),'Git_mutations':0,'owner_repository_mutations':0,'future004source_included':False,'science_status':status['status'],'full_gate':'PENDING','CPUadequacy':'OPEN'}
write('UNIT3_PACKAGE_RECEIPT.json',receipt)
(W/'CLOSEOUT_READY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
