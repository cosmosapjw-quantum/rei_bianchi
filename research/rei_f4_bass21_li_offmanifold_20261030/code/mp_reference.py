"""Different-arithmetic, 85-digit direct 21×21 source reconstruction (NO IVP)."""
from __future__ import annotations
import sys,json
from pathlib import Path
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import off_manifold as b
mp.mp.dps=85

def mf(x):
    p,q=float(x).as_integer_ratio()
    return mp.mpf(p)/mp.mpf(q)

def run():
    net,rows=b.load(); c=rows[0]; T=c['T_K'];uv=c['uv'];nb=mf(c['nb_m3'])
    Y=np.asarray(c['Y'],float).copy(); nu6=float(net.isotope_inventory['Li6'])
    Y[15]+=0.05*nu6; Y[16]-=0.05*nu6
    y=[mf(Y[i]) for i in b.RETAIN]; g=mf(net.isotope_inventory['Li6']/net.isotope_inventory['Li7'])
    full=[mf(z) for z in Y];lift=full.copy()
    for k in range(4):lift[13+k]=g*y[13+k]
    q=[int(z) for z in net.q]
    rates=net.rates(T,uv)
    G0=[[mf(v) for v in row] for row in rates['G0']+rates['D']]
    Grec=[[mf(v) for v in row] for row in rates['Gne']]
    def F(state):
        ne=nb*sum(q[i]*state[i] for i in range(21))
        return [sum(G0[i][j]*state[j] for j in range(21))+ne*sum(Grec[i][j]*state[j] for j in range(21)) for i in range(21)]
    FF=F(full);FL=F(lift)
    dd=[full[13+k]-g*full[17+k] for k in range(4)]
    e_delta=sum(k*dd[k] for k in range(4))
    forcing=[nb*e_delta*sum(Grec[i][int(b.RETAIN[k])]*y[k] for k in range(17)) for i in b.RETAIN]
    resid=[FF[int(b.RETAIN[k])]-FL[int(b.RETAIN[k])]-forcing[k] for k in range(17)]
    ne=nb*sum(q[i]*full[i] for i in range(21))
    ml=[[G0[13+i][13+j]+ne*Grec[13+i][13+j] for j in range(4)] for i in range(4)]
    dprime=[FF[13+i]-g*FF[17+i] for i in range(4)]
    want=[sum(ml[i][j]*dd[j] for j in range(4)) for i in range(4)]
    rdelta=[dprime[i]-want[i] for i in range(4)]
    scale=max(abs(t) for t in forcing)
    if max(abs(x) for x in resid)>mp.mpf('1e-70') or max(abs(x) for x in rdelta)>mp.mpf('1e-70'):
        raise AssertionError('MP_DIRECT_CHEMICAL_DEFECT_NOT_VERIFIED')
    return {'scenario':'BASS stored s00_m00_r00 with five-percent lithium-6 q3 -> q2 transfer',
        'perturbation_source':'preserves Li6 isotope inventory, positive charge states, no IVP',
        'precision_dps':mp.mp.dps,
        'delta_l1':mp.nstr(sum(abs(x) for x in dd),35),
        'qdelta':mp.nstr(e_delta,35),
        'forcing_max_abs_s_inverse':mp.nstr(scale,35),
        'retained_residual_max_abs':mp.nstr(max(abs(x) for x in resid),15),
        'Li4_derivative_residual_max_abs':mp.nstr(max(abs(x) for x in rdelta),15),
        'bound_source':'fully source-native rate matrices held fixed at one original BASS endpoint; not a real time evolution'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
