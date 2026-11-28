"""Source-only, manufactured event ledger; not a physical rate provider."""
from fractions import Fraction as F
A=F('3727.3794118')
M=F('1875.61294500')
E=F(330)
J=F(1602176634,10**28)*10**6
C=F(299792458)
K=(A+E)/2-M

def source(rate=None, source_class=None, direction=None, frame='TARGET_REST'):
    if frame!='TARGET_REST': raise ValueError('wrong frame')
    if rate is None:
        if source_class is not None: raise ValueError('unmatched source class')
        return {'physical':False,'R':None,'thermal':None,'L4':False}
    if source_class!='MANUFACTURED_TEST_ONLY' or type(rate) in (float,bool):
        raise ValueError('unqualified rate')
    r=F(rate)
    if r<0: raise ValueError('negative rate')
    n=None if direction is None else tuple(F(x) for x in direction)
    if n is not None and (len(n)!=3 or sum(x*x for x in n)!=1):
        raise ValueError('nonunit direction')
    heat=2*r*K*J
    rest=(2*M-A)*r*J
    photon=-E*r*J
    if heat+rest+photon!=0: raise ArithmeticError('energy')
    p=None if n is None else tuple(r*E*J*x/C for x in n)
    return {'R':r,'S_He':-r,'S_Dfast':2*r,'S_gamma':-r,
            'S_fast_kin_J_m3s':heat,'S_rest_J_m3s':rest,
            'S_gamma_J_m3s':photon,'residual_J_m3s':0,
            'S_D_momentum_N_m3':p,'S_gamma_momentum_N_m3':None if p is None else tuple(-x for x in p),
            'physical':False,'thermal':None,'L4':False}
