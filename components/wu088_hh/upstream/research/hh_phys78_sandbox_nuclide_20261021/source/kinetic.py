"""Positive LRS canonical packets, prepared once per independent trajectory.

The massive cell rule follows the pinned REI198 CanonicalMomentumFV owner.
Massless angular packets use the same Killing-momentum transport, without an
angular-hierarchy truncation. This is finite quadrature, not a continuum bound.
Geometry: a_perp=a exp(-b), a_parallel=a exp(2b), sigma=(-s,-s,2s).
All returned energies/pressures are divided by their own initial energy.
"""
from __future__ import annotations

import math
import numpy as np
from numpy.polynomial.legendre import leggauss


class PreparedKinetic:
    def __init__(self, A_m=0., A_r=0., mass_over_Tref=30.,
                 radial_cells=12, angular_cells=12, gauss_order=3,
                 rad_ang_order=32):
        if not all(math.isfinite(float(v)) for v in (A_m,A_r,mass_over_Tref)):
            raise ValueError('nonfinite kinetic parameter')
        if not (-1 <= A_m <= 2 and -1 <= A_r <= 2):
            raise ValueError('positive angular distribution requires -1 <= A <= 2')
        if not 3 <= mass_over_Tref <= 1e5:
            raise ValueError('mass/Tref outside retained owner domain [3,1e5]')
        if not (isinstance(radial_cells,int) and 4 <= radial_cells <= 256
                and isinstance(angular_cells,int) and 4 <= angular_cells <= 128
                and gauss_order in (2,3,4) and 8 <= rad_ang_order <= 256):
            raise ValueError('unsupported finite quadrature')
        self.mass=float(mass_over_Tref)
        self.A_m=float(A_m); self.A_r=float(A_r)
        g,w=leggauss(gauss_order)
        rt=np.linspace(-1.,1.,radial_cells+1)
        at=np.linspace(-1.,1.,angular_cells+1)
        rh=np.diff(rt)/2; ah=np.diff(at)/2
        rr=((rt[:-1]+rh)[:,None]+rh[:,None]*g).ravel()
        mu=((at[:-1]+ah)[:,None]+ah[:,None]*g).ravel()
        rw=(rh[:,None]*w).ravel()
        aw=(ah[:,None]*w/2).ravel()
        q=3*(1+rr)/(1-rr)
        jac=6/(1-rr)**2
        fd=np.exp(-q)/(1+np.exp(-q))
        raw=rw[:,None]*jac[:,None]*q[:,None]**2*fd[:,None]
        raw=raw*(aw*(1+A_m*(3*mu**2-1)/2))[None,:]
        norm=float(np.sum(raw*np.hypot(self.mass,q)[:,None]))
        self.q2=q[:,None]**2
        self.mu2=mu[None,:]**2
        self.weights=raw/norm
        self.raw_weights=raw
        self.reference_energy_norm=norm
        rm,rw=leggauss(rad_ang_order)
        self.rmu2=rm**2
        self.rweights=rw/2*(1+A_r*(3*rm**2-1)/2)
        self.rweights=self.rweights/np.sum(self.rweights)
        self.packet_count=raw.size
        self.rad_packet_count=rm.size
        for a in (self.q2,self.mu2,self.weights,self.raw_weights,
                  self.rmu2,self.rweights):
            if not np.isfinite(a).all() or np.any(a<0):
                raise ValueError('nonfinite or negative prepared packet')
            a.flags.writeable=False

    def moments(self,x,b):
        """One square root per massive packet; all stress components share it."""
        if not (math.isfinite(x) and math.isfinite(b) and abs(x)<10 and abs(b)<3):
            raise ValueError('outside finite kinetic chart')
        r=math.exp(-x); ep=math.exp(2*b); ez=math.exp(-4*b)
        pp2=r*r*self.q2*ep*(1-self.mu2)
        pz2=r*r*self.q2*ez*self.mu2
        energy=np.sqrt(self.mass*self.mass+pp2+pz2)
        weighted=self.weights*r**3
        rho=float(np.sum(weighted*energy))
        # Share inverse energy, preserving signed difference before norm.
        we=weighted/energy
        pperp=float(np.sum(we*pp2)*.5)
        pparallel=float(np.sum(we*pz2))
        rp=ep*(1-self.rmu2); rz=ez*self.rmu2
        er=np.sqrt(rp+rz)
        rw=self.rweights*r**4
        rhor=float(np.sum(rw*er))
        rpp=float(np.sum(rw*rp/er)*.5)
        rpa=float(np.sum(rw*rz/er))
        return {'rho_m':rho,'pbar_m':(2*pperp+pparallel)/3,
                'pi_m':(pparallel-pperp)/3,
                'rho_r':rhor,'pbar_r':rhor/3,
                'pi_r':(rpa-rpp)/3,
                'pperp_m':pperp,'pparallel_m':pparallel,
                'pperp_r':rpp,'pparallel_r':rpa}

    def moments_batch(self,x,b,chunk=24):
        """Bounded NumPy vectorization for saved-trajectory output only."""
        x=np.asarray(x,dtype=float); b=np.asarray(b,dtype=float)
        if (x.ndim!=1 or b.shape!=x.shape or not np.isfinite(x).all()
                or not np.isfinite(b).all() or np.any(abs(x)>=10)
                or np.any(abs(b)>=3) or not 1<=chunk<=128):
            raise ValueError('invalid moment batch')
        keys=('rho_m','pbar_m','pi_m','rho_r','pbar_r','pi_r')
        out={k:np.empty(x.size) for k in keys}
        for start in range(0,x.size,chunk):
            sl=slice(start,min(x.size,start+chunk))
            r=np.exp(-x[sl])[:,None,None]
            ep=np.exp(2*b[sl])[:,None,None]
            ez=np.exp(-4*b[sl])[:,None,None]
            pp2=r*r*self.q2[None,:,:]*ep*(1-self.mu2[None,:,:])
            pz2=r*r*self.q2[None,:,:]*ez*self.mu2[None,:,:]
            en=np.sqrt(self.mass*self.mass+pp2+pz2)
            w=self.weights[None,:,:]*r**3
            pp=(w*pp2/en).sum((1,2))*.5
            pa=(w*pz2/en).sum((1,2))
            out['rho_m'][sl]=(w*en).sum((1,2))
            out['pbar_m'][sl]=(2*pp+pa)/3
            out['pi_m'][sl]=(pa-pp)/3
            rp=ep[:,0,:]*(1-self.rmu2)[None,:]
            rz=ez[:,0,:]*self.rmu2[None,:]
            er=np.sqrt(rp+rz)
            rw=self.rweights[None,:]*r[:,0,:]**4
            rr=(rw*er).sum(1)
            out['rho_r'][sl]=rr; out['pbar_r'][sl]=rr/3
            out['pi_r'][sl]=((rw*rz/er).sum(1)-(rw*rp/er).sum(1)/2)/3
        return out

    def continuity(self,x,b,w):
        """Exact directional energy derivative for this finite packet model."""
        m=self.moments(x,b)
        return {'rho_m_prime':-3*(m['rho_m']+m['pbar_m'])-6*w*m['pi_m'],
                'rho_r_prime':-4*m['rho_r']-6*w*m['pi_r']}
