#!/usr/bin/env python3
"""Compare PHYS22 independent Decimal and inherited-function binary64 coefficients."""
import argparse
from decimal import Decimal as D, getcontext
import hashlib
import json
from pathlib import Path
getcontext().prec=80

def dec(x):return D.from_float(x) if isinstance(x,float) else D(x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--owner',type=Path,required=True)
    ap.add_argument('--gas',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():raise FileExistsError('Use a fresh output')
    o=json.loads(a.owner.read_text())['results'];g=json.loads(a.gas.read_text())
    n=o['normalized_by_shear_squared'];s2=dec(o['constants']['shear_squared_s2'])
    oc=o['actual_shear_time_coefficients'];gc=g['leading_initial_cohort'];gb=g['leading_continuous_birth_particular']
    values=[
      ('C_lambda',o['spectral']['CL'][0],g['local_radiation']['C_lambda_s^-1']),
      ('C_primary_heat',o['spectral']['CL'][3],g['local_radiation']['C_primary_heat_eV_s^-1']),
      ('HII_t3',oc['state_t3'][0],gc['eta_y_t3'][0]),
      ('thermal_w_t3',oc['state_t3'][3],gc['eta_y_t3'][3]),
      ('temperature_t3',oc['temperature_t3_K_s3'],gc['eta_T_t3_K_s^-3']),
      ('HeII_t4',oc['state_t4'][1],gc['eta_HeII_t4_s^-4']),
      ('HeIII_t4',oc['state_t4'][2],gc['eta_HeIII_t4_s^-4']),
      ('birth_HII_t4',s2*dec(n['birth_particular_t4'][0]),gb['eta_y_t4'][0]),
      ('birth_w_t4',s2*dec(n['birth_particular_t4'][3]),gb['eta_y_t4'][3]),
      ('birth_T_t4',s2*dec(n['birth_temperature_t4']),gb['eta_T_t4_K_s^-4']),
      ('birth_HeII_t5',s2*dec(n['birth_particular_He_t5']['HeII']),gb['eta_HeII_t5_s^-5']),
      ('birth_HeIII_t5',s2*dec(n['birth_particular_He_t5']['HeIII']),gb['eta_HeIII_t5_s^-5']),
    ]
    mat=o['baseline_local']['A_g0'];u3=n['eta_t3']
    for row in range(4):
        v=s2*sum((dec(mat[row][j])*dec(u3[j]) for j in range(4)),D(0))
        values.append(('A_g0_eta3_row_'+str(row),v,gc['A_local_initial_eta3'][row]))
    tol=D('5e-12');rows=[]
    for name,x,y in values:
        xx,yy=dec(x),dec(y);err=abs(xx-yy)/max(abs(xx),abs(yy),D('1e-200'))
        rows.append({'name':name,'Decimal80':str(xx),'binary64_as_exact_real':str(yy),'relative_difference':str(err),'pass':err<tol})
    result={'task':'REI-PHYS22-20261010','status':'PASS' if all(x['pass'] for x in rows) else 'FAIL',
      'scope':'New initial-time physical coefficients and local coupled forcing direction, not old-suite replay or native equivalence',
      'comparison':'Separate continuum Decimal80 transcription versus contributor binary64 evaluation of inherited PHYS21 local functions',
      'arithmetic_difference':'Exact-real-input T=50000 normalized by Decimal versus binary64 initial w roundtrip T=49999.99999999999; no exact byte/numerical identity claim',
      'relative_tolerance':str(tol),'comparisons':rows,'passed':sum(x['pass'] for x in rows),'total':len(rows),
      'max_relative_difference':str(max(dec(x['relative_difference']) for x in rows)),
      'inputs_sha256':{'owner':hashlib.sha256(a.owner.read_bytes()).hexdigest(),'gas':hashlib.sha256(a.gas.read_bytes()).hexdigest()},
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'native_runs':0,'gas_IVP_runs':0,'old_proof_replays':0}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','passed','total','max_relative_difference']}))
    if result['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
