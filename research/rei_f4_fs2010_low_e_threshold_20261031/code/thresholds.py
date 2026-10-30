#!/usr/bin/env python3
"""Primary-electron threshold-resolved first-flight Li II 2E1 response on BASS193.

Source: immutable private PR297->PR294->PR293->PR287 source chain. Reproduce the
original PR287 constant-hazard substep integration at the original 16-point
spectral order / 4 substeps, but retain photoelectron kinetic-energy thresholds
within every substep, analytically in its absorption time u. No new cosmological
IVP, no actual secondary-cascade Monte Carlo and NO extra source insertion.
"""
from __future__ import annotations
import csv,hashlib,importlib.util,io,json,os,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES=['H_I','He_I','He_II','Li_I']
THRESHOLDS=np.array([10.2,13.598434599702,24.587389011,54.41776],float)
CHI_HI=float(THRESHOLDS[1])
RECIP_EV_PER_ERG=1/1.602176634e-12

def file_sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def check_sources():
 d=json.loads((ROOT/'evidence'/'SOURCE_LOCK.json').read_text())
 for name,identity in d.items():
  p=ROOT/'source'/name
  assert p.stat().st_size==identity['bytes'] and file_sha(p)==identity['sha256'],('SOURCE_IDENTITY',name)
 return d

def unpack_owner():
 """Yield historical code in a tempdir; original parent PDFs never published."""
 zpath=ROOT/'source'/'PR297_FULL.zip'
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None
  b=z.read('REI_F4_LI2E1_HHE_CAUSAL_POINT_SOURCE_20261031/source/PR294_FULL.zip')
  oldres=json.loads(z.read('REI_F4_LI2E1_HHE_CAUSAL_POINT_SOURCE_20261031/results/RESULT.json'))
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  assert z.testzip() is None
  em=pd.read_csv(io.BytesIO(z.read('REI_F4_SPIN_BOUNDED_CAUSAL_BRIDGE_20261030/results/EMITTED_SPIN_ENVELOPE_193.csv')))
  c=z.read('REI_F4_SPIN_BOUNDED_CAUSAL_BRIDGE_20261030/source/PR293_FULL.zip')
 with zipfile.ZipFile(io.BytesIO(c)) as z:
  assert z.testzip() is None
  d=z.read('REI_F4_COMMON_FJ_ELECTRON_THERMAL_CLOCK_20261030/source/REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030_FULL.zip')
 assert hashlib.sha256(d).hexdigest()=='cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef'
 return d,em,oldres

def integrated_interval(s,frac,lam,Estart,chi,width,u0,u1):
 """Count and primary kinetic energy for u in [u0,u1] (per source photon node).
 
 s:(n,), frac:(species,n), lam:(n,), Estart:(n,), chi:(species,)
 Original PR287 treats total hazard as constant in subcell, allowing exact
 conditional analytic integration of E(u)=Estart exp(-u).
 """
 dt=np.maximum(u1-u0,0)
 count=s[None,:]*frac*np.exp(-lam[None,:]*u0)*(-np.expm1(-lam[None,:]*dt))
 energy=s[None,:]*frac*Estart[None,:]*(lam/(1+lam))[None,:]*np.exp(-(lam[None,:]+1)*u0)*(-np.expm1(-(lam[None,:]+1)*dt))
 kinetic=energy-chi[:,None]*count
 # protect tiny negative from floating point cancellation, not from physics
 if np.min(kinetic)<-1e-11:raise AssertionError('NEGATIVE_PRIMARY_KINETIC')
 return count,np.maximum(kinetic,0)

