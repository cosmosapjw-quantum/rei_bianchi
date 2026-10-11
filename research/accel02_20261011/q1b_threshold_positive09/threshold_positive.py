"""Positive N/U fit with native-threshold probability panels; same closure."""
import math
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import brentq
from scipy.special import logsumexp

BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'q1b_source_entry04'))
from positive_entry import gauss
from reconstruction import reconstruct, opacity_moments
from opacity_native import THRESHOLDS_EV

def fit_threshold_positive(N,U,R,a,b,order):
    cell=reconstruct(N,U,R,a,b)
    if cell.status in ('EMPTY','ZERO_WIDTH_EMPTY'):
        return np.array([]),np.array([]),{'empty':True,'status':cell.status}
    if cell.status!='INTERIOR':raise ValueError('ENTRY_STRICT_CONE_REQUIRED')
    guard=opacity_moments(cell,lambda q:np.ones_like(q),orders=(64,128),rtol=1e-7)
    splits=sorted(set(float(E/R) for E in THRESHOLDS_EV if a<E/R<b))
    qedges=[a,*splits,b]
    vedges=[0.,*[cell.cdf(q) for q in splits],1.]
    x,w=gauss(order);nodes=[];provisional=[];panels=[]
    for left,right,vl,vr in zip(qedges[:-1],qedges[1:],vedges[:-1],vedges[1:]):
        if not left<right or not vl<vr:
            raise ArithmeticError('THRESHOLD_PANEL_PROBABILITY_UNRESOLVED')
        v=vl+(x+1)*(vr-vl)/2
        if np.any(v<=vl) or np.any(v>=vr):
            raise ArithmeticError('THRESHOLD_PANEL_PROBABILITY_UNRESOLVED')
        logq=cell.quantile_log(v);dq=a*np.expm1(logq);q=a+dq
        if np.any(q<=left) or np.any(q>=right):
            raise ArithmeticError('THRESHOLD_NODE_SIDE_UNRESOLVED')
        energy=R*q
        for E in THRESHOLDS_EV:
            boundary=float(E/R)
            if right<=boundary and np.any(energy>=E):
                raise ArithmeticError('THRESHOLD_NODE_SIDE_UNRESOLVED')
            if left>=boundary and np.any(energy<=E):
                raise ArithmeticError('THRESHOLD_NODE_SIDE_UNRESOLVED')
        nodes.append((q,dq/(b-a)));provisional.append(w*(vr-vl)/2)
        panels.append({'q_bounds':[left,right],'probability_bounds':[vl,vr],
                       'provisional_mass':vr-vl,'node_count':order})
    q=np.concatenate([row[0] for row in nodes]);xi=np.concatenate([row[1] for row in nodes]);w=np.concatenate(provisional)
    target=(cell.mean_q-a)/(b-a)
    if not xi.min()<target<xi.max():raise ValueError('ENTRY_MEAN_OUTSIDE_NODE_CONVEX_HULL')
    def weights(eta):
        lw=np.log(w)+eta*xi
        return np.exp(lw-logsumexp(lw))
    def f(eta):return float(weights(eta)@xi)-target
    lo,hi=-1.,1.
    for expansions in range(41):
        if f(lo)<=0<=f(hi):break
        if expansions==40:raise ArithmeticError('ENTRY_TILT_BRACKET_CAP')
        lo*=2;hi*=2
    eta,info=brentq(f,lo,hi,xtol=2e-13,rtol=1e-14,maxiter=160,full_output=True)
    p=N*weights(eta)
    nr=abs(math.fsum(p)-N)/N;qr=abs(math.fsum(q*p)-U/R)/(U/R)
    mr=abs(float((p/N)@xi)-target)
    if nr>1e-12 or qr>1e-12 or mr>1e-7 or np.any(p<=0) or not np.isfinite(p).all():
        raise ArithmeticError('ENTRY_POSITIVE_MOMENT_FIT_FAILED')
    for k,panel in enumerate(panels):panel['fitted_mass']=math.fsum(p[k*order:(k+1)*order])/N
    return q,p,{'status':cell.status,'p':cell.p,'panels':panels,'eta':eta,
                'iterations':info.iterations,'expansions':expansions,
                'N_residual':nr,'Q_residual':qr,'cell_mean_residual':mr,
                'coordinate_indicator':guard['float_q_coordinate_indicator'],
                'target_N':N,'target_U':U,'target_mean':cell.mean_q}
