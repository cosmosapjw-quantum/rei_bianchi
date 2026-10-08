#!/usr/bin/env python3
"""Streaming exact-input analytic controls; NOT a continuum-time solution oracle.

Execution belongs to the parent's aggregate resource supervisor. Preparation does
not execute this module. See ORACLE_SCHEMA.md for the complete input contract.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
import pathlib
import re
import struct
import sys
from collections import Counter
from fractions import Fraction as F

import mpmath as mp

OWNERS = ('N', 'U', 'QN', 'QE', 'red', 'outN', 'outE',
          'A_HI', 'A_HeI', 'A_HeII', 'B_HI', 'B_HeI', 'B_HeII')
INC = OWNERS[2:]
NTERMS = ('A_HI', 'A_HeI', 'A_HeII', 'outN')
ETERMS = ('B_HI', 'B_HeI', 'B_HeII', 'red', 'outE')
MAX_RECORD_FIELDS = 2048
MAX_RECORDS = 8192
MAX_LANES = 8
EPS = F.from_float(1.602176634e-12)


def m(x):
    """Exact rational input, rounded once at the active oracle precision."""
    return mp.mpf(x.numerator) / x.denominator if isinstance(x, F) else mp.mpf(x)


class Scalar:
    def __init__(self, bits, exponent):
        if not re.fullmatch('[0-9a-fA-F]{16}', bits):
            raise ValueError('bits must be exactly 16 hexadecimal digits')
        self.bits = bits.lower()
        self.f = struct.unpack('>d', bytes.fromhex(bits))[0]
        self.exp = int(exponent)
        if abs(self.exp) > (1 << 20):
            raise ValueError('exponent outside the immutable Wide contract')
        if math.isnan(self.f):
            raise ValueError('NaN input is forbidden')
        if not math.isfinite(self.f):
            if self.exp:
                raise ValueError('nonfinite scalar must have exp=0')
            self.q = None
        else:
            self.q = F.from_float(self.f)
            self.q *= (1 << self.exp) if self.exp >= 0 else F(1, 1 << -self.exp)


def q(r, key):
    value = r[key].q
    if value is None:
        raise ValueError('nonfinite value: ' + key)
    return value


def wide(r, key):
    v = r[key]
    if v.q is None or v.q < 0 or (v.q == 0 and (v.exp or v.bits != '0000000000000000')):
        raise ValueError('invalid canonical Wide: ' + key)
    if v.q and not 1 <= v.f < 2:
        raise ValueError('non-normalized Wide: ' + key)
    return v.q


def scalar(r, key):
    if r[key].exp:
        raise ValueError('binary64 scalar has nonzero exp: ' + key)
    return q(r, key)


def J(k, h):
    return h if k == 0 else -mp.expm1(-k * h) / k


def phi2(x):
    """Entire (exp(x)-1-x)/x^2, with no tiny-argument cancellation."""
    if abs(x) >= mp.mpf('0.1'):
        return (mp.expm1(x) - x) / x**2
    term = total = mp.mpf('0.5')
    for k in range(1, 512):
        term *= x / (k + 2)
        total += term
        if abs(term) <= mp.eps * abs(total) / 8:
            return total
    raise ValueError('analytic phi2 series did not converge within fixed cap')


def source_energy(lam, h):
    """Integral exp(-t)*(1-exp(-lam*t))/lam, including lam=0.

    The small-lam series analytically integrates each t power using 1F1.
    No quadrature, precision escalation, or stored sequence is needed.
    """
    if not h:
        return mp.mpf(0)
    z = lam * h
    if z >= mp.mpf('0.1'):
        return (J(1, h) - J(lam + 1, h)) / lam
    coefficient, total = h*h/2, mp.mpf(0)
    for k in range(512):
        term = coefficient * mp.hyp1f1(k + 2, k + 3, -h)
        total += term
        if k and abs(term) <= mp.eps * abs(total) / 8:
            return total
        coefficient *= -z / (k + 3)
    raise ValueError('analytic source series did not converge within fixed cap')


def Z(t, a, b, front):
    """Closed-form integral of exp(t*y)*(1-y)^front over [a,b]."""
    d = b - a
    if not d:
        return mp.mpf(0)
    if not t:
        return d * (1 - (a + b) / 2) if front else d
    # Physical endpoint differences stay high precision; no quadrature/cache.
    e = mp.expm1(t * d)
    plain = e / t
    return mp.exp(t * a) * (((1 - b) * plain + d*d*phi2(t*d))
                          if front else plain)


def expr_add(*parts):
    out = {}
    for e in parts:
        for epoch, coefficient in e.items():
            out[epoch] = out.get(epoch, F(0)) + coefficient
    return {k: v for k, v in out.items() if v}


def expr_neg(e):
    return {k: -v for k, v in e.items()}


def expr_value(e):
    return mp.fsum(m(v) if k is None else m(v) * mp.exp(-m(k))
                   for k, v in e.items())


def residual(n0, e0, n1, e1, inc):
    n = n1 - n0 + sum((inc[x] for x in NTERMS), F(0)) - inc['QN']
    ec = sum((inc[x] for x in ETERMS), F(0)) - inc['QE']
    return n, expr_add(e1, expr_neg(e0), {None: ec})


def allocated_bytes(value, seen=None):
    """Observed Python allocation sizes; no invented dict capacity."""
    import sys
    if seen is None: seen=set()
    if id(value) in seen: return 0
    seen.add(id(value)); total=sys.getsizeof(value)
    if isinstance(value,dict): return total+sum(allocated_bytes(k,seen)+allocated_bytes(v,seen) for k,v in value.items())
    if isinstance(value,(list,tuple,set)): return total+sum(allocated_bytes(x,seen) for x in value)
    if isinstance(value,F): return total+allocated_bytes(value.numerator,seen)+allocated_bytes(value.denominator,seen)
    if hasattr(value,'__dict__'): return total+allocated_bytes(vars(value),seen)
    if hasattr(value,'_mpf_'): return total+allocated_bytes(value._mpf_,seen)
    return total

class Audit:
    def __init__(self, writer):
        self.writer = writer
        self.counts = Counter()
        self.failures = []
        self.failure_count = 0
        self.checks = 0
        self.maxima = {}
        self.lanes = {}
        self.peak_fields = 0
        self.max_dps = 160
        self.peak_record_allocated_bytes=0
        self.peak_lane_allocated_bytes=0

    def check(self, ok, rid, name, actual=None, limit=None):
        self.checks += 1
        if not ok:
            self.failure_count += 1
            if len(self.failures) < 80:
                self.failures.append({'id': rid, 'check': name,
                    'actual': None if actual is None else mp.nstr(m(actual), 30),
                    'limit': None if limit is None else mp.nstr(m(limit), 30)})

    def metric(self, rid, name, value):
        value = m(value)
        self.writer.writerow((rid, name, mp.nstr(value, 32)))
        self.maxima[name] = max(self.maxima.get(name, mp.mpf(0)), abs(value))

    def output(self, rid, r, key, truth):
        v, loss = wide(r, key), wide(r, key + '.loss')
        ro = scalar(r, key + '.readout')
        rb = wide(r, key + '.readout_bound')
        self.check(abs(v - ro) <= rb, rid, key + ':exact_readout_bound', abs(v - ro), rb)
        error = abs(m(v) - truth) / abs(truth) if truth else abs(m(v))
        self.metric(rid, key + ':relative_amplitude_error', error)
        self.check(error <= mp.mpf('3e-12'), rid, key + ':amplitude', error, mp.mpf('3e-12'))
        lv = r[key + '.log']
        if lv.exp:
            raise ValueError('log exp must be zero')
        if not truth:
            self.check(v == 0 and loss == 0 and lv.f == -math.inf,
                       rid, key + ':exact_empty')
        else:
            lt = mp.log(truth)
            allowance = mp.mpf('2e-13') + 8 * m(F.from_float(math.ulp(float(lt))))
            le = abs(m(lv.q) - lt) if lv.q is not None else mp.inf
            self.metric(rid, key + ':log_error', le)
            self.check(v > 0 and le <= allowance, rid, key + ':log', le, allowance)
        # .loss is a lost-positive-addend bound, NOT an enclosure of analytic
        # coefficient/partial-rounding error. Exact operation controls audit it.

    def fixture(self, kind, rid, r):
        if kind == 'segment':
            f, source = m(wide(r, 'f')), m(wide(r, 'q'))
            rates = [m(scalar(r, 'r' + str(i))) for i in range(3)]
            h, energy = m(scalar(r, 'h')), m(scalar(r, 'E'))
            self.check(scalar(r, 'EPS') == EPS, rid, 'unchanged_EPS')
            eps, lam = m(EPS), mp.fsum(rates)
            if h < 0 or h > 2 or (0 < h < m(F.from_float(1e-12))) or min(rates) < 0:
                raise ValueError('unsupported segment fixture')
            n = f * mp.exp(-lam * h) + source * J(lam, h)
            ci = f * J(lam, h) + source * h*h * phi2(-lam*h)
            es = source_energy(lam, h)
            ei = eps * energy * (f * J(lam + 1, h) + source * es)
            targets = dict(N=n, U=eps*energy*mp.exp(-h)*n, QN=source*h,
                           QE=eps*energy*source*J(1, h), red=ei, outN=mp.mpf(0), outE=mp.mpf(0))
            targets.update({name: rates[i]*ci for i, name in enumerate(OWNERS[7:10])})
            targets.update({name: rates[i]*ei for i, name in enumerate(OWNERS[10:])})
            for name in OWNERS:
                self.output(rid, r, name, targets[name])
        elif kind in ('restriction', 'restriction_min_subnormal'):
            precision = 800 if kind.endswith('_min_subnormal') else 160
            self.max_dps = max(self.max_dps, precision)
            with mp.workdps(precision):
                l, right, beta, a, b = [m(scalar(r, x)) for x in ('L', 'R', 'beta', 'a', 'b')]
                front_q = scalar(r, 'front')
                if front_q not in (0, 1) or right <= l or abs(beta) > 128 or a > b:
                    raise ValueError('unsupported restriction fixture')
                if precision == 800 and not any(abs(scalar(r, x)) == F(1, 1 << 1074)
                                                for x in ('a', 'b')):
                    raise ValueError('800 digits reserved for predeclared minimum-subnormal restriction')
                front, n = bool(front_q), m(wide(r, 'n'))
                a, b = max(a, l), min(b, right)
                if a >= b or not n:
                    targets = (mp.mpf(0), mp.mpf(0))
                else:
                    width = right - l
                    ya, yb = (a-l)/width, (b-l)/width
                    den = Z(beta, mp.mpf(0), mp.mpf(1), front)
                    targets = (n*Z(beta, ya, yb, front)/den,
                               n*mp.exp(l)*Z(beta+width, ya, yb, front)/den)
                for name, target in zip(('N', 'M'), targets):
                    self.output(rid, r, name, target)
        elif kind == 'density':
            l, right, beta, eta = [m(scalar(r, x)) for x in ('L', 'R', 'beta', 'eta')]
            front_q = scalar(r, 'front')
            if front_q not in (0, 1) or right <= l or abs(beta) > 128:
                raise ValueError('unsupported point-density fixture')
            front, n = bool(front_q), m(wide(r, 'N'))
            if eta < l or eta >= right or not n:
                target = mp.mpf(0)
            else:
                width = right - l
                y = (eta - l) / width
                taper = 1 - y if front else mp.mpf(1)
                target = n * mp.exp(beta*y) * taper / (width*Z(beta, mp.mpf(0), mp.mpf(1), front))
            self.output(rid, r, 'f', target)
        elif kind == 'difference':
            target = abs(wide(r, 'a') - wide(r, 'b'))
            self.output(rid, r, 'd', m(target))
        elif kind == 'add':
            a, b, value, loss = [wide(r, x) for x in ('a', 'b', 'sum', 'loss')]
            # Whole-addend suppression only; partial ordinary rounding is separate.
            dropped = min(a, b) if a and b and value == max(a, b) else F(0)
            self.check(dropped <= loss, rid, 'exact_dropped_addend_bound', dropped, loss)
            self.metric(rid, 'add_partial_rounding_error', value + dropped - a - b)
            if 'residual_sign' in r:
                sign = scalar(r, 'residual_sign')
                if sign not in (-1, 1):
                    raise ValueError('cache residual_sign must be -1 or +1')
                self.metric(rid, 'signed_cache_reduction_defect', sign*(value-a-b))
                self.check(dropped > 0, rid, 'cache_control_has_actual_suppression')
        else:
            return False
        return True

    def record(self, kind, rid, r):
        self.counts[kind] += 1
        self.peak_fields = max(self.peak_fields, len(r))
        self.peak_record_allocated_bytes=max(self.peak_record_allocated_bytes,allocated_bytes(r))
        if self.fixture(kind, rid, r):
            return
        lane, sep, tail = rid.partition(':')
        if kind not in ('inventory', 'local', 'increment', 'global') or not lane:
            raise ValueError('unknown kind or invalid lane: ' + kind)
        if lane not in self.lanes and len(self.lanes) >= MAX_LANES:
            raise ValueError('lane cap exceeded')
        data = self.lanes.setdefault(lane, {'inventory': {}, 'local': {}, 'increment': {}})
        if kind == 'inventory':
            if not sep or tail not in ('initial', 'final') and not re.fullmatch('(in|out):[0-3]', tail):
                raise ValueError('invalid inventory identity')
            epoch, eps = scalar(r, 's'), scalar(r, 'EPS')
            self.check(eps == EPS, rid, 'unchanged_EPS')
            indices = sorted({int(k[1:-2]) for k in r if re.fullmatch(r'p[0-9]+\.[NM]', k)})
            if indices != list(range(len(indices))) or len(indices) > 256:
                raise ValueError('noncontiguous panel IDs or panel cap')
            expected = {'s', 'EPS'} | {f'p{i}.{term}' for i in indices for term in ('N', 'M')}
            if set(r) != expected:
                raise ValueError('missing/unexpected canonical inventory field')
            n = sum((wide(r, f'p{i}.N') for i in indices), F(0))
            cm = sum((wide(r, f'p{i}.M') for i in indices), F(0))
            data['inventory'][tail] = (n, {epoch: eps * cm} if cm else {})
        elif kind == 'increment':
            if set(r) != set(INC) or tail not in ('0', '1', '2', '3'):
                raise ValueError('increment must contain exactly retained11')
            data['increment'][int(tail)] = {k: wide(r, k) for k in INC}
        elif kind == 'local':
            if tail not in ('0', '1', '2', '3'):
                raise ValueError('local step outside four-step contract')
            data['local'][int(tail)] = r
        else:
            if sep or 'global' in data:
                raise ValueError('global ID must be a unique lane name')
            data['global'] = r

    def budget(self, rid, r, nr, er, inc):
        for term, exact, source, floor, cap in (
                ('N', m(nr), inc['QN'], F(1, 10**10), F(1, 10**20)),
                ('E', expr_value(er), inc['QE'], F(1, 10**20), F(1, 10**30))):
            ro = scalar(r, 'r' + term)
            bound, loss = wide(r, 'b' + term), wide(r, 'loss' + term)
            allowance = F(1, 10**10) * max(source, floor)
            self.metric(rid, term + ':canonical_residual', exact)
            self.metric(rid, term + ':residual_readout_defect', m(ro) - exact)
            self.check(bound + loss <= cap, rid, term + ':loss_plus_audit_cap', bound+loss, cap)
            self.check(abs(ro)+bound+loss <= allowance, rid, term+':readout_budget', abs(ro)+bound+loss, allowance)
            self.check(abs(exact)+m(bound+loss) <= m(allowance), rid,
                       term+':canonical_budget', abs(exact)+m(bound+loss), allowance)

    def telescope(self, lane, data):
        inv, local, increments = data['inventory'], data['local'], data['increment']
        if not local or len(local) > 4 or sorted(local) != list(range(len(local))):
            raise ValueError('empty, noncontiguous or excessive local steps: ' + lane)
        if set(local) != set(increments) or 'global' not in data:
            raise ValueError('local/authoritative increment mismatch or missing global: ' + lane)
        count = len(local)
        required = {'initial', 'final'} | {f'{side}:{i}' for i in range(count) for side in ('in', 'out')}
        if set(inv) != required:
            raise ValueError('missing independent inventories: ' + lane)
        n0, e0 = inv['initial']
        nf, ef = inv['final']
        self.check(inv['initial'] == inv['in:0'], lane, 'independent_initial_boundary')
        self.check(inv['final'] == inv[f'out:{count-1}'], lane, 'independent_final_boundary')
        total_inc = {x: sum((increments[i][x] for i in range(count)), F(0)) for x in INC}
        global_n, global_e = residual(n0, e0, nf, ef, total_inc)
        local_n, local_e, captured_n, captured_e = F(0), {}, F(0), F(0)
        permanent = {'N': F(0), 'E': F(0)}
        for i in range(count):
            rid, rec = f'{lane}:{i}', local[i]
            incoming, outgoing = inv[f'in:{i}'], inv[f'out:{i}']
            if i:
                self.check(inv[f'out:{i-1}'] == incoming, rid, 'independently_captured_boundary_continuity')
            capture_inc = {x: wide(rec, x) for x in INC}
            self.check(capture_inc == increments[i], rid, 'local_vs_authoritative_retained11')
            nr, er = residual(*incoming, *outgoing, capture_inc)
            local_n += nr
            local_e = expr_add(local_e, er)
            captured_n += scalar(rec, 'rN')
            captured_e += scalar(rec, 'rE')
            cache = [wide(rec, x) for x in ('in.N', 'in.U', 'out.N', 'out.U')]
            cn, ce = residual(cache[0], {None: cache[1]}, cache[2], {None: cache[3]}, capture_inc)
            self.metric(rid, 'N:captured_stock_cache_defect', cn - nr)
            self.metric(rid, 'E:captured_stock_cache_defect', expr_value(expr_add(ce, expr_neg(er))))
            for t in ('N', 'E'):
                permanent[t] += wide(rec, 'loss'+t)
            self.budget(rid, rec, nr, er, capture_inc)
        self.check(local_n == global_n, lane, 'exact_number_local_global_telescope', local_n-global_n, F(0))
        self.check(not expr_add(local_e, expr_neg(global_e)), lane, 'exact_symbolic_energy_local_global_telescope')
        self.metric(lane, 'N:sum_captured_residuals_minus_fresh_global', captured_n-global_n)
        self.metric(lane, 'E:sum_captured_residuals_minus_fresh_global', m(captured_e)-expr_value(global_e))
        # Outward cumulative loss may be larger than the exact per-step sum.
        for t in ('N', 'E'):
            self.check(wide(data['global'], 'loss'+t) >= permanent[t], lane,
                       t+':permanent_loss_not_erased', permanent[t], wide(data['global'], 'loss'+t))
        self.budget(lane+':global', data['global'], global_n, global_e, total_inc)


def records(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['kind', 'id', 'field', 'bits', 'exp']:
            raise ValueError('unexpected CSV header: ' + str(path))
        for (kind, rid), rows in itertools.groupby(reader, key=lambda r: (r['kind'], r['id'])):
            block = {}
            if len(rid) > 160 or len(kind) > 40:
                raise ValueError('record identifier exceeds cap')
            for row in rows:
                key = row['field']
                if None in row or not key or len(key) > 64 or key in block or len(block) >= MAX_RECORD_FIELDS:
                    raise ValueError('malformed, duplicate or excessive record field')
                block[key] = Scalar(row['bits'], row['exp'])
            yield kind, rid, block


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', nargs='*', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path('results/HIGH_PRECISION.json'))
    parser.add_argument('--metrics', type=pathlib.Path, default=pathlib.Path('results/oracle_metrics.csv'))
    parser.add_argument('--require', default='segment,restriction,density,difference,add,inventory,local,increment,global')
    args = parser.parse_args()
    inputs = args.inputs or [pathlib.Path('results/oracle.csv')]
    mp.mp.dps = 160
    csv.field_size_limit(1024)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    with args.metrics.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('id', 'metric', 'value'))
        audit, seen = Audit(writer), set()
        try:
            for path in inputs:
                for kind, rid, block in records(path):
                    identity = (kind, rid)
                    if identity in seen or len(seen) >= MAX_RECORDS:
                        raise ValueError('repeated block or record cap exceeded')
                    seen.add(identity)
                    audit.record(kind, rid, block)
                    audit.peak_lane_allocated_bytes=max(audit.peak_lane_allocated_bytes,allocated_bytes(audit.lanes))
            for requirement in filter(None, args.require.split(',')):
                audit.check(audit.counts[requirement] > 0, 'coverage', 'required:'+requirement)
            for lane, data in audit.lanes.items():
                audit.telescope(lane, data)
        except (ValueError, KeyError, ArithmeticError, OSError) as exc:
            audit.check(False, 'input_or_evaluation', type(exc).__name__ + ': ' + str(exc))
    report = {
        'status': 'FAIL' if audit.failure_count else 'PASS',
        'scope': 'Exact-binary64 analytic primitive controls and canonical numerical-state conservation only; no physical-time continuum or global spectral-error enclosure.',
        'standard_decimal_digits': 160, 'minimum_decimal_digits': 160,
        'maximum_decimal_digits_used': audit.max_dps,
        'exact_arithmetic': 'Fraction dyadics for readout/drop bounds and N; symbolic exp(-s) coefficients for energy telescope',
        'loss_scope': 'Whole suppressed addends in add controls and canonical-to-readout quantization; analytic partial rounding is separate.',
        'counts': dict(audit.counts), 'checks': audit.checks,
        'required_coverage': list(filter(None, args.require.split(','))),
        'maximum_absolute_metrics': {k: mp.nstr(v, 32) for k, v in audit.maxima.items()},
        'failure_count': audit.failure_count, 'failures': audit.failures,
        'oracle_quadrature_sites': 0, 'oracle_quadrature_cache_sites': 0,
        'peak_record_fields': audit.peak_fields,
        'peak_record_allocated_bytes_observed': audit.peak_record_allocated_bytes,
        'peak_lane_allocated_bytes_observed': audit.peak_lane_allocated_bytes,
        'seen_identity_set_allocated_bytes': allocated_bytes(seen),
        'maxima_precision_scalar_allocated_bytes': allocated_bytes(audit.maxima),
        'python_container_capacity_note': 'getsizeof observed container/backing bytes; logical dict capacity is not exposed', 'retained_lanes': len(audit.lanes),
        'record_cap': MAX_RECORDS, 'fields_per_record_cap': MAX_RECORD_FIELDS,
        'source_hash': digest(pathlib.Path(__file__)),
        'input_hashes': {str(p): digest(p) for p in inputs if p.is_file()},
        'metrics_file': str(args.metrics), 'metrics_sha256': digest(args.metrics),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(audit.failure_count)


if __name__ == '__main__':
    sys.exit(main())
