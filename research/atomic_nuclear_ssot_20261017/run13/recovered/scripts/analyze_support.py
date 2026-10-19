"""Read actual endpoints; never treat an interrupted support as completed."""
from pathlib import Path
import json,csv,math,re
from scipy.optimize import brentq
R=Path(__file__).resolve().parents[1];E=R/'evidence'
KEYS=['T_K','survivor_com3','x_HII','x_DII','x_HeII','x_HeIII','HI_com3','HeI_com3','HeII_com3','DI_com3','thermal_J_m3','photon_energy_J_com3','gas_work_J_com3','photon_work_J_com3','born_com3']
def read(n,rep='paired',tol='3e-11'):return json.loads((E/f'r{n}_{rep}_DOP853_{tol}/result.json').read_text())
def writecsv(path,rows):
 with path.open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def analyze():
 cases=[json.loads(p.read_text()) for p in sorted(E.glob('r*/result.json'))]
 series=[read(n) for n in [1,2,4,6]];rows=[]
 for d in cases:
  rows.append({k:d[k] for k in ['subdivisions','representation','method','rtol','dimension','physical_cohorts','birth_times','wall_s','threshold_roots']}|d['observable'])
 writecsv(E/'SUPPORT_COMPARISON.csv',rows)
 diffs=[]
 for a,b in zip(series[:-1],series[1:]):
  for k in KEYS:
   u,v=a['observable'][k],b['observable'][k]
   diffs.append({'coarse_r':a['subdivisions'],'fine_r':b['subdivisions'],'observable':k,'fine_value':v,'signed_difference_fine_minus_coarse':v-u,'relative_difference_fine_denominator':(v-u)/v if v else None})
 writecsv(E/'SUPPORT_DIFFERENCES.csv',diffs)
 controls=[]
 for n in [4,6]:
  a=read(n)['observable'];b=read(n,tol='3e-12')['observable']
  signal={k:read(6,tol='3e-12')['observable'][k]-read(4,tol='3e-12')['observable'][k] for k in KEYS}
  for k in KEYS:
   controls.append({'r':n,'observable':k,'tight_minus_standard':b[k]-a[k],'relative_tight_denominator':(b[k]-a[k])/b[k] if b[k] else None,'relative_to_abs_r4_to_r6_signal':abs((b[k]-a[k])/signal[k]) if signal[k] else None})
 writecsv(E/'SOLVER_TOLERANCE_CONTROLS.csv',controls)
 orders=[]
 for k in KEYS:
  y=[d['observable'][k] for d in series];d12=y[1]-y[0];d24=y[2]-y[1];d46=y[3]-y[2]
  p124=math.log(abs(d12/d24),2) if d12*d24>0 else None;p246=None
  if d24*d46>0:
   try:p246=brentq(lambda p:(2**(-p)-4**(-p))/(4**(-p)-6**(-p))-d24/d46,.05,15)
   except ValueError:pass
  orders.append({'observable':k,'p_1_2_4':p124,'fitted_p_2_4_6':p246,'scope':'three-point diagnostic, not a continuum error bound'})
 writecsv(E/'OBSERVED_SUPPORT_ORDERS.csv',orders)
 obs=[d['observable']for d in cases]
 ledger={k:max(d[k]for d in obs)for k in ['photon_ledger_rel','energy_ledger_rel_initial','energy_ledger_rel_source','species_event_rel_H','species_event_D_fraction']}
 base=read(1)['observable'];fine=read(6,tol='3e-12')['observable']
 summary={'schema':'rei.atomic.nuclear.run09.summary.v1','completed_joint_cases':len(cases),'completed_supports':[1,2,4,6],'birth_times':[40,80,160,240],'physical_cohorts':[15360,30720,61440,92160],'excluded_r8':'outer45s interruption without endpoint,not admitted,no blind retry','next_source_axis':'spectral-edge refinement;birth support4 is a bounded working choice, not an absolute error certificate','diagnostic_finest_reference':{'label':'r6_paired_DOP853_3e-12','not_continuum_reference':True,'observable':fine},'r1_to_r6_relative':{k:(fine[k]-base[k])/fine[k] for k in KEYS},'tight_r4_to_r6_relative':{k:(fine[k]-read(4,tol='3e-12')['observable'][k])/fine[k] for k in KEYS},'solver_controls':controls,'support_order_diagnostics':orders,'ledger_maxima':ledger,'completed_solver_wall_sum_s':sum(d['wall_s']for d in cases),'native_tests':sum(map(int,re.findall(r'test result: ok\. (\d+) passed;', (E/'TESTS_ALL.log').read_text()))),'new_python_tests':7,'retained_python_tests':8,'same_source_moments':json.loads((E/'SOURCE_MOMENTS.json').read_text()),'manufactured_nonlinear_witness':json.loads((E/'NONLINEAR_SOURCE_WITNESS.json').read_text()),'independence':'same original atomic/gas/retarded RHS; RUN08 Radau validation retained; new run has DOP853 tolerance and exact-reflection/full controls,not fresh Radau or independent actor'}
 (E/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:summary[k]for k in ['completed_joint_cases','completed_supports','completed_solver_wall_sum_s','native_tests','ledger_maxima','tight_r4_to_r6_relative']},indent=2));return summary
if __name__=='__main__':analyze()
