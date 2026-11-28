"""Two changed-backend solves compared to the immutable C1b l96 pair."""
import sys,json,resource
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'reference')]
from optimized_solver import solve
from fast_observables import direct_observables
from numpy.polynomial.legendre import leggauss

def main():
    folder=ROOT/'fixtures/C1B_B_l96';doc=json.loads((folder/'B_l96.json').read_text())
    selected=[];state_errors=[]
    for m in (0,1):
        s=solve(2.,m=m,lmax=96,elements=56,degree=4,quadrature=14,rmax=24.,nroots=2)
        with np.load(folder/f'B_l96_m{m}.npz',allow_pickle=False) as z:
            # Own class but exact accepted frozen coefficient input; same radial basis.
            old=type(s)(s.R,s.ZA,s.ZB,s.m,s.ls,s.boundaries,s.degree,z['coefficients'],doc['states'][m]['energy'],0.,1.,0.,s.metadata)
            q,w=leggauss(s.degree+2);total=0.
            for lo,hi in zip(s.boundaries[:-1],s.boundaries[1:]):
                jac=(hi-lo)/2;r=lo+jac*(q+1);d=s.radial(r)-old.radial(r)
                total+=np.sum(d*d*(w*jac))
            state_errors.append(float(np.sqrt(total)))
        selected.append(s)
    obs=direct_observables(*selected,14)
    ed=[abs(s.energy-doc['states'][m]['energy']) for m,s in enumerate(selected)]
    od={k:abs(obs[k]-v) for k,v in doc['direct'].items() if isinstance(v,float)}
    assert max(ed)<2e-10 and max(od.values())<2e-10 and max(state_errors)<2e-8
    assert max(s.residual for s in selected)<1e-9
    result={'status':'PASS','target_state_calls':2,'Ritz_roots':4,'energies':[s.energy for s in selected],'energy_abs_difference':ed,'state_L2_difference':state_errors,'observables':obs,'observables_abs_difference':od,'metadata':[s.metadata for s in selected],'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scope':'new native backend vs accepted frozen pair; no new continuum certificate'}
    (ROOT/'evidence/L96_NATIVE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='metadata'},indent=2))
if __name__=='__main__':main()