def run(output=True,order=16,substeps=4,select=None,top=None,progress=False):
 check_sources()
 inner,source,oldres=unpack_owner()
 with tempfile.TemporaryDirectory(prefix='rei_fs2010_parent_') as td:
  with zipfile.ZipFile(io.BytesIO(inner)) as z:
   assert z.testzip() is None
   for item in z.infolist():
    pp=Path(item.filename)
    if pp.is_absolute() or '..' in pp.parts:raise AssertionError('ZIP_SLIP')
    if item.is_dir():continue
    dest=Path(td)/pp;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(item))
  root=Path(td)/'REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030'
  path=root/'code'/'causal_firstflight.py'
  spec=importlib.util.spec_from_file_location('rei_original_frozen_287',path)
  m287=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m287;spec.loader.exec_module(m287)
  with m287.owner() as m:
   data,H,nb,epochs,bins,net=m.load_original()
   x=np.array(data['x']);z=np.array(data['z']);Y=np.array(data['Y']);Nepochs=len(x)
   assert Nepochs==193 and len(source)==193 and len(H)==len(nb)==Nepochs and Y.shape==(193,21)
   assert np.max(np.abs(source.z.to_numpy()-z))<1e-10
   emitted=source.measuredwindow_2E1_emitted_pairs_rectangle_upper.to_numpy()
   assert np.all(emitted>=0)
   yy,ww,_,_=m287._float_observables(m,net,order)
   spectral_n=len(yy)
   E0=np.concatenate([yy*m.E_SINGLET_EV,(1-yy)*m.E_SINGLET_EV])
   assert abs(ww.sum()-1)<1e-13
   chi=np.array(net.transition_energy_eV,float)
   ngroups=np.zeros((4,len(chi)),dtype=float)
   for g,name in enumerate(CATEGORIES):ngroups[g,list(m.CAT_GROUPS[name])]=1
   assert np.all(np.sum(ngroups,axis=0)<=1)  # inactive channels have zero original ion cross-section
   W=np.concatenate([ww,ww])
   if select is not None:indices=[int(k) for k in select]
   elif top is not None:indices=sorted(np.argsort(emitted)[::-1][:int(top)].tolist())
   else:indices=list(range(193))
   named_cols=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
   values=np.zeros((192,4,5,2),float) # [arrival, group, kinetic range, count or eV]
   lo_sec=np.zeros((192,4),float)   # expected integer secondary upper for H-I ionizations: floor(E/13.598)
   rows=[];max_total_residual=0.;max_energy_residual=0.
   for ik,k in enumerate(indices):
    if progress and ik%32==0:print('threshold progression',ik,'/',len(indices),flush=True)
    scale=emitted[k]
    if scale==0 or k==192:continue
    surv=np.ones(2*spectral_n)
    for j in range(k,192):
     local=np.zeros((4,5,2),float);int_ceiling=np.zeros(4,float)
     dx=(x[j+1]-x[j])/substeps
     for sub in range(substeps):
      t0=x[j]+sub*dx;tm=t0+dx/2;f=(tm-x[j])/(x[j+1]-x[j])
      Hm=np.exp(np.log(H[j])*(1-f)+np.log(H[j+1])*f)
      nbm=np.exp(np.log(nb[j])*(1-f)+np.log(nb[j+1])*f)
      Ym=(1-f)*Y[j]+f*Y[j+1]
      Ep=E0*np.exp(-(tm-x[k]))
      sigma,_=net.photo_cross_sections(Ep)
      K=nbm*Ym[:,None]*sigma
      kapp=K.sum(axis=0)
      lam=kapp*m287.C/Hm
      frac=np.divide(K,kapp[None,:],out=np.zeros_like(K),where=kapp[None,:]>0)
      Estrt=E0*np.exp(-(t0-x[k]))
      u0=np.zeros_like(K);u1=np.full_like(K,dx)
      allN,allE=integrated_interval(surv,frac,lam,Estrt,chi,dx,u0,u1)
      cumul=[]
      for thr in THRESHOLDS:
       critical=np.log(Estrt[None,:]/(chi[:,None]+thr))
       boundary=np.clip(critical,0,dx)
       nb_,eb_=integrated_interval(surv,frac,lam,Estrt,chi,dx,boundary,u1)
       cumul.append((nb_,eb_))
      thresholds=[(np.zeros_like(allN),np.zeros_like(allE))]+cumul+[(allN,allE)]
      for band in range(5):
       Nband=thresholds[band+1][0]-thresholds[band][0]
       Eband=thresholds[band+1][1]-thresholds[band][1]
       local[:,band,0]+=ngroups@(Nband@W)
       local[:,band,1]+=ngroups@(Eband@W)
      # Bound N_secondary by sum P(E_kin >= n*chi_HI) for n=1,2,3;
      # no electron can have more than 3 such ionizations for E_line=60.923 eV.
      for nsec in (1,2,3):
       bound=np.clip(np.log(Estrt[None,:]/(chi[:,None]+nsec*CHI_HI)),0,dx)
       geN,_=integrated_interval(surv,frac,lam,Estrt,chi,dx,u0,bound)
       int_ceiling+=ngroups@(geN@W)
      # preserve parent PR287 exponential survival exactly
      surv=surv*np.exp(-lam*dx)
     values[j]+=scale*local
     lo_sec[j]+=scale*int_ceiling
     row={'emission_epoch':k,'arrival_interval':j,'source_emitted_2E1_pairs_per_b':scale,'z_emission':z[k],'z_arrival':z[j+1]}
     for g,name in enumerate(CATEGORIES):
      for q,band in enumerate(named_cols):
       row[name+'_'+band+'_counts_per_pair']=local[g,q,0]
       row[name+'_'+band+'_primary_e_eV_per_pair']=local[g,q,1]
      row[name+'_integer_secondary_Hion_energy_cap_per_pair']=int_ceiling[g]
     rows.append(row)
   # all arrival summed original BASS193 singlet upper source
   out=[]
   for j in range(192):
    row={'arrival_interval':j,'z_high':z[j],'z_low':z[j+1],
       'emission_source_pairs_all_epochs_per_b':float(emitted.sum())}
    for g,name in enumerate(CATEGORIES):
     for q,band in enumerate(named_cols):
      row[name+'_'+band+'_counts_per_b']=float(values[j,g,q,0]);row[name+'_'+band+'_primary_e_eV_per_b']=float(values[j,g,q,1])
     row[name+'_integer_secondary_Hion_energy_cap_per_b']=float(lo_sec[j,g])
    row['total_absorbed_ionizations_per_b']=float(values[j,:,:,0].sum())
    row['total_primary_e_eV_per_b']=float(values[j,:,:,1].sum())
    row['FS_low_e_heat_kinematic_eV_per_b']=float(values[j,:,0,1].sum())
    row['FS_sub_excitation_primary_count_per_b']=float(values[j,:,0,0].sum())
    row['FS_excitation_no_ionization_count_per_b']=float(values[j,:,1,0].sum())
    row['FS_H_secondary_ionization_energetic_count_per_b']=float(values[j,:,2:,0].sum())
    row['discrete_H_secondary_max_count_per_b']=float(lo_sec[j].sum())
    out.append(row)
   agg=pd.DataFrame(out)
   covered_emitted=float(emitted[indices].sum());total_emitted=float(emitted.sum())
   parent_all_count=float(oldres['physical_outputs']['all_conditional_photo_events_per_baryon_upper'])
   parent_all_e=float(oldres['physical_outputs']['all_conditional_primary_e_eV_per_baryon_upper'])
   leftover_emitted=total_emitted-covered_emitted
   leftover_e_upper=min(parent_all_e,2*m.E_SINGLET_EV*leftover_emitted)
   phys={
      'emitted_singlet_pairs_per_b':total_emitted,
      'selected_emission_epochs':len(indices),
      'total_original_emission_epochs':len(emitted),
      'selected_source_fraction':covered_emitted/total_emitted,
      'missing_emitted_pairs_per_b':leftover_emitted,
      'FS_model_global_low_energy_heat_lower_eV_per_b':float(agg.FS_low_e_heat_kinematic_eV_per_b.sum()),
      'FS_model_global_low_energy_heat_upper_eV_per_b_conservative':float(agg.FS_low_e_heat_kinematic_eV_per_b.sum()+leftover_e_upper),
      'discrete_H_secondary_global_upper_per_b':float(agg.discrete_H_secondary_max_count_per_b.sum()+min(leftover_e_upper/CHI_HI,6*leftover_emitted)),
      'absorbed_primary_photo_events_per_b':float(agg.total_absorbed_ionizations_per_b.sum()),
      'primary_electron_eV_per_b':float(agg.total_primary_e_eV_per_b.sum()),
      'FS_model_sub10p2_heat_eV_per_b':float(agg.FS_low_e_heat_kinematic_eV_per_b.sum()),
      'FS_model_sub10p2_heat_fraction_of_primary':float(agg.FS_low_e_heat_kinematic_eV_per_b.sum()/agg.total_primary_e_eV_per_b.sum()),
      'FS_model_sub10p2_primary_events_per_b':float(agg.FS_sub_excitation_primary_count_per_b.sum()),
      'FS_model_10p2_to13p6_events_per_b':float(agg.FS_excitation_no_ionization_count_per_b.sum()),
      'energetically_H_ionization_eligible_primary_events_per_b':float(agg.FS_H_secondary_ionization_energetic_count_per_b.sum()),
      'discrete_secondary_Hion_ceiling_per_b':float(agg.discrete_H_secondary_max_count_per_b.sum()),
      'continuous_relaxed_secondary_ceiling_per_b':float(agg.total_primary_e_eV_per_b.sum()/CHI_HI),
      'HeII_secondary_possible_events_per_b':float(values[:,:,-1,0].sum()),
      'HeII_secondary_kinematic_impossibility':bool(m.E_SINGLET_EV-min(chi[np.flatnonzero(ngroups[0])])<THRESHOLDS[-1]),
      'events_by_absorber_per_b':{name:float(values[:,g,:,0].sum()) for g,name in enumerate(CATEGORIES)},
      'energy_by_absorber_per_b':{name:float(values[:,g,:,1].sum()) for g,name in enumerate(CATEGORIES)},
      'FS_high_energy_table_model':'NOT_APPLIED: no original 2D calibration tables available',
      'source_width':'16 point pair spectrum, 4 hazard substeps in ln(a)',
      'no_new_IVP':0,
   }
   if select is None and top is None:
    expected=oldres['physical_outputs']
    phys['reference_PR297_absorbed_primary']=float(expected['all_conditional_photo_events_per_baryon_upper'])
    phys['reference_PR297_electron_energy']=float(expected['all_conditional_primary_e_eV_per_baryon_upper'])
    phys['photon_count_relative_to_PR297']=float(phys['absorbed_primary_photo_events_per_b']/phys['reference_PR297_absorbed_primary']-1)
    phys['electron_energy_relative_to_PR297']=float(phys['primary_electron_eV_per_b']/phys['reference_PR297_electron_energy']-1)
   if output:
    dest=ROOT/'results';dest.mkdir(parents=True,exist_ok=True)
    agg.to_csv(dest/'FS2010_LOW_E_THRESHOLD_ARRIVAL_192.csv',float_format='%.17g',index=False)
    pd.DataFrame(rows).to_csv(dest/'FS2010_LOW_E_THRESHOLD_KERNEL_18528.csv',float_format='%.17g',index=False)
    (dest/'RESULT.json').write_text(json.dumps({'schema':'REI_F4_FS2010_THRESHOLD_RESOLVED_FIRST_FLIGHT_V1',
       'source_papers':['Ferrett1987','Langer1991','FurlanettoStoever2010'],
       'physics':phys,'qualification':{'LiII_1S_yield':'CONDITIONAL_FERRETT_UPPER','source_operator':'BASS_NATIVE_K_TO_LAB_N2PLUSN3_UNBOUND','R6_C9_distinct_author':'NOT_RUN','F4':'PARTIAL','production':'HOLD','canonical_delta':0,'WORKING_DAG':'33/88','CENTRAL_DAG':'28/88','FAST_DAG':'4/7','FS_deposition':'SUB10p2_ONLY_UNDER_FS2010_IDEALIZATION','real_IGM_heat':'UNBOUND','new_IVP':0}},indent=2,sort_keys=True)+'\n')
   return agg,pd.DataFrame(rows),phys

if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--smoke',type=int);pa.add_argument('--top',type=int);args=pa.parse_args()
 select=None if args.smoke is None else [args.smoke]
 a,b,v=run(args.smoke is None and args.top is None,select=select,top=args.top,progress=True)
 print('ROW_COUNTS',len(a),len(b)); print(json.dumps(v,indent=2))
