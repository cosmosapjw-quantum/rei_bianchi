#!/usr/bin/env python3
"""Pinned-source checker. --check-contract never imports JAX or executes Rust.

Default mode runs both original Python modules and the Rust public-API frontend.
A missing reference, nonzero child exit or malformed reply is a hard failure.
This is an f64 implementation comparison, never an interval proof.
"""
from __future__ import annotations
import argparse
import base64
import bisect
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/forward/rust-20260922'
CRATE = ROOT / 'rust/rei_microphysics'
PINS = {'monolithic_model_b2a.py': '3d806e1c1d3bb523bb3c339d1a141f67d7f10069',
        'node_lift_operator.py': '6f5c13f02d0e549e581a02d3c4d8b8313b209bbf'}
RTOL = 5e-13
C = 2.99792458e10
MPC = 3.085677581491367e24
OPS = {'transform', 'mass', 'signed', 'pchip', 'opacity', 'photons', 'gamma'}
SCALARS = ['redshift', 'nH_phys', 'nHe_phys', 'Hubble']
ARRAYS = ['sigma_HI', 'sigma_HeI', 'sigma_HeII', 'redshift_coeff', 'source_fraction']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def blob(b):
    return hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()


def verify_bytes(b, expected):
    require(digest(b) == expected, 'INPUT_HASH_MISMATCH')


def policy_check(policy):
    require(policy['schema'] == 1 and policy['rtol_expression'] == RTOL
            and policy['atol_global'] == 0, 'POLICY_MISMATCH')


def num(x):
    require(not isinstance(x, bool), 'BOOLEAN_NOT_NUMBER')
    if isinstance(x, str):
        require(x in ('NaN', 'Inf', '-Inf'), 'BAD_SPECIAL_TOKEN')
        return {'NaN': math.nan, 'Inf': math.inf, '-Inf': -math.inf}[x]
    require(isinstance(x, (int, float)), 'BAD_NUMBER_SHAPE')
    return float(x)


def vec(x, n=None):
    require(isinstance(x, list), 'BAD_ARRAY_SHAPE')
    if n is not None:
        require(len(x) == n, 'BAD_ARRAY_LENGTH')
    return [num(v) for v in x]


def table_shape(t):
    k = vec(t['knots']); require(len(k) >= 2, 'BAD_TABLE_SHAPE')
    require(len(t['coeffs']) == 4, 'BAD_TABLE_SHAPE')
    return k, [vec(c, len(k)-1) for c in t['coeffs']]


def table_error(t, x):
    k, c = table_shape(t)
    if any(not math.isfinite(v) for v in k + sum(c, [])) or any(a >= b for a, b in zip(k, k[1:])):
        return 'BAD_TABLE'
    if not math.isfinite(x):
        return 'NONFINITE_X'
    if not k[0] <= x <= k[-1]:
        return 'OUTSIDE_TABLE_DOMAIN'
    return None


def context(case, fixture):
    b = copy.deepcopy(fixture['base'])
    require(set(case.get('params', {})) <= set(b['params']), 'UNKNOWN_PARAMETER')
    b['params'].update(case.get('params', {}))
    for key in ('state', 'emissivity', 'tables'):
        if key in case:
            b[key] = copy.deepcopy(case[key])
    b['state'] = vec(b['state'], 10)
    e = b['emissivity']; b['emissivity'] = vec(e, 4) if isinstance(e, list) else [num(e)] * 4
    for k in SCALARS:
        b['params'][k] = num(b['params'][k])
    for k in ARRAYS:
        b['params'][k] = vec(b['params'][k], 4)
    require(len(b['tables']) == 2, 'BAD_TABLE_PAIR')
    for t in b['tables']:
        table_shape(t)
    return b


def tok(v):
    if math.isnan(v): return 'NaN'
    if v == math.inf: return 'Inf'
    if v == -math.inf: return '-Inf'
    return format(v, '.17g')


