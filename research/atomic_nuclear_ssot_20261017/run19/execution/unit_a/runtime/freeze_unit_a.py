"""Add-only evidence assembly after native sources and results stop changing."""
from pathlib import Path
import datetime,difflib,hashlib,json,shutil
RUNTIME=Path(__file__).resolve().parent
RUN19=Path('/tmp/rei_run19_repo/research/atomic_nuclear_ssot_20261017/run19')
ORIGINAL=RUN19.parent/'run13/recovered/code/rei_bass_coupled'
NATIVE=RUN19/'native';OUT=RUN19/'execution/unit_a'
OUT.mkdir(parents=True,exist_ok=False)
def ident(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
def row(path,root):
    return {'path':str(path.relative_to(root)),**ident(path.read_bytes()),
        'git_mode':'100755'if path.stat().st_mode&0o111 else '100644'}
baseline=json.loads((RUN19/'inventory/BASE_NATIVE_MANIFEST.json').read_text())
for item in baseline['files']:
    assert ident((ORIGINAL/item['path']).read_bytes())['sha256']==item['sha256'],item['path']
before={r['path']:r for r in baseline['files']}
after=[row(p,NATIVE)for p in sorted(NATIVE.rglob('*'))if p.is_file()]
changes=[];patch=[]
for item in after:
    old=before.get(item['path'])
    if old and old['sha256']==item['sha256']:continue
    changes.append({'path':item['path'],'kind':'MODIFIED_FORK_ONLY'if old else 'ADDED',
        'before':old,'after':item})
    old_text=(ORIGINAL/item['path']).read_text().splitlines(keepends=True)if old else []
    new_text=(NATIVE/item['path']).read_text().splitlines(keepends=True)
    patch.extend(difflib.unified_diff(old_text,new_text,
        fromfile='run13/recovered/code/rei_bass_coupled/'+item['path']if old else '/dev/null',
        tofile='run19/native/'+item['path']))
missing=set(before)-{r['path']for r in after};assert not missing,missing
(OUT/'SOURCE_DIFF.patch').write_text(''.join(patch))
(OUT/'NATIVE_AFTER_MANIFEST.json').write_text(json.dumps({'schema':'REI_RUN19_UNIT_A_SOURCE_V1',
    'source_commit':baseline['source_commit'],'files':after,'file_count':len(after),
    'total_bytes':sum(r['bytes']for r in after)},indent=2)+'\n')
copy_map=[]
def copy(source,dest):
    assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest);assert source.read_bytes()==dest.read_bytes()
    copy_map.append({'source':str(source),'destination':str(dest.relative_to(OUT)),**ident(dest.read_bytes())})
for source in sorted((RUNTIME/'evidence').rglob('*')):
    if source.is_file():copy(source,OUT/'evidence'/source.relative_to(RUNTIME/'evidence'))
runtime_names=['INITIAL_RUNTIME_PROBE.json','RUST_INSTALLER_INVENTORY.json','SELECTED_COMPONENT_MANIFEST.json',
    'INSTALL_PROBE_RECEIPT.json','install_and_probe.py','run_recorded.py','restore_minimal_rust.py',
    'compiler_probe.rs','summarize_bench.py','freeze_unit_a.py']
runtime_names.extend(p.name for p in RUNTIME.iterdir()if p.is_file()and p.name.endswith(('.stdout.txt','.stderr.txt')))
for name in sorted(set(runtime_names)):copy(RUNTIME/name,OUT/'runtime'/name)
copy(RUNTIME/'UNIT_A_REPORT_KO.md',OUT/'UNIT_A_REPORT_KO.md')
bin_dir=RUNTIME/'unit_a_bin';bin_dir.mkdir(exist_ok=False)
binaries=[]
for name in ['gas_rhs_server','run19_gas_bench']:
    source=RUNTIME/'target/release/examples'/name;dest=bin_dir/name;shutil.copy2(source,dest)
    assert dest.read_bytes()==source.read_bytes()
    binaries.append({'name':name,'preserved_path':str(dest),**ident(dest.read_bytes()),'mode':'0755'})
receipt={'schema':'REI_RUN19_UNIT_A_RECEIPT_V1','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_commit':baseline['source_commit'],'source_tree':baseline['source_tree'],
    'original_source_path':str(ORIGINAL),'new_source_path':str(NATIVE),'original_files_verified_unchanged':len(before),
    'new_source_file_count':len(after),'changes':changes,'binaries':binaries,'copy_map':copy_map,
    'actual_tests':{'new_integration_tests_passed':6,'new_server_tests_passed':2,'old_full_suites_rerun':0},
    'actual_experiments':{'core_probe_rows':22,'core_measurement_rows':72,'core_repetitions':5,
        'ipc_measurement_rows':24,'ipc_repetitions':3,'same_backend_ipc_replies_byte_identical':True,
        'gas_or_transport_ivps':0,'old_m2_history_repeats':0},
    'provenance_limits':['archive SHA verified; archive signature not verified',
        'prepared evaluator ID binds algorithm kind, not individual table instance',
        'core original gas source is exact include; its direct D call uses unchanged common D ledger assembly',
        'IPC compares new optimized single protocol against new batch, not historical binary',
        'table speed changes accuracy; sampled point differences are not a global or trajectory bound',
        'no explicit SIMD implementation or SIMD speedup established'],
    'publication_status':'PENDING_ROOT_PUBLICATION','backup_status':'PENDING_ROOT_ARCHIVE_AND_BACKUPS'}
(OUT/'UNIT_A_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
manifest=[row(p,OUT)for p in sorted(OUT.rglob('*'))if p.is_file()]
(OUT/'UNIT_A_EVIDENCE_MANIFEST.json').write_text(json.dumps({'schema':'REI_RUN19_UNIT_A_EVIDENCE_V1',
    'self_excluded':True,'files':manifest,'file_count':len(manifest),'total_bytes':sum(r['bytes']for r in manifest)},indent=2)+'\n')
print(json.dumps({'output':str(OUT),'original_unchanged':len(before),'source_files':len(after),
    'changes':[{'path':c['path'],'kind':c['kind'],'sha256':c['after']['sha256']}for c in changes],
    'evidence_files':len(manifest),'evidence_bytes':sum(r['bytes']for r in manifest),
    'binaries':binaries,'receipt_identity':ident((OUT/'UNIT_A_RECEIPT.json').read_bytes())},indent=2))
