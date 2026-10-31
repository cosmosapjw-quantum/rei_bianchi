#!/usr/bin/env python3
"""Read-only full BASS193 FS2010 terminal threshold source recovery.

Reuses immutable original 30-epoch kernel from PR300; computes disjoint omitted 162
actual emission epochs from exactly the original PR287->PR300 16x4 source owner.
Epoch 192 has no subsequent arrival interval and is recorded explicitly.
"""
import sys,os,json,hashlib,concurrent.futures,zipfile,io,math
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'.source_extract'/'REI_F4_FS2010_LOW_E_THRESHOLD_20261031'
if not OLD.is_dir():
 import zipfile
 zpath=ROOT/'source'/'PR300_FULL.zip'
 assert hashlib.sha256(zpath.read_bytes()).hexdigest()=='7efbf46e67faf78e5ebaac6e5a3676c2bc633d63e87e5c5b5c5c8f2ebd28b2b0','SOURCE_LOCK_MISMATCH'
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None
  for info in z.infolist():
   pp=Path(info.filename)
   assert not pp.is_absolute() and '..' not in pp.parts and not info.is_dir(),('ZIP_SLIP_OR_DIRECTORY',info.filename)
  z.extractall(ROOT/'.source_extract')
assert OLD.is_dir()
sys.path.insert(0,str(OLD/'code'))
import thresholds
BINS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
GROUPS=['H_I','He_I','He_II','Li_I']
CH=13.598434599702
EMBED_SHA='7efbf46e67faf78e5ebaac6e5a3676c2bc633d63e87e5c5b5c5c8f2ebd28b2b0'

def lock():
 p=ROOT/'source'/'PR300_FULL.zip'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==EMBED_SHA,'PR300 ZIP source mismatch'
 thresholds.check_sources()


def make_groups():
 selected=json.loads((OLD/'evidence'/'SELECTION.json').read_text())['indices'];assert len(selected)==30
 missing=sorted(set(range(192))-set(selected))
 assert len(missing)==162
 groups=[missing[i:i+12] for i in range(0,len(missing),12)]
 return selected,missing,groups

def job(inp):
 idx,epochs=inp
 agg,ker,stat=thresholds.run(output=False,select=epochs)
 dest=ROOT/'results'/'chunks'/f'left_{idx:02d}'
 dest.mkdir(exist_ok=True)
 agg.to_csv(dest/'AGG192.csv',index=False,float_format='%.17g')
 ker.to_csv(dest/'KERNEL.csv',index=False,float_format='%.17g')
 (dest/'STATS.json').write_text(json.dumps({'i':idx,'emission_epochs':epochs,'rows':len(ker),'source_emitted_fraction':stat['selected_source_fraction']},indent=2,sort_keys=True)+'\n')
 return idx,len(ker),float(agg.total_primary_e_eV_per_b.sum())

