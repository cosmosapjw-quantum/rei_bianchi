from pathlib import Path
from decimal import Decimal,localcontext
import json,struct,math
W=Path(__file__).resolve().parent
D=Decimal.from_float

def decode(b): return {k:struct.unpack('>d',bytes.fromhex(v))[0] for k,v in b.items()}
def analyze(record):
 f=decode(record['bits']);d={k:D(v) for k,v in f.items()}
 with localcontext() as ctx:
  ctx.prec=90
  dt=d['dt']; vol=dt/d['nh']; r=d['nhe']/d['nh']; ev=d['ev'];c=[d['chi'+str(i)] for i in range(3)]
  df=[d['new_'+k]-d['old_'+k] for k in ['x','y','z']]
  dr=[df[i]-dt*d['rhs_'+k] for i,k in enumerate(['x','y','z'])]
  ew=d['new_w']-d['old_w']-dt*d['rhs_w']
  eb=ev*(c[0]*dr[0]+r*(c[1]*dr[1]+(c[1]+c[2])*dr[2]))
  binding=ev*(c[0]*df[0]+r*(c[1]*df[1]+(c[1]+c[2])*df[2]))
  rhs_balance=dt*d['rhs_w']+ev*dt*(c[0]*d['rhs_x']+r*(c[1]*d['rhs_y']+(c[1]+c[2])*d['rhs_z']))-dt*d['owner_absorbed']+vol*(d['escape']-d['cmb']+d['work'])
  defect=d['new_w']-d['old_w']+binding-dt*d['owner_absorbed']+vol*(d['escape']-d['cmb']+d['work'])
  assert abs(defect-(ew+eb+rhs_balance))<Decimal('1e-100')
  root_pre=(d['old_x']+d['a0'])/(1+d['a0']+d['r0'])
  af=dt*(d['gamma0']+d['final_ne']*d['ci0']);rf=dt*d['final_ne']*d['rr0']
  root_final=(d['old_x']+af)/(1+af+rf)
  computed=f['new_x']; nearest=float(root_pre)
  stable=f['old_x']+(f['a0']-(f['a0']+f['r0'])*f['old_x'])/(1.0+f['a0']+f['r0'])
  replaced=defect+ev*c[0]*(D(stable)-d['new_x'])
  result=dict(record_id=record.get('trial'),exact_defect=defect,binary_evaluated_defect=d['defect'],budget=d['budget'],energy_equation_residual=ew,binding_equation_residual=eb,rhs_identity_residual=rhs_balance,ledger_evaluation_roundoff=d['defect']-defect,fraction_equation_residuals=dr,energy_ulp=D(math.ulp(f['new_w'])),hydrogen_ulp=D(math.ulp(computed)),budget_over_energy_ulp=d['budget']/D(math.ulp(f['new_w'])),binding_one_hydrogen_ulp=ev*c[0]*D(math.ulp(computed)),old_x=d['old_x'],new_x=d['new_x'],ideal_preupdate_h_root=root_pre,ideal_final_h_root=root_final,nonlinear_h_root_shift=root_final-root_pre,stored_h_minus_ideal_pre= d['new_x']-root_pre,nearest_h_minus_ideal_pre=D(nearest)-root_pre,stable_h_minus_ideal_pre=D(stable)-root_pre,stored_h_ulp_distance_to_nearest=(d['new_x']-D(nearest))/D(math.ulp(computed)),stable_formula_h=stable,stable_formula_same_as_nearest=stable==nearest,diagnostic_replaced_h_defect_frozen_rhs=replaced,diagnostic_replaced_h_ratio=abs(replaced)/d['budget'],thermal_neighbor_equation_residuals={k:d[k+'_w']-d['old_w']-dt*d[k+'_rhs_w'] for k in ['below','above']})
  return result

def enc(obj):
 if isinstance(obj,Decimal):return str(obj)
 raise TypeError
records=json.loads((W/'diagnostic-records.json').read_text());results=[];trial=None
for r in records:
 if r['kind']=='trial':trial=r
 elif r['kind']=='inner_energy':r['trial']=trial;results.append(analyze(r))
(W/'exact-local-analysis.json').write_text(json.dumps(results,indent=2,default=enc)+'\n')
for r in results:
 if r['record_id']['number'] in [16,34]: print(json.dumps(r,indent=2,default=enc))
