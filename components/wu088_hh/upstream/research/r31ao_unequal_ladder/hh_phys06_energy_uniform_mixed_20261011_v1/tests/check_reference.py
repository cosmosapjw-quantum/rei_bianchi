"""Independent analytic/polynomial witnesses, not native physics execution."""
import json
import math
import sys
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uniform_mixed import (Interval as I, Domain, dot, matmul, matvec,
    uniform_root_arithmetic, linear_enclosure, mixed_forcing,
    implicit_mixed_arithmetic, finite_rectangle, observable_mixed,
    paired_linear_difference, energy_transform, photo_energy_component)

COUNTS = {"assertions": 0, "expected_rejections": 0}
RESULTS = []


def check(condition, message):
    COUNTS["assertions"] += 1
    if not condition:
        raise AssertionError(message)


def reject(fn, message):
    try:
        fn()
    except (ValueError, TypeError):
        COUNTS["expected_rejections"] += 1
        return
    raise AssertionError("expected rejection: " + message)


def domain():
    return Domain("manufactured_only", "analytic_v1", "common_zero",
                  "same_terminal", (I(0, 1), I(0, 1)))


def sqrt_enclosure(x, bits=120):
    """Independent integer-square-root bounds of a nonnegative rational."""
    x = Q(x)
    m = math.isqrt((x.numerator << (2 * bits)) // x.denominator)
    scale = 1 << bits
    return I(Q(m, scale), Q(m + 1, scale))


class Poly:
    """Sparse exact polynomial oracle in (y1,y2,lambda,b)."""
    def __init__(self, terms=None):
        self.terms = {k: Q(v) for k, v in (terms or {}).items() if v}

    @staticmethod
    def const(x):
        return x if isinstance(x, Poly) else Poly({(0, 0, 0, 0): Q(x)})

    @staticmethod
    def var(j):
        p = [0] * 4
        p[j] = 1
        return Poly({tuple(p): Q(1)})

    def __add__(self, other):
        other = Poly.const(other)
        out = dict(self.terms)
        for k, v in other.terms.items():
            out[k] = out.get(k, Q(0)) + v
        return Poly(out)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + (-Poly.const(other))

    def __rsub__(self, other):
        return Poly.const(other) - self

    def __mul__(self, other):
        other = Poly.const(other)
        out = {}
        for k, v in self.terms.items():
            for l, w in other.terms.items():
                key = tuple(a + b for a, b in zip(k, l))
                out[key] = out.get(key, Q(0)) + v * w
        return Poly(out)

    __rmul__ = __mul__

    def derivative(self, j):
        out = {}
        for k, v in self.terms.items():
            if k[j]:
                key = list(k)
                key[j] -= 1
                out[tuple(key)] = v * k[j]
        return Poly(out)

    def evaluate(self, values):
        return sum(v * math.prod(x**p for x, p in zip(values, k))
                   for k, v in self.terms.items())


def test_interval_and_preconditioning():
    intervals = (I(-3, -1), I(-2, 4), I(0), I(Q(1, 3), Q(4, 3)), I(2, 5))
    for a in intervals:
        for b in intervals:
            for x, y in ((a.lo, b.lo), (a.hi, b.hi), (a.mid, b.mid)):
                check((a * b).contains(x * y), "interval product enclosure")
            check(a.square().lo >= 0, "square positivity")
    reject(lambda: I(-1, 1).reciprocal(), "zero divisor")
    reject(lambda: I(0.1), "implicit float conversion")
    a = [[I(Q(19, 10), Q(21, 10)), I(Q(9, 10), Q(11, 10))],
         [I(Q(9, 10), Q(11, 10)), I(Q(29, 10), Q(31, 10))]]
    c = [[Q(3, 5), -Q(1, 5)], [-Q(1, 5), Q(2, 5)]]
    linear = linear_enclosure(a, c, [I(3), I(4)], [1, 1], center=[1, 1])
    check(linear.q < 1, "non-diagonal preconditioned contraction")
    # Independent exact inverse over 16 endpoint matrices, all within interval A.
    for mask in range(16):
        vals = [x.hi if mask & (1 << i) else x.lo
                for i, x in enumerate(sum(a, []))]
        aa, bb, cc, dd = vals
        det = aa * dd - bb * cc
        sol = ((dd * 3 - bb * 4) / det, (aa * 4 - cc * 3) / det)
        check(all(box.contains(z) for box, z in zip(linear.enclosure, sol)),
              "independent inverse lies in comparison bound")
    RESULTS.append({"name": "interval_and_nondiagonal_preconditioner", "status": "PASS",
                    "q": str(linear.q), "box": [x.json() for x in linear.enclosure]})


def test_uniform_nonlinear_family():
    # G(y,λ,b)=y+y²/8−λb/8, root y=4(sqrt(1+λb/16)−1).
    d = domain()
    root = uniform_root_arithmetic([I(-Q(1, 8), 0)],
        [[I(Q(15, 16), Q(17, 16))]], [[1]], [0], [Q(1, 4)], d)
    jets = implicit_mixed_arithmetic(root, [I(-Q(1, 8), 0)],
        [I(-Q(1, 8), 0)], [-Q(1, 8)], [[0]], [[0]], [[[Q(1, 4)]]],
        centers=([Q(1, 16)], [Q(1, 16)], [Q(1, 8)]))
    for l in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        for b in (Q(0), Q(1, 3), Q(2, 3), Q(1)):
            s = sqrt_enclosure(1 + l * b / 16)
            y = 4 * (s - 1)
            u = b / (8 * s)
            v = l / (8 * s)
            w = (1 + l * b / 32) / (8 * s * s * s)
            check(I(-Q(1, 4), Q(1, 4)).contains(y), "closed form root in X")
            for name, true_box in (("u", u), ("v", v), ("w", w)):
                check(jets[name].enclosure[0].contains(true_box), "closed form " + name)
    finite = finite_rectangle(jets["w"].enclosure, d, (I(0, 1), I(0, 1)))
    exact_corner = 4 * (sqrt_enclosure(Q(17, 16)) - 1)
    check(finite[0].contains(exact_corner), "finite corner value in integral bound")
    check(finite[0].lo > 0, "manufactured finite sign certified conditionally")
    check(not root.native_authority and not jets["native_authority"], "never native authority")
    RESULTS.append({"name": "uniform_nonlinear_analytic_family", "status": "PASS",
        "q": str(root.q), "root_image_radius": [str(x) for x in root.image_radius],
        "mixed_bound": jets["w"].enclosure[0].json(),
        "finite_corner_radical_bound": exact_corner.json(),
        "scope": "manufactured mathematical family, not HH"})


def test_all_implicit_chain_terms():
    y1, y2, la, bb = [Poly.var(i) for i in range(4)]
    target1 = la * bb * Q(1, 10)
    target2 = (la * la * bb + la * bb * bb) * Q(1, 20)
    e1, e2 = y1 - target1, y2 - target2
    gs = ((2 + la * Q(1, 7)) * e1 + (1 + bb * Q(1, 11)) * e2 + e1 * e1 * Q(1, 5),
          (1 + bb * Q(1, 17)) * e1 + (3 + la * Q(1, 19)) * e2 + e1 * e2 * Q(1, 13))
    nonzero_terms = [False, False, False]
    for l, b in ((Q(1, 3), Q(2, 5)), (Q(4, 5), Q(1, 7)), (Q(1), Q(1))):
        y = (l * b / 10, (l * l * b + l * b * b) / 20)
        values = (*y, l, b)
        u = (b / 10, (2 * l * b + b * b) / 20)
        v = (l / 10, (l * l + 2 * l * b) / 20)
        w = (Q(1, 10), (l + b) / 10)
        a = [[g.derivative(i).evaluate(values) for i in range(2)] for g in gs]
        ga = [g.derivative(2).evaluate(values) for g in gs]
        gb = [g.derivative(3).evaluate(values) for g in gs]
        gab = [g.derivative(2).derivative(3).evaluate(values) for g in gs]
        gya = [[g.derivative(i).derivative(2).evaluate(values) for i in range(2)] for g in gs]
        gyb = [[g.derivative(i).derivative(3).evaluate(values) for i in range(2)] for g in gs]
        h = [[[g.derivative(i).derivative(j).evaluate(values) for j in range(2)]
              for i in range(2)] for g in gs]
        check(all(g.evaluate(values) == 0 for g in gs), "manufactured branch exact root")
        check(matvec(a, u) == tuple(I(-x) for x in ga), "AU polynomial identity")
        check(matvec(a, v) == tuple(I(-x) for x in gb), "AV polynomial identity")
        forcing = mixed_forcing(gab, gya, gyb, h, u, v)
        check(forcing == matvec(a, w), "full mixed chain polynomial identity")
        for index, term in enumerate((matvec(gya, v), matvec(gyb, u),
                                      tuple(dot(u, matvec(hh, v)) for hh in h))):
            nonzero_terms[index] |= any(x != I(0) for x in term)
    check(all(nonzero_terms), "all three chain terms exercised nontrivially")
    RESULTS.append({"name": "independent_multivariate_polynomial_chain", "status": "PASS",
                    "families_checked": 3, "nonzero_chain_terms": nonzero_terms})


def test_photo_ledger_and_curvature():
    f, chi = Q(83, 1000), (Q(68, 5), Q(123, 5), Q(272, 5))
    gas = (Q(3, 5), Q(1, 5), Q(2, 5), Q(15))
    s, inv = energy_transform(f, chi)
    check(matmul(s, inv) == tuple(tuple(I(int(i == j)) for j in range(4))
                                   for i in range(4)), "S inverse")
    q = Q(17, 31)
    check(dot(s[3], (q, 0, 0, -chi[0] * q)) == I(0), "HH direct energy zero")
    # All He channels active, unlike the actual archived 33-group seed spectrum.
    groups = ((Q(1, 20), 70, (Q(3, 10), Q(2, 10), Q(1, 10))),
              (Q(2, 25), 90, (Q(1, 5), Q(3, 10), Q(2, 5))))
    directions = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0),
                  (0, 0, 0, 1), (1, -2, 3, -4), (-3, 2, 1, 5))
    plus_and_minus_mixed = set()
    for n, energy, sig in groups:
        z = photo_energy_component(gas, n, energy, sig, Q(2, 7), f, Q(3, 2), chi)
        check(z["energy_ledger"] == energy * z["kappa"], "H+He photo energy ledger")
        check(Q(3, 2) * z["phi"] == energy * (n - z["photon"]), "BE photon energy identity")
        for u in directions:
            aa = sum(a * b for a, b in zip(z["alpha"], u))
            contraction = sum(u[i] * z["hessian"][i][j] * u[j]
                              for i in range(4) for j in range(4))
            check(contraction == -z["negative_rank_one_weight"] * aa * aa,
                  "negative square factorization")
            check(contraction <= 0, "same-direction concavity")
            # Independent formal quotient division: p(t)=κ(t)/D(t).
            # D0 p0=κ0, D0 p1+D1 p0=αu, D0 p2+D1 p1=0.
            p0 = z["kappa"] / z["denominator"]
            d1 = Q(3, 2) * aa
            p1 = (aa - d1 * p0) / z["denominator"]
            p2 = -d1 * p1 / z["denominator"]
            check(n * energy * p1 == sum(g * d for g, d in zip(z["gradient"], u)),
                  "quotient series first coefficient")
            check(2 * n * energy * p2 == contraction, "quotient series second coefficient")
        u = (1, 0, 0, 0)
        for v in (u, tuple(-x for x in u)):
            value = sum(u[i] * z["hessian"][i][j] * v[j] for i in range(4) for j in range(4))
            plus_and_minus_mixed.add(1 if value > 0 else -1 if value < 0 else 0)
    check(plus_and_minus_mixed == {-1, 1}, "mixed directions have both signs")
    reject(lambda: photo_energy_component(gas, -1, 70, (1, 1, 1), 1, f, 1, chi),
           "negative primal photon count")
    reject(lambda: photo_energy_component((1, 1, 1, 2), 1, 70, (1, 1, 1), 1, f, 1, chi),
           "invalid helium simplex")
    RESULTS.append({"name": "energy_ledger_and_helium_curvature", "status": "PASS",
                    "groups_with_all_channels": len(groups), "signed_directions": len(directions),
                    "mixed_directions_signs": sorted(plus_and_minus_mixed)})


