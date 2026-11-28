#!/usr/bin/env python3
"""Render only saved R15 comparison certificates and depth diagnostics."""
import argparse
import hashlib
import json
import math
import pathlib
import sys
from fractions import Fraction

sys.set_int_max_str_digits(6000)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
root = pathlib.Path(a.root)
dest = root / 'figures'
dest.mkdir(exist_ok=True)
output = pathlib.Path(a.output)
targets = [dest / ('R15_' + stem + '.' + ext)
           for stem in ('comparison_envelopes', 'subdivision_convergence')
           for ext in ('png', 'svg')]
targets += [dest / 'PLOT_DATA.json', dest / 'PLOT_MANIFEST.json', output]
if any(f.exists() for f in targets):
    raise RuntimeError('Preserve existing rendered output; no implicit rerender.')

def read(path):
    return json.loads(path.read_text())

def identity(path):
    body = path.read_bytes()
    return {'path': path.relative_to(root).as_posix(), 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest()}

primary_path = root / 'raw/PRIMARY_RESULTS.json'
reference_path = root / 'raw/REFERENCE_RESULTS.json'
primary = read(primary_path)
reference = read(reference_path)
if not str(primary['status']).startswith('PASS') or not str(reference['status']).startswith('PASS'):
    raise RuntimeError('Figures require accepted saved primary and reference outcomes.')
models = {row['id']: row['result'] for row in primary['valid_cases']}
sweeps = [row for row in primary['checks'] if row.get('kind') == 'DEPTH_SWEEP']
if len(sweeps) != 2 or sum(len(s['rows']) for s in sweeps) != 14:
    raise RuntimeError('Expected two saved seven-depth diagnostics.')
f = lambda value: float(Fraction(value))
blue, orange, green = '#2064a0', '#c77713', '#287b52'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titleweight': 'semibold', 'axes.grid': True,
                     'grid.alpha': 0.22, 'svg.fonttype': 'none'})

model_ids = ['Q0_INITIAL_JUMP', 'NONALIGNED_NEGATIVE_D']
fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.1), squeeze=False)
for row_index, case_id in enumerate(model_ids):
    result = models[case_id]
    times = list(map(f, result['base_times']))
    requested = list(map(f, result['requested_times']))
    endpoint = result['raw']['refined_endpoints_upper']
    whole = result['raw']['refined_whole_cells_upper']
    observation = result['raw']['endpoints_upper']
    cells = result['exact']['R_quartic_cells']
    for component in (0, 1):
        ax = axes[row_index][component]
        whole_label = connector_label = jump_label = True
        for i, cell in enumerate(cells):
            left, right = times[i:i + 2]
            upper = f(whole[i][component])
            ax.plot([left, right], [upper, upper], color=orange, linewidth=2.1,
                    label='Whole-cell upper certificate' if whole_label else None)
            whole_label = False
            start = f(endpoint[i][component])
            finish = f(cell['right_left_limit']) if component == 0 else f(endpoint[i + 1][1])
            ax.plot([left, right], [start, finish], '--', color=blue, linewidth=1.4,
                    label='Endpoint connector (not a trajectory)' if connector_label else None)
            connector_label = False
            if component == 0 and Fraction(cell['right_left_limit']) != Fraction(cell['actual_right_endpoint']):
                actual = f(cell['actual_right_endpoint'])
                ax.plot([right, right], [actual, finish], ':', color=blue, linewidth=1.1)
                ax.scatter([right], [finish], facecolors='white', edgecolors=blue, s=42,
                           zorder=6, label='Left limit at a kernel jump' if jump_label else None)
                jump_label = False
        ax.scatter(times, [f(v[component]) for v in endpoint], color=blue, s=16,
                   zorder=5, label='Actual base-clock endpoint upper')
        ax.scatter(requested, [f(v[component]) for v in observation], color=green,
                   marker='D', s=24, zorder=7, label='Requested-clock endpoint upper')
        symbol = 'R' if component == 0 else 'E'
        name = 'q = 0: initial jump' if row_index == 0 else 'Nonaligned clocks: signed negative d'
        ax.set_title(name + ' / ' + symbol, fontsize=11)
        ax.set_xlabel('Exact input clock t (displayed as float)')
        ax.set_ylabel(symbol + ' ideal comparison')
        ax.margins(x=0.035, y=0.12)
        ax.legend(fontsize=7.1, loc='best', framealpha=0.94)
fig.suptitle('R15 saved comparison certificates', fontsize=15, y=0.988)
fig.text(0.5, 0.014,
         'Horizontal segments certify whole cells. Dashed connectors only join saved endpoints. '
         'These are conditional comparison functions, not physical error lower bounds.',
         ha='center', fontsize=8)
fig.tight_layout(rect=(0, 0.04, 1, 0.965))

