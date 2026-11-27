"""Source-explicit nuclear competition tables and three scientific figures (not new measurements)."""
import csv, json, hashlib, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams["svg.hashsalt"] = "BASS_HE_HE_DD_20261031_ALPHA_SOURCE_LOCK"
from alpha_competition import (SOURCES,sigma_cyburt_cm2,sigma_rice_dd_cm2,
                                rates,solve_cascade,state)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'; OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)

def savecsv(n, rows):
    with (OUT/n).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(f'{n}: {len(rows)} rows')

# Published source fit interpretation at multiple nuclear threshold vs high-E energies.
Es=(24,26,28,30,40,70,100,150,170,190,220,248)
xs=[]
for E in Es:
    sr=sigma_rice_dd_cm2(E) if E>=150 else None
    cy={k:sigma_cyburt_cm2(E,k) for k in SOURCES}
    xs.append(dict(E_gamma_MeV=E,**{f'sigma_{k}_cm2':v for k,v in cy.items()},
       sigma_DD_Rice_bin_surrogate_cm2=sr,
       Rice_over_Cyburt_DD_extrap_factor=(sr/cy['dd_cyburt_extrap'] if sr else None),
       source='Cyburt2003_AppendixA_items6-9_analytic_fit;150to250_highE_extrapolation'))
savecsv('SOURCE_CYBURT_ALPHA_CROSS_SECTIONS_12.csv',xs)
zs=(1e4,3e4,1e5,2e5,5e5,1e6)
Eis=(170.,220.,248.)
hazard=[]; rows=[]
for z in zs:
    for E in Eis:
        r=rates(E,z,'rice');H=state(z)['H_s_inv']
        hazard.append(dict(z=z,E_MeV=E,H_s_inv=H,
           **{f'Gamma_{k}_s_inv':v for k,v in r.items()},
           four_alpha_to_H=sum(r[k] for k in ('pT','nHe3','npD','dd'))/H,
           local_p_npD=r['npD']/sum(r.values()),
           local_p_DD=r['dd']/sum(r.values()),
           source='RiceDD_2000_surrogate_plus_Cyburt2003_high_E_extrap_3_channels'))
    data={dd_mode:{row['E_inj_MeV']:row for row in solve_cascade(z,dd_mode,delta_E=2,nquad=96)}
          for dd_mode in ('rice','cyburt_extrap')}
    for E in Eis:
        for mode in data:
            rows.append(data[mode][E])

savecsv('LOCAL_HAZARD_SEVEN_CHANNEL_18.csv',hazard)
savecsv('STATIC_KN_ALPHA_COMPETITION_36.csv',rows)
comparison=[]
for z in zs:
    for E in Eis:
        rice=next(r for r in rows if r['z']==z and r['E_inj_MeV']==E and r['DD_source_mode']=='rice')
        cy=next(r for r in rows if r['z']==z and r['E_inj_MeV']==E and r['DD_source_mode']=='cyburt_extrap')
        comparison.append(dict(z=z,E_MeV=E,P_DD_Rice=rice['P_dd'],P_DD_Cyburt_highE_extrap=cy['P_dd'],
          P_npD_Rice=rice['P_npD'],N_D_from_npD=rice['P_npD'],
          N_D_from_direct_DD=2*rice['P_dd'],
          ratio_npD_Dbirth_to_directDD_Dbirth=rice['P_npD']/(2*rice['P_dd']),
          ratio_Rice_over_Cyburt_DD_first_stop=rice['P_dd']/cy['P_dd'],
          P_all_alpha=rice['P_alpha_photo_total'],
          max_probability_error=rice['P_normalization_abs_error'],
          max_projectile_energy_error=rice['E_ledger_rel_error'],
          interpretation='Cyburt2003_highE_extrap_not_lab_observation;Rice_binned_fit_model_not_measured_excitation'))
savecsv('DD_SOURCE_COMPARISON_18.csv',comparison)

# Figures: physical cross sections with explicit extrapolative nature; probability; redshift trend.
plt.rcParams.update({'font.size':10})
fig,ax=plt.subplots(figsize=(7.2,4.3))
for k,label in [('pT','He4 -> p + T'),('nHe3','He4 -> n + He3'),('npD','He4 -> n + p + D'),('dd_cyburt_extrap','He4 -> D + D (2003 extrap)')]:
    ax.plot([r['E_gamma_MeV'] for r in xs],[r[f'sigma_{k}_cm2']/1e-33 for r in xs],marker='o',ms=2,label=label)
ax.plot([r['E_gamma_MeV'] for r in xs if r['sigma_DD_Rice_bin_surrogate_cm2'] is not None],
        [r['sigma_DD_Rice_bin_surrogate_cm2']/1e-33 for r in xs if r['sigma_DD_Rice_bin_surrogate_cm2'] is not None],
        marker='s',linestyle='--',label='He4 -> D+D (Rice bin surrogate)')
