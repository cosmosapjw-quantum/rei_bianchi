from pathlib import Path
import json,csv,math,re,hashlib
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'evidence'
reference=json.loads((E/'full_DOP853_3e-12_joint_n1/result.json').read_text());ref=reference['observable'];rows=[];catalog=[]
keys=['T_K','x_HII','x_DII','x_HeII','x_HeIII','survivor_com3','HI_com3','HeI_com3','HeII_com3','DI_com3','thermal_J_m3','photon_energy_J_com3']
for f in sorted(E.glob('*/result.json')):
 r=json.loads(f.read_text());label=f.parent.name
 if 'PRE_L2' in label:continue
 o=r['observable'];q={k:r.get(k)for k in ['method','representation','split','n','rtol','cohorts','dimension','wall_s','rhs_calls']};q['label']=label
 q.update(o)
 for k in keys:q['delta_'+k]=o[k]-ref[k];q['relative_'+k]=(o[k]-ref[k])/abs(ref[k])
 rows.append(q);catalog.append({'label':label,'file':str(f.relative_to(ROOT))})
fields=list(rows[0]);
with (E/'RETARDED_COMPARISON.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
rad=next(q for q in rows if q['method']=='Radau');dop=next(q for q in rows if q['label']=='paired_DOP853_3e-10_joint_n1')
orders=[];splitrows=sorted((q for q in rows if q['split']=='frozen_lie'),key=lambda x:x['n'])
for a,b in zip(splitrows[:-1],splitrows[1:]):
 row={'n0':a['n'],'n1':b['n']}
 for k in keys:
  e0=abs(a['delta_'+k]);e1=abs(b['delta_'+k]);row[k]=math.log(e0/e1)/math.log(b['n']/a['n'])if e0 and e1 else None
 orders.append(row)
summary={'schema':'rei.run08.results.v1','reference':{'label':'full_DOP853_3e-12_joint_n1','scope':'same finite native source packet, not continuous-source error certificate','endpoint':ref},'completed_cases':len(rows),'cases':catalog,'radau_vs_full_tight':{k:{'absolute':rad['delta_'+k],'relative':rad['relative_'+k]}for k in keys},'radau_vs_paired_dop':{k:rad[k]-dop[k]for k in keys},'frozen_lie_errors':[{'n':r['n'],**{k:r['delta_'+k]for k in keys}}for r in splitrows],'orders_nonuniform_birth_aligned':orders,'ledger_maxima':{k:max(q[k]for q in rows)for k in ['photon_ledger_rel','energy_ledger_rel_initial','energy_ledger_rel_source','species_event_rel_H','species_event_D_fraction']},'completed_native_solver_wall_sum_s':sum(q['wall_s']for q in rows),'excluded':'full Radau timeout without endpoint; initial PRE_L2 diagnostic retained separately','native_parity':json.loads((E/'NATIVE_PYTHON_PARITY.json').read_text()),'native_test_count':sum(map(int,re.findall(r'test result: ok\. (\d+) passed',(E/'TESTS_FINAL.log').read_text()))),'source_packet':{'bytes':(ROOT/'inputs/FINITE_BIRTH_PACKET.json').stat().st_size,'sha256':hashlib.sha256((ROOT/'inputs/FINITE_BIRTH_PACKET.json').read_bytes()).hexdigest(),'physical_cohorts':15360,'exact_reflection_groups':7680,'births':40,'energy_cells':48,'angle_nodes':8,'native_scope_threshold_crossings':0},'new_python_tests':8}
(E/'NUMERICAL_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items()if k not in ('native_parity','cases','reference')},indent=2))
