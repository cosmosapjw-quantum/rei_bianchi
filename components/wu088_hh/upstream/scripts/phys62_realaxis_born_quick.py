"""PHYS62 positive-real-axis original noncentral P20-Q21 finite Born check.
Full scientific code, 46 tests and input in dual-cloud C5C8 source ZIP.
Finite GL8x64 over r=27..39, NOT a certified Z_S or full radial integral.
"""
import hashlib
import sys
import numpy as np
import mpmath as mp
from scipy.special import lpmv,gammaln
EXPECTED='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'

def screen(r,m):
    mu,w=np.polynomial.legendre.leggauss(64)
    ell=(20,21)
    b=[]
    for l in ell:
        norm=np.sqrt((2*l+1)/2*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))
        b.append(norm*lpmv(m,l,mu))
    s=np.sqrt(r*r+0.7**2-1.4*r*mu)
    return float(np.dot(w,2*(1+1/s)*np.exp(-2*s)*b[0]*b[1]))

def born(tau,m=0):
    xx,ww=np.polynomial.legendre.leggauss(8)
    k=mp.sqrt(mp.mpf(49)/100+1j*mp.mpf(tau));eta=-1/k
    hb={l:mp.coulombg(l,eta,k*27)+1j*mp.coulombf(l,eta,k*27) for l in (20,21)}
    val=0j
    for x,w in zip(xx,ww):
        r=float(33+6*x)
        p=[complex((mp.coulombg(l,eta,k*r)+1j*mp.coulombf(l,eta,k*r))/hb[l]) for l in (20,21)]
        val+=float(6*w)*p[0]*p[1]*screen(r,m)
    return val

def run(npz):
    if hashlib.sha256(open(npz,'rb').read()).hexdigest()!=EXPECTED:raise ValueError('original NPZ changed')
    with mp.workdps(35):
        a=born('0.01');b=born('0.002');c=born('0')
        assert abs(b-c)<abs(a-c) and c.real>0 and c.imag>0
        for t,v in [('0.01',a),('0.002',b),('0',c)]:
            print('tau=',t,'ReBorn_m0=',format(v.real,'.15e'),'ImBorn_m0=',format(v.imag,'.15e'))
    print('PASS_FIXED_CHANNEL_FINITE_GL_BORN_ONLY_NOT_FULL_ONSHELL_DTN')

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: script original_FROZEN_U_SUBSET.npz')
    run(sys.argv[1])
