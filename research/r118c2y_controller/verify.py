import hashlib,json,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n in ('green','full_tests'):assert int((D/(n+'.exit')).read_text())==0,n
r=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;',(D/'full_tests.log').read_text())
assert sum(int(x[1]) for x in r)==349 and all(x[0]=='ok' and x[2]=='0' for x in r)
cases={}
for name in ('whole','iso','split','resume'):
 p=H/('bass_r118c2y_'+name);t=np.genfromtxt(p/'history.csv',delimiter=',',names=True)
 cfg=dict(x.split('=',1) for x in (p/'config.cfg').read_text().splitlines() if '=' in x)
 ret=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines() if '=' in x)
 assert np.all(np.diff(t['a'])>0) and np.all(t['local_error']<float(cfg['local_target']))
 assert max(abs(t['ledger']))<float(cfg['energy_budget_ev_per_h'])
 assert int(ret['rejected'])==1
 assert (ret['status']=='COMPLETE')==(name!='split')
 assert (D.parents[1]/'rust/rei_microphysics/src/external_controller.rs').read_text() in (p/'rei_source_identity.txt').read_text()
 du=np.diff(np.log(t['a']))
 cases[name]=dict(history_sha=sha(p/'history.csv'),return_=ret,config_sha=sha(p/'config.cfg'),max_error=float(max(t['local_error'])),min_du=float(min(du)),max_du=float(max(du)),max_ledger=float(max(abs(t['ledger']))))
a=H/'bass_r118c2y_split';b=H/'bass_r118c2y_resume';c=H/'bass_r118c2y_whole'
x=(a/'history.csv').read_bytes().splitlines(keepends=True);y=(b/'history.csv').read_bytes().splitlines(keepends=True)
assert x[-1]==y[1] and b''.join(x+y[2:])==(c/'history.csv').read_bytes()
assert all(sha(f)==sha(b/'checkpoint'/f.name) for f in (c/'checkpoint').iterdir())
out=dict(status='PASS_SCOPED_EXTERNAL_CONTROLLER_LIVE_RESTART',parent='77c6c809f9a07f0b312ee50a8ae1cf702541d250',full_rust_tests=349,cases=cases,restart_byte_identical=True,scope='z20 to18 actual live bridge; accepted local metric only, no global time convergence claim',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],cases['whole'])