def save_pair(figure, stem):
    figure.savefig(dest / ('R15_' + stem + '.png'), dpi=175, facecolor='white',
                   metadata={'Software': 'WU R15 saved-result renderer'})
    figure.savefig(dest / ('R15_' + stem + '.svg'), facecolor='white',
                   metadata={'Date': None, 'Creator': 'WU R15 saved-result renderer'})
    plt.close(figure)

save_pair(fig, 'comparison_envelopes')

fig, (ax_gap, ax_work) = plt.subplots(1, 2, figsize=(12.8, 5.5))
positive = [f(r['exact_gap']) for s in sweeps for r in s['rows'] if Fraction(r['exact_gap']) > 0]
floor = min(positive) / 15 if positive else 1e-40
plot_data = {'schema': 'WU_R15_SAVED_PLOT_DATA_V1',
             'model_ids': model_ids, 'model_data': {k: models[k] for k in model_ids},
             'depth_sweeps': sweeps, 'new_scientific_evaluations': 0,
             'display_conversion': 'Exact saved rational values converted to float only for plotting.'}
split_notes = []
for index, sweep in enumerate(sweeps):
    rows = sweep['rows']
    depth = [r['depth'] for r in rows]
    color = blue if index == 0 else orange
    label = 'Rational critical points' if 'RATIONAL' in sweep['id'] else 'Algebraic critical points'
    gaps = [f(r['exact_gap']) if Fraction(r['exact_gap']) > 0 else math.nan for r in rows]
    bound = [f(r['proved_gap_bound']) for r in rows]
    ax_gap.semilogy(depth, gaps, '-o', color=color, markersize=4, label=label + ': exact gap')
    ax_gap.semilogy(depth, bound, '--', color=color, alpha=0.7, label=label + ': proved bound')
    zero_depth = [r['depth'] for r in rows if Fraction(r['exact_gap']) == 0]
    if zero_depth:
        ax_gap.scatter(zero_depth, [floor] * len(zero_depth), marker='v', color=color, s=30)
    ax_work.plot(depth, [r['nodes_visited'] for r in rows], '-o', color=color,
                 markersize=4, label=label + ': visits')
    split_notes.append(label + ': D=96 splits ' + str(rows[-1]['splits_actual']) + ' / 288')
depth = [r['depth'] for r in sweeps[0]['rows']]
ax_work.plot(depth, [6 * d + 1 for d in depth], '--', color='#303030', label='Visit bound 6D + 1')
ax_gap.set_ylim(bottom=floor / 2)
ax_gap.set_title('Supremum enclosure width', fontsize=12)
ax_gap.set_xlabel('Maximum subdivision depth D')
ax_gap.set_ylabel('Exact saved upper - lower (log scale)')
ax_gap.legend(fontsize=8, loc='best')
ax_work.set_title('Visited nodes and the finite bound', fontsize=12)
ax_work.set_xlabel('Maximum subdivision depth D')
ax_work.set_ylabel('Visited tree nodes')
ax_work.legend(fontsize=8, loc='upper left')
ax_work.text(0.03, 0.035, '\n'.join(split_notes), transform=ax_work.transAxes,
             fontsize=8, bbox={'facecolor': 'white', 'alpha': 0.9, 'edgecolor': '#dddddd'})
fig.suptitle('R15 subdivision: 14 saved depth diagnostics', fontsize=15)
fig.text(0.5, 0.018,
         'Downward triangles denote an exactly zero gap, displayed below the positive range. '
         'Public model calculations use D=96. No scientific routine was rerun for these figures.',
         ha='center', fontsize=8)
fig.tight_layout(rect=(0, 0.065, 1, 0.94))
save_pair(fig, 'subdivision_convergence')

(dest / 'PLOT_DATA.json').write_text(json.dumps(plot_data, ensure_ascii=False, indent=2) + '\n')
generated = [identity(path) for path in targets if path.suffix in ('.png', '.svg')]
generated.append(identity(dest / 'PLOT_DATA.json'))
manifest = {'schema': 'WU_R15_PLOT_MANIFEST_V1', 'status': 'RENDERED_PENDING_ACTUAL_VISUAL_REVIEW',
            'inputs': [identity(primary_path), identity(reference_path), identity(pathlib.Path(__file__))],
            'outputs': generated, 'new_scientific_evaluations': 0, 'production_imports': 0,
            'endpoint_connectors_are_whole_cell_certificates': False,
            'scientific_status': 'Conditional ideal comparison controls; physical admission unchanged.'}
(dest / 'PLOT_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
result = {'schema': 'WU_R15_RENDER_RESULTS_V1', 'status': 'RENDERED_PENDING_ACTUAL_VISUAL_REVIEW',
          'png_count': 2, 'svg_count': 2, 'depth_rows': 14,
          'model_ids': model_ids, 'manifest': identity(dest / 'PLOT_MANIFEST.json'),
          'new_scientific_evaluations': 0, 'production_imports': 0}
with output.open('x') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(result))
