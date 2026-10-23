#!/usr/bin/env python3
"""Stage only authorized task source; no Git writes or provider upload."""
import base64,hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];PUB=ROOT/'publish';PUB.mkdir(exist_ok=True)
selected=[]
for f in (ROOT/'assembly').iterdir():
 if f.is_file() and f.suffix in {'.py','.md','.json'} and not (f.name.endswith('_MANIFEST.json') or f.name.endswith('_PROVIDER_ACK.json') or f.name=='publication.json'):selected.append(f)
for area in ['atomic','thermal','rei','numerics']:
 for f in (ROOT/area).rglob('*'):
  if f.is_file() and (f.suffix=='.md' or 'sources' in f.relative_to(ROOT).parts or f.name.endswith('CONTRACTS.json') or f.name in {'INTEGRATION_EDGES.json','X1_WOLFRAM.json'}):selected.append(f)
for f in selected:
 target=PUB/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
refresh=json.loads((ROOT/'intake/PREPUBLISH_REFRESH.json').read_text());rows=[]
allowed={'repo','pr','head','branch','updated_at','state','draft','merged'}
for result in refresh:
 v=result.get('value',{});rows.append({k:v[k] for k in allowed if k in v})
(PUB/'CURRENT_REFRESH.json').write_text(json.dumps({'source':'intake/PREPUBLISH_REFRESH.json','scope':'Fresh PR metadata only; actual science status comes from source contracts and reviews','items':rows},ensure_ascii=False,indent=2)+'\n')
parts=['# 저장소별 복사용 인수인계\n\n각 블록은 해당 저장소 작업자에게 전달할 수 있다. 중앙 계획은 실행 허가나 예산 초기화가 아니다.\n']
for f in sorted((PUB/'assembly').glob('HANDOFF_*_KO.md')):
 parts.append('\n## '+f.stem+'\n\n````text\n'+f.read_text()+'\n````\n')
(PUB/'ALL_REPO_HANDOFFS_KO.md').write_text(''.join(parts))
entries=[];prefix='research/orchestration_longterm_20261023/'
for f in sorted(PUB.rglob('*')):
 if not f.is_file() or '__pycache__' in f.parts:continue
 b=f.read_bytes();entry={'repo_path':prefix+str(f.relative_to(PUB)),'mode':'100644','bytes':len(b),'git_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'sha256':hashlib.sha256(b).hexdigest()}
 try:entry['content']=b.decode('utf-8')
 except UnicodeDecodeError:entry['base64']=base64.b64encode(b).decode('ascii')
 entries.append(entry)
(ROOT/'assembly/publication.json').write_text(json.dumps({'files':entries},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'publication':str(ROOT/'assembly/publication.json'),'files':len(entries),'bytes':sum(e['bytes'] for e in entries)}))
