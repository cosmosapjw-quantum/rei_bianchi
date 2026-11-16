#!/usr/bin/env python3
"""Plot saved physical diagnostics; no source evolution or fitting."""
from pathlib import Path
import hashlib
import json
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    started = time.perf_counter()
    source = HERE / 'results/stress_history.csv.gz'
    data = pd.read_csv(source)
    summary = json.loads((HERE/'results/STRESS_SUMMARY.json').read_text())
    output = HERE / 'figures'
    output.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 12,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none'})
    cases = ['ZERO', 'SHEAR_HALF_PLUS', 'SHEAR_HALF_MINUS', 'SHEAR_MINUS']
    colors = ['#777777', '#D55E00', '#009E73', '#0072B2']
    labels = [r'$q=0$', r'$q=+0.005$', r'$q=-0.005$', r'$q=-0.01$']
    fig, ax = plt.subplots(2, 2, figsize=(12.4, 8.7))
    fig.subplots_adjust(left=.08, right=.98, bottom=.17, top=.84,
                        wspace=.28, hspace=.48)
    fig.suptitle('Original REI IGM: radiation stress on the saved geometry',
                 fontsize=17, x=.08, ha='left', y=.98)
    fig.text(.08, .925, 'Mean redshift 20 to 4  |  4 actual histories  |  1,248,952 native states  |  4,004 plotted samples',
             fontsize=10, color='#444444')
    fig.legend([Line2D([], [], color=c, lw=2.2) for c in colors], labels,
               ncol=4, frameon=False, loc='upper left', bbox_to_anchor=(.073, .906))
    for case, color in zip(cases, colors):
        d = data[data.case == case]
        ax[0, 0].plot(d.zbar, 1e6*d.delta_s_total_over_H, color=color, lw=1.9)
        ax[0, 1].plot(d.zbar, 1e8*d.extra_energy_to_background, color=color, lw=1.9)
        if case != 'ZERO':
            for column, ls in [('delta_s_effective_over_H', '-'),
                               ('delta_s_ionizing_over_H', '--')]:
                values = np.abs(d[column].to_numpy())
                good = (values > 0) & (d.elapsed_Myr.to_numpy() > 0)
                ax[1, 0].plot(d.elapsed_Myr.to_numpy()[good]/1000,
                              values[good], color=color, ls=ls, lw=1.8)
    for a in ax.ravel():
        a.grid(alpha=.17)
        a.set_axisbelow(True)
    for a in ax[0]:
        a.set_xlim(20, 4)
        a.set_xticks([20, 16, 12, 8, 4])
        a.set_xlabel(r'Mean redshift $\bar z$')
    ax[0, 0].set_title('A  Forced shear response', loc='left', pad=12)
    ax[0, 0].set_ylabel(r'$10^6\,\delta s/H$')
    ax[0, 0].axhline(0, color='#777777', lw=.7)
    ax[0, 0].text(.02, .97, r'Original ceiling: $|\delta s/H|<10^{-4}$',
                  va='top', transform=ax[0, 0].transAxes, fontsize=9)
    ax[0, 0].set_ylim(-6.1, 13.0)
    ax[0, 1].set_title('B  Extra energy / background energy', loc='left', pad=12)
    ax[0, 1].set_ylabel(r'$10^8\,\epsilon_{\rm extra}/\epsilon_{\rm bg}$')
    ax[0, 1].set_ylim(0, 11.8)
    ax[0, 1].text(.02, .97, r'Original ceiling: $\epsilon_{\rm extra}/\epsilon_{\rm bg}<10^{-4}$',
                  va='top', transform=ax[0, 1].transAxes, fontsize=9)
    ax[1, 0].set_title('C  Stress contribution by radiation owner', loc='left', pad=12)
    ax[1, 0].set_xlabel('Elapsed proper time from mean redshift 20 [Gyr]')
    ax[1, 0].set_ylabel(r'$|\delta s_{\rm component}/H|$')
    ax[1, 0].set_yscale('log')
    ax[1, 0].set_ylim(1e-20, 4e-5)
    ax[1, 0].set_xlim(0, 1.36)
    ax[1, 0].legend([Line2D([], [], color='#444444'), Line2D([], [], color='#444444', ls='--')],
                    [r'Effective $\Omega_r$ fluid', 'Saved ionizing photons'],
                    frameon=False, loc='lower right', fontsize=9)
    # Zero has only a negligible saved quadrupole residual, shown in the table.
    x = np.arange(len(cases)); width = .24; yr = 31557600.0
    components = [('delta_elapsed_time_shear_s', 'Shear only', '#0072B2'),
                  ('delta_elapsed_time_energy_s', 'Energy only', '#D55E00'),
                  ('delta_elapsed_time_sum_diagnostic_s', 'Algebraic sum', '#777777')]
    for j, (key, label, color) in enumerate(components):
        vals = [summary['cases'][case]['endpoint'][key]/yr for case in cases]
        ax[1, 1].bar(x + (j-1)*width, vals, width, label=label, color=color)
    ax[1, 1].axhline(0, color='#777777', lw=.8)
    ax[1, 1].set_title('D  Elapsed-clock diagnostic at mean redshift 4', loc='left', pad=12)
    ax[1, 1].set_xticks(x, ['0', '+0.005', '-0.005', '-0.01'])
    ax[1, 1].set_xlabel(r'Initial shear parameter $q_{\rm ref}$')
    ax[1, 1].set_ylabel('Elapsed-time shift [Julian years]')
    ax[1, 1].legend(frameon=False, fontsize=8.5, loc='lower left')
    ax[1, 1].set_ylim(-72, 31)
    fig.text(.08, .043, 'Forced-background estimates; original gas and radiation histories are unchanged. Missing +0.01 case is not inferred.\n'
             'Passing these approximation ceilings does not establish coupled abundance accuracy. AX11/AX12 remain unresolved; central DAG 28/88.',
             fontsize=9.2, color='#444444', linespacing=1.5)
    stem = output / 'original_igm_radiation_stress'
    fig.savefig(stem.with_suffix('.png'), dpi=190, facecolor='white')
    fig.savefig(stem.with_suffix('.svg'), facecolor='white')
    plt.close(fig)
    manifest = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source_rows_plotted': len(data), 'extrema_authority': 'STRESS_SUMMARY.json: all native rows',
                'cases': cases, 'matplotlib': matplotlib.__version__,
                'elapsed_clock_origin': 'each case mean redshift 20; not cosmic age',
                'clipping_note': 'panel C displays positive component magnitudes between 1e-20 and 4e-5; q=0 residual reported in table',
                'wall_s': time.perf_counter()-started,
                'files': {str(f.relative_to(HERE)): hashlib.sha256(f.read_bytes()).hexdigest()
                          for f in [stem.with_suffix('.png'), stem.with_suffix('.svg')]}}
    (output/'PLOT_MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
