#!/usr/bin/env python3
"""Read-only D7 analysis of saved histories; never calls an ODE integrator."""
from pathlib import Path
import csv, hashlib, json, math, os, sys
sys.dont_write_bytecode=True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE/'repo/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021'
RESULTS=BASE/'z2_extension/results'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def readjson(p):return json.loads(Path(p).read_text())
def scalar_row(z,i,S,rhs=None):
    fields=('x','a','b','elapsed_proper_s','H','s','P_m','P_r','P_total','Sigma_F','Sigma_half','p_m_J_m3','p_r_J_m3','p_total_J_m3','cancellation_fraction')
    d={k:float(z[k][i]) for k in fields}
    d.update(index=int(i),zbar=1/d['a']-1,signed_S_F=float(S[i]))
    if rhs is not None:d['S_F_prime_from_source']=float(rhs[i])
    return d

def main():
    gate=RESULTS/'CHECK.json'
    if not gate.exists():
        print('WAITING_FOR_FINAL_B2_CHECK');return 2
    check=readjson(gate)
    if check.get('completed_or_reused')!=237 or check.get('numerical_gate')!='PASS_SCOPED_PRELIMINARY':
        print('WAITING_FOR_COMPLETE_B2_DATA',check.get('completed_or_reused'),check.get('numerical_gate'));return 2
    entries={};all_entries=[]
    for folder in sorted((RESULTS/'cases').iterdir()):
        if not folder.is_dir():continue
        inp=readjson(folder/'INPUT.json');c=inp['config'];res=readjson(folder/'RESULT.json')
        if res.get('status')!='COMPLETED':raise ValueError('NONCOMPLETED_INPUT:'+folder.name)
        path=folder/'raw.npz'
        with np.load(path) as z:r={k:z[k] for k in z.files}
        S=np.sqrt(6)*r['s']/r['H']
        axes=(c['Sigma_F_i'],c.get('P_m_i',0.),c.get('P_r_i',c['Pi_F_signed_i']))
        row={'id':folder.name,'config':c,'axes':axes,'data':r,'S':S,'raw':path,
             'input_sha256':sha(folder/'INPUT.json'),'raw_sha256':sha(path),'receipt_sha256':sha(folder/'RESULT.json'),
             'prefix_raw_sha256':inp['prefix_raw_sha256']}
        all_entries.append(row)
        if not c['guard']:
            if axes in entries:raise ValueError('AMBIGUOUS_NOMINAL_AXES')
            entries[axes]=row
    if len(all_entries)!=237 or len(entries)!=231:raise ValueError('INPUT_COHORT_SIZE')
    sys.path.insert(0,str(BASE));import adapter
    B=readjson(HERE.parent/'recovery_physics/cancellation_curvature_check.json')['B_pressure_weighted_v2_over_c2']
    cases=[];history=[]
    for pm in (.0003,-.0003):
        e=entries[(0.,pm,-pm)];z=e['data'];S=e['S'];c=e['config'];obj=adapter.model(c)
        mom=obj.momentum.moment_batch(z['x'],z['b'])
        pressure_norm=obj._mass_pref*(2*mom[:,1]+mom[:,2])/3+z['rad_energy_norm']/3
        rho_norm=z['dust_energy_norm']+z['massive_energy_norm']+z['rad_energy_norm']
        h=-1.5*(obj.source.h0/z['H'])**2*(rho_norm+pressure_norm)-3*(z['s']/z['H'])**2
        deriv=-(3+h)*S+z['P_total']
        ipeak=int(np.argmax(abs(S)))
        brackets=[]
        for i in range(1,len(S)-1):
            if deriv[i]*deriv[i+1]<0:
                brackets.append({'lower_index':i,'upper_index':i+1,'earlier':scalar_row(z,i,S,deriv),'later':scalar_row(z,i+1,S,deriv)})
        result={k:e[k]for k in ('id','axes','input_sha256','raw_sha256','receipt_sha256','prefix_raw_sha256')}
        result.update(raw_path=str(e['raw'].relative_to(HERE/'repo')),
           initial=scalar_row(z,0,S,deriv),z4=scalar_row(z,120,S,deriv),z2=scalar_row(z,152,S,deriv),
           sampled_abs_shear_peak=scalar_row(z,ipeak,S,deriv),
           peak_scope='maximum over153 actually saved epochs; no fitted continuous extremum',
           rhs_sign_change_brackets=brackets,
           B_pressure_weighted_v2_over_c2=B,
           local_curvature_S_F_second=-(1-B)*pm,
           endpoint_abs_shear_over_sampled_peak=float(abs(S[-1])/abs(S[ipeak])),
           z2_over_z4_abs_shear=float(abs(S[-1])/abs(S[120])),
           data_status='saved numerical results; independent campaign admission recorded separately')
        cases.append(result)
        for i in range(len(S)):
            history.append({'id':e['id'],'P_m_i':pm,'P_r_i':-pm,**scalar_row(z,i,S,deriv),'h_Hprime_over_H':float(h[i])})
    planes=[];secants=[];sigmas=adapter.SIGMAS
    mgrid=[-.0003,-.0001,0.,.0001,.0003];rgrid=[-.001,-.0003,0.,.0003,.001]
    for sigma in sigmas:
        cell=[entries[(sigma,m,r)] for m in mgrid for r in rgrid]
        for epoch,i in ((4,120),(2,152)):
            vals=np.array([e['S'][i]for e in cell]);imin=int(np.argmin(vals));imax=int(np.argmax(vals))
            planes.append({'Sigma_F_i':sigma,'z_endpoint':epoch,'n':25,
                'min_signed_S_F':float(vals[imin]),'max_signed_S_F':float(vals[imax]),
                'min_case_id':cell[imin]['id'],'max_case_id':cell[imax]['id'],
                'negative_count_below_minus5e_minus12':int(np.count_nonzero(vals< -5e-12)),
                'near_zero_count_abs5e_minus12':int(np.count_nonzero(abs(vals)<=5e-12)),
                'positive_count_above5e_minus12':int(np.count_nonzero(vals>5e-12))})
            mp=entries[(sigma,.0003,0.)];mm=entries[(sigma,-.0003,0.)]
            rp=entries[(sigma,0.,.0003)];rm=entries[(sigma,0.,-.0003)]
            sm=float((mp['S'][i]-mm['S'][i])/.0006);sr=float((rp['S'][i]-rm['S'][i])/.0006)
            secants.append({'Sigma_F_i':sigma,'z_endpoint':epoch,'amplitude':.0003,
                'matter_central_secant':sm,'radiation_central_secant':sr,'radiation_to_matter_secant_ratio':sr/sm,
                'input_case_ids':[mp['id'],mm['id'],rp['id'],rm['id']],
                'scope':'central secants of four computed endpoints at fixed initial shear; not a fit or derivative theorem'})
    p,m=cases
    symmetry={}
    for key in ('z4','z2'):
        sp=p[key]['signed_S_F'];sm=m[key]['signed_S_F'];odd=(sp-sm)/2;even=(sp+sm)/2
        symmetry[key]={'odd_part':odd,'even_part':even,'abs_even_over_abs_odd':abs(even/odd)}
    ev={'schema':'rei.unified.D7.saved_history_interpretation.v1','execution':'postprocessing_only_no_IVPs',
      'input_check_sha256':sha(gate),'input_check_numerical_gate':check['numerical_gate'],
      'input_check_scientific_admission':check.get('scientific_admission'),
      'analysis_source_sha256':sha(__file__),'cohort':{'unique_histories':237,'nominal':231,'guards':6,'component_grid':175,'radiation_baseline':91,'shared_nominal':35,'epochs':153},
      'norm':'full spatial Frobenius; signed S_F=sqrt6*s/H, P_X=sqrt6*K*p_X/H²',
      'cancellation_cases':cases,'fixed_shear_planes':planes,'finite_secants':secants,'sign_reversal_even_odd':symmetry,
      'next_readonly_node':{'name':'cancellation_turnover_on_saved_histories','status':'COMPLETED','method':'grid maximum and instantaneous source-formula derivative brackets on existing153 samples','new_IVPs':0},
      'claims_basis':['derived','numerically checked'],'campaign_admission':'see independent final_audit receipt; this postprocessing does not issue admission'}
    (HERE/'NEW_SCIENTIFIC_EVIDENCE.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    with (HERE/'CANCELLATION_TURNOVER_SAMPLES.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
    print(json.dumps({'output':str(HERE/'NEW_SCIENTIFIC_EVIDENCE.json'),'cases':[{k:c[k]for k in ('id','z4','z2','sampled_abs_shear_peak','rhs_sign_change_brackets')}for c in cases],
        'planes':planes,'secants_Sigma0':[s for s in secants if s['Sigma_F_i']==0],'symmetry':symmetry},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
