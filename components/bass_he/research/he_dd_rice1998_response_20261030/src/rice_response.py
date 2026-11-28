#!/usr/bin/env python3
"""Source-exact Rice (1998) detector Jacobian, SAL yields, LEGS raw candidates, Schiff flux.
All units explicit. No cosmological 150-250MeV gamma field, ionized-plasma D stopping, or production heat inferred.
"""
from __future__ import annotations
import argparse,csv,json,math,hashlib
from pathlib import Path

M_ALPHA_MEV=3727.3794118
M_D_MEV=1875.612945
ROOT=Path(__file__).resolve().parents[1]

def kinematics(eg:float, theta_cm_deg:float, m_alpha=M_ALPHA_MEV, m_d=M_D_MEV):
    """Exact target-at-rest two-body SR Jacobian J=dOmega_lab/dOmega_cm and lab angle."""
    if eg <= (4*m_d*m_d-m_alpha*m_alpha)/(2*m_alpha):
        raise ValueError('photon below exact dd threshold')
    if not 0 <= theta_cm_deg <= 180:raise ValueError('out-of-domain CM theta')
    s=m_alpha*m_alpha+2*m_alpha*eg
    sqs=math.sqrt(s)
    e_star=sqs/2
    p_star=math.sqrt(s/4-m_d*m_d)
    beta=eg/(m_alpha+eg)
    gam=(m_alpha+eg)/sqs
    mu=math.cos(math.radians(theta_cm_deg))
    para=gam*(p_star*mu+beta*e_star)
    perp=p_star*math.sqrt(max(0.,1-mu*mu))
    p_lab=math.hypot(para,perp)
    angle_lab=math.degrees(math.atan2(perp,para))
    jac=gam*p_star*p_star*(p_star+beta*e_star*mu)/p_lab**3
    return {'theta_lab_calc_deg':angle_lab,'J_calculated':abs(jac),'pair_sum_K_MeV':eg+m_alpha-2*m_d,'pstar_MeV_over_c':p_star}

def schiff_shape(k:float, eo=273.,Z=13.,me=.511,C=111.):
    """Shape of original Rice Appendix A.1 Schiff differential bremsstrahlung formula.
    Overall factor 2 Z^2 r_e^2 / 137 cancels in spectral ratios. Input k,eo,me MeV.
    """
    e=eo-k
    if k<=0 or e<=0:return 0.
    z13=Z**(1./3.)
    mx=1./((me*k/(2.*eo*e))**2+(z13/C)**2)
    b=2.*eo*e*z13/(C*me*k)
    first=((eo*eo+e*e)/eo**2-2.*e/(3.*eo))*(math.log(mx)+1.-2.*math.atan(b)/b)
    second=(e/eo)*(2.*math.log1p(b*b)/(b*b)+4.*(2.-b*b)*math.atan(b)/(3.*b**3)-8./(3.*b*b)+2./9.)
    return (first+second)/k

def simpson(f,a,b,segments=6000):
    if not (a<b and segments>0 and segments%2==0):raise ValueError('invalid Simpson domain')
    h=(b-a)/segments
    s=f(a)+f(b)
    for j in range(1,segments):s+=(4 if j%2 else 2)*f(a+j*h)
    return s*h/3

def rate_asym(n0,n90,f0,f90):
    # Instrumental ratio based on tagged polarization counting; not decontaminated nuclear A(theta).
    if min(n0,n90,f0,f90)<=0:raise ValueError('positive counts and flux needed')
    a=n0/f0;b=n90/f90
    t=(a-b)/(a+b)
    sd=(1-t*t)*math.sqrt(1/n0+1/n90)/2
    return t,sd

def load(root=ROOT):
    d=json.loads((root/'inputs/RICE_1998_SOURCE_DATA.json').read_text())
    p=json.loads((root/'inputs/RICE2000_TABLE_I_AUTHORITATIVE_PR128.json').read_text())
    return d,p

def write_csv(path,rows):
    assert rows
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

