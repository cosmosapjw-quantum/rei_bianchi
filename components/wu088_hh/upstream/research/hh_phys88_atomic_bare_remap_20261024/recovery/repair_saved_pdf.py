#!/usr/bin/env python3
"""Root-reviewed affected-PDF-only recovery preparation; no execution on import.

One original second-figure construction, PNG pass to BytesIO, one PDF render.
No first figure, source imports, integrators, original module main, original
artifact overwrite, or rerender loop. Optional candidates only replace equal-
length uncompressed CreationDate bytes within the original figure lease.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import io
import json
import os
import sys
import time
import traceback

sys.dont_write_bytecode = True
UNIT = Path('/workspace/scratch/ebcaaaa20861/WU088_HH/research/hh_phys88_atomic_bare_remap_20261024')
ORIGINAL_SCRIPT_SHA = '5b76f7f4ce85459b845107b11d9111aba7fb37c892d2e5403a8da4999ded8dcd'
RESULT_SHA = '6f3f1e8d6ce07619502dee8683d8322560fe1c13e70ae27f2eb1381969500104'
EXPECTED_PNG_SHA = 'fdc94b6977afc0e9929cfa17d1bbcec6ab86a3195ffd556cc02ecf41b55b877c'
EXPECTED_PDF_SHA = '6389368893663f161be17845fa618d8c8e9348d0a10b6eeccddf9876f18dbde7'
EXPECTED_PDF_BYTES = 21400


def write_closed(path, raw):
    with path.open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    reopened = path.read_bytes()
    if reopened != raw:
        raise ValueError('Closed candidate reopened bytes differ')
    return {'filename': path.name, 'bytes': len(reopened), 'sha256': hashlib.sha256(reopened).hexdigest(),
            'fsync_close_reopen': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.result.resolve() != UNIT/'results/primary001/RESULT.json':
        raise ValueError('Exact frozen saved primary path required')
    original = (UNIT/'source/plot_saved_results.py').read_bytes()
    raw = args.result.read_bytes()
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SCRIPT_SHA or hashlib.sha256(raw).hexdigest() != RESULT_SHA:
        raise ValueError('Frozen original plot or saved RESULT identity mismatch')
    saved = json.loads(raw)
    if saved['status'] != 'PRIMARY_COMPLETED_AWAITING_INDEPENDENT_REVIEW' or saved['failures']:
        raise ValueError('Complete passed saved primary required')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    rec = {'schema': 'PHYS88_ONE_AFFECTED_PDF_RECOVERY_V1', 'status': 'FAILED_PRESERVED',
        'original_plot_script_sha256': ORIGINAL_SCRIPT_SHA, 'input_RESULT_sha256': RESULT_SHA,
        'expected_PDF_bytes': EXPECTED_PDF_BYTES, 'expected_PDF_sha256': EXPECTED_PDF_SHA,
        'figure_constructions': 0, 'PNG_file_writes': 0, 'PDF_render_calls': 0,
        'source_callbacks': 0, 'integrations': 0, 'original_artifact_writes': 0,
        'automatic_retries': 0, 'metadata_only_candidates': [],
        'creation_date_candidate_basis': 'Original affected mtime12:06:01.357407UTC; otherPDFmetadata07:06:00-0500; originallease12:05:58.369200..12:06:01.720023UTC',
        'cause_of_original_badbytes': 'NOT_ESTABLISHED'}
    wall, cpu = time.monotonic(), time.process_time()
    try:
        render(saved, output, rec)
    except BaseException as exc:
        rec['exception'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        rec.update(cpu_s=time.process_time()-cpu, wall_s=time.monotonic()-wall,
                   cpu_affinity=sorted(os.sched_getaffinity(0)))
        with (output/'REPAIR_RECEIPT.json').open('x') as f:
            json.dump(rec, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': rec['status'], 'receipt': str(output/'REPAIR_RECEIPT.json'),
                      'PDF_render_calls': rec['PDF_render_calls'], 'integrations': 0}))
    return 0 if rec['status'] == 'EXACT_EXPECTED_PDF_RECOVERED' else 1


def render(saved, output, rec):
    os.environ['MPLCONFIGDIR'] = str(output/'.mpl_config')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.bbox': 'tight', 'pdf.fonttype': 42})
    colors = {'LAB_ANCHORED': '#145d80', 'FIXED_COM_K': '#b24a2b'}
    rec['figure_constructions'] = 1
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.4), constrained_layout=True)
    for name, color in colors.items():
        rows = sorted([r for r in saved['thermal_results'] if r['map'] == name and r['order'] == 32],
                      key=lambda r: r['T_K'])
        axes[0].loglog([r['T_K'] for r in rows], [r['kappa_cm3_per_s'] for r in rows], 'o-',
                       color=color, label=name)
        for h, style in ((0, '-'), (1, '--')):
            owned = sorted([r for r in saved['owner_rows'] if r['map'] == name and r['h'] == h and
                            r['radiation_route'] == 'emissivity_handoff'], key=lambda r: r['T_K'])
            axes[1].semilogx([r['T_K'] for r in owned], [r['Cv_Tdot_over_R_eV'] for r in owned],
                            'o'+style, color=color, label=name+', h='+str(h))
    parent = sorted(saved['parent_saved_order32_rows'], key=lambda r: r['T_K'])
    axes[0].loglog([r['T_K'] for r in parent], [r['kappa_cm3_per_s'] for r in parent], 's:',
                   color='#626262', label='Saved PHYS87 atomic-native baseline')
    axes[0].set(xlabel='Common temperature [K]', ylabel='Conditional finite-window kappa [cm³/s]',
                title='Saved four-temperature moments; distinct bare-map supports')
    axes[1].set(xlabel='Common temperature [K]', ylabel='Cv Tdot / R [eV/event]')
    axes[1].axhline(0, color='.5', lw=.6)
    for axis in axes:
        axis.legend(fontsize=8); axis.grid(alpha=.2)
    fig.supxlabel('Connecting lines are visual guides; h=1 is instantaneous caloric birth, not stopping.', fontsize=8)
    # Preserve the original draw order and constrained-layout state without a PNG file.
    png = io.BytesIO()
    fig.savefig(png, format='png', dpi=180)
    png_raw = png.getvalue(); png.close()
    rec['PNG_BytesIO_control'] = {'bytes': len(png_raw), 'sha256': hashlib.sha256(png_raw).hexdigest(),
                                'expected_sha256': EXPECTED_PNG_SHA}
    if rec['PNG_BytesIO_control']['sha256'] != EXPECTED_PNG_SHA:
        plt.close(fig)
        raise ValueError('PNG BytesIO control differs; stop without PDF or another render')
    pdf = io.BytesIO()
    creation = datetime.datetime(2026, 10, 24, 7, 6, 1,
        tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    rec['PDF_render_calls'] = 1
    fig.savefig(pdf, format='pdf', dpi=None, metadata={'CreationDate': creation})
    raw = pdf.getvalue(); pdf.close(); plt.close(fig)
    rec['first_closed_PDF'] = write_closed(output/'conditional_bare_moments_candidate.pdf', raw)
    matched = raw if len(raw) == EXPECTED_PDF_BYTES and hashlib.sha256(raw).hexdigest() == EXPECTED_PDF_SHA else None
    if matched is None:
        # These are byte substitutions only, after one closed PDF. Equal length
        # preserves all xref offsets; no new figure, draw, savefig or supplier call.
        stamp = b"/CreationDate (D:20261024070601-05'00')"
        if raw.count(stamp) != 1:
            raise ValueError('Expected single fixed-length CreationDate token unavailable')
        for candidate_stamp in [b"/CreationDate (D:20261024070558-05'00')",
                                b"/CreationDate (D:20261024070559-05'00')",
                                b"/CreationDate (D:20261024070600-05'00')"]:
            if len(candidate_stamp) != len(stamp):
                raise ValueError('Metadata replacement would change PDF offsets')
            candidate = raw.replace(stamp, candidate_stamp, 1)
            digest = hashlib.sha256(candidate).hexdigest()
            rec['metadata_only_candidates'].append({'CreationDate_token': candidate_stamp.decode(),
                'bytes': len(candidate), 'sha256': digest, 'new_render': False})
            if len(candidate) == EXPECTED_PDF_BYTES and digest == EXPECTED_PDF_SHA:
                matched = candidate
                break
    if matched is None:
        raise ValueError('One PDF render and bounded metadata-only candidates did not match; no rerender authorized')
    rec['exact_recovered_PDF'] = write_closed(output/'conditional_bare_moments_EXACT.pdf', matched)
    rec['status'] = 'EXACT_EXPECTED_PDF_RECOVERED'


if __name__ == '__main__':
    raise SystemExit(main())
