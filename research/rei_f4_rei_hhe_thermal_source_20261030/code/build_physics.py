#!/usr/bin/env python3
"""Source-qualified REI H/He point-thermal RHS on actual frozen BASS21 193 epochs.

BASS photo counts/spectrum, Grackle-v3.4.1 REI Rust-source translated
kinetics/thermal expressions, BASS H,T,n_b,UV, and optional AXBI metric K proxy.
NO REI17 full RHS, NO IVP, NO self-consistent source substitution or actual T evolution.
"""
from __future__ import annotations
import csv,hashlib,importlib.util,io,json,math,pathlib,tempfile,types,zipfile
import numpy as np
from scipy.integrate import simpson
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'source'/'PR293_FULL.zip'
SHA_293='2149e9651c393dc9c68520ef81b95ff5b22f94408da9131281466fa108711217'
PARENT='REI_F4_COMMON_FJ_ELECTRON_THERMAL_CLOCK_20261030/'
PR276='rei_f4_bass193_common_bath_20261030/'
KB_ERG=1.380649e-16
EV_ERG=1.602176634e-12
H_PLANCK=6.62607015e-27
C_CM=29979245800.0
SIGMA_T=6.6524587051e-25
M_E_G=9.1093837139e-28
T_CMB0=2.7255 # external CMB monopole assumption, not BASS source input
CHI=np.array([13.598434599702,24.587389011,54.41776])
ION_IDX=[1,10,11]; HHE_IDX=[1,2,10,11,12]

def sha(b):return hashlib.sha256(b).hexdigest()
def load():
    if sha(SRC.read_bytes())!=SHA_293:raise ValueError('PARENT_SHA')
    with zipfile.ZipFile(SRC) as z:
        if z.testzip() is not None:raise ValueError('PARENT_CRC')
        pz=z.read(PARENT+'source/REI_F4_BASS193_COMMON_BATH_RATE_DELTA_20261030_FULL.zip')
        pmeta=z.read(PARENT+'results/RESULT.json')
        with zipfile.ZipFile(io.BytesIO(pz)) as q:
            rscode=q.read(PR276+'code/matched_bath.py').decode('utf-8')
            locked=np.load(io.BytesIO(q.read(PR276+'results/HHE_CHEMICAL_F_J_STATIC_193.npz')),allow_pickle=False)
            locked_matrices={k:locked[k].copy() for k in locked.files}
            locked.close()
        # Source code is embedded in immutable parent; import only the previously checked literal rate function.
        module=types.ModuleType('source_locked_grackle_igm_mirror');module.__file__='/tmp/rei_original/code/matched_bath.py'
        exec(compile(rscode,module.__file__,'exec'),module.__dict__)
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)/'parent';d.mkdir()
            for relative in ['code/bridge.py','source/REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip',
                             'source/REI_F4_BASS193_COMMON_BATH_RATE_DELTA_20261030_FULL.zip',
                             'source/REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030_FULL.zip']:
                path=d/relative;path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(z.read(PARENT+relative))
            spec=importlib.util.spec_from_file_location('source_locked_pr293_bridge',d/'code/bridge.py')
            parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
            z278=parent.load_archive('REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip')
            try:net,state,rei=parent.net_and_trajectory(z278)
            finally:z278.close()
        return net,state,rei,module.grackle_igm_source_mirror,module.chemistry_matrix,locked_matrices,json.loads(pmeta)

def cooling_rates(T):
    """REI Rust igm_rates.rs blob dc3cc0... literal expressions and units (erg/cm3/s)."""
    t=float(T);te=t/11605.0;ln_cap=69.07755278982137
    ce=np.array([7.5e-19*np.exp(-min(118348.0/t,ln_cap))/(1.+(t/1e5)**.5),
        9.1e-27*np.exp(-min(13179.0/t,ln_cap))*t**(-.1687)/(1.+(t/1e5)**.5),
        5.54e-17*np.exp(-min(473638.0/t,ln_cap))*t**(-.397)/(1.+(t/1e5)**.5)])
    lam=np.array([2*157807./t,2*285335./t,2*631515./t])
    rrh=1.778e-29*t*lam[0]**1.965/(1.+(lam[0]/.541)**.502)**2.697
    rrhe=3.e-14*1.3806504e-16*t*lam[1]**.654 # source literal KBOLTZ (not EOS kB)
    rrheiii=8.*1.778e-29*t*lam[2]**1.965/(1.+(lam[2]/.541)**.502)**2.697
    drraw=1.24e-13*t**(-1.5)*np.exp(-min(470000./t,ln_cap))*(1.+.3*np.exp(-min(94000./t,ln_cap)))
    dr_cooling=0. if te<=.8 else drraw
    brem=1.43e-27*t**.5*(1.1+.34*np.exp(-((5.5-math.log10(t))**2)/3.))
    return ce,np.array([rrh,rrhe,rrheiii]),dr_cooling,drraw,brem

