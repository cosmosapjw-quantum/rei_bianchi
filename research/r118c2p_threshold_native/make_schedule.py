import hashlib,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;I=D.parents[1]
j=json.loads((I/'research/r118c2n_spectral/Q256.json').read_text());raw=[]
for x in j['segments']:
 p=Path(x['raw_path'])/'history.csv'
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==x['hashes']['history.csv']
 raw.append(np.genfromtxt(p,names=True,delimiter=','))
r=np.concatenate([raw[0],raw[1][1:]])
for n in (256,512,1024):
 a=np.geomspace(1/21,.2,n+1);a[0]=1/21;a[-1]=.2;m=np.sqrt(a[:-1]*a[1:])
 keys=['x_HII','x_HeII','x_HeIII']
 d=np.column_stack([a[:-1],m,a[1:]]+[np.interp(m,r['a'],r[k]) for k in keys]+[np.interp(a[1:],r['a'],r[k]) for k in keys])
 np.savetxt(D/f'schedule{n}.csv',d,delimiter=',',header='a0,amid,a1,xmid,ymid,zmid,xend,yend,zend',comments='',fmt='%.17e')
