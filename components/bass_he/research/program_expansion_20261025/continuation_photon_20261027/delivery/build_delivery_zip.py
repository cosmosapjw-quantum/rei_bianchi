#!/usr/bin/env python3
"""Package committed metadata-only S..D05 delta and its real Git bundle.

Run once after review and commit of the exact delivery HEAD. No science or network.
External closeout records the resulting D05, archive hash and backup ACKs.
"""
import argparse, hashlib, io, json, os, re, subprocess, tempfile, zipfile
from pathlib import Path
UNIT='research/program_expansion_20261025/continuation_photon_20261027'
ROOT_HANDOFF='research/program_expansion_20261025/HANDOFF_KO.md'
ALLOWED={UNIT+'/'+x for x in ('RESULT.json','RESULTS_KO.md','HANDOFF_KO.md','DAG.json','LOOP_PROGRESS.json')}|{ROOT_HANDOFF}
def git(repo,*args):
 p=subprocess.run(['git','-C',str(repo),*args],capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace').strip())
 return p.stdout
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(obj):return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def create(path,data):
 if path.exists():
  if path.read_bytes()!=data:raise ValueError('Existing unequal artifact: '+str(path))
  return
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--source',required=True);parser.add_argument('--delivery',required=True);parser.add_argument('--output-directory',type=Path,required=True);a=parser.parse_args();repo=a.repo.resolve();d=a.delivery;BASE=a.source
 if not re.fullmatch('[0-9a-f]{40}',BASE):raise ValueError('Exact source commit SHA required')
 if not re.fullmatch('[0-9a-f]{40}',d) or git(repo,'rev-parse','HEAD').decode().strip()!=d:raise ValueError('Exact committed delivery HEAD required')
 git(repo,'merge-base','--is-ancestor',BASE,d)
 if git(repo,'rev-list','--parents','-n','1',d).decode().strip().split()!=[d,BASE]:raise ValueError('Delivery commit must be a direct single-parent child of S')
 tree=git(repo,'rev-parse',d+'^{tree}').decode().strip()
 raw=git(repo,'diff','--no-renames','--name-status','-z',BASE,d);fields=raw.split(b'\0');changes=[]
 if fields[-1]!=b'':raise ValueError('Malformed diff')
 fields=fields[:-1]
 if len(fields)%2:raise ValueError('Unexpected diff fields')
 for i in range(0,len(fields),2):
  status=fields[i].decode();name=fields[i+1].decode()
  if status not in {'A','M','D'}:raise ValueError('Unexpected change '+status)
  if name not in ALLOWED and not name.startswith(UNIT+'/delivery/'):raise ValueError('Non-delivery or scientific path changed: '+name)
  if name.lower().endswith('.pdf'):raise ValueError('PDF excluded')
  changes.append((status,name))
 if not changes:raise ValueError('Empty delivery delta')
 entries={}
 for row in git(repo,'ls-tree','-r','-z','--full-tree',d).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t',1);mode,kind,blob=meta.decode().split();entries[name.decode()]=(mode,kind,blob)
 files={};modes={};deleted=[]
 for status,name in changes:
  if status=='D':deleted.append(name);continue
  mode,kind,blob=entries[name]
  if kind!='blob' or mode not in {'100644','100755'}:raise ValueError('Non-regular file: '+name)
  data=git(repo,'show',d+':'+name)
  if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=blob:raise ValueError('Blob mismatch: '+name)
  files[name]=data;modes[name]=mode
 output=a.output_directory.resolve();output.mkdir(parents=True,exist_ok=True)
 bundle_name='BASS_HE_'+BASE[:8]+'_to_'+d[:8]+'.bundle'
 with tempfile.TemporaryDirectory(prefix='photon05_tail_',dir=output) as tmp:
  bp=Path(tmp)/bundle_name;git(repo,'bundle','create',str(bp),'HEAD','^'+BASE);git(repo,'bundle','verify',str(bp))
  if not any(x.split()[0]==d for x in git(repo,'bundle','list-heads',str(bp)).decode().splitlines()):raise ValueError('Bundle HEAD mismatch')
  bundle=bp.read_bytes()
 bm='_git/'+bundle_name;files[bm]=bundle;modes[bm]='100644'
 context={'schema':'HE_PHOTON05_DELIVERY_CONTEXT_V1','source_base':BASE,'delivery_commit':d,'delivery_tree':tree,'bundle_member':bm,'bundle_sha256':sha(bundle),'bundle_base_prerequisite':BASE,'source_published':False,'central_published':False,'restore':'Start from exact source S; apply changed files and listed deletions, or fetch the bundle into a Git repository containing S. Preserve all unspecified files. The external closeout records final D05 and tail backup ACKs.','scientific_executions':0}
 files['ARCHIVE_CONTEXT.json']=encode(context)
 manifest={'schema':'HE_PHOTON05_DELIVERY_MANIFEST_V1','source_base':BASE,'delivery_commit':d,'delivery_tree':tree,'changes':[{'status':s,'path':p} for s,p in changes],'deletions':deleted,'files':[{'path':name,'bytes':len(data),'sha256':sha(data),'git_blob':entries[name][2] if name in entries else None} for name,data in sorted(files.items())],'manifest_self_hash':'Excluded; bound by external receipt'}
 files['DELIVERY_MANIFEST.json']=encode(manifest)
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_STORED;info.external_attr=int(modes.get(name,'100644'),8)<<16;z.writestr(info,data)
 archive=buf.getvalue()
 with zipfile.ZipFile(io.BytesIO(archive)) as z:
  if z.testzip() is not None or z.namelist()!=sorted(files):raise ValueError('ZIP CRC/order mismatch')
  for name,data in files.items():
   saved=z.read(name)
   if len(saved)!=len(data) or sha(saved)!=sha(data):raise ValueError('ZIP member mismatch: '+name)
 name='BASS_HE_HE_EXP_PHOTON05_DELIVERY_20261027_'+d[:8]+'.zip';path=output/name
 receipt={'schema':'HE_PHOTON05_DELIVERY_RECEIPT_V1','status':'PASS_BASIC_DELTA_BUNDLE_ZIP_VERIFICATION','source_base':BASE,'delivery_commit':d,'delivery_tree':tree,'archive':{'filename':name,'bytes':len(archive),'sha256':sha(archive),'members':len(files)},'bundle':{'filename':bundle_name,'bytes':len(bundle),'sha256':sha(bundle),'base_prerequisite':BASE},'changed_paths':len(changes),'deletions':deleted,'checks':{'committed_blobs':True,'metadata_only_paths':True,'actual_git_bundle':True,'ZIP_STORED_sorted_fixeddate':True,'CRC_and_member_hashes':True},'scientific_executions':0,'external_writes':0,'builder_sha256':sha(Path(__file__).read_bytes())}
 create(path,archive);create(output/bundle_name,bundle);create(path.with_suffix('.manifest.json'),encode(manifest));create(path.with_suffix('.receipt.json'),encode(receipt));print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