def point_thermal(T,z,H,nh,nhe,ne,ab,ion,photo_gamma,heat_abs,coeff,compton=True):
    ci_cm,rr_cm,dr_cm=coeff[:3],coeff[3:6],coeff[6]
    ce_rates,rr_cool_rates,dr_cool_coeff,dr_raw,brem=cooling_rates(T)
    photo=ab*photo_gamma
    ci=ne*ab*ci_cm
    rr=ne*ion*rr_cm
    dr=ne*ion[1]*dr_cm
    ce=np.array([ne*ab[0],ne*ne*ion[1],ne*ion[1]])*ce_rates
    ci_sink=np.dot(CHI*EV_ERG,ci)
    rr_sink=np.dot(ne*ion,rr_cool_rates)
    dr_sink=ne*ion[1]*dr_cool_coeff
    ff=ne*(ion[0]+ion[1]+4*ion[2])*brem
    rad_kin=rr_sink+dr_sink+float(sum(ce))+ff
    heat=np.dot(ab,heat_abs)
    bind=np.dot(CHI*EV_ERG,photo)
    capture=np.dot(CHI*EV_ERG,rr)+CHI[1]*EV_ERG*dr
    Tcmb=T_CMB0*(1+z)
    a_rad=8*np.pi**5*KB_ERG**4/(15*H_PLANCK**3*C_CM**3)
    cmbcoef=4*SIGMA_T*a_rad*KB_ERG/(M_E_G*C_CM)
    cmb=cmbcoef*ne*Tcmb**4*(Tcmb-T) if compton else 0.
    thermal=heat-ci_sink-rad_kin+cmb
    binding=bind+ci_sink-capture
    escape=capture+rad_kin
    photo_input=bind+heat
    energy_residual=thermal+binding+escape-photo_input-cmb
    fwd=photo+ci
    dh=fwd[0]-rr[0]
    dhe1=fwd[1]-rr[1]-dr
    dhe2=fwd[2]-rr[2]
    dNe=dh+dhe1+dhe2
    particles=nh+nhe+ne
    u=1.5*KB_ERG*T*particles
    w=u/nh
    expansion=2*H*u
    wdot=(thermal-expansion)/nh
    tdot=2*nh*wdot/(3*KB_ERG*particles)-T*dNe/particles
    return dict(photo=photo,ci=ci,rr=rr,dr=dr,ce=ce,freefree=ff,ci_sink=ci_sink,rr_sink=rr_sink,
       dr_sink=dr_sink,cmb=cmb,heat=heat,bind=bind,capture=capture,rad_kin=rad_kin,
       thermal=thermal,binding=binding,escape=escape,photo_input=photo_input,energy_residual=energy_residual,
       dNe=dNe,particles=particles,u=u,w=w,expansion=expansion,wdot=wdot,tdot=tdot,
       tdot_thermal=2*thermal/(3*KB_ERG*particles),tdot_expansion=-2*H*T,
       tdot_number=-T*dNe/particles,Tcmb=Tcmb,
       net_h=dh,net_he1=dhe1,net_he2=dhe2)

