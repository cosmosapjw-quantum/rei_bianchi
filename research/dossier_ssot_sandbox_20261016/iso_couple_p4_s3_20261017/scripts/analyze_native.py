from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[1]
def read(name):
 with (R/'evidence'/name).open() as f:return {(row['case'],int(row['nsteps']),row['mode']):{k:(v if k in ('mode','case') else float(v)) for k,v in row.items()} for row in csv.DictReader(f)}
c=read('native_retarded_campaign.csv'); c.update(read('native_retarded_refinement.csv'));c.update(read('native_matched_error_axes.csv'))
assert len(c)==41, len(c)
ledger_max=max(x['number_residual'] for x in c.values())
energy_max=max(x['energy_residual'] for x in c.values())
work_max=max(x['work_discrepancy_relative'] for x in c.values() if x['mode']!='p4s2_phi')
assert ledger_max<8e-15,(ledger_max,'observed roundoff')
assert energy_max<3e-10
out={'n_complete_unique_rows':len(c),'ledger_max_relative':ledger_max,'energy_max_relative':energy_max,'photon_work_discrepancy_max_rel_to_emitted_energy':work_max,
'comparison':{},'incomplete_or_timeout':{'flrw_N64_split_gl4_m8':'TIMEOUT_NOT_ADMITTED'}}
for n in [8,16,32]:
 base=c['flrw',n,'age_gl4_m8'];split=c['flrw',n,'split_gl4_m8'];
 for kind in ['DI_events_com3','HI_events_com3','HeI_events_com3','survivors_com_m3','T_final_K']:
  out['comparison'][f'FLRW_N{n}_{kind}_spectral_split_relative']=split[kind]/base[kind]-1
 other=c['flrw',n,'age_gl4_m4'];out['comparison'][f'FLRW_N{n}_DI_opacity_m4_m8_relative']=base['DI_events_com3']/other['DI_events_com3']-1
 other2=c['flrw',n,'p4s2_phi'];out['comparison'][f'FLRW_N{n}_survivors_age_vs_P4S2_relative']=base['survivors_com_m3']/other2['survivors_com_m3']-1
print('complete rows',len(c),'max photon',ledger_max,'max energy',energy_max,'geom work',work_max)
for k in sorted(out['comparison']):
 if 'N16' in k:print(k,out['comparison'][k])
for mode in ['p4s2_phi','age_gl4_m4','age_gl4_m8','split_gl4_m4','split_gl4_m8']:
 Ns=[4,8,16,32,64]
 vals=[]
 for N in Ns:
  x=c.get(('flrw',N,mode))
  if x:vals.append((N,x['survivors_com_m3']))
 ps=[]
 for (a,A),(b,B),(d,D) in zip(vals,vals[1:],vals[2:]):
  if b==2*a and d==2*b and (A-B)*(B-D)>0:ps.append({'steps':(a,b,d),'observed_p':math.log(abs((A-B)/(B-D)),2)})
 out.setdefault('observed_order',{})[mode]=ps
print('orders',out['observed_order'])
(R/'evidence/NATIVE_SCIENCE_ANALYSIS.json').write_text(json.dumps(out,indent=2)+'\n')
