"""Exact bounded prework checks; no physical provider or science history run."""
from fractions import Fraction as F
import json
from pathlib import Path

SPECIES = ['HI', 'HII', 'HeI', 'HeII', 'HeIII', 'e']
ROWS = {
 'H_nuclei': [1,1,0,0,0,0],
 'He_nuclei': [0,0,1,1,1,0],
 'electric_charge': [0,1,0,1,2,-1],
}
EVENTS = {
 'HI_primary_or_electron_impact': [-1,1,0,0,0,1],
 'HeI_primary_or_electron_impact': [0,0,-1,1,0,1],
 'HeII_primary_or_electron_impact': [0,0,0,-1,1,1],
 'HII_recombination': [1,-1,0,0,0,-1],
 'HeII_recombination': [0,0,1,-1,0,-1],
 'HeIII_recombination': [0,0,0,1,-1,-1],
 'HH_direct_ionization': [-1,1,0,0,0,1],
 'He2_H_CX': [-1,1,0,1,-1,0],
 'Hplus_H_resonant_CX_aggregate': [0,0,0,0,0,0],
}
def dot(a,b): return sum(F(x)*F(y) for x,y in zip(a,b))
checks = []
for event,col in EVENTS.items():
 for inv,row in ROWS.items():
  residual=dot(row,col); assert residual==0,(event,inv,residual)
  checks.append({'event':event,'invariant':inv,'exact_residual':str(residual)})
chi=[F('13.598434599702'),F('24.587389011'),F('54.417760')]
B=[0,chi[0],0,chi[1],chi[1]+chi[2],0]
for event,threshold,E in zip(list(EVENTS)[:3],chi,map(F,['13.7','24.7','54.5'])):
 dB=dot(B,EVENTS[event]); dU=E-threshold
 assert dB+dU-E==0
 checks.append({'event':event,'invariant':'absorbed_energy','exact_residual':'0'})
delta_B_CX=dot(B,EVENTS['He2_H_CX'])
assert delta_B_CX==chi[0]-chi[2]
# Polynomial identity I*(dt-Jx)-R*Jx = (I-k*x0)*psi,
# Jx=(I/k)*dt+(x0-I/k)*psi, with rational free test substitutions.
# General coefficient identity is separately recorded explicitly in PREWORK.
for I,R,x0,dt,psi in [(F(1,3),F(2,5),F(1,4),F(7),F(5,4)),
                     (F(0),F(3),F(1),F(5),F(1,3)),
                     (F(4),F(0),F(0),F(2),F(1,8))]:
 k=I+R;Jx=I/k*dt+(x0-I/k)*psi
 assert I*(dt-Jx)-R*Jx==(I-k*x0)*psi
out={'schema_version':'1.0','status':'EXACT_ALGEBRA_CHECKED',
 'scientific_runtime_executed':False,'physical_provider_executed':False,
 'species_order':SPECIES,'stoichiometric_columns':EVENTS,
 'checks':checks,'cx_binding_change_eV':str(delta_B_CX),
 'constant_rate_event_identity_rational_cases':3,
 'not_claimed':['rate accuracy','Rust implementation','full nonlinear map','whole first interval'],
 'method':'Python standard-library integer and Fraction arithmetic; finite event columns and exact energy identities'}
Path(__file__).with_name('RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('EXACT_ALGEBRA_CHECKED:',len(checks),'event invariants, 3 rational event identities')
