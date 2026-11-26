"""Source-owned event identity from native Ledgers, independent of temperature fit."""
import numpy as np,json,gzip,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
B=Path.home()/'worktrees/bass-r109-native-20261124/research/r118c3b_multistf'
H=D.parent/'r118c3g_spectral_cutoff/inputs/history.csv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def species_events(photo,ci,rr,dr,Y):
 v=np.asarray(photo)+np.asarray(ci)-np.asarray(rr);v=v.copy();v[...,1]-=dr
 return np.stack([v[...,0],(v[...,1]-v[...,2])/Y,v[...,2]/Y],axis=-1)
def transfer(src,u0,u1,work,boundary,cooling):
 absorbed=src-(u1-u0)-work-boundary
 return absorbed,absorbed-np.sum(cooling,axis=-1)
def archive():
 p=B/'table_checkpoint_rei.txt.gz';s=B/'table_secondary_spectrum.csv.gz'
 with gzip.open(p,'rt') as f:
  assert f.readline().strip()=='AXBI_CHECKPOINT_V10_GENERAL';state=np.fromstring(f.readline(),sep=' ');f.readline();L=np.fromstring(f.readline(),sep=' ')
 assert len(L)==24
 with gzip.open(s,'rt') as f:v=np.genfromtxt(f,names=True,delimiter=',')
 r=np.genfromtxt(H,names=True,delimiter=',');assert np.array_equal(v['a'],r['a'])
 F=np.stack([r[k] for k in ['xHII','xHeII','xHeIII']],axis=1);u=np.c_[F[:,0],F[:,1]+2*F[:,2]];z=np.linalg.lstsq(u,r['ne']*r['a']**3,rcond=None)[0];Y=z[1]/z[0]
 dx=F[-1]-F[0];pred=species_events(L[18:21],L[15:18],L[12:15],L[9],Y)
 co=np.array([v[k][-1]-v[k][0] for k in ['RR_H','RR_HeI','RR_HeII','DR','CE_H','CE_HeI','CE_HeII']]);ff=v['FF_birth'][-1]-v['FF_birth'][0]
 E,Q=transfer(L[1],r['J0'][0],r['J0'][-1],L[7],L[5],co)
 gas=(r['thermal'][-1]-r['thermal'][0])+(r['binding'][-1]-r['binding'][0])+L[6]
 out=dict(Y=float(Y),source=float(L[1]),absorbed=float(E),other=float(Q),cooling=co.tolist(),ff=float(ff),cmb=float(L[8]),gas=float(gas),gas_closure=float(gas-(Q+L[8]-ff)),species_delta=dx.tolist(),species_from_events=pred.tolist(),species_residual=(dx-pred).tolist(),source_sha=sha(p),history_sha=sha(H),spectrum_sha=sha(s))
 assert abs(out['gas_closure'])<1e-10 and max(abs(dx-pred))<1e-9
 return out
if __name__=='__main__':
 o=archive();(D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
