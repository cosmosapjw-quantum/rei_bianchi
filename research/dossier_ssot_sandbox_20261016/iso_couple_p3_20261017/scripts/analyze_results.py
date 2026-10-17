#!/usr/bin/env python3
"""Independent CSV acceptance math, not an original production science gate."""
import csv,json,math,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((P/'evidence'/name).open()))
all=read('p3_positive_campaign_matched.csv');assert len(all)==32
cases=('flrw','bi_plus','bi_minus','bi_fesc025'); ns=(8,16,32,64)
d={(v['case'],int(v['nsteps']),v['representation']):v for v in all}
assert len(d)==len(cases)*len(ns)*2
columns={'HI':'HI_photo_m3','HeI':'HeI_photo_m3','HeII':'HeII_photo_m3','DI':'D_photo_m3','surviving_photons':'photons_com_m3'}
rows=[]; max_photon_ledger=0.;max_energy=0.
for case in cases:
 for n in ns:
  a=d[(case,n,'positive_384')];b=d[(case,n,'projected_64')]
  y={'case':case,'steps':n,'photo_compression_relative':{}}
  for tag,key in columns.items():
   f,g=float(a[key]),float(b[key]);y['photo_compression_relative'][tag]=abs(g-f)/f if f else None
  y['temperature_delta_K']=float(b['T_final_K'])-float(a['T_final_K'])
  for item in [a,b]:
   emitted=float(item['emitted_com_m3']);absorbed=float(item['absorbed_com_m3']);surv=float(item['photons_com_m3']);
   max_photon_ledger=max(max_photon_ledger,abs(emitted-absorbed-surv)/max(emitted,1e-50))
   max_energy=max(max_energy,float(item['max_step_energy_error']))
  rows.append(y)
log_src=read('p3_geometric_age.csv');assert len(log_src)==21
metrics={}
for case in ('flrw','shear_plus','shear_minus'):
  c=[x for x in log_src if x['geometry']==case and int(x['n_age'])==128 and int(x['n_mu'])==8];assert len(c)==1
  metrics[case]={'q2_energy':float(c[0]['q2_energy']),'photons_birth_com_m3':float(c[0]['photons_birth_com_m3']),'emission_spectrum_normalization':float(c[0]['source_norm_relative']),'tail_fraction':float(c[0]['tail_trunc_fraction'])}
grey=read('p3_campaign.csv');assert len(grey)==20
src=open(P/'evidence/p3_positive_campaign_timeout_39_rows.csv').readlines(); assert len(src)==40
flrw64=[r for r in rows if r['case']=='flrw' and r['steps']==64][0]
pass_contract={
 'schema':'rei.iso.p3.evidence.20261017.v2','node':'ISO-COUPLE-P3','status':'PASS_SCOPED_384_OWNER_CELLS_PLUS_P2_THERMOCHEMISTRY','production_full_EOR':'HOLD',
 'scalar_photo_comparison':[{'case':r['case'],'nsteps':r['steps'],'relative_grey_minus_positive':r['photo_compression_relative'],'delta_T_K':r['temperature_delta_K']} for r in rows],
 'max_photon_number_ledger_relative':max_photon_ledger,'max_single_step_energy_relative':max_energy,
 'source_only_bianchi_P2':metrics,
 'main_spectrum':{'id':'MD14_Z002_FESC_BB50K_13P6_100_V1','energy_source_bins':48,'angular_bins':8,'owner_cell_count':384,'P2_projected_bins':64,'frozen_source_continuum_accuracy':'NOT_ESTABLISHED'},
 'flrw64':flrw64,
 'claim_limits':{'age_ladder':'only 8,16,32,64 intervals in matched finished campaign','source_extrapolation':'MD14 high-z continuation and BB50k model choice','gas_time_order':'fixed midpoint source/opacity + first-order split','observational':'no CMB total tau; no calibration','anisotropic_background':'prescribed off-shell constant H and s; no Einstein closure','native_subagents':'NOT_RUN','age_refinement':'positive 64 vs32 still changes; no source-age convergence admission','HeI_native_target_0p5pct':'NOT_TRANSFERABLE_to_this_short_conditional_model','source_tail_above_100_eV':'TRUNCATED'},
 'data_shape':{'matched_photo_campaign_rows':len(all),'previous_grey_rows':len(grey),'prescribed_killing_rows':len(log_src),'timeout_partial_rows':len(src)-1},
 'defect_ledger':[{'stage':'compressed P3 first event 3grp','observed':'2.39% total photo mismatch','resolved_by':'use 384 source owner cell positive comparator; retain 64-bin as controlled approximation'}, {'stage':'positive unit test first read','observed':'comparison used old gas density rather than midpoint proper density','resolved_by':'compare same geometry and same gas EOS snapshot'}, {'stage':'nonexhaustive Nx128 run','observed':'time budget expired after 39 rows; N128 last comparison missing','resolved_by':'bounded published Nx8..64 complete 32-row matrix; retain partial log'}]
}
assert max_photon_ledger < 4e-11,max_photon_ledger
assert max_energy<3e-10,max_energy
assert abs(metrics['flrw']['q2_energy'])<1e-11
assert metrics['shear_plus']['q2_energy']<0<metrics['shear_minus']['q2_energy']
assert flrw64['photo_compression_relative']['surviving_photons']>0.01
assert flrw64['photo_compression_relative']['HeI']<0.005
out=P/'contracts/P3_RESULTS.json';out.write_text(json.dumps(pass_contract,ensure_ascii=False,indent=2)+'\n')
print('SCOPED_ANALYSIS_PASS',len(rows),'max_photon_ledger',max_photon_ledger,'max_energy_rel',max_energy,'FLRW64',flrw64,'Q2',metrics)
