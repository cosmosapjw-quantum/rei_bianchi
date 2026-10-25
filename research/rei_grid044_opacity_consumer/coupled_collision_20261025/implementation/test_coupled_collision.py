"""Single bounded finite-operator suite; all scientific imports charged by runner."""
import json
import os
from pathlib import Path
import platform
import traceback
import numpy as np
from coupled_collision import Collision,source_fixture,INPUTS,SPECIES,BLOCKS,EDGES,CHI,C,DIM,B,K,X,Q,EPS

OUT=Path(os.environ['COUPLED_COLLISION_OUTPUT_DIR']);checks=[];payload={}

def clean(x):
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def write(name,x):(OUT/name).write_text(json.dumps(clean(x),indent=2,allow_nan=False)+'\n')
def check(name,passed,**details):
    checks.append({'name':name,'pass':bool(passed),**clean(details)})
    write('checks_partial.json',checks)

def relative(a,b):
    a=np.asarray(a);b=np.asarray(b);scale=np.abs(a)+np.abs(b)
    return float(np.max(np.divide(np.abs(a-b),scale,out=np.zeros_like(scale,dtype=float),where=scale!=0)))

def ratio(residual,terms):
    scale=float(np.sum(np.abs(terms)))
    return abs(float(residual))/scale if scale else (0. if residual==0 else float('inf'))

def oracle(E,S,sigma,z,nref,alpha):
    """Scalar primitive events, independently accumulated; no kernel call."""
    f=np.zeros(DIM);events=np.zeros((13,16));J=np.zeros((DIM,DIM))
    for ei,(lo,up,ch) in enumerate(EDGES):
        for j,energy in enumerate(E):
            a=C*nref*sigma[ch,j];r=a*z[16+lo]*z[j];events[ei,j]=r
            contributions=((j,-1.),(16+lo,-1.),(16+up,1.),(B,CHI[ch]),(K,energy-CHI[ch]))
            for row,w in contributions:
                f[row]+=w*r
                J[row,j]+=w*a*z[16+lo]
                J[row,16+lo]+=w*a*z[j]
    for si in range(2):
        for j,energy in enumerate(E):
            f[j]+=alpha[si]*S[si,j];f[X]+=energy*alpha[si]*S[si,j]
    return f,J,events

BLOCK_SLICES={'photon_photon':(slice(0,16),slice(0,16)),
 'photon_target':(slice(0,16),slice(16,37)),
 'target_photon':(slice(16,37),slice(0,16)),
 'target_target':(slice(16,37),slice(16,37)),
 'energy_photon_target':(slice(37,40),slice(0,37)),
 'all':(slice(None),slice(None))}

def cs_metrics(numeric,analytic):
    out={}
    for name,(rows,cols) in BLOCK_SLICES.items():
        a=analytic[rows,cols];d=numeric[rows,cols]-a;active=a!=0
        nonzero=float(np.max(np.abs(d[active]/a[active]))) if np.any(active) else 0.
        structural=float(np.max(np.abs(d[~active]))) if np.any(~active) else 0.
        out[name]={'active_entry_relative_max':nonzero,'structural_zero_absolute_max':structural,'active_entries':int(np.sum(active))}
    return out

