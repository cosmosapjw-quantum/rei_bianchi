#!/usr/bin/env python3
from __future__ import annotations
import csv
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import numpy as np
import sympy as sp

getcontext().prec=90
root=Path(__file__).resolve().parents[1]
result=json.loads((root/'results.json').read_text())
with (root/'data/policy_trial_summary.csv').open(newline='',encoding='utf-8') as handle:
    rows=list(csv.DictReader(handle))
assert len(rows)==24
assert len({(r['lane'],r['policy_id']) for r in rows})==24
assert sum(r['load_bearing']=='True' for r in rows)==12
assert all(r['hard_gates_pass']=='True' for r in rows)
assert max(Decimal(r['local_error']) for r in rows)<Decimal('2e-4')
assert result['all_numerical_gates_pass'] is True
assert result['production_history_authorized'] is False
assert result['decision']['classification']=='CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED'
assert result['continuous_parameter_certificate']=='NOT_AVAILABLE_NONLINEAR_MONOTONICITY_NOT_PROVED'
for value in result['overall_widths'].values():
    assert Decimal(str(value))<Decimal('2e-3')

# Instantaneous branch coefficients are exactly multi-affine.
v,f,y,z,v0,v1,f0,f1,lv,lf=sp.symbols('v f y z v0 v1 f0 f1 lv lf', real=True)
ell=sp.Rational(57,40);m=sp.Rational(737,1000)
AH=v*((ell-m)+m*y)+(1-v)*f*z
AHe=v*m*(1-y)+(1-v)*f*(1-z)
checks={}
for name,expr in [('AH',AH),('AHeI',AHe)]:
    assert sp.diff(expr,v,2)==0
    assert sp.diff(expr,f,2)==0
    corner=(1-lv)*(1-lf)*expr.subs({v:v0,f:f0}) + lv*(1-lf)*expr.subs({v:v1,f:f0}) + (1-lv)*lf*expr.subs({v:v0,f:f1}) + lv*lf*expr.subs({v:v1,f:f1})
    param=expr.subs({v:(1-lv)*v0+lv*v1,f:(1-lf)*f0+lf*f1})
    residual=sp.factor(sp.expand(param-corner))
    assert residual==0
    checks[name]={'d2_v':str(sp.diff(expr,v,2)),'d2_f':str(sp.diff(expr,f,2)),'corner_residual':str(residual),'mixed_derivative':str(sp.diff(expr,v,f))}

# Stable science artifacts and lane workers.
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
with np.load(root/'data/strict_corner_envelopes.npz',allow_pickle=False) as data:
    for name in data.files:
        array=np.asarray(data[name])
        assert np.all(np.isfinite(array))
        if name.endswith('_lower'):
            upper=np.asarray(data[name[:-6]+'_upper'])
            assert np.all(array<=upper)
workers={}
for lane in ('local_neutral_hazard_primary','recombination_weighted_auditor','script_self_shielding_auditor'):
    payload=json.loads((root/f'data/lane_workers/{lane}.json').read_text())
    assert len(payload['rows'])==8 and payload['strict_endpoint_count']==4
    assert all(bool(row['hard_gates_pass']) for row in payload['rows'])
    workers[lane]={
        'json_sha256':sha(root/f'data/lane_workers/{lane}.json'),
        'npz_sha256':sha(root/f'data/lane_workers/{lane}.npz'),
    }

out={
 'classification':'R2B_R2A_R2_R1A_EXACT_VALIDATION',
 'policy_count':len(rows),'load_bearing_count':12,
 'multi_affine_checks':checks,
 'maximum_local_error':str(max(Decimal(r['local_error']) for r in rows)),
 'overall_widths':{k:str(Decimal(str(v))) for k,v in result['overall_widths'].items()},
 'workers':workers,
 'continuous_parameter_certificate':'NOT_PROVED_BY_INSTANTANEOUS_MULTI_AFFINITY',
 'status':'PASS',
}
(root/'receipts/EXACT_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
