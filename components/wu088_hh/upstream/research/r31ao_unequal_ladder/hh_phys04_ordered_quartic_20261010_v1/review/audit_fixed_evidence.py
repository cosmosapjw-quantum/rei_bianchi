"""Independent static/rational audit of stored PHYS04 evidence.

No candidate module imports, exponential evaluation, BE root, native dispatch,
or completed scientific suite replay. This audits records and exact identities.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
from datetime import datetime, timezone
import argparse, difflib, hashlib, json

ROOT = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def verify_manifest(name):
    p = ROOT / name
    data = json.loads(p.read_text())
    for item in data['files']:
        raw = (p.parent / item['path']).read_bytes()
        assert len(raw) == item['bytes'], item['path']
        assert sha(raw) == item['sha256'], item['path']
    return {'manifest': name, 'sha256': sha(p.read_bytes()),
            'payload_count': len(data['files']), 'PASS': True}


def rational(record):
    return F(int(record['numerator']), int(record['denominator']))


def endpoints(record):
    return rational(record['lo_exact']), rational(record['hi_exact'])


def audit():
    manifests = [verify_manifest(n) for n in (
        'REVIEW_CORE_INPUTS.json', 'quartic/MANIFEST.json',
        'inputs/source_survey/SURVEY_MANIFEST.json')]
    survey = ROOT / 'inputs/source_survey'
    bindings = read('inputs/source_survey/SOURCE_LINE_BINDINGS.json')
    for b in bindings:
        raw = (survey / b['path']).read_bytes()
        assert sha(raw) == b['source_sha256'], b['id']
        selected = b''.join(raw.splitlines(keepends=True)[b['start']-1:b['end']])
        assert selected == b['selected_text'].encode(), b['id']
        assert len(selected) == b['selected_bytes'], b['id']
        assert sha(selected) == b['selected_sha256'], b['id']
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert git_blob == b['git_blob'], b['id']

    quartic = read('quartic/run_02/EXACT_CHECK.json')
    assert quartic['status'] == 'PASS' and quartic['case_count'] == 6
    assert quartic['exact_scalar_slots_compared'] == 6*2*4*6*4 == 1152
    quartic_diff_slots = 0
    zero_photon_slots = 0
    for case in quartic['cases']:
        assert case['status'] == 'PASS'
        a = list(map(F, case['full_mixed_quartic']))
        b = list(map(F, case['two_half_mixed_quartic']))
        diff = list(map(F, case['quartic_two_half_minus_full']))
        assert [v-u for u, v in zip(a, b)] == diff
        quartic_diff_slots += len(diff)
        if case['zero_initial_photons']:
            assert list(map(F, case['L_dependent_two_half_quartic'])) == list(map(F, case['L_specialization_prediction']))
            zero_photon_slots += len(case['L_dependent_two_half_quartic'])
    assert any(c['old_UVW_nonzero'] for c in quartic['cases'])
    before = (ROOT/'quartic/ordered_be_quartic_run_01_preserved.py').read_text().splitlines()
    after = (ROOT/'quartic/ordered_be_quartic.py').read_text().splitlines()
    diff_lines = list(difflib.unified_diff(before, after, n=1))
    substantive = [s for s in diff_lines if s.startswith(('+', '-')) and not s.startswith(('+++', '---'))]
    assert len(substantive) == 2, substantive
    assert 't/47' in substantive[0] and 'self.d*t/47' in substantive[1]

    remap = read('results/REMAP_OPACITY_EXACT_V1.json')
    box_count = 0
    def boxes(obj):
        nonlocal box_count
        if isinstance(obj, dict):
            if 'lo_exact' in obj:
                lo, hi = endpoints(obj)
                assert lo <= hi
                assert F(Decimal(obj['lo_decimal_outward'])) <= lo
                assert F(Decimal(obj['hi_decimal_outward'])) >= hi
                box_count += 1
            for v in obj.values():
                boxes(v)
        elif isinstance(obj, list):
            for v in obj:
                boxes(v)
    boxes(remap)
    witness_count = 0
    for observable, stats in remap['functionals'].items():
        assert endpoints(stats['defect_two_minus_full'])[1] < 0
        assert endpoints(stats['full'])[0] > 0
        for name in ('full', 'two_half', 'defect_two_minus_full'):
            value = F(Decimal(remap['independent_witnesses'][observable+'_'+name]['decimal']))
            lo, hi = endpoints(stats[name])
            assert lo <= value <= hi
            witness_count += 1
    cols = remap['signed_column_contributions']
    assert [x['node'] for x in cols] == list(range(16,25))
    lower = sum(endpoints(x['weighted_opacity_defect'])[0] for x in cols)
    upper = sum(endpoints(x['weighted_opacity_defect'])[1] for x in cols)
    agglo, agghi = endpoints(remap['functionals']['HI_opacity']['defect_two_minus_full'])
    assert lower <= agglo <= agghi <= upper < 0
    assert endpoints(cols[0]['weighted_opacity_defect'])[0] > 0
    assert endpoints(cols[1]['weighted_opacity_defect'])[1] < 0
    assert all(endpoints(x['weighted_opacity_defect'])[0] > 0 for x in cols[2:])
    assert all(endpoints(c['left_margin_ev'])[0] > 0 for c in remap['cell_certificates'])
    moment = remap['independent_witnesses']['number_energy_with_lower_guard']
    assert all(abs(F(Decimal(v))) < F(Decimal(moment['absolute_witness_tolerance'])) for v in moment['residuals'])
    special = remap['birth_mixed_quartic_specialization']
    assert endpoints(special['ratio_ppm'])[0] > 0
    assert endpoints(special['minus_twohalf_mixed_h4_remap_over_c_nH_q'])[0] > 0
    assert special['finite_gas_error_certificate'] is False

    implicit = read('results/IMPLICIT_MIXED_EXACT_V1.json')
    assert implicit['exact_rational_cases'] == len(implicit['cases']) == 6
    assert implicit['state_derivative_slots'] == 6*4*3 == 72
    assert implicit['zero_residual_slots'] == 6*4*4 == 96
    assert all(c['PASS'] for c in implicit['cases'])
    assert len(implicit['negative_cases']) == 4
    assert all(c['correctly_rejected'] for c in implicit['negative_cases'])
    assert any(c['zero_photon_stock_with_nonzero_signed_derivatives'] for c in implicit['cases'])
    ledger = read('RUN_LEDGER.json')
    for k in ('native_dispatches','nonlinear_BE_roots','IVP_runs','NCP_science_runs','legacy_atomic_integrals','completed_prior_physics_suite_reruns'):
        assert ledger['counts'][k] == 0, k

    return {
        'schema': 'HH_PHYS04_INDEPENDENT_STORED_EVIDENCE_AUDIT_V1',
        'reviewer': '/root/phys04_decision',
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS',
        'manifests': manifests,
        'source_bindings_sha256_line_text_git_blob_checked': len(bindings),
        'quartic_reported_count_consistent': 1152,
        'quartic_stored_difference_slots_exact': quartic_diff_slots,
        'quartic_stored_specialization_slots_exact': zero_photon_slots,
        'preserved_scope_correction_diff': diff_lines,
        'rational_boxes_ordered_and_decimal_outward_checked': box_count,
        'stored_decimal_witnesses_inside_rational_boxes': witness_count,
        'signed_column_sum_negative_and_encloses_factored_aggregate': True,
        'positive_left_cell_margins_checked': len(remap['cell_certificates']),
        'stored_guard_moment_residuals_below_declared_threshold': 4,
        'implicit_reported_counts_and_rejections_consistent': True,
        'claim_ceiling_and_zero_dispatch_consistent': True,
        'native_calls': 0, 'nonlinear_root_calls': 0, 'scientific_suite_replays': 0,
        'independence_limit': 'Stored record integrity and independent rational consistency; no second execution of candidate science or native source attestation.',
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit()
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
