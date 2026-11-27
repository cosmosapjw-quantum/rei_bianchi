"""PHYS91 exact certificates and bounded changed-candidate generator.

Importing this module imports no numerical package and executes no science.
"""
from fractions import Fraction as R
from math import lcm
import json

class CertificateContradiction(ValueError):
    pass

def rational(value):
    try:
        return R(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('NONFINITE_OR_INVALID_TOKEN') from exc

def validate(F, H):
    F = [list(row) for row in F]
    H = [list(row) for row in H]
    n = len(F)
    if not n or len(H) != n or any(len(row) != n for row in F+H):
        raise ValueError('DIMENSION_MISMATCH')
    F = [[rational(x) for x in row] for row in F]
    H = [[rational(x) for x in row] for row in H]
    if any(F[i][j] != F[j][i] for i in range(n) for j in range(n)):
        raise ValueError('NONSYMMETRIC_F')
    if any(H[i][j] != H[j][i] for i in range(n) for j in range(n)):
        raise ValueError('NONSYMMETRIC_H')
    if any(x < 0 for row in H for x in row):
        raise ValueError('NEGATIVE_H')
    return F, H

class ExactTable:
    def __init__(self, F, H):
        self.F, self.H = validate(F, H)
        self.n = len(F)
        self.scale = lcm(*(x.denominator for row in self.F+self.H for x in row))
        self.A = [[int(x*self.scale) for x in row] for row in self.F]
        self.B = [[int(x*self.scale) for x in row] for row in self.H]

def load_inputs(repo, contract):
    source = json.loads((repo/contract['inputs'][0]['path']).read_text())
    rounding = json.loads((repo/contract['inputs'][1]['path']).read_text())
    inherited = json.loads((repo/contract['inputs'][2]['path']).read_text())
    n = contract['science']['n']
    if len(source['matrix']) != n or len(source['packed']) != n*(n+1)//2 or len(rounding['halfULP']) != n*(n+1)//2:
        raise ValueError('SOURCE_SHAPE_MISMATCH')
    H = [[R(0)]*n for _ in range(n)]
    k = 0
    for i in range(n):
        for j in range(i, n):
            if rational(source['packed'][k]) != rational(source['matrix'][i][j]):
                raise ValueError('CACHED_PACKED_MATRIX_DISAGREEMENT')
            H[i][j] = H[j][i] = rational(rounding['halfULP'][k])
            k += 1
    table = ExactTable(source['matrix'], H)
    if any(x <= 0 for row in table.H for x in row):
        raise ValueError('ACTUAL_DISTANCE_REQUIRES_STRICTLY_POSITIVE_H')
    lower = rational(inherited['bracket']['lo'])
    return table, lower

def factor_guard(V, q, n):
    if type(q) is not int or q <= 0 or len(V) != n:
        raise ValueError('FACTOR_DIMENSION_OR_DENOMINATOR')
    rank = len(V[0])
    if any(len(row) != rank for row in V) or any(type(x) is not int for row in V for x in row):
        raise ValueError('NONINTEGER_OR_RAGGED_FACTOR')
    return rank

def padding_guard(numerators, denominator, n):
    if type(denominator) is not int or denominator <= 0 or len(numerators) != n:
        raise ValueError('PADDING_DIMENSION_OR_DENOMINATOR')
    if any(type(x) is not int or x < 0 for x in numerators):
        raise ValueError('NEGATIVE_OR_NONINTEGER_PADDING')

def gram_entries(V):
    n = len(V)
    values = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            values[i][j] = values[j][i] = sum(x*y for x, y in zip(V[i], V[j]))
    return values

def exact_primal(table, V, q, rho):
    rank = factor_guard(V, q, table.n)
    rho = rational(rho)
    if rho < 0:
        raise ValueError('NEGATIVE_RADIUS')
    r, s = rho.numerator, rho.denominator
    S, A, B, n = table.scale, table.A, table.B, table.n
    G = gram_entries(V)
    denominator = S*s*q*q
    padding = [max((s*A[i][i]+r*B[i][i])*q*q-S*s*G[i][i], 0) for i in range(n)]
    padding_guard(padding, denominator, n)
    best_num, best_den = 0, 1
    witness = None
    fixed_violations = []
    count = 0
    for i in range(n):
        for j in range(i, n):
            count += 1
            value = S*s*G[i][j]+(padding[i] if i == j else 0)
            error = value-A[i][j]*s*q*q
            if B[i][j] == 0:
                if error:
                    fixed_violations.append([i, j])
                continue
            numerator, divisor = abs(error), B[i][j]*s*q*q
            if witness is None or numerator*best_den > best_num*divisor:
                best_num, best_den = numerator, divisor
                witness = {'i': i, 'j': j, 'candidate_entry': R(value, denominator),
                           'F_entry': table.F[i][j], 'H_entry': table.H[i][j],
                           'signed_error': R(error, denominator), 'ratio': R(numerator, divisor)}
    alpha = None if fixed_violations else R(best_num, best_den)
    return {'kind': 'RATIONAL_GRAM_PLUS_NONNEGATIVE_DIAGONAL',
            'status': 'FINITE_EXACT_UPPER' if alpha is not None else 'FIXED_ZERO_H_ENTRY_VIOLATION',
            'n': n, 'rank': rank, 'q': q, 'factor': V, 'rho': rho,
            'padding_numerators': padding, 'padding_denominator': denominator,
            'alpha': alpha, 'alpha_witness': witness, 'upper_entries_checked': count,
            'zero_H_fixed_entry_violations': fixed_violations,
            'B1_exists': alpha is not None and alpha <= 1}

def exact_dual(table, W, q):
    rank = factor_guard(W, q, table.n)
    S, A, B, n = table.scale, table.A, table.B, table.n
    G = gram_entries(W)
    trace = 0
    support = 0
    for i in range(n):
        for j in range(i, n):
            multiplicity = 1 if i == j else 2
            trace += multiplicity*A[i][j]*G[i][j]
            support += multiplicity*B[i][j]*abs(G[i][j])
    nonzero = any(x != 0 for row in W for x in row)
    beta = R(-trace, support) if support else None
    if not nonzero:
        status = 'ZERO_FACTOR_NO_BOUND'
    elif support:
        status = 'FINITE_EXACT_LOWER'
    elif trace < 0:
        status = 'ZERO_SUPPORT_ALL_FINITE_RADII_EXCLUDED'
    else:
        status = 'ZERO_SUPPORT_NO_BOUND'
    return {'kind': 'GENERAL_RATIONAL_GRAM_PSD_DUAL', 'status': status,
            'n': n, 'rank': rank, 'q': q, 'factor': W,
            'trace_numerator': trace, 'support_numerator': support,
            'common_denominator': S*q*q, 'trace': R(trace, S*q*q),
            'support': R(support, S*q*q), 'beta': beta,
            'B1_signed_upper': R(trace+support, S*q*q),
            'B1_excluded': nonzero and trace+support < 0,
            'upper_entries_checked': n*(n+1)//2}

def combine(alpha, beta, inherited):
    alpha = rational(alpha)
    inherited = rational(inherited)
    beta = R(0) if beta is None else max(R(0), rational(beta))
    if beta > alpha or alpha <= inherited:
        raise CertificateContradiction('STOP_NO_ADMISSION_PRIMAL_DUAL_OR_INHERITED_CONTRADICTION')
    if beta > inherited:
        lower, strict = beta, False
    else:
        lower, strict = inherited, True
    exists, excluded = alpha <= 1, beta > 1
    if exists and excluded:
        raise CertificateContradiction('STOP_NO_ADMISSION_B1_CONTRADICTION')
    return {'lower': lower, 'lower_strict': strict, 'upper': alpha, 'upper_inclusive': True,
            'dual_beta': beta, 'inherited_pair_lower': inherited,
            'B1_status': 'EXISTS_BY_EXACT_PRIMAL' if exists else
                         'EXCLUDED_BY_EXACT_GENERAL_PSD_DUAL' if excluded else
                         'B1_UNRESOLVED_WITH_CERTIFIED_GLOBAL_DISTANCE_ENCLOSURE'}

def fixtures():
    result = {}
    def reject(name, callback):
        try:
            callback()
        except ValueError:
            result[name] = True
        else:
            raise AssertionError('FIXTURE_DID_NOT_REJECT:'+name)
    small = ExactTable([[1, 0], [0, 1]], [[1, 1], [1, 1]])
    primal = exact_primal(small, [[1, 1], [1, -1]], 2, 0)
    assert primal['alpha'] == 0 and primal['padding_numerators'] == [2, 2]
    result['exact small primal Gram plus diagonal'] = True
    boundary = exact_primal(ExactTable([[0]], [[1]]), [[1]], 1, 1)
    assert boundary['alpha'] == 1 and boundary['B1_exists']
    result['alpha=1 inclusive admission'] = True
    d1 = exact_dual(ExactTable([[-1]], [[1]]), [[1]], 1)
    d2 = exact_dual(ExactTable([[-2]], [[1]]), [[1]], 1)
    assert d1['beta'] == 1 and not d1['B1_excluded']
    assert d2['beta'] == 2 and d2['B1_excluded']
    result['beta=1 not exclusion'] = True
    result['beta>1 strict exclusion'] = True
    reject('negative diagonal padding rejected', lambda: padding_guard([-1], 1, 1))
    zero = exact_dual(small, [[], []], 1)
    assert zero['status'] == 'ZERO_FACTOR_NO_BOUND' and zero['beta'] is None
    result['zero factor dual no bound'] = True
    fixed = exact_primal(ExactTable([[1]], [[0]]), [[1]], 1, 1)
    wrong = exact_primal(ExactTable([[1]], [[0]]), [[2]], 1, 1)
    zsupport = exact_dual(ExactTable([[-1]], [[0]]), [[1]], 1)
    assert fixed['alpha'] == 0 and wrong['alpha'] is None
    assert zsupport['status'] == 'ZERO_SUPPORT_ALL_FINITE_RADII_EXCLUDED'
    result['zero H denominator special handling'] = True
    reject('negative H rejected', lambda: ExactTable([[1]], [[-1]]))
    reject('nonsymmetric F rejected', lambda: ExactTable([[1, 1], [0, 1]], [[1, 1], [1, 1]]))
    reject('nonsymmetric H rejected', lambda: ExactTable([[1, 0], [0, 1]], [[1, 1], [0, 1]]))
    reject('dimension mismatch rejected', lambda: ExactTable([[1, 0]], [[1]]))
    reject('nonfinite token rejected', lambda: rational('NaN'))
    from evidence import check_input_blob
    reject('source identity mismatch rejected', lambda: check_input_blob(b'altered', 7, '0'*64))
    reject('primal/dual contradiction STOP_NO_ADMISSION', lambda: combine(R(1), R(2), R(0)))
    # The all-rank-one assertion is supplied by the theory forest proof, not sampling.
    S = [[0, 1, 0, -1], [1, 0, 1, 0], [0, 1, 0, 1], [-1, 0, 1, 0]]
    F = [[R(int(i == j)+S[i][j]) for j in range(4)] for i in range(4)]
    H = [[R(1, 10) if i == j or abs(S[i][j]) == 1 else R(1) for j in range(4)] for i in range(4)]
    W = [[int(i == j)-S[i][j] for j in range(4)] for i in range(4)]
    fx = ExactTable(F, H)
    combined = exact_dual(fx, W, 1)
    separate = sum((exact_dual(fx, [[W[i][k]] for i in range(4)], 1)['support'] for k in range(4)), R(0))
    assert combined['trace'] == -4 and combined['support'] == R(14, 5)
    assert combined['beta'] == R(10, 7) and combined['B1_signed_upper'] == R(-6, 5)
    assert separate == R(54, 5) and separate > combined['support']
    assert all(sum(S[i][k]*S[k][j] for k in range(4)) == 2*int(i == j) for i in range(4) for j in range(4))
    result['exact general PSD dual support with combined-entry cancellation'] = True
    result['independent theory rank-one limitation fixture'] = {
        'trace': combined['trace'], 'support': combined['support'], 'beta': combined['beta'],
        'B1_signed_upper': combined['B1_signed_upper'], 'separate_factor_support': separate,
        'all_rank_one_failure_basis': 'THEORY_FOREST_PROOF_NOT_FINITE_SAMPLING',
    }
    L = [[1, 1], [1, -1], [-2, 0]]
    C = [[R(1), R(0)], [R(0), R(1)]]
    K = [[sum((R(x[i])*C[i][j]*R(y[j]) for i in range(2) for j in range(2)), R(0)) for y in L] for x in L]
    assert all(sum(row, R(0)) == 0 for row in K)
    assert all(sum(K[i][j] for i in range(3)) == 0 for j in range(3))
    result['same shared consumer map preserves q^T L=0'] = {'exact': True, 'physical_ACK': None}
    return result

def generate(table, inherited, algorithm, retain):
    """Only called in the one authorized primary, after metadata identity/fresh."""
    import time
    import numpy as np
    from scipy.linalg import eigh
    n = table.n
    q = 2**algorithm['dyadic_denominator_power']
    F = np.array([[float(x) for x in row] for row in table.F], dtype=float)
    H = np.array([[float(x) for x in row] for row in table.H], dtype=float)
    total_cap = algorithm['maximum_projections_total']
    stage_caps = algorithm['maximum_projections_each']
    radii = [rational(x) for x in algorithm['radii']]
    cpu_total = algorithm['soft_process_CPU_s_total_generation_and_checkpoint']
    cpu_stage = algorithm['soft_process_CPU_s_per_stage']
    projection_count = 0
    attempts = []
    stages = []
    best_primal = None
    best_dual = None
    decisive = False
    terminal = None

    def quantize(factor):
        if not np.isfinite(factor).all():
            raise ValueError('NONFINITE_FLOAT_FACTOR_PROPOSAL')
        rounded = np.rint(factor*float(q))
        if not np.isfinite(rounded).all():
            raise ValueError('NONFINITE_DYADIC_FACTOR_PROPOSAL')
        return [[int(value) for value in row] for row in rounded]

    def checkpoint(stage_index, iteration, rho, primal_proposal, dual_proposal, reason):
        nonlocal best_primal, best_dual, decisive
        index = len(attempts)+1
        if index > 18:
            raise ValueError('FROZEN_CHECKPOINT_CAP_EXCEEDED')
        V = quantize(primal_proposal['factor']) if primal_proposal is not None else [[] for _ in range(n)]
        primal = exact_primal(table, V, q, rho)
        W = quantize(dual_proposal['factor']) if dual_proposal is not None else [[] for _ in range(n)]
        dual = exact_dual(table, W, q)
        record = {
            'checkpoint': index, 'stage': stage_index, 'stage_iteration': iteration,
            'projections_total': projection_count, 'rho': rho, 'reason': reason,
            'process_CPU_s_before_retain': time.process_time(),
            'primal_float_score': None if primal_proposal is None else primal_proposal['score'],
            'dual_float_score': None if dual_proposal is None else dual_proposal['score'],
            'primal_origin_iteration': None if primal_proposal is None else primal_proposal['iteration'],
            'dual_origin_iteration': None if dual_proposal is None else dual_proposal['iteration'],
            'primal': primal, 'dual': dual,
        }
        # Raw factors and actual exact certificate are durable before early stop.
        receipt = retain(index, record)
        item = {'checkpoint': index, 'file': receipt['path'], 'sha256': receipt['sha256'],
                'stage': stage_index, 'stage_iteration': iteration, 'rho': rho,
                'projections_total': projection_count, 'alpha': primal['alpha'], 'beta': dual['beta'],
                'primal_rank': primal['rank'], 'dual_rank': dual['rank'],
                'process_CPU_s': time.process_time()}
        attempts.append(item)
        if primal['alpha'] is not None and (best_primal is None or primal['alpha'] < best_primal['certificate']['alpha']):
            best_primal = {'checkpoint': index, 'file': receipt['path'], 'certificate': primal}
        if dual['beta'] is not None and (best_dual is None or dual['beta'] > best_dual['certificate']['beta']):
            best_dual = {'checkpoint': index, 'file': receipt['path'], 'certificate': dual}
        if best_primal is not None:
            combine(best_primal['certificate']['alpha'],
                    None if best_dual is None else best_dual['certificate']['beta'], inherited)
        decisive = primal['B1_exists'] or dual['B1_excluded']

    for stage_index, (rho, cap) in enumerate(zip(radii, stage_caps), 1):
        if decisive or projection_count >= total_cap:
            break
        start = time.process_time()
        U_exact = [table.F[i][i]+rho*table.H[i][i] for i in range(n)]
        if any(x <= 0 for x in U_exact):
            raise ValueError('ACTUAL_CORRELATION_PROPOSAL_REQUIRES_POSITIVE_U')
        scale = np.sqrt(np.array([float(x) for x in U_exact]))
        if not np.isfinite(scale).all() or np.any(scale <= 0):
            raise ValueError('NONFINITE_OR_ZERO_FLOAT_CORRELATION_SCALE')
        outer = scale[:, None]*scale[None, :]
        lower = (F-float(rho)*H)/outer
        upper = (F+float(rho)*H)/outer
        X = F/outer
        np.fill_diagonal(X, 1.0)
        P = np.zeros_like(X)
        Q = np.zeros_like(X)
        primal_proposal = None
        dual_proposal = None
        last_checked = -1
        iteration = 0
        reason = 'STAGE_PROJECTION_CAP'
        for iteration in range(1, cap+1):
            if time.process_time() >= cpu_total or time.process_time()-start >= cpu_stage:
                iteration -= 1
                reason = 'SOFT_PROCESS_CPU_STOP'
                break
            if projection_count >= total_cap:
                iteration -= 1
                reason = 'TOTAL_PROJECTION_CAP'
                break
            Z = X+P
            Z = (Z+Z.T)*0.5
            # This is a correlation-scaled changed Dykstra candidate, never raw F.
            values, vectors = eigh(Z, overwrite_a=False, check_finite=True, driver='evd')
            projection_count += 1
            positive = values > 0
            negative = values < 0
            G = (vectors[:, positive]*np.sqrt(values[positive])[None, :])*scale[:, None]
            Y = (vectors[:, positive]*values[positive][None, :]) @ vectors[:, positive].T
            P = Z-Y
            # Physical primal factor requires forward correlation scaling.
            C = G @ G.T
            padding = np.maximum(np.array([float(x) for x in U_exact])-np.diag(C), 0)
            C[np.diag_indices(n)] += padding
            score = float(np.max(np.abs(C-F)/H))
            if np.isfinite(score) and (primal_proposal is None or score < primal_proposal['score']):
                primal_proposal = {'factor': G.copy(), 'score': score, 'iteration': iteration}
            # Physical dual factor requires inverse correlation scaling.
            W = (vectors[:, negative]*np.sqrt(-values[negative])[None, :])/scale[:, None]
            if W.shape[1]:
                largest = float(np.max(np.abs(W)))
                if largest > 0 and np.isfinite(largest):
                    W = W/largest
                    dual_matrix = W @ W.T
                    support = float(np.sum(H*np.abs(dual_matrix)))
                    trace = float(np.sum(F*dual_matrix))
                    dual_score = -trace/support if support > 0 else float('-inf')
                    if np.isfinite(dual_score) and (dual_proposal is None or dual_score > dual_proposal['score']):
                        dual_proposal = {'factor': W.copy(), 'score': dual_score, 'iteration': iteration}
            shifted = Y+Q
            X = np.minimum(np.maximum(shifted, lower), upper)
            X = (X+X.T)*0.5
            np.fill_diagonal(X, 1.0)
            Q = shifted-X
            if iteration % 256 == 0:
                checkpoint(stage_index, iteration, rho, primal_proposal, dual_proposal, 'FROZEN_256_CHECKPOINT')
                last_checked = iteration
                primal_proposal = None
                dual_proposal = None
                if decisive:
                    reason = 'EXACT_B1_CERTIFICATE_EARLY_STOP'
                    break
        if not decisive and last_checked != iteration:
            checkpoint(stage_index, iteration, rho, primal_proposal, dual_proposal, reason)
        stages.append({'stage': stage_index, 'rho': rho, 'iterations': iteration,
                       'process_CPU_s': time.process_time()-start, 'termination': reason})
        if decisive:
            terminal = 'EXACT_B1_CERTIFICATE_EARLY_STOP'
            break
        if time.process_time() >= cpu_total:
            terminal = 'SOFT_PROCESS_CPU_TOTAL_STOP'
            break
    if best_primal is None:
        raise ValueError('NO_RETAINED_EXACT_PRIMAL_CERTIFICATE')
    alpha = best_primal['certificate']['alpha']
    beta = None if best_dual is None else best_dual['certificate']['beta']
    enclosure = combine(alpha, beta, inherited)
    return {'enclosure': enclosure, 'selected_primal': best_primal,
            'selected_dual': best_dual, 'attempts': attempts, 'stages': stages,
            'changed_candidate_eigh_calls': projection_count, 'raw_F_eigh_calls': 0,
            'old_pair_rescans': 0, 'q': q, 'checkpoints': len(attempts),
            'termination': terminal or 'FROZEN_FINITE_PROJECTION_CAPS',
            'process_CPU_s_after_generation_and_checks': time.process_time(),
            'quantization': 'NUMPY_RINT_NEAREST_DYADIC_TIES_TO_EVEN; EXACT_ACCEPTANCE_ONLY'}

