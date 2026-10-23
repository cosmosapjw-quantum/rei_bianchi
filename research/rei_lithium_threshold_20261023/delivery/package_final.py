from pathlib import Path
import hashlib,json,zipfile,base64,ast,time
ROOT=Path('/workspace/scratch/d5baa30c266d');REPO=ROOT/'rei_isotope';UNIT=REPO/'research/rei_lithium_threshold_20261023';OUT=ROOT/'exports';DEL=UNIT/'delivery';PREFIX='research/rei_lithium_threshold_20261023'
dag=json.loads((UNIT/'DAG.json').read_text())
assert 'PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE' in (UNIT/'SCIENTIFIC_DECISION.md').read_text()
review=(UNIT/'INDEPENDENT_REVIEW.md').read_text();assert 'PASS' in review
dag.update(checkpoint='FINAL_SCIENTIFIC_COMPLETE_DELIVERY_ACK_PENDING',scientific_decision='PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE',prepared_commit='1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c',implemented_commit='906f217f412500fd8d4129818e70a4064439c945',publication_expected_head='906f217f412500fd8d4129818e70a4064439c945',checkpoint_scope='Self-contained reviewed ANGTHERM02 conditional science package with all 15 exact required donor files, bath driver, raw results and figures; final upload/Git acknowledgements are external sidecar facts')
dag.setdefault('historical_prepared_dependency',dict(dag['prior_immutable_dependency']))
dag['prior_immutable_dependency']['role']='Original immutable ANGTHERM01 archive provenance. The required 15 exact dependency files are embedded in this final package; no separate archive fetch is required for ANGTHERM02 runtime inputs.'
dag['completion'].update(theory_scientific_steps='R1-R10 scientifically complete in admitted conditional scope; actual final delivery acknowledgements tracked separately',coding_scientific_steps='C1-C10 scientifically complete in admitted conditional scope; actual final delivery acknowledgements tracked separately',global_percentage=None,scientific_unit_complete=True,external_final_delivery_status='PENDING_ACTUAL_PROVIDER_AND_COMMIT_ACKNOWLEDGEMENTS')
evs={
'R7':['results/preflight.json','results/comparisons.json','results/execution_summary.json'],
'R8':['SCIENTIFIC_DECISION.md','INDEPENDENT_REVIEW.md'],
'R9':['SCIENTIFIC_DECISION.md','REPORT_KO.md','THRESHOLD_ASYMPTOTIC.md','IMPLEMENTATION.md'],
'R10':['HANDOFF.md','REPORT_KO.md','delivery/REPRODUCE_FINAL.md','delivery/CHECKPOINT_RECEIPTS.json'],
'C5':['IMPLEMENTATION.md','code/trace_model.py','code/run_cases.py'],
'C6':['results/preflight.json','results/cost_receipts.json'],
'C7':['SCIENTIFIC_DECISION.md','results/comparisons.json','INDEPENDENT_REVIEW.md'],
'C8':['results/execution_summary.json','results/cost_receipts.json','delivery/REPRODUCE_FINAL.md'],
'C9':['INDEPENDENT_REVIEW.md','SCIENTIFIC_DECISION.md'],
'C10':['SCIENTIFIC_DECISION.md','REPORT_KO.md','HANDOFF.md','delivery/FINAL_PACKAGE_SCOPE.json']}
for n in dag['nodes']:
    i=n['id']
    if i.startswith(('R','C')) and i[1:].isdigit():
        n.update(status='COMPLETE_SCOPED_SCIENTIFIC',checkpoint='FINAL',remaining=None)
        if i in evs:n['evidence']=evs[i]
    if i=='LiA2':n.update(status='PASS_SCOPED_CONDITIONAL_RESPONSE_FULL_HISTORY_TARGET_OPEN',evidence=['SCIENTIFIC_DECISION.md','REPORT_KO.md','INDEPENDENT_REVIEW.md'],next='Construct the smallest closed feedback or retained-bath response model; earlier continuum seed, exact bath and unobserved higher-bin angular tail remain full-history dependencies')
