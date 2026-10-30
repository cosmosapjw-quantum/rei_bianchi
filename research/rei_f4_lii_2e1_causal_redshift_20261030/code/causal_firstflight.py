#!/usr/bin/env python3
"""Native BASS193 passive Li II 2E1 photon-pair cosmological redshifting and first absorption.

Conditional on PR283 1969 Li II Table II OCR source and all-singlet branch of all
kinematically eligible Li I K events. Archived BASS21 mean-FLRW-background
(21 species Y_i, nb, H) is prescribed and linearly interpolated in ln(a).
This is a non-self-consistent reduced radiative transfer, no new IVP.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, pathlib, tempfile, zipfile
from contextlib import contextmanager
from dataclasses import dataclass
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENT=ROOT/'source/PR284_FULL.zip'
PARENT_SHA='fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9'
PR283_SHA='91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a'
ORIGINAL_OWNER='cc602e209e7deeb511ab2a1f3b2268d55206c43c'
PREV_HEAD='661f34c5216aa52402be6f9db5c16ab2e55ecfb3'
CAT=('ESC','H_I','He_I','He_II','Li_I')
C=299792458.0


def sha(data):
    return hashlib.sha256(data).hexdigest()

@contextmanager
def owner():
    raw=PARENT.read_bytes()
    if sha(raw)!=PARENT_SHA:raise ValueError('PR284_IMMUTABLE_SHA_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='rei_causal_source_') as tmp:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if z.testzip() is not None:raise ValueError('PR284_CRC_FAIL')
            inner=z.read('REI_F4_LII_2E1_PAIR_CORRELATED_20261030/source/PR283_FULL.zip')
        if sha(inner)!=PR283_SHA:raise ValueError('PR283_IMMUTABLE_SHA_MISMATCH')
        with zipfile.ZipFile(io.BytesIO(inner)) as z:
            if z.testzip() is not None:raise ValueError('PR283_CRC_FAIL')
            z.extractall(tmp)
        p=pathlib.Path(tmp)/'REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030/code/two_e1_source.py'
        spec=importlib.util.spec_from_file_location('source_frozen_283',p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        if m.OWNER!=ORIGINAL_OWNER:raise ValueError('ORIGINAL_OWNER_MISMATCH')
        yield m


def simpson_coeff(x):
    assert len(x)%2==1 and np.max(abs(np.diff(x)-np.diff(x)[0]))<1e-13
    weights=np.ones(len(x));weights[1:-1:2]=4;weights[2:-1:2]=2
    return weights*(x[1]-x[0])/3


def hat_family(y,bare,m):
    # Exactly the normalized piecewise-linear positive nodal cone with a_0=0.
    x=m.Y_TAB; dy=x[1]-x[0]
    allhat=np.maximum(1-abs(y[None,:]-x[:,None])/dy,0)
    allhat=np.where(allhat<2e-13,0,allhat)
    hats=allhat[1:]
    steps=np.array([allhat[j:].sum(axis=0) for j in range(1,len(x))])
    # Numerical integration versus exact trapezoidal areas is checked by caller.
    H=hats*bare[None,:]
    M=steps*bare[None,:]
    H=H/H.sum(axis=1,keepdims=True)
    M=M/M.sum(axis=1,keepdims=True)
    return H,M


def _float_observables(m,net,order):
    y,w=m.nodes_weights(order,net.transition_energy_eV)
    a=np.interp(y,m.Y_TAB,m.A_TAB)
    assert np.all(a>0)
    bare=w*m.PAIR_NORM/a
    assert abs(bare.sum()-.5)<2e-13
    H,M=hat_family(y,bare,m)
    # Common spectrum shape, exactly normalized (quadrature approximation).
    assert abs(w.sum()-1)<1e-13
    assert np.max(abs(H.sum(axis=1)-1))<2e-13
    assert np.max(abs(M.sum(axis=1)-1))<2e-13
    return y,w,H,M


def lightcone(m,net,x,H,nb,Y,k,order=16,substeps=4,check_source=True):
    if order<2 or substeps<1:raise ValueError('DISCRETIZATION_DOMAIN')
    if not 0<=k<len(x):raise ValueError('EMISSION_EPOCH')
    y,w,hat,mon=_float_observables(m,net,order)
    n=len(y); E0=np.concatenate([y*m.E_SINGLET_EV,(1-y)*m.E_SINGLET_EV])
    surv=np.ones(2*n)
    abs_by_cat=np.zeros((4,2*n)); eprimary=np.zeros(2*n); ebinding=np.zeros(2*n)
    eredshift=np.zeros(2*n)
    transitions=net.transition_energy_eV
    # Every output is per original emitted pair and native historical photons.
    byarrival=[]
    for j in range(k,len(x)-1):
        step_abs=np.zeros((4,2*n));step_primary=np.zeros(2*n);step_binding=np.zeros(2*n)
        step_work=np.zeros(2*n)
        dx=(x[j+1]-x[j])/substeps
        for s in range(substeps):
            t0=x[j]+s*dx; t1=t0+dx; tm=(t0+t1)/2
            f=(tm-x[j])/(x[j+1]-x[j])
            Hm=np.exp(np.log(H[j])*(1-f)+np.log(H[j+1])*f)
            nbm=np.exp(np.log(nb[j])*(1-f)+np.log(nb[j+1])*f)
            Ym=(1-f)*Y[j]+f*Y[j+1]
            if Hm<=0 or nbm<=0 or np.min(Ym)<-1e-20:raise ValueError('BATH_INVALID')
            Ep=E0*np.exp(-(tm-x[k]))
            sigma,_=net.photo_cross_sections(Ep)
            K=nbm*Ym[:,None]*sigma
            kapp=K.sum(axis=0)
            dtau=kapp*C/Hm*dx
            if np.min(dtau)<0:raise ValueError('NEGATIVE_TAU')
            dabs=surv*(-np.expm1(-dtau))
            split=np.divide(K,kapp[None,:],out=np.zeros_like(K),where=kapp[None,:]>0)
            per_ion=split*dabs[None,:]
            catabs=np.array([per_ion[list(m.CAT_GROUPS[g])].sum(axis=0) for g in CAT[1:]])
            step_abs+=catabs
            binding_i=(per_ion*transitions[:,None])
            step_binding+=binding_i.sum(axis=0)
            # Do not place absorption energy artificially at the midpoint:
            # for constant optical hazard lambda per dx, E(t)=E_start exp(-u),
            # exact integrated absorbed photon energy is
            # S_start*E_start*lambda/(lambda+1)*(1-exp(-(lambda+1)*dx)).
            # This removes a substantial first-order redshift-energy error
            # in optically thick cells while keeping the archived bath fixed.
            lam=kapp*C/Hm
            E_start=E0*np.exp(-(t0-x[k]))
            absenergy=surv*E_start*lam/(1+lam)*(-np.expm1(-(1+lam)*dx))
            per_ion_energy=split*absenergy[None,:]
            kinetic_i=per_ion_energy-binding_i
            if np.min(kinetic_i)<-3e-13:raise AssertionError('PHOTON_THRESHOLD_ENERGY')
            step_primary+=np.maximum(kinetic_i,0).sum(axis=0)
            new_surv=surv*np.exp(-dtau)
            # Non-thermal, cosmological kinematic redshift work is not gas heat.
            work=surv*E_start-new_surv*E0*np.exp(-(t1-x[k]))-absenergy
            if np.min(work)<-1e-12:raise AssertionError('NEGATIVE_COSMIC_WORK')
            step_work+=np.maximum(work,0)
            surv=new_surv
        abs_by_cat+=step_abs; ebinding+=step_binding; eprimary+=step_primary
        eredshift+=step_work
        def av(q):return float(np.sum(w*(q[:n]+q[n:])))
        t=dict(emission_epoch=k,arrival_epoch=j+1,z_emission=float(m._z_source[k]) if hasattr(m,'_z_source') else float(21*np.exp(-x[k])-1),
               z_arrival=float(21*np.exp(-x[j+1])-1),x_emission=float(x[k]),x_arrival=float(x[j+1]),
               conditional_first_abs_H_I=av(step_abs[0]),conditional_first_abs_He_I=av(step_abs[1]),
               conditional_first_abs_He_II=av(step_abs[2]),conditional_first_abs_Li_I=av(step_abs[3]),
               conditional_primary_e_eV=av(step_primary),conditional_ionization_binding_eV=av(step_binding),
               conditional_cosmological_redshift_work_eV=av(step_work),
               survived_photons_after_interval=av(surv))
        byarrival.append(t)
    cat=np.concatenate((surv[None,:],abs_by_cat),axis=0)
    pair_joint=np.einsum('n,an,bn->ab',w,cat[:,:n],cat[:,n:],optimize=True)
    if abs(pair_joint.sum()-1)>5e-11:raise AssertionError('PAIR_NORM')
    P0=pair_joint[0,0];P1=pair_joint[0,1:].sum()+pair_joint[1:,0].sum();P2=pair_joint[1:,1:].sum()
    def av(q):return float(np.sum(w*(q[:n]+q[n:])))
    sc=av(surv); ep=av(eprimary);bind=av(ebinding);wr=av(eredshift)
    escaped_eV=av(surv*E0*np.exp(-(x[-1]-x[k])))
    if abs(ep+bind+wr+escaped_eV-m.E_SINGLET_EV)>3e-11:raise AssertionError('PAIR_ENERGY')
    if abs(sc+av(abs_by_cat.sum(axis=0))-2)>3e-12:raise AssertionError('PHOTON_COUNT')
    if abs(P0+P1+P2-1)>5e-12:raise AssertionError('PAIR_OUTCOMES')
    obs=2-cat[0,:n]-cat[0,n:]
    two=(1-cat[0,:n])*(1-cat[0,n:])
    h1=np.sum(pair_joint,axis=1)[0]; h2=np.sum(pair_joint,axis=0)[0]
    tv=.5*abs(pair_joint-np.outer(pair_joint.sum(axis=1),pair_joint.sum(axis=0))).sum()
    source_metrics={
        'mean_absorptions_per_pair':av(abs_by_cat.sum(axis=0)),
        'P0':float(P0),'P1':float(P1),'P2':float(P2),
        'absorbed_H_I':av(abs_by_cat[0]),'absorbed_He_I':av(abs_by_cat[1]),
        'absorbed_He_II':av(abs_by_cat[2]),'absorbed_Li_I':av(abs_by_cat[3]),
        'cosmological_redshift_work_eV':wr,'absorbed_primary_electron_eV':ep,
        'absorbed_binding_eV':bind,'survivor_eV_at_z2':escaped_eV,
        'survived_photons_at_z2':sc,'P_two_independent_marginals':float((1-h1)*(1-h2)),
        'pair_absorption_covariance':float(P2-(1-h1)*(1-h2)),
        'joint_TV_from_marginal_independence':float(tv)}
    for title,fun in [('positive',hat),('monotone',mon)]:
        val=fun@obs; dbl=fun@two
        source_metrics[title+'_mean_abs_bound_min']=float(np.min(val))
        source_metrics[title+'_mean_abs_bound_max']=float(np.max(val))
        source_metrics[title+'_P2_bound_min']=float(np.min(dbl))
        source_metrics[title+'_P2_bound_max']=float(np.max(dbl))
    return source_metrics,byarrival,pair_joint,obs,two,(y,w,hat,mon)


def generate(order=16,substeps=4,emission_indices=None,progress=False):
    with owner() as m:
        data,H,nb,epochs,bins,net=m.load_original()
        x=data['x'];z=data['z'];Y=data['Y']
        m._z_source=z
        if Y.shape!=(193,21) or len(x)!=193:raise ValueError('BASS193_SHAPE')
        if np.max(abs(nb/nb[0]-np.exp(-3*x)))>5e-14:raise AssertionError('BARYON_DILUTION')
        K=np.array([float(r['K_events_per_baryon_s']) for r in epochs])
        forced=np.array([float(r['triplet_forced_events_per_baryon_s']) for r in epochs])
        Ks=K-forced
        if np.min(Ks)<-1e-40:raise AssertionError('NEGATIVE_KS')
        Ks=np.maximum(Ks,0)
        coeff=simpson_coeff(x)*Ks/H
        selection=range(len(x)) if emission_indices is None else emission_indices
        summary_rows=[]; time_rows=[]; pair_rows=[]
        global_hat=None;global_mon=None;global_obs=None;global_two=None
        arrival_sum=np.zeros((len(x)-1,4));arrival_abs_energy=np.zeros((len(x)-1,2))
        total_exposure=0.;integrated={}
        for k in selection:
            if progress and k%16==0:print(f'CAUSAL_PROGRESS epoch={k}/193',flush=True)
            one,steps,joint,obs,two,(yv,ww,hat,mon)=lightcone(m,net,x,H,nb,Y,k,order,substeps)
            rate=float(Ks[k]);scale=coeff[k]
            summary_rows.append(dict(epoch=k,z_emission=float(z[k]),x_emission=float(x[k]),K_possible_singlet_per_baryon_s=rate,
                                     conditional_event_source_count_per_baryon=float(scale),**one))
            for tr in steps:
                time_rows.append(tr)
                j=tr['arrival_epoch']-1
                for n_,a in enumerate(('H_I','He_I','He_II','Li_I')):
                    arrival_sum[j,n_]+=scale*tr['conditional_first_abs_'+a]
                arrival_abs_energy[j,0]+=scale*tr['conditional_primary_e_eV']
                arrival_abs_energy[j,1]+=scale*tr['conditional_ionization_binding_eV']
            for i,c1 in enumerate(CAT):
                for j,c2 in enumerate(CAT):
                    pair_rows.append(dict(epoch=k,z_emission=float(z[k]),low_outcome=c1,high_outcome=c2,
                                          probability=float(joint[i,j]),conditional_event_per_baryon=float(scale*joint[i,j])))
            for name,val in one.items():
                integrated[name]=integrated.get(name,0)+scale*val
            total_exposure+=scale
            if global_obs is None:
                global_obs=np.zeros_like(obs);global_two=np.zeros_like(two)
                global_hat=hat;global_mon=mon
            global_obs+=scale*obs;global_two+=scale*two
        arrival_rows=[]
        for j in range(len(x)-1):
            arrival_rows.append(dict(first_absorption_interval=j,arrival_z_high=float(z[j]),arrival_z_low=float(z[j+1]),
               incoming_integrated_H_I_per_baryon=float(arrival_sum[j,0]),
               incoming_integrated_He_I_per_baryon=float(arrival_sum[j,1]),
               incoming_integrated_He_II_per_baryon=float(arrival_sum[j,2]),
               incoming_integrated_Li_I_per_baryon=float(arrival_sum[j,3]),
               primary_electron_eV_per_baryon=float(arrival_abs_energy[j,0]),
               binding_eV_per_baryon=float(arrival_abs_energy[j,1])))
        # Global generator source is shared across all emission epochs.
        bounds={}
        for title,fun in [('positive',global_hat),('monotone',global_mon)]:
            F=fun@global_obs;G=fun@global_two
            bounds[title]={'global_ionization_count_per_baryon':[float(F.min()),float(F.max())],
                'global_P_two_absorption_events_per_baryon':[float(G.min()),float(G.max())],
                'generator_argmax':int(np.argmax(F))+1,'generator_argmin':int(np.argmin(F))+1}
        total_energy=total_exposure*m.E_SINGLET_EV
        closed=integrated['cosmological_redshift_work_eV']+integrated['absorbed_binding_eV']+integrated['absorbed_primary_electron_eV']+integrated['survivor_eV_at_z2']
        if abs(total_energy-closed)>2e-13*max(total_energy,1e-200):raise AssertionError('INTEGRATED_ENERGY')
        if abs(arrival_sum.sum()-integrated['mean_absorptions_per_pair'])>3e-13*max(arrival_sum.sum(),1e-200):raise AssertionError('ARRIVAL_PHOTON_NORM')
        generator_integrals={q:{'mean_abs':(f@global_obs).tolist(),'P2':(f@global_two).tolist()} for q,f in [('positive',global_hat),('monotone',global_mon)]}
        result={'schema':'REI_F4_LII_2E1_PASSIVE_CAUSAL_REDSHIFT_V1',
                'scope':'Original saved BASS193 FRW-mean background, conditional singlet spectral source, first collision only, no new IVPs, NOT full self-consistent Bianchi photon transfer',
                'parent_PR':284,'parent_HEAD':PREV_HEAD,'parent_source_SHA256':PARENT_SHA,
                'original_BASS_owner':ORIGINAL_OWNER,
                'model':{'background':'isotropic effective a(t), archived H nb Y, log H/nb + linear Y between adjacent saved x; no angular Bianchi redshift',
                         'energy_redshift':'E(x)=E_emit exp(-(x-x_emit))',
                         'photo_first_hazard':'c nb(x) Y_i(x) sigma_i(E(x))/H(x) per dln(a)',
                         'midpoint_hazard_subintervals':substeps,
                         'spectral_gauss_order':order,'source_spectrum':'PR283 scanned Li II 1969 Table II, OCR-partial; 21 knots piecewise linear',
                         'singlet_yield':'1 among kinematically allowed K events only CONDITIONALLY, not source-known',
                         'positive_cone':'20 nonnegative piecewise-linear nodal hat generators with a0=0',
                         'monotone_cone':'additional optional unverified a0<=a1<=...<=a20'},
                'counts':{'saved_epochs':len(x),'computed_emission_epochs':len(summary_rows),
                          'emission_arrival_pairs':len(time_rows),'pair_channel_rows':len(pair_rows),
                          'absorber_categories':len(CAT)-1,'original_K_event_rows':len(bins),'new_IVPs':0},
                'integrated_conditional_source_pairs_per_baryon':float(total_exposure),
                'integrated_conditional_per_baryon':{k:float(v) for k,v in integrated.items()},
                'energy_conservation':{'input_eV_per_baryon':float(total_energy),
                                       'accounted_eV_per_baryon':float(closed),
                                       'residual_eV_per_baryon':float(total_energy-closed),
                                       'redshift_work_is_not_heat':True},
                'global_shape_cone_bounds':bounds,'global_linear_generator_integrals_for_chunk_combine':generator_integrals,
                'gates':{'working_DAG':'33/88','central_DAG':'28/88','F4_DAG':'4/7','canonical_physical_delta':0,
                         'new_scoped_science_data':'1/1', 'F4':'PARTIAL','L4_ready':False,'NO_MORE_IVPS':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,'AUTO_NEXT_NODE':False,'PRODUCTION':'HOLD',
                         'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN',
                         'actual_singlet_branching':'UNBOUND','real_Bianchi_anisotropic_directional_redshift':'NOT_RUN',
                         'full_REI17_BASS21_common_chemistry_clock':'UNBOUND','secondary_electron_thermal_deposition':'UNBOUND',
                         'Drake_1969_original_page_direct_visual_check':'NOT_VERIFIED',
                         'PR285_original_full_ZIP_cloud_backup':'BLOCKED_SEPARATE'}}
        return result,summary_rows,time_rows,pair_rows,arrival_rows


def write_csv(path,rows):
    with open(path,'w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def write():
    result,emissions,flights,pairs,arrivals=generate(progress=True)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for name,rows in [('EMISSIONS_193.csv',emissions),('FIRST_FLIGHT_KERNEL.csv',flights),
                      ('JOINT_OUTCOMES_4825.csv',pairs),('ABSORPTION_ARRIVALS_192.csv',arrivals)]:
        write_csv(out/name,rows)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'counts':result['counts'],'integrated':result['integrated_conditional_per_baryon'],
       'bounds':result['global_shape_cone_bounds'],'energy':result['energy_conservation']},indent=2))
if __name__=='__main__':write()
