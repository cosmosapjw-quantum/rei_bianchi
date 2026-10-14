#!/usr/bin/env python3
"""Render already-certified ranges; no new scientific bound computation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
raw = json.loads((root/'evidence/CERTIFICATE_FIRST.json').read_text())
assert raw['status'] == 'PASS_SCOPED'
fig, ax = plt.subplots(figsize=(8.4, 3.6), layout='constrained')
fig.patch.set_facecolor('white')
colors = {'upper': '#1d4e89', 'lower': '#087f8c'}
for name, y, label in [('upper', 1, 'Upper branch'), ('lower', 0, 'Lower branch')]:
    rec = raw['certificate']['branches'][name]['quartic_magnitude_coefficient']['decimal_outward_90']
    # Binary float conversion below is only for plotting coordinates, never a bound.
    lo, hi = float(rec['lower'])*1000, float(rec['upper'])*1000
    ax.hlines(y, lo, hi, color=colors[name], linewidth=7)
    ax.vlines([lo, hi], y-.065, y+.065, color=colors[name], linewidth=2)
    ax.text((lo+hi)/2, y+.17, label, color=colors[name], ha='center', fontsize=12, weight='bold')
ax.axvline(0, color='#89939a', linewidth=1)
ax.set_xlim(0, 1.45)
ax.set_ylim(-.45, 1.75)
ax.set_yticks([])
ax.set_xlabel(r'Quartic displacement magnitude $\Gamma_s$  [$10^{-3}\,\mathrm{eV}^{-2}$]', fontsize=11)
ax.set_title('PHYS35: certified profile-shift coefficients', loc='left', fontsize=15, weight='bold', pad=18)
ax.text(.0, 1.48, r'$\Delta W_s=-\delta^4\Gamma_s(\delta)$;  $0<\delta\leq0.001$ eV', fontsize=11, color='#43515c')
ax.text(.02, -.33, 'Uniform deterministic enclosures; no point estimate or statistical confidence interval.', fontsize=9, color='#43515c')
ax.grid(axis='x', color='#e3e8ec', linewidth=.8)
ax.set_axisbelow(True)
for side in ('top', 'right', 'left'):
    ax.spines[side].set_visible(False)
ax.spines['bottom'].set_color('#bdc7cd')
folder = root/'figures'
folder.mkdir(exist_ok=True)
for ext in ('png', 'svg'):
    fig.savefig(folder/('PHYS35_COEFFICIENT_RANGES.'+ext), dpi=180, facecolor='white')
plt.close(fig)
print(json.dumps({'kind':'RENDER_ONLY_FROM_FROZEN_CERTIFICATE','new_science':0,
                  'files':[str(folder/('PHYS35_COEFFICIENT_RANGES.'+e)) for e in ('png','svg')]}))
