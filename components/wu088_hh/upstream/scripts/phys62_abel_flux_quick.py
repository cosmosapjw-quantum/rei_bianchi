"""PHYS62 quick independent fixed-ell Coulomb Abel-current numerical check.
Full proof/tests/source frozen in dual-provider PHYS62 R5 source capsule.
Only central Coulomb reference at B=27, real energy E=49/200 Hartree.
"""
import hashlib
import sys
import mpmath as m
EXPECTED='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'

def wave(ell,tau):
    k=m.sqrt(m.mpf(49)/100+1j*tau)
    eta=-1/k
    r=k*27
    h=lambda l:m.coulombg(l,eta,r)+1j*m.coulombf(l,eta,r)
    z=k*(((ell+1)/r+eta/(ell+1))*h(ell)-m.sqrt(1+eta**2/(ell+1)**2)*h(ell+1))/h(ell)
    return m.im(z)

def run(source):
    if hashlib.sha256(open(source,'rb').read()).hexdigest()!=EXPECTED:raise ValueError('original frozen NPZ mismatch')
    with m.workdps(55):
        for l in (0,20,21):
            j=wave(l,0)
            f=m.coulombf(l,-m.mpf(10)/7,m.mpf(189)/10)
            g=m.coulombg(l,-m.mpf(10)/7,m.mpf(189)/10)
            target=(m.mpf(7)/10)/(f*f+g*g)
            assert abs(j-target)<m.mpf('1e-45')
            near=wave(l,m.mpf('0.0001'))
            assert j>0 and near>0
            print('ell=',l,'j0=',m.nstr(j,18),'j_tau0.0001=',m.nstr(near,18))
    print('PASS_SCOPED_FIXED_ELL_CENTRAL_COULOMB_NO_WEIGHTED_LAP_CLAIM')

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('use: python phys62_abel_flux_quick.py original.npz')
    run(sys.argv[1])
