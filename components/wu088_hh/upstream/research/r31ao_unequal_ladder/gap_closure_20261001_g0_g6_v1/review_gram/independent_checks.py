"""Artifact review probes. Synthetic only; imports no archived comparator."""
from pathlib import Path
import json
import math
import random
import struct
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from exact_gram.engine import (sqrt_interval, spectral_norm, gram2, adjoint,
    round_binary64, binary64_value, Limits, ResourceLimit, ContractError,
    audit_frozen_binary64)

def host_bits(x):
    return int.from_bytes(struct.pack('>d', x), 'big')

def z(r, i=0):
    return F(r), F(i)

def main():
    rng = random.Random(10012026)
    results = {}
    for _ in range(800):
        q = F(rng.getrandbits(rng.randrange(1, 900)),
              1 + rng.getrandbits(rng.randrange(1, 900)))
        p = rng.randrange(1, 300)
        out = sqrt_interval(q, precision=p)
        assert out.lo >= 0 and out.lo*out.lo <= q <= out.hi*out.hi
        assert out.hi-out.lo <= F(1, 2**p)
    results['exact_sqrt_inequalities'] = {'cases': 800, 'status': 'PASS'}

    # Finite raw-bit values span the full exponent range. Midpoint probes test
    # ties across normal/subnormal/power-of-two boundaries, independently of
    # the implementation's decimal-scale fixtures.
    tested = 0
    for _ in range(1000):
        b = rng.randrange(0, 0x7fefffffffffffff)
        lo = F.from_float(struct.unpack('>d', b.to_bytes(8, 'big'))[0])
        hi = F.from_float(struct.unpack('>d', (b+1).to_bytes(8, 'big'))[0])
        for q in (lo, (lo+hi)/2, (3*lo+hi)/4, (lo+3*hi)/4):
            for s in (1, -1):
                assert round_binary64(s*q) == host_bits(float(s*q))
                tested += 1
    results['full_exponent_binary64_rne'] = {'cases': tested, 'status': 'PASS'}

    # A direct exact Gram determinant test also certifies that returned upper
    # norms dominate the eigenvalue without trusting an approximate oracle:
    # u^2 I - G is PSD iff both diagonal entries and determinant are >= 0.
    for _ in range(100):
        n = rng.randrange(1, 30)
        mat = [[z(F(rng.randrange(-30,31),7), F(rng.randrange(-30,31),11))
                for j in range(2)] for i in range(n)]
        a, (br, bi), d = gram2(mat)
        assert a*d-br*br-bi*bi >= 0
        out = spectral_norm(mat, precision=100)
        u2 = out.hi*out.hi
        assert u2 >= a and u2 >= d
        assert (u2-a)*(u2-d)-br*br-bi*bi >= 0
        # To lie below the largest eigenvalue, either l^2<=max(a,d), or the
        # characteristic determinant is nonpositive in the eigenvalue gap.
        l2 = out.lo*out.lo
        assert l2 <= max(a,d) or (l2-a)*(l2-d)-br*br-bi*bi <= 0
        assert spectral_norm(adjoint(mat), precision=100) == out
    results['exact_psd_and_adjoint_norm'] = {'cases': 100, 'status': 'PASS'}

    # This is a contract probe, not a correctness assertion. A tiny custom
    # intermediate cap should not silently allow a 201-bit pn*pn shortcut.
    probe = {'max_work_bits': 8, 'input_integer_bits': 201}
    try:
        out = sqrt_interval(F(2**200), limits=Limits(max_work_bits=8))
        probe.update(status='LIMIT_BYPASSED', result=str(out.lo),
                     inferred_shortcut_product_bits=201)
    except (ResourceLimit, ContractError) as exc:
        probe.update(status='LIMIT_ENFORCED', exception=type(exc).__name__)
    results['custom_work_cap_exact_root'] = probe

    # Existing known distinct machine predicates confirmed independently.
    local = (host_bits(1.-1e-10), 0)
    other = (host_bits(1.), 0)
    p = audit_frozen_binary64(local, other, comparison='PRIMARY')
    s = audit_frozen_binary64(local, other, comparison='SECONDARY')
    assert p['frozen_binary64_supported'] is True
    assert s['frozen_binary64_supported'] is False
    results['source_strict_predicate_split'] = {'status':'PASS'}
    results['actual_HH_evaluations'] = 0
    results['old_comparator_executions'] = 0
    results['independent_review_admitted'] = False
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
