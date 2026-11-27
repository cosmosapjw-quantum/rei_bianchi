"""Changed assembly integration: compare matrices, states and direct observables."""
import sys,json,time,resource,hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'reference')]
import partialwave_centered as ref
import optimized_solver as opt
from fast_observables import direct_observables as fast_obs

def main():
    comparisons=[]; originals={}; optimized={}
    for m in (0,1):
        cfg=dict(R=2.,m=m,lmax=16,elements=24,degree=4,quadrature=14,rmax=24.,nroots=2)
        matrices={};eig=ref.eigsh
        def capture(H,**kw):
            matrices['refH']=H.copy();matrices['refM']=kw['M'].copy();return eig(H,**kw)
        ref.eigsh=capture
        try:g=ref.solve(**cfg)
        finally:ref.eigsh=eig
        def observe(H,M):matrices['newH']=H.copy();matrices['newM']=M.copy()
        b=opt.solve(**cfg,matrix_observer=observe)
        diff=matrices['newH']-matrices['refH'];mx=max(abs(diff.data),default=0.);rel=sparse.linalg.norm(diff)/sparse.linalg.norm(matrices['refH'])
        massdiff=sparse.linalg.norm(matrices['newM']-matrices['refM'])
        dc=(b.coefficients-g.coefficients)[:,1:-1].ravel();state=float(np.sqrt(max(0.,dc@(matrices['refM']@dc))))
        assert mx<2e-11 and rel<2e-13,(mx,rel)
        assert massdiff<1e-14,massdiff
        assert abs(b.energy-g.energy)<2e-10
        assert state<2e-8 and b.residual<1e-9 and abs(b.mass_norm-1)<1e-10
        comparisons.append({'config':cfg,'matrix_max_abs':float(mx),'matrix_relative_frobenius':float(rel),'mass_frobenius':float(massdiff),'energy_abs':abs(b.energy-g.energy),'state_mass_L2':state,'reference_energy':g.energy,'native_energy':b.energy,'residual':b.residual,'reference_seconds':g.metadata['elapsed_seconds'],'native_seconds':b.metadata['elapsed_seconds']})
        originals[m]=g;optimized[m]=b
    a=ref.direct_observables(originals[0],originals[1],14);b=fast_obs(optimized[0],optimized[1],14)
    diffs={k:abs(a[k]-b[k]) for k in a if isinstance(a[k],float)}
    assert max(diffs.values())<2e-10,diffs
    result={'status':'PASS','comparisons':comparisons,'direct_observables_abs_differences':diffs,'new_eigenstates':4,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scope':'implementation parity, not independent physical reference convergence','native_identity':opt.library_identity() if hasattr(opt,'library_identity') else optimized[0].metadata['native_library']}
    p=ROOT/'evidence/SOLVER_EQUIVALENCE.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='native_identity'},indent=2))
if __name__=='__main__':main()
