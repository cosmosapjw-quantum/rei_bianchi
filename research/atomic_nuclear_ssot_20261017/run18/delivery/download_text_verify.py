#!/usr/bin/env python3
"""Read two authorized TXT backup objects once; compare exact local source bytes."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor

def main():
 p=argparse.ArgumentParser();p.add_argument('--urls',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args()
 source=a.source.read_bytes();sha=hashlib.sha256(source).hexdigest();urls=json.loads(a.urls.read_text())
 def get(item):
  provider,url=item;target=a.output_root/(provider+'_handoff_download.txt')
  with urllib.request.urlopen(url,timeout=45) as response:
   status=response.status;raw=response.read(len(source)+1)
  if raw!=source:raise ValueError('TXT backup is not the exact selected source')
  with target.open('xb') as f:f.write(raw)
  return {'provider':provider,'method':'GET','http_status':status,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'exact_source_bytes_match':True}
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(get,urls.items()))
 receipt={'schema':'rei.run18.handoff-full-readback.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'source':str(a.source),'source_bytes':len(source),'source_sha256':sha,'command_argv':sys.argv,'results':results,'scientific_executions':0}
 with (a.output_root/'HANDOFF_READBACK.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
