#!/usr/bin/env python3
"""Render PHYS25 saved numerical candidate and a 241-point dual illustration.

No scientific main is invoked and no root is recomputed. The numerical helper
is imported only for original_fit_response at the 241 plotting energies.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

getcontext().prec = 160
ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'contributions/numerics/VARIANCE_CANDIDATE.json'
HELPER = ROOT / 'contributions/numerics/variance_candidate.py'
EXPECTED_RESULT = 'bb89271e705eae1db014fcb6371539af9e6496747e6cc288706c94dc87c71a63'
EXPECTED_HELPER = 'dd5cc8f5191bbefc039fabe0e92614c5a83a80fc44ebff4fdaca2235239699dd'
BASE = 'PHYS25_variance_cost'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'figures')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {extension: args.output_dir / (BASE + '.' + extension)
               for extension in ['png', 'pdf', 'json']}
    if any(path.exists() for path in outputs.values()):
        raise FileExistsError('refusing to overwrite first display output')
    if digest(RESULT) != EXPECTED_RESULT or digest(HELPER) != EXPECTED_HELPER:
        raise ValueError('frozen scientific input mismatch')
    data = json.loads(RESULT.read_text())
    spec = importlib.util.spec_from_file_location('phys25_display_helper', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    constants, dual = data['constants'], data['dual_contact_candidate']
    candidate = data['primary_candidate']
    a, b = map(D, constants['support_eV'])
    m = D(constants['mean_eV'])
    v = D(candidate['law'][1]['energy_eV'])
    probabilities = [D(item['probability']) for item in candidate['law']]
    jx, jw = D(constants['J_h2_x']), D(constants['J_h2_w'])
    l0 = D(dual['lambda0_eV2'])
    l1 = D(dual['lambda1_eV'])
    l2 = D(dual['lambda2_eV2_s4'])
    rows = []
    for i in range(241):
        e = a + (b-a)*D(i)/D(240)
        kval = helper.original_fit_response(e, jx, jw)['k_s-4']
        slack = (e-m)**2-l0-l1*(e-m)-l2*kval
        rows.append({'energy_eV': str(e), 'k_s-4': str(kval),
                     'dual_residual_eV2': str(slack)})
    record = {
        'task': 'REI-PHYS25-20261011',
        'purpose': 'display-only numerical illustration of a separately proved continuum result',
        'source_result_sha256': EXPECTED_RESULT,
        'source_helper_sha256': EXPECTED_HELPER,
        'figure_program_sha256': digest(Path(__file__)),
        'python_version': platform.python_version(),
        'matplotlib_version': matplotlib.__version__,
        'decimal_precision': getcontext().prec,
        'display_response_evaluations': 241,
        'new_root_iterations': 0,
        'new_scientific_main_invocations': 0,
        'old_scientific_main_invocations': 0,
        'scientific_checks_added': 0,
        'exact_candidate_definition': '(v-18)k(13.61)+(18-13.61)k(v)=0',
        'numerical_candidate': candidate,
        'dual_coefficients': dual,
        'residual_computation': '(E-m)^2-lambda0-lambda1*(E-m)-lambda2*k(E)',
        'rounding_policy': 'All raw Decimal display residuals are retained; no clipping to zero.',
        'exact_root_vs_midpoint': 'Curve uses saved numerical midpoint/contact coefficients; exact optimum is defined by its root, not the finite midpoint residual.',
        'scope': 'Frozen serialized numerical J; exact continuum sign and optimality require separate proofs; physical admission HOLD.',
        'rows': rows,
    }
    with outputs['json'].open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.titlesize': 12, 'axes.labelsize': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.linewidth': .8, 'xtick.direction': 'out', 'ytick.direction': 'out',
        'savefig.facecolor': 'white', 'figure.facecolor': 'white',
        'pdf.fonttype': 42, 'ps.fonttype': 42,
    })
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    fig.subplots_adjust(left=.075, right=.98, bottom=.225, top=.83, wspace=.29)
    ink, blue, orange, grid = '#213547', '#245b83', '#b66b21', '#dce3e8'
    fig.suptitle('HeIII sign reversal at fixed mean photon energy',
                 x=.52, y=.965, fontsize=15, fontweight='medium', color=ink)
    fig.text(.52, .900, r'$m=18\,\mathrm{eV}$, fixed photon number and initial gas',
             ha='center', fontsize=11, color='#52616b')

    for ax in (ax0, ax1):
        ax.set_xlim(float(a)-.38, float(b)+.25)
        ax.set_xlabel('Photon energy (eV)')
        ax.set_xticks([14, 16, 18, 20, 22, 24])
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.set_axisbelow(True)
        ax.grid(axis='y', color=grid, linewidth=.65)
        ax.tick_params(colors=ink)
        ax.spines['left'].set_color('#71808a')
        ax.spines['bottom'].set_color('#71808a')

    xs = [float(a), float(v)]
    ps = [float(p) for p in probabilities]
    ax0.vlines(xs, 0, ps, colors=blue, linewidth=2.5)
    ax0.scatter(xs, ps, s=60, color=blue, zorder=4)
    ax0.axvline(float(m), color=orange, linestyle=(0, (4, 3)), linewidth=1.3)
    ax0.text(float(m)+.16, .045, r'mean $18$ eV', color=orange, fontsize=10,
             rotation=90, va='bottom')
    ax0.text(xs[0]+.13, ps[0]+.025, r'$a=13.61$ eV' '\n' f'$p_a={ps[0]:.6f}$',
             color=blue, fontsize=10, linespacing=1.35)
    ax0.text(xs[1]-.06, ps[1]+.025, r'$v_*=21.72208$ eV' '\n' f'$p_v={ps[1]:.6f}$',
             color=blue, fontsize=10, ha='center', linespacing=1.35)
    ax0.set_ylim(0, .76)
    ax0.set_yticks([0, .2, .4, .6])
    ax0.set_ylabel('Photon-number probability')
    ax0.set_title('(a) Unique minimum-variance spectrum', loc='left', pad=13)
    ax0.text(.03, .965, r'$V_* = 16.33994465\ \mathrm{eV}^2$' '\n'
             r'$\sqrt{V_*} = 4.04226974\ \mathrm{eV}$',
             transform=ax0.transAxes, va='top', fontsize=10.5,
             color=ink, linespacing=1.45)

    ex = [float(row['energy_eV']) for row in rows]
    yy = [float(row['dual_residual_eV2']) for row in rows]
    ax1.axhline(0, color='#707c84', linewidth=.8)
    ax1.plot(ex, yy, color=blue, linewidth=2.2)
    ax1.fill_between(ex, yy, 0, color=blue, alpha=.08)
    contacts = [float(dual['contact_slack_a_eV2']), float(dual['contact_slack_v_eV2'])]
    ax1.scatter([float(a), float(v)], contacts, s=52, facecolor='white',
                edgecolor=blue, linewidth=1.6, zorder=5)
    ax1.annotate(r'$a$', (float(a), contacts[0]), xytext=(float(a)+.4, 1.0),
                 fontsize=11, color=blue,
                 arrowprops={'arrowstyle': '-', 'color': blue, 'linewidth': .8})
    ax1.annotate(r'$v_*$', (float(v), contacts[1]), xytext=(float(v)+.3, 1.15),
                 fontsize=11, color=blue,
                 arrowprops={'arrowstyle': '-', 'color': blue, 'linewidth': .8})
    ax1.set_ylim(-.45, 12.6)
    ax1.set_yticks([0, 3, 6, 9, 12])
    ax1.set_ylabel(r'Dual residual $h(E)$ (eV$^2$)')
    ax1.set_title('(b) Nonnegative dual residual', loc='left', pad=13)
    ax1.text(.98, .965, r'$h(E)\geq 0$' '\n' r'equality only at $a,\ v_*$',
             transform=ax1.transAxes, ha='right', va='top', fontsize=10.5,
             color=ink, linespacing=1.45)

    fig.text(.075, .080,
             'Curves and displayed roots are numerical illustrations; continuum positivity and optimality are proved separately.',
             fontsize=9.1, color='#52616b')
    fig.text(.075, .038,
             'Conditional on the frozen numerical Jacobian. Initial coefficient only; physical admission: HOLD.',
             fontsize=9.1, color='#52616b')
    fig.savefig(outputs['png'], dpi=240)
    fig.savefig(outputs['pdf'])
    plt.close(fig)
    print(json.dumps({
        'display_response_evaluations': 241, 'figure_main_invocations': 1,
        'scientific_main_invocations': 0, 'root_iterations': 0,
        'raw_display_min_residual_eV2': str(min(D(row['dual_residual_eV2']) for row in rows)),
        'outputs': {ext: {'path': str(path), 'sha256': digest(path),
                          'bytes': path.stat().st_size} for ext, path in outputs.items()}
    }, indent=2))


if __name__ == '__main__':
    main()
