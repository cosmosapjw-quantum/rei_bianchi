import hashlib,json,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert int((D/'green.exit').read_text())==0 and int((D/'full_tests.exit').read_text())==0
r=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;', (D/'full_tests.log').read_text())
assert sum(int(x[1]) for x in r)==352 and all(x[0]=='ok' and x[2]=='0' for x in r)
cases={}
for n in ('short','long','split','resume'):
 p=H/('bass_r118c3a_'+n);s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',');r=np.genfromtxt(p/'history.csv',names=True,delimiter=',')
 assert np.array_equal(s['a'],r['a'])
 ck=p/'checkpoint/rei.txt';head,ident=ck.read_text().split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines()
 assert l[0]=='AXBI_CHECKPOINT_V9_GENERAL' and len(l)==27
 for f in ('igm_thermal.rs','axbi_covariant_driver.rs'):assert (D.parents[1]/'rust/rei_microphysics/src'/f).read_text() in ident
 v=np.fromstring(l[26],sep=' ');ledger=np.fromstring(l[3],sep=' ')
 assert len(v)==9 and np.array_equal(v,np.array([s[k][-1] for k in s.dtype.names[2:11]]))
 assert abs(v[:8].sum()/ledger[3]-1)<1e-11
 data=np.stack([s[k] for k in s.dtype.names[2:10]],axis=1);assert min(data.ravel())>=0 and np.all(np.diff(data,axis=0)>=0)
 cases[n]=dict(ck_sha=sha(ck),spectrum_sha=sha(p/'secondary_spectrum.csv'),channels=v[:8].tolist(),ff_Tmoment=float(v[8]),escape=float(ledger[3]),max_partition_relative=float(abs(v[:8].sum()/ledger[3]-1)))
assert cases['short']['ck_sha']==cases['resume']['ck_sha']
out=dict(status='PASS_SCOPED_V9_ACCEPTED_COOLING_CHANNELS',parent='8275bf964def38b30d0504a4612c8f2292a2612f',full_rust_tests=352,cases=cases,scope='actual accepted general chemistry RHS channels and checkpoint; no spectral atomic rate change',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],cases['long'])
