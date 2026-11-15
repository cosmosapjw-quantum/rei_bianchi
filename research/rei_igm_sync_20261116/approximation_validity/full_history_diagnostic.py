"""Complete represented-history approximation stress/energy reduction, no IVP."""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_simpson, cumulative_trapezoid
from background_stress import C,G,KB,H0,OM,OR,OL,OGAMMA,AI,angular_moments,background

PINS={
 'ZERO':'4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f',
 'SHEAR_HALF_PLUS':'50efa302db22f58d55c17c0c18c4b0c94e2063cc729e12067a05b2337373031e',
 'SHEAR_HALF_MINUS':'5c8ff1e7f21f56a34514797415680256628279250c63219dccf8e317303ff83e',
 'SHEAR_MINUS':'0c1d2479eebef9b1ec2d4ff56417ee3395ecd122c17326d4a8d827e2ead76d11'}
Q={'ZERO':0,'SHEAR_HALF_PLUS':.005,'SHEAR_HALF_MINUS':-.005,'SHEAR_MINUS':-.01}
EV_J=1.602176634e-19
COUPLING=8*np.pi*G/(3*C*C)
COLS=['q_ref','a','time_s','b','H_per_s','s_per_s','nH_proper_cm3','ne_proper_cm3','temperature_K','photon_u_eV_per_H','J0_photon_u_eV_per_H','J1_photon_u_eV_per_H','J2_photon_u_eV_per_H']

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()

def load_source(path,name):
 if sha(path)!=PINS[name]:raise ValueError('source SHA mismatch '+name)
 # Native Rust emits tiny rates as long fixed-decimal strings. Pandas' default
 # decimal parser truncates some of these to 0; round_trip preserves float().
 d=pd.read_csv(path,usecols=COLS,float_precision='round_trip')
 if len(d)!=312238 or not np.all(np.isfinite(d.to_numpy())):raise ValueError('source rows/nonfinite')
 if not np.all(d.q_ref==Q[name]):raise ValueError('q identity')
 a=d.a.to_numpy()
 if np.any(np.diff(a)<=0) or abs(a[0]-AI)>1e-15 or abs(a[-1]-.2)>1e-15:raise ValueError('epoch domain')
 return d

def integrate(a,H,p):
 x=np.log(a)
 return cumulative_simpson(a**3*COUPLING*p/H,x=x,initial=0)/(a**3*H)