ax.axvspan(150,250,color='grey',alpha=.12,label='high-E extrapolative domain')
ax.set_yscale('log');ax.set_xlabel('Gamma energy (MeV)');ax.set_ylabel('Model cross section (nb)');ax.legend(fontsize=7);ax.set_title('Published fit extrapolation vs Rice source-bin DD surrogate');fig.tight_layout()
for ext in ('png','svg'):fig.savefig(FIG/f'ALPHA_FIT_SOURCE_COMPARISON.{ext}',dpi=180,metadata=({'Date':None} if ext=='svg' else {}))
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.3))
for k,label in [('P_pT','p + T'),('P_nHe3','n + He3'),('P_npD','n + p + D'),('P_dd','D + D')]:
    p=[r[k] for r in rows if r['z']==1e4 and r['DD_source_mode']=='rice' and r['E_inj_MeV'] in Eis]
    ax.plot(Eis,p,marker='o',label=label)
ax.set_yscale('log');ax.set_xlabel('Injected gamma energy (MeV)');ax.set_ylabel('Per photon terminal-channel probability')
ax.set_title('Fixed z=1e4: KN recycled 150–250 MeV gamma');ax.legend();fig.tight_layout()
for ext in ('png','svg'):fig.savefig(FIG/f'KN_ALPHA_BIRTH_BRANCHING.{ext}',dpi=180,metadata=({'Date':None} if ext=='svg' else {}))
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.3))
for k,label in [('P_npD','He4 -> n+p+D'),('P_dd','He4 -> D+D'),('P_pT','He4 -> p+T'),('P_nHe3','He4 -> n+He3')]:
    x=[r for r in rows if r['E_inj_MeV']==220 and r['DD_source_mode']=='rice']; x.sort(key=lambda a:a['z'])
    ax.loglog([r['z'] for r in x],[r[k] for r in x],marker='o',label=label)
ax.set_xlabel('Injection redshift z');ax.set_ylabel('Per injected gamma model probability')
ax.set_title('First nuclear exit after all-order KN (BW/BH terminal)');ax.legend(fontsize=8);fig.tight_layout()
for ext in ('png','svg'):fig.savefig(FIG/f'ALPHA_CHANNELS_VS_Z.{ext}',dpi=180,metadata=({'Date':None} if ext=='svg' else {}))
plt.close(fig)

rr=next(r for r in rows if r['E_inj_MeV']==220 and r['z']==1e4 and r['DD_source_mode']=='rice')
summary={
 'unit':'FLRW_KN_ALPHA_PHOTONUCLEAR_CHANNEL_COMPETITION_20261031',
 'data_class':'model_source_conditional_analytic_fits_plus_QED_no_new_observed_rows',
 'counts':{'original_source_fit_rows':len(xs),'seven_channel_hazard_rows':len(hazard),
           'kn_competing_cascade_rows':len(rows),'cross_source_comparison_rows':len(comparison),
           'new_measured_rows':0,'plots_png':3,'plots_svg':3},
 'model_scopes':{
  'reference_cosmology':'PR132_flat_reference_FLRW_fully_ionized',
  'gamma':'fixed_z_all_orders_cold_e_KN_above_150MeV_only',
  'bw_bh':'PR132_QED_terminal_electron_positron_pair_not_regenerated',
  'alpha_nuclear':'Cyburt2003 Appendix A 6,7,9 fitted cross sections extrapolated to 150to250 MeV',
  'dd_baseline':'Rice2000 8.29,4.34 nb broad bin constrained SURROGATE no E-resolved measurement',
  'dd_alternative':'Cyburt2003 Appendix A8 fit high-E extrapolation sensitivity only',
  'missing':'full e+e- inverse Compton, gamma-gamma redistribution, triplet pair, D-fast ion/nuclear stopping, net heat, real BASS gamma source, below-150 photon transport'},
 'representative_220_1e4':rr,
 'conservation_checks':{'max_P_err':max(r['P_normalization_abs_error'] for r in rows),
   'max_projectile_E_rel_err':max(r['E_ledger_rel_error'] for r in rows),
   'max_KN_pdf_abs_err':max(r['KN_pdf_max_normalization_abs_error'] for r in rows)},
 'gate':{'Central':'28/88','HE_physical':'14/18','canonical_delta':0,
    'R_event':None,'heat_rate':None,'kappa':None,'L4':False,'PRODUCTION':'HOLD',
    'no_merge':True,'no_force_push':True,'auto_next':False}}
(OUT/'SCIENTIFIC_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
print('representative 220MeV z=1e4 P_dd',rr['P_dd'],'P_npD',rr['P_npD'],'N_D',rr['N_D_birth_per_gamma'])
print('conservation',summary['conservation_checks'])
