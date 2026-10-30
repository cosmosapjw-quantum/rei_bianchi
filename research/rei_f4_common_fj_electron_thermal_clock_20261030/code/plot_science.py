#!/usr/bin/env python3
"""Produce independent publication-facing figures from saved physical computed rows."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def read(name):return list(csv.DictReader((OUT/name).open()))
def col(rows,k):return np.array([float(r[k]) for r in rows])

def fig(name,x,curves,title,ylabel,log=True):
    plt.figure(figsize=(8,5))
    for label,y in curves:
        if log:
            yy=np.abs(np.array(y,float))
            peak=float(np.nanmax(yy))
            yy[(~np.isfinite(yy)) | (yy<=max(peak*1.e-12,1.e-290))]=np.nan
            plt.semilogy(x,yy,label=label)
        else:plt.plot(x,y,label=label)
    plt.gca().invert_xaxis()
    plt.xlabel('Redshift $z$')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(fontsize=8,loc='best')
    plt.grid(alpha=.22)
    plt.tight_layout()
    plt.savefig(OUT/name,dpi=190)
    plt.close()

if __name__=='__main__':
    a=read('BASS21_FJ_ELECTRON_CLOCK_193.csv')
    b=read('CONDITIONAL_FIRSTFLIGHT_THERMAL_192.csv')
    c=read('REI7_BASS193_CLOCK_COMPARE.csv')
    za=col(a,'z');zb=col(b,'z_mid')
    fig('PLOT01_ELECTRON_SOURCE_RATES.png',zb,[
       ('PR287 conditional photon first-absorption, per Hubble',col(b,'conditional_electron_count_source_per_baryon_s')/col(b,'H_mid_s')),
       ('BASS21 native chemistry electron rate |F_e|/H (fixed original saved Y)',np.interp(zb,za[::-1],np.abs(col(a,'F_e_native_per_baryon_s')/col(a,'H_s'))[::-1])),
       ],'Native reaction source vs conditional photon first flight',r'Electron number per baryon per Hubble time',True)
    fig('PLOT02_CONDITIONAL_ENERGY_PORTS.png',zb,[
       ('primary electron energy',col(b,'conditional_primary_kinetic_source_eV_per_baryon_s')/col(b,'H_mid_s')),
       ('atomic binding energy',col(b,'conditional_binding_source_eV_per_baryon_s')/col(b,'H_mid_s')),
       ],'Causal arrival energy ports, conditional all-singlet spectrum',r'Energy per baryon per Hubble time [eV]',True)
    fig('PLOT03_THERMAL_EQUIVALENT.png',zb,[
      ('unit-deposition heating-only temperature equivalent / saved T',
       col(b,'conditional_temperature_heat_operator_K_per_s_at_efficiency_1')/col(b,'H_mid_s')/col(b,'T_mid_K')),
      ('thermalized-electron number-loading temperature |port| /H /saved T',
       np.abs(col(b,'conditional_temperature_number_operator_K_per_s_if_electrons_thermalize'))/col(b,'H_mid_s')/col(b,'T_mid_K'))
       ],'Conditional source operator amplitudes, NOT solved temperature',r'Instantaneous dimensionless rate per Hubble',True)
    fig('PLOT04_LI6_FJ_CROSS_J.png',za,[
      ('Original 21->17 omitted-Li6 cross Jacobian max',col(a,'BASS21_BASS17_cross_J17x4_max_per_s')),
      ('Original BASS 21-to-17 Jacobian internal difference max',col(a,'BASS21_minus_BASS17_Jmax_per_s'))
     ],'Original common electron pool: exact off-manifold F/J couplings',r'Max absolute Jacobian entry [s$^{-1}$]',True)
    fig('PLOT05_REI_BASS_SEPARATE_CLOCKS.png',col(c,'z_REI'),[
        ('(REI saved time - BASS interpolated time)/BASS time',col(c,'z_matched_relative_time_difference'))
       ],'Seven differently owned original histories, not clock-equivalent',r'Relative proper-time difference',False)
    print('PLOTS=5/5')
