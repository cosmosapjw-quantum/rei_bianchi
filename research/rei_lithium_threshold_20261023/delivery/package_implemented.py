from pathlib import Path
import hashlib,json,zipfile,shutil,time,base64,ast
ROOT=Path('/workspace/scratch/d5baa30c266d');REPO=ROOT/'rei_isotope';UNIT=REPO/'research/rei_lithium_threshold_20261023';OUT=ROOT/'exports';DEL=UNIT/'delivery'
tag='IMPLEMENTED_OBSERVED';DEL.mkdir(exist_ok=True)
comparisons=json.loads((UNIT/'results/comparisons.json').read_text());cost=json.loads((UNIT/'results/cost_receipts.json').read_text())
dag=json.loads((UNIT/'DAG.json').read_text())
dag['checkpoint']=tag;dag['scientific_decision']='NUMERICAL_GATES_OBSERVED_PASS_CONTROLLER_AND_FRESH_REVIEW_PENDING'
dag['completion'].update(completed_new_cases=10,theory_scientific_steps='R1-R6 established; R7 observed finite numerical checks complete; R8 pending decision, R9 result formalization pending, R10 pending',coding_scientific_steps='C1-C6 implementation/check execution observed; C7-C8 numerical observations available awaiting scientific admission; C9 fresh review pending, C10 pending')
for n in dag['nodes']:
    i=n['id']
    if i=='R7': n.update(status='COMPLETE_OBSERVED_NUMERICAL',evidence=['results/preflight.json','results/comparisons.json'],checkpoint=tag,remaining='Controller and fresh independent review pending')
    if i=='R9': n.update(status='CONTRACT_DERIVED_RESULTS_AVAILABLE_FORMALIZATION_PENDING',evidence=['THEORY_CONTRACT.md','results/comparisons.json'],checkpoint=tag)
    if i in ['C5','C6']:n.update(status='COMPLETE_OBSERVED_IMPLEMENTATION',evidence=['IMPLEMENTATION.md','results/preflight.json','results/cost_receipts.json'],checkpoint=tag,remaining='Scientific admission and fresh review pending')
    if i in ['C7','C8']:n.update(status='NUMERICAL_EVIDENCE_AVAILABLE_ADMISSION_PENDING',evidence=['results/comparisons.json','results/cost_receipts.json'],checkpoint=tag,remaining='Controller and fresh independent review pending')
    if i=='C9':n.update(status='PENDING_FRESH_ACTUAL_FILE_REVIEW',evidence=['INDEPENDENT_REVIEW.md'],checkpoint=tag)
(UNIT/'DAG.json').write_text(json.dumps(dag,ensure_ascii=False,indent=2)+'\n')
donor=REPO/'research/rei_angular_thermochemistry_20261023'
manifest=json.loads((UNIT/'inputs/driver_manifest.json').read_text())
donor_paths=list(manifest['donor_sources'])+['results/grid044_M16_tight.npz']
dependency=[]
for rel in donor_paths:
    p=donor/rel;d=p.read_bytes();h=hashlib.sha256(d).hexdigest()
    expected=manifest['source_sha256'] if rel=='results/grid044_M16_tight.npz' else manifest['donor_sources'][rel]['sha256']
    assert h==expected
    dependency.append({'path':rel,'bytes':len(d),'sha256':h,'archive_path':'research/rei_lithium_threshold_20261023/donor/rei_angular_thermochemistry_20261023/'+rel})
