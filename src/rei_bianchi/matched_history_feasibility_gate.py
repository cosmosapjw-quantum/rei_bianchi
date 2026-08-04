"""Hard feasibility gate for the B2C2B0B matched history.

A bounded species history cannot exist if the ionized-phase H I absorption
exceeds full-OTS recombination cycling plus the entire remaining H I storage
capacity over an interval.  This executable evaluates that necessary
condition for the primary hierarchy and every locked B2C2B0A sensitivity
lane before any post-hoc unresolved-sink subtraction is permitted.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import phase_space_kernel_b2c0 as B2C0

SHAPE_LANES=[
 'LOCAL_NEUTRAL_HAZARD_PRIMARY',
 'RECOMBINATION_WEIGHTED_AUDITOR',
 'SCRIPT_SELF_SHIELDING_AUDITOR',
]
CHEMISTRY_LANES=[
 'PRIMARY_DETERMINISTIC',
 'MACRO_DENSITY_VARIANCE',
 'EARLY_REIONIZED_COOLER',
 'EARLY_REIONIZED_HOTTER',
 'PATCHY_BETA_DIRICHLET',
]
MYR_S=1e6*365.25*86400.0
NHC=B2C0.NH0_CM3*B2C0.MPC_CM**3
YHE=B2C0.YHE

def execute(b0a:Path,r1:Path,output:Path)->dict:
 output.mkdir(parents=True,exist_ok=True)
 source=pd.read_csv(b0a/'data/hierarchical_full_ots_source.csv')
 primary=source[source.closure=='LOCAL_NODE_STATE_PRIMARY_DETERMINISTIC'].set_index('z')
 sens=pd.read_csv(b0a/'data/hierarchical_sensitivity_auditors.csv')
 comp=pd.read_csv(r1/'data/reconciled_physical_component_absorption.csv')
 ledger=pd.read_csv(r1/'data/canonical_direct_photon_ledger.csv').set_index('z_mid')
 history=pd.read_csv(r1/'data/canonical_direct_history.csv').set_index('z')
 hi_abs=(comp[comp.component.isin(['EFFECTIVE_HI_SUBGRID','EXPLICIT_HI_ATOMIC'])]
         .groupby('z_mid')['absorption_rate_s-1_cMpc-3'].sum())
 hei_abs=(comp[comp.component=='EXPLICIT_HEI_ATOMIC']
          .groupby('z_mid')['absorption_rate_s-1_cMpc-3'].sum())
 ratios={}
 for lane in CHEMISTRY_LANES:
  if lane=='PRIMARY_DETERMINISTIC':
   ratios[lane]=pd.Series(1.0,index=primary.index)
  else:
   key=lane
   sub=sens[sens.auditor==key].set_index('z')
   ratios[lane]=sub.m_H_ratio_to_primary
 rows=[]
 for shape in SHAPE_LANES:
  for chemistry in CHEMISTRY_LANES:
   ratio_series=ratios[chemistry]
   for z in sorted(hi_abs.index,reverse=True):
    rec=ledger.loc[z]; zstart=float(rec.z_start); dt=float(rec.dt_Myr)*MYR_S
    xh=float(history.loc[zstart,'xHII'])
    x2=float(history.loc[zstart,'xHeII']); x3=float(history.loc[zstart,'xHeIII'])
    JH=float(hi_abs.loc[z]); JHe=float(hei_abs.loc[z])
    MH=float(primary.loc[z,'m_HI_to_HII_s-1_cMpc-3']*ratio_series.loc[z])
    MHe=float(primary.loc[z,'m_HeI_to_HeII_s-1_cMpc-3'])
    storage_H=NHC*max(1-xh,0)/dt
    # Maximum HeII growth storage for HeI photoionization; a negative result
    # is not expected here, but the bound is recorded symmetrically.
    storage_He=YHE*NHC*max(1-x2-x3,0)/dt
    deficit=JH-MH-storage_H
    feasible=deficit<=0
    sat=math.inf
    if JH>MH:
      sat=NHC*max(1-xh,0)/(JH-MH)/MYR_S
    rows.append({
      'shape_lane':shape,'chemistry_lane':chemistry,'z_mid':z,
      'z_start':zstart,'dt_Myr':float(rec.dt_Myr),
      'H_absorption_s-1_cMpc-3':JH,
      'H_full_OTS_maintenance_s-1_cMpc-3':MH,
      'H_maximum_storage_rate_s-1_cMpc-3':storage_H,
      'H_capacity_deficit_s-1_cMpc-3':deficit,
      'H_absorption_over_maintenance':JH/MH,
      'H_maximum_chemistry_fraction':min((MH+storage_H)/JH,1.0),
      'H_minimum_nonchemistry_fraction_bound':max(1-(MH+storage_H)/JH,0.0),
      'H_boundary_saturation_time_Myr':sat,
      'H_feasible_without_separate_sink_reservoir':feasible,
      'HeI_absorption_s-1_cMpc-3':JHe,
      'HeI_full_OTS_maintenance_s-1_cMpc-3':MHe,
      'HeI_maximum_growth_storage_rate_s-1_cMpc-3':storage_He,
      'HeI_abs_minus_maintenance_s-1_cMpc-3':JHe-MHe,
    })
 frame=pd.DataFrame(rows)
 frame.to_csv(output/'matched_history_capacity_gate.csv',index=False)
 primary_frame=frame[(frame.shape_lane=='LOCAL_NEUTRAL_HAZARD_PRIMARY') &
                     (frame.chemistry_lane=='PRIMARY_DETERMINISTIC')].copy()
 primary_frame.to_csv(output/'primary_capacity_blocker.csv',index=False)
 maxenv=[]
 for z,sub in frame.groupby('z_mid'):
  # Shape lanes do not alter global totals; maximize only over chemistry lanes.
  unique=sub[sub.shape_lane=='LOCAL_NEUTRAL_HAZARD_PRIMARY']
  best=unique.loc[unique['H_full_OTS_maintenance_s-1_cMpc-3'].idxmax()]
  maxenv.append({
    'z_mid':z,'max_envelope_chemistry_lane':best.chemistry_lane,
    'H_absorption_s-1_cMpc-3':best['H_absorption_s-1_cMpc-3'],
    'H_max_envelope_maintenance_s-1_cMpc-3':best['H_full_OTS_maintenance_s-1_cMpc-3'],
    'H_maximum_storage_rate_s-1_cMpc-3':best['H_maximum_storage_rate_s-1_cMpc-3'],
    'H_capacity_deficit_s-1_cMpc-3':best['H_capacity_deficit_s-1_cMpc-3'],
    'H_minimum_nonchemistry_fraction_bound':best['H_minimum_nonchemistry_fraction_bound'],
    'H_boundary_saturation_time_Myr':best['H_boundary_saturation_time_Myr'],
    'feasible_within_locked_sensitivity_envelope':bool(best['H_capacity_deficit_s-1_cMpc-3']<=0),
  })
 maxenv=pd.DataFrame(maxenv).sort_values('z_mid',ascending=False)
 maxenv.to_csv(output/'maximum_sensitivity_envelope_capacity.csv',index=False)
 all_primary_fail=bool((primary_frame['H_capacity_deficit_s-1_cMpc-3']>0).all())
 maxenv_fail_count=int((maxenv['H_capacity_deficit_s-1_cMpc-3']>0).sum())
 shape_independence=float(
  frame.groupby(['chemistry_lane','z_mid'])['H_capacity_deficit_s-1_cMpc-3'].agg(lambda x:x.max()-x.min()).max()
 )
 result={
  'stage':'P0.5-B2C2B0B-MATCHED-PHASESPACE-HISTORY-LOCK',
  'verdict':'FAIL_CLOSED_ABSORPTION_CHEMISTRY_CAPACITY_MISMATCH',
  'hard_gate':{
    'necessary_condition':'J_H <= M_H + n_H^c(1-X_HII,start)/Delta_t',
    'primary_all_intervals_fail':all_primary_fail,
    'maximum_sensitivity_envelope_failed_interval_count':maxenv_fail_count,
    'interval_count':int(len(maxenv)),
    'shape_lane_global_capacity_difference_max':shape_independence,
    'primary_minimum_nonchemistry_fraction_bound_range':[
      float(primary_frame['H_minimum_nonchemistry_fraction_bound'].min()),
      float(primary_frame['H_minimum_nonchemistry_fraction_bound'].max()),
    ],
    'maximum_envelope_nonchemistry_fraction_bound_max':float(maxenv['H_minimum_nonchemistry_fraction_bound'].max()),
    'primary_saturation_time_Myr_range':[
      float(primary_frame['H_boundary_saturation_time_Myr'].min()),
      float(primary_frame['H_boundary_saturation_time_Myr'].max()),
    ],
  },
  'interpretation':(
    'The R1 effective H I absorption contains a channel that cannot be '
    'represented as photoionization plus full-OTS cycling in the locked '
    'diffuse hierarchical parcel state. Assigning all absorption to node '
    'chemistry would force X_HII above unity. This is not a timestep failure.'
  ),
  'accepted_matched_history_created':False,
  'B2C2B_authorization':{'authorized':False,'reason':'matched history capacity gate failed'},
  'next_stage':'P0.5-B2C2B0C-JOINT-CHEMISTRY-SINK-RESERVOIR-HISTORY-LOCK',
  'forbidden_work_confirmed':['no sink clipping','no post-hoc species redistribution','no new front allocation','no Q_M growth','no source/f_esc calibration','no recombination implementation','no Bianchi feedback'],
 }
 (output.parent/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--b0a-root',type=Path,required=True);p.add_argument('--r1-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(execute(a.b0a_root,a.r1_root,a.output),indent=2))
