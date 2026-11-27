"""R14 saved-output figure renderer: display work only, never a science runner.

Reads actual PRIMARY_RESULTS.json and REFERENCE_RESULTS.json. No production,
reference, ODE, primitive, convolution, root-isolation or old-unit import/run.
Only saved B2/B3 display evaluation, saved point connectors and certificate
metadata are drawn. Root authorizes one S08 render process under its budget.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback
import warnings

INTEGER_DIGITS = 6000
RATIONAL_CHARS = 10000
SAMPLES = 257
BLUE = '#2267a5'
ORANGE = '#c86a21'
RED = '#b43b42'
PURPLE = '#7650a5'
GREY = '#6b747c'
GREEN = '#34836e'


def fraction(value):
    """Bounded parse of saved exact data, separate from any science parser."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError('Saved exact scalar must be integer or rational text')
    if isinstance(value, int):
        result = Fraction(value)
    else:
        if len(value) > RATIONAL_CHARS or re.fullmatch(r'[+-]?[0-9]+(?:/[+-]?[0-9]+)?', value) is None:
            raise ValueError('Saved rational text exceeds the finite ASCII grammar')
        parts = value.split('/')
        if any(len(part.lstrip('+-')) > INTEGER_DIGITS for part in parts):
            raise ValueError('Saved rational component exceeds6000digits')
        result = Fraction(int(parts[0]), int(parts[1]) if len(parts) == 2 else 1)
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > 16384:
        raise ValueError('Saved rational component exceeds16384bits')
    return result


def number(value):
    return float(fraction(value))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def saved_record(primary, ident):
    matches = [row for row in primary['cases'] if row['id'] == ident]
    if len(matches) != 1 or matches[0].get('result') is None:
        raise ValueError('One successful saved case required: ' + ident)
    return matches[0]


def saved_cell(result, left='1', right='2'):
    rows = [row for row in result['exact']['R_cubic_cells']
            if fraction(row['left']) == fraction(left) and fraction(row['right']) == fraction(right)]
    if len(rows) != 1:
        raise ValueError('One saved cell required for the requested display')
    return rows[0]


def display_B2(coefficients, u):
    b0, b1, b2 = [number(value) for value in coefficients]
    return b0 * (1-u)**2 + 2*b1*u*(1-u) + b2*u*u


def display_B3(coefficients, u):
    b0, b1, b2, b3 = [number(value) for value in coefficients]
    return b0*(1-u)**3 + 3*b1*u*(1-u)**2 + 3*b2*u*u*(1-u) + b3*u**3


def style_axis(ax, title, xlabel=None, ylabel=None):
    ax.set_title(title, loc='left', fontsize=11.5, fontweight='semibold', pad=12)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.grid(True, color='#e3e7ea', linewidth=0.7, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)


def critical_panel(ax, record, np, title, zoom=False):
    result = record['result']
    cell = saved_cell(result)
    left, right = number(cell['left']), number(cell['right'])
    u = np.linspace(0.0, 1.0, SAMPLES)
    curve = display_B3(cell['bernstein'], u)
    ax.plot(left+(right-left)*u, curve, color=BLUE, lw=2.2, label='Saved cubic R', zorder=3)
    upper = number(cell['supremum']['dyadic_upper'])
    ax.hlines(upper, left, right, color=RED, lw=1.8, linestyle='--', label='Closed-cell upper certificate', zorder=2)
    markers = []
    for i, box in enumerate(cell['supremum']['box_bounds']):
        t = left+(right-left)*number(box['midpoint'])
        y = number(box['midpoint_value'])
        ax.plot(t, y, 'D', color=PURPLE, ms=5.5,
                label='Saved critical-box midpoint' if i == 0 else None, zorder=5)
        markers.append({'time_display': t, 'value_display': y,
                        'normalized_midpoint': box['midpoint'], 'box_lo': box['lo'], 'box_hi': box['hi']})
    ax.plot([left, right], [number(cell['bernstein'][0]), number(cell['actual_right_endpoint'])],
            'o', color=BLUE, ms=4, zorder=4)
    low, high = min(float(curve.min()), number(cell['actual_right_endpoint'])), max(float(curve.max()), upper)
    span = max(high-low, 1e-3)
    ax.set_ylim(low-0.15*span, high+0.55*span)
    ax.set_xlim(left-0.025*(right-left), right+0.025*(right-left))
    style_axis(ax, title, 'Time t (normalized)', 'R(t)')
    ax.ticklabel_format(axis='y', style='plain', useOffset=False)
    ax.legend(loc='upper left', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.95)
    if zoom:
        ax.text(0.98, 0.04, 'Vertical scale enlarged', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=8.6, color=GREY)
    return {'case': record['id'], 'left': cell['left'], 'right': cell['right'],
            'saved_bernstein': cell['bernstein'], 'closed_cell_dyadic_upper': cell['supremum']['dyadic_upper'],
            'critical_display_markers': markers,
            'box_display_note': '96-step boxes are narrower than display resolution; markers are saved midpoints.'}


