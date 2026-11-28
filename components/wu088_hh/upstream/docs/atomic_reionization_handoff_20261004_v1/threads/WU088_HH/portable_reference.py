"""Bounded HH external-rate reference; NOT a production provider or cosmology solver.
CGS inputs: T [K], n [cm^-3], chi [erg]. Supplied domain is explicit and mandatory.
LCS formula reproduces only T>3000 K Grackle analytic branch, with units=1.
The exact pinned tiny=1e-20 branch is preserved at units=1; it is discontinuous at 3000 K.
"""
import math

def rate(T, provider, domain):
    lo, hi = domain
    if not (math.isfinite(T) and 0 < lo <= T <= hi):
        raise ValueError('DOMAIN_VIOLATION')
    specs = {'LCS91': (1.2e-17, 1.2, 157800.), 'KS92_corrected_Glover15': (4.65e-21, 1.5, 157800.)}
    A,p,B = specs[provider]
    if provider == 'LCS91' and T <= 3000:
        return {'status':'GRACKLE_ARTIFICIAL_FLOOR_CGS_UNITS_1','k':1e-20,'dk_dT':None if T==3000 else 0.,'d2k_dT2':None if T==3000 else 0.}
    k=A*T**p*math.exp(-B/T)
    first=p/T+B/T**2
    return dict(status='ANALYTIC_BRANCH_REFERENCE', k=k, dk_dT=k*first,
                d2k_dT2=k*(first*first-p/T**2-2*B/T**3))

def source(nHI,k,chi):
    if not all(math.isfinite(x) and x>=0 for x in (nHI,k,chi)):
        raise ValueError('INVALID_INPUT')
    R=k*nHI*nHI
    return {'HI':-R,'HII':R,'e':R,'dn_part':R,'du_th':-chi*R,'du_binding':chi*R,'R':R}

def particle_temperature_source(npart,T,S,chi,kB):
    """Local chemistry contribution only; no expansion/other cooling terms."""
    if npart<=0 or kB<=0:raise ValueError('INVALID_INPUT')
    return 2*S['du_th']/(3*kB*npart)-T*S['dn_part']/npart

NU={'ionization':(-1,1,0,1),'ion_pair':(-2,1,1,0),'resonant_cx':(0,0,0,0),'elastic':(0,0,0,0),'spin_exchange':(0,0,0,0)}
