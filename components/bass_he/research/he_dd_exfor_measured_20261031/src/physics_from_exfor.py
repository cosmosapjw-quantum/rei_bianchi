"""Source-qualified physical calculations from EXFOR 10461 and JETP 1958 Table I.

Observed quantities are never presented as model predictions. Direct measured
sigma pT / DD anchors are inserted ONLY at their measured incident energies
into the inherited seven-channel LOCAL first-interaction hazard. Competing
channels remain source-extrapolated. No full cascade or absolute cosmic source.
"""
from __future__ import annotations
import sys,math,csv,statistics
from pathlib import Path
from scipy.integrate import quad
from scipy import constants as c
import numpy as np
ROOT=Path(__file__).resolve().parents[2] # research/
PARENT=ROOT/'he_dd_alpha_competition_20261031'/'src'
sys.path.insert(0,str(PARENT))
from alpha_competition import rates, sigma_cyburt_cm2, sigma_rice_dd_cm2, SOURCES
from physics_pr131 import state
C_CM_S=c.c*100

# 1958 6-page original PDF, scanned Table I p601, source-energy integrals.
# Statistical uncertainties only; energy windows overlap and are correlated.
JETP1958_TABLE_I=[
 ('npD','<75',7.2,.9),('npD','75-170',4.6,1.2),('npD','<170',11.8,1.5),
 ('pT_plus_nHe3','<75',71.6,2.2),('pT_plus_nHe3','75-170',10.0,1.9),('pT_plus_nHe3','<170',81.6,2.9),
]

def prior_sigma_nb(E,channel):
    if channel=='pT':return sigma_cyburt_cm2(E,'pT')/1e-33
    if channel=='dd':return sigma_rice_dd_cm2(E)/1e-33
    raise ValueError(channel)

def measured_model_comparison(obs):
    result=[]
    for r in obs:
        channel='pT' if r['subentry']=='M0484003' else 'dd'
        prior=prior_sigma_nb(r['E_MeV'],channel)
        err=r['stat_nb']
        result.append({'subentry':r['subentry'],'channel':channel,'E_MeV':r['E_MeV'],
            'observed_sigma_nb':r['sigma_nb'],'observed_stat_nb':err,
            'observed_sys_nb':r['sys_nb'],
            'observed_1sigma_stat_plus_reported_sys_nb':math.hypot(err,r['sys_nb']) if r['sys_nb'] is not None else None,
            'model_sigma_nb':prior,'model_kind':'cyburt2003_high_E_extrapolated' if channel=='pT' else 'Rice2000_bin_constant_not_energy_measured',
            'observed_over_model':r['sigma_nb']/prior,
            'delta_obs_minus_model_nb':r['sigma_nb']-prior,
            'model_uncertainty_included':False,'measured_point_used_for_kernel':True,
            'source_sys_unreported':r['sys_nb'] is None})
    return result

def anchored_local_physics(obs,zgrid=(1e4,1e5,1e6)):
    out=[]
    for r in obs:
        E=float(r['E_MeV']); ch='pT' if r['subentry']=='M0484003' else 'dd'
        for z in zgrid:
            base=rates(E,float(z),'rice')
            n_alpha=state(z)['n_alpha_cm3'];H=state(z)['H_s_inv']
            new_gamma=n_alpha*C_CM_S*r['sigma_nb']*1e-33
            gamma_other=sum(base.values())-base[ch]
            gamma_total=gamma_other+new_gamma
            P=new_gamma/gamma_total; prior=base[ch]/sum(base.values());
            # derivative of P wrt measured sigma, holding the other modeled rates fixed
            dp_dsig=P*(1-P)/r['sigma_nb']
            out.append({'EXFOR_subentry':r['subentry'],'reaction':ch,'E_MeV':E,'z':z,
             'measurement_sigma_nb':r['sigma_nb'],'measurement_stat_nb':r['stat_nb'],
             'measurement_sys_nb':r['sys_nb'],'Gamma_measured_channel_per_s':new_gamma,
             'Gamma_competing_model_per_s':gamma_other,'H_per_s':H,
             'Gamma_measured_over_H':new_gamma/H,'P_first_local_measured_channel':P,
             'P_first_local_source_extrap_baseline':prior,
             'P_first_relative_to_old':P/prior,'P_first_stat_sigma':dp_dsig*r['stat_nb'],
             'P_first_reported_sys_sigma':dp_dsig*r['sys_nb'] if r['sys_nb'] is not None else None,
             'N_D_first_local_per_gamma':2*P if ch=='dd' else None,
             'non_measured_competition_frozen':True,
             'BW_BH_KN_model_included':True,'not_cosmological_R_event':True,
             'model_kind':'source_anchored_one_channel_at_exact_measured_E_others_Cyburt_Rice_extrap'})
    return out

