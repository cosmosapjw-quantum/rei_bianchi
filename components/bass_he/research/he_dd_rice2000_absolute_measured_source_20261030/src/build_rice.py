#!/usr/bin/env python3
"""Reproduce SOURCE-OWNED Rice (2000) absolute He4(gamma,dd) observations.

No 1998/2000 conflict is hidden. No event rate or inferred detector covariance.
Data are experimentally reported photon-ENERGY-BIN cross sections; conditional
phase-space envelope is ONLY for a matched positive, otherwise unknown,
source-energy weighting of an inverse capture observable.

Units: energy MeV (including rest energy mc**2), sigma nb/sr, signature -+++.
Source PDFs: user-owned originals, identities pinned in USER_FILE_IDENTITY.json.
"""
import argparse
import csv
import hashlib
import io
import json
from decimal import Decimal, localcontext
from pathlib import Path

MA = Decimal('3727.3794118')  # original frozen PR104 alpha rest energy MeV
MD = Decimal('1875.61294500')  # original frozen PR104 deuteron rest energy MeV
Q = 2*MD-MA
D = lambda x: Decimal(str(x))
SOURCE_HASHES = {
    'RICE2000_TABLE_I_AUTHORITATIVE.json': 'dd29c7b492162b257b6b9674792c2db5cf65c98921cbea088a9283ea641bc03a',
    'RICE2000_TABLE_II_LEGENDRE_FITS.json': 'af473f049c502f3a54a34d99d9d923c98e82db4c8ac1ac71fd18867e887ac40a',
    'RICE1998_TABLE_5_1_PRELIMINARY.json': 'd188ac15bc6c329f8045f8bd1fbe2ec5a6fc4fc3fb922576f3259bcf41c7a67c',
    'X4R8587_x4.txt':'3cab0027cde915e3d98aaecfa8dfd712e095d10946b5d55462408d18bcca07a7'
}

def load_sources(root):
    p = Path(root) / 'sources'
    for name,sha in SOURCE_HASHES.items():
        actual = hashlib.sha256((p / name).read_bytes()).hexdigest()
        if actual != sha:
            raise ValueError(f'Immutable source changed: {name} expected {sha} got {actual}')
    tables = [json.loads((p/name).read_text()) for name in list(SOURCE_HASHES)[:3]]
    if 'M0826002' not in (p/'X4R8587_x4.txt').read_text() or 'RICE' in (p/'X4R8587_x4.txt').read_text().upper():
        raise ValueError('EXFOR request is not the intended M0826 source')
    return tables

def s_gamma(e):
    e=D(e)
    if e<0: raise ValueError('negative photon energy')
    return MA*MA+2*MA*e

def threshold(): return (4*MD*MD-MA*MA)/(2*MA)

def k2(e):
    ss=s_gamma(e)
    return (ss-MA*MA)**2/(4*ss)

def q2(e):
    ss=s_gamma(e)
    return (ss-4*MD*MD)/4

def cap_to_photo_ordered(e):
    if D(e)<=threshold() or q2(e)<=0: raise ValueError('pair threshold')
    return D(2)/D(9)*k2(e)/q2(e)

def cap_to_photo_event_full_sphere(e):
    # Rice's tabulated per-daughter/ordered angular density integrates to sigma_event=2*pi*A0
    # If event differential density is defined on the full sphere, divide Rice density by 2;
    # hence ratio cap / photo_event is twice the ordered one.
    return 2*cap_to_photo_ordered(e)

def matching_Td(e):return (s_gamma(e)-4*MD*MD)/(2*MD)

def q2_over_k2(e):return q2(e)/k2(e)

def ratio_minimum_e():
    # derivative zero of (s - M^2)^2/[s(s-4 m^2)] where s=MA^2+2 MA E.
    A=MA*MA; B=4*MD*MD
    s0=A*B/(2*A-B)
    return (s0-A)/(2*MA)

def norm_decimal(v, digits=15):
    return str(v.quantize(Decimal(1).scaleb(-digits)))

