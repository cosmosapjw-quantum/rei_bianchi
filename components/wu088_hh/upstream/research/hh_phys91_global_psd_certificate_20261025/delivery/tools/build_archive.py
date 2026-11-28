"""RECOVERED_METADATA: reconstructed local packaging helper; not prior byte identity."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def enc(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def run(config,mode):
 c=load(config);r=Path(c['repo']);unit=c['unit'];head=c['head'];parent=c['expected_parent']
 def git(*a):return subprocess.check_output(['git',*a],cwd=r)
 def text(*a):return git(*a).decode().strip()
 assert unit=='research/hh_phys91_global_psd_certificate_20261025'
 assert c['branch']=='research/hh-phys91-global-psd-20261025'
 assert isinstance(c['PR'],int) and isinstance(c['caps'],dict) and c['caps']
 assert isinstance(c['scoped_roles_snapshot'],int) and 0<=c['scoped_roles_snapshot']<=c['total_roles']
 assert text('rev-parse',head+'^{tree}')==c['tree']
 assert text('rev-parse',head+'^')==parent
 baseline=c['preserved_parent_head'];subprocess.run(['git','merge-base','--is-ancestor',baseline,head],cwd=r,check=True)
 delta=git('diff-tree','--no-commit-id','--name-status','-r',baseline,head).decode().splitlines()
 assert delta and all(x.startswith('A\t'+unit+'/') for x in delta),delta
 files={};records={}
 def add(n,b,role,g=None):
  assert n not in files and not Path(n).is_absolute() and '..' not in Path(n).parts
  if g:assert blob(b)==g,n
  files[n]=b;records[n]=dict(bytes=len(b),sha256=sha(b),role=role)
  if g:records[n]['git_blob']=g
 objects={}
 for row in git('ls-tree','-rz',head,'--',unit).split(b'\0'):
  if not row:continue
  meta,n=row.split(b'\t',1);m,k,g=meta.decode().split();n=n.decode()
  assert k=='blob' and m in ('100644','100755')
  add(n,(r/n).read_bytes(),'git_owned',g);objects[n]=g
 assert objects
 bindings=load(c['reuse_bindings'])
 for x in bindings['files']:
  b=(r/x['path']).read_bytes()
  assert len(b)==x['bytes'] and sha(b)==x['sha256'] and blob(b)==x['git_blob']
  assert text('rev-parse',baseline+':'+x['path'])==x['git_blob']
  if x['path'] not in files:add(x['path'],b,x['role'],x['git_blob'])
 for mp in c.get('frozen_maps',[]):
  for rel,h in load(r/mp)['files'].items():assert sha((r/unit/rel).read_bytes())==h
 inputs=load(r/c.get('contract_path',unit+'/CONTRACT.json'))['inputs']
 for x in inputs:
  b=(r/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
  if x['path'] not in files:add(x['path'],b,'contract_input',x.get('git_blob'))
 parents=0
 if mode=='final':
  for x in bindings['parent_files']:
   b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
   add('parent/'+Path(x['path']).name,b,x['role']);parents+=int(x['role']=='whole_parent_archive')
  assert parents==1
 manifest=dict(schema='PHYS91_'+mode.upper()+'_ARCHIVE_V1',helper_status='RECOVERED_METADATA',stage=c['stage'],head=head,tree=c['tree'],expected_parent=parent,PR=c['PR'],caps=c['caps'],scoped_roles_snapshot=c['scoped_roles_snapshot'],total_roles=c['total_roles'],scientific_identity=c.get('scientific_identity'),claims_source=c.get('claims_receipt'),global_physical_completion=None,parent_whole_archives=parents,parent_nested_restore=0,old_science_reruns=0,stage_wholeGET=0,force=False,files=records)
 files['ARCHIVE_MANIFEST.json']=enc(manifest)
 out=Path(c['archive_path']);receipt=Path(c['receipt_path'])
 assert not out.exists() and not receipt.exists()
 if c.get('manifest_path'):assert not Path(c['manifest_path']).exists()
 out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,b in files.items():z.writestr(n,b,compress_type=zipfile.ZIP_STORED if n.endswith('.zip') else zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None and set(z.namelist())==set(files)
  for n,b in files.items():assert sha(z.read(n))==sha(b)
 b=out.read_bytes();d={k:v for k,v in manifest.items() if k!='files'}
 d.update(path=str(out),bytes=len(b),sha256=sha(b),members=len(files),payloads=len(records),git_owned=len(objects),contract_inputs=len(inputs),provider_wholeGET='NOT_RUN',local_payload_readback='PASS')
 receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_bytes(enc(d))
 if c.get('manifest_path'):Path(c['manifest_path']).write_bytes(enc(manifest))
 print(json.dumps(d))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['stage','final']);p.add_argument('config');a=p.parse_args();run(a.config,a.mode)
