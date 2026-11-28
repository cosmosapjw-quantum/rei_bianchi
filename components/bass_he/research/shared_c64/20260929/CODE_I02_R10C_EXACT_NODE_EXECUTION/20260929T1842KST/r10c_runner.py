"""R10C research-only exact consumed-node audit and fixed-GK replay."""
from __future__ import annotations

import math
import numpy as np
from bass_he.geometry import _gk15_nodes, adaptive_vector_quadrature

def validate_query_rows(contract, branches, cutoffs):
    rows = contract['query_rows']
    nodes = [float(x) for a, b in zip(cutoffs[:-1], cutoffs[1:])
             for x in np.sqrt(_gk15_nodes(a*a, b*b))]
    expected = {(b.name, rho.hex()) for b in branches for rho in nodes
                if rho <= b.support_cutoff}
    actual = [(row['branch'], row['rho_hex']) for row in rows]
    if (len(nodes) != 105 or len(set(x.hex() for x in nodes)) != 105
            or len(rows) != 360 or len(set(actual)) != 360
            or set(actual) != expected
            or any(float(row['rho']).hex() != row['rho_hex'] for row in rows)
            or contract['coordinate_count'] != 105
            or contract['active_pair_count'] != 360):
        raise ValueError('QUERY_IDENTITY_MISMATCH')
    return 105, 360

def contour_key(branch, rho, source, environment, *, depth=96, panels=32):
    rho = float(rho)
    return {'source': source, 'environment': tuple(environment),
            'kind': 'R10A_CONTOUR', 'branch': branch.name,
            'state_a': branch.state_a, 'state_b': branch.state_b,
            'R': (branch.R.real.hex(), branch.R.imag.hex()),
            'rho_hex': rho.hex(), 'depth': depth, 'panels': panels}

def validate_exact_table(query_rows, records):
    expected = [(r['branch'], r['rho_hex']) for r in query_rows]
    actual = [(r['branch'], r['rho_hex']) for r in records]
    if (len(actual) != len(expected) or len(set(actual)) != len(actual)
            or set(actual) != set(expected)
            or any(float(r['rho']).hex() != r['rho_hex'] or
                   not math.isfinite(float(r['delta'])) or float(r['delta']) < 0
                   for r in records)):
        raise ValueError('EXACT_TABLE_INCOMPLETE_OR_INVALID')
    return len(records)

def fixed_node_integrate(evaluate, cutoffs, expected_hex, *, rtol=2e-4, atol=1e-10):
    expected_hex = set(expected_hex)
    seen = []
    def checked(rhos):
        found = [float(x).hex() for x in rhos]
        if len(found) != 105 or len(set(found)) != 105 or set(found) != expected_hex:
            raise ValueError('QUERY_IDENTITY_MISMATCH: fixed GK15 nodes')
        seen.append(found)
        if len(seen) != 1:
            raise ValueError('QUERY_IDENTITY_MISMATCH: unexpected refinement')
        return evaluate(rhos)
    result = adaptive_vector_quadrature(checked, cutoffs, rtol=rtol, atol=atol,
                                        max_intervals=len(cutoffs)-1, rule='gk15')
    if result['evaluations'] != 105 or result['refinements'] != 0 or len(seen) != 1:
        raise ValueError('QUERY_IDENTITY_MISMATCH: quadrature node count')
    return result

def frozen_geometry_map(branches, rhos, deltas0):
    out = {}
    for b in branches:
        delta = float(deltas0[b.name])
        if not math.isfinite(delta) or delta < 0:
            raise ValueError('invalid rho=0 Delta')
        for rho in rhos:
            rho = float(rho)
            if rho <= b.support_cutoff:
                out[(b.name, rho)] = {'delta': delta,
                                       'source': 'R10C_EXACT_RHO0_FROZEN_RESEARCH_ONLY'}
    return out

def probability_ratio(delta0, delta_rho, velocity, factor=2):
    if (factor not in (1, 2) or not all(math.isfinite(float(x)) for x in
                                       (delta0, delta_rho, velocity)) or velocity <= 0):
        raise ValueError('finite Delta and positive velocity required')
    return math.exp(-factor*(delta0-delta_rho)/velocity)

