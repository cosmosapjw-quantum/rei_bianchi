#!/usr/bin/env python3
"""Render saved exact-analysis summaries; no scientific calculation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
a = json.loads((root / 'analysis/N512_P60/GLOBAL_ANALYSIS.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.facecolor': 'white'})
fig, ax = plt.subplots(1, 2, figsize=(13, 6))
y = np.arange(4)
colors = ['#126782', '#b85c38']
for j, k in enumerate(['P_final', 'H_total_eV']):
    values = [float(x['metrics']['absolute'][k]['old_over_new_width']) for x in a['paths']]
    ax[0].barh(y + (j - .5) * .33, values, height=.29, color=colors[j], label=['Final photon', 'Species-sum heat'][j])
    for iy, v in zip(y + (j - .5) * .33, values):
        ax[0].text(v + .15, iy, f'{v:.2f}×', va='center', fontsize=10)
ax[0].set_yticks(y, [f"OFF {x['node']}" for x in a['paths']])
ax[0].invert_yaxis(); ax[0].set_xlim(0, 20)
ax[0].set_xlabel('Old N128 width / new N512 width')
ax[0].set_title('Selected paths: interval narrowing', loc='left', fontweight='bold', pad=16)
ax[0].legend(frameon=False, loc='upper left', bbox_to_anchor=(0, -.26), ncol=2, fontsize=9)
keys = ['P_final', 'A_total', 'B_total_eV', 'H_total_eV']
labels = ['Final photon', 'Absorption count', 'Absorbed energy', 'Species-sum heat']
actual = [float(a['global_OFF']['absolute'][k]['width_reduction_percent']) for k in keys]
ceiling = [float(a['global_OFF']['absolute'][k]['maximum_full_gain_if_selected_zero_percent']) for k in keys]
ax[1].barh(y, ceiling, color='#e4e8ea', height=.58, label='Ceiling if all four widths became zero')
ax[1].barh(y, actual, color=['#126782', '#427c8d', '#6294a0', '#b85c38'], height=.37, label='Actual N512 replacement')
for iy, v in zip(y, actual):
    ax[1].text(v + .015, iy, f'{v:.6f}%', va='center', fontsize=10)
ax[1].set_yticks(y, labels); ax[1].invert_yaxis(); ax[1].set_xlim(0, 1.42)
ax[1].set_xlabel('Full finite OFF width decrease (%)')
ax[1].set_title('Full finite budget: measured gain', loc='left', fontweight='bold', pad=16)
ax[1].legend(frameon=False, loc='upper left', bbox_to_anchor=(0, -.26), fontsize=9)
fig.suptitle('BASS_HE E13C6 · Same captured target, four OFF paths', x=.045, y=.96, ha='left', fontweight='bold', fontsize=16)
fig.text(.045, .045, 'Widths quantify conditional numerical enclosures. They are not changes in physical photon or heat yield.\nAll 136 primary old/new metric pairs are nested; no interval intersection is used.', fontsize=9, color='#444b52')
fig.subplots_adjust(left=.09, right=.96, top=.80, bottom=.33, wspace=.46)
(root / 'figures').mkdir(exist_ok=True)
fig.savefig(root / 'figures/E13C6_WIDTH_REFINEMENT.png', dpi=180)
fig.savefig(root / 'figures/E13C6_WIDTH_REFINEMENT.pdf')
plt.close(fig)
