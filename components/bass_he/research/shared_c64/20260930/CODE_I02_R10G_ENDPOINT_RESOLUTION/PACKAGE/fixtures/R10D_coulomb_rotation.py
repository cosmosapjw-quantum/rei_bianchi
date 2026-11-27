"""Research-only Coulomb rotation derived from CPC Eq.(47).

No author FORTRAN is imported or translated. Let phi be the signed polar anomaly,
negative on approach and positive on recession. Repulsive Rutherford geometry is
R(phi)=rho**2/(-a+sqrt(a*a+rho*rho)*cos(phi)), a=Z1*Z2/(mu*v*v).
Conserved angular momentum gives dt/dphi=R**2/(rho*v). The axis angle used in
the straight-line clean-room convention is theta=pi/2-phi. With
A=exp(-i*theta*Lz) B, Eq.(47) becomes

i dB/dphi = epsilon*R(phi)**4/(rho*v)
             * (sin(phi)*Lx-cos(phi)*Ly)**2 B.

Use x=rho*tan(phi) to put both trajectories on the existing normalized x grid.
Then i dB/dx = epsilon/v * [R(phi)**2/(rho**2+x**2)]**2
                    * (x*Lx-rho*Ly)**2 B.
At a=0 the bracketed factor is exactly one and this reduces algebraically to
the existing straight-line Magnus generator. The same molecular-x basis and
|m_x| probability collapse are used. This is a research trajectory adapter,
not a production/default or physical-policy change.
"""
from __future__ import annotations
import math
import numpy as np
from bass_he.rotation import angular_operators
from arseny_reimpl.rotational import epsilon_rotational, molecular_x_basis, s_sigma_boundary
from arseny_reimpl.cross_section import projectile_velocity_au


def author_cutoff(l, Z1=1.0, Z2=2.0):
    if not isinstance(l, int) or l < 1 or not all(math.isfinite(float(x)) for x in (Z1,Z2)) or Z1+Z2<=0:
        raise ValueError('finite positive charges and integer l>=1 required')
    return (l+0.5)**2/(Z1+Z2)


def coulomb_rotation_batch(N,l,energies,rhos,*,steps=256,R_cut=None,mu=0.8,Z1=1.0,Z2=2.0,a_override=None):
    if not isinstance(steps,int) or steps<4 or not isinstance(l,int) or l<1 or N<=l:
        raise ValueError('valid N,l and integer steps>=4 required')
    E,r=np.broadcast_arrays(np.asarray(energies,float),np.asarray(rhos,float))
    E=E.ravel();r=r.ravel()
    if (not len(E) or np.any(~np.isfinite(E)) or np.any(~np.isfinite(r))
            or np.any(E<=0) or np.any(r<=0)):
        raise ValueError('finite energies>0 and rho>0 required; rho=0 needs a separate limit')
    cut=s_sigma_boundary(l,Z1,Z2) if R_cut is None else float(R_cut)
    if not math.isfinite(cut) or cut<=0 or not math.isfinite(mu) or mu<=0:
        raise ValueError('finite positive cutoff and reduced mass required')
    if a_override is not None and (not math.isfinite(float(a_override)) or a_override<0):
        raise ValueError('finite nonnegative a_override required')
    velocities=np.array([projectile_velocity_au(float(x)) for x in E])
    # DMP is supplied in atomic-mass units; velocity and trajectory use atomic
    # electron-mass units. This is the same 1836.153 convention in the CPC
    # energy/velocity conversion and reproduces the static a=0.067675 at 0.5.
    a=(Z1*Z2/(mu*1836.153*velocities**2) if a_override is None else
       np.full_like(velocities,float(a_override)))
    b=np.sqrt(a*a+r*r)
    rmin=a+b
    active=rmin<cut
    dim=2*l+1
    m=np.arange(-l,l+1)
    lx,ly,lz=angular_operators(l)
    U=np.broadcast_to(np.eye(dim,dtype=complex),(len(E),dim,dim)).copy()
    idx=np.flatnonzero(active)
    if len(idx):
        ra=r[idx];va=velocities[idx];aa=a[idx];bb=b[idx]
        arg=(aa+ra*ra/cut)/bb
        theta_max=np.arccos(np.clip(arg,-1.,1.))
        xmax=ra*np.tan(theta_max)
        h=2./steps
        eps=epsilon_rotational(N,l,Z1,Z2)
        lx2=lx@lx;ly2=ly@ly;cross=lx@ly+ly@lx
        Ua=np.zeros((len(idx),dim,dim),complex)
        for parity in (0,1):
            inds=np.flatnonzero((m-m[0])%2==parity)
            if not len(inds):continue
            L2x=lx2[np.ix_(inds,inds)]
            L2y=ly2[np.ix_(inds,inds)]
            C=cross[np.ix_(inds,inds)]
            W=np.broadcast_to(np.eye(len(inds),dtype=complex),
                              (len(idx),len(inds),len(inds))).copy()
            def generator(y):
                x=xmax*y
                den=ra*ra+x*x
                radius=ra*ra/(-aa+bb*ra/np.sqrt(den))
                weight=(radius*radius/den)**2
                op=x[:,None,None]**2*L2x-x[:,None,None]*ra[:,None,None]*C+ra[:,None,None]**2*L2y
                return (eps*xmax*weight/va)[:,None,None]*op
            for k in range(steps):
                mid=-1+(k+.5)*h
                shift=h/(2*np.sqrt(3))
                H1=generator(mid-shift);H2=generator(mid+shift)
                K=.5*h*(H1+H2)+1j*np.sqrt(3)*h*h/12*(H1@H2-H2@H1)
                ev,V=np.linalg.eigh(K)
                step=(V*np.exp(-1j*ev)[:,None,:])@V.conj().swapaxes(-2,-1)
                W=step@W
            Ua[:,inds[:,None],inds]=W
        theta_in=np.pi/2+theta_max
        theta_out=np.pi/2-theta_max
        gout=np.exp(-1j*theta_out[:,None]*m)
        gin=np.exp(1j*theta_in[:,None]*m)
        U[idx]=gout[:,:,None]*Ua*gin[:,None,:]
    _,Vx=molecular_x_basis(l)
    Ux=Vx.conj().T@U@Vx
    Ps=np.abs(Ux)**2
    C=(np.abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
    Pabs=(C@Ps@C.T)/C.sum(1)[None,None,:]
    return {'U_z':U,'U_mx':Ux,'P_signed':Ps,'P_abs':Pabs,
            'R_cut':cut,'Rmin':rmin,'coulomb_a':a,'entered':active,
            'steps':steps,'method':'EQ47_COULOMB_ANGLE_GAUGE_MAGNUS4_RESEARCH_ONLY'}
