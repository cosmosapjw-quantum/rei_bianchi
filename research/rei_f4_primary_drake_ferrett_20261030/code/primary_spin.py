#!/usr/bin/env python3
"""Source-first 1969 Li II 2E1 and 1987 Li I 1s spin partial cross-sections on BASS193.

Rigor: 1987 σ(1S+3P) is *unresolved*, so is only an upper bound on 1S.
Absolute K-shell source replacement is CONDITIONAL, NOT owner-native without closure.
Uses only Ferrett energy 75--99 eV; n3 resolved normalization only >=80 eV.
No IVP, no interpolation outside the experimentally covered energy interval.
"""
import csv, io, json, hashlib, pathlib, zipfile
import numpy as np
from scipy.integrate import simpson
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASS=ROOT/'source/PR280_FULL.zip'
CASUAL=ROOT/'source/PR287_FULL.zip'
PDFS={
 'drake_original':'32_original_1969.pdf',
 'drake_typeset':'32_typeset_1969.pdf',
 'ferrett1987':'Ferrett1987_PRA36_3172.pdf',
 'langer1991':'Langer1991_PRA43_1652.pdf',
}
SHA={
 'PR280':'fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91',
 'PR287':'cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef',
 'drake_original':'213a9a620dbb9b5cc63ccdab246e6564018cc3262629d13303879ac133b59b95',
 'drake_typeset':'0f47cea95cc6dfe20f94cac3e35cea77c7e1072ac4d64f34a6871508c69288eb',
 'ferrett1987':'37b1b988798aee21b14d1d1cb018b8b1052da130e094c60f04ef1b347ea48711',
 'langer1991':'b92587d22c8698c4f46bd9069ffe5fe1f3cdd170da253653ada16f770d73fd02',
}
DR1969=np.array([0,379,1110,1810,2420,2940,3380,3740,4060,4320,4540,4730,4880,5020,5130,5220,5290,5350,5380,5410,5420],dtype=float)
DR_Y=np.linspace(0,.5,21)
# Ferrett et al., PRA 36, p.3176 Table IV (print verified). sigma in Mb.
# n3 entries at 75 and 77.5 eV were not reported, must remain None.
# sigma(1S+3P) is *unresolved*: is NOT sigma(1S) alone.
FERRETT=[
# E, n2, stat n2, n3, stat n3, 3S, stat 3S, unresolved 1S+3P, stat unresolved
(75.,1.99,.08,None,None,1.21,.11,.69,.07),
(77.5,1.90,.08,None,None,1.19,.10,.60,.05),
(80.,1.86,.02,.32,.02,1.15,.07,.63,.05),
(82.5,1.67,.02,.31,.02,1.05,.07,.54,.04),
(85.,1.58,.01,.30,.01,.99,.07,.53,.04),
(87.,1.45,.01,.30,.01,.89,.05,.51,.03),
(87.5,1.43,.01,.29,.01,.92,.06,.46,.04),
(90.,1.41,.01,.29,.01,.89,.06,.47,.04),
(92.5,1.30,.01,.31,.01,.79,.04,.46,.03),
(93.,1.29,.01,.27,.01,.81,.09,.45,.06),
(95.,1.28,.01,.28,.01,.80,.09,.44,.06),
(97.,1.18,.01,.27,.01,.74,.08,.41,.05),
(99.,1.09,.01,.26,.01,.68,.08,.38,.05),
]
# PR280 original R1 NIST source energy, not Ferrett historical level E(1S)=66.15 eV
# or Langer level 66.31 eV; leave all three identities explicit.
E_M1=59.020723673157676
E_2E1=60.922559447552004
M1_TRIPLET_LIFETIME_S=52.2
DR_TRIPLET_2PHOTON_SINV=1.50e-6 # Drake (1969) Table III, Li II
BR_M1=1/(1+M1_TRIPLET_LIFETIME_S*DR_TRIPLET_2PHOTON_SINV)


