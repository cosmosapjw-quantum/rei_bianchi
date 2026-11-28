"""Recover one original ENDF member from the observed official NNDC archive.
No archive-wide checksum claim: stop streaming after the requested member.
"""
import hashlib, json, pathlib, resource, tarfile, time, urllib.request

BASE = pathlib.Path(__file__).resolve().parent
URL = 'https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/gammas/gammas-version.VIII.1.tar.gz'
LIMIT = 32 * 1024**2
class Limited:
    def __init__(self, response):
        self.response=response; self.n=0; self.h=hashlib.sha256()
    def read(self,n=-1):
        if n < 0: n=65536
        if self.n+n > LIMIT: raise RuntimeError('COMPRESSED_SOURCE_RETRIEVAL_CAP')
        b=self.response.read(n); self.n+=len(b); self.h.update(b); return b

out=BASE/'raw'/'nndc_g-001_H_002.endf'
receipt=BASE/'NNDC_H2_RECOVERY.json'
if out.exists() or receipt.exists(): raise SystemExit('NO_OVERWRITE_NO_REPLAY')
t0=time.monotonic(); c0=time.process_time(); rows=[]
r={'source_url':URL,'source_locator':'official index -> main.js/controls.js -> releases/B-VIII.1/metadata.json -> Photonuclear ENDF-6','retrieval_kind':'PARTIAL_ARCHIVE_STREAM_SINGLE_MEMBER','whole_archive_checksum_verified':False,'new_rate_evaluations':0,'new_Q_evaluations':0}
try:
    with urllib.request.urlopen(URL,timeout=30) as response:
        r['HTTP_status']=response.status; stream=Limited(response)
        with tarfile.open(fileobj=stream,mode='r|gz') as tf:
            for member in tf:
                rows.append({'name':member.name,'bytes':member.size})
                if member.isfile() and pathlib.PurePosixPath(member.name).name=='g-001_H_002.endf':
                    if member.size>2*1024**2: raise RuntimeError('UNEXPECTED_MEMBER_SIZE')
                    data=tf.extractfile(member).read()
                    if len(data)!=member.size: raise RuntimeError('TRUNCATED_MEMBER')
                    out.write_bytes(data)
                    r.update({'status':'RECOVERED','archive_member':member.name,'raw_file':str(out.relative_to(BASE)),'bytes':len(data),'SHA256':hashlib.sha256(data).hexdigest()})
                    break
            else: r['status']='MEMBER_NOT_FOUND'
        r['compressed_bytes_read']=stream.n; r['compressed_prefix_SHA256']=stream.h.hexdigest()
except Exception as e:
    r.update(status='SOURCE_RETRIEVAL_FAILED',error=type(e).__name__+': '+str(e))
r.update(members_seen=rows,CPU_s=time.process_time()-c0,wall_s=time.monotonic()-t0)
receipt.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
