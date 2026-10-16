"""Source-shape-matched, photo-only H/He birth-age/threshold reference.

Uses HE20's MD14 50,000-K truncated stellar spectral law, native Simpson32
source bin moments, and literal H/He rows of Verner et al. (1996) photo.dat.
Does not call Rust igm_point_rhs or infer recombination/OTS/Case A from photo-only.
The source *total* comes from HE20 original q=0, m=16, 128-step C8 intake;
constant-in-ln(a) stellar injection and isotropic birth angles are prescribed
new controlled approximations, not the original time-dependent R/J source.
All gas temperatures, densities and event stocks are per original H nucleus.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np

SPECIES = ('HI', 'HeI', 'HeII')
FITS = np.array([
    # E_th E_max E0 sigma0(Mb) ya P yw y0 y1, Verner 1996 first three donor rows
    [13.60, 5e4, 0.4298, 5.475e4, 32.88, 2.963, 0, 0, 0],
    [24.59, 5e4, 13.61, 9.492e2, 1.469, 3.188, 2.039, 0.4434, 2.136],
    [54.42, 5e4, 1.720, 1.369e4, 32.88, 2.963, 0, 0, 0],
], dtype=float)
FIT_CUTS = FITS[:,0]
# Distinct physical binding energies from original bass_cr C19 README/native HHeModel
BIND_EV = np.array([13.598434599702, 24.587389011, 54.41776])
EDGES_EV = (13.60, 24.59, 54.42, 100.0)
KB_ERG_K = 1.380649e-16
EV_ERG = 1.602176634e-12
C_CM_S = 2.99792458e10
KBT_EV = KB_ERG_K / EV_ERG * 50000.0
Y_HE = 0.2454/(4*(1-0.2454))
N_H_Z20 = 0.0017575700008892194  # cm^-3, CR69 frozen cold z20 nominal
SOURCE_N_PER_H = 3.45955703510212632e-6  # HE20 q0 m16 n128 native C8
H0_PER_S = 67.4e5/3.0856775814913673e24
OMEGA_M, OMEGA_R = 0.315, 9.2e-5
OMEGA_L = 1-OMEGA_M-OMEGA_R
A_BIRTH = 1.0/21.0
X_END = math.log(21.0/20.998)


def shape(energy_ev):
    E = np.asarray(energy_ev, dtype=float)
    with np.errstate(over='ignore', invalid='ignore'):
        v = E**2 / np.expm1(E/KBT_EV)
    return np.where(E >= 0, np.nan_to_num(v, nan=0., posinf=0.), 0.)


def simpson(lo,hi,power=0):
    if not(math.isfinite(lo) and math.isfinite(hi) and lo>0 and hi>=lo):
        raise ValueError('source interval')
    if lo==hi:return 0.
    z=np.linspace(lo,hi,33)
    w=np.array([1.]+[4. if i%2 else 2. for i in range(1,32)]+[1.])
    return float(((hi-lo)/96.)*np.dot(w, shape(z)*z**power))


@lru_cache(maxsize=15)
def cells(m):
    if type(m) is not int or not 1<=m<=1024:raise ValueError('m domain')
    v=[]
    for a,b in zip(EDGES_EV[:-1],EDGES_EV[1:]):
        for j in range(m):
            lo=a if j==0 else a*(b/a)**(j/m)
            hi=b if j+1==m else a*(b/a)**((j+1)/m)
            v.append((lo,hi,simpson(lo,hi),simpson(lo,hi,1)))
    return tuple(v)


def sigma_cm2(e_ev):
    """Verner 1996 Eq. (1), photoelectric Mb converted to cm^2."""
    E=np.asarray(e_ev,dtype=float)
    if np.any(~np.isfinite(E)) or np.any(E<0) or np.any(E>50000):
        raise ValueError('Verner photon energy domain')
    vals=[]
    for threshold,emax,e0,sigma0,ya,p,yw,y0,y1 in FITS:
        x=E/e0-y0
        y=np.sqrt(x*x+y1*y1)
        with np.errstate(over='ignore',divide='ignore',invalid='ignore'):
            res=sigma0*((x-1.)**2+yw*yw)*y**(.5*p-5.5)*np.power(1+np.sqrt(y/ya),-p)
        vals.append(np.where(E>=threshold,res*1e-18,0.))
    return np.stack(vals,axis=-1)


def redshift_factor(dx,mu,signed_s_over_h):
    """Non-tilted LRS Killing-energy factor with b_birth-b_now=-s/H*dx.

    Axis convention fixed in this isolated reference. q=s/H is signed.
    Both E and work are normal-comoving-frame quantities.
    """
    if not(-.5<signed_s_over_h<1) or not math.isfinite(dx) or dx<0:
        raise ValueError('restricted expanding LRS model')
    d=-signed_s_over_h*dx
    return math.exp(-dx)*np.sqrt((1-mu*mu)*math.exp(2*d)+mu*mu*math.exp(-4*d))


def redshift_vector(dx,mu,q):
    dx=np.asarray(dx,dtype=float)
    mu=np.asarray(mu,dtype=float)
    if np.any(dx<-1e-14) or not (-.5<q<1):raise ValueError("invalid photon-time direction")
    d=-q*dx
    return np.exp(-dx)*np.sqrt((1-mu*mu)*np.exp(2*d)+mu*mu*np.exp(-4*d))


def Hubble(x):
    a=A_BIRTH*math.exp(x)
    return H0_PER_S*math.sqrt(OMEGA_R/a**4+OMEGA_M/a**3+OMEGA_L)


def binding(g):
    x,y,z=g[:3]
    return BIND_EV[0]*x + Y_HE*(BIND_EV[1]*(y+z)+BIND_EV[2]*z)


def electrons(g):
    x,y,z=g[:3]
    return x + Y_HE*(y+2*z)


def temperature(g):
    return g[3]*EV_ERG/(1.5*KB_ERG_K*(1+Y_HE+electrons(g)))


def neutral(g):
    x,y,z=g[:3]
    return np.array([1-x, Y_HE*(1-y-z), Y_HE*y],dtype=float)


def admissible(g):
    x,y,z,u=g
    return bool(np.isfinite(g).all() and 0<=x<=1 and 0<=y and 0<=z and y+z<=1 and u>0)


def _spectral_nodes(m,birth_x,mu,step_mids,q,gl_order=4,threshold_split=True):
    """HE20 source-bin N and U retained via tiny positive linear weight tilt.

    Quadrature support is split at the preimages of each species cutoff for
    every later chemical midpoint. It is not retroactively inferred from N,U:
    the original *known* blackbody source density supplies the child weights.
    """
    xs,ws=np.polynomial.legendre.leggauss(gl_order)
    N0=sum(t[2] for t in cells(m))
    energies=[]; masses=[]; lowers=[]; uppers=[]
    for lo,hi,n,u in cells(m):
        bounds=[lo,hi]
        if threshold_split:
            for xm in step_mids:
                if xm<birth_x-1e-14:continue
                g=redshift_factor(float(xm-birth_x),mu,q)
                for cut in FIT_CUTS:
                    z=cut/g
                    if lo+1e-13<z<hi-1e-13:bounds.append(float(z))
        bounds=sorted(set(bounds))
        E=[];W=[];L=[];H=[]
        for a,b in zip(bounds[:-1],bounds[1:]):
            es=(a+b)/2+(b-a)*xs/2
            raw=shape(es)*ws*(b-a)/2
            E.extend(es);W.extend(raw);L.extend([a]*len(es));H.extend([b]*len(es))
        E=np.array(E);W=np.array(W)
        W*=n/math.fsum(W)
        mean=float(np.dot(W,E)/n)
        variance=float(np.dot(W,(E-mean)**2)/n)
        if variance<=0:raise ArithmeticError('degenerate source child')
        alpha=(u/n-mean)/variance
        correction=1+alpha*(E-mean)
        if np.min(correction)<=0:raise ArithmeticError('positive source weight tilt failed')
        W*=correction
        # adjust mass defect at largest support weight; energy discrepancy is
        # tiny, recorded by an independent source ledger below
        W[np.argmax(W)]+=n-math.fsum(W)
        if np.min(W)<0:raise ArithmeticError('negative source photon')
        energies.extend(E);masses.extend(W/N0);lowers.extend(L);uppers.extend(H)
    return np.array(energies),np.array(masses),np.array(lowers),np.array(uppers)


@dataclass
class Run:
    m: int
    steps: int
    q: float
    source_count: float
    absorbed: tuple[float,float,float]
    heat_ev: float
    work_photon_ev: float
    work_gas_ev: float
    photon_final_ev: float
    binding_delta_ev: float
    gas_u_final_ev: float
    initial_gas_u_ev: float
    gas_final: tuple[float,float,float,float]
    source_energy_ev: float
    max_newton_error: float
    number_defect: float
    energy_defect: float
    electron_defect: float
    source_shape_number_defect: float
    source_shape_energy_defect: float
    max_support_crossing: int


def run(m=8,steps=16,q=0.,source_count=SOURCE_N_PER_H,photons=True,threshold_split=True,
        initial=(1e-5,1e-5,0.,None),xend=X_END,gl_order=4) -> Run:
    if not(steps>=1 and 1<=m<=1024 and source_count>=0 and math.isfinite(source_count)):
        raise ValueError('run domain')
    ginit=list(initial)
    if ginit[3] is None:
        ne=ginit[0]+Y_HE*(ginit[1]+2*ginit[2])
        ginit[3]=1.5*KB_ERG_K*8.098143045064857*(1+Y_HE+ne)/EV_ERG
    gas=np.array(ginit,dtype=float)
    if not admissible(gas):raise ValueError('initial gas domain')
    B0=binding(gas); ne0=electrons(gas); u0=gas[3]
    mids=(np.arange(steps)+.5)*(xend/steps)
    # arrays accumulate all historical source cohorts, preserving birth age
    E0=np.empty(0);M=np.empty(0);XB=np.empty(0);MU=np.empty(0);Eold=np.empty(0)
    L0=np.empty(0);H0=np.empty(0)
    workp=workg=em_u=0.;A_total=np.zeros(3);Q_heat=0.
    n_em=0.;max_error=0.;shape_n=shape_u=0.;crossings=0
    ang,aw=np.polynomial.legendre.leggauss(8)
    aw=aw/2
    for istep,xm in enumerate(mids):
        xa=istep*xend/steps; xb=(istep+1)*xend/steps
        dx=xb-xa;dt=dx/Hubble(float(xm))
        # source and gas Strang midpoint steps
        um=gas[3]*math.exp(-dx)
        workg+=gas[3]-um
        gas[3]=um
        if M.size:
            Emid=E0*redshift_vector(xm-XB,MU,q)
            workp+=float(np.dot(M,Eold-Emid))
        else:Emid=np.empty(0)
        if photons and source_count>0:
            ec=[];mc=[];mu_list=[];lower=[];upper=[]
            for mu,w in zip(ang,aw):
                ee,ww,ll,hh=_spectral_nodes(m,float(xm),float(mu),mids[istep:],q,gl_order,threshold_split)
                ec.extend(ee);mc.extend(ww*(source_count/steps)*w);mu_list.extend([mu]*len(ee))
                lower.extend(ll);upper.extend(hh)
            ec=np.asarray(ec);mc=np.asarray(mc);mu_list=np.asarray(mu_list)
            E0=np.concatenate((E0,ec));M=np.concatenate((M,mc))
            XB=np.concatenate((XB,np.full(len(ec),float(xm))));MU=np.concatenate((MU,mu_list))
            L0=np.concatenate((L0,np.asarray(lower)));H0=np.concatenate((H0,np.asarray(upper)))
            Emid=np.concatenate((Emid,ec));
            Eold=np.concatenate((Emid[:len(Eold)],ec)) if len(Eold) else ec.copy()
            n_em+=math.fsum(mc)
            em_u+=float(np.dot(ec,mc))
            refn=source_count/steps
            refmean=sum(c[3] for c in cells(m))/sum(c[2] for c in cells(m))
            shape_n=max(shape_n,abs(math.fsum(mc)-refn))
            shape_u=max(shape_u,abs(np.dot(ec,mc)-refn*refmean))
        if M.size:
            geom=redshift_vector(xm-XB,MU,q)
            if threshold_split:
                for cut in FIT_CUTS:
                    crossings+=int(np.count_nonzero((L0*geom<cut*(1-2e-12))&(H0*geom>cut*(1+2e-12))&(M>0)))
            else:
                for cut in FIT_CUTS:
                    crossings+=int(np.count_nonzero((L0*geom<cut*(1-2e-12))&(H0*geom>cut*(1+2e-12))&(M>0)))
            rates0=sigma_cm2(Emid)
            lam0=C_CM_S*(N_H_Z20*math.exp(-3*xm))*rates0
            oldN=M.copy()
            gas_pre=gas.copy()
            trial=gas_pre.copy()
            for it in range(48):
                absorber=neutral(trial)
                lam=lam0*absorber[np.newaxis,:]
                total=lam.sum(axis=1)
                prob=-np.expm1(-total*dt)
                lost=oldN*prob
                shares=np.divide(lam,total[:,None],out=np.zeros_like(lam),where=total[:,None]>0)
                a=lost[:,None]*shares
                A=a.sum(axis=0)
                newgas=gas_pre.copy()
                newgas[0]+=A[0]
                newgas[1]+=(A[1]-A[2])/Y_HE
                newgas[2]+=A[2]/Y_HE
                heat=np.sum(a*(Emid[:,None]-BIND_EV[np.newaxis,:]))
                newgas[3]+=heat
                if not admissible(newgas):raise RuntimeError('unphysical gas branch')
                err=max(abs(newgas[0]-trial[0]),abs(newgas[1]-trial[1]),
                        abs(newgas[2]-trial[2]),abs(newgas[3]-trial[3])/max(u0,1e-6))
                if err<2e-13:
                    trial=newgas
                    break
                trial=.5*trial+.5*newgas
            else:raise RuntimeError('endpoint photo branch not converged')
            max_error=max(max_error,err)
            gas=trial
            M=oldN-lost
            A_total+=A
            Q_heat+=heat
            if np.min(M)<-1e-22:raise RuntimeError('negative photons')
            M=np.maximum(M,0.)
            # Physical support crossing measured before absorption at midpoint.
        Eend=E0*redshift_vector(xb-XB,MU,q) if M.size else np.empty(0)
        workp+=float(np.dot(M,Emid-Eend)) if M.size else 0.
        Eold=Eend
        ue=gas[3]*math.exp(-dx)
        workg+=gas[3]-ue
        gas[3]=ue
    ngamma=math.fsum(M)
    ugamma=float(np.dot(M,Eold)) if M.size else 0.
    number_defect=n_em-(ngamma+math.fsum(A_total))
    Bdelta=binding(gas)-B0
    energy_defect=(em_u+u0)-(ugamma+gas[3]+Bdelta+workp+workg)
    electron_defect=(electrons(gas)-ne0)-math.fsum(A_total)
    return Run(m,steps,q,n_em,tuple(map(float,A_total)),float(Q_heat),workp,workg,
               ugamma,Bdelta,float(gas[3]),u0,tuple(map(float,gas)),em_u,max_error,
               number_defect,energy_defect,electron_defect,shape_n,shape_u,crossings)