def work(max_workers=4):
 lock();selected,missing,groups=make_groups()
 manifest={'schema':'REI_F4_FS2010_COMPLEMENT_GROUPS_V1','parent_head':'0e9024f92682bc3b7a0080cc86855cbddca8b0d9','selected_epochs_original':selected,'computed_complement':missing,'unabsorbed_final_epoch':192,'groups':groups}
 (ROOT/'evidence'/'COMPLEMENT_PLAN.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 tasks=[]
 for i,g in enumerate(groups):
  dest=ROOT/'results'/'chunks'/f'left_{i:02d}'
  if all((dest/q).is_file() for q in ['KERNEL.csv','AGG192.csv','STATS.json']):
   print('REUSE_COMPLEMENT',i,flush=True);continue
  tasks.append((i,g))
 print('NEW_CALC_COMPLEMENT',len(tasks),'groups',flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
  futures=[pool.submit(job,t) for t in tasks]
  for f in concurrent.futures.as_completed(futures):
   i,n,e=f.result();print('COMPLETE',i,n,e,flush=True)
 return manifest

def combine():
 plan=json.loads((ROOT/'evidence'/'COMPLEMENT_PLAN.json').read_text());lock()
 old_D=pd.read_csv(OLD/'results'/'FS2010_THRESHOLD_SELECTED_ARRIVAL_192.csv')
 old_K=pd.read_csv(OLD/'results'/'FS2010_THRESHOLD_SELECTED_KERNEL.csv')
 calc=[old_D]; kern=[old_K]
 for i,g in enumerate(plan['groups']):
  dest=ROOT/'results'/'chunks'/f'left_{i:02d}'
  st=json.loads((dest/'STATS.json').read_text());assert st['emission_epochs']==g
  a=pd.read_csv(dest/'AGG192.csv');k=pd.read_csv(dest/'KERNEL.csv')
  got=sorted(k.emission_epoch.unique().tolist())
  absent=sorted(set(g)-set(got))
  assert len(a)==192 and not (set(got)-set(g))
  # The first source epoch has exactly zero emitted singlet pairs in the immutable source.
  # The original PR287 18,528 rows include this 192-row zero-emission plane.
  if absent:
   _,em,_=thresholds.unpack_owner()
   w=em.measuredwindow_2E1_emitted_pairs_rectangle_upper.to_numpy()
   assert absent==[0] and w[0]==0,('UNEXPECTED_MISSING_EPOCH',absent)
   dummy=pd.DataFrame(np.zeros((192,len(old_K.columns))),columns=old_K.columns)
   dummy['emission_epoch']=0;dummy['arrival_interval']=np.arange(192)
   dummy['z_emission']=float(a.z_high.iloc[0]);dummy['z_arrival']=a.z_low.to_numpy()
   k=pd.concat([k,dummy],ignore_index=True)
   print('ZERO_SOURCE_PLANE_RESTORED epoch=0 rows=192',flush=True)
  assert sorted(k.emission_epoch.unique().tolist())==g
  calc.append(a);kern.append(k)
 excluded={'arrival_interval','z_high','z_low','emission_source_pairs_all_epochs_per_b'}
 cols=[c for c in old_D.columns if c not in excluded]
 out=old_D.copy()
 for a in calc[1:]:
  assert np.array_equal(a.arrival_interval,out.arrival_interval)
  assert np.max(abs(a.z_high-out.z_high)) < 1e-13
  assert np.max(abs(a.z_low-out.z_low)) < 1e-13
  out.loc[:,cols]=out.loc[:,cols].to_numpy()+a[cols].to_numpy()
 k=pd.concat(kern,ignore_index=True).sort_values(['emission_epoch','arrival_interval']).reset_index(drop=True)
 assert len(k)==18528 and not k.duplicated(['emission_epoch','arrival_interval']).any()
 assert set(k.emission_epoch)==set(range(192))
 assert len(out)==192
 assert np.isfinite(out.select_dtypes(include=np.number).values).all()
 # all species x energy bins must close to source totals per interval
 E_bands=np.zeros(192);N_bands=np.zeros(192)
 for g in GROUPS:
  for b in BINS:
   E_bands+=out[f'{g}_{b}_primary_e_eV_per_b'].to_numpy()
   N_bands+=out[f'{g}_{b}_counts_per_b'].to_numpy()
 np.testing.assert_allclose(E_bands,out.total_primary_e_eV_per_b,rtol=2e-12,atol=2e-24)
 np.testing.assert_allclose(N_bands,out.total_absorbed_ionizations_per_b,rtol=2e-12,atol=2e-24)
 # exact top30 raw restore unchanged; original parent total energy/number used only for independent science residual
 old_R=json.loads((OLD/'results'/'RESULT.json').read_text())['physics']
 E=float(out.total_primary_e_eV_per_b.sum());N=float(out.total_absorbed_ionizations_per_b.sum())
 origE=old_R['PR297_total_primary_eV_per_b'];origN=old_R['PR297_total_absorbed_events_per_b']
 reE=E/origE-1;reN=N/origN-1
 assert abs(reE)<5e-12,(E,origE,reE)
 assert abs(reN)<5e-12,(N,origN,reN)
 heat=float(out.FS_low_e_heat_kinematic_eV_per_b.sum());secondary=float(out.discrete_H_secondary_max_count_per_b.sum())
 # exact 4th H secondary eligibility for LiI need extra at E_e>=4*chi_HI; current categories split only 54.41776,
 # so count any LiI photoprimary with E_e>=13.6 as worst-case fourth event; stricter simple bound
 # is all LiI primary events, flagged as conservative, rather than claiming exact 4th integral.
 N_Li=float(sum(out[f'Li_I_{b}_counts_per_b'].sum() for b in BINS))
 secondary_safe=secondary+N_Li
 cons_upper=float(E/CH)
 assert secondary_safe<=cons_upper*(1+1e-10)
 # Canonical conserved HHe photo counts from included PR297 reference
 species_counts={g:float(sum(out[f'{g}_{b}_counts_per_b'].sum() for b in BINS)) for g in GROUPS}
 energy_bands={b:float(sum(out[f'{g}_{b}_primary_e_eV_per_b'].sum() for g in GROUPS)) for b in BINS}
 summary={'schema':'REI_F4_FS2010_FULL193_THRESHOLD_ORIGINAL_QUADRATURE_V1','input_head':'0e9024f92682bc3b7a0080cc86855cbddca8b0d9','physics':{
 'emission_epochs':193,'active_emission_epochs':192,'emission_arrival_rows':len(k),'arrival_intervals':192,
 'primary_eV_per_baryon':E,'first_absorption_events_per_baryon':N,
 'source_original_reference_energy_eV_per_baryon':origE,'source_original_reference_events_per_baryon':origN,
 'relative_parent_energy_residual':reE,'relative_parent_event_residual':reN,
 'FS_model_terminal_sub10p2_heat_eV_per_baryon':heat,'FS_model_terminal_sub10p2_fraction_of_primary':heat/E,
 'secondary_discrete_1to3_count_upper_per_baryon':secondary,'LiI_worst_case_fourth_count_addendum_per_baryon':N_Li,
 'secondary_H_I_event_discrete_safe_ceiling_per_baryon':secondary_safe,
 'secondary_H_I_energy_relaxed_bound_per_baryon':cons_upper,
 'species_first_absorption_counts_per_baryon':species_counts,
 'primary_electron_energy_by_bin_eV_per_baryon':energy_bands,
 'original_full_193_photoepoch_source_covered':True,
 'source_weighted_2E1_pair_total_baryon':old_R['total_original_emitted_pairs_per_b']},
 'qualifications':{'FS2010':'E_e<10.2 terminal-energy assignment only; no E-x_i grid available','ionization':'secondary ceiling only, not physical fractional yield','geometry':'original PR287 isotropic averaged BASS193 16-point pair quadrature and 4 hazard substeps, not directional Bianchi transport','singlet':'Ferrett conditional upper, unresolved 1S/3P and K_lab denominator','production':'HOLD','native_REI17':'NOT_RUN','native_subagent':'NOT_RUN','distinct_author_review':'NOT_RUN','IVP':0,'DAG':{'WORKING':'33/88','CENTRAL':'28/88','F4_FAST':'4/7','CANONICAL_DELTA':0,'AUXILIARY_THIS_UNIT':'1/1_SCOPED'},'AUTO_NEXT_NODE':False,'NO_MERGE':True,'NO_FORCE_PUSH':True}}
 (ROOT/'results'/'RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 out.to_csv(ROOT/'results'/'FS2010_FULL193_ARRIVAL_192.csv',index=False,float_format='%.17g')
 k.to_csv(ROOT/'results'/'FS2010_FULL193_KERNEL_18528.csv',index=False,float_format='%.17g')
 print('SCIENCE_RESULT',json.dumps(summary['physics'],sort_keys=True),flush=True)
 return summary

if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--workers',type=int,default=4);a.add_argument('--combine-only',action='store_true');opt=a.parse_args()
 if not opt.combine_only:work(opt.workers)
 combine()
