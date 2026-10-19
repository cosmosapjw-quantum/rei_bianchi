"""Compare the retained native split operations with the SAME birth packet oracle."""
from pathlib import Path
import json,csv,math,hashlib
R=Path(__file__).resolve().parents[1];E=R/'evidence'
s=json.loads((E/'NUMERICAL_SUMMARY.json').read_text())
ref=s['reference']['endpoint']
raw=list(csv.DictReader((E/'NATIVE_FIXED_PACKET.csv').open()))
cols={'T_k':'T_K','x_hii':'x_HII','x_dii':'x_DII','survivor_com3':'survivor_com3','HI_com3':'HI_com3','HeI_com3':'HeI_com3','HeII_com3':'HeII_com3','DI_com3':'DI_com3'}
rows=[]
for r in raw:
 o={'steps':int(r['steps'])}
 for source,k in cols.items():
  value=float(r[source]);o[k]=value;o['delta_'+k]=value-ref[k];o['relative_'+k]=(value-ref[k])/abs(ref[k])
 rows.append(o)
with (E/'NATIVE_FIXED_ERRORS.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ident=json.loads((E/'NATIVE_FIXED_EXECUTION.json').read_text())
reference_bytes=(E/'JOINT_PACKET.bits').read_bytes()
files=sorted(E.glob('NATIVE_PACKET_*.bits'))
assert len(files)==5
for f in files:assert f.read_bytes()==reference_bytes,f
s['native_fixed_packet']={'scope':'same native drift/photo/gas operators as RUN05; only emit_births replaced by interval subset of one immutable native bundle','source_tuple_identity':ident,'physical_tuples':15360,'n_cases':len(rows),'errors':rows,'ledger_maxima':{k:max(abs(float(r[k])) for r in raw)for k in ['photon_res','baryon_res','energy_step_res']},'wall_s':sum(r['wall_s'] for r in ident['runs'])}
s['completed_joint_and_controlled_cases']=len(s['cases'])
s['completed_total_cases']=len(s['cases'])+len(rows)
s['all_completed_integration_wall_s']=s['completed_native_solver_wall_sum_s']+s['native_fixed_packet']['wall_s']
import re
s['native_test_count']=sum(map(int,re.findall(r'test result: ok\. (\d+) passed',(E/'TESTS_FINAL_COMPLETE.log').read_text())))
(E/'NUMERICAL_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps({'tests':s['native_test_count'],'cases':s['completed_total_cases'],'wall_s':s['all_completed_integration_wall_s'],'native_comparison':[{k:r[k]for k in ['steps','delta_T_K','relative_survivor_com3','delta_x_DII']}for r in rows]},indent=2))