try:
    E,S,sigma,z,source_rates,provider=source_fixture()
    donor=json.loads((INPUTS/'DONOR_PAYLOAD.json').read_text())['snapshots'][-1]['production_GL32']
    nref=donor['nHref_cm3']*1e6
    op=Collision(E,S,sigma,nref);alpha=np.ones(2);f,J,Ja,Jn,events,L=op.evaluate(z,alpha)
    scale=z.copy() # frozen positive coordinate scales; no unit-sized floors
    payload={'unit':'GRID044_JOINT_PHOTON_TARGET_COLLISION_20261025','scope':'Finite instantaneous operator fixture; no IVP or continuum accuracy claim',
      'state_order':list('N'+str(j) for j in range(16))+list(SPECIES)+['B','K','Xext'],
      'energy_eV':E,'sigma_m2':sigma,'source_per_ref_s':S,'source_rates_before_packet_rule':source_rates,
      'fixture_state':z,'coordinate_scales':scale,'target_fixture':'Exact prior synthetic positive API fixture; n=T=1e-20/Href, not evolved z2 targets',
      'photon_fixture':'N=1s times actual z2 source; local operator fixture only','nref_m3':nref,
      'source_relative_amplitudes':alpha,'main_Lambda':L,'RHS':f,'Jacobian_40x40':J,'source_Jacobian_40x2':Ja,
      'density_partial_fixed_per_ref_source':Jn,'events_13x16_per_ref_s':events,
      'q_ion':Q,'epsilon_eV':EPS,'new_IVPs':0,'old_suite_replays':0,
      'requested_execution_model':'gpt-6.1-sol','requested_reasoning_effort':'high','actual_runtime_model_identity':'UNEXPOSED',
      'python':platform.python_version(),'numpy':np.__version__}
    write('partial_payload.json',payload)
    expected_ratio=np.array([.9968941924505704,.9863501584763724]);got=S.sum(axis=1)/source_rates
    check('saved_continuous_normalizer_finite_rule_ratio',relative(got,expected_ratio)<=3e-12,ratios=got,continuum_accuracy_claim=False)
    check('fixed_registry_provider_and_target_mapping',nref==5.151254745827818 and len(EDGES)==13 and len(SPECIES)==21 and tuple(SPECIES)==tuple(json.loads((INPUTS/'OPACITY_PAYLOAD.json').read_text())['target_fixture']['species']) and np.all(EPS>=0),edges=EDGES)
    check('source_and_event_support_nonnegative',np.all(S>0) and np.all(sigma>=0) and np.all(events>=0) and np.all(sigma[E[None,:]<CHI[:,None]]==0))
    of,oJ,oe=oracle(E,S,sigma,z,nref,alpha)
    active=oJ!=0
    oracleJ=float(np.max(abs((J-oJ)[active]/oJ[active])))
    check('independent_scalar_event_and_derivative_oracle',relative(f,of)<=3e-12 and relative(events,oe)<=3e-12 and oracleJ<=3e-12 and np.all(J[~active]==0),RHS_relative=relative(f,of),event_relative=relative(events,oe),active_derivative_relative=oracleJ)
    # Collision FD: injection off; keeps photons on, resolves collision scale.
    fc,Jc,*_=op.evaluate(z,(0.,0.));fd=np.zeros_like(J);cs=np.zeros_like(J)
    h=2e-4
    for j in range(DIM):
        delta=np.zeros(DIM);delta[j]=h*scale[j]
        fd[:,j]=(op.evaluate(z+delta,(0.,0.))[0]-op.evaluate(z-delta,(0.,0.))[0])/(2*delta[j])
        trial=z.astype(complex);trial[j]+=1e-28j*scale[j]
        cs[:,j]=np.imag(op.evaluate(trial,alpha)[0])/(1e-28*scale[j])
    fd_error={}
    for name,(r,c) in BLOCK_SLICES.items():
        a=J[r,c];err=(fd-J)[r,c]*scale[c][None,:]
        denom=np.sum(abs(J[r,:])*scale[None,:],axis=1)
        rowerr=np.max(abs(err),axis=1)
        fd_error[name]=float(np.max(np.divide(rowerr,denom,out=np.zeros_like(rowerr),where=denom!=0)))
        if np.any(denom==0) and np.any(rowerr[denom==0]!=0):fd_error[name]=float('inf')
    cm=cs_metrics(cs,J)
    check('centered_collision_FD_all_blocks',max(fd_error.values())<=2e-5,block_scaled_max=fd_error,step_in_coordinate_scales=h,source_off_photons_on=True)
    check('complex_step_every_active_entry_and_structural_zero',all(v['active_entry_relative_max']<=2e-12 and v['structural_zero_absolute_max']==0 for v in cm.values()),blocks=cm)
    rare={}
    for name,cols in [('trace_T',[21,22]),('Li6',[29,30,31,32]),('Li7',[33,34,35,36])]:
        aa=J[:,cols];dd=(cs-J)[:,cols];mask=aa!=0
        rare[name]={'active_entries':int(mask.sum()),'relative_max':float(np.max(abs(dd[mask]/aa[mask])))}
    check('rare_isotope_crossblock_coverage',all(v['active_entries']>0 and v['relative_max']<=2e-12 for v in rare.values()),columns=rare)
    # Source and nref parameter derivatives with state fixed.
    source_cs=np.zeros_like(Ja)
    for s in range(2):
        aa=alpha.astype(complex);aa[s]+=1e-28j
        source_cs[:,s]=np.imag(op.evaluate(z,aa)[0])/1e-28
    check('source_amplitude_columns_fixed_photon_state',relative(source_cs,Ja)<=2e-12 and np.all(Ja[16:39]==0),relative=relative(source_cs,Ja))
    dn=1e-4*nref
    nd=(Collision(E,S,sigma,nref+dn).evaluate(z,(0.,0.))[0]-Collision(E,S,sigma,nref-dn).evaluate(z,(0.,0.))[0])/(2*dn)
    check('independent_density_partial_fixed_normalized_source',relative(nd,Jn)<=2e-5,relative=relative(nd,Jn))
    g=1e-19/(DIM*scale);L0=2e-18
    lf,lJ,_,_,_,lv=op.evaluate(z,alpha,L0,g,z);lcs=np.zeros_like(J)
    for j in range(DIM):
        zz=z.astype(complex);zz[j]+=1e-28j*scale[j]
        lcs[:,j]=np.imag(op.evaluate(zz,alpha,L0,g,z)[0])/(1e-28*scale[j])
    lm=cs_metrics(lcs,lJ)
    check('affine_Lambda_recomputed_complete_quotient_Jacobian',all(v['active_entry_relative_max']<=2e-12 and v['structural_zero_absolute_max']==0 for v in lm.values()),blocks=lm,Lambda0=L0,gradient=g)
    # Identities on collision-only RHS, avoiding source cancellation in tiny physics.
    evsum=events.sum();iso=[]
    for block in BLOCKS:
        idx=16+np.array(block);iso.append(ratio(fc[idx].sum(),fc[idx]))
    charge=ratio(Q@fc[16:37]-evsum,[Q@fc[16:37],evsum])
    bind=ratio(fc[B]-EPS@fc[16:37],[fc[B],EPS@fc[16:37]])
    w=np.r_[E,np.zeros(21),1.,1.,-1.]
    energy=ratio(w@fc,w*fc);number=ratio(fc[:16].sum()+Q@fc[16:37],np.r_[fc[:16],Q*fc[16:37]])
    mass={'n':1,'H1':1,'D':2,'T':3,'He3':3,'He4':4,'Li6':6,'Li7':7}
    A=np.array([mass[name.split('_')[0]] for name in SPECIES])
    baryon=ratio(A@fc[16:37],A*fc[16:37])
    check('component_isotope_charge_binding_number_energy',max(iso+[charge,bind,energy,number,baryon])<=3e-12,isotope_by_block=iso,charge=charge,binding=bind,energy=energy,photon_electron=number,baryon=baryon)
    source=Ja@alpha
    check('source_injection_single_energy_owner',ratio(w@source,w*source)<=3e-12 and source[B]==0 and source[K]==0 and source[X]>0,energy_relative=ratio(w@source,w*source))
    # Prescribed Lambda identities include off-manifold redundant B test.
    off=z.copy();off[B]*=1.2
    off_f,*_=op.evaluate(off,(0.,0.),L0,g,z);off_L=L0+g@(off-z)
    drift=off_f[B]-EPS@off_f[16:37]+off_L*(off[B]-EPS@off[16:37])
    physical_ydot=nref*fc[16:37] # reaction source per proper m^3, main conserved reference
    bphysical=ratio(EPS@physical_ydot-nref*fc[B],[EPS@physical_ydot,nref*fc[B]])
    drift_scale=[off_f[B],EPS@off_f[16:37],off_L*(off[B]-EPS@off[16:37])]
    lambda_iso=[ratio(lf[16+np.array(b)].sum()+lv*z[16+np.array(b)].sum(),np.r_[lf[16+np.array(b)],lv*z[16+np.array(b)]]) for b in BLOCKS]
    ej=w@lJ+lv*w+(w@z)*g
    ejscale=np.sum(abs(w[:,None]*lJ),axis=0)+abs(lv*w)+abs((w@z)*g)
    ejrel=float(np.max(np.divide(abs(ej),ejscale,out=np.zeros(DIM),where=ejscale!=0)))
    check('quotient_isotopes_offconstraint_binding_and_physical_identity',max(lambda_iso+[ratio(drift,drift_scale),bphysical])<=3e-12,isotopes=lambda_iso,binding_drift=ratio(drift,drift_scale),B_physical=bphysical)
    Edot=-1e-18*E;work=Edot@z[:16]
    totalrate=op.energy_derivative(z,fc,Edot);fixedrate=op.energy_derivative(z,fc)
    work_error=relative(totalrate-fixedrate,work)
    check('energy_Jacobian_and_prescribed_redshift_work',ejrel<=3e-12 and ratio(w@lf+lv*(w@z),np.r_[w*lf,lv*w*z])<=3e-12 and work_error<=3e-12 and ratio(totalrate-work,np.r_[w*fc,work])<=3e-12,Jacobian_relative=ejrel,E_dot_dot_N=float(work),work_relative=work_error,work_included_once=True)
    k=7.;u=1e-19
    rf=Collision(E,S/k,sigma,nref*k).evaluate(z/k,alpha,L0+u)[0]
    expected=op.evaluate(z,alpha,L0)[0]/k-u*z/k
    check('proper_reference_rescaling_with_time_dependent_ratio',relative(rf,expected)<=3e-12,relative=relative(rf,expected),ratio=k,dot_ratio_over_ratio=u)
    # Fixed-radiation target generator, full crossblock has negative entries.
    tt=J[16:37,16:37].copy();np.fill_diagonal(tt,0)
    face=[]
    for j in range(DIM):
        facez=z.copy();facez[j]=0;face.append(op.evaluate(facez,alpha)[0][j]>=0)
    check('tangent_faces_target_generator_and_nonMetzler_crossblock',all(face) and np.all(tt>=0) and np.any(J[:16,16:37]<0),faces=face)
    dark=z.copy();dark[:16]=0;dark_f=op.evaluate(dark,alpha)[0]
    zero=z.copy();zero[16+np.array([0,5,6])]=0;zf,_,_,_,ze,_=op.evaluate(zero,alpha)
    edge_zero=[]
    for ei,(lo,up,ch) in enumerate(EDGES):
        facez=z.copy();facez[16+lo]=0
        edge_zero.append(bool(np.all(op.evaluate(facez,alpha)[4][ei]==0)))
    check('each_edge_zero_lower_state_zero_event',all(edge_zero),edge_zero=edge_zero)
    check('radiation_off_source_off_zero_nT_and_neutron_controls',np.all(dark_f[16:39]==0) and np.all(dark_f[:16]>0) and np.any(fc[:16]<0) and np.all(zf[16+np.array([0,5,6])]==0) and np.all(ze[2]==0) and fc[16]==0 and np.all(J[16]==0))
    rejects=[]
    for mutate in ('negative_state','nan_state','wrong_state','negative_alpha','bad_nref','bad_energy','negative_sigma','negative_source','bad_gradient'):
        try:
            zz=z.copy()
            if mutate=='negative_state':zz[0]=-1;op.evaluate(zz)
            elif mutate=='nan_state':zz[0]=np.nan;op.evaluate(zz)
            elif mutate=='wrong_state':op.evaluate(zz[:-1])
            elif mutate=='negative_alpha':op.evaluate(zz,(-1.,1.))
            elif mutate=='bad_nref':Collision(E,S,sigma,0)
            elif mutate=='bad_energy':Collision(E*0,S,sigma,nref)
            elif mutate=='negative_sigma':Collision(E,S,-sigma,nref)
            elif mutate=='negative_source':Collision(E,-S,sigma,nref)
            elif mutate=='bad_gradient':op.evaluate(zz,gradient=np.zeros(39),anchor=zz)
        except ValueError:rejects.append(True)
        else:rejects.append(False)
    check('strict_finite_physical_domain_no_clipping',all(rejects),rejected=rejects)
    payload['finite_rule_ratios']=got;payload['CS_blocks']=cm;payload['FD_blocks']=fd_error;payload['Lambda_CS_blocks']=lm;payload['rare_isotopes']=rare
    write('fixture_payload.json',payload);write('test_results.json',{'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'all_pass':all(c['pass'] for c in checks)})
    print(json.dumps({'passed':sum(c['pass'] for c in checks),'total':len(checks)}),flush=True)
    raise SystemExit(0 if all(c['pass'] for c in checks) else 1)
except Exception as exc:
    write('partial_payload.json',payload);write('failure.json',{'exception':repr(exc),'traceback':traceback.format_exc()});raise
