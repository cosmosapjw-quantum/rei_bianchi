#!/usr/bin/env python3
"""Exact arithmetic readout of PHYS15 immutable Hessian/preconditioner data.

No physical source evaluation, root solve, or history execution is performed.
The scale is the original affine gas-coordinate radius S; C is the stored
binary64 matrix, interpreted as its exact dyadic value.
"""
import argparse
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import resource
import struct
import time


def bits(s):
    return F.from_float(struct.unpack('>d', bytes.fromhex(s))[0])


def interval(x):
    return (bits(x['lo_bits']), bits(x['hi_bits']))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def scale(a, c):
    return (a[0]*c, a[1]*c) if c >= 0 else (a[1]*c, a[0]*c)


def enc(v):
    with localcontext() as ctx:
        ctx.prec = 18
        ctx.rounding = ROUND_FLOOR
        lo = str(Decimal(v.numerator)/Decimal(v.denominator))
        ctx.rounding = ROUND_CEILING
        hi = str(Decimal(v.numerator)/Decimal(v.denominator))
    return {'exact': [str(v.numerator), str(v.denominator)],
            'outward_decimal': [lo, hi]}


def identity(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phys15', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    start = time.perf_counter()
    srcp = args.phys15/'inputs/phys14/inputs/ncp07/results/full/SOURCE_BOX.json'
    cp = args.phys15/'inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json'
    src = json.loads(srcp.read_text())
    pre = json.loads(cp.read_text())
    C = [[F.from_float(x) for x in row] for row in pre['fixed_C']]
    S = [F.from_float(x) for x in pre['radius']]
    H = [[[interval(x) for x in row] for row in mat] for mat in src['G_gg']]
    q = bits(pre['q']['hi_bits'])
    Z = (F(0), F(0))
    T = [[[scale(sum_intervals([scale(H[a][j][k], C[i][a])
                                 for a in range(4)]), S[j]*S[k]/S[i])
           for k in range(4)] for j in range(4)] for i in range(4)]
    mags = [[[max(abs(v[0]), abs(v[1])) for v in row] for row in mat] for mat in T]
    rows = [sum((v for row in mat for v in row), F(0)) for mat in mags]
    L = max(rows)
    assert 0 <= q < 1
    assert L > 0
    comparisons = {
        'q_below_0.000118': q < F('0.000118'),
        'q_squared_below_1.378e-8': q*q < F('1.378e-8'),
        'q_cubed_below_1.617e-12': q*q*q < F('1.617e-12'),
        'preconditioned_hessian_positive': L > 0,
    }
    result = {
        'schema': 'WU088_HH_PHYS16_ENDPOINT_HESSIAN_READOUT_V1',
        'status': 'EXACT_DYADIC_READOUT_COMPLETED',
        'scope': 'Static arithmetic on inherited whole-X H_F Hessian; no new physical source/root/history evaluation',
        'input_identity': {'source': identity(srcp), 'preconditioner': identity(cp)},
        'tensor_definition': 'T_ijk=(s_j*s_k/s_i)*sum_a C_ia*[D^2 H_F]^a_jk(X)',
        'tensor_magnitude': [[[enc(v) for v in row] for row in mat] for mat in mags],
        'row_sums': [enc(v) for v in rows],
        'L_H': enc(L),
        'q': enc(q),
        'kappa': enc(1/(1-q)),
        'quadratic_coefficient_L_over_2_one_minus_q': enc(L/(2*(1-q))),
        'Neumann_residual_q_powers': {str(k):enc(q**k) for k in range(1,5)},
        'comparisons': comparisons,
        'comparisons_all_true': all(comparisons.values()),
        'physical_source_calls': 0, 'root_solves': 0, 'history_runs': 0,
        'elapsed_seconds': time.perf_counter()-start,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','L_H','quadratic_coefficient_L_over_2_one_minus_q','comparisons_all_true','elapsed_seconds','peak_rss_kib']},ensure_ascii=False))


def sum_intervals(xs):
    out = (F(0), F(0))
    for x in xs:
        out = add(out,x)
    return out


if __name__ == '__main__':
    main()
