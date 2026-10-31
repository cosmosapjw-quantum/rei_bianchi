from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
exp=json.loads((R/'evidence'/'OUTPUT_SHA256.json').read_text())
for p,h in exp.items():
 data=(R/p).read_bytes()
 assert hashlib.sha256(data).hexdigest()==h,(p,'DIFFERENT_OUTPUT_SHA')
print('OUTPUT_SHA_REPLAY',len(exp),'PASS')