def obs_absorption_fraction(obs,absorb):
    """Finite-energy interpolation of measured inclusive denominator, not a measurement at interpolated E.
    stat errors treated independent across neighboring energies; systematic 100% correlated within 1997 source.
    Cross-experiment numerator/denominator errors assumed independent solely for illustrative partial error accounting.
    """
    arr=sorted(absorb,key=lambda x:x['E_MeV']);out=[]
    for r in obs:
        E=r['E_MeV'];lo,hi=None,None
        for a,b in zip(arr[:-1],arr[1:]):
            if a['E_MeV']<=E<=b['E_MeV']:lo,hi=a,b;break
        if lo is None:continue
        w=(E-lo['E_MeV'])/(hi['E_MeV']-lo['E_MeV']);
        s_abs=(1-w)*lo['sigma_nb']+w*hi['sigma_nb'];
        s_stat=math.hypot((1-w)*lo['stat_nb'],w*hi['stat_nb']);
        s_sys=(1-w)*lo['sys_nb']+w*hi['sys_nb']  # 100% correlated positivity
        frac=r['sigma_nb']/s_abs
        ferr_stat=frac*math.hypot(r['stat_nb']/r['sigma_nb'],s_stat/s_abs)
        ferr_sys=None if r['sys_nb'] is None else frac*math.hypot(r['sys_nb']/r['sigma_nb'],s_sys/s_abs)
        out.append({'exclusive_subentry':r['subentry'],'E_MeV':E,'exclusive_sigma_nb':r['sigma_nb'],
            'inclusive_source_subentry':'M0520002','interp_bracket_low_MeV':lo['E_MeV'],'interp_bracket_high_MeV':hi['E_MeV'],
            'inclusive_interp_nb':s_abs,'exclusive_to_inclusive_share':frac,
            'share_stat_error_independent_sources_assumption':ferr_stat,
            'share_reported_sys_error_independent_experiments':ferr_sys,
            'denominator_sys_treated_fully_correlated_within_1997':True,
            'numerator_sys_unreported':r['sys_nb'] is None,
            'interpolated_denominator_not_a_measured_point':True})
    return out

def model_1958_integrated():
    out=[]
    for channel,window,obs,stat in JETP1958_TABLE_I:
        low,high=(75.,170.) if window=='75-170' else (None,None)
        # 1958 <75 and <170 contain near-threshold physics and do not imply integration from E=0 of a valid model.
        keys=('npD',) if channel=='npD' else ('pT','nHe3')
        val=sum(quad(lambda E:sigma_cyburt_cm2(E,k)/1e-27,low,high,epsabs=1e-10,epsrel=1e-10)[0] for k in keys) if low is not None else None
        out.append({'jetp_page':'601_Table_I','channel':channel,'energy_interval_MeV':window,
             'observed_integrated_mb_MeV':obs,'observed_stat_mb_MeV':stat,
             'cyburt2003_integrated_mb_MeV':val,
             'model_to_obs_ratio':val/obs if val is not None else None,
             'difference_obs_minus_model_mb_MeV':obs-val if val is not None else None,
             'model_uncertainty_not_available':True,
             'source_only_statistical_uncertainty':True,
             'source_same_correlation_across_overlapping_intervals':True})
    return out

def polarization_energy_near_90(ds):
    arr=ds['G4081002']['rows'];entries=[]
    for E in (120.,150.,200.,250.):
        best=min((r for r in arr if r['EN']==E),key=lambda r:abs(r['ANG-CM']-90.))
        entries.append({'EXFOR_subentry':'G4081002','E_MeV':E,'theta_cm_deg':best['ANG-CM'],
          'A_compiler_signed':best['DATA'],'DATA_ERR_source_type_unspecified':best['DATA-ERR'],
          'A_author_signed_if_simple_negation':-best['DATA'],
          'compiler_sign_negative_of_author':True,'sample_from_digitized_1988_Fig1':True,
          'not_absolute_cross_section':True})
    a=entries[1];b=entries[3]
    delta=b['A_compiler_signed']-a['A_compiler_signed']
    # scale only if treated independent, covariance unknown.
    err=math.hypot(a['DATA_ERR_source_type_unspecified'],b['DATA_ERR_source_type_unspecified'])
    return entries,{'delta_A_250_minus_150_compiler_sign':delta,'quadrature_error_if_independent':err,
        'delta_over_quadrature_error_IF_independent':delta/err,
        'unknown_source_covariance':True,'theta_difference_deg':b['theta_cm_deg']-a['theta_cm_deg']}