dag['external_delivery']={'prepared_and_implemented':'ACKNOWLEDGED_SEE_delivery/CHECKPOINT_RECEIPTS.json','final':'PENDING_ACTUAL_ACKNOWLEDGEMENTS','final_authoritative_sidecar':'delivery/FINAL_DELIVERY.json or delivery/FINAL_DELIVERY.md published after archive creation','archive_self_hash_inside_archive':False}
(UNIT/'DAG.json').write_text(json.dumps(dag,ensure_ascii=False,indent=2)+'\n')
(DEL/'REPRODUCE_FINAL.md').write_text("""# Reproduce the final ANGTHERM02 checkpoint

This delivery supplement gives the exact archive layout and fresh-output
location for the FINAL archive. The existing top-level REPRODUCE.md describes
the model and commands; use the concrete layout below with that document.

## Extracted evidence root

Extract REI_ANGTHERM02_FINAL_20261023.zip into an empty directory, for example
ang02_evidence/. Its research unit is then:

    ang02_evidence/research/rei_lithium_threshold_20261023/

That directory contains code/, inputs/, results/, figures/, sources/, delivery/,
the final scientific documents, and donor/rei_angular_thermochemistry_20261023/.
The archive also contains AGENTS.md at its top level. The embedded donor path is
the fallback explicitly implemented in code/trace_model.py. No sibling donor
checkout or separate prior archive is needed for this unit's runtime inputs.

## Preserve recorded results and use a fresh run directory

The archived results/ is completed evidence. Do not run into it: the launcher
correctly refuses to replay completed/partial cases and its receipt contains
the historical charged costs. The implementation uses BASE/results, so a
separate fresh copy of the runtime inputs defines the separate output path.

From the directory containing ang02_evidence/, create ang02_rerun/ with no
results directory, then copy these items from the extracted research unit:

    code/
    inputs/
    donor/
    THEORY_CONTRACT.md

For example, using a shell from that parent directory:

    mkdir ang02_rerun
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/code ang02_rerun/
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/inputs ang02_rerun/
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/donor ang02_rerun/
    cp ang02_evidence/research/rei_lithium_threshold_20261023/THEORY_CONTRACT.md ang02_rerun/
    cd ang02_rerun

Only an independently authorized reproduction should execute:

    python code/bounded.py preflight preflight.py
    python code/bounded.py chemistry run_cases.py 1 2 3 4 5 6 7 8
    python code/bounded.py bootstrap run_cases.py 9 10
    python code/bounded.py analysis analyze.py

The fresh output paths are ang02_rerun/results/ and ang02_rerun/figures/.
Use Python 3 with NumPy, SciPy and Matplotlib. Observed module and Python versions\nare recorded in delivery/RUNTIME_VERSIONS.json. Runtime packages are not bundled.
No dependency installation, original full gas/photon trajectory replay, or
driver regeneration is required. The retained bath_drivers.npz is an exact input
of this conditional experiment. build_drivers is available for diagnosis but is
not part of this reproduction recipe.

The archived cost receipts, driver manifest and final decision distinguish
known measured use, the conservative debit for a lost old failure, and separate
packaging costs. Numerical comparison uses the declared residuals/tolerances;
ZIP timestamps and recompressed NPZ bytes are packaging identities.
""")
donor=REPO/'research/rei_angular_thermochemistry_20261023';m=json.loads((UNIT/'inputs/driver_manifest.json').read_text());donor_paths=list(m['donor_sources'])+['results/grid044_M16_tight.npz'];deps=[]
assert hashlib.sha256((UNIT/'inputs/bath_drivers.npz').read_bytes()).hexdigest()==m['driver_sha256']
for rel in donor_paths:
    p=donor/rel;d=p.read_bytes();expected=m['source_sha256'] if rel=='results/grid044_M16_tight.npz' else m['donor_sources'][rel]['sha256'];assert hashlib.sha256(d).hexdigest()==expected,rel
    deps.append({'source_path':rel,'archive_path':PREFIX+'/donor/rei_angular_thermochemistry_20261023/'+rel,'bytes':len(d),'sha256':expected})
