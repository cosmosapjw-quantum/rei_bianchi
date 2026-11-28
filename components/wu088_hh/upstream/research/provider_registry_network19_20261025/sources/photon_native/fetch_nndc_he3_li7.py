"""Additive source recovery of the observed He3 and Li7 photonuclear files."""
import hashlib, json, pathlib, tarfile, time, urllib.request
BASE=pathlib.Path(__file__).resolve().parent
URL='https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/gammas/gammas-version.VIII.1.tar.gz'
WANTED={'g-002_He_003.endf','g-003_Li_007.endf','LICENSE'}
class Limited:
    def __init__(self,response): self.response=response; self.n=0; self.h=hashlib.sha256()
    def read(self,n=-1):
        n=65536 if n<0 else n
        if self.n+n>32*1024**2: raise RuntimeError('COMPRESSED_BYTE_CAP')
        b=self.response.read(n);self.n+=len(b);self.h.update(b);return b
t0=time.monotonic();c0=time.process_time()
r={'source_url':URL,'HTTP_status':None,'retrieval_kind':'PARTIAL_ARCHIVE_STREAM_ADDITIONAL_LIGHT_MATERIALS','whole_archive_checksum_verified':False,'new_rate_evaluations':0,'new_Q_evaluations':0,'members_seen':[],'recovered':[]}
dest=BASE/'NNDC_HE3_LI7_RECOVERY.json'
if dest.exists():raise SystemExit('NO_REPLAY')
try:
    with urllib.request.urlopen(URL,timeout=30) as response:
        r['HTTP_status']=response.status;stream=Limited(response)
        with tarfile.open(fileobj=stream,mode='r|gz') as tf:
            for member in tf:
                r['members_seen'].append({'name':member.name,'bytes':member.size})
                name=pathlib.PurePosixPath(member.name).name
                if member.isfile() and name in WANTED:
                    if member.size>8*1024**2:raise RuntimeError('MEMBER_CAP')
                    data=tf.extractfile(member).read(); out=BASE/'raw'/('nndc_'+name)
                    if out.exists():raise RuntimeError('NO_OVERWRITE')
                    if len(data)!=member.size:raise RuntimeError('TRUNCATED_MEMBER')
                    out.write_bytes(data);r['recovered'].append({'member':member.name,'file':str(out.relative_to(BASE)),'bytes':len(data),'SHA256':hashlib.sha256(data).hexdigest()})
                    WANTED.remove(name)
                    if not WANTED:break
            else:r['missing']=sorted(WANTED)
        r.update(status='RECOVERED' if not WANTED else 'PARTIAL',compressed_bytes_read=stream.n,compressed_prefix_SHA256=stream.h.hexdigest())
except Exception as e:r.update(status='RETRIEVAL_FAILED',error=type(e).__name__+': '+str(e))
r.update(CPU_s=time.process_time()-c0,wall_s=time.monotonic()-t0)
dest.write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
