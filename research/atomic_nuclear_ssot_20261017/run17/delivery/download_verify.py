#!/usr/bin/env python3
"""Full-GET two authorized backups; never print signed URLs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--urls',type=Path,required=True)
    p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--verifier-root',type=Path,required=True)
    p.add_argument('--expected-sha',required=True)
    p.add_argument('--expected-bytes',type=int,required=True)
    a=p.parse_args()
    sys.path.insert(0,str(a.verifier_root))
    from verify_archive import verify
    urls=json.loads(a.urls.read_text())
    def get(item):
        name,url=item
        target=a.output_root/(name+'_download.zip')
        if target.exists(): raise ValueError('create-only readback path already exists')
        count=0; digest=hashlib.sha256()
        with urllib.request.urlopen(url,timeout=45) as response, target.open('xb') as f:
            status=response.status
            while True:
                raw=response.read(1048576)
                if not raw:break
                count+=len(raw)
                if count>a.expected_bytes:raise ValueError('remote larger than declared archive')
                f.write(raw);digest.update(raw)
        if count!=a.expected_bytes or digest.hexdigest()!=a.expected_sha:
            raise ValueError('remote byte identity mismatch')
        checked=verify(target,a.expected_sha)
        return {'provider':name,'http_method':'GET','http_status':status,'full_bytes_downloaded':count,
                'download_sha256':digest.hexdigest(),'identity_matches_expected':True,
                'archive_verification':checked}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(get,urls.items()))
    receipt={'schema':'rei.run17.backup-full-readback.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
             'command_argv':sys.argv,'results':results,'native_calls':0,'scientific_recalculations':0}
    with (a.output_root/'BACKUP_READBACK.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
