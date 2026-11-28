"""Archive exact committed source files; no scientific code is executed."""
import argparse,hashlib,json,subprocess,zipfile,time,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--stage',required=True);p.add_argument('--full',action='store_true');p.add_argument('--repo',help='Existing detached checkout to archive; no files are modified');a=p.parse_args()
if not re.fullmatch(r'S[0-9]{2}',a.stage):raise ValueError('INVALID_STAGE')
repo=Path(a.repo).resolve() if a.repo else Path(__file__).resolve().parents[3];leaf='research/provider_registry_molecular_r5_20261027';out=repo.parent/'deliverables';out.mkdir(exist_ok=True)
scopes=['AGENTS.md',leaf,'research/provider_registry_molecular_r4_20261027']
if a.full:scopes+=['research/provider_registry_20261025','research/provider_registry_network19_20261025','research/provider_registry_exfor_target6_20261027','research/program_expansion_20261025','research/rei_chem_ledger_20261025']
def git(*s):return subprocess.check_output(['git',*s],cwd=repo)
assert git('rev-parse','HEAD').decode().strip()==a.commit
entries=git('ls-tree','-r',a.commit,'--',*scopes).decode().splitlines();manifest={'schema':'WU_R5_EXACT_COMMIT_ARCHIVE_V1','source_commit':a.commit,'source_tree':git('rev-parse',a.commit+'^{tree}').decode().strip(),'stage':a.stage,'scope':'FULL_PORTABLE_PROVIDER_SOURCE' if a.full else 'CURRENT_R5_PLUS_R4_CUMULATIVE_CHECKPOINT_WITH_PINNED_PARENT_INPUTS','parent_recovery':'R3 archive SHA256 f83ea212e17318ea80d368f99f56a7e7dc0f908f2578392136acc434e22195ed supplies reused inputs when not full','members':[]}
name=f'WU_MOLECULAR_R5_{a.stage}_20261027_{a.commit[:12]}.zip';dest=out/name
r=repo.parent/'next_loop_20261027'/('WU_R5_'+a.stage+'_'+a.commit[:12]+'_ARCHIVE.json');r.parent.mkdir(exist_ok=True)
if dest.exists() or r.exists():raise ValueError('ARCHIVE_OR_RECEIPT_EXISTS_DO_NOT_OVERWRITE')
cpu=time.process_time();wall=time.monotonic()
with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for entry in entries:
  left,path=entry.split('\t',1);mode,kind,sha=left.split();assert kind=='blob';data=git('cat-file','blob',sha);z.writestr(path,data)
  manifest['members'].append({'path':path,'git_blob_sha1':sha,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'mode':mode})
 z.writestr('SOURCE_ARCHIVE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for row in manifest['members']:
  data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob_sha1']
receipt={'stage':a.stage,'source_commit':a.commit,'source_tree':manifest['source_tree'],'archive_name':name,'local_path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'members':len(entries)+1,'scope':manifest['scope'],'all_member_bytes_verified':True,'all_member_git_blobs_verified':True,'zip_CRC_ok':True,'packager_self_CPU_s':time.process_time()-cpu,'packager_wall_s':time.monotonic()-wall,'science_reexecution':0}
with r.open('x',encoding='utf-8') as receipt_file:receipt_file.write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
