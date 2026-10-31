from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
files=json.loads((root/'evidence'/'OUTPUT_SHA256.json').read_text())
for row in files['outputs']:
 p=root/row['path'];assert p.is_file() and p.stat().st_size==row['bytes'],row['path']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],row['path']
print('RESULT_BYTE_REPLAY_PASS',len(files['outputs']))
