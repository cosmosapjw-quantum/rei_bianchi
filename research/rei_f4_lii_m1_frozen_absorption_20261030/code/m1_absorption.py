#!/usr/bin/env python3
"""Original BASS21 193-epoch 59.0207 eV M1 line local photoabsorption.

This is a source-preserving static local diagnostic, NOT an IVP, cosmological
radiative transfer, M1 yield prediction, or deposited gas heating calculation.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, pathlib, tempfile, zipfile
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
SHA_PR278='df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db'
SHA_PR280='fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91'
SHA_TRAJECTORY='37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
ENERGY=59.020723673157676
C_SI=299792458.0
PC_SI=3.0856775814913673e16
CAT_GROUPS={
 'H_I':(1,3,5),
 'He_I':(7,10),
 'He_II':(8,11),
 'Li_I':(13,17),
}

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def _extract(archive, root):
 with zipfile.ZipFile(archive) as z:
  bad=z.testzip()
  if bad:raise ValueError('ZIP_CRC:'+bad)
  for n in z.namelist():
   p=pathlib.PurePosixPath(n)
   if p.is_absolute() or '..' in p.parts:raise ValueError('ZIP_PATH_TRAVERSAL')
  z.extractall(root)

def load_sources():
 a=ROOT/'source/REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip'
 b=ROOT/'source/REI_F4_LI1S_RADIATIVE_PHOTON_20261030_FULL.zip'
 if sha(a)!=SHA_PR278 or sha(b)!=SHA_PR280:raise ValueError('SOURCE_ZIP_SHA')
 with tempfile.TemporaryDirectory() as t:
  p=pathlib.Path(t);_extract(a,p/'pr278');_extract(b,p/'pr280')
  q=p/'pr278'
  if sha(q/'trajectory.npz')!=SHA_TRAJECTORY: raise ValueError('TRAJECTORY_SHA')
  spec=importlib.util.spec_from_file_location('frozen_native_bass_rate_loader',q/'code/native_full_rate.py')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  mod.source_manifest_check();net=mod.new_native_network()
  with np.load(q/'trajectory.npz',allow_pickle=False) as v:
   arrays={k:v[k].copy() for k in ('z','x','Y','diagnostics','diagnostic_names')}
  pr=p/'pr280/REI_F4_LI1S_RADIATIVE_PHOTON_20261030'
  m1=json.loads((pr/'results/RESULT.json').read_text())
  with (pr/'results/LI1S_PHOTON_CAPACITY_EPOCH_193.csv').open(newline='') as h:
   cap=list(csv.DictReader(h))
  # Do not return a source state that depends on the extracted temp directory.
  c=net.photo_cross_sections([ENERGY])[0][:,0].copy()
  return arrays, dict(names=list(net.names),A=net.A.copy(),q=net.q.copy(),transitions_eV=net.transition_energy_eV.copy(),sigma_m2=c),m1,cap

def compute():
 v,src,pr280,cap=load_sources()
 assert pr280['energy_eV']['LiII_triplet_M1']==ENERGY
 assert len(cap)==len(v['z'])==193 and v['Y'].shape==(193,21)
 names=list(v['diagnostic_names']); H=v['diagnostics'][:,names.index('H')];nb=v['diagnostics'][:,names.index('nb_m3')]
 Y=v['Y'];sigma=src['sigma_m2'];threshold=src['transitions_eV']; kspecies=nb[:,None]*Y*sigma[None,:]
 kappa=kspecies.sum(axis=1)
 if np.any(kappa<=0) or np.any(H<=0) or np.any(nb<=0):raise ValueError('POSITIVE_LOCAL_DENSITY_REQUIRED')
 cat=np.column_stack([kspecies[:,ids].sum(axis=1) for ids in CAT_GROUPS.values()]); cats=list(CAT_GROUPS)
 if not np.allclose(cat.sum(axis=1),kappa,rtol=1e-15,atol=1e-45):raise ValueError('UNMAPPED_CHANNEL')
 frac=cat/kappa[:,None];prob=kspecies/kappa[:,None]
 primary_energy=ENERGY-threshold; active=sigma>0
 if np.any(primary_energy[active]<0):raise AssertionError('LINE_BELOW_ACTIVE_THRESHOLD')
 energy_primary=(kspecies[:,active]*primary_energy[active]).sum(axis=1)/kappa
 energy_binding=(kspecies[:,active]*threshold[active]).sum(axis=1)/kappa
 if np.max(np.abs((energy_primary+energy_binding)-ENERGY))>1e-12:raise AssertionError('PHOTO_ENERGY_LEDGER')
 mfp=1/kappa;times=mfp/C_SI;tauh=C_SI*kappa/H
 # Frozen constant-condition one-Hubble-length diagnostic only.
 onespan_prob=-np.expm1(-tauh)
 result=[]; details=[]
 for i,(z,x) in enumerate(zip(v['z'],v['x'])):
  if abs(float(cap[i]['z'])-float(z))>1e-11:raise ValueError('PR280_CLOCK_MISMATCH')
  rk=float(cap[i]['K_events_per_baryon_s']);rf=float(cap[i]['triplet_forced_events_per_baryon_s'])
  if not (0<=rf<=rk):raise ValueError('SOURCE_BRANCH_RATE_INVALID')
  row=dict(epoch=i,z=float(z),x=float(x),H_s=float(H[i]),n_b_m3=float(nb[i]),line_energy_eV=ENERGY,
    kappa_abs_m_inv=float(kappa[i]),absorption_hazard_s_inv=float(C_SI*kappa[i]),
    photo_mean_free_path_proper_pc=float(mfp[i]/PC_SI),photo_absorption_time_s=float(times[i]),
    tau_one_frozen_Hubble_length=float(tauh[i]),one_frozen_Hubble_length_absorption_probability=float(onespan_prob[i]),
    mean_primary_photoelectron_eV=float(energy_primary[i]),mean_ion_binding_eV=float(energy_binding[i]),
    pr280_K_event_rate_baryon_inv_s=rk,pr280_triplet_accessible_rate_baryon_inv_s=rf,
    conditional_M1_capacity_upper_baryon_inv_s=rk)
  for j,c in enumerate(cats):row[f'kappa_{c}_m_inv']=float(cat[i,j]);row[f'first_photoabsorption_{c}_fraction']=float(frac[i,j])
  result.append(row)
  for s,name in enumerate(src['names']):details.append(dict(epoch=i,z=float(z),species=name,Y_baryon=float(Y[i,s]),
              sigma_m2=float(sigma[s]),kappa_m_inv=float(kspecies[i,s]),
              conditional_first_photoabsorption_fraction=float(prob[i,s]),source_threshold_eV=float(threshold[s])))
 return result,details,dict(source_energy_eV=ENERGY,sigma_m2=dict(zip(src['names'],map(float,sigma))),
       epochs=193,species_rows=len(details),photo_groups=cats,source_shas=dict(PR278=SHA_PR278,PR280=SHA_PR280,trajectory=SHA_TRAJECTORY))

def write():
 r,d,meta=compute();out=ROOT/'results';out.mkdir(exist_ok=True)
 for name,rows in [('M1_ABSORPTION_EPOCH_193.csv',r),('M1_ABSORPTION_SPECIES_4053.csv',d)]:
  with (out/name).open('w',newline='') as f:
   w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
 def ext(field):
  x=np.array([r0[field] for r0 in r]);idx=int(np.argmax(x));mi=int(np.argmin(x))
  return dict(min=float(x[mi]),z_min=r[mi]['z'],max=float(x[idx]),z_max=r[idx]['z'])
 keys=['kappa_abs_m_inv','photo_mean_free_path_proper_pc','tau_one_frozen_Hubble_length',
       'mean_primary_photoelectron_eV','mean_ion_binding_eV',
       'first_photoabsorption_H_I_fraction','first_photoabsorption_He_I_fraction','first_photoabsorption_He_II_fraction',
       'first_photoabsorption_Li_I_fraction']
 outobj={**meta,'schema':'REI_F4_LII_M1_BASS21_FROZEN_ABSORPTION_V1',
     'scientific_scope':'source-native local frozen photoabsorption only, not line yield, gas heat, or cosmological RT',
     'new_IVPs':0,'summary':{k:ext(k) for k in keys},
     'first_epoch':r[0], 'last_epoch':r[-1], 'source_verification':'SHA guarded two full source archives',
     'working_DAG':'33/88','central_DAG':'28/88','physical_fast':'4/7','canonical_delta':0,
     'F4':'PARTIAL','L4_ready':False}
 (out/'RESULTS.json').write_text(json.dumps(outobj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
 print(json.dumps({'epochs':len(r),'species_rows':len(d),'tauH_first':r[0]['tau_one_frozen_Hubble_length'],
                     'tauH_last':r[-1]['tau_one_frozen_Hubble_length'],
                     'HeII_late':r[-1]['first_photoabsorption_He_II_fraction'],
                     'primary_early':r[0]['mean_primary_photoelectron_eV'],
                     'primary_late':r[-1]['mean_primary_photoelectron_eV']},indent=2))
if __name__=='__main__':write()