def calculate():
    net,s,rei,grackle,chemistry_matrix,locked_matrices,parent=load()
    Y=s['Y'];x=s['x'];z=s['z'];di={str(n):s['diagnostics'][:,i] for i,n in enumerate(s['diagnostic_names'])}
    H=di['H'];nb=di['nb_m3'];T=di['T_K'];UV=di['uv_scale'];t=di['elapsed_s'];b=di['b']
    q=np.asarray(net.q,float);A=np.asarray(net.A,float)
    # This K is *only* the axbi axisymmetric diagonal convention; it is not the BASS source K owner.
    bdot=np.gradient(b,t,edge_order=2)
    Kperp=-H+bdot;Kparallel=-H-2*bdot
    assert max(abs(2*Kperp+Kparallel+3*H))<1e-27
    rows=[];events=[];F_local=[];J_local=[];J_full_bath=[];max_energy_res=0.;max_photo_res=0.;max_legacy_F=0.;max_legacy_J=0.
    for i in range(len(x)):
        y=Y[i];rates=net.rates(T[i],UV[i]);nat=net.evaluate(y,T[i],UV[i],nb[i])
        if abs(A@nat['dY_dt'])>2e-21:raise AssertionError('BASS_BARYON_F')
        hsum=float(sum(y[[1,2]]));hesum=float(sum(y[[10,11,12]]))
        nH=nb[i]*hsum/1e6;nHe=nb[i]*hesum/1e6
        ab=np.array([y[1],y[10],y[11]],float)*nb[i]/1e6
        ions=np.array([y[2],y[11],y[12]],float)*nb[i]/1e6
        neH=(y[2]+y[11]+2*y[12])*nb[i]/1e6
        neAll=(q@y)*nb[i]/1e6
        photo_gam=np.asarray(rates['photo_s'],float)[ION_IDX]
        heat_per=np.asarray(rates['primary_kinetic_power_per_ion_W'],float)[ION_IDX]*1e7
        # BASS photo energy thresholds are rounded in its native source and do not
        # equal REI's finer ionization thresholds. Source-event identity is exact;
        # the energy-port owner mismatch is a measured source-binding defect.
        BASS_CHI=np.asarray(net.transition_energy_eV,float)[ION_IDX]
        incoming_BASS=np.asarray(rates['absorbed_power_per_ion_W'],float)[ION_IDX]*1e7
        native_abs_power=float(np.dot(ab,incoming_BASS))
        threshold_defect=float(np.dot(ab*photo_gam,(CHI-BASS_CHI)*EV_ERG))
        assert abs(native_abs_power-(np.dot(ab,heat_per)+np.dot(ab*photo_gam,BASS_CHI*EV_ERG))) < 2e-36
        actual=np.array([-nat['photo_rhs'][1],-nat['photo_rhs'][10],nat['photo_rhs'][12]])
        predicted=y[ION_IDX]*photo_gam
        pp=float(np.max(abs(actual-predicted)))
        max_photo_res=max(max_photo_res,pp)
        if pp>2e-24:raise AssertionError('OWNER_PHOTO_PARTITION')
        coeff,flags=grackle(float(T[i]))
        # EXACT REI point chemistry generator (from source-translated igm_rates),
        # with BASS native photon source replacing REI external gamma, not adding to it.
        U=np.array([1,2,10,11,12]);Q5=np.array([0.,1.,0.,1.,2.]);X=y[U]
        Gphoto=net._Gphoto[np.ix_(U,U)]*UV[i]
        Mr=chemistry_matrix(coeff*1e-6)  # source coefficients cm3/s -> m3/s
        f5=Gphoto@X+(neH*1e6)*(Mr@X)
        j5=Gphoto+(neH*1e6)*Mr+nb[i]*np.outer(Mr@X,Q5)
        # Full BASS21 electron-bath cross-J, with other species held fixed at the point.
        j5full=nb[i]*np.outer(Mr@X,q)
        j5full[:,U]+=(Gphoto+(neAll*1e6)*Mr)
        f5_common=Gphoto@X+(neAll*1e6)*(Mr@X)
        legacy_f=locked_matrices['F_REI_HHe_only_ne'][i]
        legacy_j=locked_matrices['J_REI_HHe_only_ne'][i]
        max_legacy_F=max(max_legacy_F,float(np.max(abs(f5-legacy_f))))
        max_legacy_J=max(max_legacy_J,float(np.max(abs(j5-legacy_j))))
        if np.max(abs(f5-legacy_f))>3e-24 or np.max(abs(j5-legacy_j))>2e-22:
            raise AssertionError('SOURCE_REI_GRACKLE_FJ_CONFLICT')
        F_local.append(f5);J_local.append(j5);J_full_bath.append(j5full)
        a=point_thermal(float(T[i]),float(z[i]),float(H[i]),nH,nHe,neH,ab,ions,photo_gam,heat_per,coeff)
        eb=abs(a['energy_residual']);max_energy_res=max(max_energy_res,eb)
        # REI HHe point RHS and original BASS HHe are distinct sources: quantitative finite difference only.
        F_HII=float(a['net_h']/nH)
        F_HeII=float((a['net_he1']-a['net_he2'])/nHe)
        F_HeIII=float(a['net_he2']/nHe)
        nat_h=float(nat['dY_dt'][2]/hsum)
        nat_heii=float(nat['dY_dt'][11]/hesum)
        nat_heiii=float(nat['dY_dt'][12]/hesum)
        # Proper reference-normalized source terms; do NOT inject simultaneously with original native photo source.
        cvh=1.5*KB_ERG*(nH+nHe+neH)/nH
        recombperh=float(sum(a['rr'])+a['dr'])/nH
        ionperh=float(sum(a['ci']))/nH
        nHrefPerB=hsum
        row=dict(epoch=i,z=float(z[i]),x=float(x[i]),proper_elapsed_s=float(t[i]),H_s=float(H[i]),nb_m3=float(nb[i]),
           b_BASS=float(b[i]),b_dot_proxy_s=float(bdot[i]),K_perp_proxy_s=float(Kperp[i]),K_parallel_proxy_s=float(Kparallel[i]),
           K_trace_proxy_s=float(2*Kperp[i]+Kparallel[i]),shear_squared_proxy_s2=float(3*bdot[i]**2),
           nHref_over_nb=nHrefPerB,nHe4_over_nb=hesum,nHe4_over_nHref=hesum/hsum,
           nHref_cm3=nH,nHe4_cm3=nHe,ne_HHe_cm3=neH,ne_all_BASS_cm3=neAll,ne_omitted_isotopes_cm3=neAll-neH,
           T_BASS_saved_K=float(T[i]),T_CMB_external_K=float(a['Tcmb']),T_original_K=float(T[i]),
           HII_fraction=float(y[2]/hsum),HeII_fraction=float(y[11]/hesum),HeIII_fraction=float(y[12]/hesum),
           native_BASS_HII_fraction_dt_per_s=nat_h,native_BASS_HeII_fraction_dt_per_s=nat_heii,
           native_BASS_HeIII_fraction_dt_per_s=nat_heiii,
           REI_source_translated_HII_fraction_dt_per_s=F_HII,REI_source_translated_HeII_fraction_dt_per_s=F_HeII,
           REI_source_translated_HeIII_fraction_dt_per_s=F_HeIII,
           REI_HHe_dNe_cm3_s=float(a['dNe']),REI_HHe_photon_photoevents_per_Href_s=float(sum(a['photo'])/nH),
           REI_HHe_ci_events_per_Href_s=ionperh,REI_HHe_capture_events_per_Href_s=recombperh,
           REI_HHe_cmb_exchange_erg_per_Href_s=float(a['cmb']/nH),
           REI_HHe_photo_input_erg_per_Href_s=float(a['photo_input']/nH),
           BASS_native_HHe_absorbed_input_erg_per_Href_s=float(native_abs_power/nH),
           REI_BASS_ionization_threshold_source_defect_erg_per_Href_s=float(threshold_defect/nH),
           REI_HHe_thermal_micro_erg_per_Href_s=float(a['thermal']/nH),
           REI_HHe_binding_micro_erg_per_Href_s=float(a['binding']/nH),
           REI_HHe_escape_erg_per_Href_s=float(a['escape']/nH),
           REI_HHe_adiabatic_work_erg_per_Href_s=float(a['expansion']/nH),
           REI_HHe_primary_heat_erg_per_Href_s=float(a['heat']/nH),
           REI_HHe_ci_thermal_sink_erg_per_Href_s=float(a['ci_sink']/nH),
           REI_HHe_rr_thermal_sink_erg_per_Href_s=float(a['rr_sink']/nH),
           REI_HHe_dr_thermal_sink_erg_per_Href_s=float(a['dr_sink']/nH),
           REI_HHe_ce_thermal_sink_erg_per_Href_s=float(sum(a['ce'])/nH),
           REI_HHe_ff_thermal_sink_erg_per_Href_s=float(a['freefree']/nH),
           REI_HHe_EOS_w_erg_per_Href=float(a['w']),REI_HHe_Cv_erg_per_Href_per_K=float(cvh),
           REI_HHe_Tdot_point_K_s=float(a['tdot']),REI_HHe_Tdot_thermal_K_s=float(a['tdot_thermal']),
           REI_HHe_Tdot_expansion_K_s=float(a['tdot_expansion']),REI_HHe_Tdot_electron_loading_K_s=float(a['tdot_number']),
           T_rhs_background_status='BASS_STATE_REI_HHE_POINT_COUNTERFACTUAL_NOT_INTEGRATED',
           K_status='AXBI_CONVENTION_GRADIENT_PROXY_NOT_OWNER_CERTIFIED',
           source_status='BASS_NATIVE_PHOTO_REPLACEMENT_NOT_ADDITIVE',
           energy_owner_status='BASS_ROUNDED_CHI_VS_REI_FINE_CHI_EXPLICIT_DEFECT',
           REI_HHe_F_local_Q5_dot_per_baryon_s=float(Q5@f5),
           REI_HHe_F_common_ne_Q5_dot_per_baryon_s=float(Q5@f5_common),
           REI_HHe_J_local_max_abs_s=float(np.max(abs(j5))),
           REI_HHe_J_common_5x21_max_abs_s=float(np.max(abs(j5full))),
           REI_HHe_common_electron_pool_F_difference_max_per_baryon_s=float(np.max(abs(f5_common-f5))),
           Grackle_low_T_CI_floor_active=bool(flags['low_temperature_branch']))
        rows.append(row)
        for j,name in enumerate(('H_I','He_I','He_II')):
            events.append(dict(epoch=i,z=float(z[i]),absorber=name,source_BASS_native_photo_gamma_s=float(photo_gam[j]),
             native_photoevents_per_baryon_s=float(predicted[j]),REI_point_photoevents_per_Href_s=float(a['photo'][j]/nH),
             REI_Grackle_CI_cm3_s=float(coeff[j]),REI_Grackle_RR_cm3_s=float(coeff[3+j]),
             REI_Grackle_DR_cm3_s=float(coeff[6] if j==1 else 0.),
             REI_point_collisional_ion_events_per_Href_s=float(a['ci'][j]/nH),
             REI_point_rr_events_per_Href_s=float(a['rr'][j]/nH),
             REI_point_primary_kinetic_erg_per_Href_s=float(ab[j]*heat_per[j]/nH),
             species_source='REI_GRACKLE_FORMULA_TRANSLATION__BASS_NATIVE_PHOTON_INPUT'))
    if len(rows)!=193 or len(events)!=579:raise AssertionError('COUNTS')
    # REI point-chemistry RHS follows the independently assembled event ledger at every saved state.
    for i in range(193):
        evt=events[3*i:3*i+3]
        y=Y[i];rate=net.rates(T[i],UV[i]);nbcm=nb[i]/1e6
        assert len(evt)==3
        # Rates in event CSV are per Href; convert to BASS per baryon; photo/CI/RR/DR.
        nHref_over_nb=rows[i]['nHref_over_nb']
        evtp=np.array([v['REI_point_photoevents_per_Href_s'] for v in evt])*nHref_over_nb
        evti=np.array([v['REI_point_collisional_ion_events_per_Href_s'] for v in evt])*nHref_over_nb
        evtr=np.array([v['REI_point_rr_events_per_Href_s'] for v in evt])*nHref_over_nb
        dr=rows[i]['REI_HHe_capture_events_per_Href_s']*nHref_over_nb-sum(evtr)
        exp=np.array([-evtp[0]-evti[0]+evtr[0],evtp[0]+evti[0]-evtr[0],
            -evtp[1]-evti[1]+evtr[1]+dr,
            evtp[1]+evti[1]-evtr[1]-dr-evtp[2]-evti[2]+evtr[2],
            evtp[2]+evti[2]-evtr[2]])
        if max(abs(exp-np.array(F_local[i])))>1e-22:raise AssertionError('REI_SOURCE_EVENT_F5_PARITY')
    zvec=np.array([r['z'] for r in rows]);Hvec=np.array([r['H_s'] for r in rows]);xx=np.array([r['x'] for r in rows]);
    # Backreaction-agnostic integrated source exposures have units per Href or baryon. Not solved state deltas.
    integrate=lambda k: float(simpson([r[k]/r['H_s'] for r in rows],x=xx))
    keys=['REI_HHe_photo_input_erg_per_Href_s','REI_HHe_primary_heat_erg_per_Href_s','REI_HHe_cmb_exchange_erg_per_Href_s',
          'REI_HHe_thermal_micro_erg_per_Href_s','REI_HHe_escape_erg_per_Href_s','REI_HHe_binding_micro_erg_per_Href_s',
          'REI_BASS_ionization_threshold_source_defect_erg_per_Href_s','REI_HHe_ci_events_per_Href_s','REI_HHe_photon_photoevents_per_Href_s','REI_HHe_capture_events_per_Href_s']
    isrc={k:integrate(k) for k in keys}
    rr={'schema':'REI_F4_REI_HHE_ON_BASS193_SOURCE_THERMAL_V1','new_ivp':0,
       'source_qualified':'BASS_NATIVE_PHOTO_INPUT_X_REI_IGM_RATES_AND_THERMAL_RUST_SOURCE_TRANSLATION',
       'not_native_rei_rust_execution':True,'not_native_REI17_full_FJ':True,
       'input_lock':{'parent_PR293_ZIP':SHA_293,'REI_igm_rates_git_blob':'dc3cc028a41ac852d94835372ce13545389d1c3a',
       'REI_igm_thermal_git_blob':'0648618d9822e169e9672ac3c556f86595c3b0b6',
       'REI_bianchi_i_geometry_blob':'81dc54583b76e9dcba94c5bbc867243b04ad76b1',
       'BASS_owner_commit':'cc602e209e7deeb511ab2a1f3b2268d55206c43c'},
       'counts':{'epochs':len(rows),'source_event_rows':len(events),'source_thermal_component_per_epoch':17,'REI_HHe_F5_entries':965,'REI_HHe_J5x5_entries':4825,'common_bath_J5x21_entries':20265,'new_IVP':0},
       'input_ranges':{'z':[float(z.min()),float(z.max())],'T_K':[float(T.min()),float(T.max())],
        'nHref_over_nb':[float(min(r['nHref_over_nb'] for r in rows)),float(max(r['nHref_over_nb'] for r in rows))]},
       'max_rust_thermal_energy_identity_abs_erg_cm3_s':float(max_energy_res),
       'max_BASS_photo_event_reconstruction_abs_baryon_s':float(max_photo_res),
       'max_REI_Rust_source_translated_F_vs_PR276_residual_per_baryon_s':float(max_legacy_F),
       'max_REI_Rust_source_translated_J_vs_PR276_residual_s':float(max_legacy_J),
       'max_K_trace_proxy_abs_s':float(max(abs(r['K_trace_proxy_s']+3*r['H_s']) for r in rows)),
       'integrated_frozen_source_exposures':isrc,
       'maxima':{k:{'abs':float(max(abs(r[k]) for r in rows)),'at_z':float(max(rows,key=lambda r:abs(r[k]))['z'])} for k in [
         'REI_HHe_Tdot_point_K_s','REI_HHe_Tdot_thermal_K_s','REI_HHe_cmb_exchange_erg_per_Href_s',
         'REI_HHe_photo_input_erg_per_Href_s','REI_HHe_primary_heat_erg_per_Href_s','REI_BASS_ionization_threshold_source_defect_erg_per_Href_s']},
       'physical_limits':{'full_REI17':'UNBOUND','same_IC_7_vs_193':'NOT_ESTABLISHED','source_thermal':'POINT_RHS_ONLY',
           'K_owner':'UNBOUND_BASS_AXISYM_PROXY_ONLY','secondary_deposition':'NOT_ASSIGNED',
           'true_coupled_background':'NOT_SOLVED','CMB_tau':'NOT_COMPUTED',
           'no_double_count':'REPLACEMENT_PORT_ONLY'},
       'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0,
              'new_auxiliary':'1/1_SOURCE_QUALIFIED_IGM_THERMAL_PORT','F4':'PARTIAL','L4_ready':False,'production':'HOLD'}}
    return rows,events,dict(F5=np.asarray(F_local),J5=np.asarray(J_local),J5x21_common=np.asarray(J_full_bath),x=x,z=z),rr

def write():
    rows,events,matrices,results=calculate()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for name,seq in [('HHE_IGM_THERMAL_193.csv',rows),('HHE_IGM_EVENTS_579.csv',events)]:
        with (out/name).open('w',newline='',encoding='utf8') as fp:
            w=csv.DictWriter(fp,fieldnames=list(seq[0]));w.writeheader();w.writerows(seq)
    np.savez_compressed(out/'REI_HHE_FJ_193.npz',**matrices)
    (out/'RESULT.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(results,indent=2))
if __name__=='__main__':write()
