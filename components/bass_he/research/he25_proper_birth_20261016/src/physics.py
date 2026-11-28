"""HE25 physical semi-discrete system on immutable Killing momenta.

Binary64, per total H; proper seconds. Isotropic BB50K source is pushed into
fixed momentum cells at the actual time of birth, never assigned midpoint k.
"""
from pathlib import Path
import sys,math
import numpy as np
from scipy.integrate import quad,solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'he23_density_contract_20261016/src'))
from he21_photo import (A_BIRTH,X_END,SOURCE_N_PER_H,Hubble,shape,sigma_cm2,
    Y_HE,EV_ERG,KB_ERG_K,BIND_EV,FITS,C_CM_S,binding,electrons,temperature,neutral,admissible)
LEDGER=['birth_n','birth_e','a_hi','a_hei','a_heii','heat_hi','heat_hei','heat_heii',
        'escape','cmb','work_p','work_g','ci_hi','ci_hei','ci_heii','rr_hi','rr_hei','rr_heii','dr']

def frozen_duhamel(old,source,lam,dt):
    old,source,lam=np.broadcast_arrays(np.asarray(old,float),np.asarray(source,float),np.asarray(lam,float))
    if np.any(old<0) or np.any(source<0) or np.any(lam<0) or dt<=0:raise ValueError('DUHAMEL_DOMAIN')
    tau=lam*dt;phi=np.ones_like(tau)
    np.divide(-np.expm1(-tau),tau,out=phi,where=tau!=0)
    survive=old*np.exp(-tau)+source*dt*phi
    absorbed=old*(-np.expm1(-tau))+source*dt*(1-phi)
    return survive,absorbed

