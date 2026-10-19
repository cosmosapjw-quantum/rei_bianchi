#!/usr/bin/env python3
"""Mechanical additive restoration from exact native V14 bytes. No solver design."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-root',required=True,type=Path,help='Repository research/lrs_atomic_native_bridge_20261016 root with v12/v13/v14 restoration chain');p.add_argument('--output-root',required=True,type=Path,help='Fresh run root');a=p.parse_args();spec=json.loads((ROOT/'SOURCE_DELTA_SSPRK2.json').read_text());outroot=a.output_root.resolve();inputroot=a.input_root.resolve()
 if outroot.exists():raise SystemExit('Refusing existing output root: '+str(outroot))
 chain=inputroot/'v14/RESTORE_V14.py'
 if not chain.is_file():raise SystemExit('Missing original V14 restoration chain: '+str(chain))
 outroot.mkdir(parents=True);evidence=outroot/'restore_evidence';evidence.mkdir();a.base=outroot/'frozen_v14_base';a.out=outroot/'native_owner';command=[sys.executable,str(chain),'--out',str(a.base)]
 (evidence/'v14_chain.command.json').write_text(json.dumps({'argv':command,'timeout_s':60},indent=2)+'\n');start=time.monotonic()
 with(evidence/'v14_chain.stdout').open('w')as so,(evidence/'v14_chain.stderr').open('w')as se:
  try:result=subprocess.run(command,stdout=so,stderr=se,timeout=60);code=result.returncode
  except subprocess.TimeoutExpired:code=124
 (evidence/'v14_chain.exit').write_text(str(code)+'\n');(evidence/'v14_chain.timing.json').write_text(json.dumps({'elapsed_s':time.monotonic()-start,'exit':code},indent=2)+'\n')
 if code:raise SystemExit(code)
 if a.out.exists():raise SystemExit('Refusing existing output: '+str(a.out))
 for rel,h in spec['base_sha256'].items():
  if sha(a.base/rel)!=h:raise SystemExit('Frozen V14 base mismatch: '+rel)
 for rel,h in spec['payload_sha256'].items():
  if sha(ROOT/'native_files'/rel)!=h:raise SystemExit('Additive payload mismatch: '+rel)
 shutil.copytree(a.base,a.out,ignore=shutil.ignore_patterns('target','.git','__pycache__'))
 for rec in spec['create']:
  q=a.out/rec['destination']
  if q.exists():raise SystemExit('Unexpected additive conflict: '+str(q))
  q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'native_files'/rec['payload'],q)
 for rec in spec['append']:
  q=a.out/rec['destination'];q.write_bytes(q.read_bytes()+(ROOT/'native_files'/rec['snippet']).read_bytes())
 for rel,h in spec['output_sha256'].items():
  if sha(a.out/rel)!=h:raise SystemExit('Restored output mismatch: '+rel)
 receipt={'schema':'rei.v15.sspp_restore.1','base':str(a.base.resolve()),'output':str(a.out.resolve()),'source_sha256':spec['output_sha256'],'native_compile':'NOT_PERFORMED','status':'SOURCE_RESTORED','input_root':str(inputroot),'original_chain_exit':code,'scope':'source reconstruction only; no native compile or scientific execution'}
 shutil.rmtree(a.base)
 (a.out/'SSPRK2_RESTORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
