import pathlib,hashlib,json,tarfile,time
snap=pathlib.Path(__file__).resolve().parent;dest=snap/'archives';dest.mkdir();started=time.monotonic()
def filehash(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
records=[]
for case in ['ZERO','SHEAR_PLUS']:
 for label,names in [('selected',['history.csv','abundances.csv']),('complete_prefixes',['history.csv.complete_prefix','abundances.csv.complete_prefix'])]:
  files=[snap/case/name for name in names];expected={str(p.relative_to(snap)):{'bytes':p.stat().st_size,'sha256':filehash(p)} for p in files};archive=dest/(case+'_'+label+'.tar.gz')
  with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
   for p in files:tar.add(p,arcname=str(p.relative_to(snap)))
  recovered={}
  with tarfile.open(archive,'r:gz') as tar:
   for member in tar:
    if member.isfile():
     h=hashlib.sha256();f=tar.extractfile(member)
     for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
     recovered[member.name]={'bytes':member.size,'sha256':h.hexdigest()}
  if recovered!=expected:raise SystemExit('Lossless archive mismatch:'+str(archive))
  records.append({'path':str(archive),'bytes':archive.stat().st_size,'sha256':filehash(archive),'members':expected,'verification':'Exactmembernames/sizes/SHA fromarchive streammatched original files','recovery_command':['tar','-xzf',str(archive.resolve()),'-C','/absolute/empty/snapshot-recovery-directory']})
(snap/'ARCHIVE_RECEIPT.json').write_text(json.dumps({'scope':'SelectedCSVandcomplete-prefixlossless packaging','archives':records,'original_files_preserved':True,'no_source_deletion':True,'wall_seconds':time.monotonic()-started,'scientific_admission':'NOT_ISSUED_BY_PACKAGING'},indent=2)+'\n');print(json.dumps({'archives':[{k:v for k,v in r.items() if k in ['path','bytes','sha256']} for r in records]},indent=2))
