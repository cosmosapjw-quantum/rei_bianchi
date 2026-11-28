"""Measured 4He coherent-pi0 source to prompt 2gamma kinematic transfer.

Everything is conditional on exact EXFOR source identity. A photoabsorbed gamma
can regenerate two photons; alpha survives in this coherent channel.  Final
nonthermal particle cascade and cosmological injection are NOT computed.
"""
from __future__ import annotations
import csv, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'he_dd_exfor_measured_20261031'/'data'/'EXFOR_CATALOG_2270.csv'
PARENT_SRC=ROOT/'he_dd_exfor_measured_20261031'/'src'
if not SRC.is_file() or not PARENT_SRC.is_dir():
    raise RuntimeError('Source-owned exact PR134 repository tree required')
sys.path.insert(0,str(PARENT_SRC))
from physics_from_exfor import state, rates, C_CM_S

# All mass parameters are rest energies in MeV, i.e. mass*c**2.
M_ALPHA=3727.3794118  # MeV, 2022 CODATA alpha-nucleus m*c^2 (source-qualified rounded)
M_PI0=134.9768       # MeV, PDG 2025 pi0 m*c^2
B_2G=0.98823         # pi0 -> 2 gamma branching fraction (PDG 2025)
B_2G_SIGMA=0.00034  # absolute 1-sigma
TAU_PI0=8.43e-17    # s, PDG 2025
M_P=938.27208816
M_N=939.56542052
M_D=1875.61294257
Q_NPD=26.0711       # MeV, Cyburt 2003 alpha photo-split threshold
CUT=150.            # MeV; cutoff of inherited BASS_HE PR133 gamma-only model


def source_rows(subentry:str):
    out=[]
    with SRC.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            if r['subentry']!=subentry:continue
            keys=r['fields_ordered'].split('|')
            vals=r['values_ordered'].split('|')
            units=r['units_ordered'].split('|')
            if len(keys)!=len(vals) or len(keys)!=len(units):raise ValueError('column-length mismatch')
            if len(set(keys))!=len(keys):raise ValueError('duplicate EXFOR column '+subentry)
            rec={k:float(v) for k,v in zip(keys,vals)}
            out.append({'subentry':subentry,'row_index':int(r['row_index']),'reaction':r['reaction'],
                        'source_ref':r['source_ref'],'fields':r['fields_ordered'],'units':r['units_ordered'],
                        **rec})
    if not out:raise ValueError('missing source subentry '+subentry)
    return out


def interpolated_absorption(E:float):
    """Interpolated 1997 inclusive absorption, never an exactly measured point unless grid matches."""
    raw=source_rows('M0520002')
    x=np.array([r['EN'] for r in raw]);j=np.searchsorted(x,E,side='right')-1
    if not (x[0]<=E<=x[-1]):raise ValueError('outside EXFOR absorption range')
    j=max(0,min(j,len(x)-2));lo,hi=raw[j:j+2]
    w=(E-lo['EN'])/(hi['EN']-lo['EN'])
    val=(1-w)*lo['DATA']+w*hi['DATA']
    stat=math.hypot((1-w)*lo['ERR-S'],w*hi['ERR-S'])
    sys=(1-w)*lo['ERR-SYS']+w*hi['ERR-SYS'] # source systematic common-mode assumed fully correlated
    return dict(E_MeV=E,low_MeV=lo['EN'],high_MeV=hi['EN'],measured_E=(w==0 or w==1),
                sigma_micro_b=val,stat_micro_b=stat,sys_micro_b=sys)


def pion_cm(E):
    """Two-body gamma+alpha(rest)->alpha+pi0; all energies in MeV."""
    threshold=M_PI0 + M_PI0**2/(2*M_ALPHA)
    if E<threshold:raise ValueError('coherent pi0 production below exact nuclear recoil threshold')
    sqrt_s=math.sqrt(M_ALPHA*M_ALPHA+2*M_ALPHA*E)
    epi_star=(sqrt_s*sqrt_s+M_PI0*M_PI0-M_ALPHA*M_ALPHA)/(2*sqrt_s)
    p_star=math.sqrt(max(0.,epi_star*epi_star-M_PI0*M_PI0))
    beta=E/(M_ALPHA+E)
    gamma=(M_ALPHA+E)/sqrt_s
    return dict(threshold_MeV=threshold,pi_cm_energy_MeV=epi_star,
                pi_cm_p_c_MeV=p_star,beta_cm=beta,gamma_cm=gamma)


