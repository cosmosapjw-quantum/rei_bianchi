from pathlib import Path
import json,math,hashlib
R=Path('/mnt/data/rei_iso_p3_work/REI_ISO_COUPLE_P3_20261017')
prefix='research/dossier_ssot_sandbox_20261016/iso_couple_p3_20261017/'
files=[]
for k in ['README_KO.md']:
 files.append(R/k)
for folder in ['contracts','docs','scripts']:
 files.extend(p for p in sorted((R/folder).rglob('*')) if p.is_file() and p.suffix in {'.md','.json','.py','.sh','.mmd'})
for p in sorted((R/'rust/rei_iso_couple_p3').rglob('*')):
 if p.is_file() and p.suffix in {'.rs','.toml','.lock'} and 'target' not in p.parts:files.append(p)
for p in sorted((R/'evidence').rglob('*')):
 if p.is_file() and p.suffix in {'.csv','.log'} and p.stat().st_size<125000 and p.name in {
  'p3_campaign.csv','p3_geometric_age.csv','p3_spectral_scan.csv','p3_deep_refinement.csv',
  'p3_positive_campaign_matched.csv','p3_positive_campaign_timeout_39_rows.csv',
  'p3_science_validation.log','p3_positive_campaign_completed.log','TESTS_68_FINAL.log',
  'CLIPPY_FINAL.log','FMT_FINAL.log','P3_REPLAY_EXECUTION.log','positive_first_try.log','positive_repair.log',
  'grey_3_group.log'}:files.append(p)
files=sorted(files,key=lambda p:str(p.relative_to(R)))
assert len(files)==len(set(files)),len(files)
part_size=10
for i in range(0,len(files),part_size):
 group=files[i:i+part_size]
 content={'schema':'rei.github.p3.public.textfiles.1','parent_commit':'b6551164bc192a2ba1f3458717b96e6fc2386c9c',
   'part':i//part_size+1,'parts_total':math.ceil(len(files)/part_size),
   'files':[{'path':prefix+p.relative_to(R).as_posix(),'content':p.read_text()} for p in group]}
 path=R.parent/f'REI_ISO_COUPLE_P3_GITHUB_PART_{content["part"]}.json';path.write_text(json.dumps(content,ensure_ascii=False,separators=(',',':')))
 print(content['part'],str(path),path.stat().st_size,len(group))
meta={'parts_total':math.ceil(len(files)/part_size),'files_total':len(files),'file_list':[str(p.relative_to(R)) for p in files],'parent_commit':'b6551164bc192a2ba1f3458717b96e6fc2386c9c'}
(R.parent/'REI_ISO_COUPLE_P3_GITHUB_PUBLICATION.json').write_text(json.dumps(meta,indent=2))
