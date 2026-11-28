#!/usr/bin/env python3
"""Exact saved-data arithmetic and durable JSON; no scientific kernel import."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path

SP = ('HI', 'HeI', 'HeII')
MOM = ['Z_eV', 'QN', 'QE_eV'] + [p + '_' + s + ('_eV' if p != 'A' else '') for p in ('A', 'B', 'H') for s in SP]
EPS = F.from_float(1.602176634e-12)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def read(path):
    return json.loads(Path(path).read_bytes())

def save_bytes(path, raw):
    """Publish a complete fresh file without overwriting a preexisting target."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_name(p.name + '.partial-' + str(os.getpid()))
    with t.open('xb') as f:
        if f.write(raw) != len(raw):
            raise OSError('short write')
        f.flush()
        os.fsync(f.fileno())
    os.link(t, p)  # atomic create-only publication; EEXIST is a failure
    t.unlink()
    d = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(d)
    finally:
        os.close(d)

def save(path, x):
    save_bytes(path, (json.dumps(x, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n').encode())

def capture(x):
    x = float(x)
    if not math.isfinite(x):
        raise ValueError('nonfinite binary64 capture')
    return F.from_float(x)

def box(x):
    a, b = F(x['lo']), F(x['hi'])
    if a > b:
        raise ValueError('inverted interval')
    return a, b

def enc(x):
    return {'lo': str(x[0]), 'hi': str(x[1])}

def add(a, b):
    return a[0] + b[0], a[1] + b[1]

def scale(a, w):
    if w < 0:
        raise ValueError('weight must be nonnegative')
    return a[0] * w, a[1] * w

def totals(m):
    for p in ('A', 'B', 'H'):
        s = '_eV' if p != 'A' else ''
        m[p + '_total' + s] = tuple(sum(m[p + '_' + sp + s][i] for sp in SP) for i in (0, 1))
    return m

def old_metrics(path):
    w = box(path['weight'])
    if w[0] != w[1] or w[0] <= 0:
        raise ValueError('non-point/nonpositive original weight')
    absolute = {k: box(path['weighted_reduction'][k]) for k in ['P_final', 'anchor'] + MOM}
    correction = {k: scale(box(path['cumulative_correction'][k]), w[0]) for k in MOM}
    correction['P_final'] = scale(box(path['segments'][-1]['DP']), w[0])
    correction['energy_eV'] = scale(box(path['segments'][-1]['energy_endpoint_minus_captured_erg']), w[0] / EPS)
    return {'absolute': totals(absolute), 'correction': totals(correction)}

def new_metrics(track, weight):
    # Old absolute endpoints are already weighted; new endpoints are not.
    a = {k: scale(box(track['true_moment_enclosures'][k]), weight) for k in MOM}
    a['P_final'] = scale(box(track['final_photon']['true_absolute_interval']), weight)
    a['anchor'] = scale(box(track['summed_true_anchor_eV']), weight)
    c = {k: scale(box(track['cumulative_moment_corrections'][k]['interval']), weight) for k in MOM}
    c['P_final'] = scale(box(track['final_photon']['true_minus_captured_interval']), weight)
    c['energy_eV'] = scale(box(track['final_energy_stock_eV']['true_minus_captured_interval']), weight)
    return {'absolute': totals(a), 'correction': totals(c)}

def encode_metrics(x):
    return {kind: {k: enc(v) for k, v in vals.items()} for kind, vals in x.items()}

def decode_metrics(x):
    return {kind: {k: box(v) for k, v in vals.items()} for kind, vals in x.items()}

def sum_metrics(seq):
    out = {'absolute': {}, 'correction': {}}
    for x in seq:
        for kind, vals in x.items():
            for k, v in vals.items():
                out[kind][k] = add(out[kind].get(k, (F(0), F(0))), v)
    return out

def compare_metrics(old, new):
    rows = []
    if set(old) != set(new):
        raise ValueError('metric kind mismatch')
    for kind in sorted(old):
        if set(old[kind]) != set(new[kind]):
            raise ValueError('metric key mismatch')
        for k in sorted(old[kind]):
            a, b = old[kind][k], new[kind][k]
            wa, wb = a[1] - a[0], b[1] - b[0]
            rows.append({'kind': kind, 'quantity': k, 'old': enc(a), 'new_raw': enc(b),
                         'overlap': max(a[0], b[0]) <= min(a[1], b[1]),
                         'nested': a[0] <= b[0] <= b[1] <= a[1],
                         'width_nonincreasing': wb <= wa,
                         'old_width': str(wa), 'new_width': str(wb),
                         'gain_fraction': str((wa - wb) / wa) if wa else None})
    if len(rows) != 34:
        raise ValueError('expected 17 absolute + 17 correction metrics')
    return rows

def decimal_display(x, digits=22):
    with localcontext() as c:
        c.prec = digits
        return str(Decimal(x.numerator) / Decimal(x.denominator))