def pion_lab(E,mu):
    if not -1-1e-12<=mu<=1+1e-12:raise ValueError('invalid cos(theta_cm)')
    cm=pion_cm(E)
    e=cm['gamma_cm']*(cm['pi_cm_energy_MeV']+cm['beta_cm']*cm['pi_cm_p_c_MeV']*mu)
    p=math.sqrt(max(0,e*e-M_PI0*M_PI0))
    t_recoil=E-e
    if t_recoil<-1e-8:raise ArithmeticError('negative nuclear recoil energy')
    return dict(E_pi_MeV=e,p_pi_c_MeV=p,recoil_alpha_K_MeV=t_recoil,
                E_gamma_min_MeV=(e-p)/2,E_gamma_max_MeV=(e+p)/2)


def daughter_above(E,mu,cut=CUT):
    """Isotropic spin-0 pi0->2gamma in pi0 rest frame; conditional on 2gamma decay.
    Returns expected count and energy above cut per pion of the specified direction.
    """
    v=pion_lab(E,mu); lo=v['E_gamma_min_MeV'];hi=v['E_gamma_max_MeV']
    if hi<=cut:return dict(P_daughter_above=0.,count_above_per_pi0=0.,
                          E_above_per_pi0_MeV=0.,E_below_per_pi0_MeV=B_2G*v['E_pi_MeV'],**v)
    if lo>=cut:frac=1.;e_above=B_2G*v['E_pi_MeV']
    else:
        frac=(hi-cut)/(hi-lo)
        e_above=B_2G*(hi*hi-cut*cut)/(hi-lo)
    frac=max(0,min(1,frac));count=2*B_2G*frac
    return dict(P_daughter_above=frac,count_above_per_pi0=count,
                E_above_per_pi0_MeV=e_above,
                E_below_per_pi0_MeV=B_2G*v['E_pi_MeV']-e_above,**v)


def selected_angular_rows(index):
    ids=('M0752002','M0752003','M0752004','M0752005')
    d=source_rows(ids[index]);assert len(d)>=24
    out=[]
    for r in d:
        out.append(dict(subentry=r['subentry'],angle_cm_deg=r['ANG-CM'],
                        sigma_micro_b_per_sr=r['DATA-CM'],stat_micro_b_per_sr=r['ERR-S'],
                        sys_percent=r['ERR-SYS'],E_min_MeV=r['EN-MIN'],E_max_MeV=r['EN-MAX'],
                        row_index=r['row_index'],origin='EXFOR_Rambo1999_angle_binned_not_pointwise_excitation'))
    return out


def angular_support_moment(E,index):
    """Observed 7..~147deg angular SUPPORT ONLY. Angular tails unmeasured."""
    a=selected_angular_rows(index)
    angle=np.array([r['angle_cm_deg'] for r in a]);sigma=np.array([r['sigma_micro_b_per_sr'] for r in a]);
    mu=np.cos(np.deg2rad(angle));order=np.argsort(mu)
    mu=mu[order];sigma=sigma[order]
    # Integrate 2pi dmu times sampled cross section; no angular tail extrapolation.
    area=float(2*math.pi*np.trapezoid(sigma,mu))
    weighted=lambda key:float(2*math.pi*np.trapezoid(sigma*np.array([daughter_above(E,float(x))[key] for x in mu]),mu)/area)
    return dict(E_MeV=E,subentry=a[0]['subentry'],angular_E_min_MeV=a[0]['E_min_MeV'],
                angular_E_max_MeV=a[0]['E_max_MeV'],theta_min_deg=float(min(angle)),theta_max_deg=float(max(angle)),
                sigma_partial_micro_b=area,mu_daughter_above_count_support_only=weighted('count_above_per_pi0'),
                mu_daughter_above_energy_support_MeV=weighted('E_above_per_pi0_MeV'),
                mu_pion_energy_support_MeV=weighted('E_pi_MeV'),
                angular_tails_unmeasured=True,absolute_shape_normalization_not_force_matched=True)


