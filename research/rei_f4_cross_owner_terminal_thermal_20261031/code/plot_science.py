#!/usr/bin/env python3
"""Six publication-facing source-snapshot plots; each derived from original archived rows."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
output=root/'results'
df=pd.read_csv(output/'CROSS_OWNER_TERMINAL_THERMAL_192.csv')
assert len(df)==192
z=df['z_mid'].to_numpy();dt=df['proper_interval_s'].to_numpy()

def draw(name,title,ylabel,curves,logy=True,abs_y=False):
    fig,ax=plt.subplots(figsize=(7.5,4.7))
    for label,vals in curves:
        x=np.asarray(vals,dtype=float)
        if abs_y:x=np.abs(x)
        if logy:x=np.where(x>0,x,np.nan)
        ax.semilogy(z,x,label=label) if logy else ax.plot(z,x,label=label)
    ax.set_xlabel('Redshift $z$ (original BASS193)')
    ax.set_ylabel(ylabel)
    ax.set_title(title,fontsize=10)
    ax.grid(alpha=.22)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(output/name,dpi=180)
    plt.close(fig)

A=lambda k:df[k].to_numpy(dtype=float)
draw('PLOT01_TERMINAL_ENERGY_BOUNDS.png',
    'Causal first-generation electron energy partitions',
    'Primary kinetic energy [eV per original baryon per arrival bin]',
    [('Selected: $E_e<10.2$ eV',A('conditional_terminal_selected_low_e_eV_per_b')),
     ('Selected low + all unselected upper',A('conditional_terminal_low_e_upper_eV_per_b')),
     ('All primary electron energy (distinct ceiling)',A('conditional_total_primary_energy_all_eV_per_b'))])
draw('PLOT02_TEMPERATURE_SOURCE_OPERATORS.png',
    'Conditional point-source temperature coefficients, not evolved $T$',
    'Thermal source coefficient [K / s]',
    [('Selected $<10.2$ eV',A('terminal_Tdot_selected_K_s')),
     ('First-generation + missing upper',A('terminal_Tdot_upper_K_s')),
     ('All-primary energy ceiling',A('conditional_all_primary_to_heat_Tdot_ceiling_K_s'))])
draw('PLOT03_ELECTRON_NUMBER_LOADING.png',
    'Photoelectron number loading versus terminal heat',
    '|Source coefficient| [K / s]',
    [('Electron-loading (if immediately thermalized)',A('hypothetical_instant_electron_loading_Tdot_K_s')),
     ('Terminal upper, first-generation',A('terminal_Tdot_upper_K_s')),
     ('Hybrid source replacement |point temperature|',A('original_hybrid_source_replacement_formal_Tdot_K_s'))],abs_y=True)
draw('PLOT04_CROSS_SOURCE_PROPER_CLOCK.png',
    'Independent PR297 and PR298 original clock agreement',
    'Absolute clock diagnostic (dimensionless)',
    [('Proper $\\Delta t$ inter-archive relative',A('clock_rel_to_PR298')),
     ('Midpoint $|H\\Delta t/\\Delta\\ln a -1|$',A('clock_midpoint_Hdt_dx_minus_1'))],abs_y=True)
draw('PLOT05_FROZEN_SOURCE_RATIO.png',
    'Conditional thermal versus hybrid-chemistry source scale',
    'Instantaneous ratio (diagnostic, no additive coupling)',
    [('Terminal first-generation upper / |hybrid formal $\\dot T$|',A('terminal_Tdot_upper_over_hybrid_abs'))],logy=True)
draw('PLOT06_CUMULATIVE_ENERGY_PORTS.png',
    'Frozen exposure only (not thermochemical evolution)',
    'Accumulated source coefficient [K]',
    [('Selected subthreshold terminal',np.cumsum(A('terminal_Tdot_selected_K_s')*dt)),
     ('Terminal first-generation upper',np.cumsum(A('terminal_Tdot_upper_K_s')*dt)),
     ('All-primary energy ceiling',np.cumsum(A('conditional_all_primary_to_heat_Tdot_ceiling_K_s')*dt))],logy=True)
print('SCIENTIFIC_PLOTS=6/6; source=192 archived causal arrival rows')
