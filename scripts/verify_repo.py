#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha256(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
registry=json.loads((ROOT/'artifacts/registry/ARTIFACT_REGISTRY.json').read_text())
errors=[]
for item in registry['artifacts']:
 if not item['in_main_branch']:continue
 name='bianchibianchic2.tar.gz' if item['name']=='bianchibianchic2.tar(1).gz' else item['name']
 p=ROOT/'artifacts/compact'/name
 if not p.exists():errors.append(f'missing {p}');continue
 if sha256(p)!=item['sha256']:errors.append(f'hash mismatch {p}')
state=json.loads((ROOT/'PROJECT_STATE.json').read_text())
if not (ROOT/'handoff/CURRENT_HANDOFF_PROMPT.md').exists():errors.append('missing handoff prompt')
if errors:
 print('\n'.join(errors),file=sys.stderr);raise SystemExit(1)
print(f"rei_bianchi verification PASS: {sum(a['in_main_branch'] for a in registry['artifacts'])} main artifacts; current={state['current_stage']}")