class Model:
    def __init__(self,owner,m=4,angles=4,q=0.,source_count=SOURCE_N_PER_H):
        if m not in [4,8,16] or angles not in [4,8,16,32] or q not in [-.005,0.,.005]:raise ValueError('HE25_SCOPE')
        self.owner=owner;self.m=m;self.angles=angles;self.q=q
        self.source_count=source_count;self.source_per_x=source_count/X_END
        self.t_end=quad(lambda x:1/Hubble(x),0,X_END,epsabs=.0001,epsrel=3e-14)[0]
        # Geometry-only clock is independently checked against proper-time quadrature.
        clock=solve_ivp(lambda t,x:[Hubble(float(x[0]))],(0,self.t_end),[0.],method='DOP853',rtol=3e-14,atol=1e-18,dense_output=True,max_step=self.t_end/8)
        if not clock.success:raise RuntimeError('CLOCK_FAILURE')
        self._clock=clock.sol
        mus,mw=np.polynomial.legendre.leggauss(angles);eg,ew=np.polynomial.legendre.leggauss(4)
        es=[];mm=[];ww=[]
        for mu,aw in zip(mus,mw/2):
            g=self.factor(X_END,mu)
            # Exact preimages at both interval ends isolate moving cutoffs/source edges.
            bounds=sorted(set([13.6,24.59,54.42,100.,13.6/g,24.59/g,54.42/g,100./g]))
            for lo,hi in zip(bounds[:-1],bounds[1:]):
                parts=m if hi/lo>1.01 else 1
                edges=np.geomspace(lo,hi,parts+1)
                for a,b in zip(edges[:-1],edges[1:]):
                    ee=(a+b)/2+(b-a)*eg/2
                    es.extend(ee);mm.extend([mu]*len(ee));ww.extend(ew*(b-a)/2*aw)
        self.Eref=np.array(es);self.mu0=np.array(mm);self.weights=np.array(ww);self.K=len(es)
        self.k_perp=A_BIRTH*self.Eref*np.sqrt(1-self.mu0**2)
        self.k_parallel=A_BIRTH*self.Eref*self.mu0
        times=[]
        for E,mu in zip(self.Eref,self.mu0):
            for cut in [13.6,24.59,54.42,100.]:
                if E>cut and E*self.factor(X_END,mu)<cut:
                    root=brentq(lambda x:E*self.factor(x,mu)-cut,0,X_END,xtol=1e-19,rtol=1e-14)
                    times.append(quad(lambda x:1/Hubble(x),0,root,epsabs=.0001,epsrel=3e-14)[0])
        self.breakpoints=sorted(set(times))
        self.g0=np.array([1e-5,1e-5,0.,0.])
        self.g0[3]=1.5*KB_ERG_K*8.098143045064857*(1+Y_HE+electrons(self.g0))/EV_ERG
        # Scale only conditions the independent ODE, not physical precision.
        ps=source_count*self.weights*shape(self.Eref)
        if ps.sum()>0:ps=ps/ps.sum()*max(source_count,1e-12)
        else:ps=self.weights/self.weights.sum()*1e-12
        self.scale=np.r_[1e-5,1e-5,1e-12,self.g0[3],np.maximum(ps,1e-18),
                          [max(source_count,1e-12),max(source_count*25,1e-11)],
                          np.full(3,max(source_count,1e-12)),np.full(3,max(source_count*10,1e-11)),
                          [1e-9,1e-9,1e-10,1e-6],np.full(3,1e-10),np.full(3,1e-10),1e-10]
        self.last_native=None
        self._source_mask=None;self._sigma_mask=None
    def factor(self,x,mu):
        return np.sqrt((1-np.asarray(mu)**2)*np.exp(-2*(1+self.q)*x)+np.asarray(mu)**2*np.exp(-2*(1-2*self.q)*x))
    def x(self,t):
        if t==0:return 0.
        if t==self.t_end:return X_END
        return float(self._clock(t)[0])
    def H(self,t):return Hubble(self.x(t))
    def geometry(self,t):
        x=self.x(t);G=self.factor(x,self.mu0)
        E=self.Eref*G;mu=self.mu0*np.exp(-(1-2*self.q)*x)/G
        return E,mu,-self.H(t)*(1+self.q*(1-3*mu**2))*E
    def source(self,t):
        x=self.x(t);G=self.factor(x,self.mu0);E=self.Eref*G
        # dE_b/dEref * dmu_b/dmu0 = A_parallel A_perp^2 / G^2.
        jac=np.exp(-3*x)/G**2
        mask=((E>=13.6)&(E<=100.)) if self._source_mask is None else self._source_mask
        raw=self.weights*shape(E)*jac*mask
        total=float(raw.sum())
        if total<=0:raise RuntimeError('SOURCE_SUPPORT_EMPTY')
        return raw/total*(self.H(t)*self.source_per_x)
    def set_interval(self,left,right):
        # Exact crossing segmentation permits unambiguous one-sided endpoint values.
        E,_,_=self.geometry((left+right)/2)
        self._source_mask=(E>=13.6)&(E<=100.)
        self._sigma_mask=E[:,None]>=FITS[:,0]
    def sigma(self,t):
        E,_,_=self.geometry(t)
        if self._sigma_mask is None:return sigma_cm2(E)
        out=[]
        for i,(cut,emax,e0,s0,ya,p,yw,y0,y1) in enumerate(FITS):
            x=E/e0-y0;y=np.sqrt(x*x+y1*y1)
            raw=s0*((x-1)**2+yw*yw)*y**(.5*p-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18
            out.append(raw*self._sigma_mask[:,i])
        return np.array(out).T
    def initial_state(self):return np.r_[self.g0,np.zeros(self.K+len(LEDGER))]
    def rates(self,t,g):
        a=A_BIRTH*math.exp(self.x(t));nh,nhe=self.owner.density(a)
        E,mu,Edot=self.geometry(t);sig=self.sigma(t)
        return a,nh,E,Edot,C_CM_S*nh*sig*neutral(g)[None,:]
    def rhs(self,t,y):
        g=y[:4];N=y[4:4+self.K]
        a,nh,E,Edot,lam=self.rates(t,g)
        sig=self.sigma(t)
        gamma=C_CM_S*nh*(sig*N[:,None]).sum(axis=0)
        heat=C_CM_S*nh*EV_ERG*(sig*N[:,None]*(E[:,None]-BIND_EV)).sum(axis=0)
        p=self.owner.point(a,g,gamma,heat);self.last_native=p
        A=(lam*N[:,None]).sum(axis=0);Q=(lam*N[:,None]*(E[:,None]-BIND_EV)).sum(axis=0)
        S=self.source(t);workg=2*self.H(t)*g[3]
        gas=np.r_[p['fraction_dt'],p['w_dt_ev_per_h_s']-workg]
        ledger=np.r_[sum(S),np.dot(S,E),A,Q,p['escape']/nh/EV_ERG,p['cmb']/nh/EV_ERG,
                     -np.dot(N,Edot),workg,p['ci']/nh,p['rr']/nh,p['dr']/nh]
        return np.r_[gas,S-lam.sum(axis=1)*N,ledger]
    def jac(self,t,y):
        base=self.rhs(t,y);size=len(y);J=lil_matrix((size,size))
        for j in range(4):
            h=1e-5*max(abs(y[j]),self.scale[j]);trial=y.copy();trial[j]+=h
            if not admissible(trial[:4]):h=-h;trial[j]=y[j]+h
            J[:,j]=((self.rhs(t,trial)-base)/h)[:,None]
        a,nh,E,Edot,lam=self.rates(t,y[:4]);L=4+self.K
        for k in range(self.K):
            h0,h1,h2=lam[k]
            J[0,4+k]=h0;J[1,4+k]=(h1-h2)/Y_HE;J[2,4+k]=h2/Y_HE
            J[3,4+k]=np.dot(lam[k],E[k]-BIND_EV)
            J[4+k,4+k]=-sum(lam[k])
            for j in range(3):J[L+2+j,4+k]=lam[k,j];J[L+5+j,4+k]=lam[k,j]*(E[k]-BIND_EV[j])
            J[L+10,4+k]=-Edot[k]
        return J.tocsr()
    def conservation_rate(self,t,y,f):
        L=4+self.K;E,_,Edot=self.geometry(t);gdot=f[:4]
        bdot=BIND_EV[0]*gdot[0]+Y_HE*(BIND_EV[1]*(gdot[1]+gdot[2])+BIND_EV[2]*gdot[2])
        return {'number':f[L]-sum(f[4:L])-sum(f[L+2:L+5]),
                'energy':f[L+1]+f[L+9]-(np.dot(E,f[4:L])+np.dot(Edot,y[4:L])+gdot[3]+bdot+f[L+8]+f[L+10]+f[L+11])}
    def result(self,y,metadata):
        L=4+self.K;d=dict(zip(LEDGER,map(float,y[L:])));E,_,_=self.geometry(self.t_end)
        g=y[:4];N=y[4:L]
        number=d['birth_n']-sum(N)-sum(y[L+2:L+5])
        energy=d['birth_e']+self.g0[3]+d['cmb']-(np.dot(E,N)+g[3]+binding(g)-binding(self.g0)+d['escape']+d['work_p']+d['work_g'])
        photo=y[L+2:L+5];ci=y[L+12:L+15];rr=y[L+15:L+18];dr=y[L+18]
        predicted=np.array([photo[0]+ci[0]-rr[0],(photo[1]+ci[1]-rr[1]-dr-photo[2]-ci[2]+rr[2])/Y_HE,(photo[2]+ci[2]-rr[2])/Y_HE])
        return dict(m=self.m,angles=self.angles,q=self.q,photon_modes=self.K,gas_final=g.tolist(),temperature_K=temperature(g),
                    photon_number=float(sum(N)),photon_energy_ev=float(np.dot(E,N)),binding_delta_ev=float(binding(g)-binding(self.g0)),
                    number_defect=float(number),energy_defect_ev=float(energy),species_defect=(g[:3]-self.g0[:3]-predicted).tolist(),
                    min_photon=float(min(N)),gas_positive=admissible(g),ledger=d,metadata=metadata)
