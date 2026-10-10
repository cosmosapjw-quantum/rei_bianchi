from pathlib import Path
import json,sys,hashlib
import mpmath as mp
r=Path.cwd();d=r/'.cuh/fastest-track/REI-F04';o=d/'FT03_original';sys.path.insert(0,str(o/'research'));import mp_reference as ref
mp.mp.dps=80;m=mp.mpf;rows=[]
for T0 in [30000,32000,40000,50000,75000,90000,100000,110000]:
 T=m(T0);alpha=[ref.ar(T,a) for a in range(3)];slopes=[T*mp.diff(lambda x:ref.ar(x,a),T)/alpha[a] for a in range(3)];gps=[T*mp.diff(lambda x:x*mp.diff(lambda t:ref.ar(t,a),x)/ref.ar(x,a),T) for a in range(3)];gps[1]=mp.mpf('0');kin=[ref.KB*T*alpha[a]*(m('1.5')+slopes[a]) for a in range(3)];ci=[]
 for a,(A,p,c,q,h) in enumerate(zip(['21.11','32.38','19.95'],['-1.089','-1.146','-1.089'],['.354','.416','.553'],['.874','.987','.735'],['1.101','1.056','1.275'])):
  l=ref.L[a]/T;ci.append(m(A)*T**m('-1.5')*mp.exp(-l/2)*l**m(p)/(1+(l/m(c))**m(q))**m(h))
 b1=m('40.49664394833662')*11605;b2=m('8.099328789667')*11605;da=m('1.54e-9')*(T/11605)**m('-1.5')*mp.exp(-b1/T);db=da*m('.3')*mp.exp(-b2/T)
 rows.append({'T_K':T0,'alpha_rr':list(map(str,alpha)),'log_slope':list(map(str,slopes)),'log_slope_derivative':list(map(str,gps)),'rr_kinetic_coeff':list(map(str,kin)),'ci_beta':list(map(str,ci)),'dr_alpha':list(map(str,[da,db])),'dr_kinetic_energy_erg':list(map(str,[ref.KB*b1,ref.KB*(b1+b2)]))})
sigma=[[str(ref.photo_sigma(row,E)) for E in ref.EG] for row in ref.rows]
archive=json.loads((o/'results/float_reference.json').read_text());dd=archive['DOP853'];endpoint={'observables':dd['endpoint'][:3]+[float(mp.log(m(str(dd['final_T_K']))))],'T_K':dd['final_T_K'],'photons_cm3':[z*1e-4 for z in dd['endpoint'][3:6]],'u_erg_cm3':dd['endpoint'][6]*1e-4*1.602176634e-12,'escaped_erg_cm3':dd['endpoint'][7]*1e-4*1.602176634e-12}
out={'model_id':'REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1','archive_sha256':json.loads((d/'intake.json').read_text())['archive_sha256'],'working_digits':80,'comparison_relative_tolerance':3e-12,'point_references_not_uniform_enclosures':True,'coefficient_rows':rows,'sigma_cm2':sigma,'archived_endpoint_reused':endpoint,'derivative_reference':'mpmath.diff of archived alpha expression, not Rust analytic slope','original_reference_receipts_reused_not_reexecuted':True};(d/'oracle.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'coefficient_rows':len(rows),'values':len(rows)*19,'sigma_values':9,'endpoint':endpoint},indent=2))