report={'checkpoint':tag,'scope':'Observed implementation, raw ten-case execution and numerical gate results; scientific decision and fresh independent review pending','completed_cases':10,'all_numerical_gates_observed':comparisons['all_numerical_gates_pass'],'new_ivps_in_packaging':0,'cost_receipt_summary':{k:cost[k] for k in ['CPU_charge_s','wall_charge_s','measured_CPU_s','measured_wall_s']},'requested_implementation_worker':'gpt-6.1-sol/high','observed_runtime_identity':'not exposed by tools','prior_source_commit':'6daf382ee698835e7a141378c232d1d97c1c5cf1','prepared_published_commit':'1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c','dependency_closure':'Complete exact donor bytes embedded at trace_model fallback path; code uses Python standard library, NumPy, SciPy and Matplotlib supplied by runtime, not bundled installations','donor_files':dependency,'verification_method':'Static import/path inspection, existing driver identity comparison and ZIP member reads; no import-side scientific calculations or IVPs performed','excluded':['__pycache__','*.pyc','results/mplconfig','results/launcher_smoke_workspace','results/launcher_smoke_workspace_capfixed'],'retained':'Available failure logs, zero-IVP smoke summaries, cost receipts, all raw completed/partial case NPZ/JSON, figures, code, drivers and source records'}
(DEL/'IMPLEMENTED_OBSERVED.json').write_text(json.dumps(report,indent=2)+'\n')
STAGE=OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_STAGING'
if STAGE.exists():raise SystemExit('Preserve existing immutable snapshot')
STAGE.mkdir()
files=[]
for p in sorted(UNIT.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(UNIT)
    if '__pycache__' in rel.parts or p.suffix=='.pyc' or any(s in rel.parts for s in ['mplconfig','launcher_smoke_workspace','launcher_smoke_workspace_capfixed']):continue
    files.append((p,p.relative_to(REPO).as_posix()))
files.append((REPO/'AGENTS.md','AGENTS.md'))
files.extend((donor/f['path'],f['archive_path']) for f in dependency)
for src,rel in files:
    p=STAGE/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(src.read_bytes())
# Verify the complete fallback dependency closure by reading archived-path staged bytes.
for f in dependency:assert hashlib.sha256((STAGE/f['archive_path']).read_bytes()).hexdigest()==f['sha256']
for rel in ['code/trace_model.py','code/preflight.py','code/run_cases.py','code/analyze.py','code/bounded.py']:
    ast.parse((STAGE/'research/rei_lithium_threshold_20261023'/rel).read_text())
pub=[];members=[]
for p in sorted(STAGE.rglob('*')):
    if not p.is_file():continue
    d=p.read_bytes();rel=p.relative_to(STAGE).as_posix()
    entry={'path':rel,'mode':'100644','gitsha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest(),'size':len(d),'sha256':hashlib.sha256(d).hexdigest()}
    members.append(entry)
    # Publish additive new-unit text; the donor originals already exist in Git.
    if '/donor/' in rel or rel=='AGENTS.md' or p.suffix.lower() in ['.npz','.png','.pdf','.zip']:continue
    try:content=d.decode('utf-8')
    except UnicodeDecodeError:continue
    pub.append(dict(entry,content=content))
(OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_TEXT_PAYLOAD_ALL.json').write_text(json.dumps({'checkpoint':tag,'files':pub},ensure_ascii=False)+'\n')
(OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_GIT_MANIFEST.json').write_text(json.dumps([{k:v for k,v in x.items() if k!='content'} for x in pub],ensure_ascii=False,indent=2)+'\n')
# Large individual UTF8 files use byte-bounded content chunks; root concatenates parts for one Git blob.
chunks=[]
for entry in pub:
    d=entry['content'].encode();parts=[d[i:i+48000] for i in range(0,len(d),48000)] or [b'']
    # UTF8 files here are ASCII-heavy, but split by characters to preserve multibyte boundaries.
    if any(True for _ in []):pass
    texts=[];cur=''
    for line in entry['content'].splitlines(keepends=True):
        if cur and len((cur+line).encode())>48000:texts.append(cur);cur=''
        if len(line.encode())>48000:
            for i in range(0,len(line),12000):
                frag=line[i:i+12000]
                if cur and len((cur+frag).encode())>48000:texts.append(cur);cur=''
                cur+=frag
        else:cur+=line
    if cur or not texts:texts.append(cur)
    assert ''.join(texts)==entry['content']
    for i,text in enumerate(texts):chunks.append(dict({k:v for k,v in entry.items() if k!='content'},part=i,total_parts=len(texts),content=text))
batches=[];cur=[]
for f in chunks:
    if cur and len(json.dumps({'files':cur+[f]},ensure_ascii=False).encode())>79000:batches.append(cur);cur=[]
    cur.append(f)
if cur:batches.append(cur)
batchpaths=[]
for i,b in enumerate(batches,1):
    p=OUT/f'ANGTHERM02_IMPLEMENTED_OBSERVED_TEXT_BATCH_{i:02d}.json';p.write_text(json.dumps({'checkpoint':tag,'files':b},ensure_ascii=False)+'\n');assert p.stat().st_size<=80000;batchpaths.append(str(p))
zp=OUT/'REI_ANGTHERM02_IMPLEMENTED_OBSERVED_20261023.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for e in members:z.write(STAGE/e['path'],e['path'])
with zipfile.ZipFile(zp) as z:
    assert z.testzip() is None
    for f in dependency:assert hashlib.sha256(z.read(f['archive_path'])).hexdigest()==f['sha256']
    assert len(z.namelist())==len(members)
mp=OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_ZIP_MEMBERS.json';mp.write_text(json.dumps(members,indent=2)+'\n')
b64=base64.b64encode(zp.read_bytes()).decode()
chunkdir=OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_ZIP_B64';chunkdir.mkdir()
b64paths=[]
for i,start in enumerate(range(0,len(b64),80000)):
    p=chunkdir/f'{i:04d}.txt';p.write_text(b64[start:start+80000]);b64paths.append(str(p))
receipt={'checkpoint':tag,'archive':str(zp),'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'members':len(members),'text_files':len(pub),'text_batches':batchpaths,'zip_base64_chunks':b64paths,'member_manifest':str(mp),'static_dependency_closure':'15 exact donor files included at implemented fallback path; source/background/M16 accepted history identities verified against driver manifest; ZIP reads verified','new_ivps':0,'scientific_admission':'pending controller and fresh independent review','remote_publication':'not performed'}
(OUT/'ANGTHERM02_IMPLEMENTED_OBSERVED_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
