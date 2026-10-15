"""Reproduce bounded manufactured frozen-rate RR+CI+Verner photo study."""
from __future__ import annotations
import json
import hashlib
import sys
import time
import platform
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
sys.path.insert(0,str(root/'src'))
sys.path.insert(0,str(root/'tests'))
import source_aware as src
import thermal_bridge as tb
from test_thermal_bridge import state, MANUFACTURED, ZERO, independent_rhs, vector

start=state()
thermo=tb.ThermalReservoir(110.)
nh=1.e-3
dt=4.e10
initial=vector(start,thermo.thermal_ev_per_h,thermo.escape_ev_per_h)
start_s=time.perf_counter()
ref=solve_ivp(independent_rhs(start,MANUFACTURED,nh),(0.,dt),initial,
              method='DOP853',rtol=5e-13,atol=3e-15)
assert ref.success
ref_s=time.perf_counter()-start_s
runs=[]
for N in (1,2,4,8,16,32,64,128,256):
    t0=time.perf_counter()
    out,t,l=tb.evolve_coupled_photo_thermal(start,thermo,dt,nh,MANUFACTURED,reaction_substeps=N)
    elapsed=time.perf_counter()-t0
    actual=vector(out,t.thermal_ev_per_h,t.escape_ev_per_h)
    runs.append({'substeps':N, 'error_max_abs':float(np.max(np.abs(actual-ref.y[:,-1]))),
                 'elapsed_wall_s':elapsed,'number_residual_abs':abs(l.photon_number_residual),
                 'energy_residual_abs_eV_per_h':abs(l.total_energy_residual_ev_per_h),
                 'electron_residual_abs':abs(l.electron_charge_residual),
                 'ci_events':list(l.ci_events),'rr_events':list(l.rr_events),
                 'photo_events':list(l.photo_events),'T_diag_k':tb.temperature_k(out.gas,t.thermal_ev_per_h),
                 'escaped_ev_per_h':t.escape_ev_per_h,'thermal_ev_per_h':t.thermal_ev_per_h})
for prev,now in zip(runs[:-1],runs[1:]):
    now['previous_over_current_error_ratio']=prev['error_max_abs']/now['error_max_abs']
xs=np.log(np.array([1.0/v['substeps'] for v in runs[-5:]]))
ys=np.log(np.array([v['error_max_abs'] for v in runs[-5:]]))
order=float(np.polyfit(xs,ys,1)[0])
assert 1.95<order<2.05,order
baseline=tb.evolve_coupled_photo_thermal(start,thermo,dt,nh,ZERO,reaction_substeps=256)
source_dir=root/'upstream'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':'rei.C16B.source_aware_rr_ci_thermal.v1',
        'interpretation':'MANUFACTURED FROZEN RATES; RESEARCH REFERENCE ONLY',
        'original_PR154_commit':'daf653e87a5b208ed6f51113e83d56fec4abf4f8',
        'original_PR154_source_sha256':sha(root/'source_aware.py'),
        'original_PR154_git_blob':'db822a53da3ccdca7cf96628e9ef3bbcec83db5a',
        'original_PR150_snapshot':'fe789b0b13b1883c5a74cbc907f72f6f963a5d66',
        'native_rates_blob_sha1':'dc3cc028a41ac852d94835372ce13545389d1c3a',
        'native_thermal_blob_sha1':'0648618d9822e169e9672ac3c556f86595c3b0b6',
        'runtime':{'python':platform.python_version(),'numpy':np.__version__},
        'reference':{'solver':'SciPy DOP853','rtol':5e-13,'atol':3e-15,'seconds':ref_s,
                     'all_final_state':ref.y[:,-1].tolist()},
        'sample':{'proper_nh_cm3':nh,'proper_dt_s':dt,'initial_thermal_ev_per_h':110.,
                  'rates_alpha_rr':list(MANUFACTURED.alpha_rr_cm3_s),
                  'rates_beta_ci':list(MANUFACTURED.beta_ci_cm3_s),
                  'rr_electron_kinetic_ev':list(MANUFACTURED.rr_electron_kinetic_ev)},
        'refinement':runs,'last_five_measured_order':order,
        'physical_meaning':'positive exact analytic subflows under fixed external manufactured rate, matched independent DOP853 continuous RHS',
        'production_status':'NOT_IMPLEMENTED_NOT_VERIFIED',
        'remote_NCP_status':'NOT_RUN_QUOTA_BLOCKED',
        'external_physical_cooling_providers':'NATIVE_GRACKLE_OWNER_UNCONNECTED',
        'scientific_limits':['No dynamical T dependent Grackle coeff activation','No CE/DR/freefree/CMB/adiabatic gas terms',
                             'No recombination photon spectrum or local reionization from escape reservoir',
                             'No native two-moment photon closure replacement','No born-source or varying-geometry temporal convergence claim',
                             'No baryon recoil Euler partner or stellar energy-momentum closure']}
p=root/'evidence'/'study_results.json'
p.write_text(json.dumps(report,indent=2)+'\n')
print('Reference SciPy DOP853:',ref_s,'s, success',ref.success)
print('N  max|state-reference|  |Eledger|  |charge|')
for t in runs:print(t['substeps'],format(t['error_max_abs'],'.13g'),format(t['energy_residual_abs_eV_per_h'],'.4g'),format(t['electron_residual_abs'],'.4g'))
print('LAST5_CONVERGENCE_ORDER',order)
print('FINAL_PHOTO_EVENTS',runs[-1]['photo_events'])
print('FINAL_CI_EVENTS',runs[-1]['ci_events'])
print('FINAL_RR_EVENTS',runs[-1]['rr_events'])
print('FINAL_TDIAG_K',runs[-1]['T_diag_k'])
print('FINAL_ESC_RADIATION_EV_H',runs[-1]['escaped_ev_per_h'])