def table_tokens(t):
    k, c = table_shape(t)
    return [str(len(k))] + [tok(v) for v in k + sum(c, [])]


def request_line(case, fixture):
    op = case['op']; out = [case['id'], op]
    require(op in OPS, 'UNKNOWN_OPERATION')
    if op == 'transform': out += [tok(x) for x in vec(case['z'], 9)]
    elif op in ('mass', 'signed'):
        p = vec(case['prior']); v = num(case['total'] if op == 'mass' else case['rate'])
        out += [tok(v), str(len(p))] + [tok(x) for x in p]
    elif op == 'pchip': out += [tok(num(case['x']))] + table_tokens(case['table'])
    else:
        b = context(case, fixture); p = b['params']
        values = b['state'] + [p[k] for k in SCALARS] + sum([p[k] for k in ARRAYS], []) + b['emissivity']
        out += [tok(x) for x in values]
        for t in b['tables']: out += table_tokens(t)
    return ' '.join(out)


def parse_replies(text, ids):
    rows = text.splitlines(); require(len(rows) == len(ids), 'REPLY_COUNT_MISMATCH')
    result = {}
    for row, expected_id in zip(rows, ids):
        t = row.split(); require(len(t) >= 3 and t[0] == expected_id, 'REPLY_ID_MISMATCH')
        require(expected_id not in result, 'DUPLICATE_REPLY')
        if t[1] == 'ERR':
            require(len(t) == 3, 'MALFORMED_ERROR_REPLY'); result[expected_id] = {'error': t[2]}
        else:
            require(t[1] == 'OK', 'MALFORMED_REPLY'); n = int(t[2])
            require(n >= 0 and len(t) == n+3, 'REPLY_SHAPE_MISMATCH')
            values = [float(x) for x in t[3:]]
            result[expected_id] = {'values': values}
    return result


def guard_tests():
    count = 0
    def rejects(fn):
        nonlocal count
        try: fn()
        except (ValueError, KeyError, TypeError): count += 1; return
        raise AssertionError('NEGATIVE_GUARD_DID_NOT_REJECT')
    rejects(lambda: verify_bytes(b'changed', digest(b'original')))
    rejects(lambda: policy_check({'schema': 1, 'rtol_expression': 5e-12, 'atol_global': 0}))
    rejects(lambda: vec([[1, 2]]))
    rejects(lambda: vec([1, 2], 4))
    for text in ['', 'b OK 0', 'a OK 2 1', 'a ERR BAD EXTRA', 'a BAD 0', 'a OK 1 not_float']:
        rejects(lambda text=text: parse_replies(text, ['a']))
    return count


