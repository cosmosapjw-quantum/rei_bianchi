import json,hashlib,re
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n in ('download','green','quadrature','full_tests'):assert int((D/(n+'.exit')).read_text())==0
assert sha(D/'gauntff.dat')=='07312b2068393c39acac6fb7478003060210b936b0547e8569749a792b851cf7'
r=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed;', (D/'full_tests.log').read_text())
assert sum(int(x[1]) for x in r)==353 and all(x[0]=='ok' and x[2]=='0' for x in r)
q=np.genfromtxt(D/'quadrature.csv',names=True,delimiter=',');assert len(q)==384
quad={}
for mode in (1,2):
 v=q['ratio'][q['mode']==mode].reshape(-1,4);assert min(v.ravel())>0
 quad[str(mode)]=np.max(abs(v[:,:3]/v[:,3:]-1),axis=0).tolist()
assert quad['2'][1]<1e-5
cases={}
for n in ('off','grey','table','fine','fine_off','split','resume','late_table'):
 p=H/('bass_r118c3b_'+n);s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',');r=np.genfromtxt(p/'history.csv',names=True,delimiter=',')
 assert np.array_equal(s['a'],r['a'])
 ck=p/'checkpoint/rei.txt';head,ident=ck.read_text().split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines();assert l[0]=='AXBI_CHECKPOINT_V10_GENERAL' and len(l)==27
 for f in ('igm_thermal.rs','ff_balance.rs','axbi_covariant_driver.rs'):assert (D.parents[1]/'rust/rei_microphysics/src'/f).read_text() in ident
 assert (D/'gauntff.dat').read_text() in ident
 v=np.fromstring(l[26],sep=' ');led=np.fromstring(l[3],sep=' ')
 assert len(v)==10 and np.array_equal(v[:9],np.array([s[k][-1] for k in s.dtype.names[2:11]])) and v[9]==s['FF_abs_birth'][-1]
 assert abs(v[:8].sum()/led[3]-1)<1e-11 and np.all(np.diff(s['FF_abs_birth'])>=0)
 assert (v[9]==0)==(n in ('off','fine_off'))
 cases[n]=dict(ck_sha=sha(ck),history_sha=sha(p/'history.csv'),spectrum_sha=sha(p/'secondary_spectrum.csv'),ff_abs_ev=float(v[9]),gross_ff_ev=float(v[7]),gross_escape=float(led[3]),cmb_input=float(led[8]))
assert cases['table']['ck_sha']==cases['resume']['ck_sha']
out=dict(status='PASS_SCOPED_V10_PLANCK_FF_ABSORPTION',parent='52e7d84d47e1e85a8926755bdc130845e23cc4e0',full_rust_tests=353,gaunt_sha=sha(D/'gauntff.dat'),quadrature_max_rel=quad,cases=cases,scope='table spectral shape, legacy gross normalization, prescribed Planck absorption, no evolving spectral feedback',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],quad)
