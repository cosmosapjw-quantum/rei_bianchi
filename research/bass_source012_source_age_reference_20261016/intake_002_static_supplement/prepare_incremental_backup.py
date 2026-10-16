#!/usr/bin/env python3
"""Prepare exactly the committed incremental selection; no upload/Git mutation."""
import argparse,hashlib,io,json,re,subprocess,zipfile
from pathlib import Path
UNIT='research/bass_source012_source_age_reference_20261016/intake_002_static_supplement'
SELECTION=UNIT+'/PUBLIC_SELECTION.json'
CANON={f'research/flrw_covariant_transport_20261015/{n}.json' for n in ['LATEST_RESUME','HANDOFF','NEXT_DAG']}
CAP=4*1024*1024
GIT=['git','-c','core.packedGitWindowSize=32m','-c','core.packedGitLimit=64m']
def show(commit,path):return subprocess.check_output(GIT+['show',commit+':'+path])
def main():
 p=argparse.ArgumentParser();p.add_argument('--content-commit',required=True);p.add_argument('--archive-path',type=Path,required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.content_commit),'EXACT_CONTENT_SHA_REQUIRED';assert not a.archive_path.exists(),'EXCLUSIVE_ARCHIVE_REQUIRED';subprocess.run(GIT+['cat-file','-e',a.content_commit+'^{commit}'],check=True)
 selection_bytes=show(a.content_commit,SELECTION);selection=json.loads(selection_bytes);members=[('public/'+SELECTION,selection_bytes,None)];seen=set()
 for item in selection['files']:
  rel=item['path'];assert rel!=SELECTION and (rel.startswith(UNIT+'/') or rel.startswith('research/external_update_intake_20261016_001/refresh_006/') or rel in CANON),'NON_INCREMENTAL_MEMBER';assert '..' not in Path(rel).parts and not rel.startswith('/');assert rel not in seen;seen.add(rel);data=show(a.content_commit,rel);members.append(('public/'+rel,data,item['sha256']))
 meta=json.loads(show(a.content_commit,UNIT+'/repair_001/MANIFEST.json'));assert meta['status']=='STATIC_DEPENDENCY_BUNDLE_COMPLETE' and len(meta['files'])==2
 expected={'configs/rei_fastest_v1/science_scenario_v1.json','docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json'};assert {x['path'] for x in meta['files']}==expected
 for item in meta['files']:
  private=Path(item['private_path']);root=Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/static_supplement_001/repair_001');assert private==root/item['path'];data=private.read_bytes();assert len(data)==item['size_bytes'];members.append(('private_static/'+item['path'],data,item['copy_time_sha256']))
 manifest={'content_commit':a.content_commit,'selection':SELECTION,'members':[{'name':n,'bytes':len(d),'sha256':h} for n,d,h in members],'scope':'new public metadata plus exact two private static JSON copies only; excludes old409/oldarchive/fullraw/Git-source-payload'};manifest_data=json.dumps(manifest,indent=2).encode()+b'\n';members.append(('ARCHIVE_MANIFEST.json',manifest_data,None));stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,data,_ in members:z.writestr(name,data)
 payload=stream.getvalue();assert len(payload)<=CAP,'ARCHIVE_CAP_4MIB';a.archive_path.parent.mkdir(parents=True,exist_ok=True)
 with a.archive_path.open('xb') as f:f.write(payload)
 checks=[]
 with zipfile.ZipFile(a.archive_path) as z:
  assert len(z.infolist())==len(members)
  for name,original,expected_sha in members:
   decoded=z.read(name) # read verifies member CRC in the same pass
   digest=hashlib.sha256(decoded).hexdigest();assert len(decoded)==len(original)
   if expected_sha is not None:assert digest==expected_sha,'MEMBER_SHA_MISMATCH:'+name
   else:assert decoded==original
   checks.append({'name':name,'sha256':digest,'bytes':len(decoded),'CRC_verified':True})
 archive_sha=hashlib.sha256(a.archive_path.read_bytes()).hexdigest();print(json.dumps({'status':'INCREMENTAL_ARCHIVE_VERIFIED','content_commit':a.content_commit,'archive_path':str(a.archive_path),'archive_sha256':archive_sha,'archive_bytes':len(payload),'archive_cap_bytes':CAP,'members':len(checks),'public_members':len(selection['files'])+1,'private_static_members':2,'member_checks':checks,'upload_performed':False,'old_archive_read_or_rehashed':False,'git_mutation':False},indent=2))
if __name__=='__main__':main()
