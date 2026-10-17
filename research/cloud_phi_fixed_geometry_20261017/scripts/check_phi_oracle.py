import csv,json,pathlib,mpmath as mp,math
root=pathlib.Path(__file__).resolve().parents[1];mp.mp.dps=450
rows=list(csv.DictReader((root/'evidence/final_phi_probe.stdout').open())); worst={};normal_worst={};fail=[]
for row in rows:
 t,n,b=[mp.mpf(float(row[k])) for k in ['tau','old','births']]
 phi=-mp.expm1(-t)/t if t else mp.mpf(1); missing=1-phi
 ref={'surviving':n*mp.exp(-t)+b*phi,'absorbed':n*(-mp.expm1(-t))+b*missing}
 for k,v in ref.items():
  got=mp.mpf(float(row[k]));err=abs(got-v);rel=err/abs(v) if v else mp.mpf(0)
  if k not in worst or rel>mp.mpf(worst[k]['relative_error']):worst[k]={'relative_error':str(rel),'tau':row['tau'],'old':row['old'],'births':row['births']}
  if abs(v)>=mp.mpf(float.fromhex('0x1.0p-1022')) and (k not in normal_worst or rel>mp.mpf(normal_worst[k]['relative_error'])):normal_worst[k]={'relative_error':str(rel),'tau':row['tau'],'old':row['old'],'births':row['births']}
  if err>mp.mpf('5e-13')*abs(v)+mp.mpf(float.fromhex('0x0.0000000000001p-1022'))*4:fail.append([row,k,str(err),str(v)])
result={'rows':len(rows),'precision_decimal_digits':450,'criterion':'abs_error <= 5e-13*abs(reference)+4*smallest_subnormal_f64','worst_relative':worst,'worst_normal_reference_relative':normal_worst,'failures':fail,'status':'PASS_SCOPED' if not fail else 'FAIL','scope':'scalar constant-opacity constant-source partition only, not full chemistry error'}
(root/'evidence/ORACLE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not fail
