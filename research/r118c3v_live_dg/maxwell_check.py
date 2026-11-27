"""Conditional collisionless Maxwell current spectral tensor checks."""
import json,numpy as np
from numpy.polynomial.hermite import hermgauss
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 # Gaussian velocity independent longitudinal/transverse components; integrate
 # δ(ω-Qv_parallel) in units vth=1, Q=1.
 z,w=hermgauss(64);v=np.sqrt(2)*z;w=w/np.sqrt(np.pi)
 m=np.array([w.sum(),w@v,w@(v*v),w@(v**4)]);assert max(abs(m-[1,0,1,3]))<1e-13
 # conditional transverse current and density-current covariance at fixed ω.
 rows=[]
 for x in [-3,-1,0,1,3]:
  sn=np.exp(-x*x/2)/np.sqrt(2*np.pi);a=np.array([1,0,0,x]);M=sn*np.outer(a,a);M[1,1]=M[2,2]=sn
  ev=np.linalg.eigvalsh(M);assert ev[0]>-1e-15
  rows.append(dict(omega_over_Qv=x,S_nn=sn,continuity=float(np.max(abs(M[3]-x*M[0]))),min_eigenvalue=float(ev.min())))
 out=dict(moments=m.tolist(),rows=rows,scope='free-particle Maxwellian density/velocity spectral tensor, no self-consistent electromagnetic screening')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
