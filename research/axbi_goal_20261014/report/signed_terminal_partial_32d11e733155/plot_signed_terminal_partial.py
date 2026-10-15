#!/usr/bin/env python3
"""Plot the five original, resource-capped partial histories; no solver."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
READER = ROOT / 'research/axbi_goal_20261014/report/terminal_pair_32d11e733155/plot_terminal_pair.py'
CASES = {
    'ZERO': ROOT / 'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO',
    **{name: ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155' / name
       for name in ('SHEAR_PLUS', 'SHEAR_MINUS', 'SHEAR_HALF_PLUS', 'SHEAR_HALF_MINUS')},
}
Q = {'ZERO': '0', 'SHEAR_PLUS': '+0.01', 'SHEAR_MINUS': '−0.01',
     'SHEAR_HALF_PLUS': '+0.005', 'SHEAR_HALF_MINUS': '−0.005'}
EXPECTED_CONFIG = {
    'ZERO': 'b83ac8f4e93704b249f08e2114501db56e3e5de039b99056c7c10efa9a782e41',
    'SHEAR_PLUS': 'b9a8bdeaf61a68839e23486fa8ad0740fe1318c55cbc7f522e11cacbb4ff21c0',
    'SHEAR_MINUS': 'd5227c1925d27a89e71bf59e1e5abd0557061f910172ea5fa9baacaece46c677',
    'SHEAR_HALF_PLUS': 'a5af5c6e61b2bca228baa8bf71e33e12ebbebb3638425704178badcba6135b81',
    'SHEAR_HALF_MINUS': 'd0c4d48fdcec402d4e2108d5ac205be00428846156f3613ff6e2e842e168bef2',
}
EXPECTED_SOURCE = 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'
EXPECTED_ENDPOINT = 0.08873654701704167
MYR = 365.25 * 86400 * 1e6


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if any((BASE / name).exists() for name in ('FIGURE_MANIFEST.json',
           'abundance_vs_elapsed_time.png', 'abundance_vs_Tgas_time_ordered.png')):
        raise RuntimeError('FIGURE_OUTPUT_ALREADY_EXISTS')
    spec = importlib.util.spec_from_file_location('frozen_terminal_plot_reader', READER)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    reader.BASE = BASE  # The proven reader writes its samples only in this new subtree.
    loaded = {}
    for case, path in CASES.items():
        data, info = reader.load(case, path)
        hashes = info['input_sha256']
        if hashes['config.cfg'] != EXPECTED_CONFIG[case] or hashes['source_identity.txt'] != EXPECTED_SOURCE:
            raise RuntimeError('FROZEN_CONFIG_OR_SOURCE_CHANGED:' + case)
        if info['a_endpoint'] != EXPECTED_ENDPOINT or info['accepted'] != 200000 or info['full_rows_checked'] != 200001:
            raise RuntimeError('ORIGINAL_PARTIAL_TERMINAL_CHANGED:' + case)
        loaded[case] = (data, info)

    outputs = {}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'savefig.dpi': 190})
    for axis, name in [('time', 'abundance_vs_elapsed_time.png'),
                       ('temperature', 'abundance_vs_Tgas_time_ordered.png')]:
        fig, axs = plt.subplots(2, 3, figsize=(16.5, 10.7), sharey=True)
        for ax, case in zip(axs.flat, CASES):
            data, info = loaded[case]
            x = data['t'] / MYR if axis == 'time' else data['T']
            for species, label, color in zip(reader.SPECIES, reader.LABELS, reader.COLORS):
                y = np.ma.masked_where(data[species] == 0, data[species])
                ax.plot(x, y, label=label, color=color, lw=1.45,
                        ls=':' if species == 'electron' else '-')
                if axis == 'temperature' and species in ('H_II', 'He_II'):
                    for fraction in (0.30, 0.65):
                        i = int(fraction * (len(x) - 1))
                        j = min(len(x) - 1, i + max(1, len(x) // 24))
                        if data[species][i] > 0 and data[species][j] > 0:
                            ax.annotate('', xy=(x[j], data[species][j]),
                                        xytext=(x[i], data[species][i]),
                                        arrowprops={'arrowstyle': '->', 'color': color, 'lw': 1.0})
            ax.set_yscale('log')
            ax.set_title(f'{case}  |  q_ref = {Q[case]}\npartial stop: z̄ = {info["zbar_endpoint"]:.4f};  {info["time_Myr_endpoint"]:.4f} Myr')
            ax.grid(alpha=.22)
            ax.set_xlabel('Elapsed proper time since z̄ = 20 [Myr]' if axis == 'time'
                          else 'Gas temperature [K] (arrows: increasing time)')
        axs.flat[-1].axis('off')
        ymin = min(v[1]['positive_minimum'][species] for v in loaded.values()
                   for species in reader.SPECIES)
        for ax in axs.flat[:-1]:
            ax.set_ylim(ymin / 2, 1.2)
        for ax in axs[:, 0]:
            ax.set_ylabel(r'$Y_i = n_i/(n_H+4n_{He})$')
        handles, labels = axs.flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
                   bbox_to_anchor=(.5, .085))
        fig.suptitle('Original five case histories | resource-capped partial interval only', fontsize=16)
        fig.text(.5, .018,
                 'All curves stop at z̄ = 10.2693; target z̄ = 4 not reached. No resolved shear or convergence claim.\n'
                 'Chronological extrema-preserving samples; exact zeros masked only on log display. Electron is charge census, not a nucleus.',
                 ha='center', fontsize=10)
        fig.subplots_adjust(left=.075, right=.985, top=.875, bottom=.23, hspace=.45, wspace=.17)
        target = BASE / name
        fig.savefig(target)
        plt.close(fig)
        outputs[name] = {'sha256': sha(target), 'bytes': target.stat().st_size}

    manifest = {
        'schema': 'rei.axbi.original_five_signed_terminal_partial_figures.v1',
        'status': 'ORIGINAL_FIVE_TERMINAL_PARTIAL_FIGURES',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'script_sha256': sha(Path(__file__)),
        'validated_reader_path': str(READER.relative_to(ROOT)),
        'validated_reader_sha256': sha(READER),
        'cases': {case: info for case, (_, info) in loaded.items()},
        'figures': outputs,
        'selection': 'Per chronological 100-row block, first/last and min/max of six species and T; both endpoints retained',
        'normalization': 'Y_i=n_i/(nH+4nHe); electron is charge census, not nucleus',
        'temperature_order': 'Saved chronological order; temperature is not sorted',
        'common_partial_stop_zbar': 1 / EXPECTED_ENDPOINT - 1,
        'full_target_zbar': 4,
        'full_target_reached': False,
        'scientific_admission': 'NOT_ISSUED',
        'solver_runs': 0,
        'source_mutations': 0,
        'versions': {'matplotlib': matplotlib.__version__, 'numpy': np.__version__},
    }
    (BASE / 'FIGURE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': manifest['status'],
                      'cases': {k: {'rows_checked': v['full_rows_checked'],
                                     'display_rows': v['display_rows'],
                                     'zbar_endpoint': v['zbar_endpoint']}
                                for k, v in manifest['cases'].items()},
                      'figures': outputs}))


if __name__ == '__main__':
    main()