def pion_source_kinematics():
    main=[r for r in source_rows('M0752019') if r['EN']<250]
    out=[];ang=[];comp=[]
    for j,r in enumerate(main):
        E=r['EN'];a=angular_support_moment(E,j);vmin=daughter_above(E,-1.);vmax=daughter_above(E,1.)
        a.update(sigma_pi0_measured_micro_b=r['DATA'],stat_sigma_pi0_micro_b=r['ERR-S'],
                 source_pi0_7percent_correlated_sys_micro_b=.07*r['DATA'],
                 partial_vs_total_ratio=a['sigma_partial_micro_b']/r['DATA'],
                 angular_vs_total_difference_micro_b=a['sigma_partial_micro_b']-r['DATA'],
                 angular_measured_support_integral_may_exceed_total_within_source_uncertainty=True)
        ang.append(a)
        absr=interpolated_absorption(E);frac=r['DATA']/absr['sigma_micro_b']
        stat=frac*math.hypot(r['ERR-S']/r['DATA'],absr['stat_micro_b']/absr['sigma_micro_b'])
        sys=frac*math.hypot(.07,absr['sys_micro_b']/absr['sigma_micro_b'])
        comp.append(dict(E_MeV=E,EXFOR_pi='M0752019',EXFOR_abs='M0520002',
                         sigma_pi_micro_b=r['DATA'],pi_stat_micro_b=r['ERR-S'],pi_sys_micro_b=.07*r['DATA'],
                         sigma_inclusive_interpolated_micro_b=absr['sigma_micro_b'],
                         inclusive_stat_micro_b=absr['stat_micro_b'],inclusive_sys_micro_b=absr['sys_micro_b'],
                         inclusive_low_MeV=absr['low_MeV'],inclusive_high_MeV=absr['high_MeV'],
                         exclusive_pi0_over_inclusive=frac,frac_stat_indep_sources_assumption=stat,
                         frac_sys_indep_experiments_assumption=sys,
                         inclusive_absorption_contains_pi0_ASSUMPTION_REQUIRES_DETECTOR_CHECK=True,
                         is_interpolated_absorption=not absr['measured_E']))
        out.append(dict(E_MeV=E,theta_cm_min=-1,theta_cm_max=1,
                        E_pi_lab_min_MeV=vmin['E_pi_MeV'],E_pi_lab_max_MeV=vmax['E_pi_MeV'],
                        alpha_recoil_K_min_MeV=vmax['recoil_alpha_K_MeV'],alpha_recoil_K_max_MeV=vmin['recoil_alpha_K_MeV'],
                        one_daughter_energy_min_MeV=min(vmin['E_gamma_min_MeV'],vmax['E_gamma_min_MeV']),
                        one_daughter_energy_max_MeV=max(vmin['E_gamma_max_MeV'],vmax['E_gamma_max_MeV']),
                        daughters_gt150_count_lower=min(vmin['count_above_per_pi0'],vmax['count_above_per_pi0']),
                        daughters_gt150_count_upper=max(vmin['count_above_per_pi0'],vmax['count_above_per_pi0']),
                        E_gamma_above150_lower_MeV=min(vmin['E_above_per_pi0_MeV'],vmax['E_above_per_pi0_MeV']),
                        E_gamma_above150_upper_MeV=max(vmin['E_above_per_pi0_MeV'],vmax['E_above_per_pi0_MeV']),
                        full_angular_kinematic_bound=True,no_pion_angular_model=True,
                        branch_2gamma=B_2G,branch_2gamma_sigma=B_2G_SIGMA))
    return out,ang,comp


