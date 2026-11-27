"""Value-only Coulomb-force projection, independent of direct derivatives/gap.

Angular integration by parts is exact for the finite spherical expansion.
Assembly uses potential multipoles; this is not independent state evidence.
"""
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss,legvander
from partialwave_centered import angular

@lru_cache(maxsize=8)
def angular_force_moments(lg_tuple,lb_tuple):
    lg=np.array(lg_tuple);lb=np.array(lb_tuple);nmax=int(max(lg)+max(lb))
    eta,w=leggauss(nmax+3);s=np.sqrt(1-eta*eta)
    Ag=np.stack([angular(int(l),0,eta) for l in lg])
    dAg=np.stack([angular(int(l),0,eta,True) for l in lg])
    Ab=np.stack([angular(int(l),1,eta) for l in lb])
    dAb=np.stack([angular(int(l),1,eta,True) for l in lb])
    Q=Ag[:,None,:]*Ab[None,:,:]*s
    dQ=(dAg[:,None,:]*Ab[None,:,:]*s+Ag[:,None,:]*dAb[None,:,:]*s
        -Ag[:,None,:]*Ab[None,:,:]*(eta/s))
    P=legvander(eta,nmax)
    K=np.einsum('lkq,qn,q->nlk',dQ,P,w,optimize=True)
    C=np.einsum('lkq,q->lk',Q,w)
    # Polynomial degree and parity are exact; remove structurally absent moments.
    for i,l in enumerate(lg):
        for j,k in enumerate(lb):
            orders=np.arange(nmax+1)
            K[(orders>l+k)|((orders+l+k)%2==1),i,j]=0.
            if abs(l-k)!=1:C[i,j]=0.
    return C,K


def force_integrals(g,b,quadrature=22):
    """Return T_A,T_B. No energy/gap, direct L or momentum enters the integral."""
    if g.m!=0 or b.m!=1 or (g.R,g.ZA,g.ZB)!=(b.R,b.ZA,b.ZB):
        raise ValueError('requires compatible ground/bright states')
    if g.metadata['origin_center']!=b.metadata['origin_center'] or g.boundaries[-1]!=b.boundaries[-1]:
        raise ValueError('requires a common numerical origin and outer boundary')
    if isinstance(quadrature,bool) or not isinstance(quadrature,int) or quadrature<4:
        raise ValueError('quadrature must be integer >=4')
    positions=np.asarray(g.metadata['nuclear_positions'],float)
    charges=(g.ZA,g.ZB)
    C,K=angular_force_moments(tuple(g.ls),tuple(b.ls))
    orders=np.arange(K.shape[0]); q,w=leggauss(quadrature)
    bounds=np.unique(np.r_[g.boundaries,b.boundaries,np.abs(positions)])
    total=np.zeros(2)
    for lo,hi in zip(bounds[:-1],bounds[1:]):
        jac=(hi-lo)/2;r=lo+jac*(q+1)
        ug,ub=g.radial(r),b.radial(r)
        for idx,(charge,a) in enumerate(zip(charges,positions)):
            if a==0:
                val=np.einsum('lr,kr,lk->r',ug,ub,C,optimize=True)/r**2/np.sqrt(2)
            else:
                rad=abs(a)
                multipoles=-(charge/np.maximum(r,rad))[:,None]*(np.minimum(r,rad)/np.maximum(r,rad))[:,None]**orders*np.sign(a)**orders
                val=np.einsum('lr,kr,nlk,rn->r',ug,ub,K,multipoles,optimize=True)/(np.sqrt(2)*charge*a)
            total[idx]+=np.dot(w*jac,val)
    return {'T_A':float(total[0]),'T_B':float(total[1]),'radial_quadrature':quadrature,
            'angular_method':'finite polynomial integration-by-parts moments, exact degree selection'}


def torque_observables(g,b,quadrature=22):
    f=force_integrals(g,b,quadrature)
    delta=b.energy-g.energy
    if not np.isfinite(delta) or delta<=0:raise ValueError('positive pair gap required')
    R,ZA,ZB=g.R,g.ZA,g.ZB
    CR=ZA*ZB*R/(ZA+ZB)
    f.update(L_O_bar=CR*(f['T_B']-f['T_A'])/delta,
             L_B_bar=-ZA*R*f['T_A']/delta,p_x_force_bar=(ZA*f['T_A']+ZB*f['T_B'])/delta,gap=delta)
    # Finite Dirichlet sphere boundary correction; not a continuum enclosure.
    C,_=angular_force_moments(tuple(g.ls),tuple(b.ls))
    ugp=g.radial(np.array(g.boundaries[-1]),True)
    ubp=b.radial(np.array(b.boundaries[-1]),True)
    surf=float(ugp@C@ubp/np.sqrt(2))
    shift=ZA*R/(ZA+ZB) if g.metadata['origin_center']=='B' else 0.
    f.update(boundary_surface_x=surf,boundary_L_O_minus_torque_prediction=shift*surf/(2*delta))
    return f
