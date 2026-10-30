#!/usr/bin/env python3
"""Render six source-derived scientific figures, no synthetic data."""
import csv,pathlib,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
with (OUT/'HHE_IGM_THERMAL_193.csv').open() as f: rows=list(csv.DictReader(f))
def C(k):return np.array([float(r[k]) for r in rows])
z=C('z');x=C('x');H=C('H_s')
def fig(tag,title,ylabel,curves,symlog=False):
    f,ax=plt.subplots(figsize=(9,5.6))
    for label,y in curves:
        ax.plot(z,y,label=label,linewidth=1.55)
    if symlog:
        mx=max(float(np.max(abs(y))) for _,y in curves)
        ax.set_yscale('symlog',linthresh=max(mx*1e-4,1e-70))
    ax.invert_xaxis();ax.set_xlabel('Redshift z (original BASS193 sampled epochs)');ax.set_ylabel(ylabel)
    ax.set_title(title,fontsize=12);ax.grid(alpha=.22);ax.legend(fontsize=8,loc='best')
    ax.text(.015,.015,'Frozen BASS background + REI Grackle translated point RHS; NOT an evolved solution',transform=ax.transAxes,fontsize=7,alpha=.8)
    f.tight_layout();f.savefig(OUT/tag,dpi=180);plt.close(f)
fig('PLOT01_REI_VS_BASS_HHE_F.png','Shared photon input: actual BASS H/He vs translated REI chemical F',
    'dY fraction / dt [s$^{-1}$]',[
    ('REI HII',C('REI_source_translated_HII_fraction_dt_per_s')),
    ('BASS HII',C('native_BASS_HII_fraction_dt_per_s')),
    ('REI HeIII',C('REI_source_translated_HeIII_fraction_dt_per_s')),
    ('BASS HeIII',C('native_BASS_HeIII_fraction_dt_per_s'))],True)
fac=1./H
fig('PLOT02_REI_THERMAL_ENERGY_PORTS.png','H/He proper-clock thermal energy port decomposition',
    'Integrated-rate amplitude [eV / Href / Hubble interval]',[
    ('Native BASS primary photoelectron input',C('REI_HHe_primary_heat_erg_per_Href_s')/1.602176634e-12*fac),
    ('REI thermal microphysical net',C('REI_HHe_thermal_micro_erg_per_Href_s')/1.602176634e-12*fac),
    ('REI captured escape (binding+kinetic)',C('REI_HHe_escape_erg_per_Href_s')/1.602176634e-12*fac),
    ('CMB Compton exchange',C('REI_HHe_cmb_exchange_erg_per_Href_s')/1.602176634e-12*fac)],True)
fig('PLOT03_REI_POINT_TEMPERATURE.png','Translated REI point temperature RHS decomposition (not evolved)',
    r'Instantaneous source amplitude $\dot{T}/H$ [K]',[
    ('Total REI HHe point RHS',C('REI_HHe_Tdot_point_K_s')*fac),
    ('Thermal source',C('REI_HHe_Tdot_thermal_K_s')*fac),
    ('Expansion work',C('REI_HHe_Tdot_expansion_K_s')*fac),
    ('Chemical electron number loading',C('REI_HHe_Tdot_electron_loading_K_s')*fac)],True)
fig('PLOT04_BACKGROUND_BIANCHI_K_PROXY.png','Original BASS b,H to conditional AXBI K-convention proxy',
    r'Dimensionless anisotropic expansion or metric coefficient',[
    ('original b',C('b_BASS')),
    (r'$\dot b/H$ from saved proper clock',C('b_dot_proxy_s')/H),
    (r'$(K_\parallel-K_\perp)/3H$',(C('K_parallel_proxy_s')-C('K_perp_proxy_s'))/(3*H))],False)
fig('PLOT05_COMMON_ELECTRON_REFERENCE.png','H reference normalization and BASS electron bath',
    'Number per original baryon',[
    (r'$n_{H,ref}/n_b$',C('nHref_over_nb')),
    ('BASS full electron fraction',C('ne_all_BASS_cm3')/(C('nb_m3')/1e6)),
    ('REI HHe-only electron fraction',C('ne_HHe_cm3')/(C('nb_m3')/1e6))],False)
fig('PLOT06_CHEM_THERMAL_SOURCE_CHANNELS.png','Physical kinetic/Compton cooling coefficients on BASS193',
    'Source-equivalent temperature rate / H [K]',[
    ('BASS-primary heat only',C('REI_HHe_primary_heat_erg_per_Href_s')/C('REI_HHe_Cv_erg_per_Href_per_K')*fac),
    ('REI CE cooling',-C('REI_HHe_ce_thermal_sink_erg_per_Href_s')/C('REI_HHe_Cv_erg_per_Href_per_K')*fac),
    ('REI RR cooling',-C('REI_HHe_rr_thermal_sink_erg_per_Href_s')/C('REI_HHe_Cv_erg_per_Href_per_K')*fac),
    ('CMB Compton',C('REI_HHe_cmb_exchange_erg_per_Href_s')/C('REI_HHe_Cv_erg_per_Href_per_K')*fac)],True)
print('SIX_PLOTS=6/6')