# Execution remains in this research namespace. The imported numerical functions
# are source-pinned to the unchanged R10A implementation.
def run_phase_a(repo, r10a, r10b, archive, out, *, max_new=360):
    import hashlib
    import importlib.util
    import json
    import platform
    import time
    import traceback
    from pathlib import Path
    from bass_he.eq54 import BRANCHES, DeltaSurrogate, support_cutoffs
    from bass_he.geometry import EvidenceCache, atomic_json, contour_geometry, _canonical, unjsonable
    from scripts.r10a_rho_freeze import _source_identity

    repo, r10a, r10b, archive, out = map(Path, (repo, r10a, r10b, archive, out))
    out.mkdir(parents=True, exist_ok=True)
    source, deps = _source_identity(repo)
    if source != '496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba':
        raise ValueError('R10C_IDENTITY_MISMATCH: numerical source')
    import numpy as np
    env = (np.__version__, platform.python_version())
    if env != ('2.3.5', '3.12.3'):
        raise ValueError('R10C_IDENTITY_MISMATCH: numerical environment')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != '2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75':
        raise ValueError('R10C_IDENTITY_MISMATCH: original archive')
    query_path = r10b/'PROPOSED_QUERY_CONTRACT.json'
    if hashlib.sha256(query_path.read_bytes()).hexdigest() != '97ee706c2765cac40cb001592fe5c543053ed5457b3ee4776e282a742238f215':
        raise ValueError('R10C_IDENTITY_MISMATCH: query contract bytes')
    if (r10b/'node_view.py').read_bytes() != (repo/'research/shared_c64/20260929/CODE_I02_R10B_NODE_IDENTITY/node_view.py').read_bytes():
        raise ValueError('R10C_IDENTITY_MISMATCH: reviewed node view')
    contract = json.loads((r10a/'RUN_CONTRACT.json').read_text())
    if (contract['source_sha256'] != source or contract['numpy'] != env[0]
            or contract['python'] != env[1] or contract['depth'] != 96
            or contract['panels'] != 32 or contract['dependencies'] != list(deps)):
        raise ValueError('R10C_IDENTITY_MISMATCH: R10A run contract')
    query = json.loads(query_path.read_text())
    cuts = support_cutoffs(rotation_cut_scale=1.0)
    validate_query_rows(query, BRANCHES, cuts)
    rows = query['query_rows']
    branches = {b.name: b for b in BRANCHES}
    old_cache = EvidenceCache(r10a/'cache')
    new_cache = EvidenceCache(out/'cache')
    endpoints = {}
    for b in BRANCHES:
        epkey = {'source': source, 'environment': env, 'kind': 'R10A_EP',
                 'branch': b.name, 'state_a': b.state_a, 'state_b': b.state_b,
                 'R': (b.R.real.hex(), b.R.imag.hex()), 'depth': 96}
        ep = old_cache.get(epkey)
        saved = unjsonable(json.loads((r10a/f'EP_{b.name}.json').read_text())['ep'])
        if (ep is None or _canonical(ep) != _canonical(saved)
                or ep['certificate']['simple_fold'] is not True
                or ep['pair_membership']['passed'] is not True
                or ep['depth'] != 96 or tuple(ep['state_a']) != b.state_a
                or tuple(ep['state_b']) != b.state_b):
            raise RuntimeError('R10C_ENDPOINT_AUTHORITY_BLOCKED: '+b.name)
        endpoints[b.name] = ep
    atomic_json(out/'PRECHECK.json', {'source_sha256': source, 'dependencies': deps,
                                     'environment': env, 'query_sha256': hashlib.sha256(query_path.read_bytes()).hexdigest(),
                                     'r10a_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                                     'endpoint_authority': {b: 'ARCHIVED_KEY_AND_PAYLOAD_HASH_VERIFIED' for b in endpoints},
                                     'query_coordinates': 105, 'active_pairs': 360,
                                     'depth': 96, 'panels': 32, 'support_cutoffs': cuts})
    output_rows = []
    counts = {'original_r10a_cache_reuse': 0, 'prior_local_cache_reuse': 0, 'new_contour_calls': 0}
    for i, q in enumerate(rows):
        b = branches[q['branch']]
        rho = float(q['rho'])
        if rho.hex() != q['rho_hex']:
            raise ValueError('R10C_IDENTITY_MISMATCH: rho hex')
        key = contour_key(b, rho, source, env)
        rec = old_cache.get(key)
        if rec is not None:
            origin = 'ORIGINAL_R10A_CACHE_EXACT_IDENTITY'
            counts['original_r10a_cache_reuse'] += 1
        else:
            rec = new_cache.get(key)
            if rec is not None:
                origin = 'R10C_LOCAL_CACHE_EXACT_IDENTITY'
                counts['prior_local_cache_reuse'] += 1
            else:
                if counts['new_contour_calls'] >= max_new:
                    atomic_json(out/'PROGRESS.json', {'status': 'PILOT_PAUSED', 'completed': i,
                                                     'total': len(rows), 'counts': counts})
                    return {'status': 'PILOT_PAUSED', 'completed': i, 'counts': counts}
                try:
                    start = time.perf_counter()
                    rec = contour_geometry(endpoints[b.name], rho, panels=32)
                    rec['elapsed_s'] = time.perf_counter()-start
                    if (not math.isfinite(float(rec['delta'])) or rec['delta'] < 0
                            or rec['rho'] != rho or rec['panels'] != 32):
                        raise ValueError('invalid exact Delta record')
                    new_cache.put(key, rec)
                except Exception:
                    atomic_json(out/f'FAIL_{i:03d}_{b.name}.json', {'index': i, 'branch': b.name,
                                 'rho_hex': rho.hex(), 'traceback': traceback.format_exc()})
                    raise
                origin = 'R10C_NEW_32_PANEL_CONTOUR'
                counts['new_contour_calls'] += 1
        delta = float(rec['delta'])
        if not math.isfinite(delta) or delta < 0 or float(rec['rho']).hex() != rho.hex() or rec['panels'] != 32:
            raise ValueError('EXACT_TABLE_INCOMPLETE_OR_INVALID: cached record')
        row = {'index': i, 'branch': b.name, 'rho': rho, 'rho_hex': rho.hex(),
               'delta': delta, 'delta_hex': delta.hex(), 'depth': 96, 'panels': 32,
               'source_sha256': source, 'environment': env,
               'cache_key_sha256': hashlib.sha256(_canonical(key)).hexdigest(),
               'origin': origin, 'elapsed_s': rec.get('elapsed_s'),
               'max_spectral_residual': rec['max_spectral_residual'],
               'minimum_normalized_sheet_gap': rec['minimum_normalized_sheet_gap'],
               'accepted_continuation_steps': rec['accepted_continuation_steps'],
               'bisected_continuation_steps': rec['bisected_continuation_steps']}
        atomic_json(out/'rows'/f'{i:03d}.json', row)
        output_rows.append(row)
        atomic_json(out/'PROGRESS.json', {'status': 'PHASE_A_IN_PROGRESS', 'completed': i+1,
                                         'total': len(rows), 'counts': counts})
        if counts['new_contour_calls'] and counts['new_contour_calls'] % 10 == 0:
            print('new contour calls', counts['new_contour_calls'], 'completed', i+1, flush=True)
    validate_exact_table(rows, output_rows)
    atomic_json(out/'EXACT_NODE_TABLE.json', {'schema': 'bass_he.r10c.exact_node_table.v1',
                                             'status': 'COMPLETE_VALID_EXACT_NODE_TABLE',
                                             'source_sha256': source,
                                             'query_sha256': hashlib.sha256(query_path.read_bytes()).hexdigest(),
                                             'counts': counts, 'rows': output_rows})
    atomic_json(out/'PROGRESS.json', {'status': 'PHASE_A_COMPLETE', 'completed': len(rows),
                                     'total': len(rows), 'counts': counts})
    return {'status': 'PHASE_A_COMPLETE', 'completed': len(rows), 'counts': counts}


