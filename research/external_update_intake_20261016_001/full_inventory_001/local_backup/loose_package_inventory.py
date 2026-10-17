import csv, datetime, json, os, re, stat, tarfile, zipfile
from pathlib import Path

base = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/external_update_intake_20261016_001/full_inventory_001/local_backup')
dropbox = Path('/home/cosmosapjw/Dropbox')
roots = [
 ('DROPBOX_TOPLEVEL_FILES', dropbox, False),
 ('DBX_BASS_DERIVATION', dropbox/'BASS_DERIVATION_DOSSIERS_20260912', True),
 ('DBX_BASS_BACKUPS', dropbox/'BASS_BACKUPS', True),
 ('DBX_WU088_BACKUPS', dropbox/'WU088_HH_Backups', True),
 ('DBX_BASS_FORMULA_SSOT', dropbox/'BASS_FORMULA_SSOT_V2', True),
 ('DBX_BASS_PR165', dropbox/'BASS_PR165_NATIVE_LOOP_20261016', True),
 ('DBX_REI_BASS_DYNAMIC', dropbox/'REI_BASS_DYNAMIC_20261016', True),
 ('DBX_WU088_HH_PROJECT', dropbox/'WU088_HH', True),
 ('DBX_BASS_CR_PROJECT', dropbox/'bass_cr', True),
 ('REI_PROJECT', dropbox/'bianchi'/'rei_bianchi', True),
 ('REC_PROJECT', dropbox/'bianchi'/'rec_bianchi', True),
 ('BIANCHI_RESEARCH_BACKUPS', dropbox/'bianchi'/'research_backups', True),
 ('BIANCHI_RUNTIME_RECEIPTS', dropbox/'bianchi'/'_runtime_receipts', True),
 ('BIANCHI_RUNTIME_ATTEMPTS', dropbox/'bianchi'/'_runtime_attempt_state', True),
]
archive_re = re.compile(r'(?:\.zip|\.tar|\.tar\.(?:gz|bz2|xz|zst)|\.tgz|\.tbz2|\.txz|\.7z|\.rar|\.bundle|\.patch|\.diff)$', re.I)
prune_names = {'.git','target','targets','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','node_modules','.venv','venv','cache','caches','build-cache'}
prior = set()
with (base/'RAW_INVENTORY.tsv').open(encoding='utf-8',newline='') as f:
    prior = {r['path'] for r in csv.DictReader(f,delimiter='\t')}
