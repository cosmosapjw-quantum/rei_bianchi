from pathlib import Path
import csv,io,json,zipfile,hashlib
import numpy as np
from scipy.integrate import simpson
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'
with zipfile.ZipFile(ROOT/'source/PR295_FULL.zip') as z:
 src='REI_F4_REI_HHE_THERMAL_SOURCE_20261030/results/HHE_IGM_THERMAL_193.csv'
 history=list(csv.DictReader(io.StringIO(z.read(src).decode())))
source=list(csv.DictReader((ROOT/'data/native_rei_igm_193_cases.csv').open()))
assert len(source)==193 and len(history)==193
A=lambda rs,k:np.array([float(r[k]) for r in rs],float)
x=A(source,'x'); H=A(source,'H_s'); z=A(source,'z')
nh=A(source,'nHref_cm3'); photo=A(source,'expected_photo_input_erg_cm3_s')
th=A(source,'expected_thermal_erg_cm3_s')
par=np.column_stack([A(source,k) for k in ['Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s']])
maxgap=0.
chi=np.array([13.598434599702,24.587389011,54.41776]); ev=1.602176634e-12
for r in source:
 vals=lambda cols:np.array([float(r[k]) for k in cols])
 nH,nHe=float(r['nHref_cm3']),float(r['nHe4_cm3']);f=vals(['x_HII','x_HeII','x_HeIII']); a=np.array([nH*(1-f[0]),nHe*(1-f[1]-f[2]),nHe*f[1]])
 g=vals(['Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s']);heat=vals(['heat_HI_erg_per_absorber_s','heat_HeI_erg_per_absorber_s','heat_HeII_erg_per_absorber_s'])
 reconstructed=np.sum(a*(g*chi*ev+heat));expect=float(r['expected_photo_input_erg_cm3_s'])
 maxgap=max(maxgap,abs(reconstructed-expect)/max(abs(expect),1e-70))
clock=np.diff(A(source,'proper_elapsed_s'))/(2*np.diff(x)/(H[1:]+H[:-1]))-1
stats={'schema':'REI_F4_NATIVE_IGM193_STATISTICS_V1','source_epochs':len(source),'source_event_rows':579,
 'temperature_range_K':[float(A(source,'T_K').min()),float(A(source,'T_K').max())],
 'maximum_relative_photo_reconstruction_gap':float(maxgap),
 'maximum_relative_proper_clock_midpoint_discrepancy':float(np.max(abs(clock))),
 'maximum_HI_photo_Gamma_over_H':float(np.max(par[:,0]/H)),
 'max_omitted_isotopic_electron_density_cm3':float(A(source,'ne_other_isotopes_cm3').max()),
 'frozen_source_exposures_erg_per_Href':{'photo_input':float(simpson(photo/(nh*H),x=x)),'thermal_micro':float(simpson(th/(nh*H),x=x))},
 'source_event_and_energy_operator':'BASS_REPLACEMENT_ONLY_NOT_ADDITIVE',
 'native_Rust_evaluation':'REFER_TO_EXACT_GITHUB_CI_RECEIPT','REI17_complete':'UNBOUND',
 'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0}}
(R/'SCIENCE_STATS.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,indent=2))
