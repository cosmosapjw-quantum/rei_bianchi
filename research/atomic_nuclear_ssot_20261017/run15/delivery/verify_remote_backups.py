#!/usr/bin/env python3
import concurrent.futures,datetime,hashlib,json,time,urllib.request,zipfile,sys
from pathlib import Path
cfg=json.loads(Path(sys.argv[1]).read_text())
def one(e):
    output=Path(e['output']);started=time.perf_counter();sh=hashlib.sha256();blocks=[];pending=b'';size=0
    with urllib.request.urlopen(e['url'],timeout=120) as response,output.open('xb') as out:
        status=response.status
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            out.write(chunk);sh.update(chunk);size+=len(chunk);pending+=chunk
            while len(pending)>=4*1024*1024:
                blocks.append(hashlib.sha256(pending[:4*1024*1024]).digest());pending=pending[4*1024*1024:]
    if pending:blocks.append(hashlib.sha256(pending).digest())
    content_hash=hashlib.sha256(b''.join(blocks)).hexdigest()
    digest=sh.hexdigest()
    assert status==200 and size==cfg['expected_bytes'] and digest==cfg['expected_sha256']
    if 'content_hash' in e:assert content_hash==e['content_hash']
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('MANIFEST.json'))
        for f in manifest['files']:
            b=z.read(f['path']);assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
    return {'provider':e['provider'],'file_id':e['file_id'],'download_method':'single HTTP GET, no HEAD or Range preflight','http_status':status,'downloaded_bytes':size,'sha256':digest,'expected_sha256_match':True,'dropbox_content_hash_computed':content_hash,'provider_content_hash_match':('content_hash' in e),'archive_CRC_and_all_payload_hashes':'PASS','payload_files_checked':len(manifest['files']),'elapsed_seconds':time.perf_counter()-started,'local_download_path':str(output)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,cfg['entries']))
r={'schema':'rei.run15.remote_backup_download_verification.v1','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv_without_sensitive_urls':sys.argv,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':results,'all_download_bytes_and_archive_payloads_verified':True,'native_IVPs_executed':0}
Path('/tmp/rei_run15_final_remote_readback_receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
