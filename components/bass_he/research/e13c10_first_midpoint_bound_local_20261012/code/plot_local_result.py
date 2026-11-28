#!/usr/bin/env python3
"""Plot saved finite interval widths; no scientific kernel imports or runs."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True)
    args = ap.parse_args()
    root = args.package.resolve()
    source = root / 'analysis/ACTUAL/LOCAL_ANALYSIS.json'
    data = json.loads(source.read_bytes())
    out = root / 'figures'
    out.mkdir(exist_ok=False)
    started = time.perf_counter()
    labels = [str(x['node']) for x in data['selected_paths']] + ['Selected\nsum']
    series = {}
    for q in ('P_final', 'H_total_eV'):
        values = [x['P_H_summary'][q] for x in data['selected_paths']]
        values.append(data['selected_aggregate_summary'][q])
        series[q] = [float(100 * Fraction(v['candidate_width']) / Fraction(v['baseline_width'])) for v in values]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.8), gridspec_kw={'width_ratios': [1.65, 1]})
    x = np.arange(len(labels))
    colors = {'P_final': '#2563A5', 'H_total_eV': '#CC671B'}
    for offset, q, title in [(-.18, 'P_final', 'Final photon quantity P'), (.18, 'H_total_eV', 'Heating H')]:
        bars = axes[0].bar(x + offset, series[q], width=.34, color=colors[q], label=title, zorder=3)
        for b, v in zip(bars, series[q]):
            axes[0].text(b.get_x() + b.get_width()/2, v + .18, f'{v:.2f}', ha='center', va='bottom', fontsize=8.5)
    axes[0].set_xticks(x, labels)
    axes[0].set_xlabel('Captured path node (five selected paths)')
    axes[0].set_ylabel('E13C10 full interval width / E13C9 width (%)')
    axes[0].set_ylim(0, 15)
    axes[0].set_title('All 170 raw intervals are nested', loc='left', weight='bold', pad=15)
    axes[0].grid(axis='y', color='#e2e8f0', zorder=0)
    axes[0].legend(frameon=False, loc='upper right')
    categories = [('signed_rectangle', 'Second Volterra integral', '#2563A5'),
                  ('first_curvature_range', 'First-integral curvature', '#CC671B'),
                  ('finite_volterra_tail', 'Finite Volterra tail', '#399777'),
                  ('first_midpoint_rounding', 'Midpoint rounding', '#B39CCA'),
                  ('other_rounding', 'Other rounding', '#87949F')]
    bottoms = np.zeros(2)
    for key, name, color in categories:
        vals = [float(data['selected_bound_halfwidth_allocation'][q]['percent'][key]) for q in ('P_final', 'H_total_eV')]
        axes[1].bar([0, 1], vals, bottom=bottoms, width=.56, color=color, label=name)
        bottoms += vals
    axes[1].set_xticks([0, 1], ['P', 'H'])
    axes[1].set_ylabel('Share of selected residual bound (%)')
    axes[1].set_ylim(0, 106)
    axes[1].set_title('Remaining bound: 98.83% second integral', loc='left', weight='bold', pad=15, fontsize=11)
    for i, q in enumerate(('P_final', 'H_total_eV')):
        v = float(data['selected_bound_halfwidth_allocation'][q]['percent']['signed_rectangle'])
        axes[1].text(i, 50, f'{v:.2f}%', ha='center', va='center', color='white', weight='bold', fontsize=15)
    axes[1].legend(frameon=False, loc='upper center', bbox_to_anchor=(.5, -.11), fontsize=9, ncol=1)
    fig.suptitle('BASS_HE E13C10 — local signed Peano enclosure', x=.065, ha='left', fontsize=17, weight='bold')
    fig.text(.065, .025, 'Fixed captured finite problem, P60. Widths and bound allocations are not measured physical errors. Full population: NOT_RUN.', fontsize=9, color='#475569')
    fig.subplots_adjust(left=.075, right=.97, top=.82, bottom=.28, wspace=.34)
    for ext in ('png', 'svg'):
        fig.savefig(out / ('E13C10_LOCAL_WIDTHS.' + ext), dpi=180, facecolor='white')
    plt.close(fig)
    receipt = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source_analysis_sha256': sha(source),
               'plot_code_sha256': sha(__file__), 'scientific_kernel_invocations': 0,
               'elapsed_seconds': time.perf_counter() - started,
               'series_percent_for_display_only': series,
               'files': {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(out.iterdir())}}
    (out / 'PLOT_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
