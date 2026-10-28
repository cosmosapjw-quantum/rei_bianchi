"""Separate numpy float64 full-C linear solve and 256-corner oracle.
No import from exact fraction core.
"""
import json,hashlib,itertools
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def reference():
    data=json.loads((ROOT/'source/FROZEN_BB13_SUPPORT_INPUT.json').read_text())
    z=np.asarray(data['z']); X=np.column_stack([np.ones(7),z-3.6]);C=np.asarray(data['covariance_dex_squared'])
    r=np.asarray(data['observed_dex'])-np.asarray(data['template_dex'])
    v=np.asarray(data['eos_response_dex']);l=np.asarray(data['jeans_smoothing_lower_dex']);h=np.asarray(data['jeans_smoothing_upper_dex'])
    L=np.linalg.cholesky(C);W=np.linalg.solve(L.T,np.linalg.solve(L,X))
    A=np.linalg.solve(X.T@W,W.T)
    vals=[]
    for theta in (-1.,1.):
        for bits in itertools.product((0,1),repeat=7):
            j=np.where(bits,h,l)
            vals.append(A@(r+theta*v+j))
    vals=np.asarray(vals)
    out={'kappa_min':float(np.min(vals[:,1])),'kappa_max':float(np.max(vals[:,1])),
         'beta_min':float(np.min(vals[:,0])),'beta_max':float(np.max(vals[:,0])),
         'A_kappa':list(map(float,A[1,:])),'num_corners':len(vals),
         'chi2_design_rank':int(np.linalg.matrix_rank(X)),
         'source':'numpy.linalg.cholesky+solve independent of exact rational core'}
    (ROOT/'results/NUMPY_REFERENCE.json').write_text(json.dumps(out,indent=2)+'\n')
    return out
if __name__=='__main__':print(reference())
