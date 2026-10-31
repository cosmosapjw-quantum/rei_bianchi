#!/usr/bin/env python3
"""A source-bounded first-generation electron deposition crosswalk.

Strictly frozen PR302/303 physical input, FS2010 author's original E_e,x_i tables.
No new cosmic IVP, no reconstructed within-band electron spectrum, no added source,
no native isotope F/J. Results are conditional one-parameter FS surrogate bounds.
"""
from __future__ import annotations
import json, hashlib, math
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source_tar'/'x_int_tables'
BASE=ROOT/'input'
OUT=ROOT/'results'
OUT.mkdir(parents=True,exist_ok=True)
XI = np.array([1e-4, 2.318e-4, 4.677e-4, 1e-3,2.318e-3,4.677e-3,
               1e-2,2.318e-2,4.677e-2,0.1,0.5,0.9,0.99,0.999])
NAMES=['log_xi_-4.0.dat','log_xi_-3.6.dat','log_xi_-3.3.dat',
       'log_xi_-3.0.dat','log_xi_-2.6.dat','log_xi_-2.3.dat',
       'log_xi_-2.0.dat','log_xi_-1.6.dat','log_xi_-1.3.dat',
       'log_xi_-1.0.dat','xi_0.500.dat','xi_0.900.dat',
       'xi_0.990.dat','xi_0.999.dat']
