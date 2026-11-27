from pathlib import Path
import sys,json,hashlib,os,subprocess,datetime,time
R=Path(__file__).resolve().parent; E=R/'evidence'; OLD=R.parent
sys.path.insert(0,str(OLD)); import record
record.E=E
run=record.run

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(n,v):
 with (E/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def snapshot():
 paths=[OLD/'runtime_work/backend',OLD/'runtime_work/pilot',OLD/'evidence',OLD/'w3/recovered/repo']
 rows=[]
 for root in paths:
  for p in sorted(root.rglob('*')):
   st=p.lstat()
   if p.is_symlink():rows.append(dict(path=str(p),type='symlink',target=os.readlink(p),mtime_ns=st.st_mtime_ns))
   elif p.is_file():rows.append(dict(path=str(p),type='file',bytes=st.st_size,sha256=sha(p),mtime_ns=st.st_mtime_ns))
 return rows
if __name__=='__main__':
 write('PRESERVATION_BEFORE.json',snapshot())
 write('INTAKE_IDENTITY.json',dict(remote_head='ddd9e62b3b6d356f1bdc0bb7ec59a7751346eac8',prompt=dict(path='/root/.cache/WU088_HH/sha256/95/57/9557eb6de5235da550c8c5f0c24643d31f43e09904339270fb66c3946b2db49d',bytes=13046,sha256='9557eb6de5235da550c8c5f0c24643d31f43e09904339270fb66c3946b2db49d',selected_provider='Dropbox',download_count=1,Drive_ID='12PbP5dj1JAQMmJWmD4T6zWsmHLv2m9no',Dropbox_ID='id:BSpOijBcT10AAAAAADxwwg',both_metadata_size=13046,RESTORE_VERIFIED=True),cached_start_sha256='37e7b8b1c0525aa377c82ed2d4d3f8fcad7fb8dab444fba994e186c2e981fdf6',science_dispatch_count=0))
