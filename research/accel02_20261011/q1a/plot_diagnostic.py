#!/usr/bin/env python3
"""Create a provenance-bound failed-Q1A diagnostic; saved JSON only, no ODE.

Usage: plot_diagnostic.py G1_FINE G2_FINE SPECTRAL_COMPARISON.json OUTPUT_PREFIX
Creates OUTPUT_PREFIX.pdf, .png and .provenance.json without replacing files.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
LABELS = {
    'xHII': r'$x_{\rm HII}$', 'xHeII': r'$x_{\rm HeII}$', 'xHeIII': r'$x_{\rm HeIII}$',
    'T_K': r'$T$', 'ne_cm3': r'$n_e$', 'photon_cm3': r'$n_\gamma$',
    'GammaHI_s': r'$\Gamma_{\rm HI}$', 'GammaHeI_s': r'$\Gamma_{\rm HeI}$',
    'GammaHeII_s': r'$\Gamma_{\rm HeII}$',
    'source_number_ref_cm3_s': r'Source $N$, ref',
    'source_energy_ref_erg_cm3_s': r'Source $E$, ref',
    'source_number_proper_cm3_s': r'Source $N$, proper',
    'source_energy_proper_erg_cm3_s': r'Source $E$, proper',
    'cumulative_source_number_ref_cm3': r'Cumulative source $N$',
    'cumulative_source_energy_ref_erg_cm3': r'Cumulative source $E$',
    'radiation_energy_ref_erg_cm3': r'Radiation $E$, ref',
    'radiation_energy_proper_erg_cm3': r'Radiation $E$, proper',
    'photoheat_HI_per_absorber_erg_s': r'HI heat / absorber',
    'photoheat_HeI_per_absorber_erg_s': r'HeI heat / absorber',
    'photoheat_HeII_per_absorber_erg_s': r'HeII heat / absorber',
    'photoheat_HI_proper_erg_cm3_s': r'HI heat, proper',
    'photoheat_HeI_proper_erg_cm3_s': r'HeI heat, proper',
    'photoheat_HeII_proper_erg_cm3_s': r'HeII heat, proper',
    'total_photoheat_proper_erg_cm3_s': r'Total heat, proper',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def bind_saved_inputs(coarse, fine, comparison_path):
    comparison = read(comparison_path)
    if comparison['kind'] != 'spectral' or comparison['status'] != 'SPECTRAL_REFINEMENT_FAIL':
        raise ValueError('THIS_FIGURE_REQUIRES_ACTUAL_SPECTRAL_REFINEMENT_FAIL')
    if comparison['frozen_field_budget'] != 1e-3:
        raise ValueError('FROZEN_SPECTRAL_BUDGET_MISMATCH')
    recorded = comparison['files']
    inputs = {str(comparison_path.resolve()): sha(comparison_path)}
    results, identities = [], []
    for run in (coarse, fine):
        for name in ('RESULT.json', 'IDENTITY.json', 'MOMENTS.json', 'GRID.json', 'history.npz'):
            path = run/name
            digest = sha(path)
            # Comparator paths may be repository-relative or absolute. After
            # relocation, a matching run-directory/file suffix is sufficient
            # only when its recorded byte digest also matches exactly.
            candidates = [value for key, value in recorded.items()
                if Path(key).parts[-2:] == (run.name, name)]
            if candidates != [digest]:
                raise ValueError('COMPARISON_INPUT_BINDING:'+str(path))
            inputs[str(path.resolve())] = digest
        result, identity = read(run/'RESULT.json'), read(run/'IDENTITY.json')
        if result['status'] != 'COMPUTED_NOT_REVIEWED' or len(result['history']) != 129:
            raise ValueError('COMPLETED_129_EPOCH_RUN_REQUIRED:'+str(run))
        results.append(result)
        identities.append(identity)
    time = [np.array([row['time_s'] for row in result['history']]) for result in results]
    redshift = [np.array([row['z'] for row in result['history']]) for result in results]
    if (not np.array_equal(time[0], time[1]) or not np.array_equal(redshift[0], redshift[1])
        or np.any(np.diff(time[0]) <= 0.) or np.any(np.diff(redshift[0]) >= 0.)):
        raise ValueError('SHARED_PROPER_TIME_OR_MEAN_REDSHIFT_MISMATCH')
    if identities[0]['grid_order'] != 1 or identities[1]['grid_order'] != 2:
        raise ValueError('Q1A_GRID_ORDER_PAIR_REQUIRED')
    if any(identity['args']['shear'] != 0. for identity in identities):
        raise ValueError('THIS_FIGURE_IS_FOR_THE_Q1A_FLRW_PAIR')
    if set(comparison['comparisons']) != {'65', '129'}:
        raise ValueError('BOTH_FROZEN_EPOCH_SETS_REQUIRED')
    for count in ('65', '129'):
        if set(comparison['comparisons'][count]['fields']) != set(LABELS):
            raise ValueError('ALL_24_SPECTRAL_FIELDS_REQUIRED')
    return results, identities, comparison, redshift[0], inputs


def positive(values):
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all() or np.any(values < 0.):
        raise ValueError('NONFINITE_OR_NEGATIVE_LOG_DIAGNOSTIC')
    return np.ma.masked_less_equal(values, 0.)


def make_plot(results, identities, comparison, z):
    colors = {'H': '#1768ac', 'HeI': '#b05b18', 'HeII': '#6b4694', 'E': '#1768ac', 'N': '#b05b18'}
    fig, axes = plt.subplots(3, 2, figsize=(17., 15.),
        gridspec_kw={'height_ratios': [1., 1., 1.65], 'hspace': .38, 'wspace': .34})
    styles = ('-', '--')
    run_labels = [f"G1: {identities[0]['args']['energy']} energy nodes",
                  f"G2: {identities[1]['args']['energy']} energy nodes"]
    def series(result, key):
        values = np.array([row[key] for row in result['history']], dtype=float)
        if not np.isfinite(values).all():
            raise ValueError('NONFINITE_PLOT_FIELD:'+key)
        return values
    for result, style in zip(results, styles):
        axes[0, 0].plot(z, series(result, 'xHII'), style, color=colors['H'], lw=1.5)
        axes[0, 1].plot(z, series(result, 'xHeII'), style, color=colors['HeI'], lw=1.5)
        axes[0, 1].plot(z, series(result, 'xHeIII'), style, color=colors['HeII'], lw=1.5)
        axes[1, 0].semilogy(z, positive(series(result, 'T_K')), style, color=colors['H'], lw=1.5)
        for key, color in [('GammaHI_s', colors['H']), ('GammaHeI_s', colors['HeI']), ('GammaHeII_s', colors['HeII'])]:
            axes[1, 1].semilogy(z, positive(series(result, key)), style, color=color, lw=1.5)
        for key, color in [('energy_ledger_scaled', colors['E']), ('number_ledger_scaled', colors['N'])]:
            axes[2, 0].semilogy(z, positive(abs(series(result, key))), style, color=color, lw=1.2)
    titles = [('Hydrogen ionization', r'$x_{\rm HII}$'),
              ('Helium ionization', 'Fraction per helium nucleus'),
              ('Gas temperature', r'$T\ [{\rm K}]$'),
              ('Photoionization rates', r'$\Gamma\ [{\rm s}^{-1}]$'),
              ('Conservation residuals at saved epochs', 'Absolute normalized residual')]
    for ax, (title, ylabel) in zip(axes.flat, titles):
        ax.set(title=title, ylabel=ylabel, xlabel=r'Mean redshift $z_{\rm mean}$')
        ax.set_xlim(float(z[0]), float(z[-1]))
        ax.grid(True, alpha=.23, lw=.6)
        ax.tick_params(labelsize=9)
    axes[0, 0].set_ylim(-.015, 1.015)
    axes[0, 1].set_ylim(-.015, 1.015)
    axes[0, 0].legend([Line2D([], [], color=colors['H'], linestyle=style) for style in styles], run_labels,
                      loc='best', fontsize=9, frameon=False)
    axes[0, 1].legend([Line2D([], [], color=colors['HeI']), Line2D([], [], color=colors['HeII'])],
                      [r'$x_{\rm HeII}$', r'$x_{\rm HeIII}$'], frameon=False, fontsize=10)
    axes[1, 1].legend([Line2D([], [], color=colors[key]) for key in ('H', 'HeI', 'HeII')],
                      ['HI', 'HeI', 'HeII'], frameon=False, fontsize=9, ncol=3)
    axes[2, 0].axhline(1e-9, color='#8d1b23', linestyle=':', lw=1.5)
    axes[2, 0].legend([Line2D([], [], color=colors['E']), Line2D([], [], color=colors['N']),
                       Line2D([], [], color='#8d1b23', linestyle=':')],
                      [r'Energy / initial energy', r'Number / initial $n_{\rm H}$', r'Frozen bound $10^{-9}$'],
                      frameon=False, fontsize=9, loc='upper left')
    ledger_lines = []
    for label, result in zip(('G1', 'G2'), results):
        ledger_lines.append(f"{label} endpoint+sample maxima: E={result['max_energy_ledger']:.3e}, N={result['max_number_ledger']:.3e}")
    axes[2, 0].text(.025, .025, '\n'.join(ledger_lines), transform=axes[2, 0].transAxes,
                    fontsize=8, va='bottom', bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .85})

    ax = axes[2, 1]
    fields = comparison['comparisons']
    error_rows = []
    for key in LABELS:
        values = [fields[count]['fields'][key] for count in ('65', '129')]
        value = max(row['scaled_error'] for row in values)
        failed = any(not row['pass_budget'] for row in values)
        if not np.isfinite(value) or value < 0.:
            raise ValueError('INVALID_RECORDED_SPECTRAL_METRIC:'+key)
        error_rows.append((key, value, failed))
    error_rows.sort(key=lambda row: row[1], reverse=True)
    positive_errors = [row[1] for row in error_rows if row[1] > 0.]
    floor = min([1e-5]+positive_errors)/3.
    ax.set_xscale('log')
    for j, (_, value, failed) in enumerate(error_rows):
        if value > 0.:
            ax.barh(j, max(value-floor, 0.), left=floor, height=.7,
                    color='#b32830' if failed else '#34795d', alpha=.85)
        else:
            ax.text(floor, j, ' exact zero', va='center', fontsize=7)
    ax.set_yticks(range(len(error_rows)), [LABELS[row[0]] for row in error_rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(floor, max([1e-3]+positive_errors)*2.)
    ax.axvline(1e-3, color='#252525', linestyle=':', lw=1.4)
    ax.set(title='Spectral discrepancy: all 24 frozen fields',
           xlabel=r'Maximum of 65/129-epoch errors; frozen bound $10^{-3}$')
    ax.grid(True, axis='x', alpha=.2)
    ax.text(.02, -.14, 'Each epoch set uses its own fine-history amplitude.\nRed = failed in either set; green = passed in both.',
            transform=ax.transAxes, fontsize=8, va='top')
    fig.suptitle('NUMERICAL DIAGNOSTIC — SPECTRAL ACCEPTANCE FAILED',
                 fontsize=18, fontweight='bold', color='#92232a', y=.975)
    fig.text(.5, .948, 'Conditional FLRW HM12 primary-only Case A | G1 solid; G2 dashed | unchanged physical band 10–50000 eV',
             ha='center', fontsize=11)
    fig.subplots_adjust(top=.91, bottom=.10)
    fig.text(.075, .025,
        'All curves use the same 129 proper-time epochs over mean z = 15.9 → 4. Mean redshift is the background scale-factor redshift, not observer redshift.\n'
        'Prescribed isotropic CMB bath; conditional cold initial gas. No CR/RCT, Bianchi signal, continuum error certificate, or BASS visibility admission.\n'
        'Logarithmic panels omit exact zero values. Passing ledger bounds does not establish spectral convergence.', fontsize=9, va='bottom')
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('coarse', type=Path)
    parser.add_argument('fine', type=Path)
    parser.add_argument('comparison', type=Path)
    parser.add_argument('output_prefix', type=Path)
    args = parser.parse_args()
    outputs = {kind: Path(str(args.output_prefix)+suffix)
               for kind, suffix in [('pdf', '.pdf'), ('png', '.png'), ('provenance', '.provenance.json')]}
    for path in outputs.values():
        if path.exists():
            raise FileExistsError(path)
    if not args.output_prefix.parent.is_dir():
        raise FileNotFoundError(args.output_prefix.parent)
    results, identities, comparison, z, inputs = bind_saved_inputs(args.coarse, args.fine, args.comparison)
    figure = make_plot(results, identities, comparison, z)
    buffers = {}
    for kind in ('pdf', 'png'):
        stream = io.BytesIO()
        figure.savefig(stream, format=kind, dpi=170, facecolor='white')
        buffers[kind] = stream.getvalue()
    plt.close(figure)
    provenance = dict(schema='rei.q1a.failed_spectral_plot.v1',
        status='NUMERICAL_DIAGNOSTIC_SPECTRAL_ACCEPTANCE_FAILED',
        script_sha256=sha(__file__), source_file_sha256=inputs,
        output_sha256={kind: hashlib.sha256(data).hexdigest() for kind, data in buffers.items()},
        matplotlib_version=matplotlib.__version__,
        ODE_calls=0, native_calls=0, old_reference_replays=0,
        grid_order=[identity['grid_order'] for identity in identities],
        grid_arrays_sha256=[identity['grid_arrays_sha256'] for identity in identities],
        physical_time_convention='proper time since initial mean z15.9; shared129 epochs',
        x_axis='mean scale-factor redshift, reversed15.9to4; not observer redshift',
        spectral_bar_metric='max of recorded65/129 scaled errors, each normalized by its own fine-history amplitude',
        error_bar_zero_semantics='Exact zero displayed as text; no artificial nonzero error assigned',
        state_zero_semantics='Exact zero masked only on logarithmic display; saved data unchanged',
        scope='Conditional FLRW source-band-limited10to50000eV HM12 primary-only CaseA HHe, prescribed isotropic CMB bath. No CR/RCT, anisotropy signal, continuum guarantee or BASS visibility admission.',
        scientific_promotion=False)
    for kind in ('pdf', 'png'):
        with outputs[kind].open('xb') as handle:
            handle.write(buffers[kind])
    with outputs['provenance'].open('x') as handle:
        json.dump(provenance, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'status': provenance['status'], 'outputs': {k: str(v) for k, v in outputs.items()},
                      'sha256': provenance['output_sha256']}, indent=2))


if __name__ == '__main__':
    main()
