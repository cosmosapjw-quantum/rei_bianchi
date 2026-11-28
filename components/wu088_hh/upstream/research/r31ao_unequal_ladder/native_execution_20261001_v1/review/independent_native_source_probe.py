"""Independent exact invariants; no native runtime or scientific-admission claim."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import tarfile

HERE = Path(__file__).resolve().parent
LADDER = HERE.parents[1]
REPO = LADDER.parents[1]


def add(poly, key, value):
    poly[key] = poly.get(key, Q(0)) + value
    if not poly[key]:
        del poly[key]


def main():
    # Represent exp(-mu^2/(4t))*mu^m*t^(q/2), starting from U_0.
    # Independent construction is the defining recurrence U_(i+1)=-d_mu U_i.
    recurrence = {(1, -3): Q(1, 2)}
    checks = []
    for i in range(9):
        closed = {}
        n = i + 1
        for r in range(n // 2 + 1):
            add(closed, (n - 2*r, -(2*i + 3 - 2*r)),
                Q((-1)**r * math.factorial(n),
                  2**n * math.factorial(r) * math.factorial(n - 2*r)))
        assert closed == recurrence
        checks.append({'i': i, 'coefficient_identity': True})
        following = {}
        for (m, q), value in recurrence.items():
            if m:
                add(following, (m - 1, q), -m * value)
            add(following, (m + 1, q - 2), value / 2)
        recurrence = following

    windows = []
    for name, l, T in [('W1', Q(1, 16), Q(256)),
                       ('W2', Q(1, 64), Q(2)**64),
                       ('W3', Q(1, 256), Q(2)**192)]:
        margin = min(Q(1, 2**20), l / 2**20)
        # For every a,b>0 and t=u=T, sigma < 1/T, independent of input details.
        sigma_upper = 1 / T
        windows.append({'window': name, 'old_margin': str(margin),
                        'sigma_strict_upper_at_t_u_T': str(sigma_upper),
                        'real_endpoint_guard_impossible': sigma_upper <= margin})
    assert [w['real_endpoint_guard_impossible'] for w in windows] == [False, True, True]

    paths = [
        'production_solver_20261001_v1/native_driver/primitive_worker.cpp',
        'production_solver_20261001_v1/native_driver/driver.py',
        'gap_closure_20261001_g0_g6_v1/validated_callback/callback.cpp',
        'gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.cpp',
    ]
    identities = {p: hashlib.sha256((LADDER/p).read_bytes()).hexdigest() for p in paths}
    archive = REPO/'backend_sources/C01.tar.gz'
    members = {}
    with tarfile.open(archive) as tar:
        for item in tar.getmembers():
            if any(item.name.endswith(s) for s in [
                    '/src/acb_calc/integrate.c', '/src/acb_calc/integrate_gl_auto_deg.c',
                    '/doc/source/acb_calc.rst']):
                members[item.name] = hashlib.sha256(tar.extractfile(item).read()).hexdigest()
    result = {'status': 'PASS_EXACT_DENSITY_AND_FAIL_CLOSED_MARGIN_FINDING',
              'density_recurrence_checks': checks, 'margin_checks': windows,
              'source_sha256': identities,
              'pinned_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'pinned_member_sha256': members,
              'native_execution_observed': False, 'scientific_admission': False,
              'production_admission': False}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
