"""HE22 direct HE21 source-age transport with a point microphysical RHS owner.

Uses genuine HE21 source shape and spectral cut reconstruction. For actual physics
native_factory must supply original Grackle/rei_microphysics. A fake test double
may be used ONLY to verify interface and photo-only limit. In this scope source
emission per logarithmic interval remains prescribed, NOT native MD14 true history.
"""
from __future__ import annotations
import math
import numpy as np
from he21_photo import (
    SOURCE_N_PER_H,X_END,A_BIRTH,Y_HE,N_H_Z20,KB_ERG_K,EV_ERG,
    cells,admissible,binding,electrons,redshift_vector,Hubble,_spectral_nodes,FIT_CUTS
)
from he22_contract import solve_midpoint

def run_coupled(native_factory, m=8,steps=16,q=0.,source_count=SOURCE_N_PER_H,
        photons=True,threshold_split=True, initial=(1e-5,1e-5,0.,None),
        xend=X_END,gl_order=4,density_provider=None):
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
    workp=workg=em_u=0.;A_total=np.zeros(3);Q_heat=0.;escaped=cmb=0.;native_calls=0
    ci_total=np.zeros(3);rr_total=np.zeros(3);dr_total=0.;density_history=[]
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
            oldN=M.copy()
            gas_pre=gas.copy()
            owner=native_factory(float(A_BIRTH*math.exp(float(xm))),float(xm))
            nh=(N_H_Z20*math.exp(-3*float(xm)) if density_provider is None else
                float(density_provider(float(A_BIRTH*math.exp(float(xm))),float(xm))))
            step=solve_midpoint(gas_pre, oldN, Emid, nh, dt, owner)
            density_history.append(nh)
            if step.ci_per_H is not None:
                ci_total+=step.ci_per_H;rr_total+=step.rr_per_H;dr_total+=step.dr_per_H
            max_error=max(max_error,step.scaled_implicit_residual)
            native_calls+=step.rhs_calls
            gas=step.gas
            M=step.photons
            A_total+=step.events_per_H
            Q_heat+=float(step.photoheat_per_H.sum())
            escaped+=step.escaped_ev_per_H
            cmb+=step.cmb_to_gas_ev_per_H
            if np.min(M)<-1e-22:raise RuntimeError('negative photons')
            # Physical support crossing measured before absorption at midpoint.
        else:
            owner=native_factory(float(A_BIRTH*math.exp(float(xm))),float(xm))
            nh=(N_H_Z20*math.exp(-3*float(xm)) if density_provider is None else
                float(density_provider(float(A_BIRTH*math.exp(float(xm))),float(xm))))
            step=solve_midpoint(gas,np.empty(0),np.empty(0),nh,dt,owner)
            density_history.append(nh)
            if step.ci_per_H is not None:
                ci_total+=step.ci_per_H;rr_total+=step.rr_per_H;dr_total+=step.dr_per_H
            max_error=max(max_error,step.scaled_implicit_residual)
            native_calls+=step.rhs_calls
            gas=step.gas
            escaped+=step.escaped_ev_per_H
            cmb+=step.cmb_to_gas_ev_per_H
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
    electron_defect=None # CI/RR/DR also change electron abundance; not a photon-only identity.
    energy_defect=(em_u+u0+cmb)-(ugamma+gas[3]+Bdelta+workp+workg+escaped)
    return dict(m=m,steps=steps,q=q,source_count=n_em,
       absorbed=list(map(float,A_total)),heat_ev=float(Q_heat),work_photon_ev=workp,
       work_gas_ev=workg,photon_final_ev=ugamma,binding_delta_ev=Bdelta,
       gas_u_final_ev=float(gas[3]),initial_gas_u_ev=u0,
       gas_final=list(map(float,gas)),source_energy_ev=em_u,
       max_newton_error=max_error,number_defect=number_defect,
       energy_defect=energy_defect,electron_defect=electron_defect,
       source_shape_number_defect=shape_n,source_shape_energy_defect=shape_u,
       max_support_crossing=crossings,escaped_ev=escaped,cmb_to_gas_ev=cmb,
       native_evaluator_calls=native_calls,ci_per_H=ci_total.tolist(),rr_per_H=rr_total.tolist(),
       dr_per_H=dr_total,total_hydrogen_density_cm3=density_history,
       normalization='per total hydrogen nucleus' if density_provider is not None else 'HE21 historical density convention',
       chemical_species_defect=(gas[:3]-np.asarray(ginit[:3])-np.array([
         A_total[0]+ci_total[0]-rr_total[0],
         (A_total[1]+ci_total[1]-rr_total[1]-dr_total-A_total[2]-ci_total[2]+rr_total[2])/Y_HE,
         (A_total[2]+ci_total[2]-rr_total[2])/Y_HE])).tolist())
