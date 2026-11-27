"""Exactly gauge-regularized Eq47; parity-block batched fourth-order Magnus.

A=exp(-i theta Lz) B gives i dB/dx=(epsilon/v)(x Lx-rho Ly)^2 B.
This is an exact change of representation of the same small-R model, not a
new physical closure. Default R_cut is the inherited approximate S-series rule.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from arseny_reimpl.rotational import (angular_momentum_operators,epsilon_rotational,
    s_sigma_boundary,molecular_x_basis)
from arseny_reimpl.cross_section import projectile_velocity_au


@lru_cache(maxsize=16)
def angular_operators(l):
    m,lx,lz=angular_momentum_operators(l)
    ly=-1j*(lz@lx-lx@lz)
    # i Ly = [Lz,Lx]. Cache immutable matrices only.
    for a in (lx,ly,lz):a.flags.writeable=False
    return lx,ly,lz


def rotation_batch(N,l,energies,rhos,*,steps=32,R_cut=None):
    """Paired broadcast energies/rhos -> U and probability arrays (batch,d,d).

    `steps` is the number of uniform normalized-x Magnus steps, not legacy time
    midpoint steps. No empirical fit, row normalization or clipping is applied.
    Energy conversion remains the explicitly named legacy paper convention.
    """
    if not isinstance(steps,int) or steps<4:raise ValueError('integer steps >=4')
    if not isinstance(l,int) or l<1 or N<=l:raise ValueError('require 1<=l<N')
    E,r=np.broadcast_arrays(np.asarray(energies,float),np.asarray(rhos,float));E=E.ravel();r=r.ravel()
    if len(E)==0 or not np.all(np.isfinite(E)) or not np.all(np.isfinite(r)) or np.any(E<=0) or np.any(r<0):
        raise ValueError('finite energies>0 and rho>=0 required')
    cut=s_sigma_boundary(l) if R_cut is None else float(R_cut)
    if not np.isfinite(cut) or cut<=0:raise ValueError('finite positive R_cut required')
    dim=2*l+1;batch=len(E);lx,ly,lz=angular_operators(l);m=np.arange(-l,l+1)
    U=np.broadcast_to(np.eye(dim,dtype=complex),(batch,dim,dim)).copy()
    active=(r<cut)&(r>0);idx=np.flatnonzero(active)
    if len(idx):
        ra=r[idx];v=np.array([projectile_velocity_au(e) for e in E[idx]])
        xmax=np.sqrt(cut*cut-ra*ra);eps=epsilon_rotational(N,l)
        a2=(eps*xmax**3/v)[:,None,None]*(lx@lx)
        a1=(-eps*xmax*xmax*ra/v)[:,None,None]*(lx@ly+ly@lx)
        a0=(eps*xmax*ra*ra/v)[:,None,None]*(ly@ly)
        h=2./steps
        # Exact invariant parity subspaces; independent batched Hermitian eigensystems.
        Ub=np.zeros((len(idx),dim,dim),complex)
        for parity in (0,1):
            inds=np.flatnonzero((m-m[0])%2==parity)
            if len(inds)==0:continue
            A2=a2[:,inds,:][:,:,inds];A1=a1[:,inds,:][:,:,inds];A0=a0[:,inds,:][:,:,inds]
            W=np.broadcast_to(np.eye(len(inds),dtype=complex),(len(idx),len(inds),len(inds))).copy()
            for k in range(steps):
                mid=-1+(k+.5)*h;d=h/(2*np.sqrt(3));y1=mid-d;y2=mid+d
                H1=A2*y1*y1+A1*y1+A0;H2=A2*y2*y2+A1*y2+A0
                K=.5*h*(H1+H2)+1j*np.sqrt(3)*h*h/12*(H1@H2-H2@H1)
                ev,V=np.linalg.eigh(K);step=(V*np.exp(-1j*ev)[:,None,:])@V.conj().swapaxes(-2,-1)
                W=step@W
            Ub[:,inds[:,None],inds]=W
        # Return to rotating frame; endpoints fixed by trajectory, not fitted.
        theta_in=np.arctan2(ra,-xmax);theta_out=np.arctan2(ra,xmax)
        gout=np.exp(-1j*theta_out[:,None]*m);gin=np.exp(1j*theta_in[:,None]*m)
        U[idx]=gout[:,:,None]*Ub*gin[:,None,:]
    # At rho=0: exact smooth head-on limit. Signed sheets swap under the pi
    # rotation; the physically used |m_x| probabilities remain exactly identity.
    for i in np.flatnonzero(r==0):
        v=projectile_velocity_au(E[i]);phase=2*epsilon_rotational(N,l)*cut**3/(3*v)
        ev,V=np.linalg.eigh(lx@lx);B=(V*np.exp(-1j*phase*ev))@V.conj().T
        U[i]=B*np.exp(1j*np.pi*m)[None,:]
    _,Vx=molecular_x_basis(l);Ux=Vx.conj().T@U@Vx;Ps=np.abs(Ux)**2
    C=(np.abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
    deg=C.sum(1);Pabs=(C@Ps@C.T)/deg[None,None,:]
    return dict(U_z=U,U_mx=Ux,P_signed=Ps,P_abs=Pabs,R_cut=cut,
                entered=(r<cut),steps=steps,method='GAUGE_POLYNOMIAL_PARITY_MAGNUS4',
                velocity_policy='PAPER_LEGACY_27.07_1.836153')


def full_rotation_batch(Nmax,energies,rhos,*,steps=32,R_cut_scale=1.0):
    from arseny_reimpl.state_index import state_index
    E,r=np.broadcast_arrays(np.asarray(energies,float),np.asarray(rhos,float));E=E.ravel();r=r.ravel()
    if not np.isfinite(R_cut_scale) or R_cut_scale<=0:raise ValueError('finite positive R_cut_scale required')
    dim=state_index(Nmax,Nmax-1,Nmax-1)
    P=np.broadcast_to(np.eye(dim),(len(E),dim,dim)).copy()
    for N in range(2,Nmax+1):
        for l in range(1,N):
            inds=np.array([state_index(N,l,m)-1 for m in range(l+1)])
            block=rotation_batch(N,l,E,r,steps=steps,R_cut=s_sigma_boundary(l)*R_cut_scale)['P_abs']
            P[:,inds[:,None],inds]=block
    return P
