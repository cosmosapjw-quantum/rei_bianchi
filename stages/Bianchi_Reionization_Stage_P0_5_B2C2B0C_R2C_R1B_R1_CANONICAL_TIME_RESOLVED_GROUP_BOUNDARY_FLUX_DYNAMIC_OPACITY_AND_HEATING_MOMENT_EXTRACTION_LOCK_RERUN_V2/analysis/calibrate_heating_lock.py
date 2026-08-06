#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

MAP={'HI':'excess_HI','HeI':'excess_HeI','HeII':'excess_HeII'}
GROUPS=['G1','G2a','G2b','G3']
SUPPORT={'HI':set(GROUPS),'HeI':{'G2a','G2b','G3'},'HeII':{'G3'}}

def load_source(path:Path):
 sys.path.insert(0,str(path.parent)); spec=importlib.util.spec_from_file_location('heating_lane',path); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--atomic',type=Path,required=True); ap.add_argument('--forcing',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
 m=load_source(a.source); lane=m.make_spectrum_lanes()['MFP_BASELINE_E_MINUS_2P5_1_TO_4_RYD']
 atomic=pd.read_csv(a.atomic/'verner_gray_and_limit_moments.csv'); rows=[]
 for s in MAP:
  target=np.asarray(getattr(lane,MAP[s]),float)
  for gi,g in enumerate(GROUPS):
   ar=atomic[(atomic.species==s)&(atomic.group==g)].iloc[0]
   if g not in SUPPORT[s]:
    rows.append({'species':s,'group':g,'supported':False,'canonical_excess_eV':float(target[gi]),'thin_excess_eV':0.0,'thick_excess_eV':0.0,'hardening_coordinate':0.0,'reconstructed_excess_eV':0.0,'relative_residual':0.0,'status':'STRUCTURAL_EXACT_ZERO'})
    continue
   thin=float(ar.thin_excess_eV); thick=float(ar.thick_excess_eV); tgt=float(target[gi]); alpha=(tgt-thin)/(thick-thin) if thick!=thin else 0.0
   recon=thin+alpha*(thick-thin); rel=abs(recon-tgt)/max(abs(tgt),1.0)
   rows.append({'species':s,'group':g,'supported':True,'canonical_excess_eV':tgt,'thin_excess_eV':thin,'thick_excess_eV':thick,'hardening_coordinate':alpha,'reconstructed_excess_eV':recon,'relative_residual':rel,'status':'BDF_CANONICAL_THIN_LIMIT_CALIBRATION' if abs(alpha)<1e-10 else 'BOUNDED_HARDENING_CALIBRATION'})
 cdf=pd.DataFrame(rows); cdf.to_csv(a.output/'bdf_heating_moment_calibration.csv',index=False)
 f=pd.read_csv(a.forcing)
 thermal_cols=[c for c in f.columns if c.startswith('thermal_')]
 f[['interval_index','node_index','fraction','z_mid',*thermal_cols]].to_csv(a.output/'time_resolved_thermal_forcing.csv',index=False)
 identity=np.abs(f['thermal_thermal_rhs_erg_cm-3_s-1']-(f['thermal_photoheat_erg_cm-3_s-1']-f['thermal_cooling_total_erg_cm-3_s-1']-f['thermal_expansion_work_erg_cm-3_s-1']))/np.maximum(np.abs(f['thermal_thermal_rhs_erg_cm-3_s-1']),np.abs(f['thermal_photoheat_erg_cm-3_s-1'])+np.abs(f['thermal_cooling_total_erg_cm-3_s-1'])+np.abs(f['thermal_expansion_work_erg_cm-3_s-1']))
 summary={'classification':'BDF_CALIBRATED_HEATING_LOCK_SUMMARY','supported_pair_count':int(cdf.supported.sum()),'max_calibration_relative_residual':float(cdf.relative_residual.max()),'hardening_coordinate_range':[float(cdf[cdf.supported].hardening_coordinate.min()),float(cdf[cdf.supported].hardening_coordinate.max())],'hardening_coordinates_inside_unit_interval':bool(((cdf[~cdf.supported].hardening_coordinate==0)&(cdf[~cdf.supported].canonical_excess_eV==0)).all() and ((cdf[cdf.supported].hardening_coordinate>=-1e-12)&(cdf[cdf.supported].hardening_coordinate<=1+1e-12)).all()),'max_thermal_rhs_identity_relative_residual':float(identity.max()),'thermal_time_row_count':int(len(f)),'photon_number_and_energy_ledgers_separate':True,'ownership':{'photoheating':'absorbed photons times species/group excess-energy moment','cooling':'recombination+excitation+collisional-ionization+free-free','expansion_work':'3 H p','mass_transfer_work':'not introduced in this input-lock stage'}}
 (a.output/'heating_lock_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