def figure_one(primary, plt, np):
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9.8))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.13, top=0.865, wspace=0.27, hspace=0.43)
    fig.suptitle('R14: source positivity and closed-cell R certificates', fontsize=16, fontweight='semibold', y=0.985)
    fig.text(0.075, 0.944, 'Synthetic conditional arithmetic controls; physical source binding remains pending.', fontsize=10.5, color=GREY)
    metadata = {}

    record = saved_record(primary, 'signed_middle_nonnegative')
    original = record['input']['g_r'][0]
    u = np.linspace(0.0, 1.0, SAMPLES)
    ax = axes[0, 0]
    ax.plot(u, display_B2(original, u), color=BLUE, lw=2.2, label='Original source polynomial', zorder=3)
    ax.plot([0, 0.5, 1], [number(x) for x in original], color=ORANGE, ls='--',
            marker='s', markerfacecolor='white', ms=5.2, label='Original B2 control polygon', zorder=2)
    vertices = record['result']['effective_source']['source_vertex_times']
    for i, vertex in enumerate(vertices):
        ax.axvline(number(vertex), color=GREY, ls=':', lw=1.4, label='Exact source split' if i == 0 else None)
    ax.axhline(0, color='#a9b0b5', lw=0.8)
    ax.set_xlim(-0.025, 1.025)
    ax.set_ylim(-0.255, 0.73)
    style_axis(ax, '(a) Nonnegative source, signed control coefficient', 'Source time s (normalized)', 'g_r(s)')
    ax.legend(loc='upper left', fontsize=8.9, frameon=True, facecolor='white', framealpha=0.95)
    ax.text(0.98, 0.04, 'g_r(s) = (s - 1/4)^2\nb1 = -3/16; g_r(s) >= 0',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=9.1,
            bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.92, 'pad': 2.5})
    metadata['a'] = {'case': record['id'], 'source_B2': original, 'source_vertex_times': vertices,
                     'read_scope': 'Saved original quadratic source; polynomial display only.'}
    metadata['b'] = critical_panel(axes[0, 1], saved_record(primary, 'one_irrational_maximum'), np,
                                   '(b) One interior maximum and its whole-cell bound')
    metadata['c'] = critical_panel(axes[1, 0], saved_record(primary, 'two_irrational_critical_roots'), np,
                                   '(c) Two interior critical points (zoom)', zoom=True)

    record = saved_record(primary, 'initial_downward_jump')
    cell = record['result']['exact']['R_cubic_cells'][0]
    ax = axes[1, 1]
    left, right = number(cell['left']), number(cell['right'])
    ax.plot(left+(right-left)*u, display_B3(cell['bernstein'], u), color=BLUE, lw=2.2, label='Saved cubic before the jump')
    sup = number(cell['supremum']['dyadic_upper'])
    left_limit, actual = number(cell['right_left_limit']), number(cell['actual_right_endpoint'])
    ax.hlines(sup, left, right, color=RED, ls='--', lw=1.6, label='Closed-cell supremum upper')
    ax.plot(right, left_limit, 'o', ms=8, markerfacecolor='white', markeredgecolor=BLUE, mew=1.8, zorder=6)
    ax.plot(right, actual, 'o', color='#222b33', ms=6, zorder=6)
    ax.vlines(right, actual, left_limit, color=GREY, lw=1.1, ls=':', zorder=1)
    ax.annotate('R(1-) = 4/3  (open)', xy=(right, left_limit), xytext=(0.53, 1.465),
                fontsize=9.2, color=BLUE, arrowprops={'arrowstyle': '-', 'color': BLUE, 'lw': 0.8})
    ax.annotate('R(1) = 1/3  (actual)', xy=(right, actual), xytext=(0.52, 0.47),
                fontsize=9.2, color='#222b33', arrowprops={'arrowstyle': '-', 'color': GREY, 'lw': 0.8})
    ax.set_xlim(-0.025, 1.06)
    ax.set_ylim(0.18, 1.56)
    style_axis(ax, '(d) Actual endpoint and unattained left limit', 'Time t (normalized)', 'R(t)')
    ax.legend(loc='lower left', fontsize=8.7, frameon=True, facecolor='white', framealpha=0.95)
    metadata['d'] = {'case': record['id'], 'actual_right_endpoint': cell['actual_right_endpoint'],
                     'right_left_limit': cell['right_left_limit'], 'supremum': cell['supremum'],
                     'vertical_dotted_line': 'Jump guide; no continuous interpolation through the discontinuity.'}
    fig.text(0.075, 0.068, 'Critical markers use saved root-box midpoints. Their 96-step boxes are narrower than display resolution.', fontsize=9.4, color=GREY)
    fig.text(0.075, 0.037, 'Curves evaluate saved polynomial coefficients for display; horizontal certificates retain the exact stored bounds.', fontsize=9.4, color=GREY)
    return fig, metadata


