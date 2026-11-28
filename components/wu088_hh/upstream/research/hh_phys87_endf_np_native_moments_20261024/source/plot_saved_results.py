#!/usr/bin/env python3
"""Render2PNG+2PDF from one saved primary RESULT.json; never imports source code."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    raw = args.result.read_bytes(); saved = json.loads(raw)
    if saved['status'] != 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW':
        raise ValueError('SAVED_COMPLETE_PRIMARY_REQUIRED')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    os.environ['MPLCONFIGDIR'] = str(output/'.mpl_config')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.bbox': 'tight', 'pdf.fonttype': 42})
    knots = saved['source_native_knots']
    energies = [float(r['En_eV']) for r in knots]
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True, constrained_layout=True)
    axes[0].loglog(energies, [float(r['sigma_barn']) for r in knots], color='#174b6b')
    axes[0].set_ylabel('Capture cross section [barn]')
    axes[0].set_title('ENDF/B-VIII.1 H1 native knots; finite source support')
    fig.supxlabel('Native knots; connecting lines are visual guides', fontsize=9)
    for key, color in [('a1', '#b34a24'), ('a2', '#476f39')]:
        axes[1].semilogx(energies, [float(r[key]) for r in knots], label=key, color=color)
    axes[1].set_xlabel('Incident neutron LAB energy [eV]'); axes[1].set_ylabel('Legendre coefficient')
    axes[1].legend(); axes[1].grid(alpha=.2)
    figures = []
    for extension in ('png', 'pdf'):
        path = output/('native_source.'+extension)
        fig.savefig(path, dpi=180 if extension == 'png' else None); figures.append(path)
    plt.close(fig)
    moments = sorted([r for r in saved['thermal_results'] if r['order'] == 32], key=lambda r: r['T_K'])
    times = [r['T_K'] for r in moments]
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True, constrained_layout=True)
    axes[0].loglog(times, [r['kappa_cm3_per_s'] for r in moments], 'o-', color='#174b6b')
    axes[0].set_ylabel('Finite-window kappa [cm³/s]')
    axes[0].set_title('Four frozen common-T points; finite native source window')
    fig.supxlabel('Connecting lines are visual guides; no continuum certificate', fontsize=9)
    for h, color, label in [(0, '#b34a24', 'Fast residual (h=0)'),
                             (1, '#476f39', 'Instantaneous caloric birth (h=1)')]:
        rows = sorted([r for r in saved['owner_rows'] if r['h'] == h and
                       r['radiation_route'] == 'emissivity_handoff'], key=lambda r: r['T_K'])
        axes[1].semilogx([r['T_K'] for r in rows], [r['Cv_Tdot_over_R_eV'] for r in rows],
                         'o-', label=label, color=color)
    axes[1].axhline(0, color='0.5', lw=.7); axes[1].set_xlabel('Common temperature [K]')
    axes[1].set_ylabel('Cv Tdot / R [eV/event]'); axes[1].legend(); axes[1].grid(alpha=.2)
    for extension in ('png', 'pdf'):
        path = output/('finite_window_moments.'+extension)
        fig.savefig(path, dpi=180 if extension == 'png' else None); figures.append(path)
    plt.close(fig)
    receipt = {'schema': 'PHYS87_SAVED_RESULT_FIGURE_RECEIPT_V1',
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'input_RESULT_sha256': hashlib.sha256(raw).hexdigest(),
               'input_RESULT_path': str(args.result.resolve()),
               'figures': [{'filename': p.name, 'bytes': p.stat().st_size,
                            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in figures],
               'PNG_count': 2, 'PDF_count': 2, 'source_recomputations': 0,
               'scientific_integrations': 0, 'physical_uncertainty_bands': False,
               'connecting_lines': 'Visual guides through saved native knots/four T points, not evaluated native INT2 curves or continuum accuracy claims',
               'HH_R10': 'OFF', 'production_admission': 'NOT_ISSUED'}
    with (output/'FIGURE_RECEIPT.json').open('x') as f:
        json.dump(receipt, f, indent=2); f.write('\n')
    print(json.dumps({'status': 'SAVED_RESULT_FIGURES_CREATED', 'files': [p.name for p in figures],
                      'scientific_integrations': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