def science(root):
    measured, fits, thesis=load_sources(root)
    if len(measured['observations'])!=12 or len(fits['records'])!=8 or len(thesis['entries'])!=6:
        raise ValueError('Source cardinalities changed')
    keys=[(x['bin'],x['theta_lab']) for x in measured['observations']]
    if len(set(keys))!=12: raise ValueError('duplicates/reflected pseudoreplication')
    if set(x['bin'] for x in measured['observations'])!={'150-190','190-250'}:
        raise ValueError('energy bin cardinality')
    for x in measured['observations']:
        if (x['Emin'],x['Emax']) not in [(150,190),(190,250)]: raise ValueError('energy-bin mismatch')
        if x['sigma'] < 0 or x['stat_sd'] < 0: raise ValueError('negative measurement')
    with localcontext() as c:
        c.prec=65
        e_star=ratio_minimum_e()
        if not 0 < e_star < 150: raise ValueError('phase-space monotonicity not shown')
        obs=[]; bin_props={}; anomalies=[]; fitdata=[]
        for b in ['150-190','190-250']:
            a,z=map(int,b.split('-'))
            vals=[x for x in measured['observations'] if x['bin']==b]
            if len(vals)!=6: raise ValueError('expected six measured telescope angles')
            conv_low,conv_hi=cap_to_photo_ordered(a),cap_to_photo_ordered(z)
            if not conv_low < conv_hi: raise ValueError('positive envelope order')
            f=[x for x in fits['records'] if x['bin']==b]
            totals=[D(x['sigma_tot']) for x in f]
            bin_props[b]={
                'photon_energy_support_MeV':[a,z],
                'same_s_deuteron_lab_Td_support_MeV':[norm_decimal(matching_Td(a),12),norm_decimal(matching_Td(z),12)],
                'photo_to_capture_ordered_factor_support':[norm_decimal(conv_low,18),norm_decimal(conv_hi,18)],
                'photo_to_capture_full_sphere_event_density_factor_support':[norm_decimal(2*conv_low,18),norm_decimal(2*conv_hi,18)],
                'pair_birth_kinetic_support_MeV':[norm_decimal(D(a)-Q,8),norm_decimal(D(z)-Q,8)],
                'reported_sys_total_fraction':measured['systematics'][b]['fraction'],
                'source_fit_totals_model_selection_central_range_nb':[str(min(totals)),str(max(totals))],
                'total_rate':None,'photon_spectrum':None,'actual_covariance_matrix':None,
                'interpretation':'source-published finite photon bin; conversion factor is pointwise exact but bounds on a bin-averaged capture observable require SAME nonnegative E-weighting, angular matching and detector acceptance as source, none established'
            }
            for x in vals:
                sf=D(x['sigma']);sd=D(x['stat_sd']);sys=D(measured['systematics'][b]['fraction'])
                obs.append({**x,
                    'source_status':'MEASURED_ABSOLUTE_BINNED_DA',
                    'author_stat_error_nb_sr':str(sd),
                    'author_systematic_scale_nb_sr':norm_decimal(sf*sys,8),
                    'common_covariance_known':False,
                    'conditional_inverse_capture_DA_if_same_positive_source_weight_nb_sr':[norm_decimal(sf*conv_low,14),norm_decimal(sf*conv_hi,14)],
                    'conditional_inverse_if_photodisintegration_event_full_sphere_convention_nb_sr':[norm_decimal(sf*conv_low*2,14),norm_decimal(sf*conv_hi*2,14)],
                    'at_exact_measured_E':False,
                    'R_event':None,'heat_rate':None})
        for i,f in enumerate(fits['records']):
            a0=D(f['A0']); reported=D(f['sigma_tot']); one_sigma_sys=D(f['sigma_tot_sys']); ftype=f['constraint']+('_P4' if f['P4'] else '_P2')
            # Analytic identity is exact, but A0 and sigma_tot published at two decimals; conservative 0.04 nb tolerance.
            import math
            prediction=a0*D(str(math.tau))
            residual=reported-prediction
            expected_sys=reported*D(measured['systematics'][f['bin']]['fraction'])
            ident_ok=abs(residual) <= D('0.04')
            sys_ok=abs(one_sigma_sys-expected_sys) <= D('0.015')
            if not ident_ok or not sys_ok:
                anomalies.append({'bin':f['bin'],'type':ftype,'author_A0':str(a0),'author_total':str(reported),
                                  'sigma_tot_minus_2piA0_nb':norm_decimal(residual,9),
                                  'source_systematic_nb':str(one_sigma_sys),'r_times_total_expected_nb':norm_decimal(expected_sys,9),
                                  'violates_rounded_identity':not ident_ok,'disagrees_with_uniform_r':not sys_ok,
                                  'status':'SOURCE_TABLE_DISCREPANCY_UNRESOLVED_NO_SILENT_REPAIR'})
            fitdata.append({**f,'source_is_alternative_fit_not_independent_measurement':True,
                'expected_2pi_A0_nb':norm_decimal(prediction,9),'identity_residual_nb':norm_decimal(residual,9),
                'rounding_identity_compatible':ident_ok,'uniform_systematic_fraction_compatible':sys_ok})
        prior=[]
        for t in thesis['entries']:
            a=next(x for x in measured['observations'] if x['bin']=='150-190' and x['theta_lab']==t['lab_angle'])
            prior.append({'angle_lab':t['lab_angle'],'thesis1998_preliminary_sigma_nb_sr':t['sigma'],
                'journal2000_published_sigma_nb_sr':a['sigma'],
                'published_over_thesis_ratio':norm_decimal(D(a['sigma'])/D(t['sigma']),10),
                'same_measurement_campaign':True,'revision_cause':'UNRESOLVED'})
        comp={
          'source':{'pdf_sha256':measured['pdf_sha256'],'doi':measured['doi'],'table':'Rice et al 2000 Table I'},
          'units':{'differential_cross_section':'nb/sr','total_cross_section':'nb','energy':'MeV'},
          'masses_parent_PR104':{'MA_rest_MeV':str(MA),'MD_rest_MeV':str(MD),'Q_MeV':str(Q)},
          'threshold_gamma_lab_MeV':norm_decimal(threshold(),14),
          'ratio_cap_to_photo_ordered_turning_point_MeV':norm_decimal(e_star,14),
          'observed_absolute_differential_rows':len(obs),
          'independent_original_campaigns':1,
          'observations':obs,
          'energy_bins':bin_props,
          'alternative_author_fit_rows':fitdata,
          'model_total_fit_count':len(fitdata),
          'fit_author_identity_discrepancies':anomalies,
          'preliminary_1998_vs_2000':prior,
          'raw_pdf_1998_complete':False,
          'sys_decomposition_from_thesis':{
              'shared_component_percent':{'photon_energy_cut':3.3,'target_length':2.0,'target_density':2.5,'tagging_efficiency':2.8},
              'PID_cut_percent':{'150-190':4.6,'190-250':11.7},
              'quadrature_percent':{'150-190':norm_decimal((D(3.3)**2+D(2)**2+D(2.5)**2+D(2.8)**2+D(4.6)**2).sqrt(),9),
                   '190-250':norm_decimal((D(3.3)**2+D(2)**2+D(2.5)**2+D(2.8)**2+D(11.7)**2).sqrt(),9)},
              'report_author_systematic_percent':{'150-190':7.1,'190-250':13.0},
              'source_covariance_matrix':None,
              'note':'Quadrature mimics 1998 author method. Per-angle/bin correlated covariance NOT provided.'},
          'X4R8587_role':'historical Arkatov EXFOR M0826 ONLY, zero Rice measurement rows',
          'DAG':{'central':'28/88','HE_physical':'14/18','new_Rice_source_scoped':'3/3','canonical_physical_delta':0},
          'gates':{'kappa':None,'R_event':None,'heat_rate':None,'L4':False,'production':'HOLD','Rice_absolute_input':'SOURCE_QUALIFIED_RICE_2000_TABLE_I_12'}
        }
        return comp

