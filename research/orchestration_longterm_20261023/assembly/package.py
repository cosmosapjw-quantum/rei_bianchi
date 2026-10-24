#!/usr/bin/env python3
"""Freeze staged source without caches, old binary cohorts or private inventories."""
import argparse,hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'assembly';PUB=ROOT/'publish'
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['S1_REVIEWED','S2_DELIVERY']);args=ap.parse_args()
files=[f for f in PUB.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
manifest={'stage':args.stage,'scope':'Reviewed task source; staged publication bytes, no private conversation bodies or giant provider inventories','files':[]}
for f in sorted(files):
 b=f.read_bytes();manifest['files'].append({'path':str(f.relative_to(PUB)),'size_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
mp=OUT/(args.stage+'_MANIFEST.json');mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
zp=OUT/('ORCHESTRATION_LONGTERM_20261023_'+args.stage+'.zip')
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(files):z.write(f,str(f.relative_to(PUB)))
 z.write(mp,'MANIFEST.json')
with zipfile.ZipFile(zp) as z:
 bad=z.testzip()
 if bad:raise ValueError('ZIP CRC failure '+bad)
 for row in manifest['files']:
  b=z.read(row['path'])
  if hashlib.sha256(b).hexdigest()!=row['sha256']:raise ValueError('member hash mismatch '+row['path'])
receipt={'path':str(zp),'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'members':len(files)+1,'crc':'PASS','member_sha256':'PASS','publication_files':len(files)}
(OUT/(args.stage+'_ARTIFACT_RECEIPT.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
