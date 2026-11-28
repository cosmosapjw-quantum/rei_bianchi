"""Probe small isotope energy defects under the fixed event-energy gate."""
import sys,math,json,numpy as np
sys.path.insert(0,'/tmp/hh_phys79_work/WU088_HH/research/hh_phys79_collisional_closure_20261022/source')
import collisional as c
A=c.atomic;ix=A.SPECIES_INDEX;n=c.CollisionNetwork(ci_rows=(),d_cx=True)
rows=[]
for T in [2.7,10.,300.,1e4,25370.7,2e5]:
 for h in [1e-10,2e-4,.1,.5,.9,1-1e-10]:
  for d in [0.,1e-4,.01,.1,.5,.9,1.]:
   y=A.neutral_abundances();Yd=A.DEFAULT_INVENTORY['D'];y[ix['H1_I']]=1-h;y[ix['H1_II']]=h;y[ix['D_I']]=Yd*(1-d);y[ix['D_II']]=Yd*d
   z=n.rhs(T,1e-5,y);scale=sum(abs(n.delta_binding_eV*z.event_per_H_s));rel=abs(z.energy_ledger_residual_eV_per_H_s)/scale
   rows.append({'T_K':T,'xH':h,'xD':d,'nH_cm3':1e-5,'heat':z.heat_eV_per_H_s,'binding_dot':z.binding_derivative_eV_per_H_s,'event_scale':scale,'relative_residual':rel})
out={'case_count':len(rows),'max_case':max(rows,key=lambda r:r['relative_residual']),'fail_count_at_2e13':int(sum(r['relative_residual']>2e-13 for r in rows)),'gate':2e-13,'scope':'floating arithmetic derivative identity; no ODE','rows':rows}
open('/tmp/hh_phys79_thermal/C9_ENERGY_CONDITIONING.json','w').write(json.dumps(out,indent=2)+'\n')
p='/tmp/hh_phys79_thermal/C9_REVIEW.json';r=json.load(open(p))
r['status']='CHANGES_REQUESTED_FINITE_GUARDS_AND_STABLE_ENERGY_DERIVATIVE'
r['findings'].append({'id':'C9-F2','severity':'medium','scope':'fixed energy acceptance gate','finding':'Computing delta energy via epsilon@dY cancels the ~13.6eV common H/D potential against the0.003705eV defect.85of252 physical D/H states exceed fixed2e-13 event-energy relative gate despite mathematically conservative stoichiometry.','evidence':{k:v for k,v in out.items() if k!='rows'},'minimum_fix':'Compute authoritative binding_derivative as math.fsum(delta_binding_eV[r]*event[r]); retain epsilon@dY as independent conditioning diagnostic using constituent energy scale. Keep the declared2e-13 energy gate.'})
json.dump(r,open(p,'w'),indent=2)
print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
