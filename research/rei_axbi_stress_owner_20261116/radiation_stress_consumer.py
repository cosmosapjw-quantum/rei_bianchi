#!/usr/bin/env python3
"""Consume actual AXBI history moments; no original coupled ODE is executed."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import resource
import time

import numpy as np
import pandas as pd
import scipy
from scipy.integrate import cumulative_trapezoid, simpson

HERE = Path(__file__).resolve().parent
G = 6.67430e-11                     # m^3 kg^-1 s^-2
C = 299792458.0                    # m s^-1
KB = 1.380649e-23                  # J K^-1
EV = 1.602176634e-19               # J eV^-1
MPC_CM = 3.0856775814913673e24
H0 = 67.4e5 / MPC_CM
OM, OR = .315, .000092
OL = 1 - OM - OR
FHE = .2454 / (4 * (1 - .2454))
AI = 1 / 21
MYR = 31557600e6
COEFF = 8 * np.pi * G / (3 * C * C)
RAD0 = 3 * H0 * H0 * C * C * OR / (8 * np.pi * G)
COLS = ['q_ref', 'a', 'zbar', 'time_s', 'b', 'H_per_s', 's_per_s',
        'nH_proper_cm3', 'ne_proper_cm3', 'temperature_K', 'x_HII',
        'x_HeII', 'x_HeIII', 'photon_u_eV_per_H', 'J0_photon_u_eV_per_H',
        'J1_photon_u_eV_per_H', 'J2_photon_u_eV_per_H']


def require(condition, reason):
    if not bool(condition):
        raise ValueError(reason)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def hf(a):
    return H0 * np.sqrt(OR / a**4 + OM / a**3 + OL)


def local_moments(b, order=16):
    """Return J0-1,J2. Subtract the isotropic term before quadrature."""
    values = np.asarray(b, dtype=float)
    require(np.all(np.isfinite(values)), 'NONFINITE_B')
    require(np.max(np.abs(values), initial=0) < .02, 'OUTSIDE_LOCKED_B_DOMAIN')
    mu, w = np.polynomial.legendre.leggauss(order)
    p2 = (3 * mu * mu - 1) / 2
    energy, stress = np.empty_like(values), np.empty_like(values)
    flat, en, st = values.ravel(), energy.ravel(), stress.ravel()
    for start in range(0, flat.size, 8192):
        bb = flat[start:start+8192, None]
        u = np.expm1(-2 * bb) * (1 - mu**2) + np.expm1(4 * bb) * mu**2
        # 1/(1+u)^2 - 1, stably near b=0.
        difference = -u * (2 + u) / (1 + u)**2
        en[start:start+8192] = difference @ (w / 2)
        st[start:start+8192] = difference @ (w * p2 / 2)
    return energy, stress


def initial_direction_moments(b, order=32):
    """Independent momentum representation used for numerical cross-checks."""
    b = np.asarray(b, dtype=float)
    mu, w = np.polynomial.legendre.leggauss(order)
    r = np.sqrt(np.exp(2*b[:,None])*(1-mu**2) + np.exp(-4*b[:,None])*mu**2)
    moved = mu * np.exp(-2*b[:,None]) / r
    p2 = (3 * moved**2 - 1) / 2
    return (r-1) @ (w/2), (r*p2-(3*mu**2-1)/2) @ (w/2)


def read_source(root, spec):
    path = Path(root) / spec['relative_input']
    require(path.stat().st_size == spec['bytes'], 'SOURCE_SIZE')
    require(digest(path) == spec['sha256'], 'SOURCE_HASH')
    frame = pd.read_csv(path, usecols=COLS, float_precision='round_trip')
    require(len(frame) == spec['rows'], 'SOURCE_ROW_COUNT')
    require(np.isfinite(frame.to_numpy()).all(), 'NONFINITE_SOURCE')
    a, t = frame.a.to_numpy(), frame.time_s.to_numpy()
    require(np.all(np.diff(a)>0) and np.all(np.diff(t)>0), 'NONMONOTONE_SOURCE')
    require(a[0] == AI and a[-1] == .2 and t[0] == 0, 'SOURCE_ENDPOINTS')
    require(np.all(frame.q_ref == spec['q_ref']), 'SOURCE_Q')
    require(np.all(frame.nH_proper_cm3>0) and np.all(frame.temperature_K>0), 'NONPOSITIVE_GAS')
    require(np.all(frame.ne_proper_cm3>=0), 'NEGATIVE_ELECTRON_DENSITY')
    nh, ne = frame.nH_proper_cm3.to_numpy(), frame.ne_proper_cm3.to_numpy()
    charge = frame.x_HII.to_numpy()+FHE*(frame.x_HeII.to_numpy()+2*frame.x_HeIII.to_numpy())
    charge_residual = float(np.max(np.abs(ne/nh-charge)))
    require(charge_residual<=1e-12, 'CHARGE_PROPER_DENSITY')
    require(np.max(np.abs(nh*a**3/(nh[0]*a[0]**3)-1))<1e-12, 'COMOVING_NUCLEI')
    expected_s = spec['q_ref']*hf(AI)*(AI/a)**3
    expected_h = np.sqrt(hf(a)**2+expected_s**2)
    require(np.max(np.abs(frame.H_per_s.to_numpy()/expected_h-1))<2e-12,'GEOMETRY_H')
    require(np.max(np.abs((frame.s_per_s.to_numpy()-expected_s)/expected_h))<2e-12,'GEOMETRY_S')
    u0 = frame.J0_photon_u_eV_per_H.to_numpy()
    u1 = frame.J1_photon_u_eV_per_H.to_numpy()
    u2 = frame.J2_photon_u_eV_per_H.to_numpy()
    require(np.all(u0>=0) and np.all(np.abs(u2)<=u0+1e-14), 'PHOTON_MOMENT_DOMAIN')
    require(np.max(np.abs(u1)/np.maximum(u0,1))<1e-12, 'REFLECTION_ODD_MOMENT')
    require(np.max(np.abs(u0-frame.photon_u_eV_per_H.to_numpy()))<1e-12,'U0_ENERGY_OWNER')
    return frame, {'charge_max_abs_per_H':charge_residual,'rows':len(frame),'sha256':spec['sha256']}


def cumulative(y, x):
    return cumulative_trapezoid(y, x=x, initial=0)


def extremum(x, frame):
    i = int(np.argmax(np.abs(x)))
    return {'abs':float(abs(x[i])),'signed':float(x[i]),'native_row':i,
            'zbar':float(frame.zbar.iloc[i]),'elapsed_Myr':float(frame.time_s.iloc[i]/MYR)}


def calculate(frame):
    a = frame.a.to_numpy()
    t = frame.time_s.to_numpy()
    b = frame.b.to_numpy()
    h = frame.H_per_s.to_numpy()
    s = frame.s_per_s.to_numpy()
    nh = frame.nH_proper_cm3.to_numpy() * 1e6
    ne = frame.ne_proper_cm3.to_numpy() * 1e6
    u0 = frame.J0_photon_u_eV_per_H.to_numpy()
    u2 = frame.J2_photon_u_eV_per_H.to_numpy()
    e0, j2 = local_moments(b)
    background_radiation = RAD0/a**4
    dp_r = background_radiation*j2
    dp_ion = nh*u2*EV
    ds_r = COEFF*cumulative(a**3*dp_r,t)/a**3
    ds_ion = COEFF*cumulative(a**3*dp_ion,t)/a**3
    ds = ds_r + ds_ion
    dh_shear = (s/h)*(ds/h)
    dt_shear = -cumulative(dh_shear,t)
    de_r = background_radiation*e0
    gas_energy = 1.5*KB*frame.temperature_K.to_numpy()*(nh*(1+FHE)+ne)
    ion_energy = nh*u0*EV
    bg_energy = 3*C*C*hf(a)**2/(8*np.pi*G)
    extra = de_r+ion_energy+gas_energy
    dh_energy = (4*np.pi*G/(3*C*C*h*h))*extra
    dt_energy = -cumulative(dh_energy,t)
    # Independent variable and pressure normalization, using all native rows.
    lna = np.log(a)
    independent_r = H0*H0*OR/a[-1]**3*simpson(j2/(a*h),x=lna)
    nh0 = nh[0]*a[0]**3
    independent_ion = COEFF*nh0*EV/a[-1]**3*simpson(u2/h,x=lna)
    integration_gap = float(abs((independent_r+independent_ion-ds[-1])/h[-1]))
    require(integration_gap<2e-11,'INDEPENDENT_INTEGRATION')
    idx = np.unique(np.rint(np.linspace(0,len(frame)-1,65)).astype(int))
    ee, jj = initial_direction_moments(b[idx])
    e32, j32 = local_moments(b[idx],32)
    angular_gap = max(float(np.max(np.abs(ee-e0[idx]))),float(np.max(np.abs(jj-j2[idx]))))
    angular_refinement_gap = max(float(np.max(np.abs(e32-e0[idx]))),float(np.max(np.abs(j32-j2[idx]))))
    require(angular_gap<2e-13 and angular_refinement_gap<2e-13,'ANGULAR_REPRESENTATION')
    out = {
        'time_s':t,'elapsed_Myr':t/MYR,'a':a,'zbar':frame.zbar.to_numpy(),'b':b,'Sigma':s/h,
        'J0_effective_minus1':e0,'J2_effective':j2,
        'U2_ionizing_eV_per_H':u2,'DeltaP_effective_J_m3':dp_r,'DeltaP_ionizing_J_m3':dp_ion,
        'delta_s_effective_over_H':ds_r/h,'delta_s_ionizing_over_H':ds_ion/h,
        'delta_s_total_over_H':ds/h,'delta_H_shear_over_H':dh_shear,
        'delta_elapsed_time_shear_s':dt_shear,
        'effective_radiation_extra_to_background':de_r/bg_energy,
        'ionizing_energy_to_background':ion_energy/bg_energy,
        'thermal_energy_to_background':gas_energy/bg_energy,
        'extra_energy_to_background':extra/bg_energy,
        'delta_H_energy_over_H':dh_energy,'delta_elapsed_time_energy_s':dt_energy,
        'delta_elapsed_time_sum_diagnostic_s':dt_shear+dt_energy
    }
    stress_peak = extremum(ds/h,frame)
    energy_peak = extremum(extra/bg_energy,frame)
    active = np.abs(s/h)>1e-12
    ds_over_s = float(np.max(np.abs(ds[active]/s[active]))) if np.any(active) else None
    info={
        'native_rows':len(frame),'q_ref':float(frame.q_ref.iloc[0]),
        'stress_peak':stress_peak,'extra_energy_peak':energy_peak,
        'effective_stress_peak':extremum(ds_r/h,frame),
        'ionizing_stress_peak':extremum(ds_ion/h,frame),
        'max_abs_delta_s_over_s_where_defined':ds_over_s,
        'max_abs_delta_H_shear_over_H':float(np.max(np.abs(dh_shear))),
        'max_abs_delta_H_energy_over_H':float(np.max(np.abs(dh_energy))),
        'endpoint':{k:float(v[-1]) for k,v in out.items()},
        'original_stress_ceiling':1e-4,'original_energy_ceiling':1e-4,
        'stress_ceiling_pass':stress_peak['abs']<1e-4,
        'energy_ceiling_pass':energy_peak['abs']<1e-4,
        'independent_lna_Simpson_endpoint_delta_s_over_H':float((independent_r+independent_ion)/h[-1]),
        'independent_integration_abs_gap_delta_s_over_H':integration_gap,
        'angular_local_vs_initial_momentum_max_abs_gap':angular_gap,
        'angular_GL16_vs_GL32_max_abs_gap':angular_refinement_gap,
        'angular_audited_native_rows':len(idx),
        'quadrature_gap_is_evolution_error_bound':False,
        'scope':'FIRST_ORDER_DIAGNOSTIC_ON_ORIGINAL_SAVED_HISTORY'
    }
    return out, info


def write_csv(path, rows):
    with Path(path).open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
            with io.TextIOWrapper(gz,encoding='utf-8',newline='') as txt:
                w=csv.DictWriter(txt,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main(root, output):
    began, cpu = time.monotonic(), time.process_time()
    manifest = json.loads((HERE/'INPUT_MANIFEST.json').read_text())
    dest = Path(output)
    dest.mkdir(parents=True,exist_ok=True)
    require(not (dest/'STRESS_SUMMARY.json').exists(),'EXISTING_RESULT_NO_OVERWRITE')
    cases, checks, rows, halves = {}, {}, [], {}
    for spec in manifest['cases']:
        case = spec['id'];frame, checks[case] = read_source(root,spec)
        out, cases[case] = calculate(frame)
        idx = np.unique(np.rint(np.linspace(0,len(frame)-1,1001)).astype(int))
        for i in idx:
            row={'case':case,'q_ref':spec['q_ref'],'native_row':int(i)}
            row.update({k:float(v[i]) for k,v in out.items()});rows.append(row)
        if case in ['SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']:
            halves[case]=frame[['a','x_HII','x_HeII','x_HeIII','temperature_K']].to_numpy()
        require(time.monotonic()-began<120,'CONSUMER_WALL_CAP')
    pos, neg = halves['SHEAR_HALF_PLUS'],halves['SHEAR_HALF_MINUS']
    require(np.array_equal(pos[:,0],neg[:,0]),'PARITY_COORDINATE_GRID')
    parity={}
    for j,name in enumerate(['x_HII','x_HeII','x_HeIII','temperature_K'],start=1):
        odd=(pos[:,j]-neg[:,j])/2;floor=.01 if name=='temperature_K' else 1e-7
        parity[name]={'max_abs_odd_saved_response':float(np.max(np.abs(odd))),
                      'original_response_floor':floor,'above_floor':bool(np.max(np.abs(odd))>floor),
                      'interpretation':'SAVED_ESTIMATE_BELOW_FLOOR_NOT_EXACT_PARITY_OR_NULL_PROOF'}
    parity_out={'cases':['SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'],'native_rows_each':len(pos),
                'observables':parity,'missing_SHEAR_PLUS_manufactured':False,
                'full_evolution_refinement_uncertainty':'UNKNOWN_AX11'}
    (dest/'SCALAR_PARITY.json').write_text(json.dumps(parity_out,indent=2)+'\n')
    csv_path=dest/'stress_history.csv.gz';write_csv(csv_path,rows)
    summary={'schema':'rei.axbi.original-stress-consumer.v1',
             'status':'COMPLETED_SCOPED_PERTURBATIVE_DIAGNOSTIC',
             'cases':cases,'source_checks':checks,'original_rows_consumed':sum(c['native_rows'] for c in cases.values()),
             'output_rows':len(rows),'new_coupled_solver_trajectories':0,
             'central_completed':28,'central_total':88,'canonical_delta':0,
             'original_goal_completed':9,'original_goal_total':17,
             'previous_stress_case_coverage':2,'current_stress_case_coverage':4,'available_complete_cases':4,'requested_full_cases':5,
             'all_available_cases_below_original_ceilings':all(c['stress_ceiling_pass'] and c['energy_ceiling_pass'] for c in cases.values()),
             'constants_SI':{'G':G,'c':C,'k_B':KB,'eV_J':EV,'H0_per_s':H0,'Omega_r':OR},
             'result_sha256':{csv_path.name:digest(csv_path),'SCALAR_PARITY.json':digest(dest/'SCALAR_PARITY.json')},
             'code_sha256':digest(__file__),
             'runtime':{'wall_s':time.monotonic()-began,'cpu_s':time.process_time()-cpu,
                        'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__},
             'unresolved':['full +0.01 case','AX11 time/energy/angle refinement','AX12 source and IC variants',
                           'feedback propagated into coupled abundances','source and atomic model accuracy'],
             'claim_scope':'actual saved-model radiation stress and first-order geometry diagnostics; no coupled history replacement',
             'subagents':0,'independent_authorship':False}
    (dest/'STRESS_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'status':summary['status'],'rows':summary['original_rows_consumed'],
                      'outputs':len(rows),'runtime':summary['runtime'],
                      'stress_peak_by_case':{k:v['stress_peak'] for k,v in cases.items()},
                      'all_available_cases_below_original_ceilings':summary['all_available_cases_below_original_ceilings']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',required=True)
    p.add_argument('--output',default=str(HERE/'results'));a=p.parse_args()
    main(a.inputs,a.output)