def check_contract():
    lock = json.loads((DOC/'SOURCE_IMPORT_LOCK.json').read_text())
    policy_check(json.loads((DOC/'PARITY_POLICY.json').read_text()))
    checked = []
    for r in lock['references']:
        p = ROOT/r['path']; raw = p.read_bytes()
        require(p.name in PINS and blob(raw) == PINS[p.name] == r['git_blob'], 'SOURCE_BLOB_MISMATCH')
        verify_bytes(raw, r['sha256']); require(len(raw) == r['bytes'], 'SOURCE_SIZE_MISMATCH')
        # Validate live originals when present, without altering them.
        original = ROOT/r['original_path']
        if original.exists(): require(blob(original.read_bytes()) == r['git_blob'], 'LIVE_SOURCE_DRIFT')
        checked.append(r['git_blob'])
    require(len(checked) == len(set(checked)) == 2, 'MISSING_REFERENCE')
    for r in lock['boundary_subset']: verify_bytes((ROOT/r['path']).read_bytes(), r['sha256'])
    for path, sha in lock['immutable_repository_blobs'].items():
        p = ROOT/path
        if p.exists(): require(blob(p.read_bytes()) == sha, 'SCIENTIFIC_STATE_DRIFT')
    manifest = DOC/'CODE_INPUT_MANIFEST.sha256'; seen = set()
    for line in manifest.read_text().splitlines():
        sha, path = line.split(None, 1)
        require(path not in seen and not Path(path).is_absolute() and '..' not in Path(path).parts, 'BAD_MANIFEST_PATH')
        seen.add(path); verify_bytes((ROOT/path).read_bytes(), sha)
    needed = {p.relative_to(ROOT).as_posix() for p in CRATE.rglob('*') if p.is_file() and 'target' not in p.parts}
    needed |= {Path(__file__).relative_to(ROOT).as_posix(), (DOC/'PARITY_POLICY.json').relative_to(ROOT).as_posix(), (DOC/'SOURCE_IMPORT_LOCK.json').relative_to(ROOT).as_posix()}
    require(needed <= seen, 'UNBOUND_CODE_OR_FIXTURE')
    cargo = tomllib.loads((CRATE/'Cargo.toml').read_text())
    require(cargo['package']['name'] == 'rei_microphysics' and not cargo.get('dependencies'), 'CRATE_SCOPE_DRIFT')
    require(tomllib.loads((CRATE/'Cargo.lock').read_text())['package'] == [{'name':'rei_microphysics','version':'0.1.0'}], 'LOCK_SCOPE_DRIFT')
    fixture = json.loads((CRATE/'tests/fixtures/forward_inputs.json').read_text())
    require(fixture['schema'] == 1 and fixture['kind'] == 'SYNTHETIC_IMPLEMENTATION_FIXTURE', 'FIXTURE_KIND_DRIFT')
    ids = [c['id'] for c in fixture['cases']]
    require(len(ids) == len(set(ids)), 'DUPLICATE_CASE_ID')
    require({c['op'] for c in fixture['cases']} == OPS, 'MISSING_FUNCTION_CASES')
    for case in fixture['cases']:
        require(case['id'] and not any(x.isspace() for x in case['id']), 'BAD_CASE_ID')
        request_line(case, fixture)
    return fixture, {'grade':'CONTRACT_ONLY_NOT_RUST_PARITY', 'cases':len(ids),
                     'raw_protocol_cases':len(fixture['raw_protocol_cases']), 'source_blobs':checked,
                     'manifest_files':len(seen), 'negative_guards':guard_tests()}


def load_reference(name):
    path = DOC/'source_subset/python'/name
    require(blob(path.read_bytes()) == PINS[name], 'SOURCE_BLOB_MISMATCH')
    spec = importlib.util.spec_from_file_location('forward_reference_'+path.stem, path)
    require(spec is not None and spec.loader is not None, 'REFERENCE_LOADER_MISSING')
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # Import/package failures propagate. No fallback.
    return module


def error_code(e):
    mapping = {
        'prior must be a finite one-dimensional array':'PRIOR_NOT_FINITE',
        'conditional_mass_prior must be a finite one-dimensional array':'CONDITIONAL_MASS_PRIOR_NOT_FINITE',
        'total must be finite and nonnegative':'INVALID_TOTAL',
        'prior must be nonnegative':'NEGATIVE_PRIOR',
        'INFEASIBLE_ZERO_PRIOR_SUPPORT':'INFEASIBLE_ZERO_PRIOR_SUPPORT',
        'conditional_mass_prior must be nonnegative with positive sum':'INVALID_CONDITIONAL_MASS_PRIOR',
        'rate must be finite':'NONFINITE_RATE',
    }
    require(isinstance(e, ValueError) and str(e) in mapping, 'UNEXPECTED_REFERENCE_FAILURE: '+repr(e))
    return mapping[str(e)]


