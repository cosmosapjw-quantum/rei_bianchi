#!/usr/bin/env python3
"""Independent PHYS91 exact reference; resume uses metadata only."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
from pathlib import Path
from evidence import UNIT, REPO, identity, main_args, resume, fresh, publish, write_json


def read_json(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def primary_binding(directory, binding):
    """Hash-only dependency validation, permitted before a resume SKIP."""
    directory = Path(directory)
    result = resume(directory, 'primary', binding)
    manifest = read_json(directory/'MANIFEST.json')
    for name in ('RESULTS.json', 'CERTIFICATES.json', 'CHECKPOINTS.json',
                 'FIXTURES_AND_GUARDS.json'):
        require(name in manifest['payload_sha256'], 'PRIMARY_REQUIRED_FILE:'+name)
    return {'manifest_sha256': result['manifest_sha256'],
            'identity_sha256': binding['sha256'],
            'payload_sha256': manifest['payload_sha256']}


def exact_checker():
    """Construct the independent integer/Fraction checker after resume handling."""
    from fractions import Fraction
    from math import gcd

    def rat(x):
        require(type(x) in (int, str, Fraction), 'INVALID_OR_NONFINITE_RATIONAL_TOKEN')
        try:
            return Fraction(x)
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError('INVALID_OR_NONFINITE_RATIONAL_TOKEN') from exc

    def matrix_pair(f, h):
        n = len(f)
        require(n > 0 and len(h) == n and all(len(row) == n for row in f+h),
                'MATRIX_DIMENSION')
        f = [[rat(x) for x in row] for row in f]
        h = [[rat(x) for x in row] for row in h]
        require(all(f[i][j] == f[j][i] for i in range(n) for j in range(n)), 'ASYMMETRIC_F')
        require(all(h[i][j] == h[j][i] for i in range(n) for j in range(n)), 'ASYMMETRIC_H')
        require(all(x >= 0 for row in h for x in row), 'NEGATIVE_H')
        scale = 1
        for row in f+h:
            for x in row:
                scale = scale//gcd(scale, x.denominator)*x.denominator
        return {'f': f, 'h': h, 'n': n, 'scale': scale,
                'a': [[int(x*scale) for x in row] for row in f],
                'b': [[int(x*scale) for x in row] for row in h]}

    def factor(v, q, n):
        require(type(q) is int and q > 0 and isinstance(v, list) and len(v) == n,
                'FACTOR_DENOMINATOR_OR_DIMENSION')
        require(all(isinstance(row, list) for row in v), 'FACTOR_ROW_TYPE')
        rank = len(v[0])
        require(rank <= n and all(len(row) == rank for row in v), 'FACTOR_RANK_OR_RAGGED')
        require(all(type(x) is int for row in v for x in row), 'FACTOR_NOT_INTEGER')
        # Independent full Gram construction. Symmetry follows exactly.
        g = [[0]*n for _ in range(n)]
        for i, row in enumerate(v):
            for j in range(i, n):
                value = sum(a*b for a, b in zip(row, v[j]))
                g[i][j] = value
                g[j][i] = value
        return rank, g

    def padding_guard(values, denominator, n):
        require(type(denominator) is int and denominator > 0 and len(values) == n,
                'PADDING_DENOMINATOR_OR_DIMENSION')
        require(all(type(x) is int and x >= 0 for x in values), 'NEGATIVE_OR_NONINTEGER_PADDING')

    def primal(table, v, q, rho):
        n = table['n']; f = table['f']; h = table['h']
        rank, g = factor(v, q, n)
        radius = rat(rho)
        require(radius >= 0, 'NEGATIVE_RADIUS')
        # Compute padding as rational diagonal differences, independently of the
        # production integer numerator formula. Retain its declared denominator.
        den = table['scale']*radius.denominator*q*q
        diagonal = [max(f[i][i]+radius*h[i][i]-Fraction(g[i][i], q*q), Fraction(0))
                    for i in range(n)]
        padding = [int(x*den) for x in diagonal]
        require(all(Fraction(p, den) == d for p, d in zip(padding, diagonal)), 'PADDING_SCALE')
        padding_guard(padding, den, n)
        alpha = Fraction(0); witness = None; violations = []; checked = 0
        for i in range(n):
            for j in range(i, n):
                checked += 1
                value = Fraction(g[i][j], q*q)+(diagonal[i] if i == j else 0)
                error = value-f[i][j]
                if h[i][j] == 0:
                    if error:
                        violations.append([i, j])
                    continue
                ratio = abs(error)/h[i][j]
                if witness is None or ratio > alpha:
                    alpha = ratio
                    witness = {'i': i, 'j': j, 'candidate_entry': value,
                               'F_entry': f[i][j], 'H_entry': h[i][j],
                               'signed_error': error, 'ratio': ratio}
        if violations:
            alpha = None
        return {'kind': 'RATIONAL_GRAM_PLUS_NONNEGATIVE_DIAGONAL',
                'status': 'FINITE_EXACT_UPPER' if alpha is not None else 'FIXED_ZERO_H_ENTRY_VIOLATION',
                'n': n, 'rank': rank, 'q': q, 'factor': v, 'rho': radius,
                'padding_numerators': padding, 'padding_denominator': den,
                'alpha': alpha, 'alpha_witness': witness, 'upper_entries_checked': checked,
                'zero_H_fixed_entry_violations': violations,
                'B1_exists': alpha is not None and alpha <= 1}

    def dual(table, w, q):
        n = table['n']; rank, g = factor(w, q, n)
        # Full ordered matrix contraction: offdiagonal multiplicity is obtained
        # by actual i,j iteration, and abs is taken after factor summation.
        signed = sum(table['a'][i][j]*g[j][i] for i in range(n) for j in range(n))
        support = sum(table['b'][i][j]*abs(g[i][j]) for i in range(n) for j in range(n))
        nonzero = any(x for row in w for x in row)
        denominator = table['scale']*q*q
        beta = Fraction(-signed, support) if support else None
        status = ('ZERO_FACTOR_NO_BOUND' if not nonzero else
                  'FINITE_EXACT_LOWER' if support else
                  'ZERO_SUPPORT_ALL_FINITE_RADII_EXCLUDED' if signed < 0 else
                  'ZERO_SUPPORT_NO_BOUND')
        return {'kind': 'GENERAL_RATIONAL_GRAM_PSD_DUAL', 'status': status,
                'n': n, 'rank': rank, 'q': q, 'factor': w,
                'trace_numerator': signed, 'support_numerator': support,
                'common_denominator': denominator, 'trace': Fraction(signed, denominator),
                'support': Fraction(support, denominator), 'beta': beta,
                'B1_signed_upper': Fraction(signed+support, denominator),
                'B1_excluded': bool(nonzero and signed+support < 0),
                'upper_entries_checked': n*(n+1)//2}

    def enclosure(alpha, beta, inherited):
        alpha = rat(alpha); inherited = rat(inherited)
        beta = max(Fraction(0), Fraction(0) if beta is None else rat(beta))
        require(beta <= alpha and alpha > inherited,
                'STOP_NO_ADMISSION_PRIMAL_DUAL_OR_INHERITED_CONTRADICTION')
        exists = alpha <= 1; excluded = beta > 1
        require(not (exists and excluded), 'STOP_NO_ADMISSION_B1_CONTRADICTION')
        lower = max(beta, inherited)
        return {'lower': lower, 'lower_strict': beta <= inherited,
                'upper': alpha, 'upper_inclusive': True, 'dual_beta': beta,
                'inherited_pair_lower': inherited,
                'B1_status': 'EXISTS_BY_EXACT_PRIMAL' if exists else
                'EXCLUDED_BY_EXACT_GENERAL_PSD_DUAL' if excluded else
                'B1_UNRESOLVED_WITH_CERTIFIED_GLOBAL_DISTANCE_ENCLOSURE'}

    def serialized(value):
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, dict):
            return {k: serialized(v) for k, v in value.items()}
        if isinstance(value, list):
            return [serialized(v) for v in value]
        return value

    return Fraction, rat, matrix_pair, primal, dual, enclosure, serialized, padding_guard


def independent_fixtures(tools):
    R, rat, table, primal, dual, combine, serial, padguard = tools
    outcomes = {}
    def check(name, condition):
        require(condition, 'REFERENCE_FIXTURE_FAILED:'+name)
        outcomes[name] = True
    def reject(name, callback):
        try:
            callback()
        except (ValueError, TypeError):
            outcomes[name] = True
            return
        raise ValueError('REFERENCE_GUARD_FAILED:'+name)
    t = table([[1, 0], [0, 1]], [[1, 1], [1, 1]])
    p = primal(t, [[1, 1], [1, -1]], 2, 0)
    check('small_Gram_nonnegative_diagonal', p['alpha'] == 0 and p['padding_numerators'] == [2, 2])
    p1 = primal(table([[0]], [[1]]), [[1]], 1, 1)
    check('alpha1_inclusive', p1['alpha'] == 1 and p1['B1_exists'])
    d1 = dual(table([[-1]], [[1]]), [[1]], 1)
    d2 = dual(table([[-2]], [[1]]), [[1]], 1)
    check('beta1_not_exclusion', d1['beta'] == 1 and not d1['B1_excluded'])
    check('beta_gt1_strict_exclusion', d2['beta'] == 2 and d2['B1_excluded'])
    reject('negative_padding_rejected', lambda: padguard([-1], 1, 1))
    d0 = dual(t, [[], []], 1)
    check('zero_factor_no_bound', d0['beta'] is None and d0['status'] == 'ZERO_FACTOR_NO_BOUND')
    zt = table([[1]], [[0]])
    check('zero_H_fixed_entry_exact', primal(zt, [[1]], 1, 1)['alpha'] == 0)
    check('zero_H_violation', primal(zt, [[2]], 1, 1)['alpha'] is None)
    check('zero_support_negative_trace', dual(table([[-1]], [[0]]), [[1]], 1)['status'] ==
          'ZERO_SUPPORT_ALL_FINITE_RADII_EXCLUDED')
    reject('negative_H', lambda: table([[1]], [[-1]]))
    reject('asymmetric_F', lambda: table([[1, 1], [0, 1]], [[1, 1], [1, 1]]))
    reject('asymmetric_H', lambda: table([[1, 0], [0, 1]], [[1, 1], [0, 1]]))
    reject('wrong_dimension', lambda: table([[1, 0]], [[1]]))
    reject('nonfinite_token', lambda: rat('NaN'))
    reject('noninteger_factor', lambda: primal(t, [[True], [0]], 1, 1))
    from evidence import check_input_blob
    reject('source_identity_mismatch', lambda: check_input_blob(b'altered', 7, '0'*64))
    reject('contradiction_stops', lambda: combine(1, 2, 0))
    S = [[0, 1, 0, -1], [1, 0, 1, 0], [0, 1, 0, 1], [-1, 0, 1, 0]]
    f = [[int(i == j)+S[i][j] for j in range(4)] for i in range(4)]
    h = [[R(1, 10) if i == j or S[i][j] else R(1) for j in range(4)] for i in range(4)]
    w = [[int(i == j)-S[i][j] for j in range(4)] for i in range(4)]
    t4 = table(f, h); full = dual(t4, w, 1)
    separate = sum((dual(t4, [[row[k]] for row in w], 1)['support'] for k in range(4)), R(0))
    check('general_PSD_combined_support', full['trace'] == -4 and full['support'] == R(14, 5)
          and full['beta'] == R(10, 7) and full['B1_signed_upper'] == R(-6, 5)
          and separate == R(54, 5))
    check('S_square2I', all(sum(S[i][k]*S[k][j] for k in range(4)) == 2*int(i == j)
                          for i in range(4) for j in range(4)))
    # Exact finite sign cases instantiate the theory forest argument; no vector
    # sampling is substituted for the all-real-w theorem.
    forest_cases = 0
    for mask in range(16):
        signs = [1 if mask & (1 << i) else -1 for i in range(4)]
        A = [[1 if i == j or S[i][j] == 0 else signs[i]*S[i][j]*signs[j]
              for j in range(4)] for i in range(4)]
        colors = [None]*4
        for start in range(4):
            if colors[start] is not None:
                continue
            colors[start] = 1; stack = [start]
            while stack:
                i = stack.pop()
                for j in range(4):
                    if i != j and A[i][j] == -1:
                        if colors[j] is None:
                            colors[j] = -colors[i]; stack.append(j)
                        require(colors[j] == -colors[i], 'FOREST_COLOR_CONTRADICTION')
        require(all(A[i][j]-colors[i]*colors[j] >= 0 for i in range(4) for j in range(4)),
                'FOREST_ENTRYWISE_NONNEGATIVE')
        forest_cases += 1
    outcomes['rank_one_gap_forest_sign_cases'] = forest_cases
    outcomes['all_rank_one_statement_basis'] = 'THEORY_FOREST_PROOF_WITH_EXACT_SIGN_CASE_IDENTITIES'
    L = [[1, 1], [1, -1], [-2, 0]]; q = [1, 1, 1]
    C = [[R(2), R(1)], [R(1), R(3)]]
    require(all(sum(q[i]*L[i][j] for i in range(3)) == 0 for j in range(2)), 'CONSUMER_qTL')
    K = [[sum((L[i][a]*C[a][b]*L[j][b] for a in range(2) for b in range(2)), R(0))
          for j in range(3)] for i in range(3)]
    check('same_map_qTK_Kq_zero', all(sum(q[i]*K[i][j] for i in range(3)) == 0 for j in range(3))
          and all(sum(K[i][j]*q[j] for j in range(3)) == 0 for i in range(3)))
    outcomes['physical_consumer_ACK'] = None
    return outcomes


def compute(primary_output, dependency):
    import time
    tools = exact_checker()
    R, rat, table, primal, dual, combine, serial, _ = tools
    contract = read_json(UNIT/'CONTRACT.json')
    source, rounding, inherited_raw = [read_json(REPO/x['path']) for x in contract['inputs']]
    n = contract['science']['n']; count = n*(n+1)//2
    require(n == 153 and count == contract['science']['upper_entries'] == 11781, 'FROZEN_ACTUAL_DIMENSION')
    require(len(source['matrix']) == n and len(source['packed']) == count
            and len(rounding['halfULP']) == count, 'ACTUAL_INPUT_SHAPE')
    H = [[R(0) for _ in range(n)] for _ in range(n)];k = 0
    for i in range(n):
        for j in range(i, n):
            require(rat(source['packed'][k]) == rat(source['matrix'][i][j]), 'PACKED_MATRIX_MISMATCH')
            H[i][j] = H[j][i] = rat(rounding['halfULP'][k]);k += 1
    actual = table(source['matrix'], H)
    require(all(x > 0 for row in actual['h'] for x in row), 'ACTUAL_H_NOT_STRICT_POSITIVE')
    inherited = rat(inherited_raw['bracket']['lo'])
    require(inherited == R(34406736621, 68719476736), 'INHERITED_STRICT_LO_IDENTITY')
    root = Path(primary_output); results = read_json(root/'RESULTS.json')
    certs = read_json(root/'CERTIFICATES.json'); history = read_json(root/'CHECKPOINTS.json')
    attempts = history['attempts']
    require(0 < len(attempts) <= 18, 'CHECKPOINT_COUNT')
    require([x['checkpoint'] for x in attempts] == list(range(1, len(attempts)+1)), 'CHECKPOINT_SEQUENCE')
    raw_checkpoints = {};metadata_rows = []
    previous_projection = -1
    for row in attempts:
        filename = row['file']
        require(Path(filename).name == filename, 'CHECKPOINT_FILENAME')
        raw = (root/filename).read_bytes();digest = hashlib.sha256(raw).hexdigest()
        require(digest == row['sha256'] == dependency['payload_sha256'][filename], 'CHECKPOINT_RAW_HASH')
        cp = json.loads(raw);raw_checkpoints[row['checkpoint']] = cp
        require(filename == 'CHECKPOINT_%03d.json' % row['checkpoint'], 'CHECKPOINT_FILENAME_INDEX')
        for field in ('checkpoint', 'stage', 'stage_iteration', 'projections_total', 'rho'):
            require(cp[field] == row[field], 'CHECKPOINT_METADATA:'+field)
        require(1 <= row['stage'] <= 2 and 0 <= row['stage_iteration'] <=
                contract['algorithm']['maximum_projections_each'][row['stage']-1], 'STAGE_PROJECTION_CAP')
        require(previous_projection <= row['projections_total'] <=
                contract['algorithm']['maximum_projections_total'], 'TOTAL_PROJECTION_CAP')
        previous_projection = row['projections_total']
        require(rat(cp['rho']) == rat(contract['algorithm']['radii'][row['stage']-1]), 'CHECKPOINT_RADIUS')
        for role, scalar in (('primal', 'alpha'), ('dual', 'beta')):
            require(cp[role][scalar] == row[scalar], 'CHECKPOINT_SAVED_SCALAR:'+scalar)
            require(cp[role]['q'] == 2**contract['algorithm']['dyadic_denominator_power'], 'DYADIC_DENOMINATOR')
        metadata_rows.append({'checkpoint': row['checkpoint'], 'file': filename, 'sha256': digest,
                              'factors_recomputed': False})
    verified = {}
    for role in ('primal', 'dual'):
        chosen = certs['selected_'+role]
        if chosen is None:
            require(role == 'dual', 'MISSING_SELECTED_PRIMAL')
            continue
        cp = raw_checkpoints[chosen['checkpoint']]
        row = attempts[chosen['checkpoint']-1]
        require(chosen['file'] == row['file'] and chosen['certificate'] == cp[role],
                'SELECTED_CERTIFICATE_CHECKPOINT_BINDING')
        saved = chosen['certificate']
        recalculated = (primal(actual, saved['factor'], saved['q'], cp['rho']) if role == 'primal'
                        else dual(actual, saved['factor'], saved['q']))
        require(serial(recalculated) == saved, 'SELECTED_EXACT_CERTIFICATE_MISMATCH:'+role)
        verified[role] = recalculated
    require(certs['selected_primal']['certificate']['alpha'] ==
            min((x['alpha'] for x in attempts), key=rat), 'SAVED_PRIMAL_SELECTION')
    dual_rows = [x for x in attempts if x['beta'] is not None]
    if dual_rows:
        require(certs['selected_dual'] is not None and
                rat(certs['selected_dual']['certificate']['beta']) == max(rat(x['beta']) for x in dual_rows),
                'SAVED_DUAL_SELECTION')
    else:
        require(certs['selected_dual'] is None, 'SPURIOUS_SELECTED_DUAL')
    alpha = verified['primal']['alpha']
    beta = verified.get('dual', {}).get('beta')
    interval = combine(alpha, beta, inherited)
    require(serial(interval) == results['enclosure'], 'RESULTS_ENDPOINT_OR_B1_MISMATCH')
    require(results['n'] == n and results['upper_entries_checked'] == count
            and results['all_H_strictly_positive_exact'] is True, 'RESULTS_EXACT_COUNTS')
    require(results['retained_exact_checkpoints'] == len(attempts)
            and results['changed_candidate_eigh_calls'] == attempts[-1]['projections_total'],
            'RESULTS_CHECKPOINT_OR_PROJECTION_COUNT')
    require(results['selected_primal_checkpoint'] == certs['selected_primal']['checkpoint']
            and results['selected_dual_checkpoint'] == (None if certs['selected_dual'] is None
                 else certs['selected_dual']['checkpoint']), 'RESULTS_SELECTED_INDICES')
    require(results['actual_matrix_repair'] is False and results['physical_CI'] is False
            and results['actual_consumer_ACK'] is None and results['adopted_source_covariance'] is None
            and results['HH_R10'] == 'OFF' and results['production'] == 'NOT_ISSUED'
            and results['parent_status'] == 'PARTIAL_INPUT_DEPENDENCIES', 'RESULTS_SCOPE_CEILING')
    require(all(value == 0 for value in results['forbidden_operations'].values()), 'FORBIDDEN_OPERATION_RECORD')
    fixture_results = independent_fixtures(tools)
    return {'schema': 'PHYS91_INDEPENDENT_EXACT_REFERENCE_V1', 'status': 'PASS_EXACT_SELECTED_CERTIFICATES',
            'primary_dependency': dependency, 'enclosure': interval, 'n': n,
            'upper_entries_checked_per_selected_certificate': count,
            'selected_primal_verified': True, 'selected_dual_verified': 'dual' in verified,
            'selected_primal_checkpoint': certs['selected_primal']['checkpoint'],
            'selected_dual_checkpoint': None if certs['selected_dual'] is None else certs['selected_dual']['checkpoint'],
            'checkpoint_metadata_and_hashes': metadata_rows,
            'all_checkpoint_factors_recomputed': False,
            'selection_check': 'Exact selected factors recomputed; min/max saved scalar metadata audited for all checkpoints',
            'independent_fixtures': fixture_results,
            'production_kernel_imports': 0, 'primary_imports': 0, 'candidate_generation': 0,
            'eigenvalue_calls': 0, 'raw_F_eigh_calls': 0, 'old_pair_rescans': 0,
            'ENDF_decode': 0, 'ODE': 0, 'integrals': 0, 'benchmark': 0,
            'actual_matrix_repair': False, 'actual_consumer_ACK': None,
            'physical_CI': False, 'strong_physical_no_go': 'NOT_CLAIMED',
            'HH_R10': 'OFF', 'production': 'NOT_ISSUED', 'process_CPU_s': time.process_time()}


def main():
    args = main_args('reference')
    binding = identity()
    dependency = primary_binding(args.primary_output, binding)
    if args.resume:
        # Read-only source/primary/reference identity and raw-hash checks precede
        # Fraction import, scientific computation, output mkdir and every write.
        stored = read_json(args.output/'REFERENCE.json')
        require(stored['primary_dependency'] == dependency, 'REFERENCE_PRIMARY_DEPENDENCY_CHANGED')
        print(json.dumps(resume(args.output, 'reference', binding)))
        return
    output = fresh(args.output)
    try:
        report = compute(args.primary_output, dependency)
        publish(output, 'reference', binding, {'REFERENCE.json': report})
    except BaseException as exc:
        import traceback
        write_json(output, 'FAILURE.json', {
            'status': 'STOP_NO_ADMISSION' if 'STOP_NO_ADMISSION' in str(exc) else 'REFERENCE_FAILED_PRESERVED',
            'exception': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc(),
            'automatic_retry': False, 'identity': binding['sha256'],
            'primary_dependency': dependency, 'HH_R10': 'OFF', 'production': 'NOT_ISSUED'})
        raise
    print(json.dumps({'status': 'COMPLETE', 'kind': 'reference', 'identity': binding['sha256']}))


if __name__ == '__main__':
    main()
