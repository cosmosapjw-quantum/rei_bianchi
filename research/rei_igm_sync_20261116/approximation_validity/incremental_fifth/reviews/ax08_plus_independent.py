"""Finite independent read/check of the completed native +0.01 history only.

No production reduction is imported, no evolution is run, and the frozen
four histories are not read. Inputs must be post-terminal admitted artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(args):
    manifest = json.loads(args.composition.read_text())
    admission = manifest['admission']
    if admission['status'] != 'COMPLETE_COMPOSED_HISTORY':
        raise ValueError('NOT_COMPLETE_COMPOSED_HISTORY')
    digest = sha(args.history)
    if digest != admission['sha256']:
        raise ValueError('SOURCE_HASH_MISMATCH')
    d = pd.read_csv(args.history, float_precision='round_trip')
    a, b, t, h, s = (d[k].to_numpy() for k in ['a','b','time_s','H_per_s','s_per_s'])
    fHe = .2454/(4*(1-.2454))
    xcols = ['x_HI','x_HII','x_HeI','x_HeII','x_HeIII']
    nh = d.nH_proper_cm3.to_numpy()
    ne = d.ne_proper_cm3.to_numpy()
    temperature = d.temperature_K.to_numpy()
    u0, u1, u2 = (d[k].to_numpy() for k in ['J0_photon_u_eV_per_H','J1_photon_u_eV_per_H','J2_photon_u_eV_per_H'])
    h0 = 67.4e3/3.0856775814913673e22
    ai, q = 1/21, .01
    hf2 = h0*h0*(.000092/a**4+.315/a**3+(1-.315-.000092))
    s_expected = q*h0*np.sqrt(.000092/ai**4+.315/ai**3+(1-.315-.000092))*(ai/a)**3
    norm = 1+4*fHe
    y = np.column_stack([d.x_HI/norm,d.x_HII/norm,fHe*d.x_HeI/norm,
                         fHe*d.x_HeII/norm,fHe*d.x_HeIII/norm])
    residuals = {
        'H_sum':float(np.max(abs(d.x_HI+d.x_HII-1))),
        'He_sum':float(np.max(abs(d.x_HeI+d.x_HeII+d.x_HeIII-1))),
        'charge_per_H':float(np.max(abs(ne/nh-(d.x_HII+fHe*(d.x_HeII+2*d.x_HeIII))))),
        'nH_comoving_relative':float(np.max(abs(nh*a**3/(nh[0]*a[0]**3)-1))),
        'baryon_mass_sum':float(np.max(abs(y@np.array([1,1,4,4,4])-1))),
        'H_constraint_relative':float(np.max(abs((h*h-hf2-s*s)/(h*h)))),
        's_free_decay_relative':float(np.max(abs(s/s_expected-1))),
        'Sigma':float(np.max(abs(d.Sigma-s/h))),
        'zbar':float(np.max(abs(d.zbar-(1/a-1)))),
        'J0_vs_energy_inventory':float(np.max(abs(u0-d.photon_u_eV_per_H))),
        'J1_normalized':float(np.max(abs(u1)/np.maximum(u0,1e-30))),
    }
    checks = {
        'case_identity':set(d.case_id)=={'SHEAR_PLUS'} and np.all(d.q_ref==q),
        'native_row_count':len(d)==admission['rows']==admission['native_terminal_accepted']+1,
        'finite':bool(np.isfinite(d.drop(columns='case_id').to_numpy()).all()),
        'ordered':bool(np.all(np.diff(a)>0) and np.all(np.diff(t)>0)),
        'full_domain':bool(a[0]==ai and a[-1]==.2 and t[0]==0 and b[0]==0),
        'fractions':bool(d[xcols].min().min()>=0 and d[xcols].max().max()<=1),
        'density_and_temperature_domain':bool(np.all(nh>0) and np.all(ne>=0) and np.all(temperature>=1) and np.all(temperature<=1e6)),
        'radiation_positive':bool(np.all(u0>=0) and np.all(d.photon_n_per_H>=0)),
        'moment_cone':bool(np.all(u2>=-.5*u0-1e-30) and np.all(u2<=u0+1e-30)),
        'normalizations_and_geometry':max(residuals[k] for k in residuals if k not in ['J0_vs_energy_inventory','J1_normalized'])<=1e-12,
        'energy_inventory_identity':residuals['J0_vs_energy_inventory']==0,
        'reflection_even_control':residuals['J1_normalized']<=1e-12,
    }
    # Initial-direction moments: current local angle is mapped, not integrated
    # with an incorrectly uniform conserved-label measure.
    v,w = np.polynomial.legendre.leggauss(32)
    w=w/2
    m=np.empty_like(a);f=np.empty_like(a)
    for begin in range(0,len(a),8192):
        end=min(begin+8192,len(a));bc=b[begin:end,None]
        r=np.sqrt(np.exp(2*bc)*(1-v*v)+np.exp(-4*bc)*v*v)
        mu=np.exp(-2*bc)*v/r
        m[begin:end]=np.sum(r*w,axis=1)
        f[begin:end]=np.sum(r*(3*mu*mu-1)/2*w,axis=1)
    c,g,kb,ev=299792458.0,6.67430e-11,1.380649e-23,1.602176634e-19
    coupling=8*np.pi*g/(3*c*c)
    uref=h0*h0*.000092/(coupling*a**4)
    dpbg=uref*f;dpion=nh*1e6*ev*u2
    def integrate(dp):
        integrand=np.asarray(coupling*a**3*dp,dtype=np.longdouble)
        increments=(integrand[1:]+integrand[:-1])/2*np.diff(t).astype(np.longdouble)
        integral=np.r_[np.longdouble(0),np.cumsum(increments)]
        return np.asarray(integral/(a**3*h),dtype=float)
    dsbg,dsion,dstotal=(integrate(dp) for dp in [dpbg,dpion,dpbg+dpion])
    uion=nh*1e6*ev*u0
    uth=1.5*kb*temperature*(nh*(1+fHe)+ne)*1e6
    extra=(uion+uth+abs((m-1)*uref))/(hf2/coupling)
    peak=int(np.argmax(abs(dstotal)))
    numeric={
        'max_abs_total_delta_s_over_H':float(max(abs(dstotal))),
        'max_abs_background_delta_s_over_H':float(max(abs(dsbg))),
        'max_abs_ionizing_delta_s_over_H':float(max(abs(dsion))),
        'signed_total_delta_s_over_H_at_peak':float(dstotal[peak]),
        'stress_peak_zbar':float(1/a[peak]-1),
        'max_extra_energy_over_FLRW_background_source_comparator':float(max(extra)),
        'max_abs_total_delta_s_over_s':float(max(abs(dstotal*h/s))),
    }
    production=json.loads(args.production.read_text())
    comparison={k:abs(value-production[k]) for k,value in numeric.items()}
    spots=[]
    for i in sorted(set([0,1,min(240480,len(d)-1),peak,len(d)//2,len(d)-1])):
        spots.append({'original_row':i,'time_s':float(t[i]),'a':float(a[i]),
            'temperature_K':float(temperature[i]),'Y_HI':float(y[i,0]),
            'Y_HII':float(y[i,1]),'Y_HeI':float(y[i,2]),
            'Y_HeII':float(y[i,3]),'Y_HeIII':float(y[i,4]),
            'Y_e':float(ne[i]/nh[i]/norm),'xe_per_H':float(ne[i]/nh[i])})
    milestones=[]
    ion_fraction=d.x_HII.to_numpy()
    for level in [.1,.5,.9]:
        crossings=np.flatnonzero((ion_fraction[:-1]<level)&(ion_fraction[1:]>=level))
        if not len(crossings):
            milestones.append({'x_HII_level':level,'status':'NOT_REACHED'})
            continue
        i=int(crossings[0]);weight=(level-ion_fraction[i])/(ion_fraction[i+1]-ion_fraction[i])
        lna=(1-weight)*np.log(a[i])+weight*np.log(a[i+1])
        milestones.append({'x_HII_level':level,'status':'REACHED','lower_row':i,'upper_row':i+1,
            'zbar':float(np.exp(-lna)-1),'time_s':float((1-weight)*t[i]+weight*t[i+1])})
    cohort_path=args.production.parent/'COHORT_RESIDENCE_DIAGNOSTIC.json'
    cohort_checks=[]
    if cohort_path.is_file():
        cohort=json.loads(cohort_path.read_text())
        for field,components in cohort['at_response_peaks'].items():
            for component,item in components.items():
                i=int(item['nearest_native_row'])
                actual_nearest=int(np.argmin(abs(np.log(a)-np.log(1/(1+item['response_sample_zbar'])))))
                absorption=(1-d.x_HII.iloc[i])*d.Gamma_HI_per_s.iloc[i]+fHe*(d.x_HeI.iloc[i]*d.Gamma_HeI_per_s.iloc[i]+d.x_HeII.iloc[i]*d.Gamma_HeII_per_s.iloc[i])
                number=d.photon_n_per_H.iloc[i]
                rate=absorption/number if number>0 else None
                chi=abs(s[i])/rate if rate is not None and rate>0 else None
                cohort_checks.append({'field':field,'component':component,'native_row':i,
                    'nearest_row_matches':i==actual_nearest,
                    'lambda_abs_s_inv':float(rate) if rate is not None else None,
                    'chi':float(chi) if chi is not None else None,
                    'lambda_abs_difference':abs(float(rate)-item['lambda_abs_s_inv']) if rate is not None else None,
                    'chi_abs_difference':abs(float(chi)-item['chi_abs_s_over_lambda']) if chi is not None else None})
    result={
        'schema':'rei.ax08.plus-independent-native-review.v1',
        'status':'CHECKS_PASSED_FOR_INCREMENTAL_NATIVE_SOURCE' if all(checks.values()) else 'CHECK_FAILURE',
        'runtime':'PYTHON_PASS','python':sys.version,'source_sha256':digest,
        'composition_manifest_sha256':sha(args.composition),'production_sha256':sha(args.production),
        'rows':len(d),'checks':{k:bool(v) for k,v in checks.items()},'residuals':residuals,
        'independent_proper_time_trapezoid':numeric,'difference_from_production':comparison,
        'minimum_temperature_K':float(min(temperature)),'maximum_temperature_K':float(max(temperature)),
        'native_normalization_spot_rows':spots,'independent_milestones':milestones,
        'cohort_peak_spot_checks':cohort_checks,
        'new_solver_runs':0,'old_four_histories_reprocessed':False,
        'claim_scope':'One completed native plus history and frozen-forcing quadrature; does not alone admit AX08 artifacts or AX11/AX12/AX15.',
    }
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
    if not all(checks.values()):
        raise ValueError('FAILED_NATIVE_PLUS_CHECKS_SAVED')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ['history','composition','production','out']:
        parser.add_argument('--'+name,type=Path,required=True)
    run(parser.parse_args())
