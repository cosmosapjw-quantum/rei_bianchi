"""Unmodified file SHA256 identity, independent of transport ZIP byte metadata."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
manifest=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
errors=[]
for rel,sha in manifest.items():
 p=ROOT/rel
 if not p.is_file():errors.append((rel,'MISSING'));continue
 found=hashlib.sha256(p.read_bytes()).hexdigest()
 if found!=sha:errors.append((rel,'HASH_MISMATCH',sha,found))
if errors:
 print('FAIL',len(errors),'of',len(manifest));print(errors[:10]);sys.exit(1)
print('PASS',len(manifest),'/',len(manifest),'SHA256 source/data/science/draw evidence')
