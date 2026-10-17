import csv, datetime, json, os, stat
from pathlib import Path

base = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/external_update_intake_20261016_001/full_inventory_001/local_backup')
roots = []
with (base / 'ROOTS.tsv').open(encoding='utf-8', newline='') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        roots.append((row['root_id'], Path(row['absolute_root'])))
records = []
errors = []
active_root_id = None
def record_walk_error(e):
    errors.append({'root_id': active_root_id, 'path': getattr(e, 'filename', None), 'error': repr(e)})

for root_id, root in roots:
    active_root_id = root_id
    if not root.exists():
        errors.append({'root_id': root_id, 'path': str(root), 'error': 'ROOT_NOT_FOUND'})
        continue
    try:
        for current, dirs, files in os.walk(root, followlinks=False, onerror=record_walk_error):
            dirs.sort()
            files.sort()
            for name in files:
                p = Path(current) / name
                try:
                    st = p.lstat()
                    kind = 'symlink' if stat.S_ISLNK(st.st_mode) else ('regular' if stat.S_ISREG(st.st_mode) else 'other')
                    sec, nano = divmod(st.st_mtime_ns, 1_000_000_000)
                    ts = datetime.datetime.fromtimestamp(sec, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S') + f'.{nano:09d}Z'
                    records.append({'root_id': root_id, 'path': str(p), 'bytes': st.st_size, 'mtime_utc': ts, 'mtime_ns': st.st_mtime_ns, 'mode_octal': oct(stat.S_IMODE(st.st_mode)), 'kind': kind})
                except OSError as e:
                    errors.append({'root_id': root_id, 'path': str(p), 'error': repr(e)})
            for name in list(dirs):
                p = Path(current) / name
                try:
                    if p.is_symlink():
                        st = p.lstat()
                        sec, nano = divmod(st.st_mtime_ns, 1_000_000_000)
                        ts = datetime.datetime.fromtimestamp(sec, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S') + f'.{nano:09d}Z'
                        records.append({'root_id': root_id, 'path': str(p), 'bytes': st.st_size, 'mtime_utc': ts, 'mtime_ns': st.st_mtime_ns, 'mode_octal': oct(stat.S_IMODE(st.st_mode)), 'kind': 'symlink_dir'})
                        dirs.remove(name)
                except OSError as e:
                    errors.append({'root_id': root_id, 'path': str(p), 'error': repr(e)})
    except OSError as e:
        errors.append({'root_id': root_id, 'path': str(root), 'error': repr(e)})
records.sort(key=lambda r: (r['root_id'], r['path']))
with (base / 'RAW_INVENTORY.tsv').open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['root_id','path','bytes','mtime_utc','mtime_ns','mode_octal','kind'], delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    w.writeheader(); w.writerows(records)
with (base / 'RAW_INVENTORY.jsonl').open('w', encoding='utf-8', newline='') as f:
    for r in records: f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')
with (base / 'SCAN_ERRORS.jsonl').open('w', encoding='utf-8', newline='') as f:
    for e in errors: f.write(json.dumps(e, ensure_ascii=False, separators=(',', ':')) + '\n')
print(json.dumps({'roots': len(roots), 'files_and_symlinks': len(records), 'total_bytes': sum(r['bytes'] for r in records), 'errors': len(errors), 'mtime_timezone': 'UTC'}, separators=(',', ':')))