def audit_surrogate(repo, r10a, r10b, out):
    """Classify the repaired view at every *stored* exact consumed node."""
    import hashlib
    import importlib.util
    import json
    from pathlib import Path
    from bass_he.eq54 import DeltaSurrogate
    from bass_he.geometry import atomic_json
    from arseny_reimpl.cross_section import projectile_velocity_au

    repo, r10a, r10b, out = map(Path, (repo, r10a, r10b, out))
    table_path = out/'EXACT_NODE_TABLE.json'
    table = json.loads(table_path.read_text())
    if table['status'] != 'COMPLETE_VALID_EXACT_NODE_TABLE':
        raise ValueError('EXACT_TABLE_INCOMPLETE_OR_INVALID')
    query_path = r10b/'PROPOSED_QUERY_CONTRACT.json'
    if table['query_sha256'] != hashlib.sha256(query_path.read_bytes()).hexdigest():
        raise ValueError('QUERY_IDENTITY_MISMATCH')
    query = json.loads(query_path.read_text())
    validate_exact_table(query['query_rows'], table['rows'])
    node_path = r10b/'node_view.py'
    if node_path.read_bytes() != (repo/'research/shared_c64/20260929/CODE_I02_R10B_NODE_IDENTITY/node_view.py').read_bytes():
        raise ValueError('R10C_IDENTITY_MISMATCH: node view')
    spec = importlib.util.spec_from_file_location('r10b_pinned_node_view', node_path)
    node_view = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(node_view)
    raw = json.loads((r10a/'SURROGATE_MANIFEST.json').read_text())
    view, receipt = node_view.make_view(raw)
    surrogate = DeltaSurrogate({name: [(r['rho'], r['delta']) for r in rows]
                                for name, rows in view.items()})
    records = []
    max_rel = 0.0
    fails = 0
    probability_diagnostics = []
    by_node = {}
    for q in table['rows']:
        branch, rho, exact = q['branch'], float(q['rho']), float(q['delta'])
        prediction = float(surrogate.evaluate(branch, [rho])[0])
        absolute = abs(prediction-exact)
        relative = absolute/max(abs(exact), np.finfo(float).tiny)
        a = view[branch]
        u = np.array([r['rho'] for r in a], float)**2
        y = np.array([r['delta'] for r in a], float)
        i = int(np.searchsorted(u, rho*rho))
        lo = max(0, min(i-2, len(u)-4))
        ids = np.arange(lo, lo+4)
        xx = u[ids]
        center, scale = float(xx.mean()), float(np.ptp(xx))
        z = (xx-center)/scale
        _, diag = np.polynomial.polynomial.polyfit(z, y[ids], 3, full=True)
        rank = int(diag[1]); condition = float(np.linalg.cond(np.polynomial.polynomial.polyvander(z, 3)))
        passed = bool(relative <= 2e-4 and rank == 4 and math.isfinite(condition))
        records.append({'index': q['index'], 'branch': branch, 'rho_hex': q['rho_hex'],
                        'exact_delta': exact, 'exact_delta_hex': exact.hex(),
                        'surrogate_delta': prediction, 'surrogate_delta_hex': prediction.hex(),
                        'absolute_error': absolute, 'relative_error': relative,
                        'stencil_indices': ids.tolist(), 'stencil_rank': rank,
                        'stencil_condition_2': condition, 'pass': passed})
        if not passed: fails += 1
        max_rel = max(max_rel, relative)
        for energy in (0.5, 5.0):
            v = projectile_velocity_au(energy)
            for factor in (1, 2):
                p_exact = math.exp(-factor*exact/v)
                p_surrogate = math.exp(-factor*prediction/v)
                dp = abs(p_surrogate-p_exact)
                record = {'index': q['index'], 'branch': branch, 'rho_hex': q['rho_hex'],
                          'energy_keV_u': energy, 'exponent_factor': factor,
                          'p_exact': p_exact, 'p_surrogate': p_surrogate,
                          'abs_delta_p': dp, 'event_matrix_induced_1norm': 2*dp}
                probability_diagnostics.append(record)
                node_key = (q['rho_hex'], energy, factor)
                by_node[node_key] = by_node.get(node_key, 0.0) + dp
    status = 'SURROGATE_CONSUMED_QUERY_PASS' if fails == 0 else 'SURROGATE_CONSUMED_QUERY_FAIL'
    atomic_json(out/'SURROGATE_CONSUMED_QUERY_AUDIT.json',
                {'status': status, 'count': len(records), 'failed': fails,
                 'max_relative_error': max_rel, 'threshold': 2e-4,
                 'first_failure': next((x for x in records if not x['pass']), None),
                 'view_receipt': receipt, 'rows': records,
                 'claim_limit': 'FIXED_CONSUMED_QUERY_SET_ONLY_NOT_GLOBAL_INTERPOLATION_BOUND'})
    atomic_json(out/'SURROGATE_MODEL_DISCREPANCY.json',
                {'status': 'DIAGNOSTIC_ONLY_NOT_COMBINED_WITH_GK_ESTIMATOR',
                 'event_records': probability_diagnostics,
                 'nodewise_bounds': [{'rho_hex': k[0], 'energy_keV_u': k[1],
                                      'exponent_factor': k[2], 'state_l1_bound': 4*v}
                                     for k, v in sorted(by_node.items())],
                 'bound_formula': '||delta y||_1 <= 4 sum_active_events |delta p_e|',
                 'event_matrix_formula': '||delta T_e||_1 = 2 |delta p_e|'})
    return {'status': status, 'count': len(records), 'failed': fails,
            'max_relative_error': max_rel}


