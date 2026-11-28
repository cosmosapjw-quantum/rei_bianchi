"""Two independent operator lanes on normalized prolate states (a_A,E_A units).

Direct lane differentiates the bright state in Cartesian coordinates.
Torque lane integrates Coulomb forces without differentiating a state.
Duffy patches resolve the two finite corner limits of the singular-force form.
No continuum or finite-R error enclosure follows from lane agreement alone.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss


def _compatible(g, b):
    if g.m != 0 or b.m != 1 or (g.R,g.ZA,g.ZB) != (b.R,b.ZA,b.ZB):
        raise ValueError('requires matched m=0 / bright |m|=1 states')
    if g.xi_max != b.xi_max:
        raise ValueError('states must use same finite prolate domain')


def _patches(g, b, order, duffy):
    if isinstance(order,bool) or not isinstance(order,int) or order < 2:
        raise ValueError('quadrature order must be integer >=2')
    xe=np.unique(np.r_[g._radial.edges,b._radial.edges])
    ye=np.unique(np.r_[g._angular.edges,b._angular.edges])
    q,w=leggauss(order); t=(q+1)/2; w=w/2
    T,U=np.meshgrid(t,t,indexing='ij'); W=w[:,None]*w[None,:]
    for i,(xl,xh) in enumerate(zip(xe[:-1],xe[1:])):
        for j,(yl,yh) in enumerate(zip(ye[:-1],ye[1:])):
            hx,hy=xh-xl,yh-yl
            corner=duffy and i==0 and j in (0,len(ye)-2)
            if corner:
                for a,bb in ((hx*T,hy*T*U),(hx*T*U,hy*T)):
                    eta=yl+bb if j==0 else yh-bb
                    yield (xl+a).ravel(),eta.ravel(),(hx*hy*T*W).ravel()
            else:
                yield (xl+hx*T).ravel(),(yl+hy*U).ravel(),(hx*hy*W).ravel()


def direct(g,b,order=12):
    """Lbar=L/(-i hbar), pbar=p_x/(-i hbar/a_A), dipole in a_A."""
    _compatible(g,b)
    c=g.R/2; midpoint=(g.ZA-g.ZB)*g.R/(2*(g.ZA+g.ZB))
    sums=np.zeros(6)
    for xi,eta,w in _patches(g,b,order,False):
        G,_,_=g.evaluate(xi,eta); A,Ax,Ae=b.evaluate(xi,eta)
        p=xi*xi-1; q=1-eta*eta
        rho=c*np.sqrt(p*q); z=c*xi*eta+midpoint
        rx=c*xi*np.sqrt(q/p); re=-c*eta*np.sqrt(p/q)
        zx=c*eta; ze=c*xi; det=rx*ze-re*zx
        Ar=(ze*Ax-zx*Ae)/det
        Az=(-re*Ax+rx*Ae)/det
        measure=w*g.R**3/8*(xi*xi-eta*eta)
        common=measure*G/np.sqrt(2)
        px=Ar+A/rho
        sums += [np.dot(common,z*px-rho*Az),
                 np.dot(common,(c*xi*eta-c)*px-rho*Az),
                 np.dot(common,px),np.dot(common,rho*A),
                 np.dot(measure,G*G),np.dot(measure,A*A)]
    return dict(zip(('L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b'),map(float,sums)))


def torque(g,b,order=16):
    """Independent Coulomb-force integrals TA,TB and commutator-derived Lbar.

    States are evaluated for values only in the mathematical integrand;
    evaluate also returns unused derivatives, which do not enter this lane.
    """
    _compatible(g,b)
    delta=b.energy-g.energy
    if not np.isfinite(delta) or delta <= 0:
        raise ValueError('positive isolated bright-ground gap required')
    TA=TB=0.
    for xi,eta,w in _patches(g,b,order,True):
        G=g.evaluate(xi,eta)[0]; A=b.evaluate(xi,eta)[0]
        rho=g.R/2*np.sqrt((xi*xi-1)*(1-eta*eta))
        ra=g.R/2*(xi+eta); rb=g.R/2*(xi-eta)
        common=w*g.R**3/8*(xi*xi-eta*eta)*rho*G*A/np.sqrt(2)
        TA+=np.sum(common/ra**3); TB+=np.sum(common/rb**3)
    CR=g.ZA*g.ZB*g.R/(g.ZA+g.ZB)
    return {'T_A':float(TA),'T_B':float(TB),'L_O_bar':float(CR*(TB-TA)/delta),
            'L_B_bar':float(-g.ZA*g.R*TA/delta),'gap':float(delta),'quadrature':'Duffy two corner cells + composite Gauss','order':order}


def invariants(g,b,d,t):
    delta=b.energy-g.energy
    lever=g.ZA*g.R/(g.ZA+g.ZB)
    return {'direct_torque_O_abs':abs(d['L_O_bar']-t['L_O_bar']),
            'direct_torque_B_abs':abs(d['L_B_bar']-t['L_B_bar']),
            'momentum_commutator_abs':abs(d['p_x_bar']-delta*d['dipole_x']),
            'origin_identity_abs':abs(d['L_O_bar']-d['L_B_bar']-lever*d['p_x_bar']),
            'norm_error_abs':max(abs(d['norm_g']-1),abs(d['norm_b']-1))}
