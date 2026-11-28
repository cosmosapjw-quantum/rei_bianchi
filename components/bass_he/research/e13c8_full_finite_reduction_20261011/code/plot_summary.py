#!/usr/bin/env python3
"""Standalone figure from saved scientific and telemetry evidence; no kernels."""
import argparse
from datetime import datetime
from fractions import Fraction
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True)
    a = ap.parse_args(); root = a.package
    reduction = json.loads((root / 'analysis/FULL_RETURN_REDUCTION/REDUCTION.json').read_text())
    residual = json.loads((root / 'analysis/RESIDUAL/ACTUAL/RESIDUAL_SUMMARY.json').read_text())
    performance = json.loads((root / 'analysis/PERFORMANCE/PERFORMANCE_ANALYSIS.json').read_text())
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), gridspec_kw={'width_ratios': [1.05, 1.1, 1.3]})
    quantities = ['P_final', 'H_total_eV', 'A_total', 'B_total_eV', 'Z_eV']
    ratios = []
    for q in quantities:
        row = next(x for x in reduction['full_comparison'] if x['kind'] == 'absolute' and x['quantity'] == q)
        ratios.append(float(Fraction(row['new_width']) / Fraction(row['old_width'])))
    x = np.arange(len(quantities))
    axes[0].bar(x - .18, [1] * len(x), .36, color='#cbd5e1', label='Before full return')
    axes[0].bar(x + .18, ratios, .36, color='#17687b', label='After full return')
    for i, r in enumerate(ratios):
        axes[0].text(i + .18, r * 1.13, f'{100*r:.2f}%', ha='center', fontsize=9)
    axes[0].set_yscale('log'); axes[0].set_ylim(.01, 1.6)
    axes[0].set_xticks(x, ['Photon', 'Heat', 'Absorb.\nnumber', 'Absorb.\nenergy', 'Redshift'])
    axes[0].set_ylabel('Raw interval width / previous width')
    axes[0].set_title('A. Full finite enclosure', loc='left', fontweight='bold')
    axes[0].legend(frameon=False, fontsize=9, loc='upper right')
    labels = ['Photon', 'Heat']; qs = ['P_final', 'H_total_eV']
    trunc = [float(residual['metrics'][q]['half_width_allocation']['midpoint_truncation']['percent']) for q in qs]
    coupling = [float(residual['metrics'][q]['half_width_allocation']['coupling_bound']['percent']) for q in qs]
    axes[1].barh(labels, trunc, color='#17687b', label='Midpoint truncation bound')
    axes[1].barh(labels, coupling, left=trunc, color='#d99543', label='Propagated coupling bound')
    for i in range(2):
        axes[1].text(trunc[i]/2, i, f'{trunc[i]:.2f}%', ha='center', va='center', color='white', fontweight='bold')
        axes[1].text(trunc[i]+coupling[i]/2, i, f'{coupling[i]:.2f}%', ha='center', va='center', color='#172635', fontweight='bold')
    axes[1].set_xlim(0, 100); axes[1].set_xlabel('Allocation of current half-width (%)')
    axes[1].set_title('B. Remaining upper bounds', loc='left', fontweight='bold')
    axes[1].legend(frameon=False, fontsize=9, loc='lower left', bbox_to_anchor=(0, -.34))
    ranks = performance['per_rank']
    t0 = min(datetime.fromisoformat(r['rank_start_utc']) for r in ranks)
    for r in ranks:
        start = (datetime.fromisoformat(r['rank_start_utc']) - t0).total_seconds()/60
        duration = r['rank_start_to_receipt_utc_seconds']/60
        axes[2].broken_barh([(start, duration)], (r['rank']-.4, .8), facecolors='#17687b', alpha=.84)
    axes[2].set_ylim(-1, 64); axes[2].set_xlim(0, 34)
    axes[2].set_yticks([0, 15, 31, 47, 63]); axes[2].set_ylabel('Computing MPI rank')
    axes[2].set_xlabel('Minutes from first rank start (UTC)')
    axes[2].set_title('C. Actual 64-rank activity', loc='left', fontweight='bold')
    fig.suptitle('BASS_HE E13C8  |  Complete OFF reduction and actual MPI return', x=.055, ha='left', fontsize=15, fontweight='bold')
    fig.text(.055, .012, 'Fixed captured finite target only. Panel B is bound accounting, not an irreducible error floor. Panel C includes waits and I/O; CPU utilization was not measured.', fontsize=9, color='#465465')
    fig.subplots_adjust(left=.055, right=.985, top=.81, bottom=.23, wspace=.36)
    out = root / 'figures'; out.mkdir(exist_ok=True)
    for ext in ('png', 'svg'):
        path = out / ('E13C8_SCIENCE_AND_PARALLEL.' + ext)
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=200, facecolor='white')
    print(json.dumps({'status': 'CREATED_FROM_SAVED_EVIDENCE', 'outputs': ['figures/E13C8_SCIENCE_AND_PARALLEL.png', 'figures/E13C8_SCIENCE_AND_PARALLEL.svg'], 'kernel_invocations': 0}))


if __name__ == '__main__':
    main()
