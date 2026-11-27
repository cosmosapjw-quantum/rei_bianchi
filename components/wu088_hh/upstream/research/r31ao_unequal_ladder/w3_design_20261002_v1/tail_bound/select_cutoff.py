"""Fixed-input positive endpoint budget split; no HH callback or interior run.

CLI execution requires explicit --execute-pinned-endpoint. The caller supplies
hard process wall/address-space isolation; this module also checks cooperative
limits. Existing source/plan/result/input bytes are immutable dependencies.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
LADDER = HERE.parents[1]
PRIOR = LADDER / 'production_solver_20261001_v1'
PLANNER = PRIOR / 'endpoint_tasks/planner.py'
SOURCE_PINS = {
    'endpoint_tasks/planner.py': '53fe8cea32fb24efe9ef2682f480d63595db2bf32525ed57f46df391fe3eb4e6',
    'runtime/endpoint_cutoff_probe_capped/W3_PLAN.json': '86da77a3aff825e8ac1c049f414d88f75f05a952ccc1deef217e0e0966a571a2',
    'runtime/endpoint_cutoff_probe_capped/W3_RESULT.json': 'f1f1d7ad7ee668bd3dd4d63903b65fe349550e512108f6f6db0e4bc6a773593e',
    'inputs/FROZEN_INPUTS.npz': '8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c',
}
CANDIDATE_EXPONENTS = (32, 40, 48, 56, 64)
BITS = 128
TARGET = Q(1, 1 << 21)
LOWER = Q(1, 512)
BASELINE_LOWER = Q(1, 256)
MAX_ENGINE_CALLS = 128
MAX_WALL_SECONDS = 60
MAX_BITS = 16384
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
SCHEMA = 'WU088_SEPARATED_ENDPOINT_CUTOFF_V1'


class CutoffError(ValueError): pass
class LimitReached(RuntimeError): pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(value): return hashlib.sha256(encoded(value)).hexdigest()


def exact_nonnegative(value):
    if type(value) not in (int, Q) or value < 0:
        raise CutoffError('nonnegative exact int/Fraction required')
    value = Q(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise LimitReached('rational bit cap')
    return value


def up(value):
    """Exact relative-grid upward rounding identical to pinned planner policy."""
    q = exact_nonnegative(value)
    if not q: return q
    n, d = q.numerator, q.denominator
    exponent = n.bit_length() - d.bit_length()
    below_power = n < (d << exponent) if exponent >= 0 else (n << -exponent) < d
    if below_power:
        exponent -= 1
    step = exponent - BITS + 1
    if step >= 0:
        denominator = d << step
        return exact_nonnegative(Q(((n + denominator - 1) // denominator) << step))
    numerator = n << -step
    return exact_nonnegative(Q((numerator + d - 1) // d, 1 << -step))


def aggregate(rows):
    """Rows contain proved positive factors; no physical validity inferred here.

    Each row: |c|, C_F, L_t, W_t, L_u, W_u, U_t/U_u power maps.
    Returns outward lower-complement sum, upper polynomial, per-term evidence.
    """
    lower = Q(0); coefficients = {}; evidence = []
    for row in rows:
        factor = up(exact_nonnegative(row['c_abs']) * exact_nonnegative(row['C_F']))
        lt, wt, lu, wu = (exact_nonnegative(row[k]) for k in ('L_t', 'W_t', 'L_u', 'W_u'))
        upper_t, upper_u = row['U_t'], row['U_u']
        for mapping in (upper_t, upper_u):
            if type(mapping) is not dict or any(type(p) is not int or not 2 <= p <= 10 for p in mapping):
                raise CutoffError('upper polynomial degrees must lie in 2..10')
            for value in mapping.values(): exact_nonnegative(value)
        lower_term = up(factor * up(lt * wu + wt * lu))
        lower = up(lower + lower_term)
        contributions = {}
        for power in sorted(set(upper_t) | set(upper_u)):
            value = up(factor * up(upper_t.get(power, Q(0)) * wu + wt * upper_u.get(power, Q(0))))
            coefficients[power] = up(coefficients.get(power, Q(0)) + value)
            contributions[power] = value
        evidence.append({'lower_contribution': lower_term, 'upper_coefficients': contributions})
    return lower, coefficients, evidence


def evaluate_polynomial(coefficients, exponent):
    if type(exponent) is not int or exponent not in CANDIDATE_EXPONENTS:
        raise CutoffError('candidate outside fixed finite exponent set')
    total = Q(0)
    for power in sorted(coefficients):
        if type(power) is not int or not 2 <= power <= 10:
            raise CutoffError('polynomial degree outside source range')
        coefficient = exact_nonnegative(coefficients[power])
        total = up(total + up(coefficient / (1 << (exponent * power))))
    return total


def choose(lower, coefficients, target=TARGET):
    lower, target = exact_nonnegative(lower), exact_nonnegative(target)
    if not target: raise CutoffError('positive target required')
    records = []
    selected = None
    for exponent in CANDIDATE_EXPONENTS:
        upper = evaluate_polynomial(coefficients, exponent)
        combined = up(lower + upper)
        passed = combined <= target
        records.append({'upper_exponent': exponent, 'T': str(1 << exponent),
                        'upper_radius': str(upper), 'combined_radius': str(combined),
                        'meets_endpoint_budget': passed})
        if passed and selected is None: selected = exponent
    status = ('LOWER_BUDGET_EXCEEDED' if lower > target else
              'FIRST_TESTED_CUTOFF_SELECTED' if selected is not None else 'NO_TESTED_CUTOFF_MEETS_BUDGET')
    return {'status': status, 'selected_upper_exponent': selected,
            'selection_is_global_optimum': False, 'candidates': records}


def _load_planner():
    identities = {}
    for relative, expected in SOURCE_PINS.items():
        path = PRIOR / relative; data = path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected: raise CutoffError('source byte identity mismatch: ' + relative)
        identities[relative] = {'sha256': actual, 'bytes': len(data)}
    spec = importlib.util.spec_from_file_location('_wu088_separated_endpoint_planner', PLANNER)
    planner = importlib.util.module_from_spec(spec); sys.modules[spec.name] = planner
    previous = sys.dont_write_bytecode; sys.dont_write_bytecode = True
    try: spec.loader.exec_module(planner)
    finally: sys.dont_write_bytecode = previous
    return planner, identities


def evaluate_pinned(*, execute_pinned=False, lower_cutoff=LOWER):
    if execute_pinned is not True:
        raise CutoffError('explicit pinned endpoint execution required')
    lower_cutoff = exact_nonnegative(lower_cutoff)
    if lower_cutoff != LOWER:
        raise CutoffError('this bounded campaign fixes the lower cutoff at 1/512')
    started = time.monotonic_ns()
    p, identities = _load_planner()
    archive = (PRIOR / 'inputs/FROZEN_INPUTS.npz').read_bytes()
    plan = p.read_json(PRIOR / 'runtime/endpoint_cutoff_probe_capped/W3_PLAN.json')
    prior_result = p.read_json(PRIOR / 'runtime/endpoint_cutoff_probe_capped/W3_RESULT.json')
    p.validate_plan(plan, source_archive_bytes=archive); p.validate_result(plan, prior_result)
    if plan['precision_bits'] != BITS or prior_result['index'] != 0 or prior_result['status'] != 'CONDITIONAL_TAIL_BOUND':
        raise CutoffError('fixed 128-bit primitive-0 baseline required')
    if plan['window'] != {'l_t': str(BASELINE_LOWER), 'l_u': str(BASELINE_LOWER), 'T_t': str(1 << 192), 'T_u': str(1 << 192)}:
        raise CutoffError('fixed W3 baseline window required')
    task = plan['tasks'][0]
    if task['indices'] != {'active': 0, 'field': 0, 'orbital': 0, 'ia': 0, 'ib': 0}:
        raise CutoffError('fixed canonical primitive zero required')
    par = task['parameters']; a, b, mu = (Q(par[k]) for k in ('a', 'b', 'mu'))
    d1, d2 = (tuple(map(Q, par[k])) for k in ('d1', 'd2'))
    calls = 0; majorants = {}; masses = {}; upper_maps = {}; rows = []; term_evidence = []
    def check():
        if time.monotonic_ns() - started > MAX_WALL_SECONDS * 10**9:
            raise LimitReached('cooperative wall cap')
    def dispatch(fn, *args):
        nonlocal calls
        check()
        if calls >= MAX_ENGINE_CALLS: raise LimitReached('engine call cap')
        calls += 1
        value = fn(*args); check()
        return value
    def mass(i, exponent):
        key = (i, exponent)
        if key not in masses:
            lower = up(dispatch(p.engine.lower_mass_bound, i, mu, exponent, lower_cutoff, BITS))
            whole_lower = dispatch(p.engine.lower_mass_bound, i, mu, exponent, Q(1), BITS)
            whole_upper = dispatch(p.engine.upper_mass_bound, i, mu, Q(1), BITS)
            whole = up(whole_lower + whole_upper)
            masses[key] = {'L': lower, 'W': whole}
        return masses[key]
    def upper_map(i):
        if i not in upper_maps:
            mapping = {}
            for r in range((i + 1) // 2 + 1):
                power = i + 2 - r
                h = dispatch(p.engine.hermite_coefficient, i, r, mu, BITS).hi
                mapping[power] = up(h / power)
            upper_maps[i] = mapping
        return upper_maps[i]
    for term, old in zip(plan['terms'], prior_result['terms']):
        check(); i, j, k = (term[key] for key in ('i', 'j', 'k'))
        if k not in majorants:
            majorants[k] = up(dispatch(p.engine.gaussian_field_majorant, a, b, d1, d2, k, 's', 'O', BITS))
        if majorants[k] != Q(old['field_majorant']):
            raise CutoffError('recomputed field majorant differs from pinned W3 record')
        mt, mu_mass = mass(i, a), mass(j, b)
        row = {'c_abs': abs(Q(term['coefficient'])), 'C_F': majorants[k],
               'L_t': mt['L'], 'W_t': mt['W'], 'L_u': mu_mass['L'], 'W_u': mu_mass['W'],
               'U_t': upper_map(i), 'U_u': upper_map(j)}
        rows.append(row)
        term_evidence.append({'i': i, 'j': j, 'k': k, 'coefficient': term['coefficient'],
                              **{key: str(value) for key, value in row.items() if key not in ('U_t', 'U_u')},
                              'U_t': {str(k): str(v) for k, v in row['U_t'].items()},
                              'U_u': {str(k): str(v) for k, v in row['U_u'].items()}})
    lower, coefficients, per_term = aggregate(rows)
    for row, contribution in zip(term_evidence, per_term):
        row['lower_contribution'] = str(contribution['lower_contribution'])
        row['upper_coefficients'] = {str(k): str(v) for k, v in contribution['upper_coefficients'].items()}
    choice = choose(lower, coefficients)
    check()
    source_data = Path(__file__).read_bytes()
    result = {
        'schema': SCHEMA, 'component': 'UNNORMALIZED_POSITIVE_DOMAIN_ENDPOINT_ONLY',
        'scope': 'FROZEN107_PINNED_PRIMITIVE_0_ONLY', 'primitive_index': 0,
        'source_identities': identities, 'source_hashes': p.source_hashes(),
        'selector_source_sha256': hashlib.sha256(source_data).hexdigest(),
        'archive_sha256': plan['archive_sha256'], 'input_record_sha256': plan['input_record_sha256'],
        'baseline_plan_sha256': plan['plan_sha256'], 'baseline_task_sha256': task['task_sha256'],
        'baseline_result_sha256': prior_result['result_sha256'],
        'baseline_endpoint_radius': prior_result['endpoint_radius'],
        'budget_strictly_less_than_baseline_bound': TARGET < Q(prior_result['endpoint_radius']),
        'parameters': par, 'lower_cutoffs': {'l_t': str(lower_cutoff), 'l_u': str(lower_cutoff)},
        'endpoint_budget': str(TARGET), 'endpoint_budget_origin': 'STRICTER_THAN_EXISTING_W3_EXACT_BOUND_2^-21_NOT_FINAL_D_GOAL',
        'precision_bits': BITS, 'rounding': '128_BIT_RELATIVE_DYADIC_UPPER_AT_EACH_POSITIVE_STAGE',
        'proof_formula': 'B_lower+sum_p(A_p*T^-p); B_lower=sum|c|CF(L_t*W_u+W_t*L_u)',
        'disjoint_complement': '(outside_t x all_u) disjoint_union (inside_t x outside_u)',
        'inside_mass_replacement': 'inside_t_mass <= W_t; preserves disjoint original integration regions',
        'lower_radius': str(lower), 'upper_coefficients': {str(k): str(v) for k, v in coefficients.items()},
        'terms': term_evidence, 'term_count': len(rows), 'field_majorants_match_prior_W3': True,
        **choice, 'engine_calls': calls, 'max_engine_calls': MAX_ENGINE_CALLS,
        'elapsed_ns': time.monotonic_ns() - started, 'max_wall_seconds': MAX_WALL_SECONDS,
        'hh_callback_evaluations': 0, 'native_integrations': 0, 'archived_B192_recomputations': 0,
        'normalization_applied': False, 'full_D_epsilon': None, 'scientific_admission': False,
        'interior_integrated_for_selected_window': False,
        'evidence_contract': 'SOURCE_BOUND_ENGINE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'validation_level': 'SOURCE_IDENTITY_EXACT_OUTWARD_ARITHMETIC_COMPONENT_ONLY',
    }
    result['result_sha256'] = digest(result)
    if len(encoded(result)) > MAX_OUTPUT_BYTES: raise LimitReached('output byte cap')
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--execute-pinned-endpoint', action='store_true')
    cli.add_argument('--output', required=True)
    args = cli.parse_args()
    output = Path(args.output)
    if output.exists(): raise CutoffError('create-only output already exists')
    result = evaluate_pinned(execute_pinned=args.execute_pinned_endpoint)
    with output.open('xb') as file: file.write(encoded(result) + b'\n')
    print(json.dumps({key: result[key] for key in ('status', 'selected_upper_exponent', 'term_count', 'engine_calls', 'elapsed_ns', 'result_sha256')}))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except (CutoffError, LimitReached, ValueError, OSError) as exc:
        print(json.dumps({'status': 'ENDPOINT_SELECTION_REFUSED', 'reason': str(exc), 'scientific_admission': False}), file=sys.stderr)
        raise SystemExit(2)
