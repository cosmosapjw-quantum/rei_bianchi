#!/usr/bin/env python3
"""Display actual comparison tables. Plotting is assigned no scientific node credit."""
import argparse
import csv
import gzip
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('results', type=Path)
    args = parser.parse_args()
    summary = json.loads((args.results / 'SUMMARY.json').read_text())
    tables = {}
    for mode in ['fixed_a', 'fixed_t']:
        with gzip.open(args.results / f'comparison_{mode}.csv.gz', 'rt') as stream:
            rows = list(csv.DictReader(stream))
        tables[mode] = {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}
    plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .22,
                         'savefig.dpi': 180, 'axes.spines.top': False, 'axes.spines.right': False})
    fields = [('x_HII', r'$\Delta x_{\rm HII}$', 'Element fraction'),
              ('temperature_K', r'$\Delta T_{\rm gas}$', 'K')]
    for kind in ['responses', 'discrepancies']:
        fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.0), layout='constrained')
        for col, mode in enumerate(['fixed_a', 'fixed_t']):
            data = tables[mode]
            x = data['coordinate'] if mode == 'fixed_a' else data['coordinate'] / (31557600. * 1e6)
            for row, (field, label, unit) in enumerate(fields):
                ax = axes[row, col]
                floor = summary['modes'][mode]['observables'][field]['original_response_floor']
                if kind == 'responses':
                    ax.plot(x, data[field + '_response_T0'], color='#7c8794', lw=2.2, ls='--', label='T0')
                    ax.plot(x, data[field + '_response_T1'], color='#125b8e', lw=1.1, label='T1')
                    ax.axhspan(-floor, floor, color='#d9dfe5', alpha=.35, label='Original response floor')
                    ax.set_ylabel(label + ' [' + unit + ']')
                    ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
                else:
                    for suffix, color, name, style in [
                        ('D01_ZERO', '#6b7280', 'Absolute ZERO change', '-'),
                        ('D01_PLUS', '#d99a00', 'Absolute PLUS change', '--'),
                        ('D01_pair', '#b53d45', 'Paired response change', '-'),
                    ]:
                        y = abs(data[field + '_' + suffix])
                        ax.semilogy(x, np.where(y > 0, y, np.nan), color=color, lw=1.1, ls=style, label=name)
                    y = .1 * abs(data[field + '_response_T1'])
                    visible = abs(data[field + '_response_T1']) >= floor
                    ax.semilogy(x, np.where(visible & (y > 0), y, np.nan), color='#125b8e', lw=1.0,
                                ls=':', label='0.1 |T1 response| above floor')
                    ax.set_ylabel(r'$|D_{01}|$ [' + unit + ']')
                if mode == 'fixed_a':
                    ax.invert_xaxis()
                    ax.set_xlabel(r'Common redshift $\bar z$')
                else:
                    ax.set_xlabel('Common elapsed proper time [Myr]')
                if row == 0:
                    ax.set_title('Fixed scale factor' if mode == 'fixed_a' else 'Equal elapsed proper time')
                if row == 1:
                    ax.legend(fontsize=8, loc='best')
        title = ('Conditional primary-only H/He: PLUS minus ZERO' if kind == 'responses'
                 else 'T0 to T1 changes: individual histories and paired response')
        fig.suptitle(title + '\nTwo levels; evolution error bound and full AX11 gate remain unresolved', fontsize=12)
        fig.savefig(args.results / (kind + '.png'))
        fig.savefig(args.results / (kind + '.pdf'))
        plt.close(fig)
    print('Rendered actual-data figures; scientific node credit=0')


if __name__ == '__main__':
    main()
