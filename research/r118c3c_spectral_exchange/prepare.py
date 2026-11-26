import hashlib,json
import numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out={}
for n in ('table','fine','late_table'):
 p=H/('bass_r118c3b_'+n);r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'secondary_spectrum.csv',names=True,delimiter=',')
 assert np.array_equal(r['a'],s['a'])
 a=r['a'];am=np.sqrt(a[:-1]*a[1:]);birth=np.diff(s['FF_birth']);temp=np.diff(s['FF_T_moment'])/birth;tc=2.7255/am
 yhe=.245/(4*(1-.245));hii=(r['xHII'][1:]+r['xHII'][:-1])/2;heii=(r['xHeII'][1:]+r['xHeII'][:-1])/2;heiii=(r['xHeIII'][1:]+r['xHeIII'][:-1])/2;frac=4*yhe*heiii/(hii+yhe*heii+4*yhe*heiii)
 bb=s['BB_U'];v=np.c_[a[1:],temp,tc,frac,birth,bb[:-1],np.sqrt(bb[:-1]*bb[1:]),bb[1:]]
 assert min(v.ravel())>=0 and np.isfinite(v).all() and min(birth)>0
 q=D/(n+'_stages.csv');np.savetxt(q,v,delimiter=',',fmt='%.17e',header='a,T,Tcmb,z2frac,birth,BB0,BBmid,BB1',comments='')
 out[n]=dict(source={str(p/f):sha(p/f) for f in ('history.csv','secondary_spectrum.csv')},stages_sha=sha(q),n=len(v),actual_birth=float(s['FF_birth'][-1]),actual_absorption=float(s['FF_abs_birth'][-1]),actual_end_emission=float(s['FF_U'][-1]),actual_end_absorption=float(s['FF_abs_U'][-1]))
(D/'STAGES.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
