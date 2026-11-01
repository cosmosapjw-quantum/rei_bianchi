#!/usr/bin/env python3
"""Independent physical algebra and source CSV check; no import from thermochemical_closure."""
import argparse,csv,gzip,hashlib,io,json,math
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-archive',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert sha(a.source_archive)=='48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7'
 with ZipFile(a.source_archive) as z:
  assert z.testzip() is None
  inputs=pd.read_csv(io.BytesIO(z.read('NODEWISE_LOCAL_NEUTRAL_HAZARD_PRIMARY_46080_PHYSICAL.csv.gz')),compression='gzip')
 outputs=pd.read_csv(a.candidate,compression='gzip')
 assert inputs.shape[0]==outputs.shape[0]==46080
 assert np.array_equal(inputs['node'].values,outputs['node'].values)
 mid=lambda name:(inputs[name+'_lo'].to_numpy()+inputs[name+'_hi'].to_numpy())/2
 nH=mid('x_HII');nHe2=mid('x_HeII');nHe3=mid('x_HeIII');T=mid('T_K');xe=mid('xe_per_H'); u=mid('U_thermal_erg_per_H')
 # Independent atomic energy form: E=(I_H nH + I_HeI nHe2*y + (I_HeI+I_HeII)nHe3*y).
 y=.079;k=1.380649e-16;ev=1.602176634e-12
 I_H=13.598434599702;I_He1=24.587389011;I_He2=54.4177655282
 B=I_H*nH+y*I_He1*nHe2+y*(I_He1+I_He2)*nHe3
 N=1+y+xe
 material_ion_ratio=B/(u/ev)
 thermo_sus_H=I_H/(u/ev)+1/N
 thermo_sus_He2_to_He3=y*I_He2/(u/ev)+y/N
 geometric_width=np.log(inputs['T_K_hi'].to_numpy()/inputs['T_K_lo'].to_numpy())
 independent_width=np.log(inputs['U_thermal_erg_per_H_hi'].to_numpy()/inputs['U_thermal_erg_per_H_lo'].to_numpy())+np.log((1+y+inputs['xe_per_H_hi'].to_numpy())/(1+y+inputs['xe_per_H_lo'].to_numpy()))
 for name, expected in [('E_ion_eV_per_H',B),('E_ion_over_U_thermal',material_ion_ratio),('abs_dlnT_dx_HII_at_fixed_Ematerial',thermo_sus_H),('abs_dlnT_dHeII_to_HeIII_at_fixed_Ematerial',thermo_sus_He2_to_He3),('parent_logT_width_from_source',geometric_width),('parent_logT_width_independent_U_xe',independent_width)]:
  result=outputs[name].to_numpy();difference=np.max(np.abs(result-expected));scale=max(np.max(np.abs(expected)),1.)
  assert difference/scale<3e-14,(name,difference)
 # Direct thermodynamic reconstruction, independent of source-candidate implementation.
 reconstructed_u=1.5*k*T*N
 assert np.max(np.abs(reconstructed_u-u)/u) < 2e-9
 # Exact H and He transition finite differences on 200 deterministic original nodes.
 sample=np.linspace(0,46079,200,dtype=int);eps=2e-7
 for idx in sample:
  ion=B[idx];en=u[idx]/ev+ion
  def lt(h,he2,he3):
   bind=I_H*h+y*I_He1*he2+y*(I_He1+I_He2)*he3
   npe=1+y+h+y*(he2+2*he3)
   return math.log((en-bind)/npe)
  h=nH[idx];he2=nHe2[idx];he3=nHe3[idx]
  h_slope=(lt(h+eps,he2,he3)-lt(h-eps,he2,he3))/(2*eps)
  he_slope=(lt(h,he2-eps,he3+eps)-lt(h,he2+eps,he3-eps))/(2*eps)
  assert abs(h_slope+thermo_sus_H[idx])<2e-8,(idx,h_slope)
  assert abs(he_slope+thermo_sus_He2_to_He3[idx])<2e-8,(idx,he_slope)
 assert np.sum(independent_width>2e-4)==252
 assert np.sum(geometric_width>2e-4)==0
 report={'schema':'ORIGINAL_PR320_46080_INDEPENDENT_PHYSICAL_ALGEBRA_AUDIT_V1',
   'source_sha256':sha(a.source_archive),'candidate_sha256':sha(a.candidate),'rows':len(outputs),
   'real_nodes_recomputed':len(inputs),'transition_finite_difference_sample':len(sample),
   'max_direct_thermal_relative_residual':float(np.max(abs(reconstructed_u-u)/u)),
   'marginal_width_exceed_numerical_2e-4':252,'source_width_exceed_numerical_2e-4':0,
   'scoped_physical_audit':'PASS','distinct_author':'NOT_RUN','canonical_delta':0,
   'notice':'The original 2e-4 criterion is a local-error threshold, not a parent width gate.'}
 a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