def dump(root):
    root=Path(root)
    data=science(root)
    results=root/'results';results.mkdir(exist_ok=True,parents=True)
    (results/'RICE_2000_ABSOLUTE_ATLAS.json').write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    with open(results/'RICE_2000_MEASURED_12.csv','w',newline='') as fh:
        cols=['bin','Emin','Emax','theta_lab','theta_cm','sigma','stat_sd']
        wr=csv.DictWriter(fh,fieldnames=cols,lineterminator='\n');wr.writeheader()
        for row in data['observations']:wr.writerow({k:row[k] for k in cols})
    (results/'RICE_2000_BLIND_REFEREE_FLAGS.json').write_text(json.dumps({
        'kind':'ADVERSARIAL_SOURCE_CHECK_SAME_AUTHOR_NOT_INDEPENDENT',
        'fit_source_table_anomalies':data['fit_author_identity_discrepancies'],
        'preliminary_difference_is_source_revision_not_independent_observation':True,
        'Rice1998_attachment_incomplete_139pages':True,
        'source_systematic_covariance_unavailable':True,
        'false_absorbed_source_X4R8587':False,
        'stop':'Never silently fix the author table, invent common covariance, multiply 12 measurements as 24 reflected measurements or promote to rate.'
    },indent=2,sort_keys=True)+'\n')
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default=str(Path(__file__).resolve().parent.parent));args=parser.parse_args()
    x=dump(args.root)
    print(json.dumps({'observed_absolute_rows':x['observed_absolute_differential_rows'], 'fit_source_anomalies':x['fit_author_identity_discrepancies'], 'source_scoped_DAG':x['DAG']},indent=2))
