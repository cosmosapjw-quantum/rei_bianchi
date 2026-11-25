import hashlib,json,re,gzip
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def frombits(s):return np.asarray([int(x,16) for x in s.split()],dtype=np.uint64).view(np.float64)
for n in ('green','negative','full_tests'):assert int((D/(n+'.exit')).read_text())==0
tests=re.findall(r'test result: (\w+)\. (\d+) passed; (\d+) failed; (\d+) ignored',(D/'full_tests.log').read_text());assert sum(int(x[1]) for x in tests)==348 and all(x[0]=='ok' for x in tests)
cases={}
for name in ('first','refined','split4','resume4'):
 root=H/('bass_r118c2x_'+name);p=root/'checkpoint'
 manifest=(p/'MANIFEST').read_text().splitlines();assert manifest[0]=='C2X_JOINT_V1'
 for line in manifest[3:]:
  h,f=line.split();assert sha(p/f)==h
 text=(p/'rei.txt').read_text();head,ident=text.split('\nGENERAL_SOURCE_IDENTITY\n',1);l=head.splitlines();assert len(l)==26 and l[0]=='AXBI_CHECKPOINT_V8_GENERAL'
 for f in ('general_history.rs','general_angular.rs','axbi_covariant_driver.rs','axbi_covariant_transport.rs'):assert (D.parents[1]/'rust/rei_microphysics/src'/f).read_text() in ident
 reg=frombits(l[24]);ref=reg[:9].reshape(3,3);r=reg[9:].reshape(-1,4);n=len(r);assert n==32 and min(r[:,3])>0
 points=frombits(l[25]).reshape(-1,11);a,h=points[-1,:2];f=points[-1,2:].reshape(3,3);assert np.all(np.diff(points[:,0])>0)
 v=np.fromstring(l[1],sep=' ');assert v[0]==a and np.all(v[3:6]>=0) and v[4]+v[5]<=1
 b=frombits((p/'bass.txt').read_text().splitlines()[2]);assert b[0]==a and b[1]==h and np.array_equal(b[8:17].reshape(3,3),f)
 vec=r[:,:3]@ref@np.linalg.inv(a*f);scale=np.linalg.norm(vec,axis=1);direction=vec/scale[:,None];s=np.repeat(scale,35)
 us=np.zeros(n*35);ns=np.zeros_like(us)
 for k,lo,hi in ((19,0,13.6),(4,13.6,24.59),(15,24.59,54.42),(11,54.42,np.inf)):
  nn,u,x,y=[np.fromstring(l[j],sep=' ') for j in range(k,k+4)]
  assert len(nn)==n*35 and min(nn)>=0 and np.all(u>=x*nn) and np.all(u<=y*nn)
  m=nn>0;assert np.all(x[m]*s[m]>=lo-1e-12) and np.all(y[m]*s[m]<=hi+1e-12)
  us+=u;ns+=nn
 U=us.reshape(n,35).sum(axis=1)*scale;P=np.einsum('a,ai,aj->ij',U,direction,direction)
 a0=np.genfromtxt(root/'history.csv',names=True,delimiter=',')[-1]
 assert abs(U.sum()-a0['J0'])<1e-14 and abs(P[1,2]-a0['Pyz'])<1e-14
 assert np.max(abs(U@direction))<1e-12*U.sum()
 assert abs(np.fromstring(l[3],sep=' ')[1]-a0['source'])<1e-14
 assert int(l[2].split()[0])==int(a0['accepted'])
 cases[name]=dict(raw=str(root),checkpoint_hashes={f.name:sha(f) for f in p.iterdir()},history_sha=sha(root/'history.csv'),accepted=int(a0['accepted']),z=float(a0['z']),J0=float(U.sum()),Pyz=float(P[1,2]),registry_sha=hashlib.sha256(l[24].encode()).hexdigest(),source_sha=hashlib.sha256(ident.encode()).hexdigest())
assert cases['refined']['checkpoint_hashes']==cases['resume4']['checkpoint_hashes']
assert len(set(c['registry_sha'] for c in cases.values()))==1
out=dict(status='PASS_SCOPED_V8_GENERAL_JOINT_RESTART',parent='3821603988d2e5a4a769b0a234aad6c419f2e43b',cases=cases,full_rust_tests=348,scope='exact compiled source/config/registry identity; reconstruct original registry then restore accepted interval; full coupled restart evidence in BASS; legacy FLRW checkpoint clock fields are compatibility sentinels, not general proper-time history',native_subagent='NOT_RUN')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print('verified four V8 checkpoints, moments and identities; 348 Rust tests')
