import csv,hashlib,json,math,struct
from pathlib import Path
root=Path(__file__).resolve().parent.parent;base=root.parent;c=json.loads((root/'CONTRACT.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def rows(out,name):
 with (out/(name+'.csv')).open(newline='') as f:data=list(csv.reader(f))
 schema=c['compiled_endpoint_csv_schemas'][name];require(all(len(row)==len(schema) for row in data),'HEADERLESS_SCHEMA_ROW_WIDTH '+name)
 return [dict(zip(schema,row)) for row in data]
def read(case,out,h,steps):
 history=rows(out,'history');abundances=rows(out,'abundances');ledgers=rows(out,'ledgers');require(len(history)==1 and len(abundances)==6,'ENDPOINT_ROWS_NOT_DROPPED');hr=history[0];require(hr['case_id']==case,'HISTORY_CASE')
 species={r['species_id']:r for r in abundances};require(set(species)=={'H_I','H_II','He_I','He_II','He_III','electron'},'SIX_SPECIES');require(all(r['run_id']==case and float(r['time_s'])==float(hr['time_s']) and float(r['Tgas_K'])==float(hr['temperature_K']) for r in abundances),'EXACT_ENDPOINT_ALIGNMENT')
 values={'temperature_K':float(hr['temperature_K']),'time_s':float(hr['time_s']),'b':float(hr['b']),'H_per_s':float(hr['H_per_s']),'signed_s_over_H':float(hr['Sigma']),'photon_N_per_H':float(hr['photon_n_per_H']),'photon_U_eV_per_H':float(hr['photon_u_eV_per_H'])}
 for sp,row in species.items():
  values['Y_'+sp]=float(row['Ybaryon'])
  if sp!='electron':values['fraction_'+sp]=float(row['element_fraction'])
 for row in ledgers:
  require(row['case_id']==case and float(row['time_s'])==float(hr['time_s']),'LEDGER_ENDPOINT_ALIGNMENT')
  value=float(row['residual']);require(math.isfinite(value),'FINITE_LEDGER')
  if row['status']=='PASS':require(abs(value)<=float(row['tolerance']),'LEDGER_OUTSIDE_NATIVE_RECORDED_TOLERANCE')
  else:require(row['status']=='VALUE','LEDGER_FAILURE_OR_UNKNOWN_STATUS')
  values[('ledger_residual_' if row['status']=='PASS' else 'ledger_')+row['ledger_name']]=value
 for name in ['absorbed_U_eV_per_H','escaped_N_per_H']:
  if 'ledger_'+name not in values:values['ledger_'+name]=None
 a=float(hr['a']);endpoint={'a':a,'a_raw_text':hr['a'],'a_binary64_hex':struct.pack('>d',a).hex(),'ln_a_over_a_ref':math.log(a/(1/21)),'zbar':float(hr['zbar']),'time_s':float(hr['time_s']),'requested_h':h,'requested_steps':steps,'nominal_h_times_steps':float(h)*steps,'nominal_decimal_interval':'0.0004'}
 return {'case':case,'directory':str(out),'endpoint':endpoint,'values':values,'missing_fields':{k:'NOT_RECORDED_IN_CURRENT_NATIVE_ENDPOINT_SCHEMA' for k,v in values.items() if v is None},'headerless_rows_retained':{'history':len(history),'abundances':len(abundances),'ledgers':len(ledgers)},'files':[{'path':str(out/name),'sha256':sha(out/name)} for name in ['history.csv','abundances.csv','ledgers.csv','result.json','source_time_check.txt','owner_rates.json','step_trace.csv','checkpoint.bass-v1']]}
all_points={};comparison=[];endpoint_reports={}
for case in ['COLD_FLRW','SIGNED_MINUS']:
 points=[read(case,base/'component_001/results'/case,'0.0001',4),read(case,root/'results'/(case+'_h2'),'0.00005',8),read(case,root/'results'/(case+'_h4'),'0.000025',16)];all_points[case]=points
 endpoints=[p['endpoint'] for p in points];same12=endpoints[0]['a_binary64_hex']==endpoints[1]['a_binary64_hex'];same24=endpoints[1]['a_binary64_hex']==endpoints[2]['a_binary64_hex'];scope='SAME_ACTUAL_ENDPOINT_BITS' if same12 and same24 else 'SAME_NOMINAL_INTERVAL_ACTUAL_ENDPOINT_DIFFERENCES'
 endpoint_reports[case]={'classification':scope,'same_endpoint_bits_h_h2':same12,'same_endpoint_bits_h2_h4':same24,'endpoints':endpoints,'signed_actual_endpoint_differences':{k:{'h_minus_h2':endpoints[0][k]-endpoints[1][k],'h2_minus_h4':endpoints[1][k]-endpoints[2][k]} for k in ['a','ln_a_over_a_ref','zbar','time_s']},'same_endpoint_convergence_claim':False,'alignment_operation':'NONE; raw final states retained'}
 keys=sorted(set().union(*(p['values'] for p in points)))
 for key in keys:
  vals=[p['values'].get(key) for p in points];row={'case':case,'observable':key,'h':vals[0],'h2':vals[1],'h4':vals[2],'endpoint_classification':scope,'delta_definition':'h-h2 and h2-h4','signed_delta_h_h2':None,'signed_delta_h2_h4':None,'abs_delta_h_h2':None,'abs_delta_h2_h4':None,'R':None,'p_log2_R':None,'ratio_null_reason':None,'p_null_reason':None,'sign_flip':None,'exact_zero_delta1':None,'exact_zero_delta2':None,'trend':None}
  if any(v is None for v in vals):row.update(ratio_null_reason='NOT_RECORDED',p_null_reason='NOT_RECORDED',trend='NOT_RECORDED')
  elif not all(math.isfinite(v) for v in vals):row.update(ratio_null_reason='NONFINITE_INPUT',p_null_reason='NONFINITE_INPUT',trend='NOT_EVALUABLE')
  else:
   d1=vals[0]-vals[1];d2=vals[1]-vals[2];a1=abs(d1);a2=abs(d2);row.update(signed_delta_h_h2=d1,signed_delta_h2_h4=d2,abs_delta_h_h2=a1,abs_delta_h2_h4=a2,sign_flip=(d1>0 and d2<0) or (d1<0 and d2>0),exact_zero_delta1=d1==0,exact_zero_delta2=d2==0,trend='DECREASE' if a2<a1 else 'INCREASE' if a2>a1 else 'STAGNATION')
   if not math.isfinite(d1) or not math.isfinite(d2):row.update(ratio_null_reason='NONFINITE_DELTA',p_null_reason='NONFINITE_DELTA')
   elif a2==0:row.update(ratio_null_reason='ZERO_SECOND_DELTA',p_null_reason='ZERO_SECOND_DELTA')
   else:
    ratio=a1/a2
    if not math.isfinite(ratio):row.update(ratio_null_reason='NONFINITE_RATIO',p_null_reason='NONFINITE_RATIO')
    else:
     row['R']=ratio
     if ratio>0:row['p_log2_R']=math.log2(ratio)
     else:row['p_null_reason']='ZERO_RATIO_LOG_UNDEFINED'
  comparison.append(row)
write(root/'ENDPOINTS.json',endpoint_reports);write(root/'RAW_ENDPOINT_VALUES.json',all_points);write(root/'COMPARISON.json',{'status':'FIXED_STEP_SENSITIVITY_DIAGNOSTIC_ONLY','comparison_rows':comparison,'no_order_acceptance_threshold':True,'no_interpolation_or_endpoint_projection':True,'full_convergence':'HOLD'})
with (root/'comparison.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
print(json.dumps({'endpoint_classifications':{k:v['classification'] for k,v in endpoint_reports.items()},'comparison_rows':len(comparison),'missing_observables':[r['observable'] for r in comparison if r['trend']=='NOT_RECORDED'],'selected_thermal_rows':[r for r in comparison if r['observable']=='temperature_K']}))
