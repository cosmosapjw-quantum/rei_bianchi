"""Finalize independent HE34-SCR review records by artifact readback only.

No author files are written. No scientific solver, transport module, renderer,
benchmark, or old suite is imported or executed.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import xml.etree.ElementTree as ET


OWN = Path(__file__).resolve().parent
REPO = Path('/tmp/he32_resume_20261022/repos/BASS_HE')
UNIT = REPO / 'research/he34_sandbox_certified_relaxation_20261022'
NOW = datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(name, payload):
    target = OWN / name
    fd, temporary = tempfile.mkstemp(prefix=name + '.', suffix='.tmp', dir=OWN)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(payload, handle, indent=2, allow_nan=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        fd = os.open(OWN, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


reviewed_names = [
    'CONTRACT.json',
    'theory/CERTIFIED_REDUCTION.md',
    'theory/NEUTRAL_TRANSPORT_KO.md',
    'data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json',
    'data/SAVED_BACKGROUND.csv',
    'src/certified_relaxation.py',
    'src/neutral_transport.py',
    'run_control.py',
    'checks/check_relaxation.py',
    'checks/check_transport.py',
    'plot_results.py',
    'results/MECHANICAL_CONTROLS.json',
    'results/MECHANICAL_RECEIPT.json',
    'results/mechanics_chi_10.csv',
    'results/mechanics_chi_100.csv',
    'results/mechanics_chi_1000.csv',
    'results/mechanics_chi_10000.csv',
    'results/NEUTRAL_TRANSPORT.json',
    'results/NEUTRAL_H_HE_s07_m03_r03.csv',
    'evidence/CONTROL_NUMERICAL_GUARD.json',
    'evidence/MECHANICAL_EXECUTION.json',
    'evidence/TRANSPORT_VALIDATION.json',
    'evidence/PLOT_EXECUTION.json',
    'figures/MECHANICAL_ERROR_CERTIFICATE.png',
    'figures/MECHANICAL_ERROR_CERTIFICATE.svg',
    'figures/NEUTRAL_TRANSPORT_DIAGNOSTIC.png',
    'figures/NEUTRAL_TRANSPORT_DIAGNOSTIC.svg',
]
unit_hashes = {name: sha(UNIT / name) for name in reviewed_names}
assert unit_hashes['src/certified_relaxation.py'] == '1b1c717c630aed08afe3a8e39a33395f74cd6684ea355ef126fbdfcb31c90e12'
assert unit_hashes['run_control.py'] == '891f08aefadfb45929e3c8a6891f16e1983dead02e3016bb095fa5f954eff370'
initial = json.loads((OWN / 'REVIEWED_SOURCE_HASHES_INITIAL.json').read_text())
changes = {name: {'initial': value, 'final': unit_hashes[name]}
           for name, value in initial.items() if unit_hashes[name] != value}
assert set(changes) == {'CONTRACT.json', 'src/certified_relaxation.py', 'run_control.py'}
contract = json.loads((UNIT / 'CONTRACT.json').read_text())
assert contract['acceptance']['numerical_quadrature_estimate_plus_tail_max'] == 1e-9
for record_name in ['TRANSPORT_OUTPUT_REVIEW.json', 'MECHANICAL_OUTPUT_REVIEW.json']:
    record = json.loads((OWN / record_name).read_text())
    assert record['passed']
    assert all(unit_hashes[name] == value for name, value in record['artifact_sha256'].items())

upstream = Path('/tmp/he34_transport_sources/upstream')
upstream_names = ['CapitelliIntegrals.h', 'CapitelliIntegrals.cpp', 'CollisionDB.cpp',
                  'ViscosityChapmannEnskog.cpp', 'collisions.xml']
source_manifest = {
    'schema': 'he34_scr.independent_review_source_hashes.v1',
    'unit': 'HE34-SCR', 'recorded_utc': NOW,
    'unit_root': str(UNIT), 'hash_algorithm': 'sha256',
    'unit_files': unit_hashes,
    'repo_policy': {'AGENTS.md': sha(REPO / 'AGENTS.md')},
    'changes_from_initial_review': changes,
    'upstream': {
        'Mutation++_commit': '58678c0e038eb2f078fed3b45640741fdaf167dc',
        'local_source_root': str(upstream),
        'files': {name: sha(upstream / name) for name in upstream_names},
        'collisions_xml_git_blob': 'd86bf74e05e6bcac9db67cfc03055621ebed2f8c',
        'Wargnier_author_PDF': 'https://jbscoggi.github.io/website/assets/pdf/Wargnier2020_A&A.pdf',
        'Bruno_DOI': '10.1063/1.3495980',
    },
    'qualification': 'Hashes identify reviewed bytes; they do not enlarge the scientific scope of the review.'
}
atomic_json('FINAL_SOURCE_HASHES.json', source_manifest)

plot = json.loads((UNIT / 'evidence/PLOT_EXECUTION.json').read_text())
assert plot['status'] == 'passed'
assert all(sha(UNIT / name) == value for name, value in plot['inputs_sha256'].items())
assert all(sha(UNIT / name) == value for name, value in plot['code_sha256'].items())
assert len(plot['attempts']) == 2
assert all(a['exit_code'] == 0 and not a['stderr'] for a in plot['attempts'])
environment = plot['attempts'][-1]['environment']
fingerprint = {
    'inputs': plot['inputs_sha256'], 'code': plot['code_sha256'],
    'render_environment': {key: environment[key] for key in
        ('matplotlib', 'numpy', 'pillow', 'backend', 'font_size_pt', 'png_dpi')},
    'font_sha256': environment['font']['sha256'],
}
assert hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest() == plot['cache_identity']
assert sha(Path(environment['font']['path'])) == environment['font']['sha256']
assert [(a['new_render_pairs'], a['reused_render_pairs']) for a in plot['attempts']] == [(2, 0), (0, 2)]
assert 'no renderer invoked' in plot['attempts'][1]['stdout']
assert plot['cumulative_counts'] == {
    'new_render_pairs': 2, 'new_png_files': 2, 'new_svg_files': 2,
    'reused_render_pairs': 2, 'old_HE32_renders_repeated': 0,
    'new_IVPs': 0, 'new_benchmarks': 0,
}
outputs = {}
for name, info in plot['outputs'].items():
    path = UNIT / name
    assert sha(path) == info['sha256']
    assert path.stat().st_size == info['bytes']
    entry = {'sha256': sha(path), 'bytes': path.stat().st_size}
    height_mm = 150.0 if 'MECHANICAL' in name else 145.0
    if path.suffix == '.png':
        raw = path.read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n'
        size = list(struct.unpack('>II', raw[16:24]))
        assert size == info['pixels']
        assert abs(size[0] - 90.0 / 25.4 * 300) < 1
        assert abs(size[1] - height_mm / 25.4 * 300) < 1
        entry['pixels'] = size
        entry['actual_original_resolution_image_inspection'] = 'passed'
    else:
        root = ET.parse(path).getroot()
        assert root.attrib['width'].endswith('pt') and root.attrib['height'].endswith('pt')
        size_mm = [float(root.attrib[key][:-2]) * 25.4 / 72 for key in ('width', 'height')]
        assert abs(size_mm[0] - 90.0) < 1e-5 and abs(size_mm[1] - height_mm) < 1e-5
        entry['export_dimensions_mm'] = size_mm
    outputs[name] = entry

visual = {
    'schema': 'he34_scr.independent_visual_review.v1', 'unit': 'HE34-SCR',
    'recorded_utc': NOW, 'status': 'passed', 'open_findings': [],
    'method': 'Direct original-resolution inspection of both saved PNGs using view_image, followed by read-only artifact/provenance/cache verification.',
    'plot_execution_sha256': unit_hashes['evidence/PLOT_EXECUTION.json'],
    'plot_source_sha256': unit_hashes['plot_results.py'],
    'cache_identity': plot['cache_identity'], 'outputs': outputs,
    'checks': {
        'input_code_output_hashes_match': True,
        'recorded_cache_identity_recomputes': True,
        'actual_font_hash_matches': True,
        'actual_PNG_and_SVG_dimensions_match': True,
        'first_attempt_two_pairs_then_cache_reuse_two_pairs': True,
        'labels_ticks_units_legends_readable': True,
        'no_clipped_text_or_scope_notes': True,
        'saved_data_to_plot_mapping_reviewed': True,
        'mechanical_fixed_target_and_discrete_status_match_results': True,
        'mechanical_saved_node_errors_distinguished_from_continuum_envelopes': True,
        'neutral_subset_common_temperature_units_visible': True,
        'neutral_chi_one_explicitly_diagnostic_only': True,
    },
    'figure_observations': {
        'MECHANICAL_ERROR_CERTIFICATE': [
            'Two logarithmic panels; ratio and log-pressure are dimensionless absolute errors.',
            'Blue solid filled-circle errors remain distinguishable from orange dashed hollow-square envelopes.',
            'Fixed 1e-6 target and chi=10,100 rejected / chi=1000,10000 accepted labels are legible.',
            'Connecting lines summarize four sampled chi values; no intermediate-chi acceptance is certified.'
        ],
        'NEUTRAL_TRANSPORT_DIAGNOSTIC': [
            'Viscosity is correctly displayed in 1e-4 Pa s; chi_match=nu_match/H is dimensionless.',
            'Neutral H1 plus He4, common T=20000 K, and descending mean redshift are explicit.',
            'The chi=1 line and final caption state diagnostic scope and exclude a fluid certificate.',
            'Scope annotations occupy unused plot area without hiding data.'
        ],
    },
    'reviewer_new_render_pairs': 0, 'reviewer_new_scientific_calculations': 0,
}
atomic_json('VISUAL_REVIEW.json', visual)

review_files = [
    'PHYSICS_AND_CODE_REVIEW.md', 'INDEPENDENT_CHECKS.json', 'IMPLEMENTATION_CHECKS.json',
    'VARYING_SOURCE_CHECKS.json', 'CONTROL_GUARD_READBACK.json',
    'TRANSPORT_OUTPUT_REVIEW.json', 'MECHANICAL_OUTPUT_REVIEW.json',
    'VISUAL_REVIEW.json', 'REVIEWED_SOURCE_HASHES_INITIAL.json', 'FINAL_SOURCE_HASHES.json',
    'independent_checks.py', 'implementation_checks.py', 'varying_source_checks.py',
    'finalize_review.py',
]
structured = {
    'schema': 'he34_scr.independent_scientific_review.v1',
    'unit': 'HE34-SCR', 'unit_path': str(UNIT), 'recorded_utc': NOW,
    'workflow_version': '1.0.0', 'approval_version': '0.2',
    'verdict': 'pass_within_stated_scope', 'open_blockers': 0,
    'reviewer_role': 'Independent of theory/implementation authors and saved-background execution',
    'author_files_modified_by_reviewer': 0,
    'stages_in_review_order': [
        {'stage': 'physics_and_primary_source_audit', 'status': 'passed'},
        {'stage': 'mathematics_code_and_normalization_audit', 'status': 'passed'},
        {'stage': 'saved_output_receipt_and_timing_readback', 'status': 'passed'},
        {'stage': 'actual_image_and_plot_provenance_review', 'status': 'passed'},
    ],
    'findings': [
        {
            'id': 'SCR-R1', 'severity': 'medium', 'status': 'resolved_before_first_saved_background_execution',
            'evidence': 'Initial driver did not gate the separately computed quadrature convergence and finite numerical budget; the solver continuum flag was correctly scoped.',
            'fix': 'Revised driver records and requires approximation availability, quadrature convergence, and finite estimate-plus-tail <= 1e-9, separately from continuum acceptance.',
            'minimal_test': 'Valid result accepted; nonconverged, unavailable, over-budget, and nonfinite results rejected.',
            'verification': 'CONTROL_GUARD_READBACK.json',
            'fixed_source_sha256': unit_hashes['run_control.py'],
        },
        {
            'id': 'SCR-R2', 'severity': 'low', 'status': 'resolved_before_first_saved_background_execution',
            'evidence': 'Initial benchmark always ran the reduced lane before the selected implicit lane.',
            'fix': 'Alternate execution order over five trials and preserve actual order and all raw times.',
            'minimal_test': 'Inspect alternating trial-order metadata and both timed branches in saved receipt.',
            'verification': 'MECHANICAL_OUTPUT_REVIEW.json',
            'fixed_source_sha256': unit_hashes['run_control.py'],
        },
    ],
    'mechanical_decisions_at_fixed_1e_6': {
        'chi_10': 'reject', 'chi_100': 'reject',
        'chi_1000': 'accept_continuum_bound', 'chi_10000': 'accept_continuum_bound',
    },
    'qualifications': [
        'Analytic continuum certification is distinct from binary64 evaluation, finite reference evidence, and quadrature estimates; outward-rounded arithmetic is not provided.',
        'The mechanical source is the prescribed saved piecewise-linear signed shear; no self-consistent background or full cosmological IVP was solved.',
        'Neutral H1/He4 viscosity uses the stated mass-number convention and common temperature; physical fit and kinetic truncation uncertainties are outside the mechanical certificate.',
        'nu_match=p/eta is hydrodynamic matching and is not an exact transient Boltzmann relaxation eigenvalue or fluid-validity certificate.',
        'Timing ratios are bounded host measurements with retained scatter; the selected implicit baseline is more accurate than the target and is not shown to be accuracy-optimized.',
    ],
    'reviewer_execution_scope': {
        'old_HE32_background_runs': 0, 'old_HE33_suite_runs': 0,
        'new_full_cosmological_IVPs': 0, 'new_synthetic_reference_histories': 2,
        'new_synthetic_reference_source_intervals': 6,
        'new_figure_renders': 0, 'benchmark_reruns': 0,
    },
    'review_artifacts_sha256': {name: sha(OWN / name) for name in review_files},
}
atomic_json('INDEPENDENT_REVIEW.json', structured)
print(json.dumps({'verdict': structured['verdict'], 'open_blockers': 0,
                  'final_core_sha256': unit_hashes['src/certified_relaxation.py'],
                  'visual_status': visual['status'],
                  'artifacts': ['PHYSICS_AND_CODE_REVIEW.md', 'INDEPENDENT_REVIEW.json',
                                'FINAL_SOURCE_HASHES.json', 'VISUAL_REVIEW.json']}, indent=2))