def legacy_context(b, jnp):
    v = b['state']; s = {'N':jnp.asarray(v[:4], dtype=jnp.float64),'xHII':v[4],
        'xHeI':v[5],'xHeII':v[6],'xHeIII':v[7],'u':v[8],'GammaHI':v[9]}
    p = {k:jnp.asarray(v, dtype=jnp.float64) for k, v in b['params'].items() if k != 'redshift'}
    p['z_cos'] = b['params']['redshift']
    # Source has one knot grid. Both fixtures use the same grid.
    require(b['tables'][0]['knots'] == b['tables'][1]['knots'], 'REFERENCE_SHARED_KNOT_GRID_REQUIRED')
    p['log_kappa_knots'] = jnp.asarray(b['tables'][0]['knots'], dtype=jnp.float64)
    p['log_kappa_pchip_coeffs'] = jnp.asarray([t['coeffs'] for t in b['tables']], dtype=jnp.float64)
    return s, p


def table_value(t, x):
    k, c = table_shape(t); i = min(bisect.bisect_right(k, x)-1, len(k)-2); dx = x-k[i]
    terms = [c[j][i]*dx**(3-j) for j in range(4)]
    return ((c[0][i]*dx+c[1][i])*dx+c[2][i])*dx+c[3][i], sum(map(abs, terms))


def opacity_terms(b, si=False):
    s = b['state']; p = b['params']; x = math.log(s[9]/1e-12)
    low = [math.exp(table_value(t, x)[0]) for t in b['tables']]
    density_factor = 1e6 if si else 1.0; cross_factor = 1e4 if si else 1.0
    length = MPC/100.0 if si else MPC
    nh = p['nH_phys']*(1-s[4])*density_factor; ne = p['nHe_phys']*s[5]*density_factor
    ne2 = p['nHe_phys']*s[6]*density_factor
    a = [[n*sig/cross_factor*length/(1+p['redshift']) for sig in p[key]]
         for n, key in [(nh,'sigma_HI'),(ne,'sigma_HeI'),(ne2,'sigma_HeII')]]
    return [[low[0]], [low[1],a[1][1]], [a[0][2],a[1][2]], [a[0][3],a[1][3],a[2][3]]]


def scales(case, fixture, reference):
    op = case['op']
    if op in ('transform','mass','signed'): return list(map(abs, reference))
    if op == 'pchip': return [table_value(case['table'], num(case['x']))[1]]
    b = context(case, fixture); p = b['params']; n = b['state'][:4]
    if op == 'gamma':
        pref = C*(1+p['redshift'])**3/MPC**3
        groups = [[pref*sig*v for sig, v in zip(p[key], n)] for key in ['sigma_HI','sigma_HeI','sigma_HeII']]
        return [sum(map(abs,g)) for g in groups] + list(map(abs,groups[0]))
    kt = opacity_terms(b)
    if op == 'opacity': return [sum(map(abs,t)) for t in kt]
    k = list(map(sum, kt)); red = [p['Hubble']*v for v in p['redshift_coeff']]
    return [abs(b['emissivity'][i]*p['source_fraction'][i])+abs(C*(1+p['redshift'])/MPC*k[i]*n[i])
            +abs(red[i]*n[i])+(abs(red[i+1]*n[i+1]) if i<3 else 0) for i in range(4)]


