import csv,pathlib,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=pathlib.Path(__file__).resolve().parents[1]

def load(name):
 with open(P/'data'/name) as f:return [{k:float(v) for k,v in row.items() if k not in ('redshift_basis','cosmology')} for row in csv.DictReader(f)]

def save(name):
 plt.grid(alpha=0.25)
 plt.tight_layout()
 plt.savefig(P/'figures'/(name+'.png'),dpi=180)
 plt.savefig(P/'figures'/(name+'.svg'))
 plt.close()

a=load('PHYSICAL_CMB_GAMMAGAMMA_PAIR_OPACITY_55.csv')
for energy in [150.,170.,190.,220.,250.]:
 d=[x for x in a if x['E_gamma_MeV']==energy]
 plt.loglog([x['z'] for x in d], [max(x['gamma_gamma_to_H'],1e-32) for x in d],marker='.',label=f'{energy:g} MeV')
plt.axhline(1,linestyle='--')
plt.xlabel('Redshift z, Planck FLRW reference')
plt.ylabel('Gamma(gamma gamma -> e+e-) / H')
plt.title('Actual CMB target: high-energy photon pair opacity')
plt.legend()
save('CMB_GAMMAGAMMA_OPACITY_VS_REDSHIFT')

b=load('PHYSICAL_FASTD_PLASMA_ELECTRON_DRAG_55.csv')
for energy in [50.,75.,100.,125.,150.]:
 d=[x for x in b if x['E_d_MeV']==energy]
 plt.loglog([x['z'] for x in d], [x['t_loss_e_dynamic_over_Hubble'] for x in d],marker='.',label=f'D {energy:g} MeV')
plt.xlabel('Redshift z, fully ionized benchmark')
plt.ylabel('Electron-only Spitzer slowing time / Hubble time')
plt.title('Modelled fast-deuteron electron drag: NOT total heat')
plt.legend()
save('FASTD_ELECTRON_DRAG_TIMESCALE_VS_REDSHIFT')

h=load('RICE_BINMODEL_DD_VS_CMB_PAIR_HAZARDS_22.csv')
for energy in [170.,220.]:
 d=[x for x in h if x['E_gamma_MeV']==energy and x['z']>=1e5]
 plt.loglog([x['z'] for x in d], [x['two_channel_first_interaction_dd_fraction'] for x in d], marker='.',label=f'{energy:g} MeV (Rice bin-model)')
plt.xlabel('Redshift z')
plt.ylabel('P(first dd | only dd, gamma-gamma absorption)')
plt.title('Conditional first-interaction branch; ignores other channels')
plt.legend()
save('RICE_DD_FIRST_INTERACTION_VS_GAMMAGAMMA')

z=load('PHYSICAL_GAMMA_TRANSPARENCY_TRANSITION_15.csv')
for tar in [.1,1.,10.]:
 d=[x for x in z if x['target_Gamma_gg_over_H']==tar]
 plt.plot([x['E_gamma_MeV'] for x in d],[x['z_transition'] for x in d],marker='o',label=f'Gamma/H = {tar:g}')
plt.xlabel('Test-photon energy (MeV)')
plt.ylabel('Instantaneous crossover redshift z')
plt.title('CMB gamma-gamma absorption transition')
plt.legend()
save('CMB_PAIR_OPACITY_CROSSOVER_ENERGY')
print('plots: 4 PNG + 4 SVG')
