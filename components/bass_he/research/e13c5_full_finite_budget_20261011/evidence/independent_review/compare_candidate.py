#!/usr/bin/env python3
"""Compare saved candidate output to the independent one-pass exact replay."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/scratch/7fd51143e473/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1')
HERE = BASE / 'evidence/independent_review'
CANDIDATE = BASE / 'evidence/budget_control/EXEC01'
COUNTS = Counter()
FAILURES = []

def check(kind, good, identity):
    COUNTS[kind] += 1
    if not good:
        FAILURES.append({'category': kind, 'identity': identity})

def pair(x):
    return F(x['lo']), F(x['hi'])

def eqn(a, b):
    return a is None and b is None or a is not None and b is not None and F(a) == F(b)

def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def main():
    independent = json.loads((HERE / 'INDEPENDENT_ARITHMETIC.json').read_text())
    candidate = json.loads((CANDIDATE / 'RESULTS.json').read_text())
    projection = json.loads((CANDIDATE / 'NUMERICAL_PROJECTION.json').read_text())
    numerical_identity = json.loads((CANDIDATE / 'NUMERICAL_IDENTITY.json').read_text())
    resource = json.loads((CANDIDATE / 'RESOURCE_RECEIPT.json').read_text())
    check('independent_arithmetic_pass', independent['failed_count'] == 0, 'independent')
    check('candidate_status', candidate['status'] == 'PASS_SCOPED_SAVED_FULL_FINITE_BUDGET' and candidate['audit']['failed_count'] == 0, 'candidate')
    check('candidate_resource_pass', resource['status'] == candidate['status'] and resource['wall_seconds'] < 300 and resource['max_RSS_KiB'] < 1024**2, 'candidate')
    check('candidate_no_physics', candidate['new_coefficient_evaluations'] == candidate['new_ODE_native_or_gas_runs'] == 0, 'candidate')
    check('coverage', candidate['coverage']['paths'] == 7320 and candidate['coverage']['segments'] == 14652 and candidate['coverage']['stream_passes'] == 1 and candidate['coverage']['retained_paths'] == 7318, 'candidate')
    partnames = {'full': 'full', 'selected4': 'selected_S4', 'complement2436': 'complement_R2436', 'K2': 'replacement_K2', 'retained': 'retained_outside_K2'}
    variants = {'original': 'old', 'hybrid': 'hybrid'}
    signnames = {'STRICTLY_POSITIVE': 'STRICT_POSITIVE', 'STRICTLY_NEGATIVE': 'STRICT_NEGATIVE', 'EXACT_ZERO': 'EXACT_ZERO', 'UNRESOLVED': 'UNRESOLVED'}
    widthnames = {'original_width': 'old_full', 'hybrid_width': 'hybrid_full', 'selected4_original_width': 'old_selected_S4', 'complement2436_width': 'complement_R2436', 'selected4_share_original': 'old_selected_fraction', 'complement_share_original': 'old_complement_fraction', 'removed_fraction_original': 'gain_fraction_of_old_full', 'retained_width_floor': 'fixed_retained_route_floor', 'max_further_gain_only_K2': 'further_K2_max_gain_at_zero_width'}
    for mode, entries in independent['diagnostics'].items():
        for name, diagnostic in entries.items():
            family, metric = name.split('/')
            c = candidate['budgets_by_mode'][mode][family][metric]
            for iv, cv in variants.items():
                for ip, cp in partnames.items():
                    v = independent['sums'][mode][iv][ip].get(name, {'lo': '0', 'hi': '0'})
                    check('exact_partition_interval', pair(v) == pair(c[cv][cp]), [mode, name, iv, ip])
                check('full_sign', signnames[diagnostic[iv + '_sign']] == c['full_sign'][cv], [mode, name, iv])
                r = independent['rankings'][mode][name][iv]
                ranking = c['concentration'][cv]
                check('top10_node_order', r['top_nodes'][:10] == [x['node'] for x in ranking['top10']], [mode, name, iv])
                for i, row in enumerate(ranking['top10']):
                    check('top10_path_width', F(row['width']) == F(r['top_widths'][i]), [mode, name, iv, i])
                for k in ('1', '2', '4', '10', '100'):
                    check('topk_concentration', eqn(r['topk_fraction'][k], ranking['top_width_fractions'][k]), [mode, name, iv, k])
                check('zero_width_ranking', (ranking['denominator_status'] == 'ZERO_FULL_WIDTH') == r['zero_width'], [mode, name, iv])
            for ik, ck in widthnames.items():
                check('exact_width_budget', eqn(diagnostic[ik], c['width'][ck]), [mode, name, ik])
            p = pair(c['hybrid']['full'])
            maxf = F(c['width']['further_K2_max_gain_at_zero_width']) / (p[1] - p[0]) if p[1] != p[0] else None
            check('max_further_relative_gain', eqn(diagnostic['max_further_fraction_hybrid'], maxf), [mode, name])
            check('whole_full_nesting', c['consistency']['old_full_contains_hybrid'] and c['consistency']['full_overlap'], [mode, name])
            for cv in ('old', 'hybrid'):
                check('candidate_path_sign_count_total', sum(c['path_sign_counts'][cv].values()) == 2440, [mode, name, cv])
    for name, ident in independent['input_identities'].items():
        check('same_immutable_inputs', candidate['input_identities'][name] == ident, name)
    check('projection_file_identity', identity(CANDIDATE / 'NUMERICAL_PROJECTION.json') == {k: numerical_identity[k] for k in ('bytes', 'sha256')}, 'projection')
    object_raw = json.dumps(projection, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    check('projection_object_identity', hashlib.sha256(object_raw).hexdigest() == numerical_identity['canonical_object_sha256'], 'projection')
    for key, value in projection.items():
        check('result_projection_same_field', candidate[key] == value, key)
    check('reducer_source_identity', candidate['source_sha256'] == identity(BASE / 'code/full_finite_budget.py')['sha256'], 'reducer')
    check('contract_source_identity', candidate['contract_sha256'] == identity(BASE / 'SCIENTIFIC_CONTRACT.json')['sha256'], 'contract')
    check('ranking_file_identity', {k: candidate['ranking_artifact'][k] for k in ('bytes', 'sha256')} == identity(CANDIDATE / 'WIDTH_RANKINGS.csv.gz'), 'ranking')
    check('scope_no_promotion', candidate['mode_mixing'] is False and candidate['cross_mode_total'] is None and candidate['intersection_used'] is False and candidate['finite_cover_status'] == 'DONE_INHERITED_PR20_ALL_2440_NODES_PER_MODE' and 'continuum_spectral_quadrature_error' in candidate['holds'] and 'physical_global_admission' in candidate['holds'], 'scope')
    result = {'schema': 'independent-candidate-comparison-v1', 'created_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS' if not FAILURES else 'FAIL', 'check_count': sum(COUNTS.values()), 'check_counts': dict(COUNTS), 'failed_count': len(FAILURES), 'failures': FAILURES, 'inputs': {str(p.relative_to(BASE)): identity(p) for p in (HERE / 'INDEPENDENT_ARITHMETIC.json', CANDIDATE / 'RESULTS.json', CANDIDATE / 'NUMERICAL_PROJECTION.json', CANDIDATE / 'WIDTH_RANKINGS.csv.gz', BASE / 'SCIENTIFIC_CONTRACT.json', BASE / 'code/full_finite_budget.py')}, 'independence': 'Independent arithmetic script never imported the candidate or predecessor producers. This comparison parses their saved outputs only.', 'physical_executions': 0, 'raw_additional_stream_passes': 0}
    with (HERE / 'CANDIDATE_COMPARISON.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'check_count', 'check_counts', 'failed_count', 'failures')}))

if __name__ == '__main__':
    main()
