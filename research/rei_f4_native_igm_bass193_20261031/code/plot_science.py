"""Science plots from genuine locked BASS source histories, NOT an evolved REI history."""
from pathlib import Path
import zipfile,io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
res=ROOT/'results';res.mkdir(exist_ok=True)
case=pd.read_csv(ROOT/'data/native_rei_igm_193_cases.csv')
with zipfile.ZipFile(ROOT/'source/PR295_FULL.zip') as archive:
 old=pd.read_csv(io.BytesIO(archive.read('REI_F4_REI_HHE_THERMAL_SOURCE_20261030/results/HHE_IGM_THERMAL_193.csv')))
z=case.z.to_numpy(float)
def save(name,curves,ylabel,title,log=False):
 fig,ax=plt.subplots(figsize=(8.2,5.2))
 for label,y in curves:
  y=np.asarray(y,dtype=float)
  if log:
   y=np.where(y>0,y,np.nan)
   ax.semilogy(z,y,label=label)
  else:ax.plot(z,y,label=label)
 ax.invert_xaxis();ax.set_xlabel('Redshift z (original saved BASS193)');ax.set_ylabel(ylabel);ax.set_title(title)
 ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(res/name,dpi=190);plt.close(fig)
save('PLOT01_NATIVE_RUST_SOURCE_GAMMA.png',[(k,case[k]/case.H_s) for k in ['Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s']],r'Original BASS photoionization $\Gamma_i/H$','H/He source replacement input to native Rust',True)
save('PLOT02_NATIVE_RHS_TDOT_PORTS.png',[
 (r'REI Rust translated point $\dot T$',case.expected_temperature_dt_K_s),
 ('REI source thermal component',old.REI_HHe_Tdot_thermal_K_s),
 ('REI source expansion component',old.REI_HHe_Tdot_expansion_K_s)],r'$\dot T$ [K s$^{-1}$]','Frozen-state thermal RHS: NOT evolved temperature')
save('PLOT03_ENERGY_REPLACEMENT_MISMATCH.png',[
 (r'REI fine vs BASS rounded $\chi$',np.abs(case.expected_threshold_defect_erg_per_Href_s)),
 ('REI point photo input',old.REI_HHe_photo_input_erg_per_Href_s)],r'Source energy rate [erg / Href / s]','Nonadditive photon source: threshold energy owner defect',True)
save('PLOT04_ELECTRON_BATH_OMITTED.png',[
 ('Electron fraction omission $n_{e,other}/n_{H,ref}$',case.ne_other_isotopes_cm3/case.nHref_cm3),
 ('HII fraction',case.x_HII)],'Number fraction','Common electron pool: omitted isotopes versus HII',True)
save('PLOT05_HHE_NATIVE_VS_BASS_F.png',[
 ('Original BASS HII fraction time derivative',old.native_BASS_HII_fraction_dt_per_s),
 ('REI source-translated HII derivative (native test target)',case.expected_HII_dt_s)],r'$d x_{HII}/dt$ [s$^{-1}$]','Distinct rate owners on identical frozen BASS inputs')
print('plots=5')
