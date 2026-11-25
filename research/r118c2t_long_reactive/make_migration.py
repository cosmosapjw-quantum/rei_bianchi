import hashlib,json,sys
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
name=sys.argv[1];p=H/('rei_r118c2t_'+name+'_cont')
r=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines() if '=' in x)
assert r['status'] in ('STOPPED_NUMERICAL:InvalidInput("AXBI_COVARIANT_SOURCE_OUTSIDE_GRID")','STOPPED_SEGMENT_WALL_CAP')
for l in (D/(name+'.prefix.sha256')).read_text().splitlines():
 h,fn=l.split(maxsplit=1);assert sha(fn)==h
prior=json.loads((D.parent/'r118c2s_reactive/RESULTS.json').read_text())
assert sha(p/'source_identity.txt')==prior['source_sha']
assert (p/'config.cfg').read_bytes()==(D/(name+'.cfg')).read_bytes()
a=(p/'checkpoint.txt').read_text().splitlines();assert a[0]=='AXBI_CHECKPOINT_V7' and len(a)==23
v=a[1].split();c=a[2].split();hist=np.genfromtxt(p/'history.csv',names=True,delimiter=',');last=hist[-1]
assert float(v[0])==last['a'] and int(c[0])==int(last['accepted'])
changes={}
if r['status'].startswith('STOPPED_NUMERICAL'):
 # Only controller state resets; retain every attempted/rejected count.
 for i,k in [(7,'next_h'),(8,'root_error'),(9,'local_error')]:
  old=v[i];v[i]=format(last[k],'.17e');changes['clock_line_'+str(i)]=[old,v[i]]
 changes['consecutive_rejects']=[c[3],'0'];c[3]='0'
 assert float(v[7])>=1e-10
a[1]=' '.join(v);a[2]=' '.join(c)
out=D/(name+'.adjusted.ck');out.write_text('\n'.join(a)+'\n')
cfg=(p/'config.cfg').read_text();assert cfg.endswith('\n')
(D/(name+'.extended.cfg')).write_text(cfg+'reactive_extra_high_cells=3\n')
receipt=dict(status='EXPLICIT_GRID_EXTENSION_MIGRATION',original_status=r['status'],source_path=str(p),source_hashes={f:sha(p/f) for f in ('config.cfg','source_identity.txt','checkpoint.txt','history.csv','RETURN.txt')},adjusted_checkpoint_sha=sha(out),new_config_sha=sha(D/(name+'.extended.cfg')),controller_changes=changes)
(D/(name+'.migration_input.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
