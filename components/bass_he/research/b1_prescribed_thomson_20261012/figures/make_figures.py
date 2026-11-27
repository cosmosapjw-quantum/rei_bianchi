"""Reproduce B1 overview from saved run outputs; executes no physics solver."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np


REPORT_Y = np.array([0.1, 0.3, 1.0, 3.0, 6.0, 10.0])
RUNS = {
    **{c: f'base_{c}_t128_mu24_e257' for c in ['F', 'M', 'B', 'B0', 'B_F', 'M_F']},
    **{f'{mode}_{c}': f'{mode}_{c}_t{t}_mu{mu}_e{e}'
       for mode, t, mu, e in [('time', 256, 24, 257),
                              ('angle', 128, 48, 257),
                              ('energy', 128, 24, 513)]
       for c in ['B', 'B_F']},
}


def read_runs(root: Path) -> dict[str, dict[str, np.ndarray]]:
    out = {}
    for key, directory in RUNS.items():
        run = root / directory
        receipt = json.loads((run / 'RECEIPT.json').read_text())
        if receipt['status'] != 'EXECUTED_SCOPED_PYTHON':
            raise ValueError(f'REQUIRED_COMPLETED_RUN:{directory}')
        if receipt['backend'] != 'EXPLICIT_EXISTING_BASS_PYTHON':
            raise ValueError(f'BACKEND_SCOPE_CHANGED:{directory}')
        raw = (run / 'result.npz').read_bytes()
        if hashlib.sha256(raw).hexdigest() != receipt['output_sha256']['result.npz']:
            raise ValueError(f'RUN_OUTPUT_IDENTITY_MISMATCH:{directory}')
        with np.load(run / 'result.npz', allow_pickle=False) as archive:
            out[key] = {k: archive[k].copy() for k in archive.files}
        data = out[key]
        if not np.allclose(data['y'][data['report_indices']], REPORT_Y, rtol=2e-15, atol=0):
            raise ValueError(f'REPORT_ENERGY_COORDINATES_CHANGED:{directory}')
    for c in ['M', 'B0', 'B_F', 'M_F']:
        if not np.array_equal(out[c]['u'], out['B']['u']) or not np.array_equal(out[c]['y'], out['B']['y']):
            raise ValueError(f'BASE_COMPARISON_GRID_MISMATCH:{c}')
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=Path, default=Path(__file__).resolve().parents[1] / 'runs')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    data = read_runs(args.runs)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 10.5,
        'axes.labelsize': 11, 'axes.titlesize': 11.5,
        'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in',
        'xtick.top': True, 'ytick.right': True, 'legend.frameon': False,
        'legend.fontsize': 9.5, 'lines.linewidth': 1.9,
        'pdf.fonttype': 42, 'ps.fonttype': 42,
        'savefig.facecolor': 'white',
    })
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.6))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.15, top=0.865,
                        hspace=0.40, wspace=0.27)
    fig.suptitle('B1: prescribed-history polarized photon transport',
                 fontsize=16, y=0.967)
    fig.text(0.5, 0.923,
             'Isotropic Planck initial field  |  LRS Bianchi I, initial s/H = +0.1  |  Existing Python Thomson backend',
             ha='center', fontsize=10.5, color='#444444')

    b = data['B']
    keep = (b['y'] >= 0.1*(1-1e-14)) & (b['y'] <= 10*(1+1e-14))
    y = b['y'][keep]
    y_label = r'$y=(a/a_i)\,E/(k_{\rm B}T_{\gamma,i})$'
    blue, orange, grey = '#1764A0', '#D17C26', '#737373'

    ax = axes[0, 0]
    ax.plot(y, data['B']['q2'][-1, keep], color=blue, label='B: Bianchi + Thomson')
    ax.plot(y, data['B0']['q2'][-1, keep], color=orange, ls='--', label='B0: same geometry, no scattering')
    ax.plot(y, data['M']['q2'][-1, keep], color=grey, ls=':', label='M: matched-H isotropic control')
    ax.set(xscale='log', xlim=(0.1, 10), xlabel=y_label, ylabel=r'$q_2$',
           title=r'(a) Directional quadrupole at $\bar z=4$')
    ax.legend(loc='lower left')

    ax = axes[0, 1]
    ax.plot(y, 100*data['B']['pL_equator'][-1, keep], color=blue)
    ax.set(xscale='log', xlim=(0.1, 10), ylim=(0, None), xlabel=y_label,
           ylabel=r'Equatorial $p_L$ [%]', title=r'(b) Linear polarization at $\bar z=4$')
    ax.text(0.04, 0.94, r'$\mu=0$, $p_L=\sqrt{Q_S^2+U_S^2}/I$',
            transform=ax.transAxes, va='top', fontsize=10.5, color='#444444')

    history = ((data['B']['q2'] - data['M']['q2'])
               - (data['B_F']['q2'] - data['M_F']['q2']))
    ax = axes[1, 0]
    history_colors = ['#305A91', '#3C8C81', '#C98427', '#A63E51']
    for value, color in zip([0.1, 1.0, 3.0, 10.0], history_colors):
        j = int(np.argmin(np.abs(b['y']-value)))
        ax.plot(b['z_mean'], 1e6*history[:, j], color=color, label=f'y = {value:g}')
    ax.axhline(0.0, color='#999999', lw=0.7)
    ax.set(xlim=(20, 4), xlabel=r'Mean-volume redshift $\bar z$',
           ylabel=r'$\delta_{\rm hist}q_2$ [$10^{-6}$]',
           title='(c) Electron-history response at fixed geometry')
    ax.legend(loc='lower left', ncol=2, columnspacing=1.4)

    report = b['report_indices']
    baseline = history[-1, report]
    null_difference = data['M']['q2'][-1, report] - data['M_F']['q2'][-1, report]
    variations = []
    for mode in ['time', 'angle', 'energy']:
        refined_b, refined_f = data[f'{mode}_B'], data[f'{mode}_B_F']
        # The same null control contribution cancels in a refinement difference.
        # No unperformed refined M/M_F run is fabricated here.
        refined = (refined_b['q2'][-1, refined_b['report_indices']]
                   - refined_f['q2'][-1, refined_f['report_indices']]
                   - null_difference)
        variations.append(np.abs(refined-baseline))
    empirical_variation = np.sum(variations, axis=0)
    if not np.all(empirical_variation > 0.0):
        raise ValueError('ZERO_REFINEMENT_VARIATION_REQUIRES_EXPLICIT_LOG_PLOT_TREATMENT')
    ax = axes[1, 1]
    ax.loglog(REPORT_Y, np.abs(baseline), 'o-', color=blue,
              markersize=5, label=r'$|\delta_{\rm hist}q_2|$')
    ax.loglog(REPORT_Y, empirical_variation, 's--', color=orange,
              markersize=4.7, label=r'$\sum_{t,\mu,E}|\Delta_{\rm refine}\delta_{\rm hist}q_2|$')
    ax.set(xlim=(0.08, 12.5), ylim=(2e-13, 4e-6), xlabel=y_label,
           ylabel=r'Absolute $q_2$ difference',
           title=r'(d) Final response and empirical numerical variation')
    ax.set_xticks(REPORT_Y)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:g}'))
    ax.legend(loc='center left')

    for ax in axes.flat:
        ax.grid(True, which='major', color='#E5E5E5', linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)
    fig.text(0.085, 0.083,
             r'$\delta_{\rm hist}q_2=(q_2^B-q_2^M)-(q_2^{B_F}-q_2^{M_F})$; '
             'all paired histories use the same B proper clock.',
             fontsize=10, color='#333333')
    fig.text(0.085, 0.054,
             'Panel (d): separate timestep, angle and energy refinements; their sum is an empirical sensitivity measure, not a rigorous error bound.',
             fontsize=9.5, color='#555555')
    fig.text(0.085, 0.028,
             r'Test-field, elastic Thomson result over mean-volume $z=20\rightarrow4$; no observer tail or observed CMB $C_\ell$ prediction.',
             fontsize=9.5, color='#555555')

    for extension in ['png', 'pdf']:
        path = args.output_dir / f'B1_overview.{extension}'
        fig.savefig(path, dpi=220 if extension == 'png' else None,
                    metadata={'Creator': 'B1 saved-output plotting script'})
        print(path)
    plt.close(fig)


if __name__ == '__main__':
    main()
