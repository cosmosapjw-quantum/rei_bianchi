"""Inspect saved exact endpoints; no source flow is rerun."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import argparse
import hashlib
import json


def dyad(d):
    return Fraction(int(d['mantissa'])) * Fraction(2) ** int(d['exponent_2'])


def scan(o, path):
    if isinstance(o, dict):
        if 'lower_exact_dyadic' in o:
            lo, hi = dyad(o['lower_exact_dyadic']), dyad(o['upper_exact_dyadic'])
            dlo, dhi = Fraction(Decimal(o['lower'])), Fraction(Decimal(o['upper']))
            assert dlo <= lo <= hi <= dhi, path
            yield path
        for k, v in o.items():
            yield from scan(v, path + '/' + k)
    elif isinstance(o, list):
        for k, v in enumerate(o):
            yield from scan(v, path + '/' + str(k))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('candidate', type=Path)
    p.add_argument('--source-audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    reports = []
    for name in ['REMAINDER_256_FINAL.json', 'REMAINDER_384_CHECK.json']:
        path = a.candidate / 'results' / name
        d = json.loads(path.read_text())
        count = len(list(scan(d, name)))
        c = d['leading']['c3_normalized']
        r = d['fourth_derivative_divided_by_factorial_uniform']
        i = d['I_over_lambda_s_at_h_enclosure']
        rlo, rhi = dyad(r['lower_exact_dyadic']), dyad(r['upper_exact_dyadic'])
        clo, chi = dyad(c['lower_exact_dyadic']), dyad(c['upper_exact_dyadic'])
        ilo, ihi = dyad(i['lower_exact_dyadic']), dyad(i['upper_exact_dyadic'])
        assert ilo <= clo + rlo and chi + rhi <= ihi < 0
        assert 0 < rlo <= rhi and rhi / (-chi) < Fraction(269, 100000)
        reports.append({
            'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'all_decimal_exports_outward': True, 'exported_balls_checked': count,
            'signed_sum_enclosed': True, 'strict_negative_endpoint': True,
            'relative_tail_below_0p269_percent': True})
    identity = json.loads((a.candidate / 'INPUT_IDENTITY.json').read_text())
    for f in identity['files']:
        path = a.candidate / f['path']
        assert path.stat().st_size == f['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == f['sha256']
    audit = json.loads(a.source_audit.read_text())
    for path, digest in audit['candidate_sha256'].items():
        assert hashlib.sha256((a.candidate / path).read_bytes()).hexdigest() == digest
    out = {
        'kind': 'DECISION_REVIEWER_EXACT_RATIONAL_CERTIFICATE_SCAN',
        'status': 'PASS_SCOPED', 'arithmetic': 'fractions.Fraction; Decimal parse only',
        'reports': reports, 'input_identity_files_matched': len(identity['files']),
        'source_audit_candidate_hashes_matched': len(audit['candidate_sha256']),
        'IVP_trajectories': 0, 'native_runs': 0, 'BE_roots': 0}
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'status': out['status'], 'result_files': len(reports)}, indent=2))


if __name__ == '__main__':
    main()
