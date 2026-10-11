#!/usr/bin/env python3
"""Render the restored, rejected G1 history; no provider/native/ODE invocation.

Only saved data and their existing MOMENTS/review identities are consumed.
Outputs are create-only PDF, PNG and provenance JSON.
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
import numpy as np

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def saved_inputs(run, review_path):
    moments, result, identity = [read(run/name) for name in ('MOMENTS.json', 'RESULT.json', 'IDENTITY.json')]
    review = read(review_path)
    require(moments['status'] == 'POSTPROCESSED_NO_ODE_NO_PROMOTION', 'BOUND_SAVED_MOMENTS_REQUIRED')
    require(result['status'] == 'COMPUTED_NOT_REVIEWED'
            and result['checks']['whole_interval'] is True and len(result['history']) == 129,
            'FULL_129_EPOCH_G1_REQUIRED')
    required = {'RESULT.json', 'IDENTITY.json', 'history.npz', 'EVENTS.json', 'GRID.json',
                'driver_as_run.py', 'base_driver_as_run.py', 'fixed_grid_as_run.py',
                'characteristics_as_run.py', 'events_as_run.py'}
    require(required.issubset(moments['saved_file_sha256']), 'INCOMPLETE_MOMENT_BINDINGS')
    inputs = {}
    for name, expected in moments['saved_file_sha256'].items():
        path = run/name
        require(path.is_file() and sha(path) == expected, 'MISSING_OR_CHANGED_BOUND_INPUT:'+str(path))
        inputs[str(path.resolve())] = expected
    require(sha(HERE/'postprocess.py') == moments['implementation_sha256'], 'PINNED_POSTPROCESS_CHANGED')
    for name, expected in review['identities'].items():
        require(sha(run/name) == expected, 'SAVED_INDEPENDENT_REVIEW_BINDING:'+name)
    geometry_path = run/moments['geometry_preflight']['relative_path']
    require(sha(geometry_path) == moments['geometry_preflight']['sha256'], 'GEOMETRY_PREFLIGHT_CHANGED')
    require(result['checks']['number_ledger'] is False and review['checks']['number_gate'] is False
            and result['max_number_ledger'] == review['number_max'] > 1e-9,
            'RECORDED_NUMBER_LEDGER_REJECTION_REQUIRED')
    require(result['checks']['energy_ledger'] is True and review['checks']['energy_gate'] is True
            and result['max_energy_ledger'] == review['energy_max'] <= 1e-9,
            'RECORDED_ENERGY_GATE_MISMATCH')
    require('continuation' not in identity and identity['grid_order'] == 1
            and identity['args']['shear'] == 0., 'ORIGINAL_Q1A_G1_FLRW_REQUIRED')
    with np.load(run/'history.npz', allow_pickle=False) as archive:
        require(np.array_equal(archive['u'], np.linspace(0., 1., 129)), 'SAVED_FULL_INTERVAL_EPOCH_GRID')
    require(len(moments['history']) == 129 and
            np.array_equal([r['time_s'] for r in moments['history']], [r['time_s'] for r in result['history']]),
            'SAVED_MOMENT_EPOCH_MISMATCH')
    z = np.array([row['z'] for row in result['history']])
    require(np.isfinite(z).all() and np.all(np.diff(z) < 0.)
            and abs(z[0]-15.9) <= 1e-12 and abs(z[-1]-4.) <= 1e-12, 'FULL_MEAN_REDSHIFT_INTERVAL_REQUIRED')
    for path in (run/'MOMENTS.json', review_path, geometry_path, HERE/'postprocess.py'):
        inputs[str(path.resolve())] = sha(path)
    return result, identity, review, z, inputs


def make_plot(result, identity, z):
    fig, axes = plt.subplots(3, 2, figsize=(16., 12.),
        gridspec_kw={'hspace': .43, 'wspace': .25})
    blue, amber, purple, red = '#1768ac', '#b05b18', '#6b4694', '#a92530'
    def values(key):
        v = np.array([row[key] for row in result['history']])
        require(np.isfinite(v).all(), 'NONFINITE_SAVED_FIELD:'+key)
        return v
    def log_values(v):
        require(np.all(v >= 0.), 'NEGATIVE_LOG_DISPLAY_INPUT')
        return np.ma.masked_equal(v, 0.)
    axes[0, 0].plot(z, values('xHII'), color=blue, lw=1.7)
    axes[0, 0].set(title='Hydrogen ionization', ylabel=r'$x_{\rm HII}$', ylim=(-.015, 1.015))
    for key, label, color in [('xHeII', r'$x_{\rm HeII}$', amber), ('xHeIII', r'$x_{\rm HeIII}$', purple)]:
        axes[0, 1].plot(z, values(key), color=color, lw=1.7, label=label)
    axes[0, 1].set(title='Helium ionization', ylabel='Fraction per helium nucleus', ylim=(-.015, 1.015))
    axes[0, 1].legend(frameon=False, fontsize=10)
    axes[1, 0].semilogy(z, log_values(values('T_K')), color=blue, lw=1.7)
    axes[1, 0].set(title='Gas temperature', ylabel=r'$T\ [{\rm K}]$')
    for key, label, color in [('GammaHI_s', 'HI', blue), ('GammaHeI_s', 'HeI', amber), ('GammaHeII_s', 'HeII', purple)]:
        axes[1, 1].semilogy(z, log_values(values(key)), color=color, lw=1.7, label=label)
    axes[1, 1].set(title='Photoionization rates', ylabel=r'$\Gamma\ [{\rm s}^{-1}]$')
    axes[1, 1].legend(frameon=False, ncol=3, fontsize=10)
    for ax, key, maximum, title, ylabel, color in [
        (axes[2, 0], 'energy_ledger_scaled', result['max_energy_ledger'], 'Energy ledger: recorded gate passed',
         r'$|\mathcal{R}_E|/E_{\rm initial}$', blue),
        (axes[2, 1], 'number_ledger_scaled', result['max_number_ledger'], 'Photon-number ledger: recorded gate FAILED',
         r'$|\mathcal{R}_N|/n_{{\rm H,initial}}$', red)]:
        ax.semilogy(z, log_values(abs(values(key))), color=color, lw=1.6, label='Saved 129 epochs')
        ax.axhline(1e-9, color='#252525', linestyle=':', lw=1.4, label=r'Frozen bound $10^{-9}$')
        ax.set(title=title, ylabel=ylabel)
        ax.legend(loc='upper left', fontsize=9, frameon=True,
                  facecolor='white', edgecolor='none', framealpha=.97)
        ax.text(.02, .04, f'Recorded endpoint + sample maximum: {maximum:.6e}',
                transform=ax.transAxes, fontsize=9, va='bottom', color=color,
                bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .85})
    for ax in axes.flat:
        ax.set_xlim(float(z[0]), float(z[-1]))
        ax.set_xlabel(r'Mean redshift $z_{\rm mean}$')
        ax.grid(True, alpha=.22, linewidth=.6)
    fig.suptitle('FULL-INTERVAL NUMERICAL DIAGNOSTIC — REJECTED: PHOTON-NUMBER LEDGER',
                 color=red, fontsize=15.5, fontweight='bold', y=.98)
    fig.text(.5, .946,
        f"GAUSS1_FINE | {identity['args']['energy']} energy × {identity['args']['angle']} angular nodes | "
        'Spectral/time acceptance unavailable | Scientific admission: false',
        ha='center', fontsize=10.5)
    fig.subplots_adjust(top=.897, bottom=.115)
    fig.text(.075, .025,
        'Restored saved history only: common proper-time epochs span mean z = 15.9 → 4. Mean redshift is a background scale-factor coordinate, not observer redshift.\n'
        'Conditional FLRW HM12 primary-only Case A H/He, source band 10–50000 eV, prescribed isotropic CMB bath. No CR/RCT, Bianchi signal or BASS visibility admission.\n'
        'Curves display recorded data; exact zeros are omitted only on logarithmic axes. No new physical solution or convergence certificate is produced.',
        fontsize=8.5, va='bottom')
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, default=HERE/'evidence/GAUSS1_FINE')
    parser.add_argument('--review', type=Path, default=HERE/'review/G1_FINE_SAVED_AUDIT.json')
    parser.add_argument('--output-prefix', type=Path, default=HERE/'figures/G1_REJECTED_HISTORY')
    args = parser.parse_args()
    paths = {kind: Path(str(args.output_prefix)+extension) for kind, extension in
             [('pdf', '.pdf'), ('png', '.png'), ('provenance', '.provenance.json')]}
    for path in paths.values():
        if path.exists():
            raise FileExistsError(path)
    result, identity, review, z, inputs = saved_inputs(args.run, args.review)
    fig = make_plot(result, identity, z)
    rendered = {}
    for kind in ('pdf', 'png'):
        buffer = io.BytesIO()
        fig.savefig(buffer, format=kind, dpi=160, facecolor='white')
        rendered[kind] = buffer.getvalue()
    plt.close(fig)
    provenance = dict(schema='rei.q1a.restored_g1_rejected_plot.v1',
        status='FULL_INTERVAL_DIAGNOSTIC_REJECTED_PHOTON_NUMBER_LEDGER',
        scientific_admission=False, spectral_acceptance='UNAVAILABLE', time_acceptance='UNAVAILABLE',
        native_calls=0, provider_initializations=0, ODE_calls=0, reference_replays=0, new_physics_calculations=0,
        plot_script_sha256=sha(__file__), source_file_sha256=inputs,
        plot_output_sha256={kind: hashlib.sha256(data).hexdigest() for kind, data in rendered.items()},
        recorded_number_ledger_max=result['max_number_ledger'], recorded_energy_ledger_max=result['max_energy_ledger'],
        frozen_energy_and_number_budget=1e-9, existing_review_all_checks=review['all_checks'],
        existing_review_sha256=sha(args.review), matplotlib_version=matplotlib.__version__,
        full_saved_epoch_count=129, mean_redshift_endpoints=[float(z[0]), float(z[-1])],
        provenance_operation='Verified existing MOMENTS and review file bindings; no provider execution or replacement input',
        physical_time='proper-time samples since initial mean z15.9; same saved epochs throughout',
        display='Mean redshift decreases15.9to4. Log panels mask exact zero for display only; no stored value changed.',
        scope='Conditional FLRW HM12 primary-only CaseA HHe10to50000eV source band, isotropic CMB bath; no CR/RCT, Bianchi signal, continuum certificate or BASS visibility admission')
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    for kind in ('pdf', 'png'):
        with paths[kind].open('xb') as handle:
            handle.write(rendered[kind])
    with paths['provenance'].open('x') as handle:
        json.dump(provenance, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'status': provenance['status'], 'outputs': {kind: str(path) for kind, path in paths.items()},
                      'sha256': provenance['plot_output_sha256']}, indent=2))


if __name__ == '__main__':
    main()