def prompt_first_hits(source,angular,comparison,zs=(1e4,1e5,1e6)):
    out=[]
    for p,a,s in zip(source,angular,comparison):
        E=p['E_MeV'];inc=s['sigma_inclusive_interpolated_micro_b'];spi=s['sigma_pi_micro_b']
        for z in zs:
            h=state(float(z));N=h['n_alpha_cm3']*C_CM_S*1e-30
            # All nuclear photoabsorption is replaced by one source-owned inclusive sink.
            # It includes pi0 as a SUBchannel, not added twice.
            r=rates(float(E),float(z),'rice')
            gamma_em=sum(r[k] for k in ('bw','bh','kn'))
            gamma_abs=N*inc;tot=gamma_em+gamma_abs
            Ppi=N*spi/tot
            if Ppi<0 or Ppi>1:raise ArithmeticError('unphysical first-hit branch')
            lower=Ppi*p['daughters_gt150_count_lower'];upper=Ppi*p['daughters_gt150_count_upper'];val=Ppi*a['mu_daughter_above_count_support_only']
            if not lower-1e-14<=val<=upper+1e-14:raise ArithmeticError('angular estimate beyond kinematic bound')
            out.append(dict(E_MeV=E,z=float(z),source_pi0='M0752019',source_abs='M0520002',
                  Gamma_pi0_per_s=N*spi,Gamma_abs_allalpha_per_s=gamma_abs,
                  Gamma_em_per_s=gamma_em,Gamma_total_per_s=tot,
                  H_s_inv=h['H_s_inv'],P_first_pi0=Ppi,
                  alpha_retained_on_pi0_event=True,
                  N_high_photons_per_injected_gamma_lower=lower,
                  N_high_photons_per_injected_gamma_upper=upper,
                  N_high_photons_per_injected_gamma_angular_support_proxy=val,
                  photon_cut_MeV=CUT,photoabsorbed_gamma_reinjected=True,
                  no_photon_below150_followup=True,no_positron_inverse_compton=True,
                  H_times_tau_pi0=h['H_s_inv']*TAU_PI0,
                  inclusive_contains_coherent_pi0_assumed_not_independently_proved=True))
    return out


def four_nucleon_source():
    return [dict(E_MeV=r['EN'],energy_res_MeV=20.,sigma_2p2n_micro_b=r['DATA'],
                 stat_micro_b=r['ERR-S'],EXFOR='M0384002',
                 alpha_destroyed=True,deuteron_direct_birth_count=0,
                 exact_monochromatic_sigma=False) for r in source_rows('M0384002')]


def jensen_fastd_table():
    """JETP1958 p604 TableII: experimental *mean |p|*, NOT measured <kinetic energy>."""
    rows=[('25.9-75',25.9,75,123,118,124),('75-170',75,170,214,259,190)]
    def kinetic(p,mc2):return math.hypot(mc2,p)-mc2
    out=[]
    for label,lo,hi,pp,pn,pd in rows:
        kp=kinetic(pp,M_P);kn=kinetic(pn,M_N);kd=kinetic(pd,M_D)
        e_lower=Q_NPD+kp+kn+kd
        if e_lower>=hi:raise ArithmeticError('Jensen lower bound exceeds reported photon source support')
        out.append(dict(JETP='GorbunovSpiridonov1958_page604_TableII',E_gamma_bin_label_MeV=label,
             E_gamma_low_MeV=lo,E_gamma_high_MeV=hi,
             mean_p_proton_MeV_over_c=pp,mean_p_neutron_MeV_over_c=pn,
             mean_p_deuteron_MeV_over_c=pd,
             Jensen_lower_mean_Kp_MeV=kp,Jensen_lower_mean_Kn_MeV=kn,
             Jensen_lower_mean_Kd_MeV=kd,
             Jensen_lower_mean_total_K_MeV=kp+kn+kd,
             inferred_lower_mean_E_gamma_MeV=e_lower,
             upper_mean_E_gamma_MeV=hi,
             mean_K_not_equal_K_of_mean_p=True,
             pbar_detector_selected_sample=True,source_uncertainty_unreported=True,
             cannot_use_as_220MeV_dd_kinematics=True))
    return out