def reference_case(case, fixture, model, lift, jnp):
    op = case['op']
    if op in ('mass','signed'):
        try:
            prior = vec(case['prior'])
            if op == 'mass': out = lift.positive_mass_projection(prior, num(case['total'])); vals = out.tolist()
            else: vals = [float(v) for a in lift.signed_transfer_lift(num(case['rate']),prior) for v in a]
            return {'values':vals}
        except ValueError as e: return {'error':error_code(e)}
    if op == 'transform':
        s = model.transform_z_to_y(jnp.asarray(vec(case['z'],9),dtype=jnp.float64))
        return {'values':[float(v) for v in s['N']]+[float(s[k]) for k in ['xHII','xHeI','xHeII','xHeIII','u','GammaHI']]}
    if op == 'pchip':
        t = case['table']; x = num(case['x']); restriction = table_error(t,x)
        legacy = float(model.pchip_eval(jnp.asarray(vec(t['knots']),dtype=jnp.float64),jnp.asarray([vec(c) for c in t['coeffs']],dtype=jnp.float64),jnp.asarray(x,dtype=jnp.float64)))
        if restriction: return {'error':restriction,'intentional_api_restriction':True,'legacy_value':legacy}
        return {'values':[legacy]}
    b = context(case,fixture); s,p = legacy_context(b,jnp)
    if op == 'gamma':
        a,c,d,g = model.gamma_species(s,p)
        return {'values':[float(a),float(c),float(d)]+[float(v) for v in g]}
    gamma = b['state'][9]
    x = math.log(gamma/1e-12) if gamma>0 else -math.inf if gamma==0 else math.nan
    restriction = next((e for t in b['tables'] if (e := table_error(t,x))),None)
    legacy = model.opacity_cMpc_inv(s,p) if op=='opacity' else model.photon_rates(s,jnp.asarray(b['emissivity'],dtype=jnp.float64),p)
    if restriction: return {'error':restriction,'intentional_api_restriction':True,'legacy_values':[float(v) for v in legacy]}
    return {'values':[float(v) for v in legacy]}


def close(actual, expected, scale):
    if math.isnan(expected): require(math.isnan(actual),'NAN_CLASS_MISMATCH'); return
    if math.isinf(expected): require(actual==expected,'INF_CLASS_MISMATCH'); return
    require(math.isfinite(actual), 'NONFINITE_RUST_VALUE')
    require(math.isfinite(scale) and scale >= 0, 'INVALID_COMPARISON_SCALE')
    require(abs(actual-expected) <= RTOL*scale, f'PARITY_MISMATCH actual={actual:.17e} reference={expected:.17e} scale={scale:.17e}')


def invariants(fixture, got):
    v = lambda key: got[key]['values']
    require(v('opacity_baseline') == v('opacity_hi_mutation'), 'LOWGROUP_HI_DOUBLE_COUNT')
    p = fixture['base']['params']; s = fixture['base']['state']
    delta = p['nHe_phys']*s[5]*p['sigma_HeI'][1]*MPC/(1+p['redshift'])
    close(v('opacity_hei_mutation')[1]-v('opacity_baseline')[1],delta,abs(delta))
    for a,b in zip(v('gamma_baseline'),v('gamma_z0')): close(a,64*b,abs(64*b))
    b = context({},fixture)
    for actual, terms in zip(v('opacity_baseline'),opacity_terms(b,si=True)): close(actual,sum(terms),sum(map(abs,terms)))
    pref = (C/100)*(1+p['redshift'])**3/(MPC/100)**3
    for i,key in enumerate(['sigma_HI','sigma_HeI','sigma_HeII']):
        expected = pref*sum(sig/1e4*n for sig,n in zip(p[key],s[:4])); close(v('gamma_baseline')[i],expected,abs(expected))
    for i in (2,3): close(v('opacity_z0')[i],4*v('opacity_baseline')[i],abs(4*v('opacity_baseline')[i]))
    case = next(c for c in fixture['cases'] if c['id']=='telescoping'); b = context(case,fixture)
    absorb = [C*4/MPC*sum(t)*n for t,n in zip(opacity_terms(b),[1,2,3,4])]
    terms = v('telescoping')+absorb
    close(sum(terms),-.1,sum(map(abs,terms)))
    sites = [v(k) for k in ['population_t0','population_t1_predictor','thermal_tgamma','thermal_t1_final']]
    require(len({tuple(x) for x in sites})==4,'SITE_VALUES_COLLAPSED')
    return ['HI_OWNER','G2A_HEI','GAMMA_Z_CUBE','CGS_SI_GAMMA','CGS_SI_OPACITY','PROPER_OPACITY_Z','REDSHIFT_TELESCOPING','FOUR_DISTINCT_SITES']


def json_safe(x):
    if isinstance(x,float) and not math.isfinite(x): return tok(x)
    if isinstance(x,list): return [json_safe(v) for v in x]
    if isinstance(x,dict): return {k:json_safe(v) for k,v in x.items()}
    return x


