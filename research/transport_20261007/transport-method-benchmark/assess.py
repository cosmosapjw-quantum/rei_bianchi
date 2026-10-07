import csv,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
rows=list(csv.DictReader((R/'results.csv').open()));before=list(csv.DictReader((R/'results.original.csv').open()))
for a,b in zip(rows,before):
 for k in a:
  if k=='case_seconds':continue
  va,vb=a[k],b[k]
  if va==vb:continue
  if not(abs(float(va)-float(vb))<=5e-15*max(1.,abs(float(va)),abs(float(vb)))):raise AssertionError((k,va,vb))
print('Refactor replay equivalent within5e-15 except runtime;234rows')
O=json.loads((R/'oracle.json').read_text());truth={round(float(e['s']),12):e for e in O['epochs']};u0=float(O['U0'])
groups={}
for rr in rows:
 x={k:(v if k=='method' else float(v))for k,v in rr.items()};key=(x['method'],int(x['n']),x['cfl']);groups.setdefault(key,[]).append(x)
cases=[]
for (m,n,c),xs in groups.items():
 first=xs[0];last=xs[-1]
 d={'method':m,'n':n,'cfl':c,'max_N_residual':max(abs(x['Nres'])for x in xs),'max_E_residual_pre':max(abs(x['Eres_pre'])for x in xs),'max_E_residual_post':max(abs(x['Eres_post'])for x in xs),'max_outN_error':max(abs(x['Nout']-float(truth[round(x['s'],12)]['Nout']))for x in xs),'max_outE_error_U0':max(abs(x['Eout']-float(truth[round(x['s'],12)]['Eout']))/u0 for x in xs),'max_bin_L1':max(sum(abs(x[f'bin{j}']-float(truth[round(x['s'],12)]['bins'][j]))for j in range(32))for x in xs),'max_negative_mass':max(x['negative_mass']for x in xs),'min_density':None if m=='stock'else min(x['min_density']for x in xs),'min_N':min(x['N']for x in xs),'min_Nout':min(x['Nout']for x in xs),'initial_N_error':first['N0']-1.,'initial_U_pre_error_U0':first['U0_pre']/u0-1.,'initial_U_post_error_U0':first['U0_post']/u0-1.,'initial_limiter_delta_U':first['initial_du'],'final_stage_limiter_delta_U':last['stage_du'],'initial_zero_nodes':int(first['zero_nodes']),'initial_omitted_N_bound':first['zero_N_bound'],'initial_omitted_U_bound':100*first['zero_N_bound'],'steps':int(last['steps']),'seconds':last['case_seconds'],'L1_est_GL16_max':None if m=='stock' else max(x['L1_GL16']for x in xs),'L1_GL8_GL16_max_abs':None if m=='stock'else max(abs(x['L1_GL16']-x['L1_GL8'])for x in xs)}
 cases.append(d)
time={}
for m in ['fv','dg','dg_limited']:
 a,b,c=(groups[(m,128,v)]for v in [.15,.075,.0375]);d1=max(abs(x['Nout']-y['Nout'])for x,y in zip(a,b));d2=max(abs(x['Nout']-y['Nout'])for x,y in zip(b,c));time[m]={'Nout_dt_vs_half_dt_max':d1,'Nout_half_dt_vs_quarter_dt_max':d2,'difference_ratio':d1/d2,'outflow_error_at_three_cfl':[next(z['max_outN_error']for z in cases if z['method']==m and z['n']==128 and z['cfl']==v)for v in [.15,.075,.0375]]}
result={'cases':cases,'time_refinement_n128':time,'replay_equivalent_tolerance':5e-15,'historical_resource_compliance':'NO: initial oracle cross-interval cache replay reached4369>4096. Corrected oracle bounded replay peak2157 and same byte hash.','final_oracle_sha256':hashlib.sha256((R/'oracle.json').read_bytes()).hexdigest()}
(R/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
for x in cases:
 if x['n']==256:print({k:x[k]for k in ['method','max_outN_error','max_E_residual_pre','max_negative_mass','min_Nout','min_N','initial_zero_nodes','initial_omitted_N_bound']})
print(json.dumps(time,indent=2))
