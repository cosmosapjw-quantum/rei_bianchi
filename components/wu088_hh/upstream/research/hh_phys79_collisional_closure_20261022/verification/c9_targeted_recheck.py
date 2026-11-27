"""Changed-dependency recheck only for C9-F1/F2/N1; initial review untouched."""
import sys,math,json,hashlib
from pathlib import Path
import numpy as np
root=Path('/tmp/hh_phys79_work/WU088_HH/research/hh_phys79_collisional_closure_20261022/source')
source_before=hashlib.sha256((root/'collisional.py').read_bytes()).hexdigest()
sys.path.insert(0,str(root));import collisional as c
A=c.atomic;ix=A.SPECIES_INDEX;empty=c.CollisionNetwork(ci_rows=(),d_cx=False)
checks=[]
def rejects(label,fn):
 try:
  result=fn();checks.append({'name':label,'passed':False,'returned':str(result)})
 except (ValueError,ArithmeticError) as error:
  checks.append({'name':label,'passed':True,'error_type':type(error).__name__,'reason':str(error)})
y=np.zeros(A.N_SPECIES);y[ix['H1_I']]=1e308;y[ix['He4_I']]=1e308
rejects('F1_aggregate_overflow_thermal_energy',lambda:empty.thermal_energy(300.,y))
rejects('F1_aggregate_overflow_temperature',lambda:empty.temperature(1.,y))
rejects('F1_aggregate_overflow_rhs',lambda:empty.rhs(300.,1.,y))
z=A.neutral_abundances()
rejects('F1_output_overflow_thermal_energy',lambda:empty.thermal_energy(1e308,z*1e308))
rejects('F1_output_overflow_temperature',lambda:empty.temperature(1e308,z))
rejects('F1_output_underflow_temperature',lambda:empty.temperature(np.nextafter(0.,1.),z*1e308))
for value in (math.inf,math.nan,-1.,0.):
 rejects('F1_invalid_thermal_input_'+str(value),lambda value=value:empty.temperature(value,z))
net=c.CollisionNetwork(ci_rows=(),d_cx=True)
conditioning=[]
for T in [2.7,10.,300.,1e4,25370.7,2e5]:
 for h in [1e-10,2e-4,.1,.5,.9,1-1e-10]:
  for d in [0.,1e-4,.01,.1,.5,.9,1.]:
   y=A.neutral_abundances();Yd=A.DEFAULT_INVENTORY['D'];y[ix['H1_I']]=1-h;y[ix['H1_II']]=h;y[ix['D_I']]=Yd*(1-d);y[ix['D_II']]=Yd*d
   r=net.rhs(T,1e-5,y);scale=float(np.sum(abs(net.delta_binding_eV*r.event_per_H_s)))
   direct=r.diagnostics['binding_derivative_direct_state_eV_per_H_s'];diff=r.diagnostics['binding_derivative_direct_minus_event_eV_per_H_s'];cs=r.diagnostics['binding_derivative_constituent_energy_scale_eV_per_H_s']
   conditioning.append({'T_K':T,'xH':h,'xD':d,'event_relative':abs(r.energy_ledger_residual_eV_per_H_s)/scale,'direct_minus_event_on_constituent_scale':abs(diff)/cs if cs else 0.,'diagnostic_preserved':bool(direct==float(net.binding_eV@r.d_species_per_H_dt))})
checks.append({'name':'F2_252_fixed_event_gate','passed':bool(all(r['event_relative']<=2e-13 for r in conditioning)),'cases':len(conditioning),'maximum_event_relative':max(r['event_relative'] for r in conditioning),'note':'Zero event-ledger residual is an operator construction; independent direct-state derivative retained separately.'})
checks.append({'name':'F2_direct_diagnostic_preserved','passed':all(r['diagnostic_preserved'] for r in conditioning),'maximum_constituent_scaled_discrepancy':max(r['direct_minus_event_on_constituent_scale'] for r in conditioning)})
raw=c.CollisionNetwork(ci_rows=(),d_cx=True,d_cx_closure='raw_fit').rhs(300.,1.,A.neutral_abundances())
checks.append({'name':'N1_neutral_model_family_with_explicit_closure','passed':'DB43K' not in raw.diagnostics['model'] and raw.diagnostics['d_cx_closure']=='raw_fit','model':raw.diagnostics['model'],'closure':raw.diagnostics['d_cx_closure']})
source_after=hashlib.sha256((root/'collisional.py').read_bytes()).hexdigest()
checks.append({'name':'reviewed_source_stable_during_checks','passed':source_before==source_after})
out={'status':'PASS_TARGETED_C9_FIXES' if all(c['passed'] for c in checks) else 'FAIL_TARGETED_RECHECK','source_sha256':source_after,'checks':checks,'unique_targeted_checks':len(checks),'conditioning_cases':len(conditioning),'initial_review_preserved':'C9_REVIEW.json','closed_findings':['C9-F1','C9-F2','C9-N1'],'no_new_ode':True,'prior_core29_reused':True}
Path('/tmp/hh_phys79_thermal/C9_TARGETED_RECHECK.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
