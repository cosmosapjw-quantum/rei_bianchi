import csv, json, tarfile, zipfile
from pathlib import Path

base = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/external_update_intake_20261016_001/full_inventory_001/local_backup')
known = ('.zip', '.tar', '.tar.gz', '.tgz', '.tar.xz', '.txz', '.tar.bz2', '.tbz2')
unsupported = ('.7z', '.rar', '.tar.zst', '.tzst')
archives = []
with (base / 'RAW_INVENTORY.jsonl').open(encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        low = rec['path'].lower()
        if low.endswith(known):
            archives.append((rec['path'], 'index'))
        elif low.endswith(unsupported):
            archives.append((rec['path'], 'unsupported'))
summary = []
errors = []
with (base / 'ARCHIVE_MEMBERS.tsv').open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    w.writerow(['archive_path','format','member_name','declared_bytes','compressed_bytes','member_type'])
    for path, mode in archives:
        if mode == 'unsupported':
            summary.append({'archive_path': path, 'format': Path(path).suffix.lower(), 'status': 'FORMAT_NOT_INDEXED', 'member_count': None, 'declared_bytes': None})
            continue
        try:
            low = path.lower()
            members = []
            if low.endswith('.zip'):
                with zipfile.ZipFile(path, 'r') as z:
                    for info in z.infolist():
                        typ = 'directory' if info.is_dir() else 'file'
                        w.writerow([path, 'zip', info.filename, info.file_size, info.compress_size, typ])
                        members.append(info.file_size)
                fmt = 'zip'
            else:
                with tarfile.open(path, mode='r:*') as t:
                    for info in t.getmembers():
                        typ = 'directory' if info.isdir() else ('symlink' if info.issym() else ('hardlink' if info.islnk() else ('file' if info.isfile() else 'other')))
                        w.writerow([path, 'tar', info.name, info.size, '', typ])
                        members.append(info.size)
                fmt = 'tar'
            summary.append({'archive_path': path, 'format': fmt, 'status': 'CENTRAL_DIRECTORY_INDEXED_NO_EXTRACTION', 'member_count': len(members), 'declared_bytes': sum(members)})
        except Exception as e:
            msg = repr(e)
            summary.append({'archive_path': path, 'format': 'zip' if low.endswith('.zip') else 'tar', 'status': 'ARCHIVE_INDEX_ERROR', 'member_count': None, 'declared_bytes': None, 'error': msg})
            errors.append({'archive_path': path, 'error': msg})
with (base / 'ARCHIVE_INDEX.jsonl').open('w', encoding='utf-8', newline='') as f:
    for rec in summary: f.write(json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n')
with (base / 'ARCHIVE_ERRORS.jsonl').open('w', encoding='utf-8', newline='') as f:
    for rec in errors: f.write(json.dumps(rec, ensure_ascii=False, separators=(',', ':')) + '\n')
print(json.dumps({'archive_candidates': len(archives), 'indexed': sum(1 for x in summary if x['status'] == 'CENTRAL_DIRECTORY_INDEXED_NO_EXTRACTION'), 'unsupported': sum(1 for x in summary if x['status'] == 'FORMAT_NOT_INDEXED'), 'errors': len(errors), 'member_rows': sum(x['member_count'] or 0 for x in summary)}, separators=(',', ':')))