def test_finite_scope_counterexample_and_observable():
    # y=λb−2λ²b: W(0,0)=1 but finite unit-rectangle interaction is −1.
    la, bb = Poly.var(2), Poly.var(3)
    y = la * bb - 2 * la * la * bb
    w = y.derivative(2).derivative(3)
    corners = [y.evaluate((0, 0, l, b)) for l, b in ((1, 1), (1, 0), (0, 1), (0, 0))]
    interaction = corners[0] - corners[1] - corners[2] + corners[3]
    check(w.evaluate((0, 0, 0, 0)) == 1 and interaction == -1,
          "point mixed sign is not finite rectangle sign")
    bound = finite_rectangle([I(-3, 1)], domain())
    check(bound[0].contains(interaction), "whole rectangle valid enclosure")
    # Nonlinear observable O=y², y=λ+b has W=0, but O_ab=2.
    obs = observable_mixed([I(0, 4)], [[2]], [1], [1], [0])
    check(obs == I(2), "observable Hessian term retained")
    small = replace(domain(), theta=(I(Q(1, 4), Q(3, 4)), I(Q(1, 3), Q(2, 3))))
    check(finite_rectangle([I(2, 3)], small) == (I(Q(1, 3), Q(1, 2)),), "rectangle area scaling")
    RESULTS.append({"name": "point_sign_counterexample_and_observable", "status": "PASS",
                    "point_W": "1", "finite_interaction": "-1", "observable_W": "2"})


