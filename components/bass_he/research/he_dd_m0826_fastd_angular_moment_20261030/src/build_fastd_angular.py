#!/usr/bin/env python3
"""Source-locked measured M0826 angular shape -> conditional D-fast pair moment atlas.

This is NOT a Rice data substitute, monoenergetic measurement, measured covariance,
absolute calibrated event rate, or kinetic-energy deposition in gas.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

SOURCE = {
 'M0826': {'sha256':'05ea65eaa1a7245f19fd47aa14e91bef3d706fe2a55c6d70a512808ee4e9284c', 'blob':'95010842754215e98eea8d99eff5f3de0799c666'},
 'M0011': {'sha256':'8d45af5ca4f0df3c000a5cf672cd84e2e8512b65b52b03a912c5080d2bf5d9b2', 'blob':'20804471fb7584e07ab979ecad6a3e96cba0c6a2'},
}
M_ALPHA_MEV = 3727.37941180  # M_alpha c^2; original PR104 mass convention
M_D_MEV = 1875.61294500     # m_d c^2
REFERENCE_E_MEV = (30.0,40.0,50.0) # bounds & diagnostic, not measured monoenergetic gamma points


def checked_source(root:Path, key:str)->bytes:
    data=(root/'sources'/f'{key}.x4').read_bytes()
    if hashlib.sha256(data).hexdigest()!=SOURCE[key]['sha256']:
        raise ValueError('EXFOR_SHA256_MISMATCH:'+key)
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=SOURCE[key]['blob']:
        raise ValueError('EXFOR_GIT_BLOB_MISMATCH:'+key)
    return data


def source_rows(raw:bytes, subentry:str, header:str, unit:str, n:int, reaction:str)->list[list[float]]:
    txt=raw.decode('ascii')
    start=txt.index('SUBENT        '+subentry)
    end=txt.index('ENDSUBENT',start)
    sub=txt[start:end]
    if reaction not in sub:
        raise ValueError('REACTION_MISMATCH:'+subentry)
    if 'STATUS     (CURVE)' not in sub and subentry=='M0826003':
        raise ValueError('CURVE_PROVENANCE_MISSING')
    lines=sub.splitlines()
    i=next(i for i,line in enumerate(lines) if line.startswith('DATA '))
    if lines[i].split()[1:3]!=[str(len(header.split())),str(n)]:
        raise ValueError('SOURCE_COUNT_MISMATCH')
    if lines[i+1].split()!=header.split() or lines[i+2].split()!=unit.split():
        raise ValueError('SOURCE_UNIT_OR_COLUMNS_MISMATCH')
    dat=[line.split() for line in lines[i+3:i+3+n]]
    if len(dat)!=n or any(len(r)!=len(header.split()) for r in dat):
        raise ValueError('SOURCE_ROW_FORMAT')
    if not lines[i+3+n].startswith('ENDDATA'):
        raise ValueError('SOURCE_ENDDATA_MISSING')
    return [[float(x) for x in r] for r in dat]


def source_angular(root:Path):
    raw=checked_source(root,'M0826')
    checked_source(root,'M0011')
    if not 'EN-MIN     EN-MAX\nMEV        MEV\n    30.        50.' in raw.decode('ascii'):
        raise ValueError('SOURCE_ENERGY_SUPPORT_CHANGED')
    rows=source_rows(raw,'M0826003',
      'ANG-CM-MIN ANG-CM-MAX DATA-CM ERR-S',
      'ADEG ADEG MU-B/SR MU-B/SR',9,
      '(2-HE-4(G,D)1-H-2,,DA)')
    if rows[0][0]!=0. or rows[-1][1]!=180.:
        raise ValueError('ANGLES_NOT_FULL_SPHERE')
    if any(rows[i][1]!=rows[i+1][0] for i in range(8)):
        raise ValueError('ANGULAR_GAP')
    if any(d<0 or e<0 or lo<0 or hi>180 or lo>=hi for lo,hi,d,e in rows):
        raise ValueError('SOURCE_BAD_DA')
    return rows


def angle_bins(rows):
    bins=[]
    for i,(lo,hi,d,err) in enumerate(rows):
        mu_hi=math.cos(math.radians(lo))
        mu_lo=math.cos(math.radians(hi))
        omega=2*math.pi*(mu_hi-mu_lo)
        m2_low=0.0 if mu_lo<=0<=mu_hi else min(mu_lo*mu_lo,mu_hi*mu_hi)
        m2_high=max(mu_lo*mu_lo,mu_hi*mu_hi)
        m2_const=(mu_hi**2+mu_hi*mu_lo+mu_lo**2)/3
        bins.append({'row':i+1,'subentry':'M0826003','theta_cm_lo_deg':lo,'theta_cm_hi_deg':hi,
          'DA_muB_sr':d,'ERR_S_muB_sr':err,'solid_angle_sr':omega,
          'source_bin_weight_muB':d*omega,
          'source_err_box_weight_lo_muB':max(0.,d-err)*omega,
          'source_err_box_weight_hi_muB':(d+err)*omega,
          'mu_lo':mu_lo,'mu_hi':mu_hi,
          'mu2_bin_support_min':m2_low,'mu2_bin_support_max':m2_high,
          'mu2_piecewise_constant_reference':m2_const})
    if abs(sum(b['solid_angle_sr'] for b in bins)-4*math.pi)>1.e-12:
        raise ValueError('SOLID_ANGLE_CLOSURE_FAIL')
    return bins


def weighted_moment_bounds(bins,weight_key,mu2_key):
    total=sum(b[weight_key] for b in bins)
    if total<=0:raise ValueError('UNPOSITIVE_SOURCE_WEIGHT')
    return sum(b[weight_key]*b[mu2_key] for b in bins)/total


def source_error_box_extrema(bins):
    # Exact endpoint search over 2^9 numerator/denominator vertices, assuming
    # each reported ERR-S interval is a Cartesian box, NOT a joint-confidence region.
    lower=[];upper=[]
    for bits in itertools.product((0,1),repeat=len(bins)):
        weights=[b['source_err_box_weight_hi_muB'] if bit else b['source_err_box_weight_lo_muB'] for bit,b in zip(bits,bins)]
        den=sum(weights)
        if den<=0:continue
        lower.append(sum(w*b['mu2_bin_support_min'] for w,b in zip(weights,bins))/den)
        upper.append(sum(w*b['mu2_bin_support_max'] for w,b in zip(weights,bins))/den)
    if not lower:raise ValueError('EMPTY_SOURCE_ERROR_BOX')
    return (min(lower),max(upper))


def pair_kinematics(egamma:float):
    M=M_ALPHA_MEV;m=M_D_MEV
    Q=2*m-M
    s=M*M+2*M*egamma
    threshold=((2*m)**2-M*M)/(2*M)
    if egamma<threshold:
        raise ValueError('BELOW_PHOTODISINTEGRATION_THRESHOLD')
    sqrt_s=math.sqrt(s)
    q=math.sqrt(s/4-m*m)
    boost=M+egamma
    beta_cm=egamma/boost
    amp=egamma*q/sqrt_s
    mean_kin=(egamma-Q)/2
    return {'gamma_energy_alpha_rest_MeV':egamma,'M_alpha_c2_MeV':M,'m_d_c2_MeV':m,
       's_MeV2':s,'sqrt_s_MeV':sqrt_s,'q_cm_times_c_MeV':q,
       'beta_cm':beta_cm,'gamma_cm':boost/sqrt_s,
       'Q_MeV':Q,'threshold_Egamma_MeV':threshold,
       'pair_total_D_kinetic_alpha_rest_MeV':egamma-Q,
       'daughter_mean_kinetic_alpha_rest_MeV':mean_kin,
       'daughter_energy_angular_amplitude_MeV':amp,
       'daughter_K_min_MeV':mean_kin-amp,'daughter_K_max_MeV':mean_kin+amp}


def build(root:Path)->dict:
    bins=angle_bins(source_angular(root))
    norm=sum(b['source_bin_weight_muB'] for b in bins)
    for b in bins:b['nominal_P_bin_conditioned_on_DA_bin_mean']=b['source_bin_weight_muB']/norm
    m2_min=weighted_moment_bounds(bins,'source_bin_weight_muB','mu2_bin_support_min')
    m2_max=weighted_moment_bounds(bins,'source_bin_weight_muB','mu2_bin_support_max')
    m2_mid=weighted_moment_bounds(bins,'source_bin_weight_muB','mu2_piecewise_constant_reference')
    rect_min,rect_max=source_error_box_extrema(bins)
    conditions=[]; bin_atlas=[]
    for E in REFERENCE_E_MEV:
        kin=pair_kinematics(E)
        A=kin['daughter_energy_angular_amplitude_MeV']
        kin['daughter_kinetic_variance_MeV2_bin_shape_min']=A*A*m2_min
        kin['daughter_kinetic_variance_MeV2_bin_shape_max']=A*A*m2_max
        kin['daughter_kinetic_variance_MeV2_flat_in_bin_reference']=A*A*m2_mid
        kin['daughter_kinetic_variance_MeV2_ERR_S_box_low']=A*A*rect_min
        kin['daughter_kinetic_variance_MeV2_ERR_S_box_high']=A*A*rect_max
        kin['NOT_measured_monochromatic']=True
        conditions.append(kin)
        for b in bins:
            klow=kin['daughter_mean_kinetic_alpha_rest_MeV']+A*b['mu_lo']
            khigh=kin['daughter_mean_kinetic_alpha_rest_MeV']+A*b['mu_hi']
            bin_atlas.append({'source_id':'M0826003','row':b['row'],'gamma_energy_evaluation_MeV':E,
              'energy_is_source_reported_monochromatic':False,
              'theta_cm_lo_deg':b['theta_cm_lo_deg'],'theta_cm_hi_deg':b['theta_cm_hi_deg'],
              'conditional_DA_shape_probability':b['nominal_P_bin_conditioned_on_DA_bin_mean'],
              'one_daughter_K_support_MeV':[klow,khigh],
              'partner_daughter_K_support_MeV':[2*kin['daughter_mean_kinetic_alpha_rest_MeV']-khigh,2*kin['daughter_mean_kinetic_alpha_rest_MeV']-klow],
              'paired_kinetic_sum_MeV':2*kin['daughter_mean_kinetic_alpha_rest_MeV']})
    return {'schema':'HE_DD_M0826_EXFOR_SHAPE_CONDITIONAL_FASTD_KINEMATICS_V1',
       'authority':{'repository':'IAEA-NDS/exfor_master','commit':'939a14d7bba1ddce51975cb5e8711ce96b3b0871','source_git_blobs':{k:v['blob'] for k,v in SOURCE.items()},'source_sha256':{k:v['sha256'] for k,v in SOURCE.items()},'experiment':'Arkatov et al. 1972','angular_status':'CURVE_FROM_FIG_1','record_count':9,'source_gamma_energy_support_MeV':[30.,50.]},
       'assumptions':{'angular_DA_values_as_bin_solid_angle_average':'CONDITIONAL_NOT_EXPERIMENTALLY_ESTABLISHED',
          'unknown_within_bin_distribution':'SHARP_SUPPORT_BOUNDS',
          'energy_angular_separability':'NOT_ESTABLISHED',
          'ERR_S_cartesian':'WHAT_IF_NOT_JOINT_CONFIDENCE',
          'daughter_exchange_symmetry':'EXACT_FINAL_IDENTICAL_DEUTERONS',
          'source_sigma_event_counting':'UNQUALIFIED',
          'detector_acceptance':'UNQUALIFIED',
          'actual_gamma_phase_space':'MISSING','Dfast_transport_stopping_deposition':'MISSING'},
       'angular_bins':bins,
       'normalized_angular_moments':{'mu2_nominal_low':m2_min,'mu2_nominal_high':m2_max,
            'mu2_flat_in_bin_reference':m2_mid,'mu2_ERR_S_cartesian_min':rect_min,'mu2_ERR_S_cartesian_max':rect_max,
            'all_are_conditional_on_bin_average_interpretation':True,
            '4pi_DA_reported_muB':norm},
       'reference_energy_evaluations':conditions,'derived_pair_bin_atlas':bin_atlas,
       'data_grain':{'new_original_experiments':0,'original_M0826_DA_rows_reused':9,'new_parametric_pair_bin_records':len(bin_atlas)},
       'DAG':{'central':'28/88','HE_physical':'14/18','new_source_scoped':'2/2','physical_delta':0},
       'production':{'R_event':None,'heat_rate':None,'kappa':None,'D_fast_pool':None,
                     'L4':False,'physical_activation':False,'status':'HOLD'}}


def dump(root:Path)->dict:
    d=build(root)
    out=root/'results'/'M0826_FASTD_ANGULAR_MOMENT_ATLAS.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    return d


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args()
    d=dump(args.root)
    print(json.dumps({'moments':d['normalized_angular_moments'],'kinematics':d['reference_energy_evaluations'],'DAG':d['DAG']},indent=2))
if __name__=='__main__':main()
