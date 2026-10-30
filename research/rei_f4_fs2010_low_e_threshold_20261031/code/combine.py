#!/usr/bin/env python3
"""Combine independently run top-30 emission blocks into rigorous source-mass bounds."""
from pathlib import Path
from io import BytesIO
import json,zipfile,hashlib
import numpy as np,pandas as pd
import thresholds as t
ROOT=Path(__file__).resolve().parents[1]
SEL=json.loads((ROOT/'evidence/SELECTION.json').read_text())

def combine():
 frames=[];kernels=[]
 for i,ids in enumerate(SEL['groups']):
  folder=ROOT/'results'/'chunks'/('chunk%02d'%i)
  a=pd.read_csv(folder/'AGG192.csv');k=pd.read_csv(folder/'KERNEL.csv')
  assert len(a)==192 and sorted(k.emission_epoch.unique().tolist())==ids
  frames.append(a);kernels.append(k)
 agg=frames[0].copy()
 cols=[c for c in agg if c not in ('arrival_interval','z_high','z_low','emission_source_pairs_all_epochs_per_b')]
 for x in frames[1:]:
  assert np.all(x.arrival_interval.to_numpy()==agg.arrival_interval.to_numpy())
  assert np.max(np.abs(x.z_high.to_numpy()-agg.z_high.to_numpy()))<1e-13
  agg.loc[:,cols]+=x[cols].to_numpy()
 kernel=pd.concat(kernels,ignore_index=True).sort_values(['emission_epoch','arrival_interval'])
 assert len(kernel)==sum(192-e for e in SEL['indices'])
 inner,em,pr297=t.unpack_owner()
 with zipfile.ZipFile(BytesIO(inner)) as z:
  original=pd.read_csv(BytesIO(z.read('REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/results/FIRST_FLIGHT_KERNEL.csv')))
 sub=original.loc[original.emission_epoch.isin(SEL['indices'])].copy()
 w=em.measuredwindow_2E1_emitted_pairs_rectangle_upper.to_numpy()
 assert len(sub)==len(kernel)
 species=['H_I','He_I','He_II','Li_I']
 resid={}
 for name in species:
  ref=float(np.sum(sub['conditional_first_abs_'+name].to_numpy()*w[sub.emission_epoch.to_numpy(int)]))
  got=float(agg.filter(regex='^'+name+'_.*_counts_per_b$').sum().sum())
  resid[name]={'parent_kernel_per_b':ref,'new_reconstruction_per_b':got,'relative_residual':got/ref-1 if ref else 0}
 refE=float(np.sum(sub.conditional_primary_e_eV.to_numpy()*w[sub.emission_epoch.to_numpy(int)]))
 gotE=float(agg.total_primary_e_eV_per_b.sum())
 refN=float(sum(x['parent_kernel_per_b'] for x in resid.values()))
 gotN=float(agg.total_absorbed_ionizations_per_b.sum())
 originalE=float(pr297['physical_outputs']['all_conditional_primary_e_eV_per_baryon_upper'])
 originalN=float(pr297['physical_outputs']['all_conditional_photo_events_per_baryon_upper'])
 assert abs(refE/gotE-1)<1e-10,(refE,gotE)
 assert abs(refN/gotN-1)<1e-10,(refN,gotN)
 missingE=originalE-refE;missingN=originalN-refN
 assert missingE>=-2e-24 and missingN>=-2e-24
 missingE=max(0,missingE);missingN=max(0,missingN)
 low=float(agg.FS_low_e_heat_kinematic_eV_per_b.sum())
 disc=float(agg.discrete_H_secondary_max_count_per_b.sum())
 # H/He photoelectrons have E<=60.9226-13.5984=47.324 eV (<4*chi_H).
 # Rare Li I photoelectrons have lower ionization threshold (~5.39 eV);
 # a FOURTH H secondary event is kinematically possible. The 1..3 count
 # recorded in the frozen kernel is therefore augmented by a strictly
 # conservative LiI count, never mistaken for a zero channel.
 selected_LiI=float(sum(agg[f'Li_I_{s}_counts_per_b'].sum() for s in ['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']))
 disc_safe=disc+selected_LiI
 consE=float(gotE)
 # lower/upper bounded under 2010 idealized stopping rule and frozen first flight:
 heat_up=low+missingE
 discrete_up=disc_safe+min(missingE/t.CHI_HI,4*missingN)
 self_check={
    'covered_original_emission_epochs':len(SEL['indices']),
    'covered_emitted_singlet_pairs_fraction':SEL['coverage_fraction'],
    'computed_emission_arrival_kernel_rows':len(kernel),
    'original_arrival_epochs':len(agg),
    'total_original_emitted_pairs_per_b':SEL['total_source_pairs_per_b'],
    'missing_source_pairs_per_b':SEL['remaining_source_pairs_per_b'],
    'PR297_total_primary_eV_per_b':originalE,
    'PR297_total_absorbed_events_per_b':originalN,
    'computed_covered_primary_eV_per_b':consE,
    'computed_covered_absorbed_events_per_b':gotN,
    'missing_primary_eV_per_b_parent_provenance':missingE,
    'missing_absorbed_events_per_b_parent_provenance':missingN,
    'FS_assigned_sub10p2_covered_eV_per_b':low,
    'FS_assigned_sub10p2_global_energy_bracket_eV_per_b':[low,heat_up],
    'FS_assigned_sub10p2_global_heat_fraction_bracket':[low/originalE,heat_up/originalE],
    'covered_primary_electron_events_below10p2_per_b':float(agg.FS_sub_excitation_primary_count_per_b.sum()),
    'covered_primary_electron_events_10p2_to13p6_per_b':float(agg.FS_excitation_no_ionization_count_per_b.sum()),
    'covered_primary_electron_events_above13p6_per_b':float(agg.FS_H_secondary_ionization_energetic_count_per_b.sum()),
    'covered_discrete_H_ionization_three_threshold_sum_per_b':disc,
    'covered_LiI_fourth_secondary_worstcase_addendum_per_b':selected_LiI,
    'covered_discrete_H_ionization_secondary_SAFE_ceiling_per_b':disc_safe,
    'global_discrete_H_ionization_secondary_ceiling_per_b':discrete_up,
    'global_continuous_secondary_ceiling_PR297_per_b':originalE/t.CHI_HI,
    'covered_secondary_HeII_kinematically_eligible_events_from_HHe_primary_per_b':float(sum(agg[f'{g}_e54p42_plus_counts_per_b'].sum() for g in ['H_I','He_I','He_II'])),
    'covered_secondary_HeII_kinematically_eligible_events_from_LiI_primary_per_b':float(agg['Li_I_e54p42_plus_counts_per_b'].sum()),
    'max_HHe_initial_primary_e_eV':60.922559447552-13.598434599702,
    'max_LiI_initial_primary_e_eV':60.922559447552-5.39,
    'HHe_absorber_primary_cannot_secondary_HeII':bool(60.922559447552-13.598434599702<54.41776),
    'all_absorbers_secondary_HeII_impossible':False,
    'parent_AGG_photon_counts_reference_residuals':resid,
    'parent_AGG_total_electron_energy_relative_residual':gotE/refE-1,
    'parent_AGG_photo_counts_relative_residual':gotN/refN-1,
 }
 out=ROOT/'results'
 agg.to_csv(out/'FS2010_THRESHOLD_SELECTED_ARRIVAL_192.csv',float_format='%.17g',index=False)
 kernel.to_csv(out/'FS2010_THRESHOLD_SELECTED_KERNEL.csv',float_format='%.17g',index=False)
 qualification={
   'model':'FS2010 original sub-10.2 eV low-energy terminal assignment only; not complete FS2010 2D deposition tables or actual thermochemical evolution',
   'conditional_source':'PR294 Ferrett R31 R32 rectangular upper on BASS193 K operator not reconciled against native lab n2+n3 denominator',
   'metric_signature':'-+++',
   'unit':'eV per original baryon, no c=hbar=kB=1 assumption',
   'numerical_approximation':'PR287 original 16 spectral order and 4 ln(a) constant-hazard substeps, analytic within-step threshold crossing',
   'source_selection':'top30 by actual emitted LiII singlet pairs (99.4806% coverage), uncomputed rest bounded using parent PR297 energy ledger',
   'FS_ambient_ion_fraction':'2010 uses shared x_i for H and helium, not applied to actual BASS species; 2D tables NOT_ACQUIRED',
   'native_REI17':'NOT_RUN',
   'no_new_IVP':True,'auto_next_node':False,'production':'HOLD','F4':'PARTIAL','L4_ready':False,
   'R6_C9_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN',
   'DAG':{'WORKING':'33/88','CENTRAL':'28/88','F4_FAST':'4/7','CANONICAL_DELTA':0,'NEW_AUXILIARY':'1/1_SCOPED'},
 }
 manifest={'schema':'REI_F4_FS2010_TOP30_THRESHOLD_FIRSTFLIGHT_V1','selection':SEL,'physics':self_check,'qualification':qualification}
 (out/'RESULT.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print(json.dumps(self_check,indent=2))
 return agg,kernel,manifest
if __name__=='__main__':combine()
