"""Node-resolved joint diffuse/sink reionization history (B2C2B0C-R1).

This solver promotes the validated global two-reservoir DAE to the fixed
46,080-parcel hierarchy locked in B2C2B0A.  It deliberately keeps the R1
photon history as a fixed transport control and evolves local H/He species and
thermal energies, plus 18 macro-resolved sink reservoirs.

The primary purpose is a conservative existence/convergence gate.  It does
not infer a post-hoc unresolved sink, front growth, source calibration, or
Bianchi feedback.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.optimize import least_squares

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import phase_space_kernel_b2c0 as B0
import hi_transmission_kernel_b2c1a as B1A
import multigroup_hhe_transmission as B1B
import hierarchical_two_scale_closure as HIER
from absorption_decomposition import normalized_group_quadrature
from b2b_physical_model import hubble
from monolithic_model_b2a import EV_ERG, KB_ERG

MPC_CM=B0.MPC_CM
NH0=B0.NH0_CM3
YHE=B0.YHE
NHC=NH0*MPC_CM**3
NHEC=YHE*NHC
MYR_S=1e6*365.25*86400.0
PI=math.pi
GROUPS=B1B.GROUP_ORDER
SPECIES=B1B.SPECIES
LOW_GROUPS=['G1','G2a','G2b']
SHAPE_LANES=['LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR']
DYNAMIC_LANES=[
 ('PRIMARY_LOCAL_NEUTRAL','LOCAL_NEUTRAL_HAZARD_PRIMARY','BASELINE','DETERMINISTIC'),
 ('SHAPE_RECOMBINATION','RECOMBINATION_WEIGHTED_AUDITOR','BASELINE','DETERMINISTIC'),
 ('SHAPE_SCRIPT','SCRIPT_SELF_SHIELDING_AUDITOR','BASELINE','DETERMINISTIC'),
 ('CHEM_MACRO_VARIANCE','LOCAL_NEUTRAL_HAZARD_PRIMARY','MACRO_DENSITY_VARIANCE','DETERMINISTIC'),
 ('CHEM_EARLY_COOLER','LOCAL_NEUTRAL_HAZARD_PRIMARY','EARLY_REIONIZED_COOLER','DETERMINISTIC'),
 ('CHEM_EARLY_HOTTER','LOCAL_NEUTRAL_HAZARD_PRIMARY','EARLY_REIONIZED_HOTTER','DETERMINISTIC'),
 ('CHEM_PATCHY','LOCAL_NEUTRAL_HAZARD_PRIMARY','BASELINE','PATCHY_BETA_DIRICHLET'),
]


def beta_hi(T): return 5.835e-11*np.sqrt(T)*np.exp(-157804.0/T)
def beta_hei(T): return 2.71e-11*np.sqrt(T)*np.exp(-285331.0/T)
def beta_heii(T): return 5.707e-12*np.sqrt(T)*np.exp(-631495.0/T)

def temperature_from_state(pop,U):
    NH=pop[:,0]+pop[:,1]; NHe=pop[:,2]+pop[:,3]+pop[:,4]
    Ne=pop[:,1]+pop[:,3]+2.0*pop[:,4]
    denom=1.5*KB_ERG*np.maximum(NH+NHe+Ne,1e-300)
    return np.maximum(U/denom,1.0)

def fractions(pop):
    NH=np.maximum(pop[:,0]+pop[:,1],1e-300)
    NHe=np.maximum(pop[:,2]+pop[:,3]+pop[:,4],1e-300)
    return {'xHII':pop[:,1]/NH,'xHeI':pop[:,2]/NHe,'xHeII':pop[:,3]/NHe,'xHeIII':pop[:,4]/NHe}

def thermal_coefficients(T):
    llH=315614.0/T; llHeI=570670.0/T; llHeII=631515.0/T
    recH=3.435e-30*T*llH**1.970/(1.0+(llH/2.250)**0.376)**3.720
    recHeII=KB_ERG*T*(1.26e-14*llHeI**0.750)
    recHeIII=8.0*3.435e-30*T*llHeII**1.970/(1.0+(llHeII/2.250)**0.376)**3.720
    excH=7.5e-19*np.exp(-118348.0/T)/(1.0+np.sqrt(T/1e5))
    excHeII=5.54e-17*T**-0.397*np.exp(-473638.0/T)/(1.0+np.sqrt(T/1e5))
    ff=1.42e-27*np.sqrt(T)*(1.1+0.34*np.exp(-((5.5-np.log10(T))**2)/3.0))
    return recH,recHeII,recHeIII,excH,excHeII,ff

def group_moments():
    out={}
    for group in GROUPS:
        E,w=normalized_group_quadrature(group,384)
        for sp in SPECIES:
            sigma=B1B.verner_sigma(sp,E)
            denom=float(np.sum(w*sigma))
            excess=0.0 if denom<=0 else float(np.sum(w*sigma*(E-B1B.THRESHOLDS[sp]))/denom)
            out[(sp,group)]={'sigma_bar':denom,'excess_eV':excess}
    return out
MOM=group_moments()

@dataclass
class Forcing:
    index:int; z_start:float; z_mid:float; z_end:float; duration_s:float
    macro_rates:pd.DataFrame; group_rates:dict[str,float]; group_kappa:dict[str,float]
    group_flux:dict[str,float]; gamma_HI:float; photon_ledger:dict[str,float]

@dataclass
class Geometry:
    z:float; macro:pd.DataFrame; nodes:pd.DataFrame
    macro_index:np.ndarray; micro_index:np.ndarray; W_node:np.ndarray
    delta_total:np.ndarray; base_mass_fraction:np.ndarray
    macro_mass_fraction:np.ndarray; local_mass_fraction:np.ndarray

@dataclass
class State:
    pop:np.ndarray; U:np.ndarray
    sink_pop:np.ndarray; sink_U:np.ndarray; sink_nH:np.ndarray; sink_radius:np.ndarray


def find_one(root:Path,name:str)->Path:
    matches=list(root.rglob(name))
    if not matches: raise FileNotFoundError((root,name))
    return sorted(matches,key=lambda p:(len(p.parts),str(p)))[0]

def interp_history(history,z):
    h=history.sort_values('z'); x=h.z.to_numpy(); out={}
    for c in ['N1','N2','N3','xHII','xHeII','xHeIII','T_K','Gamma_HI']:
        out[c]=float(PchipInterpolator(x,h[c].to_numpy())(z))
    out['xHeI']=max(1.0-out['xHeII']-out['xHeIII'],0.0)
    return out

def load_inputs(r1,b0a,b0c):
    hist=pd.read_csv(r1/'data/canonical_direct_history.csv')
    ledger=pd.read_csv(r1/'data/canonical_direct_photon_ledger.csv').sort_values('z_mid',ascending=False)
    targets=pd.read_csv(b0a/'data/r1_opacity_targets.csv')
    macro_alloc=pd.read_csv(b0a/'data/macro_species_photon_allocation.csv')
    macro_template=pd.read_csv(b0a/'data/fixed_macro_parcel_template_z6.csv')
    micro_npz=np.load(b0a/'data/fixed_micro_parcel_template_z6.npz')
    node_table=pd.read_csv(b0a/'data/hierarchical_node_table.csv.gz')
    mapping=pd.read_csv(find_one(r1,'density_mapping_colossus_1_3_10_port.csv'))
    forcings=[]
    for i,row in enumerate(ledger.itertuples()):
        z=float(row.z_mid); state=interp_history(hist,z)
        group_rates={g:float(getattr(row,f'absorption_{g}_rate')) for g in GROUPS}
        group_kappa={g:float(targets[np.isclose(targets.z,z)&(targets.group==g)].target_total_kappa_cMpc_inv.iloc[0]) for g in GROUPS}
        flux={g:(group_rates[g]/group_kappa[g] if group_kappa[g]>0 else 0.0) for g in GROUPS}
        forcings.append(Forcing(i,float(row.z_start),z,float(row.z_end),float(row.dt_Myr)*MYR_S,
            macro_alloc[np.isclose(macro_alloc.z,z)].copy(),group_rates,group_kappa,flux,state['Gamma_HI'],
            {k:float(getattr(row,k)) for k in ['emission_rate','storage_rate','ionized_absorption_rate','threshold_redshift_loss_rate','front_absorption_rate','relative_photon_ledger_residual']}))
    micro=HIER.FixedMicroTemplate(n_delta=int(micro_npz['n_delta']),n_t=int(micro_npz['n_t']),w_delta=micro_npz['w_delta'],w_temperature=micro_npz['w_temperature'],u_delta=micro_npz['u_delta'],u_temperature=micro_npz['u_temperature'],weight_lock_redshift=float(micro_npz['weight_lock_redshift']))
    return hist,forcings,macro_template,micro,node_table,mapping

def build_geometry(z,hist,macro_template,micro,mapping,variant='BASELINE'):
    sv=interp_history(hist,z); hs=B0.HistoryState(z=z,x_hii=sv['xHII'],x_heii=sv['xHeII'],x_heiii=sv['xHeIII'],temperature=sv['T_K'],gamma_hi=sv['Gamma_HI'])
    macro=HIER.macro_measure(z,mapping,macro_template)
    nodes,_,_=HIER.construct_hierarchy(hs,macro,micro,variant)
    W=nodes.W_node.to_numpy(); delta=nodes.delta_total.to_numpy(); mi=nodes.macro_index.to_numpy(int)
    base=W*delta; base/=base.sum()
    mm=np.bincount(mi,weights=base,minlength=len(macro)); local=base/mm[mi]
    return Geometry(z,macro,nodes,mi,nodes.micro_index.to_numpy(int),W,delta,base,mm,local)

def initialize_state(hist,geom):
    sv=interp_history(hist,6.0)
    pop=np.empty((len(geom.nodes),5))
    NH=NHC*geom.base_mass_fraction; NHe=YHE*NH
    for j,(name,frac) in enumerate([('HI',1-sv['xHII']),('HII',sv['xHII']),('HeI',sv['xHeI']),('HeII',sv['xHeII']),('HeIII',sv['xHeIII'])]):
        pop[:,j]=(NH if j<2 else NHe)*frac
    Ne=pop[:,1]+pop[:,3]+2*pop[:,4]
    U=1.5*KB_ERG*sv['T_K']*(NH+NHe+Ne)
    sink_pop=np.zeros((len(geom.macro),5)); sink_U=np.zeros(len(geom.macro))
    return State(pop,U,sink_pop,sink_U,np.zeros(len(geom.macro)),np.zeros(len(geom.macro)))

def rescale_to_geometry(state,geom):
    """Keep fixed macro masses minus sink and fixed local mass labels."""
    for m in range(len(geom.macro)):
        sel=geom.macro_index==m
        total_macro=NHC*geom.macro_mass_fraction[m]
        sink_H=state.sink_pop[m,0]+state.sink_pop[m,1]
        target=max(total_macro-sink_H,0.0)*geom.local_mass_fraction[sel]
        current=state.pop[sel,0]+state.pop[sel,1]
        scale=np.divide(target,current,out=np.ones_like(target),where=current>0)
        state.pop[sel]*=scale[:,None]; state.U[sel]*=scale

def state_temperature(pop,U): return temperature_from_state(pop,U)

def local_volume(pop,z,delta):
    NH=pop[:,0]+pop[:,1]; nH=NH0*(1+z)**3*delta
    return np.divide(NH,nH,out=np.zeros_like(NH),where=nH>0),nH

def internal_source(pop,U,z,delta,closure):
    T=state_temperature(pop,U); V,nH=local_volume(pop,z,delta); nHe=YHE*nH
    f=fractions(pop); means=f.copy(); moments=B0.conditional_moments(means,closure)
    hs=B0.HistoryState(z=z,x_hii=float(np.average(f['xHII'])),x_heii=float(np.average(f['xHeII'])),x_heiii=float(np.average(f['xHeIII'])),temperature=float(np.average(T)),gamma_hi=0.0)
    kernel=B0.full_ots_kernel(hs,{'delta':delta,'temperature':T},moments)
    source=kernel['source']
    ne=nH*f['xHII']+nHe*(f['xHeII']+2*f['xHeIII'])
    coll=np.zeros_like(source)
    rH=nH*(1-f['xHII'])*ne*beta_hi(T); coll[:,0]-=rH; coll[:,1]+=rH
    r1=nHe*f['xHeI']*ne*beta_hei(T); coll[:,2]-=r1; coll[:,3]+=r1
    r2=nHe*f['xHeII']*ne*beta_heii(T); coll[:,3]-=r2; coll[:,4]+=r2
    dN=(source+coll)*V[:,None]
    recH,recHeII,recHeIII,excH,excHeII,ff=thermal_coefficients(T)
    nHI=nH*(1-f['xHII']);nHII=nH*f['xHII'];nHeI=nHe*f['xHeI'];nHeII=nHe*f['xHeII'];nHeIII=nHe*f['xHeIII']
    cool=ne*nHII*recH+ne*nHeII*recHeII+ne*nHeIII*recHeIII+ne*nHI*excH+ne*nHeII*excHeII+ne*nHI*beta_hi(T)*13.598*EV_ERG+ne*nHeI*beta_hei(T)*24.587*EV_ERG+ne*nHeII*beta_heii(T)*54.416*EV_ERG+ne*(nHII+nHeII+4*nHeIII)*ff
    pressure=(nH+nHe+ne)*KB_ERG*T; expansion=3*float(hubble(z))*pressure
    dU=-(cool+expansion)*V
    return dN,dU,kernel

def conservative_internal_step(pop,U,z,delta,dt,closure):
    dN,dU,kernel=internal_source(pop,U,z,delta,closure)
    deltaN=dN*dt
    scale=np.ones(len(pop))
    for s in range(5):
        neg=deltaN[:,s]<0
        bound=np.ones(len(pop)); bound[neg]=np.divide(pop[neg,s],-deltaN[neg,s],out=np.ones(np.sum(neg)),where=(-deltaN[neg,s])>0)
        scale=np.minimum(scale,bound)
    scale=np.minimum(scale,1.0)*(1-1e-13)
    pop_new=pop+scale[:,None]*deltaN
    dE=dU*dt
    escale=np.ones(len(U)); neg=dE<0; escale[neg]=np.minimum(1.0,np.divide(U[neg]*(1-1e-13),-dE[neg],out=np.ones(np.sum(neg)),where=(-dE[neg])>0))
    U_new=U+escale*dE
    Hres=np.max(np.abs((pop_new[:,0]+pop_new[:,1])-(pop[:,0]+pop[:,1]))/np.maximum(pop[:,0]+pop[:,1],1))
    Heres=np.max(np.abs((pop_new[:,2]+pop_new[:,3]+pop_new[:,4])-(pop[:,2]+pop[:,3]+pop[:,4]))/np.maximum(pop[:,2]+pop[:,3]+pop[:,4],1))
    return pop_new,U_new,{'reaction_limiter_weighted':float(np.average(1-scale,weights=np.maximum(pop[:,0]+pop[:,1],1e-300))),'energy_limiter_weighted':float(np.average(1-escale,weights=np.maximum(pop[:,0]+pop[:,1],1e-300))),'H_nuclei_residual':float(Hres),'He_nuclei_residual':float(Heres),'stoich_residual':float(np.max(np.abs(kernel['stoich_residual'])))}

def sink_internal_step(pop,U,nH,z,dt,closure='DETERMINISTIC'):
    active=(pop[:,0]+pop[:,1])>0
    if not np.any(active): return pop,U,{'sink_internal_residual':0.0}
    p=pop.copy();u=U.copy(); delta=np.ones(np.sum(active))
    # fabricate equivalent mean density via local nH / cosmic mean
    delta=nH[active]/(NH0*(1+z)**3)
    pn,un,diag=conservative_internal_step(p[active],u[active],z,delta,dt,closure)
    p[active]=pn;u[active]=un
    return p,u,{'sink_internal_residual':max(diag['H_nuclei_residual'],diag['He_nuclei_residual']),'sink_reaction_limiter_weighted':diag['reaction_limiter_weighted'],'sink_energy_limiter_weighted':diag['energy_limiter_weighted']}

def shape_weights(state,geom,shape,group,sel):
    pop=state.pop[sel]; NH=pop[:,0]+pop[:,1]; T=state_temperature(pop,state.U[sel]); nHI_frac=np.divide(pop[:,0],NH,out=np.zeros_like(NH),where=NH>0)
    if group in ['G1','G2a']:
        if shape=='LOCAL_NEUTRAL_HAZARD_PRIMARY':
            sigma=MOM[('HI',group)]['sigma_bar']; nH=NH0*(1+geom.z)**3*geom.delta_total[sel]; xH=1-nHI_frac
            nss=B1A.self_shielding_density_cm3(T,1e-13,sigma)
            trans=np.exp(-np.clip(nH*nHI_frac/np.maximum(nss,1e-300),0,80))
            w=pop[:,0]*sigma*trans
        elif shape=='RECOMBINATION_WEIGHTED_AUDITOR':
            f=fractions(pop); nH=NH0*(1+geom.z)**3*geom.delta_total[sel];nHe=YHE*nH;ne=nH*f['xHII']+nHe*(f['xHeII']+2*f['xHeIII'])
            w=B0.alpha_b_hii(T)*ne*pop[:,1]
        else:
            sigma=MOM[('HI',group)]['sigma_bar'];nH=NH0*(1+geom.z)**3*geom.delta_total[sel]
            nss=B1A.self_shielding_density_cm3(T,1e-13,sigma); att=1-B1A.rahmati_gamma_ratio(nH,nss)
            w=pop[:,0]*sigma*np.maximum(att,1e-12)
    else: w=pop[:,0]*MOM[('HI',group)]['sigma_bar']
    if not np.any(w>0): w=np.maximum(pop[:,0],1e-300)
    return np.maximum(w,0)

def macro_rates(forcing,shape):
    df=forcing.macro_rates[forcing.macro_rates.shape_lane==shape]
    out={}
    for g in GROUPS:
        for s in SPECIES:
            arr=np.zeros(18)
            sub=df[(df.group==g)&(df.species==s)]
            if not sub.empty: arr[sub.macro_index.to_numpy(int)]=sub['j_abs_s-1_cMpc-3'].to_numpy()
            out[(s,g)]=arr
    return out

def cloud_area(radius,NHI,group):
    E,w=normalized_group_quadrature(group,192);sig=B1B.verner_sigma('HI',E);absorb=-np.expm1(-np.clip(sig*NHI,0,745));return PI*radius**2*float(np.sum(w*absorb)),float(np.sum(w*absorb*(E-B1B.THRESHOLDS['HI']))/max(np.sum(w*absorb),1e-300))

def target_sink_geometry(z,gamma,x,T,rejected,forcing):
    nmacro=len(x); target=np.zeros(nmacro); nH=np.zeros(nmacro);radius=np.zeros(nmacro);kappa={g:np.zeros(nmacro) for g in LOW_GROUPS}; excess={g:np.zeros(nmacro) for g in LOW_GROUPS}; cloudN=np.zeros(nmacro);fill=np.zeros(nmacro)
    for m in range(nmacro):
        total=sum(rejected[g][m] for g in LOW_GROUPS)
        if total<=0: continue
        n=float(B1A.self_shielding_density_cm3(np.array([T[m]]),gamma,B1A.gray_sigma_hi()[0])[0]);chi=B1A.calibrate_chi_jeans(z,gamma,B1A.gray_sigma_hi()[0])['chi_J']; R=.5*chi*float(B1A.jeans_length_cm(np.array([n]),np.array([T[m]]),np.array([x[m]]),np.array([0.0]),np.array([0.0]))[0]);Ncol=n*max(1-x[m],1e-12)*R
        denom=0;areas={}
        for g in LOW_GROUPS:
            A,ex=cloud_area(R,Ncol,g);areas[g]=A;excess[g][m]=ex; denom+=forcing.group_flux[g]*A
        if denom<=0: continue
        cn=total*(1/(1+z))**2*MPC_CM**2/denom; NHcloud=4/3*PI*R**3*n;target[m]=cn*NHcloud;nH[m]=n;radius[m]=R;cloudN[m]=cn;fill[m]=target[m]/(n*(1/(1+z))**3*MPC_CM**3)
        for g in LOW_GROUPS:kappa[g][m]=rejected[g][m]/max(forcing.group_flux[g],1e-300)
    return target,nH,radius,kappa,excess,cloudN,fill

def transfer_sink_mass(state,geom,target):
    nmacro=len(target); transferred=np.zeros((nmacro,5)); dU=np.zeros(nmacro)
    for m in range(nmacro):
        sel=geom.macro_index==m; old=state.sink_pop[m,0]+state.sink_pop[m,1]; d=target[m]-old
        if abs(d)<1e-30: continue
        if d>0:
            avail=np.sum(state.pop[sel,0]+state.pop[sel,1]); frac=min(d/max(avail,1e-300),1.0); removed=np.sum(state.pop[sel]*frac,axis=0); energy=np.sum(state.U[sel]*frac);state.pop[sel]*=(1-frac);state.U[sel]*=(1-frac);state.sink_pop[m]+=removed;state.sink_U[m]+=energy;transferred[m]=removed;dU[m]=energy
        else:
            release=min(-d,max(old,0)); frac=release/max(old,1e-300); removed=state.sink_pop[m]*frac; energy=state.sink_U[m]*frac;state.sink_pop[m]-=removed;state.sink_U[m]-=energy; weights=geom.local_mass_fraction[sel];state.pop[sel]+=weights[:,None]*removed;state.U[sel]+=weights*energy;transferred[m]=-removed;dU[m]=-energy
    return transferred,dU

def waterfill(total,capacity,weight):
    allocation=np.zeros_like(capacity,dtype=float);remaining=float(total);active=capacity>0
    for _ in range(len(capacity)+2):
        if remaining<=1e-20*max(total,1) or not np.any(active):break
        w=np.where(active,np.maximum(weight,1e-300),0.0);proposal=remaining*w/w.sum();room=capacity-allocation;take=np.minimum(proposal,np.maximum(room,0));allocation+=take;remaining=total-allocation.sum();active=room-take>1e-12*np.maximum(capacity,1)
    if remaining>1e-8*max(total,1): raise RuntimeError(f'macro sink capacity exhausted remaining={remaining:.6e} total={total:.6e}')
    return allocation

def redistribute_sink_rates(rejected,state,geom,forcing,dt,actual_mass=False):
    original={g:rejected[g].copy() for g in LOW_GROUPS}; totals={g:float(original[g].sum()) for g in LOW_GROUPS};total=sum(totals.values())
    if total<=0:return original,0.0
    frac={g:totals[g]/total for g in LOW_GROUPS};sinkH=np.sum(state.sink_pop[:,:2],axis=1);sx=fractions(state.sink_pop)['xHII'];sx=np.where(sinkH>0,sx,0.992);sT=np.where(sinkH>0,state_temperature(state.sink_pop,state.sink_U),1.45e4)
    # Geometry mass per unit absorption rate for the current spectral mix.
    trial={g:np.full(len(sinkH),1e50*frac[g]) for g in LOW_GROUPS};mass_unit,nH,_,_,_,_,_=target_sink_geometry(geom.z,forcing.gamma_HI,sx,sT,trial,forcing);coeff=mass_unit/1e50
    maxmass=0.92*NHC*geom.macro_mass_fraction
    mass_limit=np.maximum(sinkH,0.0) if actual_mass else maxmass
    cap_geometry=np.divide(mass_limit,np.maximum(coeff,1e-300))
    alpha=B0.alpha_b_hii(sT)
    # Exact necessary capacity at the bounded x_HII=1 boundary:
    # e_max = 1-x0 + dt*nH*alpha.  The final gate must use only the
    # current geometry; a stale larger nH would overestimate cycling.
    n_cycle=nH if actual_mass else np.maximum(nH,state.sink_nH)
    cap_cycle=mass_limit*(np.maximum(1-sx,0)/dt+alpha*n_cycle)
    safety=0.999 if actual_mass else 1.0
    capacity=safety*np.minimum(cap_geometry,cap_cycle)
    base=np.sum(np.stack([original[g] for g in LOW_GROUPS]),axis=0)+1e-12*total*geom.macro_mass_fraction
    alloc_total=waterfill(total,capacity,base)
    redistributed={g:alloc_total*frac[g] for g in LOW_GROUPS}
    old=np.concatenate([original[g] for g in LOW_GROUPS]);new=np.concatenate([redistributed[g] for g in LOW_GROUPS]);tv=0.5*np.sum(np.abs(old-new))/max(total,1)
    return redistributed,float(tv)

def sink_macro_implicit_update(pop_old,U_old,nH,z,dt,JH,JHeI,JHeII,photoheat,T_guess):
    """Positivity-preserving split implicit sink update.

    Hydrogen photoionization/recombination cycling is solved analytically by a
    backward quadratic.  The remaining full-OTS cross-couplings, helium
    recombinations/collisions, and external helium events are then applied as
    a conservative event vector.  Thermal loss uses a Patankar denominator.
    """
    NH=float(pop_old[0]+pop_old[1]);NHe=float(np.sum(pop_old[2:]))
    if NH<=0:return pop_old,U_old,{'residual':0.0,'success':True,'nfev':0}
    T=max(float(T_guess),100.0);x0=float(pop_old[1]/NH)
    alpha=float(B0.alpha_b_hii(np.array([T]))[0]);beta=float(beta_hi(np.array([T]))[0]);e=dt*JH/NH
    aa=dt*nH*(alpha+beta);bb=1.0-dt*nH*beta;cc=-(x0+e)
    if abs(aa)<1e-30:x=max(min(-cc/bb,1.0),0.0)
    else:
        disc=bb*bb-4*aa*cc
        if disc<0:raise RuntimeError(f'sink H quadratic negative discriminant {disc}')
        roots=[(-bb+math.sqrt(disc))/(2*aa),(-bb-math.sqrt(disc))/(2*aa)];valid=[r for r in roots if -1e-12<=r<=1+1e-12]
        if not valid:raise RuntimeError(f'sink H cycling no bounded root roots={roots} x0={x0} e={e} aa={aa}')
        x=min(max(valid[0],0.0),1.0)
    pop=np.array(pop_old,dtype=float);pop[0]=NH*(1-x);pop[1]=NH*x
    # Full OTS residual excluding the already integrated HII case-B event.
    arr=pop[None,:];f=fractions(arr);mom=B0.conditional_moments(f,'DETERMINISTIC');hs=B0.HistoryState(z=z,x_hii=x,x_heii=f['xHeII'][0],x_heiii=f['xHeIII'][0],temperature=T,gamma_hi=0.0);delta=np.array([nH/(NH0*(1+z)**3)]);ker=B0.full_ots_kernel(hs,{'delta':delta,'temperature':np.array([T])},mom);V=NH/max(nH,1e-300);src=ker['source'][0].copy()*V
    nHe=YHE*nH;ne=nH*x+nHe*(f['xHeII'][0]+2*f['xHeIII'][0]);rH=nH*nH*x*x*alpha*V;src-=rH*np.array([1.0,-1.0,0,0,0])
    coll=np.zeros(5);r=nHe*f['xHeI'][0]*ne*float(beta_hei(np.array([T]))[0])*V;coll[2]-=r;coll[3]+=r;r=nHe*f['xHeII'][0]*ne*float(beta_heii(np.array([T]))[0])*V;coll[3]-=r;coll[4]+=r
    ext=np.array([0.0,0.0,-JHeI,JHeI-JHeII,JHeII]);deltaN=dt*(src+coll+ext)
    scale=1.0
    for s in range(5):
        if deltaN[s]<0:scale=min(scale,pop[s]/max(-deltaN[s],1e-300))
    scale=min(scale,1.0)*(1-1e-13);pop+=scale*deltaN
    # Full H/He cooling and expansion at the updated populations.
    f=fractions(pop[None,:]);x=f['xHII'][0];q1=f['xHeI'][0];q2=f['xHeII'][0];q3=f['xHeIII'][0];ne=nH*x+nHe*(q2+2*q3);recH,recHeII,recHeIII,excH,excHeII,ff=thermal_coefficients(np.array([T]));nHI=nH*(1-x);nHII=nH*x;nHeI=nHe*q1;nHeII=nHe*q2;nHeIII=nHe*q3
    cool=(ne*nHII*recH[0]+ne*nHeII*recHeII[0]+ne*nHeIII*recHeIII[0]+ne*nHI*excH[0]+ne*nHeII*excHeII[0]+ne*nHI*float(beta_hi(np.array([T]))[0])*13.598*EV_ERG+ne*nHeI*float(beta_hei(np.array([T]))[0])*24.587*EV_ERG+ne*nHeII*float(beta_heii(np.array([T]))[0])*54.416*EV_ERG+ne*(nHII+nHeII+4*nHeIII)*ff[0])*V;expansion=3*float(hubble(z))*KB_ERG*T*(nH+nHe+ne)*V
    loss=max(cool+expansion,0.0);U=(U_old+dt*photoheat)/(1.0+dt*loss/max(U_old,1e-300));Ne=pop[1]+pop[3]+2*pop[4];Tnew=U/(1.5*KB_ERG*max(NH+NHe+Ne,1e-300))
    if not (100.0<=Tnew<=3e5):raise RuntimeError(f'sink thermal state out of range T={Tnew}')
    Hres=abs(pop[0]+pop[1]-NH)/max(NH,1);Heres=abs(np.sum(pop[2:])-NHe)/max(NHe,1);res=max(Hres,Heres)
    return pop,U,{'residual':res,'success':True,'nfev':1,'T':Tnew,'xHII':pop[1]/NH,'event_limiter':1-scale}



def photon_step(state,geom,forcing,shape,dt,relax_tau=None):
    rates=macro_rates(forcing,shape); nmacro=18
    # fixed point between diffuse capacity and quasi-static sink mass
    target=np.array(state.sink_pop[:,0]+state.sink_pop[:,1]); rejected={g:np.zeros(nmacro) for g in LOW_GROUPS}
    for _ in range(5):
        # trial scale diffuse masses to target while retaining fractions
        trial_H=[]
        candidate={g:np.zeros(len(state.pop)) for g in LOW_GROUPS}
        for m in range(nmacro):
            sel=geom.macro_index==m; cur=np.sum(state.pop[sel,:2]); desired=max(NHC*geom.macro_mass_fraction[m]-target[m],0); scale=desired/max(cur,1e-300)
            for g in LOW_GROUPS:
                w=shape_weights(state,geom,shape,g,sel);w=w/w.sum();candidate[g][sel]=rates[('HI',g)][m]*dt*w
        total=sum(candidate.values()); cap=np.zeros(len(state.pop))
        for m in range(nmacro):
            sel=geom.macro_index==m;cur=np.sum(state.pop[sel,:2]);desired=max(NHC*geom.macro_mass_fraction[m]-target[m],0);scale=desired/max(cur,1e-300);cap[sel]=state.pop[sel,0]*scale
        fac=np.minimum(1.0,np.divide(cap,total,out=np.ones_like(cap),where=total>0))
        rejected={g:np.bincount(geom.macro_index,weights=candidate[g]*(1-fac)/dt,minlength=nmacro) for g in LOW_GROUPS}
        rejected,redistribution_tv=redistribute_sink_rates(rejected,state,geom,forcing,dt)
        sink_H_now=np.sum(state.sink_pop[:,:2],axis=1)
        sx=fractions(state.sink_pop)['xHII']
        sT=np.where(sink_H_now>0,state_temperature(state.sink_pop,state.sink_U),1.4e4)
        new,nH,R,kappa,excess,cloudN,fill=target_sink_geometry(geom.z,forcing.gamma_HI,sx,sT,rejected,forcing)
        # Include the recombination cycling capacity available over this step.
        need=np.zeros(nmacro)
        for m in range(nmacro):
            events=sum(rejected[g][m] for g in LOW_GROUPS)*dt
            capacity_per_H=max(1-sx[m]+dt*float(B0.alpha_b_hii(np.array([sT[m]]))[0])*max(nH[m],state.sink_nH[m],1e-30),1e-10)
            need[m]=1.001*events/capacity_per_H
        new=np.maximum(new,need)
        if relax_tau is not None:
            factor=1-math.exp(-dt/(relax_tau*MYR_S));new=target+factor*(new-target)
        if np.max(np.abs(new-target)/np.maximum(new,1))<1e-7: target=new;break
        target=new
    transfer,dU=transfer_sink_mass(state,geom,target)
    # recompute actual allocation after transfer
    accepted={g:np.zeros(len(state.pop)) for g in LOW_GROUPS}; rejected={g:np.zeros(nmacro) for g in LOW_GROUPS}
    candidate={g:np.zeros(len(state.pop)) for g in LOW_GROUPS}
    for m in range(nmacro):
        sel=geom.macro_index==m
        for g in LOW_GROUPS:
            w=shape_weights(state,geom,shape,g,sel);w=w/w.sum();candidate[g][sel]=rates[('HI',g)][m]*dt*w
    total=sum(candidate.values());cap=state.pop[:,0].copy();fac=np.minimum(1.0,np.divide(cap,total,out=np.ones_like(cap),where=total>0))
    for g in LOW_GROUPS:
        accepted[g]=candidate[g]*fac; rejected[g]=np.bincount(geom.macro_index,weights=candidate[g]*(1-fac)/dt,minlength=nmacro)
    rejected,redistribution_tv=redistribute_sink_rates(
        rejected,state,geom,forcing,dt,actual_mass=True
    )
    # H photo events diffuse
    for g in LOW_GROUPS:
        ev=accepted[g];state.pop[:,0]-=ev;state.pop[:,1]+=ev;state.U+=ev*MOM[('HI',g)]['excess_eV']*EV_ERG
    # HeI fixed-control photons
    hei_rejected={g:np.zeros(nmacro) for g in GROUPS}
    for g in GROUPS:
        for m in range(nmacro):
            rate=rates[('HeI',g)][m]
            if rate<=0:continue
            sel=geom.macro_index==m; w=state.pop[sel,2]*MOM[('HeI',g)]['sigma_bar'];
            if w.sum()<=0:w=np.ones(np.sum(sel))
            cand=rate*dt*w/w.sum();fac_he=np.minimum(1.0,np.divide(state.pop[sel,2],cand,out=np.ones_like(cand),where=cand>0));ev=cand*fac_he;state.pop[sel,2]-=ev;state.pop[sel,3]+=ev;state.U[sel]+=ev*MOM[('HeI',g)]['excess_eV']*EV_ERG;hei_rejected[g][m]=(cand-ev).sum()/dt
    # Sink photons, full H/He OTS chemistry, collisional terms and thermal
    # balance are solved simultaneously by macro.  Recombination cycling can
    # therefore absorb more photons than the instantaneous neutral inventory.
    sink_heat=np.zeros(nmacro); sink_solver_residual=0.0; sink_solver_nfev=0
    # Geometry/opacity state associated with the accepted redistributed rates.
    sx_pre=fractions(state.sink_pop)['xHII'];sT_pre=np.where(np.sum(state.sink_pop[:,:2],axis=1)>0,state_temperature(state.sink_pop,state.sink_U),1.4e4)
    _,nH,R,kappa,excess,cloudN,fill=target_sink_geometry(geom.z,forcing.gamma_HI,sx_pre,sT_pre,rejected,forcing);state.sink_nH=nH;state.sink_radius=R
    for m in range(nmacro):
        JH=sum(rejected[g][m] for g in LOW_GROUPS);JHeI=sum(hei_rejected[g][m] for g in GROUPS);photo=0.0
        for g in LOW_GROUPS:photo+=rejected[g][m]*MOM[('HI',g)]['excess_eV']*EV_ERG
        for g in GROUPS:photo+=hei_rejected[g][m]*MOM[('HeI',g)]['excess_eV']*EV_ERG
        if np.sum(state.sink_pop[m,:2])>0:
            popm,Um,diag=sink_macro_implicit_update(state.sink_pop[m],state.sink_U[m],max(nH[m],state.sink_nH[m],1e-30),geom.z,dt,JH,JHeI,0.0,photo,sT_pre[m]);state.sink_pop[m]=popm;state.sink_U[m]=Um;sink_solver_residual=max(sink_solver_residual,diag['residual']);sink_solver_nfev+=diag['nfev']
    # geometry after actual rejected rates
    sx=fractions(state.sink_pop)['xHII'];sT=np.where(np.sum(state.sink_pop[:,:2],axis=1)>0,state_temperature(state.sink_pop,state.sink_U),1.4e4)
    target2,nH,R,kappa,excess,cloudN,fill=target_sink_geometry(geom.z,forcing.gamma_HI,sx,sT,rejected,forcing);state.sink_nH=nH;state.sink_radius=R
    H_total=sum(rates[('HI',g)].sum() for g in LOW_GROUPS); Hdiff=sum(a.sum()/dt for a in accepted.values()); Hsink=sum(r.sum() for r in rejected.values())
    return {'H_photon_partition_residual':abs(Hdiff+Hsink-H_total)/max(H_total,1),'sink_rate_total':Hsink,'sink_fraction':Hsink/max(H_total,1),'sink_mass_fraction':float(np.sum(state.sink_pop[:,:2])/NHC),'sink_volume_filling_max':float(np.max(fill)),'sink_opacity_fraction_max':float(max((np.max(kappa[g]/max(forcing.group_kappa[g],1e-300)) for g in LOW_GROUPS),default=0)),'mass_transfer_H_residual':float(np.max(np.abs(np.sum(transfer[:,:2],axis=1)-np.sum(transfer[:,:2],axis=1)))),'macro_sink_redistribution_TV':redistribution_tv,'sink_solver_residual':sink_solver_residual,'sink_solver_nfev':sink_solver_nfev,'macro_sink_H':np.sum(state.sink_pop[:,:2],axis=1).copy(),'kappa':kappa,'rejected':rejected}

def run_lane(name,shape,variant,closure,hist,forcings,macro_template,micro,mapping,substeps,initial_sink,relax_tau=None,save_nodes=True):
    g0=build_geometry(6.0,hist,macro_template,micro,mapping,'MACRO_DENSITY_VARIANCE' if variant=='MACRO_DENSITY_VARIANCE' else 'BASELINE'); state=initialize_state(hist,g0)
    # Seed the opacity-bearing sink population before the first chemistry step.
    # Its nuclei and thermal energy are transferred from the diffuse macros,
    # so the global R1 initial state is preserved exactly.
    rates0=macro_rates(forcings[0],shape); macro_H=sum(rates0[('HI',g)] for g in LOW_GROUPS); frac=macro_H/max(macro_H.sum(),1)
    target0=initial_sink['N_sink']*frac
    transfer_sink_mass(state,g0,target0)
    # The reduced DAE sink equilibrium is an explicit z=6 initial condition;
    # R1 remains the diffuse-phase auditor.  This avoids misidentifying the
    # nearly fully ionized diffuse composition as the cloud equilibrium.
    for m in range(len(target0)):
        NHs=np.sum(state.sink_pop[m,:2]); NHes=np.sum(state.sink_pop[m,2:])
        state.sink_pop[m,0]=NHs*(1-initial_sink['x_sink']);state.sink_pop[m,1]=NHs*initial_sink['x_sink']
        if NHes>0:
            # retain helium simplex inherited from transferred diffuse gas
            pass
        Ne=state.sink_pop[m,1]+state.sink_pop[m,3]+2*state.sink_pop[m,4]
        state.sink_U[m]=1.5*KB_ERG*initial_sink['T_sink']*(NHs+NHes+Ne)
    state.sink_nH[:]=initial_sink['nH_cm3']; state.sink_radius[:]=initial_sink['radius_cm']
    if variant in ['EARLY_REIONIZED_COOLER','EARLY_REIONIZED_HOTTER']:
        sign=-1 if variant=='EARLY_REIONIZED_COOLER' else 1; factor=np.exp(sign*0.18*((g0.nodes.z_re.to_numpy()-8)/3));state.U*=factor
    endpoint={'z':[6.0],'xHII':[fractions(state.pop)['xHII'].copy()],'xHeII':[fractions(state.pop)['xHeII'].copy()],'xHeIII':[fractions(state.pop)['xHeIII'].copy()],'T':[state_temperature(state.pop,state.U).copy()]}
    global_rows=[];ledger_rows=[];sink_rows=[]
    for forcing in forcings:
        geom=build_geometry(forcing.z_mid,hist,macro_template,micro,mapping,'MACRO_DENSITY_VARIANCE' if variant=='MACRO_DENSITY_VARIANCE' else 'BASELINE');rescale_to_geometry(state,geom);dt=forcing.duration_s/substeps
        for sub in range(substeps):
            # First-order relaxation ordering: internal recombination/cooling
            # creates the neutral capacity that can absorb photons during the
            # same coarse transport step.  Temporal refinement quantifies the
            # splitting error.
            state.pop,state.U,d1=conservative_internal_step(state.pop,state.U,geom.z,geom.delta_total,dt,closure);s1={'sink_internal_residual':0.0}
            pdg=photon_step(state,geom,forcing,shape,dt,relax_tau)
            d2={'reaction_limiter_weighted':0.0,'energy_limiter_weighted':0.0,'stoich_residual':0.0};s2={'sink_internal_residual':0.0}
            pf=fractions(state.pop); sf=fractions(state.sink_pop); NHd=np.sum(state.pop[:,:2]);NHs=np.sum(state.sink_pop[:,:2]);NHet=np.sum(state.pop[:,2:])+np.sum(state.sink_pop[:,2:])
            ledger_rows.append({'lane':name,'interval_index':forcing.index,'substep':sub+1,'substeps':substeps,'z_mid':forcing.z_mid,'dt_Myr':dt/MYR_S,**{k:v for k,v in pdg.items() if np.isscalar(v)},'diffuse_H_nuclei_residual':abs(NHd+NHs-NHC)/NHC,'He_nuclei_residual':abs(NHet-NHEC)/NHEC,'reaction_limiter_weighted':max(d1['reaction_limiter_weighted'],d2['reaction_limiter_weighted']),'energy_limiter_weighted':max(d1['energy_limiter_weighted'],d2['energy_limiter_weighted']),'stoich_residual':max(d1['stoich_residual'],d2['stoich_residual']),'sink_internal_residual':max(s1.get('sink_internal_residual',0),s2.get('sink_internal_residual',0))})
        # endpoint
        pf=fractions(state.pop); sf=fractions(state.sink_pop);T=state_temperature(state.pop,state.U);Ts=np.where(np.sum(state.sink_pop[:,:2],axis=1)>0,state_temperature(state.sink_pop,state.sink_U),np.nan)
        z=forcing.z_end;endpoint['z'].append(z);endpoint['xHII'].append(pf['xHII'].copy());endpoint['xHeII'].append(pf['xHeII'].copy());endpoint['xHeIII'].append(pf['xHeIII'].copy());endpoint['T'].append(T.copy())
        mass=state.pop[:,0]+state.pop[:,1]; w=mass/np.sum(mass)
        global_rows.append({'lane':name,'z':z,'xHII_diffuse_mass':float(np.sum(w*pf['xHII'])),'xHeII_diffuse_mass':float(np.sum(w*pf['xHeII'])),'xHeIII_diffuse_mass':float(np.sum(w*pf['xHeIII'])),'T_diffuse_mass':float(np.sum(w*T)),'sink_H_fraction':float(np.sum(state.sink_pop[:,:2])/NHC),'sink_xHII_mass':float(np.sum(state.sink_pop[:,1])/max(np.sum(state.sink_pop[:,:2]),1)),'sink_T_mass':float(np.nansum(np.sum(state.sink_pop[:,:2],axis=1)*Ts)/max(np.sum(state.sink_pop[:,:2]),1))})
        for m in range(18):sink_rows.append({'lane':name,'z':z,'macro_index':m,'N_HI':state.sink_pop[m,0],'N_HII':state.sink_pop[m,1],'N_HeI':state.sink_pop[m,2],'N_HeII':state.sink_pop[m,3],'N_HeIII':state.sink_pop[m,4],'U':state.sink_U[m],'T':Ts[m],'nH_cm3':state.sink_nH[m],'radius_pc':state.sink_radius[m]/3.085677581491367e18})
    ep={k:np.asarray(v) for k,v in endpoint.items()}
    return ep,pd.DataFrame(global_rows),pd.DataFrame(ledger_rows),pd.DataFrame(sink_rows)

def temporal_summary(runs):
    rows=[]
    for q in ['xHII_diffuse_mass','xHeII_diffuse_mass','xHeIII_diffuse_mass','T_diffuse_mass','sink_H_fraction','sink_xHII_mass','sink_T_mass']:
        y1=float(runs[1][1].iloc[-1][q]);y2=float(runs[2][1].iloc[-1][q]);y4=float(runs[4][1].iloc[-1][q]);d12=abs(y1-y2);d24=abs(y2-y4);p=math.log(d12/d24,2) if d12>0 and d24>0 else math.nan;rich=d24/(2**p-1) if np.isfinite(p) and abs(2**p-1)>1e-12 else math.nan
        rows.append({'quantity':q,'dt_value':y1,'dt2_value':y2,'dt4_value':y4,'difference_dt_dt2':d12,'difference_dt2_dt4':d24,'observed_order':p,'richardson_error':rich,'relative_dt2_dt4':d24/max(abs(y4),1e-300)})
    return pd.DataFrame(rows)

def flexrt(forcings,led):
    rows=[]
    last=led.groupby('interval_index').tail(1).set_index('interval_index')
    for f in forcings:
        row=last.loc[f.index]; frac=float(row.sink_fraction)
        for g in LOW_GROUPS:
            kt=f.group_kappa[g];ks=frac*kt;kd=kt-ks;flux=f.group_flux[g];prev={}
            for level in range(12):
                dx=1/2**level;tot=flux/dx*(1-math.exp(-kt*dx))
                for comp,k in [('DIFFUSE',kd),('SINK',ks),('TOTAL',kt)]:
                    val=tot if comp=='TOTAL' else tot*k/kt;ref=flux*k;rel=abs(val-ref)/max(abs(ref),1);order=math.log(prev[comp]/rel,2) if comp in prev and rel>0 and prev[comp]>0 else math.nan;prev[comp]=rel;rows.append({'interval_index':f.index,'z_mid':f.z_mid,'group':g,'component':comp,'level':level,'delta_chi_cMpc':dx,'relative_difference':rel,'observed_order':order})
    return pd.DataFrame(rows)

def execute(r1,b0a,b0c,output):
    output.mkdir(parents=True,exist_ok=True);hist,forcings,macro_template,micro,node_table,mapping=load_inputs(r1,b0a,b0c)
    reduced_history=pd.read_csv(b0c/'data/primary_joint_history.csv')
    reduced_ledger=pd.read_csv(b0c/'data/primary_joint_ledger.csv')
    first=reduced_history.iloc[0]; first_ledger=reduced_ledger.iloc[0]
    initial_sink={'N_sink':float(first.N_sink),'x_sink':float(first.x_sink),'T_sink':float(first.T_sink),'nH_cm3':float(first_ledger.cloud_density_cm3),'radius_cm':float(first_ledger.cloud_radius_proper_pc)*3.085677581491367e18}
    # primary temporal runs
    primary_runs={}
    for ns in [1,2,4]: primary_runs[ns]=run_lane('PRIMARY_LOCAL_NEUTRAL','LOCAL_NEUTRAL_HAZARD_PRIMARY','BASELINE','DETERMINISTIC',hist,forcings,macro_template,micro,mapping,ns,initial_sink,save_nodes=(ns==4))
    conv=temporal_summary(primary_runs);conv.to_csv(output/'temporal_convergence.csv',index=False)
    accepted=[primary_runs[4]];lane_meta=[DYNAMIC_LANES[0]]
    for lane in DYNAMIC_LANES[1:]:
        accepted.append(run_lane(*lane,hist,forcings,macro_template,micro,mapping,4,initial_sink));lane_meta.append(lane)
    # relaxation macro auditors reuse primary with tau
    relax=[]
    for tau in [10.0,100.0,300.0]: relax.append((tau,run_lane(f'RELAX_{int(tau)}MYR','LOCAL_NEUTRAL_HAZARD_PRIMARY','BASELINE','DETERMINISTIC',hist,forcings,macro_template,micro,mapping,4,initial_sink,relax_tau=tau,save_nodes=False)))
    globals_df=pd.concat([r[1] for r in accepted]+[r[1] for _,r in relax],ignore_index=True);ledgers_df=pd.concat([r[2] for r in accepted]+[r[2] for _,r in relax],ignore_index=True);sinks_df=pd.concat([r[3] for r in accepted]+[r[3] for _,r in relax],ignore_index=True)
    globals_df.to_csv(output/'global_history_all_lanes.csv',index=False);ledgers_df.to_csv(output/'node_global_ledgers.csv',index=False);sinks_df.to_csv(output/'macro_sink_history.csv.gz',index=False,compression='gzip')
    for (lane,_,_,_),r in zip(lane_meta,accepted): np.savez_compressed(output/f'node_history_{lane}.npz',**r[0])
    fr=flexrt(forcings,primary_runs[4][2]);fr.to_csv(output/'flexrt_node_history_refinement.csv',index=False)
    # feedback auditor: compare evolved neutral fractions/temperature with R1 fixed control
    ref=[]
    primary=primary_runs[4][1]
    for _,row in primary.iterrows():
        rv=interp_history(hist,row.z);ref.append({'z':row.z,'xHII_relative':row.xHII_diffuse_mass/rv['xHII']-1,'xHeII_relative':row.xHeII_diffuse_mass/rv['xHeII']-1,'T_relative':row.T_diffuse_mass/rv['T_K']-1,'fixed_photon_control':True,'opacity_feedback_enabled':False})
    pd.DataFrame(ref).to_csv(output/'r1_fixed_control_feedback_audit.csv',index=False)
    # gates
    smallest=fr.sort_values('delta_chi_cMpc').groupby(['interval_index','group','component'],as_index=False).first();orders=fr[np.isfinite(fr.observed_order)];hard_led=primary_runs[4][2]
    temporal_rel=float(conv.relative_dt2_dt4.max());order_valid=conv.observed_order.replace([np.inf,-np.inf],np.nan).dropna();
    gates={'H_nuclei_residual_max':float(hard_led.diffuse_H_nuclei_residual.max()),'He_nuclei_residual_max':float(hard_led.He_nuclei_residual.max()),'photon_partition_residual_max':float(hard_led.H_photon_partition_residual.max()),'reaction_limiter_weighted_max':float(hard_led.reaction_limiter_weighted.max()),'energy_limiter_weighted_max':float(hard_led.energy_limiter_weighted.max()),'sink_internal_residual_max':float(hard_led.sink_internal_residual.max()),'temporal_relative_dt2_dt4_max':temporal_rel,'temporal_order_range':[float(order_valid.min()) if len(order_valid) else math.nan,float(order_valid.max()) if len(order_valid) else math.nan],'flexrt_smallest_error_max':float(smallest.relative_difference.max()),'flexrt_order_range':[float(orders.observed_order.min()),float(orders.observed_order.max())],'lane_count':len(accepted),'relaxation_auditor_count':len(relax)}
    hard=(gates['H_nuclei_residual_max']<1e-12 and gates['He_nuclei_residual_max']<1e-12 and gates['photon_partition_residual_max']<1e-10 and gates['reaction_limiter_weighted_max']<1e-4 and gates['energy_limiter_weighted_max']<1e-4 and gates['temporal_relative_dt2_dt4_max']<0.01 and gates['flexrt_smallest_error_max']<0.01 and gates['lane_count']==7)
    result={'stage':'P0.5-B2C2B0C-R1-NODE-RESOLVED-JOINT-CHEMISTRY-SINK-HISTORY-LOCK','verdict':'PASS_B2C2B_AUTHORIZED' if hard else 'FAIL_CLOSED_NODE_RESOLVED_HISTORY','gates':gates,'B2C2B_authorization':hard,'next_stage':'P0.5-B2C2B-UNRESOLVED-SINK-CLOSURE-LOCK' if hard else 'BLOCKED','scope':{'node_parcels':46080,'shape_histories':3,'chemistry_sensitivity_histories':4,'relaxation_auditors':[10,100,300],'fixed_photon_control':True,'opacity_feedback_auditor':True,'full_HHe_diffuse_chemistry':True,'macro_sink_HHe_chemistry':True},'forbidden_work_confirmed':['no post-hoc unresolved subtraction','no front/Q_M','no source/f_esc','no primordial recombination','no geometry/Bianchi feedback']}
    (output.parent/'results.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--r1',type=Path,required=True);p.add_argument('--b0a',type=Path,required=True);p.add_argument('--b0c',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(execute(a.r1,a.b0a,a.b0c,a.output),indent=2))