records=[]
root_errors=[]
for root_id, root, recursive in roots:
    if not root.exists():
        root_errors.append({'root_id':root_id,'path':str(root),'error':'ROOT_NOT_FOUND'})
        continue
    candidates=[]
    if recursive:
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in prune_names and not d.endswith('_target') and not d.endswith('_cache'))
            for name in sorted(files):
                if archive_re.search(name): candidates.append(Path(current)/name)
            for name in list(dirs):
                p=Path(current)/name
                if p.is_symlink() and archive_re.search(name):
                    candidates.append(p); dirs.remove(name)
    else:
        for p in root.iterdir():
            if p.is_file() and archive_re.search(p.name): candidates.append(p)
    for p in candidates:
        try:
            st=p.lstat(); kind='symlink' if stat.S_ISLNK(st.st_mode) else ('regular' if stat.S_ISREG(st.st_mode) else 'other')
            sec,nano=divmod(st.st_mtime_ns,1_000_000_000)
            ts=datetime.datetime.fromtimestamp(sec,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+f'.{nano:09d}Z'
            records.append({'root_id':root_id,'path':str(p),'bytes':st.st_size,'mtime_utc':ts,'mtime_ns':st.st_mtime_ns,'mode_octal':oct(stat.S_IMODE(st.st_mode)),'kind':kind,'prior_inventory_status':'ALREADY_IN_NAMED_ROOT_INVENTORY' if str(p) in prior else 'NEW_LOOSE_PACKAGE_PATH'})
        except OSError as e: root_errors.append({'root_id':root_id,'path':str(p),'error':repr(e)})
records.sort(key=lambda r:(r['root_id'],r['path']))
with (base/'LOOSE_PACKAGE_FILES.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['root_id','path','bytes','mtime_utc','mtime_ns','mode_octal','kind','prior_inventory_status'],delimiter='\t',quoting=csv.QUOTE_MINIMAL,lineterminator='\n');w.writeheader();w.writerows(records)
with (base/'LOOSE_PACKAGE_ERRORS.jsonl').open('w',encoding='utf-8') as f:
    for e in root_errors: f.write(json.dumps(e,separators=(',',':'))+'\n')
# Index only newly found, previously unindexed ZIP/TAR files. No extraction or hashing.
prior_archives=set()
with (base/'ARCHIVE_INDEX.jsonl').open(encoding='utf-8') as f:
    for line in f:
        try: prior_archives.add(json.loads(line)['archive_path'])
        except Exception: pass
indexed=[]; members=[]; errors=[]
for r in records:
    path=r['path']
    if r['prior_inventory_status']!='NEW_LOOSE_PACKAGE_PATH' or path in prior_archives: continue
    ext=Path(path).suffix.lower()
    fmt='zip' if ext=='.zip' else ('tar' if ext in ('.tar','.tgz') or path.lower().endswith(('.tar.gz','.tar.bz2','.tar.xz','.tbz2','.txz')) else 'unsupported')
    if fmt=='unsupported':
        indexed.append({'archive_path':path,'format':ext.lstrip('.'),'status':'UNSUPPORTED_FORMAT_NOT_OPENED','member_count':None,'declared_bytes':None})
        continue
    try:
        if fmt=='zip':
            with zipfile.ZipFile(path) as z:
                infos=z.infolist()
                for i in infos:
                    mode=(i.external_attr>>16)&0xffff
                    members.append({'archive_path':path,'format':'zip','member_name':i.filename,'declared_bytes':i.file_size,'compressed_bytes':i.compress_size,'member_type':'directory' if i.is_dir() else ('symlink' if stat.S_ISLNK(mode) else 'file')})
        else:
            with tarfile.open(path,'r:*') as t:
                infos=t.getmembers()
                for i in infos:
                    members.append({'archive_path':path,'format':'tar','member_name':i.name,'declared_bytes':i.size,'compressed_bytes':'','member_type':'directory' if i.isdir() else ('symlink' if i.issym() or i.islnk() else 'file')})
        indexed.append({'archive_path':path,'format':fmt,'status':'CENTRAL_DIRECTORY_INDEXED_NO_EXTRACTION','member_count':len(infos),'declared_bytes':sum(i.file_size if fmt=='zip' else i.size for i in infos)})
    except Exception as e:
        errors.append({'archive_path':path,'error':repr(e)})
        indexed.append({'archive_path':path,'format':fmt,'status':'INDEX_ERROR','member_count':None,'declared_bytes':None,'error':repr(e)})
with (base/'LOOSE_ARCHIVE_INDEX.jsonl').open('w',encoding='utf-8') as f:
    for x in indexed: f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
with (base/'LOOSE_ARCHIVE_MEMBERS.tsv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['archive_path','format','member_name','declared_bytes','compressed_bytes','member_type'],delimiter='\t',quoting=csv.QUOTE_MINIMAL,lineterminator='\n');w.writeheader();w.writerows(members)
with (base/'LOOSE_ARCHIVE_ERRORS.jsonl').open('w',encoding='utf-8') as f:
    for e in errors: f.write(json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({'roots':len(roots),'root_errors':len(root_errors),'candidate_rows':len(records),'candidate_unique_paths':len({r['path'] for r in records}),'new_unique_paths':sum(r['prior_inventory_status']=='NEW_LOOSE_PACKAGE_PATH' for r in records),'previous_inventory_overlaps':sum(r['prior_inventory_status']=='ALREADY_IN_NAMED_ROOT_INVENTORY' for r in records),'new_archive_index_rows':len(indexed),'new_member_rows':len(members),'new_index_errors':len(errors),'no_extract':True,'no_hash_or_crc':True},separators=(',',':')))
