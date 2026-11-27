"""Positive proper-time Duhamel map plus implicit native midpoint gas.

Hazards are held at physical/gas midpoint on each no-cutoff-crossing substep.
The source is sampled at actual proper-time birth nodes in conserved k-space.
Absorption energies and redshift work are separately integrated in proper time.
This approximation is tested against adaptive continuous-time native RHS.
"""
import time,math
import numpy as np
from physics import (A_BIRTH,Y_HE,EV_ERG,BIND_EV,neutral,admissible,binding,LEDGER,frozen_duhamel)

class BirthCell:
    def __init__(self,model,left,right,order=16):
        self.model=model;self.left=left;self.right=right;self.dt=right-left
        model.set_interval(left,right)
        z,w=np.polynomial.legendre.leggauss(order);self.u=(z+1)/2;self.w=w/2
        self.times=left+self.dt*self.u
        self.S=np.array([model.source(t) for t in self.times])
        self.E=np.array([model.geometry(t)[0] for t in self.times])
        self.Ed=np.array([model.geometry(t)[2] for t in self.times])
        self.Sinner=np.array([[model.source(left+self.dt*ue*ub) for ub in self.u] for ue in self.u])
        self.births=self.dt*np.einsum('i,ik->k',self.w,self.S)
        self.birth_energy=self.dt*np.einsum('i,ik,ik->',self.w,self.S,self.E)
    def photon_map(self,old,lam):
        total=lam.sum(axis=1);tau=total*self.dt
        shares=np.divide(lam,total[:,None],out=np.zeros_like(lam),where=total[:,None]>0)
        age=1-self.u
        surv=old*np.exp(-tau)+self.dt*np.einsum('i,ik,ik->k',self.w,self.S,np.exp(-age[:,None]*tau))
        lost=old*(-np.expm1(-tau))+self.dt*np.einsum('i,ik,ik->k',self.w,self.S,-np.expm1(-age[:,None]*tau))
        # N(t_event) is a second, positive Duhamel integral over actual birth times.
        T=self.u[:,None,None]*self.dt
        expinner=np.exp(-T*(1-self.u)[None,:,None]*total[None,None,:])
        at_event=old[None,:]*np.exp(-self.u[:,None]*tau)+T[:,0,:]*np.einsum('j,ijk,ijk->ik',self.w,self.Sinner,expinner)
        # For a truly constant source, recover analytic phi1 at every optical depth.
        if np.all(self.S==self.S[0]) and np.all(self.Sinner==self.S[0]):
            surv,lost=frozen_duhamel(old,self.S[0],total,self.dt)
            at_event=np.array([frozen_duhamel(old,self.S[0],total,u*self.dt)[0] for u in self.u])
        integ=self.dt*np.einsum('i,ik->k',self.w,at_event)
        e_integ=self.dt*np.einsum('i,ik,ik->k',self.w,at_event,self.E)
        meanE=np.divide(e_integ,integ,out=self.E[len(self.u)//2].copy(),where=integ>0)
        events=(lost[:,None]*shares).sum(axis=0)
        heats=(lost[:,None]*shares*(meanE[:,None]-BIND_EV)).sum(axis=0)
        work=-self.dt*np.einsum('i,ik,ik->',self.w,at_event,self.Ed)
        if np.any(surv<0) or np.any(events<0) or np.any(heats<0):raise RuntimeError('HE25_POSITIVITY')
        return surv,events,heats,work

def solve_step(model,y,cell,tolerance=3e-12,maxiter=15):
    gas0=y[:4].copy();old=y[4:4+model.K];trial=gas0.copy()
    mid=(cell.left+cell.right)/2;a=A_BIRTH*math.exp(model.x(mid));nh,_=model.owner.density(a)
    scale=np.r_[1.,1.,1.,max(gas0[3],1e-5)]
    def evaluate(end):
        gas=(gas0+end)/2
        _,_,_,_,lam=model.rates(mid,gas)
        photons,events,heats,workp=cell.photon_map(old,lam)
        alpha=neutral(gas)
        gamma=np.divide(events,cell.dt*alpha,out=np.zeros(3),where=alpha>0)
        heat=np.divide(heats*EV_ERG,cell.dt*alpha,out=np.zeros(3),where=alpha>0)
        p=model.owner.point(a,gas,gamma,heat)
        np.testing.assert_allclose(p['photo_events'],nh*events/cell.dt,rtol=2e-10,atol=1e-29)
        expected=nh*(np.dot(events,BIND_EV)+sum(heats))*EV_ERG/cell.dt
        if abs(p['thermal_micro']+p['binding_micro']+p['escape']-p['cmb']-p['photo_input'])>2e-9*max(abs(expected),1e-29):raise RuntimeError('HE25_NATIVE_MICRO_LEDGER')
        workg=cell.dt*2*model.H(mid)*gas[3]
        residual=end-gas0-cell.dt*np.r_[p['fraction_dt'],p['w_dt_ev_per_h_s']]+np.r_[0.,0.,0.,workg]
        escape=p['escape']*cell.dt/nh/EV_ERG;cmb=p['cmb']*cell.dt/nh/EV_ERG
        Ea=model.geometry(cell.left)[0];Eb=model.geometry(cell.right)[0]
        energy=np.dot(photons,Eb)-np.dot(old,Ea)-cell.birth_energy+end[3]-gas0[3]+binding(end)-binding(gas0)+escape-cmb+workp+workg
        limit=max(3e-11*max(cell.birth_energy,1e-15),2e-12*abs(end[3]))
        return residual,(photons,events,heats,workp,workg,escape,cmb,p),energy,limit
    calls=0
    for iteration in range(maxiter+1):
        residual,data,energy,limit=evaluate(trial);calls+=1
        err=float(max(abs(residual)/scale))
        if err<tolerance and abs(energy)<=limit:break
        if iteration==maxiter:raise RuntimeError(f'HE25_NEWTON_CAP err={err} energy={energy} limit={limit}')
        jac=np.empty((4,4))
        for j in range(4):
            h=(1e-6*max(abs(trial[j]),1e-4)) if j<3 else 2e-6*max(trial[j],1e-4)
            g=trial.copy();g[j]+=h
            if not admissible(g):h=-h;g[j]=trial[j]+h
            rr,_,_,_=evaluate(g);calls+=1;jac[:,j]=(rr-residual)/h
        direction=np.linalg.solve(jac,-residual)
        for back in range(24):
            candidate=trial+direction*2.**(-back)
            if not admissible(candidate):continue
            rr,_,_,_=evaluate(candidate);calls+=1
            if max(abs(rr)/scale)<err:trial=candidate;break
        else:raise RuntimeError('HE25_LINESEARCH')
    photons,events,heats,workp,workg,escape,cmb,p=data
    delta=np.r_[sum(cell.births),cell.birth_energy,events,heats,escape,cmb,workp,workg,
                p['ci']*cell.dt/nh,p['rr']*cell.dt/nh,p['dr']*cell.dt/nh]
    out=np.r_[trial,photons,y[4+model.K:]+delta]
    return out,dict(newton=err,energy=energy,iterations=iteration,calls=calls)

def solve_transport(model,n=16,quadrature_order=16,cohort_path=None,newton_tolerance=3e-15):
    if n not in [16,32,64,128,256]:raise ValueError('HE25_TIME_SCOPE')
    start=time.perf_counter();y=model.initial_state()
    bounds=np.array(sorted(set([*np.linspace(0,model.t_end,n+1),*model.breakpoints])))
    maximum=energy_max=0.;calls=0;birth_t=[];birth_a=[];birth_weights=[]
    for left,right in zip(bounds[:-1],bounds[1:]):
        cell=BirthCell(model,float(left),float(right),order=quadrature_order)
        y,info=solve_step(model,y,cell,tolerance=newton_tolerance)
        maximum=max(maximum,info['newton']);energy_max=max(energy_max,abs(info['energy']));calls+=info['calls']
        if cohort_path is not None:
            birth_t.extend(cell.times);birth_a.extend([A_BIRTH*math.exp(model.x(t)) for t in cell.times])
            birth_weights.extend(cell.S*cell.dt*cell.w[:,None])
    if cohort_path is not None:
        # Each row is a proper-time birth cohort; columns retain their own covariant k.
        # E_birth, mu_birth are reconstructed exactly from (k,a_birth), not inferred from moments.
        with open(cohort_path,'xb') as f:np.savez_compressed(f,t_birth=np.array(birth_t),a_birth=np.array(birth_a),counts=np.array(birth_weights),c_k_perp_eV=model.k_perp,c_k_parallel_eV=model.k_parallel,Eref=model.Eref,mu0=model.mu0)
    r=model.result(y,dict(method='HE25_positive_Duhamel_native_midpoint',n=n,substeps=len(bounds)-1,
          quadrature_order=quadrature_order,newton_tolerance=newton_tolerance,newton_max=maximum,local_energy_max=energy_max,native_evaluations=calls,wall_s=time.perf_counter()-start))
    if abs(r['number_defect'])>3e-15 or abs(r['energy_defect_ev'])>3e-12 or not r['gas_positive'] or r['min_photon']<0 or max(abs(v) for v in r['species_defect'])>3e-12:raise RuntimeError('HE25_GLOBAL_LEDGER: '+str(r))
    return r
