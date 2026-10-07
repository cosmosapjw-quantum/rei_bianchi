#!/usr/bin/env python3
"""Reproduce SYNC03 from the full backup packet or source-pinned Git subset."""
import argparse,hashlib,json,os,pathlib,subprocess,sys,urllib.request
R=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--rustc',required=True);p.add_argument('--sysroot');p.add_argument('--fetch-missing-inputs',action='store_true');a=p.parse_args()
manifest=json.loads((R/'intake/rei/NE_INPUT_MANIFEST.json').read_text())
for item in manifest['files']:
 out=R/'intake/rei/sources'/item['path']
 if not out.exists():
  if not a.fetch_missing_inputs:raise SystemExit('Missing pinned input; use full ZIP or --fetch-missing-inputs: '+str(out))
  url='https://raw.githubusercontent.com/cosmosapjw-quantum/rei_bianchi/'+manifest['head']+'/'+item['path']
  data=urllib.request.urlopen(url,timeout=120).read()
  assert hashlib.sha256(data).hexdigest()==item['sha256'],'immutable source hash mismatch'
  out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 assert hashlib.sha256(out.read_bytes()).hexdigest()==item['sha256']
env=os.environ.copy();env['SYNC03_RUSTC']=str(pathlib.Path(a.rustc).resolve())
if a.sysroot:env['SYNC03_RUST_SYSROOT']=str(pathlib.Path(a.sysroot).resolve())
for name in ['loop1/run_receiver.py','loop1/check_decimal.py','loop2/analyze_transfer.py','loop2/plot_observables.py']:
 subprocess.run([sys.executable,str(R/name)],env=env,check=True,cwd=R)
print('Reproduced scoped finite-history diagnostics. This does not change scientific admission or remote publication.')
