#!/usr/bin/env python3
"""Independent table/trace consumer checks; no re-evolution or tolerance change."""
from pathlib import Path
import csv,json,struct,sys,numpy as np
roots=[Path(x) for x in sys.argv[1:3]];out=Path(sys.argv[3]);per={}
parents=[roots[0]/'results',roots[1]/'time_preflight_results',roots[1]/'grid_preflight_results']
fhe=.2454/(4*(1-.2454));kb=1.380649e-16
for parent in parents:
 for d in sorted(parent.iterdir()):
  if not d.is_dir():continue
  h=list(csv.DictReader((d/'history.csv').open()));l=list(csv.DictReader((d/'ledgers.csv').open()))
  ratios={}
  for row in l:
   assert np.isfinite(float(row['residual'])),(d.name,row)
   if row['status']=='VALUE':
    assert row['tolerance']=='',(d.name,row)
    continue  # Dimensional ledger quantity, not an acceptance residual.
   assert row['status']=='PASS',(d.name,row)
   ratio=abs(float(row['residual']))/float(row['tolerance']);assert ratio<=1,(d.name,row)
   ratios[row['ledger_name']]=max(ratios.get(row['ledger_name'],0),ratio)
  charge=max(abs(float(row['ne_proper_cm3'])/float(row['nH_proper_cm3'])-(float(row['x_HII'])+fhe*(float(row['x_HeII'])+2*float(row['x_HeIII'])))) for row in h)
  assert charge<=1e-12,(d.name,charge)
  b=(d/'raw/state_trace.bin').read_bytes();assert b[:8]==b'AX11TRC1'
  photons,nfloat,ncount,record_bytes,n,capacity=struct.unpack('<6Q',b[8:56]);assert n==len(h) and len(b)==56+n*record_bytes
  max_t=0.;max_a=0.
  for i,row in enumerate(h):
   state=struct.unpack_from('<32d',b,56+i*record_bytes)
   xe=state[1]+fhe*(state[2]+2*state[3]);t=2*state[4]/(3*kb*(1+fhe+xe))
   max_t=max(max_t,abs(t-float(row['temperature_K'])));max_a=max(max_a,abs(state[0]-float(row['a'])))
  assert max_t<=2e-8 and max_a==0,(d.name,max_t,max_a)
  per[d.name]={'history_rows':len(h),'trace_rows':n,'ledger_rows':len(l),'ledger_gate_rows':sum(x['status']=='PASS' for x in l),'dimensional_VALUE_rows':sum(x['status']=='VALUE' for x in l),'all_ledger_gate_rows_PASS':True,'ledger_max_abs_residual_over_original_tolerance':ratios,'charge_reconstruction_normalized_max':charge,'temperature_from_trace_w_max_abs_K':max_t,'trace_history_a_exact':True}
result={'status':'PASS_SCOPED_CONSUMER_VALIDATION','method':'same-author adversarial independent consumer; native source not re-executed; all27windows included including2failedstartupstates','windows':per,'not_a_global_evolution_error_bound':True,'original_DAG':'10/17','expansion_DAG':'28/88'}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'windows':len(per),'all_history_rows':sum(v['history_rows'] for v in per.values()),'max_charge':max(v['charge_reconstruction_normalized_max'] for v in per.values()),'max_T_reconstruction_K':max(v['temperature_from_trace_w_max_abs_K'] for v in per.values())}))
