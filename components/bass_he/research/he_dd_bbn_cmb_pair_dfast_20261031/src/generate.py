import csv,json,pathlib,sys,hashlib
from physics import *
import numpy as np
from scipy import constants as c
root=pathlib.Path(__file__).resolve().parents[1]
root.joinpath('data').mkdir(exist_ok=True)
def csvwrite(name, rows):
    with open(root/'data'/name,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(name,len(rows),'rows')
rows=[];pairs=[]
csvwrite('SOURCE_FLRW_IONIZED_STATES_11.csv', [state(z) for z in REDSHIFTS])
for z in REDSHIFTS:
    s=state(z)
    for E in GAMMA_E_MEV:
        rate=bb_pair_rate_s(E,z)
        rows.append(dict(z=z,E_gamma_MeV=E,bb_pair_rate_s_inv=rate,
           gamma_gamma_to_H=rate/s['H_s_inv'],H_s_inv=s['H_s_inv'],
           cmb_T_K=s['T_K'],cmb_kBT_MeV=s['kBT_MeV'],n_cmb_cm3=gg_number_density(z)))
    for E in [170.,220.]:
        g=bb_pair_rate_s(E,z)
        dd=he_dd_rate_per_photon(E,z)
        nuisance = 0.071 if E==170 else 0.13  # Rice 1998 thesis 1-sigma systematic by bin, not full posterior
        pairs.append(dict(z=z,E_gamma_MeV=E,bin_model_sigma_event_nb=(8.29 if E==170 else 4.34),
          sigma_normalization_sys_only_fraction=nuisance,
          gamma_dd_per_photon_s_inv=dd,gamma_gg_per_photon_s_inv=g,
          ratio_dd_to_gg=dd/g if g else float('inf'),
          two_channel_first_interaction_dd_fraction=dd/(dd+g),
          pair_only_fraction_sys_lower=dd*(1-nuisance)/(dd*(1-nuisance)+g),
          pair_only_fraction_sys_upper=dd*(1+nuisance)/(dd*(1+nuisance)+g),
          H_s_inv=s['H_s_inv'],n_alpha_cm3=s['n_alpha_cm3']))
csvwrite('PHYSICAL_CMB_GAMMAGAMMA_PAIR_OPACITY_55.csv',rows)
csvwrite('RICE_BINMODEL_DD_VS_CMB_PAIR_HAZARDS_22.csv',pairs)
stopping=[]
for z in REDSHIFTS:
    for Ed in D_E_MEV:stopping.append(d_electron_drag(Ed,z))
csvwrite('PHYSICAL_FASTD_PLASMA_ELECTRON_DRAG_55.csv',stopping)
from scipy.optimize import brentq
trans=[]
for E in GAMMA_E_MEV:
    for target in (0.1,1.,10.):
        zroot=brentq(lambda z: math.log10(bb_pair_rate_s(E,z)/state(z)['H_s_inv']) - math.log10(target),8.e4,5.e5,xtol=1e-5)
        trans.append(dict(E_gamma_MeV=E,target_Gamma_gg_over_H=target,z_transition=zroot,
             redshift_basis='Planck_CMB_pair_absorption_without_injection',cosmology='PDG_Planck2018_reference'))
csvwrite('PHYSICAL_GAMMA_TRANSPARENCY_TRANSITION_15.csv',trans)
# daughter exact nominal and electron-drag links at 170,220 MeV (mu = 0, +-0.5), 6 D pairs and 12 daughter estimates.
daughters=[]
for Eg in [170.,220.]:
    for mu in [0.,0.5,1.]:
        ka,kb=born_d_pair_kinetics(Eg,mu)
        daughters.append(dict(E_gamma_MeV=Eg,mu_CM=mu,K_plus_MeV=ka,K_minus_MeV=kb,sumK_MeV=ka+kb,Q_MeV=Q_MEV))
csvwrite('MODEL_CONDITIONAL_SOURCE_BIN_BIRTH_6.csv',daughters)
summary={
 'provenance':'source-anchored, model-conditional physical predictions, NOT observed cosmic 150-250 MeV gamma injection and NOT a full fast-D deposition',
 'source_condition':{'CMB_T0_K':T0_K,'n_b0_cm3':N_B0_CM3,'Yp':Y_P,'Omega_m':OM_M,'h':h,'Neff':NEFF,
 'rice_bin_sigma_nb':[8.29,4.34],'source_age':'Planck2018/PDG2025 + Rice2000 final constrained fit PR128'},
 'calculations':{'CMB_Breit_Wheeler_rows':len(rows),'fastD_drag_rows':len(stopping),'dd_vs_gg_rows':len(pairs),'birth_rows':len(daughters),'pair_transparency_transition_rows':len(trans),'background_state_rows':len(REDSHIFTS)},
 'physics_limits': ['CMB Planck isotropic; FLRW homogeneous fully ionized plasma; Z_d=+1',
  'no injected MeV photon source, no self-consistent cosmological nonthermal photon distribution',
  'He4 photo-dd event sigma in each Rice bin is a fitted bin-scale surrogate; not monochromatic measurement',
  'gamma gamma pair production only; competing Compton/BH/other channels and cascades not included',
  'Spitzer Maxwellian electron leading-log friction only, screening variants; not BPS exact NLO nor ions/secondary nuclear/survival/heat',
  'CMB_T and n_e baryon state are adopted standard homogeneous FLRW calibration, not BASS-native anisotropic snapshot',
  'source Rice dissertation user 139-page SHA256: 87fe939659151b09a1653467f1ac2098d971048fa4cf3611b447fce8cc976336; full thesis table 5.2 separate previous source'],
 'DAG_current':{'central':'28/88','HE_physical':'14/18','physical_delta':0,'new_aux':'2/2_scoped'},
 'scientific_slice':[], 'gamma_gamma_crossover_E_z':[{"E_gamma_MeV":v['E_gamma_MeV'],"z_c_Gamma_over_H_1":v['z_transition']} for v in trans if v['target_Gamma_gg_over_H']==1.]}
for z in [2.e5,5.e5,1.e6,2.e6,1.e7]:
    a=next(v for v in pairs if v['z']==z and v['E_gamma_MeV']==220.)
    d=next(v for v in stopping if v['z']==z and v['E_d_MeV']==100.)
    summary['scientific_slice'].append(dict(z=z,Gamma_gg_s=a['gamma_gg_per_photon_s_inv'],Gamma_dd_s=a['gamma_dd_per_photon_s_inv'],P_dd_pair_only=a['two_channel_first_interaction_dd_fraction'],D100_t_stop_over_H=d['t_loss_e_dynamic_over_Hubble']))
(root/'data'/'PHYSICS_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
print('source',json.dumps(summary['scientific_slice'],indent=2))