def figure_two(primary, plt, np, Line2D):
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 10.6))
    fig.subplots_adjust(left=0.08, right=0.975, bottom=0.18, top=0.865, wspace=0.29, hspace=0.47)
    fig.suptitle('R14: conditional comparisons, enclosure gaps and finite work', fontsize=15.5, fontweight='semibold', y=0.985)
    fig.text(0.08, 0.944, 'Saved primary/reference results only. Ratios describe ideal comparison controls, not physical accuracy.', fontsize=10.4, color=GREY)
    metadata = {}

    ax = axes[0, 0]
    ids = ['quadratic_q1', 'affine_reduction_q1', 'constant_reduction_q1']
    records = [saved_record(primary, ident) for ident in ids]
    exact_values = [row['input']['controls']['endpoint'] for row in records]
    positions = np.arange(3)
    width = 0.32
    for offset, key, color in [(-width/2, 'R', BLUE), (width/2, 'E', ORANGE)]:
        values = [number(row[key]) for row in exact_values]
        bars = ax.bar(positions+offset, values, width, label=key+'(T), exact control', color=color, alpha=0.88, zorder=3)
        ax.bar_label(bars, labels=[row[key] for row in exact_values], padding=4, fontsize=9.2)
    r_ratio = (fraction(exact_values[2]['R'])-fraction(exact_values[0]['R'])) / fraction(exact_values[2]['R'])
    e_ratio = (fraction(exact_values[2]['E'])-fraction(exact_values[0]['E'])) / fraction(exact_values[2]['E'])
    ax.set_xticks(positions, ['Quadratic\ng_r = s^2', 'Affine\ng_r = s', 'Constant\ng_r = 1'])
    ax.set_ylim(0, 1.24)
    style_axis(ax, '(a) Exact endpoint controls on the same horizon', None, 'Endpoint comparison value')
    ax.legend(loc='upper left', fontsize=8.8, ncol=2, frameon=False)
    ax.text(0.02, 0.76, 'Quadratic vs constant:\nR lower by '+str(r_ratio)+'; E lower by '+str(e_ratio),
            transform=ax.transAxes, ha='left', va='top', fontsize=9.2,
            bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.94, 'pad': 2.5})
    metadata['a'] = {'case_ids': ids, 'saved_exact_endpoint_controls': exact_values,
                     'conditional_relative_reduction_R': str(r_ratio), 'conditional_relative_reduction_E': str(e_ratio),
                     'meaning': 'Ideal synthetic comparison only; no physical gain or speed claim.'}

    ax = axes[0, 1]
    panel_rows = []
    maximum = 0.0
    for ident, color in [('signed_d_positive', BLUE), ('signed_d_negative', ORANGE)]:
        result = saved_record(primary, ident)['result']
        times = [number(x) for x in result['requested_times']]
        endpoint_upper = [number(row[1]) for row in result['raw']['endpoints_upper']]
        whole_upper = [number(row[1]) for row in result['raw']['whole_cells_upper']]
        ax.plot(times, endpoint_upper, color=color, ls='--', marker='o', ms=4.5, lw=1.6, zorder=4)
        for i, bound in enumerate(whole_upper):
            ax.hlines(bound, times[i], times[i+1], color=color, lw=2.8, alpha=0.65, zorder=2)
            ax.plot([times[i], times[i+1]], [bound, bound], '|', color=color, ms=7, zorder=3)
        maximum = max(maximum, *whole_upper, *endpoint_upper)
        panel_rows.append({'case': ident, 'requested_times': result['requested_times'],
                           'saved_endpoint_E_upper': [row[1] for row in result['raw']['endpoints_upper']],
                           'saved_closed_cell_E_upper': [row[1] for row in result['raw']['whole_cells_upper']]})
    handles = [Line2D([0], [0], color=BLUE, lw=2, label='d = +2'), Line2D([0], [0], color=ORANGE, lw=2, label='d = -2'),
               Line2D([0], [0], color=GREY, ls='--', marker='o', label='Endpoint upper connector'),
               Line2D([0], [0], color=GREY, lw=2.8, label='Closed-cell upper bar')]
    ax.set_ylim(0, maximum*1.35)
    ax.set_xlim(-0.025, 1.025)
    style_axis(ax, '(b) Signed d: endpoint connectors and whole-cell bounds', 'Time t (normalized)', 'E upper value')
    ax.legend(handles=handles, loc='upper left', ncol=2, fontsize=8.0, frameon=True, facecolor='white', framealpha=0.95)
    metadata['b'] = panel_rows

    ax = axes[1, 0]
    gap_ids = ['one_irrational_maximum', 'two_irrational_critical_roots', 'golden_irrational_maximum']
    gap_rows = []
    for ident in gap_ids:
        result = saved_record(primary, ident)['result']
        sup = result['exact']['observation_R_suprema'][1]
        width_exact = fraction(result['raw']['whole_cells_upper'][1][0])-fraction(result['raw']['whole_cells_lower'][1][0])
        gap_rows.append({'case': ident, 'exact_gap': sup['exact_gap'], 'dyadic_width': str(width_exact),
                         'proved_gap_bound': sup['proved_gap_bound']})
    keys = [('exact_gap', 'Exact sup gap', PURPLE), ('dyadic_width', 'Dyadic width', GREEN), ('proved_gap_bound', 'Proved gap bound', GREY)]
    positive = [number(row[key]) for row in gap_rows for key, _, _ in keys if fraction(row[key]) > 0]
    display_floor = min(positive)/20 if positive else 1e-40
    display_top = max(positive)*30 if positive else 1e-20
    zeros = []
    for index, (key, label, color) in enumerate(keys):
        for group, row in enumerate(gap_rows):
            xpos = group+(index-1)*0.23
            value = number(row[key])
            if value > 0:
                ax.bar(xpos, value-display_floor, bottom=display_floor, width=0.21, color=color,
                       alpha=0.88, label=label if group == 0 else None, zorder=3)
            else:
                ax.plot(xpos, display_floor*2, 'v', color=color, markerfacecolor='white', ms=6, zorder=4)
                ax.annotate('0 exact', (xpos, display_floor*2), xytext=(0, 7), textcoords='offset points',
                            ha='center', fontsize=7.8, rotation=90)
                zeros.append({'case': row['case'], 'quantity': key, 'display': 'Zero marker only; no positive floor substituted into data.'})
    ax.set_yscale('log')
    ax.set_ylim(display_floor, display_top)
    ax.set_xticks([0, 1, 2], ['One maximum', 'Two critical roots', 'Golden maximum'])
    style_axis(ax, '(c) Stored supremum gaps and outward widths', None, 'Absolute R gap or width (log scale)')
    legend_handles = [Line2D([0], [0], color=color, lw=6, label=label) for _, label, color in keys]
    ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.23),
              ncol=3, fontsize=8.5, frameon=False)
    metadata['c'] = {'rows': gap_rows, 'zeros': zeros, 'display_floor': display_floor,
                     'display_floor_is_data': False, 'exact_gap_source': 'Saved observation_R_suprema; no new root solve.'}

    ax = axes[1, 1]
    full = saved_record(primary, 'full_effective48_nonaligned_tau')['result']
    work = full['work']
    rows = [['Original source cells', str(work['original_source_cells'])],
            ['Effective source cells', str(work['effective_source_cells'])],
            ['Observation cells', str(len(full['requested_times'])-1)],
            ['Base cells (actual)', str(work['base_cells'])],
            ['Full kernel blocks', str(work['full_blocks'])],
            ['Overlap visits / precharge', format(work['overlap_terms_actual'], ',')+' / '+format(work['overlap_terms_upper'], ',')],
            ['Root bisections / precharge', format(work['root_bisections_actual'], ',')+' / '+format(work['root_bisections_upper'], ',')],
            ['Stored coefficient builds', str(work['coefficient_cell_builds'])]]
    ax.set_title('(d) Full-capacity control: saved work counters', loc='left', fontsize=11.5, fontweight='semibold', pad=12)
    ax.axis('off')
    table = ax.table(cellText=rows, colLabels=['Recorded quantity', 'Saved value'], colWidths=[0.58, 0.42],
                     cellLoc='left', colLoc='left', bbox=[0.0, 0.12, 1.0, 0.83])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor('#d5dce1')
        cell.set_linewidth(0.55)
        if row == 0:
            cell.set_facecolor('#e3edf6')
            cell.set_text_props(weight='semibold')
        elif row % 2 == 0:
            cell.set_facecolor('#f5f7f9')
    ax.text(0.0, 0.035, 'tau = 2/17; original global forcing memory retained.', transform=ax.transAxes,
            fontsize=9.2, color=GREY)
    metadata['d'] = {'case': 'full_effective48_nonaligned_tau', 'tau': full['parameters']['tau'],
                     'observation_cells': len(full['requested_times'])-1, 'saved_work': work}
    fig.text(0.08, 0.071, 'Endpoint connectors show saved point bounds; horizontal bars certify the closed observation cells.', fontsize=9.4, color=GREY)
    fig.text(0.08, 0.039, 'Exact zero gaps, if present, use labelled zero markers. Positive log-axis display limits do not replace zero data.', fontsize=9.4, color=GREY)
    return fig, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--primary', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    primary_path = args.primary or root/'raw/PRIMARY_RESULTS.json'
    reference_path = args.reference or root/'raw/REFERENCE_RESULTS.json'
    out = args.output_dir or root/'figures'
    out.mkdir(parents=True, exist_ok=True)
    names = ['R14_SOURCE_AND_EXTREMA.png', 'R14_SOURCE_AND_EXTREMA.svg',
             'R14_COMPARISON_AND_RESOURCE.png', 'R14_COMPARISON_AND_RESOURCE.svg',
             'PLOT_DATA.json', 'PLOT_MANIFEST.json', 'RENDER_RESULT.json']
    if any((out/name).exists() for name in names) or (out/'RENDER_FAILURE.json').exists():
        parser.error('Existing figure/result evidence cannot be overwritten')
    sys.set_int_max_str_digits(INTEGER_DIGITS)
    started, started_utc = time.process_time(), datetime.now(timezone.utc).isoformat()
    stage = 'read_saved_inputs'
    identities = {'render_source': {'path': str(Path(__file__).resolve()),
                                    'sha256': sha256(Path(__file__).read_bytes())}}
    render_id = None
    try:
        primary_bytes = primary_path.read_bytes()
        identities['primary'] = {'path': str(primary_path), 'bytes': len(primary_bytes), 'sha256': sha256(primary_bytes)}
        reference_bytes = reference_path.read_bytes()
        identities['reference'] = {'path': str(reference_path), 'bytes': len(reference_bytes), 'sha256': sha256(reference_bytes)}
        render_id = 'WU_R14_RENDER_'+sha256((identities['primary']['sha256']+identities['reference']['sha256']+identities['render_source']['sha256']).encode())[:20]
        primary, reference = json.loads(primary_bytes), json.loads(reference_bytes)
        if primary.get('schema') != 'WU_R14_PRIMARY_RESULTS_V1' or primary.get('status') != 'PASS_SCOPED':
            raise ValueError('Actual scoped primary PASS required')
        if primary['summary']['failed'] != 0:
            raise ValueError('Primary has failed checks')
        if reference.get('schema') != 'WU_R14_INDEPENDENT_REFERENCE_V1' or reference.get('status') != 'PASS':
            raise ValueError('Actual independent reference PASS required')
        if reference['checks_failed'] != 0 or reference['component_failures'] != 0:
            raise ValueError('Reference has failed checks or components')
        if reference['input_identities']['primary_sha256'] != sha256(primary_bytes):
            raise ValueError('Reference is not bound to these primary bytes')
        stage = 'import_display_libraries'
        for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
            os.environ[key] = '1'
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        import numpy as np
        plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5, 'axes.labelsize': 10.5,
                             'xtick.labelsize': 9.2, 'ytick.labelsize': 9.2, 'axes.linewidth': 0.8,
                             'savefig.facecolor': 'white', 'svg.fonttype': 'none', 'svg.hashsalt': render_id})
        outputs, data = [], {}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            for stem, builder in [('R14_SOURCE_AND_EXTREMA', lambda: figure_one(primary, plt, np)),
                                  ('R14_COMPARISON_AND_RESOURCE', lambda: figure_two(primary, plt, np, Line2D))]:
                stage = 'build_'+stem
                fig, details = builder()
                data[stem] = details
                for extension in ('png', 'svg'):
                    stage = 'save_'+stem+'.'+extension
                    target = out/(stem+'.'+extension)
                    fig.savefig(target, dpi=160, metadata={'Creator': 'R14 saved-output renderer', 'Date': None} if extension == 'svg' else {'Software': 'R14 saved-output renderer'})
                    payload = target.read_bytes()
                    outputs.append({'filename': target.name, 'bytes': len(payload), 'sha256': sha256(payload)})
                plt.close(fig)
        warning_rows = [{'category': row.category.__name__, 'message': str(row.message),
                         'filename': row.filename, 'lineno': row.lineno} for row in caught]
        for row in warning_rows:
            print(row['category']+': '+row['message'], file=sys.stderr)
        (out/'PLOT_DATA.json').write_text(json.dumps({'render_id': render_id, 'panels': data,
            'display_samples_per_curve': SAMPLES, 'binary64_is_display_only': True}, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        outputs.append({'filename': 'PLOT_DATA.json', 'bytes': (out/'PLOT_DATA.json').stat().st_size,
                        'sha256': sha256((out/'PLOT_DATA.json').read_bytes())})
        execution = {'render_process_runs': 1, 'new_science_runs': 0, 'new_ODE_runs': 0,
                     'new_root_solves': 0, 'new_primitive_or_convolution_evaluations': 0,
                     'production_or_reference_imports': 0, 'old_science_replay': 0,
                     'saved_polynomial_display_evaluation': True, 'integer_decimal_digit_limit': sys.get_int_max_str_digits(),
                     'display_library_threads': {'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'},
                     'internal_renderer_CPU_s': time.process_time()-started,
                     'CPU_scope': 'Renderer body; root wrapper records whole-process CPU/wall/memory.'}
        manifest = {'schema': 'WU_R14_SAVED_FIGURE_MANIFEST_V1', 'render_id': render_id,
                    'input_identities': identities, 'outputs': outputs, 'execution': execution,
                    'warnings': warning_rows, 'started_utc': started_utc,
                    'finished_utc': datetime.now(timezone.utc).isoformat(),
                    'visual_review': 'NOT_RUN_BY_RENDERER;root must inspect the actual PNGs',
                    'scope': 'Saved synthetic conditional comparison figures; physical input remains pending.'}
        (out/'PLOT_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        result = {'schema': 'WU_R14_RENDER_RESULT_V1', 'status': 'RENDERED_PENDING_ACTUAL_VISUAL_REVIEW',
                  'render_id': render_id, 'output_count': len(outputs),
                  'manifest_sha256': sha256((out/'PLOT_MANIFEST.json').read_bytes()), 'execution': execution}
        (out/'RENDER_RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        failure = {'schema': 'WU_R14_RENDER_FAILURE_V1', 'status': 'FAILED', 'stage': stage,
                   'error_class': type(exc).__name__, 'error': str(exc), 'traceback': traceback.format_exc(),
                   'started_utc': started_utc, 'failed_utc': datetime.now(timezone.utc).isoformat(),
                   'render_id': render_id, 'input_identities': identities,
                   'preserve_partial_outputs': True, 'new_science_runs': 0,
                   'internal_renderer_CPU_s': time.process_time()-started}
        with (out/'RENDER_FAILURE.json').open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(failure, ensure_ascii=False, indent=2)+'\n')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
