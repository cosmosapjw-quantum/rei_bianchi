#!/usr/bin/env python3
"""One saved-RESULT-only figure child; no source or numerical supplier imports."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); raw = args.result.read_bytes(); saved = json.loads(raw)
    if saved['status'] != 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' or saved['failures']:
        raise ValueError('COMPLETE_PASSED_SAVED_PRIMARY_REQUIRED')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    os.environ['MPLCONFIGDIR'] = str(output/'.mpl_config')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.bbox': 'tight', 'pdf.fonttype': 42})
    colors = {'LAB_ANCHORED': '#145d80', 'FIXED_COM_K': '#b24a2b'}
    figures = []
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.4), constrained_layout=True)
    for mapping in saved['mapping_knots']:
        name = mapping['map']; rows = mapping['knots']
        axes[0].loglog([r['native_Es_eV'] for r in rows], [r['bare_Eb_eV'] for r in rows],
                       color=colors[name], label=name)
        axes[1].semilogx([r['native_Es_eV'] for r in rows],
            [(r['bare_Eb_eV']/r['native_Es_eV']-1)*1e6 for r in rows], color=colors[name], label=name)
    axes[0].set(xlabel='Original native source Es [eV]', ylabel='Mapped bare LAB Eb [eV]',
                title='Two explicit conditional kernel-transport maps')
    axes[1].set(xlabel='Original native source Es [eV]', ylabel='(Eb / Es - 1) [ppm]')
    for axis in axes:
        axis.legend(); axis.grid(alpha=.2)
    fig.supxlabel('Native knots; connecting lines are visual guides. Map differences are not uncertainty bounds.', fontsize=8)
    for ext in ('png', 'pdf'):
        path = output/('conditional_maps.'+ext)
        fig.savefig(path, dpi=180 if ext == 'png' else None); figures.append(path)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.4), constrained_layout=True)
    for name, color in colors.items():
        rows = sorted([r for r in saved['thermal_results'] if r['map'] == name and r['order'] == 32],
                      key=lambda r: r['T_K'])
        axes[0].loglog([r['T_K'] for r in rows], [r['kappa_cm3_per_s'] for r in rows], 'o-',
                       color=color, label=name)
        for h, style in ((0, '-'), (1, '--')):
            owned = sorted([r for r in saved['owner_rows'] if r['map'] == name and r['h'] == h and
                            r['radiation_route'] == 'emissivity_handoff'], key=lambda r: r['T_K'])
            axes[1].semilogx([r['T_K'] for r in owned], [r['Cv_Tdot_over_R_eV'] for r in owned],
                            'o'+style, color=color, label=name+', h='+str(h))
    parent = sorted(saved['parent_saved_order32_rows'], key=lambda r: r['T_K'])
    axes[0].loglog([r['T_K'] for r in parent], [r['kappa_cm3_per_s'] for r in parent], 's:',
                   color='#626262', label='Saved PHYS87 atomic-native baseline')
    axes[0].set(xlabel='Common temperature [K]', ylabel='Conditional finite-window kappa [cm³/s]',
                title='Saved four-temperature moments; distinct bare-map supports')
    axes[1].set(xlabel='Common temperature [K]', ylabel='Cv Tdot / R [eV/event]')
    axes[1].axhline(0, color='.5', lw=.6)
    for axis in axes:
        axis.legend(fontsize=8); axis.grid(alpha=.2)
    fig.supxlabel('Connecting lines are visual guides; h=1 is instantaneous caloric birth, not stopping.', fontsize=8)
    for ext in ('png', 'pdf'):
        path = output/('conditional_bare_moments.'+ext)
        fig.savefig(path, dpi=180 if ext == 'png' else None); figures.append(path)
    plt.close(fig)
    receipt = {'schema': 'PHYS88_SAVED_RESULT_FIGURE_RECEIPT_V1',
        'input_RESULT_path': str(args.result.resolve()), 'input_RESULT_sha256': hashlib.sha256(raw).hexdigest(),
        'figures': [{'filename': f.name, 'bytes': f.stat().st_size,
                     'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in figures],
        'PNG_count': 2, 'PDF_count': 2, 'source_recomputations': 0, 'scientific_integrations': 0,
        'source_native_knots_and_T_lines': 'Visual guides; no mapped-knot native reinterpolation or continuum claim',
        'map_difference_is_uncertainty_band': False, 'HH_R10': 'OFF', 'production_admission': 'NOT_ISSUED'}
    with (output/'FIGURE_RECEIPT.json').open('x', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': 'SAVED_RESULT_FIGURES_CREATED', 'files': [f.name for f in figures],
                      'scientific_integrations': 0}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
