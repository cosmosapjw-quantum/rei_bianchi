#!/usr/bin/env python3
"""Compare the NCP VigilODE matrix with the committed sandbox matrix.

Physics (endpoints, finite differences, raw ledgers, independent balances) and
cost (RHS counts, wall clocks) are reported separately. Byte equality of CSVs
across hosts is neither required nor used as a pass criterion.
"""
import csv, hashlib, json, math, sys
from pathlib import Path

sandbox, ncp, ncp_audit_path, out = map(Path, sys.argv[1:5])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
J = lambda p: json.loads(Path(p).read_text())
COST = {'native_rhs', 'native_wall_s', 'process_wall_s'}
KEY = ('mode', 'method', 'N')

def rows(path):
    with open(path) as f:
        return {(r['mode'], r['method'], r['N']): r for r in csv.DictReader(f)}

def diff(a, b):
    a, b = float(a), float(b)
    d = abs(a - b)
    return dict(abs=d, rel=(d / abs(b) if b != 0 else None), denom_zero=(b == 0),
                bitwise_equal=(a == b) and (math.copysign(1, a) == math.copysign(1, b)))

def walk(a, b, path=''):
    """Yield (path, a, b) for every numeric leaf; flag structural mismatch."""
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            yield path, 'KEYS', sorted(set(a) ^ set(b))
        for k in sorted(set(a) & set(b)):
            yield from walk(a[k], b[k], f'{path}/{k}')
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield path, 'LEN', (len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            yield from walk(x, y, f'{path}[{i}]')
    elif isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
        yield path, float(a), float(b)
    elif a != b:
        yield path, 'VALUE', (a, b)

TIMING = ('wall', 'elapsed', 'utc', 'seconds')
def is_timing(path):
    return any(t in path.lower() for t in TIMING)

sc, nc = rows(sandbox / 'analysis/ENDPOINTS_AND_COST.csv'), rows(ncp / 'analysis_r2/ENDPOINTS_AND_COST.csv')
assert set(sc) == set(nc) and len(sc) == 19
endpoint, cost = {}, {}
for k in sorted(sc, key=lambda k: (k[0], k[1], int(k[2]))):
    name = '/'.join(k)
    endpoint[name] = {c: diff(nc[k][c], sc[k][c]) for c in sc[k] if c not in COST and c not in KEY}
    cost[name] = dict(native_rhs_sandbox=int(sc[k]['native_rhs']), native_rhs_ncp=int(nc[k]['native_rhs']),
                      native_wall_s_sandbox=float(sc[k]['native_wall_s']), native_wall_s_ncp=float(nc[k]['native_wall_s']),
                      process_wall_s_sandbox=float(sc[k]['process_wall_s']), process_wall_s_ncp=float(nc[k]['process_wall_s']))
ep_max = {}
for name, cols in endpoint.items():
    for c, d in cols.items():
        m = ep_max.setdefault(c, dict(max_abs=0., max_rel=0., all_bitwise_equal=True, denom_zero_cases=[]))
        m['max_abs'] = max(m['max_abs'], d['abs'])
        if d['rel'] is not None: m['max_rel'] = max(m['max_rel'], d['rel'])
        else: m['denom_zero_cases'].append(name)
        m['all_bitwise_equal'] &= d['bitwise_equal']

# Raw record comparison: every non-timing numeric leaf of every case raw.json.
sm = J(sandbox / 'receipts/MATRIX_RECEIPT.json')
raw_cmp, raw_hash = {}, {}
for c in sm['cases']:
    name = f"{c['mode']}/{c['method']}/{c['N']}"
    sdir = sandbox / 'receipts' / Path(c['receipt']).name
    if not (sdir / 'raw.json').exists():
        sdir = sandbox / 'receipts/final_source_n4'   # reused final-source fixed N4
    ndir = ncp / 'evidence' / f"{c['mode']}_{c['method']}_n{c['N']}"
    a, b = J(ndir / 'raw.json'), J(sdir / 'raw.json')
    assert (a['mode'], a['method'], int(a['N'])) == (b['mode'], b['method'], int(b['N']))
    numeric, structural, timing_leaves, max_abs, unequal = 0, [], 0, 0., 0
    for path, x, y in walk(a, b):
        if isinstance(x, str):
            if not is_timing(path): structural.append([path, x, str(y)[:120]])
            continue
        if is_timing(path):
            timing_leaves += 1; continue
        numeric += 1
        if x != y:
            unequal += 1; max_abs = max(max_abs, abs(x - y))
    raw_cmp[name] = dict(sandbox_receipt=str(sdir.relative_to(sandbox)), numeric_leaves=numeric,
                         unequal_numeric_leaves=unequal, max_abs_numeric_difference=max_abs,
                         timing_leaves_skipped=timing_leaves, structural_differences=structural[:10])
    raw_hash[name] = dict(sandbox_raw_sha256=sha(sdir / 'raw.json'), ncp_raw_sha256=sha(ndir / 'raw.json'))

# Finite-difference / refinement section of the analyzer outputs.
sa, na = J(sandbox / 'analysis/MATRIX_ANALYSIS.json'), J(ncp / 'analysis_r2/MATRIX_ANALYSIS.json')
fd = {}
for section in ('refinement', 'empirical_comparisons'):
    leaves = [(p, x, y) for p, x, y in walk(na[section], sa[section]) if not isinstance(x, str) and not is_timing(p)]
    other = [(p, x, str(y)[:80]) for p, x, y in walk(na[section], sa[section]) if isinstance(x, str)]
    fd[section] = dict(numeric_leaves=len(leaves), unequal=sum(x != y for _, x, y in leaves),
                       max_abs=max((abs(x - y) for _, x, y in leaves), default=0.), structural=other[:10])

# Independent C9 balances: sandbox committed audit vs the same audit re-applied on NCP.
s_aud, n_aud = J(sandbox / 'c9_code/MATRIX_INDEPENDENT_RAW_AUDIT.json'), J(ncp_audit_path)
audit = {}
for section in ('max_abs_independent_audits', 'max_abs_cumulative_balances_over_all_prefixes'):
    audit[section] = {k: dict(sandbox=s_aud[section].get(k), ncp=n_aud[section].get(k),
                              equal=s_aud[section].get(k) == n_aud[section].get(k))
                      for k in sorted(set(s_aud[section]) | set(n_aud[section]))}
for k in ('unique_cases', 'accepted_macro_records', 'Radau_chemical_segments', 'Radau_accepted_stages',
          'Radau_dimension_counts', 'Radau_prepared_node_counts', 'native_rhs_attempts',
          'reported_Radau_max_scaled_component_residual', 'reported_Radau_max_library_wrms', 'SSPRK_accepted_max_tau'):
    audit[k] = dict(sandbox=s_aud.get(k), ncp=n_aud.get(k), equal=s_aud.get(k) == n_aud.get(k))
case_bal = {}
for s_case, n_case in zip(sorted(s_aud['cases'], key=lambda c: (c['mode'], c['method'], int(c['N']))),
                          sorted(n_aud['cases'], key=lambda c: (c['mode'], c['method'], int(c['N'])))):
    assert (s_case['mode'], s_case['method'], int(s_case['N'])) == (n_case['mode'], n_case['method'], int(n_case['N']))
    name = f"{s_case['mode']}/{s_case['method']}/{s_case['N']}"
    case_bal[name] = dict(source_birth_N_equal=s_case['source_birth_N'] == n_case['source_birth_N'],
                          source_birth_U_equal=s_case['source_birth_U'] == n_case['source_birth_U'],
                          whole_history_balances_max_abs_change=max(abs(n_case['whole_history_balances'][k] - s_case['whole_history_balances'][k]) for k in s_case['whole_history_balances']),
                          rhs_equal=s_case['native_rhs_attempts'] == n_case['native_rhs_attempts'])

totals = dict(native_rhs_sandbox=sum(v['native_rhs_sandbox'] for v in cost.values()),
              native_rhs_ncp=sum(v['native_rhs_ncp'] for v in cost.values()),
              native_wall_s_sandbox=sum(v['native_wall_s_sandbox'] for v in cost.values()),
              native_wall_s_ncp=sum(v['native_wall_s_ncp'] for v in cost.values()),
              process_wall_s_sandbox=sum(v['process_wall_s_sandbox'] for v in cost.values()),
              process_wall_s_ncp=sum(v['process_wall_s_ncp'] for v in cost.values()))
result = dict(schema='rei.lrs.vigilode.ncp_vs_sandbox.1',
              policy='CSV byte equality across hosts NOT required; physics and cost reported separately',
              csv_sha256=dict(sandbox=sha(sandbox / 'analysis/ENDPOINTS_AND_COST.csv'), ncp=sha(ncp / 'analysis_r2/ENDPOINTS_AND_COST.csv')),
              endpoint_columns_max=ep_max, endpoint_per_case=endpoint,
              raw_records=raw_cmp, raw_hashes=raw_hash, finite_difference=fd,
              independent_balances=audit, per_case_balances=case_bal,
              cost_per_case=cost, cost_totals=totals)
out.write_text(json.dumps(result, indent=2) + '\n')
summary = dict(endpoint_all_bitwise={c: m['all_bitwise_equal'] for c, m in ep_max.items()},
               endpoint_max_abs={c: m['max_abs'] for c, m in ep_max.items() if not m['all_bitwise_equal']},
               raw_unequal={k: (v['unequal_numeric_leaves'], v['numeric_leaves'], v['max_abs_numeric_difference'], len(v['structural_differences'])) for k, v in raw_cmp.items()},
               fd=fd, audit_all_equal=all(v['equal'] for s in ('max_abs_independent_audits', 'max_abs_cumulative_balances_over_all_prefixes') for v in audit[s].values()),
               audit_counts={k: audit[k] for k in audit if not k.startswith('max_abs')},
               rhs_all_equal=all(v['rhs_equal'] for v in case_bal.values()), totals=totals)
print(json.dumps(summary, indent=1))