def run(root=ROOT):
    src,pub=load(root)
    rows=[];spec=[]
    for bin_id in ('150-190','190-250'):
        tbl=src['sal'][bin_id]
        P=[r for r in pub['observations'] if r['bin']==bin_id]
        assert len(tbl)==len(P)==6
        for i,(a,b) in enumerate(zip(tbl,P)):
            assert a['lab_angle_deg']==b['theta_lab'] and a['cm_angle_deg']==b['theta_cm']
            calc=kinematics(src['experiment_midpoints_MeV'][bin_id],a['cm_angle_deg'])
            J=src['jacobians_thesis_table3_2'][bin_id][i]
            f=src['f_pb_sr'][bin_id]
            ds=a['yield']*J*f/1000
            ds_sd=a['yield_stat_sd']*J*f/1000
            rows.append({'bin_MeV':bin_id,'lab_theta_deg':a['lab_angle_deg'],'CM_theta_deg':a['cm_angle_deg'],'yield_1998':a['yield'],'yield_stat_sd':a['yield_stat_sd'],'J_thesis':J,'J_SR_exact':round(calc['J_calculated'],9),'lab_theta_SR_exact_deg':round(calc['theta_lab_calc_deg'],6),'f_pb_sr_per_yield':f,'reconstructed_1998_nb_sr':round(ds,9),'thesis_1998_nb_sr':a['prelim_dsigma_nb_sr'],'reconstructed_stat_sd_nb_sr':round(ds_sd,9),'thesis_stat_sd_nb_sr':a['prelim_stat_sd_nb_sr'],'stat_error_internal_source_mismatch':abs(ds_sd-a['prelim_stat_sd_nb_sr'])>.003,'published_2000_nb_sr':b['sigma'],'published_stat_sd_nb_sr':b['stat_sd'],'published_to_thesis_ratio':round(b['sigma']/a['prelim_dsigma_nb_sr'],9),'source_status':'preliminary_same_experiment_vs_published_no_independence'})
    norm=simpson(schiff_shape,171.,212.)
    for label,x,y in [('150-190',150,190),('190-250',190,250),('190-270_DIAGNOSTIC',190,270)]:
        val=simpson(schiff_shape,x,y)
        rep=src['schiff']['author_reported_flux_ratios'].get(label)
        spec.append({'interval':label,'Emin_MeV':x,'Emax_MeV':y,'integral_arbitrary_units':val,'ratio_to_tagged_171_212':val/norm,'author_ratio':rep,'status':'NOT_AUTHOR_ENERGY_BIN' if 'DIAGNOSTIC' in label else ('SOURCE_REPRODUCED' if abs(val/norm-rep)<.005 else 'CONCERN_SOURCE_RATIO_NOT_REPRODUCED')})
    legs=[]
    for v in src['legs_raw']:
        a,b=v['raw_counts_0deg'],v['raw_counts_90deg'];q0,q90=v['CG3_flux_0deg_e9'],v['CG3_flux_90deg_e9'];acc=v['accidental_fraction']
        sig,sd=rate_asym(a,b,q0,q90)
        legs.append({'detector':v['detector'],'lab_angle_deg':v['lab_angle_deg'],'raw_counts_parallel':a,'raw_counts_perpendicular':b,'CG3_flux_parallel_e9':q0,'CG3_flux_perpendicular_e9':q90,'accidental_fraction_bin':acc,'common_accidental_corrected_rate_parallel':(1-acc)*a/q0,'common_accidental_corrected_rate_perp':(1-acc)*b/q90,'flux_corrected_raw_asymmetry':round(sig,8),'Poisson_only_sd':round(sd,8),'interpretation':'instrumental_candidate_ratio_not_npd_cleaned_not_physical_A'})
    res=root/'results';res.mkdir(exist_ok=True)
    write_csv(res/'SAL_SOURCE_NORMALIZATION_12.csv',rows)
    write_csv(res/'SCHIFF_SOURCE_FLUX_RATIOS_3.csv',spec)
    write_csv(res/'LEGS_RAW_POLARIZATION_CANDIDATES_10.csv',legs)
    ratio=[r['published_to_thesis_ratio'] for r in rows]
    out={'schema':'BASS_HE_PR130_SOURCE_RESPONSE_V1','canonical_central_dag':'28/88','HE_physical_dag':'14/18','new_source_micro_dag':'2/2_SCOPED','native_subagent':'NOT_RUN','physical_DAG_delta':0,'rows_detector_J_calibrated':12,'rows_LEGS_raw_polarization':10,'Schiff_spectrum_rows':3,'experimental_campaigns_reused':{'SAL':'one same 1996 experiment in 1998 and 2000','LEGS':'distinct 1993 low-statistics experiment','Asbury':'prior independent 1965 experiment unchanged'},'stat_error_source_inconsistency_rows':sum(r['stat_error_internal_source_mismatch'] for r in rows),'stat_error_inconsistency_detail':'1998 Table5.1 last row 827 ±136 yields computed 0.14042 nb/sr statistical SD vs printed 0.122 nb/sr, requires source clarification','max_absolute_cross_section_rounded_source_error_nb_sr':max(abs(r['reconstructed_1998_nb_sr']-r['thesis_1998_nb_sr']) for r in rows),'max_J_reported_minus_SR_exact':max(abs(r['J_thesis']-r['J_SR_exact']) for r in rows),'author_flux_ratio_low':src['schiff']['author_reported_flux_ratios']['150-190'],'direct_Schiff_ratio_low':spec[0]['ratio_to_tagged_171_212'],'author_flux_ratio_high':src['schiff']['author_reported_flux_ratios']['190-250'],'direct_Schiff_ratio_high':spec[1]['ratio_to_tagged_171_212'],'diagnostic_190_270_ratio':spec[2]['ratio_to_tagged_171_212'],'author_high_to_direct_high_ratio':src['schiff']['author_reported_flux_ratios']['190-250']/spec[1]['ratio_to_tagged_171_212'],'published_over_thesis_first11_mean_descriptive':sum(ratio[:11])/11,'published_over_thesis_last_row':ratio[-1],'missing_actual_cosmological_gamma_history':True,'missing_Dfast_ionized_plasma_deposition':True,'missing_experiment_covariance':True,'kappa':None,'R_event':None,'heat_rate':None,'L4':False,'PRODUCTION':'HOLD','source_anomalies':['1998 Appendix A1 sample code midbin sum upper k290 conflicts prose low k190','published 1998 high flux ratio 1.546 differs from literal A1 formula 1.2575; investigate unprovided corrections','1998 dissertation world Asbury DA 8.0±2.5 nb/sr conflicts original 1965 Asbury TableII 6.3±2.2; source-version note','1998 Table5.1 132.2deg low-bin yield 827±136 disagrees with printed dσ statistical SD 0.122, reconstructed 0.14042','1998 SAL preliminary 12 vs 2000 final same experiment and high final row is different direction','LEGS raw candidate asymmetry not physical analyzed A(theta), contaminated npd'], 'sources':{'Rice98_sha256':src['pdf_sha256'],'Rice2000_json_sha256':src['rice2000_source_sha256']}}
    (res/'SCIENCE_SUMMARY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k in ('max_absolute_cross_section_rounded_source_error_nb_sr','max_J_reported_minus_SR_exact','direct_Schiff_ratio_low','direct_Schiff_ratio_high','published_over_thesis_first11_mean_descriptive','author_high_to_direct_high_ratio')},indent=2))
    return out,rows,spec,legs

if __name__=='__main__':run()