def run_phase_b(repo, r10a, r10b, out):
    """Use the complete exact table at the existing seven support splits, once."""
    import json
    import platform
    from pathlib import Path
    from bass_he.eq54 import BRANCHES, assemble_initial_column_batch, support_cutoffs
    from bass_he.geometry import EvidenceCache, _gk15_reduce, atomic_json, AdaptiveQuadratureError
    from scripts.r10a_rho_freeze import _source_identity, _shell_summary
    repo, r10a, r10b, out = map(Path, (repo, r10a, r10b, out))
    source, _ = _source_identity(repo)
    table = json.loads((out/'EXACT_NODE_TABLE.json').read_text())
    query = json.loads((r10b/'PROPOSED_QUERY_CONTRACT.json').read_text())
    validate_exact_table(query['query_rows'], table['rows'])
    if source != table['source_sha256'] or table['status'] != 'COMPLETE_VALID_EXACT_NODE_TABLE':
        raise ValueError('R10C_IDENTITY_MISMATCH: Phase A table')
    rhos = sorted({float(row['rho']) for row in query['query_rows']})
    expected_hex = set(row['rho_hex'] for row in query['query_rows'])
    exact = {(row['branch'], float(row['rho'])): {'delta': row['delta'], 'source': 'R10C_EXACT_32_PANEL'}
             for row in table['rows']}
    old_cache = EvidenceCache(r10a/'cache')
    delta0 = {}
    for b in BRANCHES:
        key = contour_key(b, 0.0, source, (np.__version__, platform.python_version()))
        rec = old_cache.get(key)
        if rec is None or not math.isfinite(float(rec['delta'])) or rec['delta'] < 0:
            raise RuntimeError('R10C_ENDPOINT_AUTHORITY_BLOCKED: exact rho=0 '+b.name)
        delta0[b.name] = float(rec['delta'])
    captured = {}
    def evaluate(nodes):
        node_hex = [float(x).hex() for x in nodes]
        if len(node_hex) != 105 or set(node_hex) != expected_hex:
            raise ValueError('QUERY_IDENTITY_MISMATCH: transport nodes')
        dynamic = assemble_initial_column_batch(exact, (0.5, 5.0), nodes,
                                                 exponent_factors=(2, 1), rotation_steps=32)
        frozen = assemble_initial_column_batch(frozen_geometry_map(BRANCHES, nodes, delta0),
                                                (0.5, 5.0), nodes,
                                                exponent_factors=(2,), rotation_steps=32)
        lanes = {'F2-RHO': dynamic['probabilities'][:, 0],
                 'F2-FROZEN': frozen['probabilities'][:, 0],
                 'F1-RHO': dynamic['probabilities'][:, 1]}
        keep = np.arange(lanes['F2-RHO'].shape[-1]) != 2
        values = np.concatenate([p[..., keep].reshape(len(nodes), -1) for p in lanes.values()], axis=1)
        captured['nodes'] = node_hex
        captured['values'] = values
        captured['max_column_sum_defect'] = max(float(np.max(abs(p.sum(-1)-1.))) for p in lanes.values())
        captured['minimum_probability'] = min(float(np.min(p)) for p in lanes.values())
        return values
    cuts = support_cutoffs(rotation_cut_scale=1.0)
    try:
        quad = fixed_node_integrate(evaluate, cuts, expected_hex, rtol=2e-4, atol=1e-10)
        converged = True
        exception = None
    except AdaptiveQuadratureError as exc:
        converged = False
        exception = str(exc)
    if 'values' not in captured:
        raise RuntimeError('R10C_IDENTITY_MISMATCH: no fixed node evaluation')
    # Diagnostic reconstruction uses the exact same captured 105 integrand values,
    # with the unchanged production GK15/GK7 reduction; it requests no new nodes.
    intervals = [_gk15_reduce(a*a, b*b, captured['values'][15*i:15*(i+1)])
                 for i, (a, b) in enumerate(zip(cuts[:-1], cuts[1:]))]
    total = sum((x['high'] for x in intervals), np.zeros_like(intervals[0]['high']))
    error = sum((x['error'] for x in intervals), np.zeros_like(total))
    tolerance = 1e-10 + 2e-4*np.abs(total)
    normalized = error/np.maximum(tolerance, np.finfo(float).tiny)
    diag = {'status': 'EXACT_NODE_FIXED_GK15_REPLAY_PASS_NOT_GLOBAL_CONTINUUM_BOUND' if converged
            else 'EXACT_NODE_FIXED_GK15_QUADRATURE_UNRESOLVED',
            'evaluations': 105, 'refinements': 0, 'mandatory_intervals': len(cuts)-1,
            'support_cutoffs': cuts, 'rtol': 2e-4, 'atol': 1e-10,
            'max_normalized_component_error': float(np.max(normalized)),
            'failed_component_count': int(np.sum(error > tolerance)),
            'component_error_estimate': error.tolist(),
            'component_tolerance': tolerance.tolist(),
            'max_column_sum_defect': captured['max_column_sum_defect'],
            'minimum_probability': captured['minimum_probability'],
            'adaptive_exception': exception,
            'error_claim': 'EMBEDDED_NUMERICAL_ESTIMATE_NOT_INTERVAL_BOUND'}
    atomic_json(out/'FIXED_GK_DIAGNOSTIC.json', diag)
    if not converged:
        return diag
    if quad['evaluations'] != 105 or quad['refinements'] != 0 or np.any(error > tolerance):
        raise RuntimeError('fixed GK15 internal verdict contradiction')
    vals = np.asarray(quad['integral']).reshape(3, 2, 9)
    errs = np.asarray(quad['component_error_estimate']).reshape(3, 2, 9)
    lanes = {}
    for k, name in enumerate(('F2-RHO', 'F2-FROZEN', 'F1-RHO')):
        lanes[name] = {}
        for j, E in enumerate((0.5, 5.0)):
            vec = np.zeros(10); err = np.zeros(10)
            vec[np.arange(10) != 2] = vals[k, j]
            err[np.arange(10) != 2] = errs[k, j]
            lanes[name][str(E)] = {'indexed_transition_areas_a0sq':
                                  {str(i+1): float(x) for i, x in enumerate(vec) if i != 2},
                                  'indexed_reaction_loss_a0sq': float(vec.sum()),
                                  'indexed_reaction_loss_error_estimate_a0sq': float(err.sum()),
                                  'Z2_shell_areas_a0sq': _shell_summary(vec),
                                  'component_error_estimate_a0sq':
                                  {str(i+1): float(x) for i, x in enumerate(err) if i != 2}}
    result = {'status': diag['status'], 'lanes': lanes,
              'claim_limit': 'FINITE_INDEXED_STATE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION'}
    atomic_json(out/'EXACT_THREE_LANE_RESULT.json', result)
    return result