COLUMNS = ['fion','fheat','fexc','nlya','nion_HI','nion_HeI','nion_HeII']
# In source, [E, fion, fheat, fexc, nlya, nion_HI, nion_HeI, nion_HeII, fit_heat]
BANDS = ['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
SPECIES=['H_I','He_I','He_II','Li_I']
E_PAIR=60.922559447552  # frozen original Li II two-photon transition; upper bound only
LIMITS=[(0.,10.2),(10.2,13.598434599702),(13.598434599702,24.587389011),
        (24.587389011,54.41776),(54.41776,E_PAIR)]
EV_ERG=1.602176634e-12
SOURCE_EXPECT={
 'PUBLIC_results_FULL193_ARRIVAL_192.csv':'155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df',
 'PUBLIC_results_FULL193_KERNEL_18528.csv':'d7ca818ce55835f8c38408e4c575f42d6529d6e225aab346fad76709b4354538',
 'PUBLIC_results_FULL193_HHE_TERMINAL_THERMAL_192.csv':'292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6',
 'BASS193_FS2010_SPECIES_COMPAT_192.csv':'dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09'
}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class FS2010:
 def __init__(self):
  grid=[]; energy=None; self.meta=[]
  for j,name in enumerate(NAMES):
   lines=(SRC/name).read_text().splitlines()
   metadata=[float(x) for x in lines[1].split()]
   self.meta.append(dict(file=name, xi=float(XI[j]), neutral_H=metadata[0],neutral_He=metadata[1],HeII=metadata[2],z=metadata[3],T=metadata[4]))
   table=np.loadtxt(lines[3:])
   assert table.shape==(258,9), (name,table.shape)
   if energy is None: energy=table[:,0]
   else: assert np.array_equal(energy,table[:,0]), name
   grid.append(table[:,1:8])
  self.E=energy
  self.data=np.stack(grid,axis=0)
  assert self.data.shape==(14,258,7)
  assert np.all(np.diff(self.E)>0)
  assert self.E[0]==10 and self.E[-1]>9900
  self.closure_max=float(np.max(abs(self.data[:,:,0:3].sum(axis=2)-1)))
  assert self.closure_max < 5e-5, self.closure_max
  assert self.data.min()>-5e-5

 def interp(self, energies, xis):
  """Piecewise bilinear native author's linear-E, linear-x interpolation.
  No clipping out-of-range input. For E<10.2, explicit FS terminal branch.
  Returns shape (7,) or (...,7). Callers own source-model assumptions.
  """
  E,X=np.broadcast_arrays(np.asarray(energies,float),np.asarray(xis,float))
  scalar=(E.ndim==0)
  if scalar: E=E.reshape(1); X=X.reshape(1)
  if np.any(~np.isfinite(E)|~np.isfinite(X)|(E<0)|(E>self.E[-1])|(X<XI[0])|(X>XI[-1])):
   raise ValueError('FS2010_INPUT_OUTSIDE_DECLARED_DOMAIN')
  out=np.zeros(E.shape+(7,),dtype=float)
  low=E<10.2
  out[low,1]=1.
  high=~low
  if not np.any(high): return out[0] if scalar else out
  e=E[high];x=X[high]
  ie=np.clip(np.searchsorted(self.E,e,side='right')-1,0,len(self.E)-2)
  ix=np.clip(np.searchsorted(XI,x,side='right')-1,0,len(XI)-2)
  u=(e-self.E[ie])/(self.E[ie+1]-self.E[ie])
  v=(x-XI[ix])/(XI[ix+1]-XI[ix])
  A=self.data[ix,ie];B=self.data[ix,ie+1]
  C=self.data[ix+1,ie];D=self.data[ix+1,ie+1]
  out[high]=((1-v)[:,None]*((1-u)[:,None]*A+u[:,None]*B)
             +v[:,None]*((1-u)[:,None]*C+u[:,None]*D))
  return out[0] if scalar else out

 def extrema(self, lo,hi,xa,xb):
  """Exact min/max of piecewise bilinear interpolation in rectangle.
  The extrema occur on grid-segment corners, including cut endpoints.
  For E below 10.2, exact terminal rule is used separately.
  """
  if lo<10.2-1e-12: raise ValueError('TERMINAL_BRANCH_MUST_BE_SEPARATE')
  if lo>hi or xa>xb or xa<XI[0] or xb>XI[-1]:raise ValueError('INVALID_RECTANGLE')
  es=np.concatenate(([lo],self.E[(self.E>lo)&(self.E<hi)],[hi]))
  xs=np.concatenate(([xa],XI[(XI>xa)&(XI<xb)],[xb]))
  E,X=np.meshgrid(es,xs,indexing='xy')
  y=self.interp(E,X).reshape(-1,7)
  return np.min(y,axis=0), np.max(y,axis=0)

def run():
 for f,digest in SOURCE_EXPECT.items():
  assert sha(BASE/f)==digest, ('BYTE_IDENTITY_MISMATCH',f)
 # The original user-supplied archive is byte-locked, not inferred from URL alone.
 assert sha(ROOT/'source'/'elec_interp.tar')=='e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101'
 fs=FS2010()
 arr=pd.read_csv(BASE/'PUBLIC_results_FULL193_ARRIVAL_192.csv')
 kernel=pd.read_csv(BASE/'PUBLIC_results_FULL193_KERNEL_18528.csv')
 compat=pd.read_csv(BASE/'BASS193_FS2010_SPECIES_COMPAT_192.csv')
 thermal=pd.read_csv(BASE/'PUBLIC_results_FULL193_HHE_TERMINAL_THERMAL_192.csv')
 assert (len(arr),len(kernel),len(compat),len(thermal))==(192,18528,192,192)
 assert arr.arrival_interval.tolist()==compat.arrival_interval.tolist()==thermal.arrival_interval.tolist()==list(range(192))
 assert len(kernel.drop_duplicates(['emission_epoch','arrival_interval']))==18528
 assert kernel['emission_epoch'].min()==0 and kernel['emission_epoch'].max()==191
 assert max(abs(arr.z_low.values-compat.z_end.values))<1e-12
 assert max(abs(arr.z_low.values-thermal.z_low.values))<1e-12
 assert np.all(compat.xHII_end.between(0,1))
 assert np.all(thermal.proper_interval_s>0)
 # Independently reproduce one canonical sum from the emission-arrival kernel, not re-solving it.
 src=kernel.source_emitted_2E1_pairs_per_b.to_numpy(float)
 check=np.zeros(192)
 for a in SPECIES:
  for band in BANDS:
   c=a+'_'+band+'_primary_e_eV_per_pair'
   np.add.at(check,kernel.arrival_interval.to_numpy(int),src*kernel[c].to_numpy(float))
 assert np.max(abs(check-arr.total_primary_e_eV_per_b.to_numpy(float)))<1e-24
 summary=[]; bands_out=[]
 for j in range(192):
  r=arr.iloc[j]; co=compat.iloc[j]; th=thermal.iloc[j]
  xa,xb=float(min(co.xHII_start,co.xHII_end)),float(max(co.xHII_start,co.xHII_end))
  valid=(xa>=XI[0]) and (xb<=XI[-1])
  primary=float(r.total_primary_e_eV_per_b)
  terminal=float(r.FS_low_e_heat_kinematic_eV_per_b)
  coeffs={k+'_'+d:0. for k in COLUMNS for d in ('lower','upper','moment')}
  Ntot=0.;Etot=0.
  for a in SPECIES:
   for b,(lo,hi) in zip(BANDS,LIMITS):
    count=float(r[f'{a}_{b}_counts_per_b']); kinetic=float(r[f'{a}_{b}_primary_e_eV_per_b'])
    assert count>=-1e-26 and kinetic>=-1e-24
    count=max(0.,count);kinetic=max(0.,kinetic)
    Ntot+=count; Etot+=kinetic
    if count>0:
     ebar=kinetic/count
     assert lo-1e-2<=ebar<=hi+1e-2, (a,b,j,ebar,lo,hi)
    else: ebar=0.
    entry={'arrival_interval':j,'species':a,'energy_band':b,
           'E_min_eV':lo,'E_max_eV':hi,'electron_count_per_b':count,'kinetic_eV_per_b':kinetic,
           'electron_mean_eV':ebar,'xi_start':float(co.xHII_start),'xi_end':float(co.xHII_end),
           'FS_xi_in_native_domain':valid}
    if b=='e0_10p2':
     amin=np.zeros(7);amax=np.zeros(7);amom=np.zeros(7)
     amin[1]=amax[1]=amom[1]=1.
    elif valid:
     amin,amax=fs.extrema(lo,hi,xa,xb)
     amom=fs.interp(max(lo,min(ebar,hi)),float(co.xHII_end))
    else: amin=amax=amom=None
    if amin is not None:
     for ci,k in enumerate(COLUMNS):
      weight= count if k.startswith('n') else kinetic
      for d,value in [('lower',amin[ci]),('upper',amax[ci]),('moment',amom[ci])]:
       coeffs[k+'_'+d]+=weight*value
       entry[k+'_'+d]=weight*value
    bands_out.append(entry)
  assert abs(primary-Etot)<1e-24, (j,primary,Etot)
  assert abs(terminal-sum(float(r[f'{a}_e0_10p2_primary_e_eV_per_b']) for a in SPECIES))<1e-24
  d={'arrival_interval':j,'z_high':float(r.z_high),'z_low':float(r.z_low),
     'proper_interval_s':float(th.proper_interval_s),'xHII_start':float(co.xHII_start),
     'xHII_end':float(co.xHII_end),'xHeII_end':float(co.xHeII_end),
     'xHeIII_end':float(co.xHeIII_end),'electron_pool_projection_defect':float(co.relative_abs_electron_density_projection_defect_end),
     'FS_xi_in_native_domain':valid,'FS_exact_species_valid':bool(co.FS_chemical_exact_at_both_saved_endpoints),
     'primary_kinetic_eV_per_b':primary,'terminal_eV_per_b':terminal,
     'HHe_Cv_erg_per_Href_K':float(th.HHe_Cv_erg_per_Href_K),'nHref_over_nb':float(th.nHref_over_nb)}
  d.update(coeffs)
  if valid:
   for k in COLUMNS:
    assert coeffs[k+'_lower']<=coeffs[k+'_moment']+1e-21,(k,j,'bad min')
    assert coeffs[k+'_moment']<=coeffs[k+'_upper']+1e-21,(k,j,'bad max')
   denom=d['HHe_Cv_erg_per_Href_K']*d['nHref_over_nb']
   for tag in ['lower','upper','moment']:
    v=coeffs['fheat_'+tag]*EV_ERG/denom
    d[f'frozen_FS_thermal_increment_proxy_K_{tag}']=v
    d[f'frozen_FS_thermal_coefficient_K_s_{tag}']=v/d['proper_interval_s']
  summary.append(d)
 df=pd.DataFrame(summary);bd=pd.DataFrame(bands_out)
 df.to_csv(OUT/'FS2010_NATIVE_CROSSWALK_192.csv',index=False,float_format='%.17g')
 bd.to_csv(OUT/'FS2010_BANDS_3840.csv',index=False,float_format='%.17g')
 # Specific physically relevant sample grid points, not 3keV asymptotes.
 diag=[]
 for x in [1e-4,0.001,0.01,0.1,0.5,0.9,0.999]:
  for E in [10,10.2,15,20,30,40,50,60,3000]:
   d=dict(xi=x,Ee_eV=E,**dict(zip(COLUMNS,fs.interp(E,x).reshape(7))))
   diag.append(d)
 pd.DataFrame(diag).to_csv(OUT/'FS2010_ORIGINAL_63_SAMPLES.csv',index=False,float_format='%.17g')
 valid=df.FS_xi_in_native_domain.to_numpy(bool)
 e_total=float(df.primary_kinetic_eV_per_b.sum());terminal_tot=float(df.terminal_eV_per_b.sum())
 valid_e=float(df.loc[valid,'primary_kinetic_eV_per_b'].sum())
 excluded_e=e_total-valid_e
 invalid_terminal=float(df.loc[~valid,'terminal_eV_per_b'].sum())
 vmin=float(df.loc[valid,'fheat_lower'].sum());vmax=float(df.loc[valid,'fheat_upper'].sum())
 vmean=float(df.loc[valid,'fheat_moment'].sum())
 assert vmin<=vmean<=vmax
 # Outside xi domain: only the source-threshold terminal branch is fixed; nonterminal unmodeled.
 whole_lower=vmin+invalid_terminal
 whole_upper=vmax+excluded_e
 assert whole_lower<=whole_upper<=e_total*1.001
 phys=dict(
  status='CONDITIONAL_FS2010_ONE_XI_SURROGATE_NOT_BASS_SPECIES_EXACT',
  rows=192,band_rows=len(bd),kernel_rows=len(kernel),
  fs_grid_rows=int(fs.data.shape[0]*fs.data.shape[1]),
  fs_energy_bounds_eV=[float(fs.E.min()),float(fs.E.max())],fs_xi_bounds=[float(XI.min()),float(XI.max())],
  tabulated_energy_closure_max_abs=float(fs.closure_max),
  source_primary_kinetic_eV_per_b=e_total,
  source_FS_terminal_eV_per_b=terminal_tot,
  source_FS_nonterminal_eV_per_b=e_total-terminal_tot,
  original_FS_valid_rows=int(valid.sum()),
  original_FS_invalid_rows=int((~valid).sum()),
  native_domain_covered_energy_eV_per_b=valid_e,
  native_domain_excluded_energy_eV_per_b=excluded_e,
  native_domain_covered_energy_fraction=valid_e/e_total,
  model_conditional_valid_fheat_eV_per_b=[vmin,vmax],
  model_conditional_valid_fheat_M1_closure_eV_per_b=vmean,
  conservative_total_heat_eV_per_b_with_unmodeled_rows=[whole_lower,whole_upper],
  valid_conditional_fion_eV_per_b=[float(df.loc[valid,'fion_lower'].sum()),float(df.loc[valid,'fion_upper'].sum())],
  valid_conditional_fexc_eV_per_b=[float(df.loc[valid,'fexc_lower'].sum()),float(df.loc[valid,'fexc_upper'].sum())],
  valid_conditional_Lya_count_per_b=[float(df.loc[valid,'nlya_lower'].sum()),float(df.loc[valid,'nlya_upper'].sum())],
  valid_conditional_ionization_counts_per_b={k:[float(df.loc[valid,k+'_lower'].sum()),float(df.loc[valid,k+'_upper'].sum())] for k in ['nion_HI','nion_HeI','nion_HeII']},
  isotope_species_chemistry_exact=int(df.FS_exact_species_valid.sum()),
  species_incompatible_energy_fraction=float(df.loc[~df.FS_exact_species_valid,'primary_kinetic_eV_per_b'].sum()/e_total),
  source_input_shas=SOURCE_EXPECT,original_tar_sha=sha(ROOT/'source'/'elec_interp.tar'),
  caveats=['FS2010 assumes xHII=xHeII and xHeIII=0; xHII is only conditional surrogate',
   'No electron sub-band spectrum, only count and energy moments; bounds valid for tabulated bilinear interpolant, not a Monte Carlo physical uncertainty',
   'xHII out of [1e-4,0.999] excluded except E<10.2 model terminal branch',
   'No native REI17 F/J or production photon source changes; no new IVP',
   'Frozen Cv conversion is a point-source coefficient, not evolved gas temperature'])
 (OUT/'RESULTS.json').write_text(json.dumps(phys,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 (OUT/'FS_RAW_TABLE_METADATA.json').write_text(json.dumps(fs.meta,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in phys.items() if k not in ['source_input_shas','caveats']},indent=2))
 return phys,df,bd,fs

if __name__=='__main__':run()
