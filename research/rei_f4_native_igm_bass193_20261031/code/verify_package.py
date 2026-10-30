from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mode=sys.argv[1] if len(sys.argv)>1 else 'manifest'
if mode=='manifest':
 d=json.loads((ROOT/'MANIFEST.json').read_text());names=d['sha256'];bad=[p for p,v in names.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=v]
 if bad:raise SystemExit('MANIFEST_MISMATCH: '+repr(bad))
 print(f'MANIFEST={len(names)}/{len(names)} PASS')
elif mode=='output':
 d=json.loads((ROOT/'OUTPUT_SHA256.json').read_text());bad=[p for p,v in d['sha256'].items() if sha(ROOT/p)!=v]
 if bad:raise SystemExit('OUTPUT_MISMATCH: '+repr(bad))
 print(f'OUTPUT_REPLAY={len(d["sha256"])}/{len(d["sha256"])} SHA PASS')
else:raise SystemExit('unknown mode')