def compare_appendix_and_classify(repo, out):
    """Apply the precommitted implementation-comparison rule after Phase B PASS."""
    import json
    from pathlib import Path
    from bass_he.geometry import atomic_json
    repo, out = map(Path, (repo, out))
    exact = json.loads((out/'EXACT_THREE_LANE_RESULT.json').read_text())
    if exact['status'] != 'EXACT_NODE_FIXED_GK15_REPLAY_PASS_NOT_GLOBAL_CONTINUUM_BOUND':
        raise ValueError('Phase B admission required')
    base = repo/'research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST'
    oracle = json.loads((base/'APPENDIX_A_ORACLE.json').read_text())
    old = json.loads((base/'APPENDIX_A_COMPARISON.json').read_text())
    scale = old['a0_squared_cm2']
    classification = 'AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'
    lanes = {}
    for name, values in exact['lanes'].items():
        rows = []; log_all = []; log_dom = []
        for energy in ('0.5', '5.0'):
            for shell in ('1', '2', '3'):
                model = values[energy]['Z2_shell_areas_a0sq'][shell]*scale
                author = oracle['shell_capture_cm2'][energy][shell]
                if model <= 0 or author <= 0:
                    raise ValueError('nonpositive Appendix-A comparison cell')
                ratio = model/author; logratio = math.log(ratio)
                rows.append({'energy_keV_u': float(energy), 'shell_n': int(shell),
                             'model_cm2': model, 'author_cm2': author,
                             'model_over_author': ratio, 'log_ratio': logratio,
                             'classification': classification})
                log_all.append(logratio)
                if shell in ('2', '3'): log_dom.append(logratio)
        lanes[name] = {'rows': rows,
                       'all_six_multiplicative_rms': math.exp(math.sqrt(sum(x*x for x in log_all)/6)),
                       'dominant_n2_n3_multiplicative_rms': math.exp(math.sqrt(sum(x*x for x in log_dom)/4)),
                       'classification': classification}
    impacts = {}
    material_change = False
    small_all = True
    for energy in ('0.5', '5.0'):
        dyn = exact['lanes']['F2-RHO'][energy]
        frozen = exact['lanes']['F2-FROZEN'][energy]
        a = dyn['indexed_reaction_loss_a0sq']; b = frozen['indexed_reaction_loss_a0sq']
        if a <= 0: raise ValueError('nonpositive F2-RHO indexed loss')
        diff = abs(b-a); relative = diff/a
        err = (dyn['indexed_reaction_loss_error_estimate_a0sq']+
               frozen['indexed_reaction_loss_error_estimate_a0sq'])
        important = relative > 0.01 and diff > 10*err
        material_change |= important
        small_all &= relative <= 0.01 and diff <= 10*err
        impacts[energy] = {'F2_FROZEN_over_F2_RHO': b/a, 'absolute_change_a0sq': diff,
                           'relative_change': relative,
                           'sum_embedded_error_estimates_a0sq': err,
                           'change_over_sum_embedded_error': diff/err if err else None,
                           'material_output_change': important}
    improved = (lanes['F2-FROZEN']['all_six_multiplicative_rms'] <=
                0.95*lanes['F2-RHO']['all_six_multiplicative_rms'] and
                lanes['F2-FROZEN']['dominant_n2_n3_multiplicative_rms'] <=
                0.95*lanes['F2-RHO']['dominant_n2_n3_multiplicative_rms'])
    if material_change:
        case = 'I2_MEASURABLE_CASE_A' if improved else 'I2_MEASURABLE_CASE_B'
    elif small_all:
        case = 'I2_SCOPED_NEGLIGIBLE_CASE_C'
    else:
        case = 'I2_QUANTIFICATION_UNRESOLVED'
    result = {'classification': classification, 'I2_case': case,
              'material_author_improvement': improved,
              'material_output_change': material_change,
              'materiality_rule': json.loads((Path(__file__).parent/'DECISION_RULE_PRECOMMITTED.json').read_text()),
              'lanes': lanes, 'frozen_impact': impacts,
              'quarantined_R10A_exploratory_ratios':
              {e: old['F2_frozen_impact'][e]['F2_FROZEN_over_F2_RHO'] for e in ('0.5', '5.0')},
              'claim_limit': 'AUTHOR_IMPLEMENTATION_COMPARISON_NOT_PHYSICAL_VALIDATION'}
    atomic_json(out/'APPENDIX_A_AND_I2_COMPARISON.json', result)
    return result