def child_streams(record, stdout, stderr):
    """Retain raw bytes where supplied, plus readable text for the receipt."""
    for name, value in [('stdout', stdout), ('stderr', stderr)]:
        if isinstance(value, bytes):
            record[name+'_base64'] = base64.b64encode(value).decode('ascii')
            record[name] = value.decode('utf-8', errors='backslashreplace')
        else:
            record[name] = '' if value is None else str(value)


def run_rust_batch(command, batch, label, trace):
    """Record every attempted child, including partial output on timeout.

    Capture bytes before decoding, so invalid UTF-8 cannot destroy the raw log.
    A timeout is not assigned a made-up exit code. No retries or fallbacks.
    """
    payload = ('\n'.join(batch)+'\n').encode('utf-8')
    record = {'command':list(command), 'cwd':str(ROOT), 'batch':label,
              'stdin_sha256':digest(payload), 'timeout_seconds':180,
              'returncode':None, 'status':'ATTEMPTING', 'stdout':'', 'stderr':''}
    trace['child_runs'].append(record)
    print('COMMAND', json.dumps(command), flush=True)
    try:
        proc = subprocess.run(command, input=payload, capture_output=True,
                              cwd=ROOT, timeout=180)
    except subprocess.TimeoutExpired as exc:
        record['status'] = 'TIMEOUT'; record['error'] = repr(exc)
        child_streams(record, exc.output, exc.stderr)
        raise
    except OSError as exc:
        record['status'] = 'LAUNCH_ERROR'; record['error'] = repr(exc)
        raise
    else:
        record['returncode'] = proc.returncode
        record['status'] = 'COMPLETED' if proc.returncode == 0 else 'NONZERO_EXIT'
        child_streams(record, proc.stdout, proc.stderr)
    finally:
        print('CHILD_STATUS', record['status'], flush=True)
        print('EXIT', record['returncode'], flush=True)
        print('RUST_STDERR_BEGIN\n'+record['stderr']+'RUST_STDERR_END', flush=True)
        print('RUST_STDOUT_BEGIN\n'+record['stdout']+'RUST_STDOUT_END', flush=True)
    require(proc.returncode == 0, 'RUST_EXECUTION_FAILED')
    return proc.stdout.decode('utf-8') if isinstance(proc.stdout, bytes) else proc.stdout