def angular_support_daughter_spectrum(E,index,bin_width_MeV=5.):
    """Source-angular-support-conditioned two-gamma lab spectrum, not full-sky.

    Normalizes the experimentally sampled angular SHAPE on the covered angular range,
    uses exact flat decay-photon distribution in lab at each pion angle, and integrates
    daughter counts and photon energies exactly in the binned photon energy dimension.
    All outputs are per produced pi0; 1-B_2G Dalitz/other decays NOT accounted as 2gamma.
    """
    rows=selected_angular_rows(index)
    mu=np.cos(np.deg2rad([r['angle_cm_deg'] for r in rows]));sig=np.array([r['sigma_micro_b_per_sr'] for r in rows]);
    order=np.argsort(mu);mu=mu[order];sig=sig[order];n=len(mu)
    # Endpoint trapezoid weights for integral dmu sigma(mu); 2pi cancels on normalization.
    q=np.zeros(n)
    q[0]=sig[0]*(mu[1]-mu[0])/2
    q[-1]=sig[-1]*(mu[-1]-mu[-2])/2
    q[1:-1]=sig[1:-1]*(mu[2:]-mu[:-2])/2
    q=q/q.sum()
    if np.min(q)<0 or abs(q.sum()-1)>1e-12:raise ArithmeticError('invalid experimental angular support')
    bin_edges=np.arange(0,250+bin_width_MeV,bin_width_MeV)
    if not np.isclose(bin_edges[-1],250.):raise ValueError('bin grid must end at 250')
    pion=[pion_lab(E,float(x)) for x in mu]
    result=[]
    for lo,hi in zip(bin_edges[:-1],bin_edges[1:]):
        count=energy=0.
        for wi,v in zip(q,pion):
            emin=v['E_gamma_min_MeV'];emax=v['E_gamma_max_MeV']
            left=max(lo,emin);right=min(hi,emax)
            if right<=left:continue
            delta=emax-emin
            count+=float(wi)*2*B_2G*(right-left)/delta
            energy+=float(wi)*B_2G*(right*right-left*left)/delta
        result.append({'incident_E_MeV':E,'daughter_bin_low_MeV':float(lo),
                       'daughter_bin_high_MeV':float(hi),
                       'mean_daughter_number_per_pi0':count,
                       'gamma_energy_MeV_per_pi0':energy,
                       'angular_source_subentry':rows[0]['subentry'],
                       'pion_angular_support_deg':f'{rows[0]["angle_cm_deg"]}-{rows[-1]["angle_cm_deg"]}',
                       'source_shape_norm_conditional_on_support':True,
                       'fraction_not_pion_2gamma_untracked':1.-B_2G,
                       'exact_decay_two_body_energy_bins':True,
                       'not_full_cascade':True})
    if abs(sum(x['mean_daughter_number_per_pi0'] for x in result)-2*B_2G)>1e-12:raise ArithmeticError('daughter number violation')
    expected_E=B_2G*sum(wi*v['E_pi_MeV'] for wi,v in zip(q,pion))
    if abs(sum(x['gamma_energy_MeV_per_pi0'] for x in result)-expected_E)>1e-10:raise ArithmeticError('pion gamma energy violation')
    return result


def first_hit_daughter_spectra(spectra,hit):
    lookup={(r['E_MeV'],r['z']):r for r in hit};res=[]
    for r in spectra:
        E=r['incident_E_MeV']
        for z in (1e4,1e5,1e6):
            parent=lookup[(E,z)];prob=parent['P_first_pi0']
            res.append({'incident_E_MeV':E,'z':z,
                 'daughter_bin_low_MeV':r['daughter_bin_low_MeV'],
                 'daughter_bin_high_MeV':r['daughter_bin_high_MeV'],
                 'expected_daughter_number_per_injected_gamma':prob*r['mean_daughter_number_per_pi0'],
                 'expected_daughter_energy_MeV_per_injected_gamma':prob*r['gamma_energy_MeV_per_pi0'],
                 'P_local_first_pi0':prob,'angular_support_only':True,
                 'other_EM_and_nuclear_final_states_untracked':True})
    return res