def test_paired_cancellation():
    # A_F=A_T=1. W_F=10^6+θ and W_T=10^6+θ+10^-6, θ∈[0,1].
    # Joint Δf=10^-6 is an exact analytic bound; it is not guessed from boxes.
    d = domain()
    eps = Q(1, 10**6)
    wf, wt = I(10**6, 10**6 + 1), I(Q(10**6) + eps, Q(10**6 + 1) + eps)
    naive = wt - wf
    paired = paired_linear_difference([[1]], [[1]], [[0]], [eps], [wf], [1], d, d,
                                      center=[eps])
    exact = paired["difference"].enclosure[0]
    check(exact == I(eps), "joint paired delta exact")
    check(naive.width == 2 and naive.lo < 0 < naive.hi, "independent subtraction loses sign")
    check(paired["rectangle_difference"][0] == I(eps), "paired finite area")
    RESULTS.append({"name": "paired_shared_parameter_cancellation", "status": "PASS",
                    "independent_box": naive.json(), "joint_delta_box": exact.json(),
                    "scope": "analytic witness only; actual HH delta bounds absent"})


def test_rejections():
    d = domain()
    root = lambda **kw: uniform_root_arithmetic(kw.get("gc", [0]), kw.get("a", [[1]]),
        kw.get("c", [[1]]), [0], kw.get("r", [1]), kw.get("d", d))
    reject(lambda: root(a=[[3]]), "q >= 1")
    reject(lambda: root(gc=[1]), "strict inclusion equality")
    reject(lambda: root(r=[0]), "zero radius")
    reject(lambda: root(c=[[I(Q(9, 10), Q(11, 10))]]), "interval preconditioner")
    reject(lambda: root(d=replace(d, coverage="POINT_ONLY")), "point coverage")
    reject(lambda: root(d=replace(d, source_revision="")), "missing source binding")
    reject(lambda: root(d=replace(d, admissibility_assumption=False)), "missing admitted domain")
    reject(lambda: root(d=replace(d, smoothness_assumption="UNKNOWN")), "missing C2")
    reject(lambda: finite_rectangle([I(-1, 1)], replace(d, theta=(I(0), I(0, 1)))),
           "degenerate coverage")
    reject(lambda: finite_rectangle([I(0, 1)], d, (I(0, 2), I(0, 1))), "wrong rectangle")
    reject(lambda: paired_linear_difference([[1]], [[1]], [[0]], [0], [1], [1], d,
                                            replace(d, common_seed_id="other")), "different seed")
    reject(lambda: paired_linear_difference([[1]], [[1]], [[0]], [0], [1], [1], d,
                                            replace(d, terminal_time_id="other")), "different terminal time")
    reject(lambda: mixed_forcing([0], [[0, 0]], [[0]], [[[0]]], [0], [0]), "malformed Hessian dimensions")
    RESULTS.append({"name": "invalid_prerequisites_rejected", "status": "PASS"})


def main():
    for test in (test_interval_and_preconditioning, test_uniform_nonlinear_family,
                 test_all_implicit_chain_terms, test_photo_ledger_and_curvature,
                 test_finite_scope_counterexample_and_observable, test_paired_cancellation,
                 test_rejections):
        test()
        print(test.__name__ + ": PASS", flush=True)
    payload = {"schema": "WU088_HH_PHYS06_REFERENCE_CHECK_V1", "status": "PASS",
        "arithmetic": "exact Fraction; independent integer radical enclosures and polynomial oracle",
        "counts": COUNTS, "cases": RESULTS, "native_endpoint_runs": 0,
        "native_root_runs": 0, "IVP_runs": 0, "historical_suite_replays": 0,
        "actual_HH_W": None, "actual_HH_I": None, "native_authority": False}
    (ROOT / "evidence" / "reference_checks.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "PASS", **COUNTS, "case_groups": len(RESULTS)}))


if __name__ == "__main__":
    main()
