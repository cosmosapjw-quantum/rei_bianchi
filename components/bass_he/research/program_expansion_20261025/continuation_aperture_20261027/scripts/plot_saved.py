"""Three fixed panels using only new, previously saved validation values."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
payload = json.loads((ROOT / 'evidence/validation/SAVED_PLOT_DATA.json').read_text())
if payload['schema'] != 'HE_APERTURE07_SAVED_DATA_V1':
    raise RuntimeError('new APERTURE07 saved values required')
if payload['source_angular06_saved_sha256'] != '71812d18e39080ace31cfb0d0a5b418ea0dc291210b6d34c8b79c992d6376ff6':
    raise RuntimeError('wrong immutable native parameter source')

fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.5), constrained_layout=True)
fig.suptitle('Conditional annular acceptance | rational mass bounds | physical normalization open', fontsize=12)

bins = payload['fold_bin_mass']
x = [r['lab_bin_width']['display_float'] for r in bins]
lower = [r['mass']['lower']['display_float'] for r in bins]
upper = [r['mass']['upper']['display_float'] for r in bins]
axes[0].plot(x, lower, 'o-', color='#19647e', label='lower bound')
axes[0].plot(x, upper, 'x--', color='#d67d00', label='upper bound')
axes[0].set(xscale='log', yscale='log', xlabel='Lab cosine bin width above fold',
            ylabel='Conditional event mass', title='A  Finite fold-bin mass')
axes[0].legend(fontsize=8)

rows = payload['convergence']
axes[1].plot([r['bits'] for r in rows], [r['mass']['width']['display_float'] for r in rows],
             'o-', color='#276749', label='observed enclosure width')
axes[1].plot([r['bits'] for r in rows], [r['mass']['width_bound']['display_float'] for r in rows],
             's--', color='#8064a2', label='recorded analytic width bound')
axes[1].set(yscale='log', xlabel='Bisection target bits (delta = 2^-bits)',
            ylabel='Rational mass interval width', title='B  Same-input convergence', xticks=[8, 16, 24, 40])
axes[1].legend(fontsize=8)

counterexample = payload['correlated_counterexample']
values = [counterexample['coincidence']['lower']['display_float'],
          counterexample['product_of_marginal_hits']['display_float'],
          counterexample['coincidence_daughters']['lower']['display_float']]
axes[2].bar(['Pair event\nyield', 'Product of\nmarginal hits', 'Daughters in\ncoincidence'], values,
            color=['#19647e', '#b94a48', '#8064a2'], width=0.65)
axes[2].set(ylim=(0, 1.15), ylabel='Mass or represented daughter count',
            title='C  Shared-event correlation')
for i, value in enumerate(values):
    axes[2].text(i, value + 0.025, f'{value:g}', ha='center', fontsize=10)
for axis in axes:
    axis.grid(True, alpha=0.22, axis='y')
    axis.spines[['top', 'right']].set_visible(False)
out = ROOT / 'evidence/plot'
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / 'APERTURE07_BOUNDS.png', dpi=160)
fig.savefig(out / 'APERTURE07_BOUNDS.svg')
plt.close(fig)