def h(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def verify_sources():
 assert h(BASS)==SHA['PR280'],'PR280_IMMUTABLE_SHA_FAIL'
 assert h(CASUAL)==SHA['PR287'],'PR287_IMMUTABLE_SHA_FAIL'
 for k,n in PDFS.items():
  assert h(ROOT/'source'/n)==SHA[k],f'ORIGINAL_PDF_SHA_FAIL:{k}'
 with zipfile.ZipFile(CASUAL) as z:
  assert z.testzip() is None
  assert z.read('REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/source/PR284_FULL.zip')
 with zipfile.ZipFile(BASS) as z:
  assert z.testzip() is None
  base='REI_F4_LI1S_RADIATIVE_PHOTON_20261030/'
  b=list(csv.DictReader(io.StringIO(z.read(base+'results/LI1S_VACUUM_PHOTON_CAPACITY_8492.csv').decode())))
  e=list(csv.DictReader(io.StringIO(z.read(base+'results/LI1S_PHOTON_CAPACITY_EPOCH_193.csv').decode())))
 assert len(b)==8492 and len(e)==193
 # Get the owner-native 21-value spectrum solely from the frozen nested source chain.
 # PR287 embeds exact PR284; PR284 embeds exact PR283; no container-absolute path.
 with zipfile.ZipFile(CASUAL) as z:
  pr284=z.read('REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/source/PR284_FULL.zip')
 assert hashlib.sha256(pr284).hexdigest()=='fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9'
 with zipfile.ZipFile(io.BytesIO(pr284)) as z:
  pr283=z.read('REI_F4_LII_2E1_PAIR_CORRELATED_20261030/source/PR283_FULL.zip')
 assert hashlib.sha256(pr283).hexdigest()=='91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a'
 with zipfile.ZipFile(io.BytesIO(pr283)) as z:
  txt=z.read('REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030/code/two_e1_source.py').decode()
 import ast,re
 m=re.search(r'A_TAB\s*=\s*np\.array\(\s*\[(.*?)\]\s*,\s*float\s*\)',txt,re.S)
 assert m is not None,'OWNER_21_ORDINATES_NOT_FOUND'
 values=np.array(ast.literal_eval('['+m.group(1)+']'),dtype=float)
 assert np.array_equal(values,DR1969),'ORIGINAL_1969_PRINTED_VS_PUBLISHED_PR283_SOURCE_MISMATCH'
 return b,e


def lab_points():
 out=[]
 for a in FERRETT:
  E,n2,dn2,n3,dn3,t,dt,agg,dagg=a
  assert n2>=t+agg-1e-12
  row=dict(energy_eV=E,sigma_n2_Mb=n2,stat_sigma_n2_Mb=dn2,
    sigma_n3_Mb=n3,stat_sigma_n3_Mb=dn3,sigma_1s2s_3S_Mb=t,stat_sigma_3S_Mb=dt,
    sigma_unresolved_1S_plus_3P_Mb=agg,stat_unresolved_Mb=dagg,
    sigma_1s2p_1P_residual_Mb=n2-t-agg,
    triplet_3S_fraction_within_n2=t/n2,
    singlet_1S_fraction_max_within_n2=agg/n2,
    triplet_3S_fraction_within_n2plusn3=t/(n2+n3) if n3 is not None else None,
    singlet_1S_fraction_max_within_n2plusn3=agg/(n2+n3) if n3 is not None else None,
    experimental_cross_section_absolute_scale_uncertainty_fraction=.20,
    source='Ferrett1987_PRA36_p3176_TableIV',
    warning='unresolved_1S_plus_3P_is_not_singlet_yield; n2plusn3_excludes_n4_higher_and_valence')
  out.append(row)
 return out


def interp_rows(E,lab):
  """Interpolate measured sigma values, never extrapolate or invent n3 below 80 eV."""
  if not 75<=E<=99: return None
  energies=np.array([r['energy_eV'] for r in lab])
  out={'energy_eV':E}
  for key in ['sigma_n2_Mb','sigma_1s2s_3S_Mb','sigma_unresolved_1S_plus_3P_Mb']:
   out[key]=float(np.interp(E,energies,[r[key] for r in lab]))
  if E>=80:
   subset=[r for r in lab if r['energy_eV']>=80]
   out['sigma_n3_Mb']=float(np.interp(E,[r['energy_eV'] for r in subset],[r['sigma_n3_Mb'] for r in subset]))
  else:out['sigma_n3_Mb']=None
  out['sigma_other_n2_1P_Mb']=out['sigma_n2_Mb']-out['sigma_1s2s_3S_Mb']-out['sigma_unresolved_1S_plus_3P_Mb']
  if out['sigma_other_n2_1P_Mb'] < -1e-10: raise ValueError('STATE_CHANNEL_NEGATIVE')
  out['f3S_n2']=out['sigma_1s2s_3S_Mb']/out['sigma_n2_Mb']
  out['f1S_n2_UB']=out['sigma_unresolved_1S_plus_3P_Mb']/out['sigma_n2_Mb']
  if out['sigma_n3_Mb'] is not None:
   denom=out['sigma_n2_Mb']+out['sigma_n3_Mb']
   out['f3S_n2n3']=out['sigma_1s2s_3S_Mb']/denom
   out['f1S_n2n3_UB']=out['sigma_unresolved_1S_plus_3P_Mb']/denom
  else:
   out['f3S_n2n3']=None;out['f1S_n2n3_UB']=None
  return out


def compute():
  B,EPOCHS=verify_sources()
  labs=lab_points()
  H=np.array([float(r['H_s']) for r in EPOCHS]); x=np.array([float(r['x']) for r in EPOCHS]); z=np.array([float(r['z']) for r in EPOCHS]);
  assert np.all(np.diff(x)>0) and np.all(H>0)
  seen=set(); measured=[];matched_bins=set(); all_bins=[]
  rsum={k:np.zeros(193) for k in ['K_all','K_75_99','K_80_99','triplet3S_n2only','singlet1S_upper_n2only','triplet3S_n2n3','singlet1S_upper_n2n3','M1_photons_n2n3','2E1_photon_pairs_upper_n2n3']}
  for r in B:
   epoch=int(r['epoch']);e=float(r['photon_eV']);k=float(r['native_K_events_per_baryon_s']);iso=r['isotope'];idx=int(r['bin_index']);
   assert r['allowed_singlet_2E1']=='True' or e<66.315
   assert epoch>=0 and epoch<193 and k>=0
   rsum['K_all'][epoch]+=k
   f=interp_rows(e,labs); status='MEASURED_75_99' if f is not None else 'OUTSIDE_EXPERIMENT_75_99'
   all_bins.append(dict(epoch=epoch,z=float(r['z']),isotope=iso,bin_index=idx,photon_eV=e,original_BASS_K_per_baryon_s=k,
                        experimental_match=status,
                        measured_n2n3_applicable=(f is not None and e>=80),original_DAG='working33/88|central28/88|fast4/7'))
   if f is None:continue
   matched_bins.add(round(e,12));rsum['K_75_99'][epoch]+=k
   if e>=80:rsum['K_80_99'][epoch]+=k
   K3S_n2=k*f['f3S_n2'];K1S_n2_UB=k*f['f1S_n2_UB']
   rsum['triplet3S_n2only'][epoch]+=K3S_n2;rsum['singlet1S_upper_n2only'][epoch]+=K1S_n2_UB
   n2n3_ok=(f['f3S_n2n3'] is not None)
   T=k*f['f3S_n2n3'] if n2n3_ok else None
   SU=k*f['f1S_n2n3_UB'] if n2n3_ok else None
   if n2n3_ok:
    rsum['triplet3S_n2n3'][epoch]+=T
    rsum['singlet1S_upper_n2n3'][epoch]+=SU
    rsum['M1_photons_n2n3'][epoch]+=T*BR_M1
    rsum['2E1_photon_pairs_upper_n2n3'][epoch]+=SU
   measured.append(dict(epoch=epoch,z=float(r['z']),isotope=iso,bin_index=idx,photon_eV=e,
      BASS_native_K_per_baryon_s=k,
      measured_sigma_n2_Mb=f['sigma_n2_Mb'],measured_sigma_n3_Mb=f['sigma_n3_Mb'],
      measured_sigma3S_Mb=f['sigma_1s2s_3S_Mb'],
      measured_sigma1Splus3P_Mb=f['sigma_unresolved_1S_plus_3P_Mb'],
      measured_sigma1P_residual_Mb=f['sigma_other_n2_1P_Mb'],
      ratio3S_given_n2=f['f3S_n2'],singlet_1S_ratio_upper_given_n2=f['f1S_n2_UB'],
      ratio3S_given_n2n3=f['f3S_n2n3'],singlet_1S_ratio_upper_given_n2n3=f['f1S_n2n3_UB'],
      conditional_triplet3S_n2only_per_baryon_s=K3S_n2,
      conditional_singlet1S_n2only_upper_per_baryon_s=K1S_n2_UB,
      conditional_triplet3S_n2n3_per_baryon_s=T,
      conditional_singlet1S_n2n3_upper_per_baryon_s=SU,
      conditional_M1_59eV_photons_n2n3_per_baryon_s=(T*BR_M1 if T is not None else None),
      conditional_2E1_photon_pairs_n2n3_upper_per_baryon_s=SU,
      conditional_M1_line_energy_n2n3_eV_per_baryon_s=(T*BR_M1*E_M1 if T is not None else None),
      conditional_2E1_pair_energy_upper_n2n3_eV_per_baryon_s=(SU*E_2E1 if SU is not None else None),
      experimental_status='MEASURED_INTERPOLATION_80_99_N2_PLUS_N3' if n2n3_ok else 'N2_ONLY_N3_NOT_REPORTED',
      physical_rate_admission='CONDITIONAL_NATIVE_K_EQUALS_EXPERIMENTAL_SUBSPACE_N2_OR_N2N3;NOT_REI_PHYSICAL_OWNER'))
  assert len(all_bins)==8492 and len(measured)==193*2*6 and len(matched_bins)==6
  for i,old in enumerate(EPOCHS):
   assert np.isclose(rsum['K_all'][i],float(old['K_events_per_baryon_s']),rtol=4e-14,atol=1e-64)
  epochs=[]
  for i in range(193):
   line=dict(epoch=i,z=float(z[i]),x=float(x[i]),H_s=float(H[i]),original_DAG='working33/88|central28/88|fast4/7',new_IVPs=0)
   line.update({k+'_per_baryon_s':float(v[i]) for k,v in rsum.items()})
   epochs.append(line)
  integ={key:float(simpson(arr/H,x=x)) for key,arr in rsum.items()}
  integral_sha_tab=float(np.trapezoid(DR1969,DR_Y))
  assert abs(integral_sha_tab-1945.475)<1e-9
  summary={'schema':'REI_F4_PRIMARY_DRAKE_FERRETT_20261030_V1',
   'source':{'drake_original_sha256':SHA['drake_original'],'drake_typeset_sha256':SHA['drake_typeset'],'ferrett1987_sha256':SHA['ferrett1987'],'langer1991_sha256':SHA['langer1991'],'PR287_immutable_sha256':SHA['PR287'],'PR280_immutable_sha256':SHA['PR280'],'BASS_owner_commit':'cc602e209e7deeb511ab2a1f3b2268d55206c43c'},
   'Drake1969':{'visually_verified_tableII_LiII_points':'21/21','table_integrated_pair_rate_s_inv':integral_sha_tab,'original_printed_rounded_rate_s_inv':1950.0,'original_tableIII_triplet_twophoton_rate_s_inv':DR_TRIPLET_2PHOTON_SINV},
   'Ferrett1987':{'measured_energies_points':len(labs),'sigma_stat_err_separate_from_20pct_absolute_scale':True,'n2_plus_n3_measured_min_energy_eV':80.,'n2_only_measured_min_energy_eV':75.,'max_energy_eV':99.,'unresolved_1S_plus_3P_is_not_singlet_yield':True,'triplet_3S_M1_competitive_2E1_branch':BR_M1,'mainline_1S_bind_1987_eV':66.15,'mainline_1S_bind_1991_eV':66.31,'NIST_BASS_source_eV':5.391714996+E_2E1},
   'data':{'source_original_event_rows':len(all_bins),'source_matched_event_rows':len(measured),'source_epoch_rows':len(epochs),'measured_native_energy_bins':sorted(matched_bins),'source_original_energy_bins_total':22},
   'integrated_conditional':integ,
   'admission':{'measured_lab_absolute_sections':'LITERATURE_SUPPORTED_VISUAL_13_ROWS','LiII_2E1_ordinates':'LITERATURE_SUPPORTED_VISUAL_21_ROWS','native_BASS_event_count':'SOURCE_OWNED','K_scaled_partial_emission':'CONDITIONAL_ON_K_SUBSPACE_OWNER_UNVERIFIED','real_singlet_production':'UNRESOLVED_1S_PLUS_3P','n2n3_less_than_80eV':'NOT_MEASURED','outside_75_99eV':'NOT_MEASURED','actual_gas_heat':'NOT_RUN','CMB_tau':'NOT_RUN'},
   'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0,'F4':'PARTIAL','L4_ready':False,'new_IVPs':0,'PRODUCTION':'HOLD'}}
  return labs,measured,epochs,all_bins,summary


def dump_csv(path,rows):
 with path.open('w',newline='',encoding='utf8') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)

def main():
 a,b,c,d,e=compute()
 R=ROOT/'results';R.mkdir(exist_ok=True)
 for name,rows in [('LAB_FERRETT_TABLEIV_13.csv',a),('BASS_MEASURED_WINDOW_2316.csv',b),('BASS_EPOCH_SPIN_193.csv',c),('BASS_ALL_EVENTS_COVERAGE_8492.csv',d)]:dump_csv(R/name,rows)
 dump_csv(R/'DRAKE_LII_2E1_VERIFIED_21.csv',[{'y':float(y),'dA_dy_s_inv':float(A),'source':'Drake_Victor_Dalgarno_1969_original_p29_TableII','visual':'PRINTED_MATCH'} for y,A in zip(DR_Y,DR1969)])
 (R/'RESULTS.json').write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print(json.dumps({'source_verified':e['Drake1969'],'rows':e['data'],'integrated':e['integrated_conditional']},indent=2))
if __name__=='__main__':main()