def absorption_anchored_first_hit(exclusive, inclusive, zgrid=(1e4,1e5,1e6)):
    """EXFOR inclusive absorption used as ALL-alpha sink, no extrapolation outside measured bracket.

    Does not assume inclusive photoabsorption equals sum of the PR133 four alpha channels:
    pion production and other breakups are included in the measured total.
    """
    arr=sorted(inclusive,key=lambda r:r['E_MeV']); out=[]
    for r in exclusive:
        ch='pT' if r['subentry']=='M0484003' else 'dd'
        E=float(r['E_MeV']); bracket=None
        for lo,hi in zip(arr[:-1],arr[1:]):
            if lo['E_MeV']<=E<=hi['E_MeV']:
                bracket=(lo,hi);break
        if bracket is None:continue
        lo,hi=bracket;w=(E-lo['E_MeV'])/(hi['E_MeV']-lo['E_MeV']);
        source_abs_nb=(1-w)*lo['sigma_nb']+w*hi['sigma_nb'];
        source_abs_stat_nb=math.hypot((1-w)*lo['stat_nb'],w*hi['stat_nb']);
        source_abs_sys_nb=(1-w)*lo['sys_nb']+w*hi['sys_nb'];
        # source measured exclusive physical lower bound, photoabsorption is inclusive
        assert source_abs_nb>r['sigma_nb']
        for z in zgrid:
            h=state(z);na=h['n_alpha_cm3'];C=na*C_CM_S*1e-33
            old=rates(E,z,'rice');nonalpha=sum(old[k] for k in ('bw','bh','kn'))
            alpha_abs=C*source_abs_nb; excl=C*r['sigma_nb'];total=nonalpha+alpha_abs
            P=excl/total
            frac=excl/alpha_abs
            # derivatives from measured exclusive and inclusive values, treating
            # everything else (including the CMB and EM kernels) as fixed.
            dp_dexcl=P/r['sigma_nb']
            dp_dabs=-P*(C/total)
            stat=math.hypot(dp_dexcl*r['stat_nb'],dp_dabs*source_abs_stat_nb)
            syspt=dp_dexcl*r['sys_nb'] if r['sys_nb'] is not None else None
            sysabs=abs(dp_dabs)*source_abs_sys_nb
            out.append({'exclusive_EXFOR':r['subentry'],'inclusive_EXFOR':'M0520002',
                'reaction':ch,'E_MeV':E,'z':z,'source_inclusive_interp_nb':source_abs_nb,
                'inclusive_lower_MeV':lo['E_MeV'],'inclusive_upper_MeV':hi['E_MeV'],
                'source_exclusive_measured_nb':r['sigma_nb'],
                'alpha_absorption_over_H':alpha_abs/h['H_s_inv'],
                'alpha_absorption_fraction_exclusive':frac,
                'Gamma_total_EM_plus_all_alpha_per_s':total,
                'P_first_measured_exclusive_competing_all_alpha':P,
                'P_first_reported_stat_unc_independent_source_assumption':stat,
                'P_first_reported_exclusive_sys_unc':syspt,
                'P_first_reported_inclusive_sys_unc':sysabs,
                'P_first_source_only_7channel':excl/(nonalpha+sum(old[k] for k in ('pT','nHe3','npD','dd'))-old[ch]+excl),
                'nuclear_kinematics_and_secondaries_uncomputed':True,
                'incl_interpolated_not_measured_exact_E':True,
                'not_full_cosmic_R_event':True})
    return out

def model_photoabsorption_gap(exclusive,inclusive):
    """Descriptive comparison only: model 4 alpha exclusive channels NOT a complete set.
    At energies with measured total photoabsorption interpolation.
    Never promote this residual to measured individual missing-channel sigma.
    """
    arr=sorted(inclusive,key=lambda x:x['E_MeV']);result=[]
    for r in exclusive:
        E=r['E_MeV']; pair=None
        for lo,hi in zip(arr[:-1],arr[1:]):
            if lo['E_MeV']<=E<=hi['E_MeV']:pair=(lo,hi);break
        if pair is None:continue
        lo,hi=pair;w=(E-lo['E_MeV'])/(hi['E_MeV']-lo['E_MeV']);sabs=(1-w)*lo['sigma_nb']+w*hi['sigma_nb']
        sig={k:1e33*sigma_cyburt_cm2(E,k) for k in ('pT','nHe3','npD')};sig['dd']=prior_sigma_nb(E,'dd')
        ch='pT' if r['subentry']=='M0484003' else 'dd'
        sig[ch]=r['sigma_nb']
        subtotal=sum(sig.values());
        result.append({'E_MeV':E,'source_measured_exclusive_channel':ch,
            'nuclear_channels_completed_4':len(sig),
            'measured_inclusive_photoabs_interp_nb':sabs,
            'sum_one_measured_three_models_nb':subtotal,
            'measured_total_minus_incomplete_model_nb':sabs-subtotal,
            'missing_fraction_if_four_models_assumed':(sabs-subtotal)/sabs,
            'unknown_other_channels_cannot_be_positively_estimated_from_this_without_valid_models':True,
            'source_inclusive_interpolated':True})
    return result
