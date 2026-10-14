#!/usr/bin/env python3
"""Render the PHYS23 initial-coefficient map; grid is for display, not a proof."""
from __future__ import annotations

import argparse
from decimal import Decimal as D
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = [args.output_dir / ('PHYS23_spectral_initial_response.' + ext)
             for ext in ('json', 'png', 'pdf')]
    if any(p.exists() for p in paths):
        raise FileExistsError('refusing to overwrite figure evidence')
    numerical = ROOT / 'contributions/numerics/SPECTRAL_RESPONSE.json'
    raw = json.loads(numerical.read_text())
    module_path = ROOT / 'contributions/numerics/spectral_response.py'
    spec = importlib.util.spec_from_file_location('phys23_spectral_numerics', module_path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    inherited = json.loads(model.INPUT.read_text())['results']
    jac = [[D(x) for x in row] for row in inherited['baseline_local']['J_nonphoto']]
    lo, hi = D('13.61'), D('24.58')
    rows = [model.response(lo + (hi - lo) * D(i) / 160, jac) for i in range(161)]
    selected = ['energy_eV', 'HII_t3_s-3', 'w_t3_eV_H-1_s-3', 'T_t3_K_s-3',
                'HeII_t4_s-4', 'HeIII_t4_s-4', 'signed_curvature_ratio_eV']
    root = raw['HeIII_numerical_roots'][0]['midpoint_eV']
    data = {
        'task': 'REI-PHYS23-20261010',
        'purpose': '161-point rendering grid after exact sign structure was established; no validation-count credit',
        'input_result_sha256': hashlib.sha256(numerical.read_bytes()).hexdigest(),
        'evaluated_module_sha256': hashlib.sha256(module_path.read_bytes()).hexdigest(),
        'claim_scope': 'initial-time epsilon^2 coefficients with physical q and N0 included; no finite-time history',
        'HeIII_root_status': 'numerical input inherited-Jnp conditional',
        'HeIII_root_eV': root,
        'thermal_particle_cost_eV': raw['constants']['e_th_eV'],
        'HeIII_ratio_critical_eV': raw['HeIII_signed_ratio_critical_eV'],
        'rows': [{key: str(row[key]) for key in selected} for row in rows],
    }
    paths[0].write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.titleweight': 'bold', 'axes.labelsize': 11})
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.4))
    x = [float(row['energy_eV']) for row in rows]
    panels = [(axes[0, 0], 'HII_t3_s-3', 1e47, '#2463a5',
               'A  HII: negative throughout', r'$a_{3,x}\;[10^{-47}\,\mathrm{s}^{-3}]$'),
              (axes[0, 1], 'T_t3_K_s-3', 1e42, '#a42b75',
               'B  Temperature: negative throughout', r'$\theta_3\;[10^{-42}\,\mathrm{K}\,\mathrm{s}^{-3}]$'),
              (axes[1, 1], 'HeIII_t4_s-4', 1e64, '#b46612',
               'D  HeIII: one conditional sign transition', r'$a_{4,\mathrm{HeIII}}\;[10^{-64}\,\mathrm{s}^{-4}]$')]
    for ax, key, scale, color, title, ylabel in panels:
        ax.plot(x, [float(row[key]) * scale for row in rows], color=color, lw=2.5)
        ax.axhline(0, color='#5b6470', lw=0.9)
        ax.set(title=title, ylabel=ylabel)
    ax = axes[1, 0]
    ax.plot(x, [float(row['signed_curvature_ratio_eV']) for row in rows],
            color='#137b66', lw=2.5, label=r'$r(E)$')
    ax.axhline(float(raw['constants']['e_th_eV']), color='#a42b75', ls=':', lw=1.7,
               label=r'$e_{\mathrm{th},*}=6.463$ eV')
    ax.axhline(float(raw['HeIII_signed_ratio_critical_eV']), color='#b46612', ls='--', lw=1.4,
               label=r'$r_{\mathrm{HeIII}}=23.7905$ eV')
    ax.set(title='C  Signed curvature ratio: strictly increasing', ylabel=r'$r(E)\;[\mathrm{eV}]$')
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    ax.set_ylim(0, 73)
    ax = axes[1, 1]
    ax.axvline(float(root), color='#56616d', ls='--', lw=1.2)
    ax.annotate(r'$E_{\mathrm{HeIII}}\simeq15.43367$ eV',
                xy=(float(root), 0), xytext=(17.0, 1.1), fontsize=10,
                arrowprops={'arrowstyle': '-', 'color': '#56616d'})
    for ax in axes.flat:
        ax.set_xlim(float(lo), float(hi))
        ax.set_xlabel('Photon energy E [eV]')
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.grid(alpha=.18)
        ax.set_axisbelow(True)
        ax.title.set_fontsize(11)
    fig.suptitle('PHYS23 | Spectral dependence of the initial shear response',
                 fontsize=17, weight='bold', x=.065, ha='left', y=.985)
    fig.text(.065, .94,
             r'$T_*=50{,}000$ K; $N_0=0.05$ photon/H; $q\simeq2\times10^{-32}\ \mathrm{s}^{-2}$; '
             r'$[\epsilon^2]x=a_{3,x}t^3+\cdots$, $[\epsilon^2]h_2=a_{4,h_2}t^4+\cdots$',
             fontsize=10.5, color='#384350')
    fig.text(.065, .025,
             'Curves: analytic continuum evaluated on 161 display points. HII/T signs and r monotonicity: exact rational certificate.\n'
             'HeIII uses the inherited numerical local Jacobian. These coefficients do not certify finite-time histories.',
             fontsize=9.5, color='#384350')
    fig.subplots_adjust(left=.09, right=.98, top=.87, bottom=.13, hspace=.39, wspace=.27)
    fig.savefig(paths[1], dpi=160)
    fig.savefig(paths[2], metadata={'Title': 'PHYS23 spectral initial response', 'Author': 'REI research loop',
                                  'CreationDate': None, 'ModDate': None})
    plt.close(fig)
    print(json.dumps({'status': 'RENDERED', 'display_points': len(rows),
                      'scientific_validation_credit': 0, 'outputs': [str(p) for p in paths]}))


if __name__ == '__main__':
    main()
