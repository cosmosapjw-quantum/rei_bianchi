#!/usr/bin/env python3
"""Discriminating exact examples for PHYS15 mean-residual and finite readout.

The polynomial map is manufactured, not a WU088_HH physical source. No old
candidate imports, physical roots, source callbacks, or history runs occur.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time


def matvec(a, x):
    return [sum((v*w for v, w in zip(row, x)), Q()) for row in a]


def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), Q())


def inv(a):
    n = len(a)
    b = [list(row)+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        p = next(i for i in range(j, n) if b[i][j])
        b[j], b[p] = b[p], b[j]
        pivot = b[j][j]
        b[j] = [v/pivot for v in b[j]]
        for i in range(n):
            if i != j:
                fac = b[i][j]
                b[i] = [v-fac*w for v, w in zip(b[i], b[j])]
    return [row[n:] for row in b]


def pair(q):
    return {'numerator': str(q.numerator), 'denominator': str(q.denominator),
            'display_float': float(q)}


def main(output):
    start = time.perf_counter()
    checks = []
    equalities = 0

    def same(name, a, b):
        nonlocal equalities
        if not isinstance(a, list):
            a, b = [a], [b]
        assert a == b, name
        equalities += len(a)
        checks.append({'name': name, 'status': 'PASS', 'exact_equalities': len(a)})

    def holds(name, condition):
        assert condition, name
        checks.append({'name': name, 'status': 'PASS', 'exact_comparison': True})

    # Four gas-like coordinates; off-diagonal coupling and a true quadratic term.
    L = [[Q(1), Q(-1,10000), Q(0), Q(1,20000)],
         [Q(1,20000), Q(1), Q(-1,50000), Q(0)],
         [Q(0), Q(1,50000), Q(1), Q(-1,100000)],
         [Q(-1,1000), Q(1,30000), Q(1,20000), Q(1)]]
    eps = Q(1,10000)
    v = [Q(1), Q(0), Q(0), Q(-13,10)]
    gF = [Q(9,10), Q(3,10), Q(3,5), Q(27,2)]
    d = [Q(1,100000), Q(-1,10000000), Q(3,10000000), Q(1,20000)]
    g2 = [a+b for a,b in zip(gF,d)]
    constant = [z+eps*c*gF[0]**2 for z,c in zip(matvec(L,gF),v)]

    def H(g):
        return [z+eps*c*g[0]**2-k for z,c,k in zip(matvec(L,g),v,constant)]

    def jac(g):
        return [[L[i][j]+(2*eps*v[i]*g[0] if j == 0 else 0)
                 for j in range(4)] for i in range(4)]

    r = H(g2)
    meanA = [[L[i][j]+(eps*v[i]*(gF[0]+g2[0]) if j == 0 else 0)
              for j in range(4)] for i in range(4)]
    same('constructed_full_root', H(gF), [Q(0)]*4)
    same('mean_jacobian_residual_positive_sign', matvec(meanA,d), r)
    endpoint_error = [a-b for a,b in zip(matvec(jac(g2),d),r)]
    same('endpoint_jacobian_has_quadratic_remainder', endpoint_error,
         [eps*c*d[0]**2 for c in v])
    holds('endpoint_jacobian_cannot_replace_mean_exactly', any(endpoint_error))

    # The same preconditioner proof in a small exact manufactured example.
    C = inv(L)
    Cr = matvec(C,r)
    Cv = matvec(C,v)
    S = [Q(3,200),Q(1,100),Q(1,100),Q(1,2)]
    xmax = max(g2[0],gF[0])
    B = [[2*eps*xmax*abs(Cv[i]) if j == 0 else Q(0)
          for j in range(4)] for i in range(4)]
    Bt = [[B[i][j]*S[j]/S[i] for j in range(4)] for i in range(4)]
    q = max(sum(row,Q()) for row in Bt)
    holds('uniform_q_below_one', Q(0) <= q < Q(1))
    scaled_cr = [abs(a)/s for a,s in zip(Cr,S)]
    radius = max(scaled_cr)/(1-q)
    holds('scaled_norm_residual_bound', max(abs(a)/s for a,s in zip(d,S)) <= radius)
    component = matvec(inv([[Q(i==j)-Bt[i][j] for j in range(4)] for i in range(4)]),scaled_cr)
    holds('componentwise_neumann_bound', all(abs(a)/s <= b for a,s,b in zip(d,S,component)))

    f, ct = Q(2,25), Q(10000)
    le = [Q(1),f,2*f,Q(0)]
    def Pi(g):
        return 1+f+dot(le,g)
    def temp(g):
        return ct*g[3]/Pi(g)
    de, dw = dot(le,d),d[3]
    t2, tF = temp(g2),temp(gF)
    dt = t2-tF
    same('finite_temperature_exact_denominator', dt, (ct*dw-t2*de)/(Pi(g2)-de))
    lt = [((ct if j == 3 else Q())-t2*le[j])/Pi(gF) for j in range(4)]
    same('endpoint_covector_temperature', dot(lt,d), dt)
    z = matvec(inv([list(col) for col in zip(*meanA)]),lt)
    same('adjoint_residual_temperature', dot(z,r), dt)
    sectors = [matvec(L,d), [eps*c*(g2[0]**2-gF[0]**2) for c in v]]
    same('same_inverse_sector_additivity', sum((dot(z,s) for s in sectors),Q()),dt)
    holds('positive_heat_increment_with_negative_temperature_increment', dw > 0 and de > 0 and dt < 0)
    tangent = (ct*dw-t2*de)/Pi(g2)
    holds('finite_readout_distinguished_from_tangent_readout', tangent != dt)

    # Static reuse of the original scalar contraction endpoint, no physical solve.
    original_q = Q(float.fromhex('0x1.ec474231fbe16p-14'))
    amplification = 1/(1-original_q)
    holds('original_full_amplification_display_bound', amplification < Q(500059,500000))
    result = {
        'schema':'WU088_HH_PHYS15_MANUFACTURED_TRANSFER_CHECK_V1',
        'status':'PASS','arithmetic':'fractions.Fraction; exact rational comparisons',
        'scientific_role':'R7 discriminating algebra example; not a physical source or endpoint evaluation',
        'checks':checks,'relation_count':len(checks),'exact_scalar_equalities':equalities,
        'input':{'gF':list(map(pair,gF)),'d':list(map(pair,d)),'quadratic_coefficient':pair(eps),
                 'f':pair(f),'CT':pair(ct)},
        'outputs':{'r':list(map(pair,r)),'delta_T_manufactured':pair(dt),
                   'endpoint_jacobian_residual_remainder':list(map(pair,endpoint_error)),
                   'manufactured_q':pair(q),'original_full_q':pair(original_q),
                   'original_amplification':pair(amplification)},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'physical_source_calls':0,'physical_root_calls':0,'physical_history_runs':0,
        'wall_seconds':time.perf_counter()-start}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','relation_count','exact_scalar_equalities','wall_seconds']}))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    main(ap.parse_args().output)