def execute(fixture, contract, trace=None):
    trace = {} if trace is None else trace
    trace.update({'phase':'reference_import', 'child_runs':[]})
    os.environ.setdefault('JAX_PLATFORMS','cpu')
    model = load_reference('monolithic_model_b2a.py'); lift = load_reference('node_lift_operator.py')
    import jax
    import jax.numpy as jnp
    import numpy
    import scipy
    require(jax.config.read('jax_enable_x64'), 'REFERENCE_NOT_F64')
    trace['versions'] = {'python':sys.version, 'jax':jax.__version__,
                         'numpy':numpy.__version__, 'scipy':scipy.__version__,
                         'jax_x64':bool(jax.config.read('jax_enable_x64')),
                         'jax_backend':jax.default_backend()}
    cases = fixture['cases']; lines = [request_line(c,fixture) for c in cases]
    raw = fixture['raw_protocol_cases']; ids = [c['id'] for c in cases]+[c['line'].split()[0] for c in raw]
    command = ['cargo','run','--quiet','--manifest-path',str(CRATE/'Cargo.toml'),'--locked','--example','eval_fixture']
    observed = []
    for batch in [lines+[c['line'] for c in raw],list(reversed(lines))]:
        label = 'forward' if len(observed) == 0 else 'reverse'
        trace['phase'] = 'rust_'+label
        stdout = run_rust_batch(command, batch, label, trace)
        observed.append(parse_replies(stdout, ids if len(observed)==0 else list(reversed([c['id'] for c in cases]))))
    got, reverse = observed; report = []; failures = []
    trace.update({'phase':'comparison', 'cases':report, 'failures':failures})
    for c in cases:
        ref = None
        try:
            ref = reference_case(c,fixture,model,lift,jnp); actual = got[c['id']]
            if 'error' in ref:
                require(ref['error']==c.get('error')==actual.get('error')==reverse[c['id']].get('error'),'ERROR_BRANCH_MISMATCH')
            else:
                require('error' not in actual and 'error' not in reverse[c['id']] and 'error' not in c,'UNEXPECTED_ERROR')
                expected = ref['values']; a = actual['values']; rr = reverse[c['id']]['values']
                require(len(a)==len(expected)==len(rr),'OUTPUT_SHAPE_MISMATCH')
                for x,y,scale in zip(a,expected,scales(c,fixture,expected)): close(x,y,scale)
                for x,y in zip(rr,a): close(x,y,0 if math.isfinite(y) else abs(y))
                if 'exact' in c: require(a==vec(c['exact']),'EXACT_ASSERTION_FAILED')
            report.append({'id':c['id'],'status':'PASS','reference':ref,'rust':actual})
        except Exception as e:
            failures.append({'id':c['id'],'error':repr(e),'reference':ref,
                             'rust':got.get(c['id']),'rust_reverse':reverse.get(c['id'])})
    for c in raw:
        require(got[c['line'].split()[0]].get('error')==c['error'],'PROTOCOL_NEGATIVE_CASE_FAILED')
    for c in fixture['python_shape_cases']:
        try:
            if c['op']=='mass': lift.positive_mass_projection(c['prior'],c['total'])
            else: lift.signed_transfer_lift(c['rate'],c['prior'])
        except ValueError as e: require('finite one-dimensional' in str(e),'REFERENCE_SHAPE_ERROR_MISMATCH')
        else: raise ValueError('REFERENCE_ACCEPTED_NESTED_PRIOR')
    try: inv = invariants(fixture,got)
    except Exception as e: inv=[];failures.append({'id':'independent_invariants','error':repr(e)})
    result = {'grade':'PINNED_FUNCTION_F64_PARITY_ONLY','passed':not failures,'contract':contract,'cases':report,'failures':failures,'invariants':inv,
        'versions':trace['versions'], 'child_runs':trace['child_runs'], 'validated_enclosure_replaced':False}
    print(json.dumps(json_safe(result),indent=2,allow_nan=False))
    return result


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--check-contract',action='store_true')
    parser.add_argument('--output',type=Path,help='New receipt path; existing evidence is never overwritten.')
    args = parser.parse_args()
    output = None
    trace = {'phase':'receipt_destination', 'child_runs':[]}
    try:
        # Reserve the destination before doing any validation or expensive work.
        # Never reopen/replace an existing evidence file, even on failure.
        if args.output:
            output = args.output.open('x', encoding='utf-8')
        trace['phase'] = 'contract'
        fixture, contract = check_contract()
        result = contract if args.check_contract else execute(fixture,contract,trace)
        if args.check_contract: print(json.dumps(result,indent=2))
        code = 0 if args.check_contract or result['passed'] else 1
    except Exception as exc:
        result = {'passed':False, 'error':repr(exc),
                  'classification':'CHECKER_OR_REFERENCE_OR_EXECUTION_FAILURE',
                  'fallback_used':False, **trace}
        print(json.dumps(json_safe(result),allow_nan=False),file=sys.stderr)
        code = 2
    if output is not None:
        try:
            with output:
                json.dump(json_safe(result),output,indent=2,allow_nan=False)
                output.write('\n'); output.flush(); os.fsync(output.fileno())
        except Exception as exc:
            print(json.dumps({'passed':False,'classification':'RECEIPT_WRITE_FAILURE',
                              'error':repr(exc),'prior_exit_code':code,
                              'fallback_used':False}),file=sys.stderr)
            code = 2
    return code


if __name__ == '__main__':
    raise SystemExit(main())
