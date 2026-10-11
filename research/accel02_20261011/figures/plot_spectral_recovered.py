#!/usr/bin/env python3
"""Plot saved 128/256-grid histories and frozen spectral metric; no ODE calls."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
COARSE = BASE / 'n2/evidence/EVENT_COUPLED002/RESULT.json'
FINE = BASE / 'n2/evidence/EVENT_COUPLED003_RECOVERED/RESULT.json'
COMPARISON = BASE / 'n2/evidence/EVENT_SPECTRAL_COMPARISON_RECOVERED.json'
FIELDS = ['xHII', 'xHeII', 'xHeIII', 'T_K', 'ne_cm3', 'photon_cm3',
          'GammaHI_s', 'GammaHeI_s', 'GammaHeII_s']
LABELS = ['H II', 'He II', 'He III', 'T', 'n_e', 'n_gamma',
          'Gamma HI', 'Gamma HeI', 'Gamma HeII']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = [json.loads(path.read_text()) for path in (COARSE, FINE)]
    comparison = json.loads(COMPARISON.read_text())
    histories = [record['history'] for record in records]
    epochs = [np.array([row['time_s'] for row in rows]) for rows in histories]
    if len(epochs[0]) != 129 or not np.array_equal(*epochs):
        raise ValueError('Expected 129 exact shared output epochs')
    budget = comparison['frozen_field_budget']
    if budget != 1e-3:
        raise ValueError('Protected spectral budget differs from 1e-3')
    metrics = comparison['comparisons']['129']['fields']
    for field in FIELDS:
        aa, bb = [np.array([row[field] for row in rows]) for rows in histories]
        amplitude = max(abs(bb))
        error = max(abs(aa-bb)) / amplitude if amplitude else max(abs(aa-bb))
        if not np.isclose(error, metrics[field]['scaled_error'], rtol=2e-14, atol=0):
            raise ValueError('Figure/comparison mismatch: ' + field)
    passed = all(metrics[field]['pass_budget'] for field in FIELDS)
    verdict = 'PASS' if passed else 'FAIL'
    plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .18,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    colors = ['#186FAF', '#E48B1C', '#8A52A1']
    for i, rows in enumerate(histories):
        z = np.array([row['z'] for row in rows])
        style = '-' if i == 0 else '--'
        def column(key):
            return np.array([row[key] for row in rows])
        for field, label, color in zip(FIELDS[:3], LABELS[:3], colors):
            axes[0, 0].plot(z, column(field), color=color, ls=style, lw=1.9,
                            label=label if i == 0 else None)
        axes[0, 1].plot(z, column('T_K'), color='#B64241', ls=style, lw=1.9)
        for field, label, color in zip(FIELDS[-3:], ['H I', 'He I', 'He II'], colors):
            axes[1, 0].semilogy(z, column(field), color=color, ls=style, lw=1.7,
                               label=label if i == 0 else None)
    axes[0, 0].set(ylabel='Homogeneous ionic fraction', ylim=(-.015, 1.035))
    axes[0, 0].legend(frameon=False, ncol=3)
    axes[0, 1].set(ylabel='Gas temperature [K]')
    axes[1, 0].set(ylabel=r'Photoionization rate $\Gamma$ [s$^{-1}$]')
    axes[1, 0].legend(frameon=False, ncol=3)
    for ax in [axes[0, 0], axes[0, 1], axes[1, 0]]:
        ax.set(xlim=(15.9, 4), xlabel=r'Mean-scale-factor redshift $z_a$')
    errors = [metrics[field]['scaled_error'] for field in FIELDS]
    axes[1, 1].barh(LABELS, errors,
        color=['#197E69' if v <= budget else '#BC4C44' for v in errors])
    axes[1, 1].set_xscale('log')
    axes[1, 1].axvline(budget, color='#353B43', ls='--', lw=1.1)
    axes[1, 1].set(xlabel='Max difference / fine-grid history amplitude',
                    title=f'128 → 256 energy nodes: {verdict} at frozen 10⁻³ target')
    axes[1, 1].invert_yaxis()
    axes[1, 1].grid(axis='y', visible=False)
    legend = [Line2D([0], [0], color='#303740', lw=2, ls='-', label='128 × 2'),
              Line2D([0], [0], color='#303740', lw=2, ls='--', label='256 × 2, recovered raw run')]
    fig.legend(handles=legend, loc='upper right', bbox_to_anchor=(.98, .952),
               frameon=False, ncol=2)
    fig.suptitle('Conditional native reionization: full-interval spectral diagnostic',
                 fontsize=16, x=.075, ha='left', y=.988)
    fig.text(.075, .945, 'FLRW r=0 | HM12 10–50,000 eV | Case A | z = 15.9 → 4', fontsize=10)
    fig.text(.075, .018,
        'Saved actual histories; solid 128 and dashed 256 energy nodes, two angular nodes each.\n'
        'Finite-grid comparison only. CR/RCT/secondary cascades OFF; isotropic CMB bath; no continuum or observational claim.',
        fontsize=9, color='#50545A')
    fig.tight_layout(rect=(.015, .072, 1, .922))
    outputs = [HERE / 'NATIVE_SPECTRAL_RECOVERED_128_256.png',
               HERE / 'NATIVE_SPECTRAL_RECOVERED_128_256.svg']
    fig.savefig(outputs[0], dpi=170)
    fig.savefig(outputs[1])
    plt.close(fig)
    outputs[1].write_text('\n'.join(s.rstrip() for s in outputs[1].read_text().splitlines())+'\n')
    provenance = {
        'schema': 'rei_accel02_spectral_figure_v1',
        'scope': 'Conditional full-interval finite-grid diagnostic; no continuum or observational admission',
        'solver_executions': 0,
        'source_files': {str(p.relative_to(BASE)): sha(p) for p in (COARSE, FINE, COMPARISON)},
        'plotter_sha256': sha(Path(__file__)),
        'output_files': {str(p.relative_to(BASE)): sha(p) for p in outputs},
        'shared_epoch_count': 129,
        'grid_styles': {'128x2': 'solid', '256x2_recovered': 'dashed'},
        'frozen_spectral_budget': budget,
        'plotted_nine_field_spectral_verdict': verdict,
        'comparison_status': comparison['status'],
        'promotion': 'Use independent review; this plot performs no promotion',
        'original_128_figure_modified': False,
    }
    (HERE / 'SPECTRAL_RECOVERED_FIGURE_PROVENANCE.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'figure': str(outputs[0]), 'comparison_status': comparison['status'],
                      'plotted_field_verdict': verdict, 'solver_executions': 0}))


if __name__ == '__main__':
    main()