def run(inputs,out):
 start=time.perf_counter();result={};samples=[];out.mkdir(parents=True,exist_ok=True)
 for name in PINS:
  started=time.perf_counter();d=load_source(inputs/name/'history.csv',name)
  a=d.a.to_numpy();b=d.b.to_numpy();H=d.H_per_s.to_numpy();s=d.s_per_s.to_numpy();x=np.log(a)
  hh,ss=background(a,Q[name])
  if np.max(np.abs(H/hh-1))>1e-12:raise ValueError('source H does not match locked background')
  M,F=angular_moments(b,16)
  # J2=sum N_gamma(E,mu)/H * E * P2(mu) in source moments(), with
  # angular weights already contained in photon stocks; apply no new weights.
  nH=d.nH_proper_cm3.to_numpy()*1e6;ne=d.ne_proper_cm3.to_numpy()*1e6
  uion=nH*d.J0_photon_u_eV_per_H.to_numpy()*EV_J
  pion=nH*d.J2_photon_u_eV_per_H.to_numpy()*EV_J
  uref=H0**2*OR/(COUPLING*a**4);prad=uref*F
  uth=1.5*KB*d.temperature_K.to_numpy()*(nH*(1+.2454/(4*(1-.2454)))+ne)
  total_energy=H**2/COUPLING
  dsrad=integrate(a,H,prad);dsion=integrate(a,H,pion);dstotal=integrate(a,H,prad+pion)
  # Same diagnostic in proper time, an independently parameterized integral.
  dstime=cumulative_simpson(a**3*COUPLING*(prad+pion),x=d.time_s.to_numpy(),initial=0)/(a**3*H)
  extra_total=(uion+uth+np.abs(uref*(M-1)))/total_energy
  hf2=H0**2*(OR/a**4+OM/a**3+OL)
  # Match source output_row's target denominator exactly: H_FLRW²/coupling.
  extra=(uion+uth+np.abs(uref*(M-1)))/(hf2/COUPLING)
  imax=int(np.argmax(np.abs(dstotal)));emax=int(np.argmax(extra))
  gl32M,gl32F=angular_moments(b[::311],32)
  bgerr=float(max(np.max(np.abs(gl32M-M[::311])),np.max(np.abs(gl32F-F[::311]))))
  indep=dstotal-dsrad-dsion
  j0diff=np.max(np.abs(d.photon_u_eV_per_H-d.J0_photon_u_eV_per_H))
  result[name]={
   'rows':len(d),'input_sha256':PINS[name],'q_ref':Q[name],
   'max_abs_total_delta_s_over_H':float(np.max(np.abs(dstotal))),
   'signed_total_delta_s_over_H_at_peak':float(dstotal[imax]),
   'stress_peak_zbar':float(1/a[imax]-1),
   'max_abs_background_delta_s_over_H':float(np.max(np.abs(dsrad))),
   'max_abs_CMB_delta_s_over_H':float(np.max(np.abs(dsrad))*OGAMMA/OR),
   'max_abs_ionizing_delta_s_over_H':float(np.max(np.abs(dsion))),
   'max_abs_total_delta_s_over_s':float(np.max(np.abs(dstotal*H/s))) if Q[name] else None,
   'max_extra_energy_over_FLRW_background_source_comparator':float(extra[emax]),
   'max_extra_energy_over_total':float(np.max(extra_total)),
   'energy_peak_zbar':float(1/a[emax]-1),
   'max_ionizing_plus_thermal_over_total':float(np.max((uion+uth)/total_energy)),
   'max_ionizing_over_total':float(np.max(uion/total_energy)),
   'max_thermal_over_total':float(np.max(uth/total_energy)),
   'max_background_energy_correction_over_total':float(np.max(np.abs(uref*(M-1))/total_energy)),
   'max_Thomson_cooling_coefficient_fractional_change':float(np.max(np.abs(M-1))),
   'total_shear_check_original_target':1e-4,
   'total_energy_check_original_target':1e-4,
   'total_shear_status':'BELOW_TARGET' if np.max(np.abs(dstotal))<1e-4 else 'EXCEEDS_TARGET',
   'total_energy_status':'BELOW_TARGET' if np.max(extra)<1e-4 else 'EXCEEDS_TARGET',
   'source_H_locked_background_max_relative_error':float(np.max(np.abs(H/hh-1))),
   'quadrature_GL16_vs_GL32_sample_error':bgerr,
   'separate_vs_joint_integral_max_abs':float(np.max(np.abs(indep))),
   'proper_time_vs_lna_integral_max_abs':float(np.max(np.abs(dstotal-dstime))),
   'source_J0_vs_photon_u_max_eV_per_H':float(j0diff),
   'runtime_wall_s':time.perf_counter()-started,
   'physical_scope':'perturbative forcing on original saved metric, no coupled feedback; original source energy comparator uses H_FLRW squared',
   'original_evolution_error_bound':None,
  }
  ids=np.unique(np.r_[np.linspace(0,len(a)-1,1001).astype(int),imax,emax])
  for i in ids:samples.append([name,Q[name],int(i),a[i],1/a[i]-1,d.time_s.iloc[i],b[i],uion[i],pion[i],uth[i],prad[i],dsrad[i],dsion[i],dstotal[i],extra[i]])
 pd.DataFrame(samples,columns=['case','q_ref','original_row','a','zbar','elapsed_proper_s','b','ionizing_u_J_m3','ionizing_DeltaP_J_m3','thermal_u_J_m3','background_DeltaP_J_m3','background_delta_s_over_H','ionizing_delta_s_over_H','total_delta_s_over_H','extra_energy_over_FLRW_background']).to_csv(out/'full_history_diagnostic_sample.csv',index=False)
 allout={'schema':'rei.axbi.full-history-stress-energy-diagnostic.v1','source_origin':'PR374 source-full archive c8efb1dbde8c51c7356013ad346e97bb0223b64d8a387844d46779d380d7510d','original_scenario':'PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1','cases':result,'runtime_wall_s':time.perf_counter()-start,'rows_consumed':sum(r['rows'] for r in result.values()),'new_IVPs':0,'original_tolerances_changed':False,'status':'SCOPED_APPROXIMATION_DIAGNOSTICS_COMPLETE_FOR_FOUR_REPRESENTED_CASES','DAG_mapping':'AX03/AX08 approximation validity obligation, not AX10 optional observables','canonical_parent_status':'PARTIAL_MISSING_PLUS001_AND_FULL_SCIENTIFIC_ADMISSION','AX11_status':'UNRESOLVED','notes':['Maxima use all original saved rows, not a continuous supremum.','All-effective-Omega_r free streaming is a conditional comparison model, not a rigorous universal stress bound.','No fraction or temperature error bound follows from these stress/energy diagnostics.']}
 (out/'FULL_SUMMARY.json').write_text(json.dumps(allout,indent=2)+'\n');return allout

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(run(a.inputs,a.out),indent=2))
