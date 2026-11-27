#!/usr/bin/env python3
"""Complete only previously unverified unequal-IC Jacobian points; no ODE.

The first receipt's Li6=0 boundary IC cannot admit a two-sided perturbation in
aggregate Li ionization. Use one new interior point, then the two original
points never reached by the first batch. No completed Jacobian point is rerun.
"""
from __future__ import annotations
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS"):
    os.environ[key]="1"
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
from datetime import datetime,timezone
import numpy as np
import scipy
import scipy.integrate

ROOT=Path('/tmp/hh_phys79_work/WU088_HH/research/hh_phys80_sandbox_reduction_20261022')
OUT=Path('/tmp/phys80_review/jacobian_supplement_001.json')
if OUT.exists():raise SystemExit('CREATE_ONLY_SUPPLEMENT_ALREADY_EXISTS')
FIRST_PATH=Path('/tmp/phys80_review/check_result_001.json')
FIRST=json.loads(FIRST_PATH.read_text())
for relative,expected in FIRST['source_hashes_before'].items():
    assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected,relative
ODE_CALLS=0
def forbidden_ode(*args,**kwargs):
    global ODE_CALLS
    ODE_CALLS+=1
    raise AssertionError('ODE_FORBIDDEN')
scipy.integrate.solve_ivp=forbidden_ode
sys.path.insert(0,str(ROOT/'source'))
from reduced import ExactReduction
from phys79_bridge import CASES,collisions,atomic
p=copy.deepcopy(CASES['C01_BASE']['binding']['physics'])
y=np.array(p['initial_Y_per_H'])
for isotope,fraction in {'He3':1.,'He4':.10,'Li6':0.,'Li7':.40}.items():
    inventory=p['isotope_inventory_per_H'][isotope]
    y[atomic.SPECIES_INDEX[isotope+'_I']]=inventory*(1-fraction)
    y[atomic.SPECIES_INDEX[isotope+'_II']]=inventory*fraction
p['initial_Y_per_H']=y.tolist()
p['initial_u_eV_per_H']=collisions.CollisionNetwork(ci_rows=p['ci_rows'],d_cx=True).thermal_energy(p['T_initial_K'],y)
model=ExactReduction(p)
offsets=[np.array([.005,.005,.002,.02]),np.array([.015,.010,.008,.10]),np.array([.040,.040,.020,.30])]
calls=0
def function(z):
    global calls
    calls+=1
    return model.rhs(0.,z)
checks=[]
for i,offset in enumerate(offsets):
    z=model.z0+offset
    jac=model.jacobian(0.,z)
    columns=[]
    for j in range(4):
        step=max(abs(float(z[j])),1e-4)*np.finfo(float).eps**.2
        delta=np.zeros(4);delta[j]=step
        columns.append((function(z-2*delta)-8*function(z-delta)+8*function(z+delta)-function(z+2*delta))/(12*step))
    fd=np.column_stack(columns)
    error=abs(jac-fd)
    component=float(np.max(error/(1+abs(jac))))
    row=float(np.max(np.max(error,axis=1)/np.maximum(np.max(abs(jac),axis=1),1e-30)))
    checks.append({'point':'UNEQUAL_1_INTERIOR_NEW' if i==0 else 'UNEQUAL_1:'+str(i),
                   'z':z.tolist(),'component_normalized_error':component,'row_relative_error':row,
                   'pass':component<=2e-6 and row<=2e-6})
assert ODE_CALLS==0
report={'schema':'PHYS80_INDEPENDENT_JACOBIAN_SUPPLEMENT_V1','utc':datetime.now(timezone.utc).isoformat(),
        'command':'python -B /tmp/phys80_review/jacobian_interior_supplement.py',
        'versions':{'Python':platform.python_version(),'NumPy':np.__version__,'SciPy':scipy.__version__},
        'test_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'prior_receipt_sha256':hashlib.sha256(FIRST_PATH.read_bytes()).hexdigest(),
        'source_hashes':FIRST['source_hashes_before'],'actual_ODE_calls':ODE_CALLS,
        'old_suite_executions':0,'completed_Jacobian_points_replayed':0,
        'new_Jacobian_points':len(checks),'new_Jacobian_columns':12,'actual_RHS_finite_difference_calls':calls,
        'original_failure_class':'TEST_FIXTURE_OUTSIDE_STRICT_PHYSICAL_DOMAIN; no implementation defect',
        'original_failure_preserved':True,'checks':checks,'passed':all(c['pass'] for c in checks),
        'maximum_component_error':max(c['component_normalized_error'] for c in checks),
        'maximum_row_error':max(c['row_relative_error'] for c in checks),
        'claim_scope':'finite independent numerical derivatives on three previously unverified interior states; boundary two-sided derivative not claimed',
        'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
with OUT.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({key:report[key] for key in ('passed','new_Jacobian_points','new_Jacobian_columns','actual_RHS_finite_difference_calls','maximum_component_error','maximum_row_error','actual_ODE_calls')},indent=2))
raise SystemExit(0 if report['passed'] else 1)
