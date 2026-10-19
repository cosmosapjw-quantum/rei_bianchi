from pathlib import Path
import csv,math,json,hashlib
out=Path('/workspace/scratch/6af5e9e6c737/v15_work/execution_coupled')
allrows=[];artifacts={}
for name in ['fixed_geometry.csv','birth_histories.csv']:
 rows=list(csv.DictReader((out/name).open()));allrows+=rows
 print(name,'rows',len(rows),'finals',sum(float(r['is_final'])==1 for r in rows))
 for suffix in ['', '.births.csv','.segments.csv','.cells.csv']:
  p=out/(name+suffix);artifacts[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
summary={'schema':'rei.v15.coupled.raw-summary.1','order_admission':'ROOT_REVIEW_PENDING','unique_histories':16,'prefix_repeat_histories':0,'accepted_step_rows':len(allrows),'artifacts':artifacts,'cases':{}}
for kind in ['fixed_geometry','physical_gl2','seeded_disabled_gl2']:
 rows=[r for r in allrows if r['kind']==kind];finals=[r for r in rows if float(r['is_final'])==1];case={'levels':[int(float(r['m'])) for r in finals],'audit_max_abs':{},'final_values':{},'signed_successive_differences':{},'successive_difference_exponents':{},'max_tau_stage1':max(float(r['max_tau_stage1']) for r in rows),'max_tau_stage2':max(float(r['max_tau_stage2']) for r in rows),'max_accepted_nonlinear_residual':max(float(r['solver_max_residual']) for r in rows),'max_abs_endpoint_log_drift':max(abs(float(r['actual_X_minus_target'])) for r in rows)}
 for key in rows[0]:
  if key.startswith('audit_')or key.startswith('owner_'):case['audit_max_abs'][key]=max(abs(float(r[key])) for r in rows)
 for key in ['final_HII','final_HeII','final_HeIII','final_w_eV_H','final_binding_eV_H','final_electrons_H','final_T_K','final_active_N','final_active_U','P_0','P_1','P_2','photo_binding','photo_heat','CE_0','RRDR_0','FF','escape','signed_CMB','gaswork','photonwork','source_N','source_U']:
  vals=[float(r[key]) for r in finals];ds=[vals[j]-vals[j+1] for j in range(len(vals)-1)];ps=[math.log(abs(ds[j]/ds[j+1]),2) if ds[j]and ds[j+1]else None for j in range(len(ds)-1)];case['final_values'][key]=vals;case['signed_successive_differences'][key]=ds;case['successive_difference_exponents'][key]=ps
 summary['cases'][kind]=case
 print('\n',kind,'maxaudit',case['audit_max_abs'],'max_tau',case['max_tau_stage1'],'max_residual',case['max_accepted_nonlinear_residual'],'drift',case['max_abs_endpoint_log_drift'])
 for key in ['final_HII','final_HeII','final_HeIII','final_w_eV_H','final_T_K','final_active_N','P_0','photo_heat']:print(key,case['successive_difference_exponents'][key])
(out/'RAW_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