scope={'unit':'ANGTHERM02','checkpoint':'FINAL','scientific_decision':'PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE','scientific_steps':'R1-R10 and C1-C10 complete in admitted conditional scope','global_percentage':None,'full_coupled_continuum_angular_target':'OPEN','final_external_delivery':'Pending actual acknowledgements; final authoritative receipt is an external sidecar published after archive creation','archive_filename':'REI_ANGTHERM02_FINAL_20261023.zip','included':'Actual final code, exact bath driver, all available raw/partial results and failure logs, cost/execution receipts, three final figures, fresh review, final decision/report/handoff, source records, prior checkpoint receipts and exact minimal donor dependency','excluded':'Nested archives, worker snapshot/chunks, caches, duplicate smoke-workspace trees; lost pre-reset raw logs are not reconstructed','donor_dependencies':deps,'input_identity_result':'All 15 exact donor dependencies and retained bath driver match frozen driver-manifest identities; no mismatch observed','reproduction':'delivery/REPRODUCE_FINAL.md','requested_implementation_worker':'gpt-6.1-sol/high','runtime_identity':'not exposed by tools; requested identity is not observed runtime evidence','new_ivps_in_packaging':0}
(DEL/'FINAL_PACKAGE_SCOPE.json').write_text(json.dumps(scope,indent=2)+'\n')
STAGE=OUT/'ANGTHERM02_FINAL_STAGING_V3'
if STAGE.exists():raise SystemExit('Final snapshot exists; preserve it')
STAGE.mkdir();files=[]
excluded_parts={'__pycache__','mplconfig','launcher_smoke_workspace','launcher_smoke_workspace_capfixed','snapshot_chunks'}
for p in sorted(UNIT.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(UNIT)
    if any(q in excluded_parts for q in rel.parts) or p.suffix.lower() in {'.pyc','.zip','.b64','.tar','.gz'} or p.name=='worker_snapshot_receipt.json':continue
    files.append((p,p.relative_to(REPO).as_posix()))
files.append((REPO/'AGENTS.md','AGENTS.md'));files.extend((donor/f['source_path'],f['archive_path']) for f in deps)
for p,rel in files:
    target=STAGE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
members=[];pub=[]
for p in sorted(STAGE.rglob('*')):
    if not p.is_file():continue
    d=p.read_bytes();rel=p.relative_to(STAGE).as_posix();e={'path':rel,'mode':'100644','gitsha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest(),'size':len(d),'sha256':hashlib.sha256(d).hexdigest()};members.append(e)
    if rel=='AGENTS.md' or '/donor/' in rel or p.suffix.lower() in {'.npz','.png','.pdf'}:continue
    try:text=d.decode('utf-8')
    except UnicodeDecodeError:continue
    pub.append(dict(e,content=text))
for rel in ['code/trace_model.py','code/preflight.py','code/run_cases.py','code/analyze.py','code/bounded.py']:ast.parse((STAGE/PREFIX/rel).read_text())
chunks=[]
for e in pub:
    texts=[];cur=''
    for line in e['content'].splitlines(keepends=True):
        if cur and len((cur+line).encode())>48000:texts.append(cur);cur=''
        if len(line.encode())>48000:
            for start in range(0,len(line),12000):
                frag=line[start:start+12000]
                if cur and len((cur+frag).encode())>48000:texts.append(cur);cur=''
                cur+=frag
        else:cur+=line
    if cur or not texts:texts.append(cur)
    assert ''.join(texts)==e['content']
    for i,text in enumerate(texts):chunks.append(dict({k:v for k,v in e.items() if k!='content'},part=i,total_parts=len(texts),content=text))
batches=[];cur=[]
for f in chunks:
    if cur and len(json.dumps({'files':cur+[f]},ensure_ascii=False).encode())>79000:batches.append(cur);cur=[]
    cur.append(f)
if cur:batches.append(cur)
batchpaths=[]
for i,b in enumerate(batches,1):
    p=OUT/f'ANGTHERM02_FINAL_TEXT_BATCH_{i:02d}.json';p.write_text(json.dumps({'checkpoint':'FINAL','files':b},ensure_ascii=False)+'\n');assert p.stat().st_size<=80000;batchpaths.append(str(p))
(OUT/'ANGTHERM02_FINAL_TEXT_PAYLOAD_ALL.json').write_text(json.dumps({'checkpoint':'FINAL','files':pub},ensure_ascii=False)+'\n')
gp=OUT/'ANGTHERM02_FINAL_GIT_MANIFEST.json';gp.write_text(json.dumps([{k:v for k,v in e.items() if k!='content'} for e in pub],indent=2)+'\n')
mp=OUT/'ANGTHERM02_FINAL_ZIP_MEMBERS.json';mp.write_text(json.dumps(members,indent=2)+'\n')
zp=OUT/'REI_ANGTHERM02_FINAL_20261023.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for e in members:z.write(STAGE/e['path'],e['path'])
with zipfile.ZipFile(zp) as z:
    assert z.testzip() is None
    for e in members:assert hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256']
    assert all(not n.lower().endswith(('.zip','.b64','.pyc')) for n in z.namelist())
b64=base64.b64encode(zp.read_bytes()).decode();chunkdir=OUT/'ANGTHERM02_FINAL_ZIP_B64';chunkdir.mkdir(exist_ok=True);b64paths=[]
for i,start in enumerate(range(0,len(b64),80000)):
    p=chunkdir/f'{i:04d}.txt';p.write_text(b64[start:start+80000]);b64paths.append(str(p))
receipt={'unit':'ANGTHERM02','checkpoint':'FINAL','archive':str(zp),'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'members':len(members),'text_files':len(pub),'text_parts':len(chunks),'text_batches':batchpaths,'zip_base64_chunks':b64paths,'member_manifest':str(mp),'git_manifest':str(gp),'dependency_closure':'15 exact donor files at implemented fallback path and exact bath driver verified; all ZIP member bytes verified; no input mismatch observed','scope':'Scientifically final, admitted conditional response; global dependencies remain open. Final provider/commit acknowledgements are external sidecars after archive creation.','scientific_decision':'PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE','new_ivps':0,'remote_publication':'not performed by packaging worker'}
(OUT/'ANGTHERM02_FINAL_PACKAGE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='zip_base64_chunks'},indent=2));print('zip_base64_chunks',len(b64paths))
