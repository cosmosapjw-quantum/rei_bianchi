"""Frozen two-coefficient GLS and deterministic-box confidence union.

Decimal source entries are interpreted exactly via Fraction(str(value)). Small
positive definite systems use exact LDL solves; floating Cholesky/whitened-rank
checks separately enforce the numerical prerequisites. No covariance is dropped,
no jitter/pseudoinverse or estimated residual-variance scaling is used.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
BLIND = UNIT / "intake/BLIND_SOURCE.json"
ORIGINAL = REPO / "research/rei_uvb_eos_jeans_box_20261029/source/FROZEN_BB13_SUPPORT_INPUT.json"
BLIND_SHA = "6e72099e6d3981ac731d5bed5ed70f6dabaa1514b7283613f3c258c4ec57e224"
ORIGINAL_SHA = "13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b"
CONTRACT_SHA = "0eb1134b7ff1f4554789d391e70ae0d24804f7f0fefe840cfa5f24012e48bcd1"
RTOL, ATOL = 1e-10, 1e-12


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_blob(blob, expected):
    if hashlib.sha256(blob).hexdigest() != expected:
        raise ValueError("BYTE_IDENTITY_MISMATCH: frozen immutable source")


def load_source():
    verify_blob(BLIND.read_bytes(), BLIND_SHA)
    verify_blob(ORIGINAL.read_bytes(), ORIGINAL_SHA)
    verify_blob((UNIT / "review/THEORY_CONTRACT.json").read_bytes(), CONTRACT_SHA)
    obj = json.loads(BLIND.read_text())
    if obj["conventions"]["source_sha256"] != ORIGINAL_SHA:
        raise ValueError("declared original source identity mismatch")
    if len(obj["z"]) != 7 or obj["eos_theta_bounds"] != [-1, 1]:
        raise ValueError("frozen seven-row/theta convention mismatch")
    return obj


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), F(0))


def transpose(a):
    return [list(c) for c in zip(*a)]


def mv(a, x):
    return [dot(row, x) for row in a]


def mm(a, b):
    return [[dot(row, col) for col in transpose(b)] for row in a]


def vec(values):
    try:
        if not all(math.isfinite(float(x)) for x in values):
            raise ValueError("nonfinite input")
        return [F(str(x)) for x in values]
    except (TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError("invalid finite numeric vector") from exc


class LDL:
    """Exact positive-definite factorization and solves, without forming C^-1."""
    def __init__(self, a):
        n = len(a)
        self.l = [[F(int(i == j)) for j in range(n)] for i in range(n)]
        self.d = []
        for i in range(n):
            di = a[i][i] - sum((self.l[i][k] ** 2 * self.d[k] for k in range(i)), F(0))
            if di <= 0:
                raise ValueError("matrix is not positive definite (no jitter)")
            self.d.append(di)
            for j in range(i + 1, n):
                self.l[j][i] = (a[j][i] - sum((self.l[j][k] * self.l[i][k] * self.d[k] for k in range(i)), F(0))) / di

    def solve(self, b):
        n = len(self.d)
        y = []
        for i in range(n):
            y.append(b[i] - dot(self.l[i][:i], y))
        x = [y[i] / self.d[i] for i in range(n)]
        for i in reversed(range(n)):
            x[i] -= sum((self.l[j][i] * x[j] for j in range(i + 1, n)), F(0))
        return x


def numerical_prerequisites(c, x):
    """Unjittered float Cholesky, forward whitening, two-column rank check."""
    n = len(c)
    l = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            v = float(c[i][j]) - math.fsum(l[i][k] * l[j][k] for k in range(j))
            if i == j:
                if v <= 0:
                    raise ValueError("numerical Cholesky failed; no jitter")
                l[i][j] = math.sqrt(v)
            else:
                l[i][j] = v / l[j][j]
    cols = []
    for col in ([F(1)] * n, x):
        w = []
        for i in range(n):
            w.append((float(col[i]) - math.fsum(l[i][k] * w[k] for k in range(i))) / l[i][i])
        cols.append(w)
    norm0 = math.sqrt(math.fsum(v * v for v in cols[0]))
    q0 = [v / norm0 for v in cols[0]]
    projection = math.fsum(a * b for a, b in zip(q0, cols[1]))
    residual = [v - projection * u for v, u in zip(cols[1], q0)]
    # Reorthogonalize to reduce cancellation, retaining the same rank decision.
    correction = math.fsum(a * b for a, b in zip(q0, residual))
    residual = [v - correction * u for v, u in zip(residual, q0)]
    norm1 = math.sqrt(math.fsum(v * v for v in residual))
    scale = max(norm0, math.sqrt(math.fsum(v * v for v in cols[1])))
    rank_threshold = max(n, 2) * math.ulp(1.0) * scale
    if norm1 <= rank_threshold:
        raise ValueError("whitened design numerical rank is below two")
    return {"cholesky": "PASS_NO_JITTER", "whitened_design_rank": 2,
            "whitened_qr_diagonal": [norm0, norm1], "rank_threshold": rank_threshold,
            "exact_ldl_positive_pivots": True}


class Model:
    def __init__(self, source):
        z = vec(source["z"])
        self.n = len(z)
        if self.n < 2:
            raise ValueError("at least two rows required")
        self.x = [v - F("3.6") for v in z]
        self.X = [[F(1), x] for x in self.x]
        self.d, self.m, self.v, self.lower, self.upper = [vec(source[key]) for key in
            ("observed_dex", "template_dex", "eos_response_dex", "jeans_smoothing_lower_dex", "jeans_smoothing_upper_dex")]
        if any(len(v) != self.n for v in (self.d, self.m, self.v, self.lower, self.upper)):
            raise ValueError("input vector dimension mismatch")
        if source.get("eos_theta_bounds", [-1, 1]) != [-1, 1]:
            raise ValueError("theta domain must be [-1,1]")
        if any(lo > hi for lo, hi in zip(self.lower, self.upper)):
            raise ValueError("reversed nuisance interval")
        self.C = [vec(row) for row in source["covariance_dex_squared"]]
        if len(self.C) != self.n or any(len(row) != self.n for row in self.C):
            raise ValueError("covariance dimension mismatch")
        if self.C != transpose(self.C):
            raise ValueError("covariance must be symmetric")
        self.factor = LDL(self.C)
        self.prerequisites = numerical_prerequisites(self.C, self.x)
        wx = [self.factor.solve(col) for col in transpose(self.X)]
        self.H = mm(transpose(self.X), transpose(wx))
        hf = LDL(self.H)
        self.V = transpose([hf.solve([F(int(i == j)) for i in range(2)]) for j in range(2)])
        self.A = mm(self.V, wx)
        self.a0 = mv(self.A, [d - m for d, m in zip(self.d, self.m)])
        self.g = mv(self.A, self.v)
        self.jc = [(lo + hi) / 2 for lo, hi in zip(self.lower, self.upper)]
        self.jh = [(hi - lo) / 2 for lo, hi in zip(self.lower, self.upper)]
        shift = mv(self.A, self.jc)
        self.center = [a + b for a, b in zip(self.a0, shift)]
        self.G = [[self.g[k]] + [self.A[k][i] * self.jh[i] for i in range(self.n)] for k in range(2)]

    def response(self, theta, j):
        return [d - m + theta * v + ji for d, m, v, ji in zip(self.d, self.m, self.v, j)]

    def fit(self, theta, j):
        return mv(self.A, self.response(theta, j))

    def q_residual(self, response, coefficients):
        residual = [r - p for r, p in zip(response, mv(self.X, coefficients))]
        return dot(residual, self.factor.solve(residual))

    def nested(self, theta, j):
        r = self.response(theta, j)
        wr = self.factor.solve(r)
        w1 = self.factor.solve([F(1)] * self.n)
        b0 = sum(wr) / sum(w1)
        q0 = self.q_residual(r, [b0, F(0)])
        a = mv(self.A, r)
        q2 = self.q_residual(r, a)
        return q0, q2, a

    def support(self, s):
        s = vec(s)
        if len(s) != 2:
            raise ValueError("direction must have dimension two")
        return dot(s, self.center) + sum((abs(dot(s, col)) for col in transpose(self.G)), F(0))

    def nuisance_witness(self, s):
        s = vec(s)
        if len(s) != 2:
            raise ValueError("direction must have dimension two")
        t = dot(s, self.g)
        theta = F((t > 0) - (t < 0))
        j = [hi if dot(s, col) > 0 else lo if dot(s, col) < 0 else mid
             for col, lo, hi, mid in zip(transpose(self.A), self.lower, self.upper, self.jc)]
        return {"theta": theta, "j": j, "fit": self.fit(theta, j)}

    def deterministic_intervals(self):
        return [[c - sum(map(abs, row)), c + sum(map(abs, row))] for c, row in zip(self.center, self.G)]

    def confidence_witness(self, s, q):
        if not isinstance(q, (int, float, F)) or not math.isfinite(float(q)) or q < 0:
            raise ValueError("q must be finite and nonnegative")
        s = vec(s)
        witness = self.nuisance_witness(s)
        vs = mv(self.V, s)
        svs = dot(s, vs)
        radius = math.sqrt(float(q) * float(svs))
        delta = [0.0, 0.0] if not svs or not q else [math.sqrt(float(q)) * float(v) / math.sqrt(float(svs)) for v in vs]
        endpoint = [float(a) + b for a, b in zip(witness["fit"], delta)]
        return {"direction": s, "q": q, "nuisance": witness,
                "ellipsoid_displacement": delta, "endpoint": endpoint,
                "deterministic_support": self.support(s), "gaussian_support_radius": radius,
                "union_support": float(self.support(s)) + radius}

    def projections(self, q):
        # Validation shares the confidence support path, including q=0.
        self.confidence_witness([0, 0], q)
        return [[float(lo) - math.sqrt(float(q) * float(self.V[k][k])),
                 float(hi) + math.sqrt(float(q) * float(self.V[k][k]))]
                for k, (lo, hi) in enumerate(self.deterministic_intervals())]

    def delta_q_range(self):
        low = self.nuisance_witness([0, -1])
        high = self.nuisance_witness([0, 1])
        lo, hi = low["fit"][1], high["fit"][1]
        if lo <= 0 <= hi:
            # Exact convex nuisance interpolation, including degenerate [0,0].
            weight = F(0) if lo == hi else -lo / (hi - lo)
            theta = (1 - weight) * low["theta"] + weight * high["theta"]
            j = [(1 - weight) * a + weight * b for a, b in zip(low["j"], high["j"])]
            minimum = {"theta": theta, "j": j, "fit": self.fit(theta, j)}
        else:
            minimum = low if abs(lo) <= abs(hi) else high
        maximum = low if abs(lo) >= abs(hi) else high
        return {"range": [minimum["fit"][1] ** 2 / self.V[1][1], maximum["fit"][1] ** 2 / self.V[1][1]],
                "minimum_nuisance": minimum, "maximum_nuisance": maximum,
                "zero_in_slope_interval": lo <= 0 <= hi,
                "interpretation": "Pointwise nested improvement at identical nuisance; no calibrated global significance"}


def quantiles():
    return {"scalar95": {"q": NormalDist().inv_cdf(.975) ** 2, "degrees_of_freedom": 1,
                         "coverage": "at least 95% for one pre-specified scalar coordinate after nuisance union; not joint2"},
            "joint2_95": {"q": -2 * math.log(.05), "degrees_of_freedom": 2,
                          "coverage": "at least 95% for full (b,kappa) after nuisance union"}}


def numeric(value):
    if isinstance(value, F):
        return float(value)
    if isinstance(value, dict):
        return {k: numeric(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [numeric(v) for v in value]
    return value


def build_result(model, test_evidence):
    qs = quantiles()
    intervals = {"deterministic": model.deterministic_intervals()}
    for name, item in qs.items():
        intervals[name] = model.projections(item["q"])
    directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, -2], [-1, 2], [0, 0]]
    witnesses = {"deterministic": [model.confidence_witness(s, 0) for s in directions]}
    for name, item in qs.items():
        witnesses[name] = [model.confidence_witness(s, item["q"]) for s in directions]
    return numeric({"schema": "REI_UVB_CONFIDENCE_UNION_RESULT_V1", "status": "COMPUTED_PENDING_INDEPENDENT_REVIEW",
        "provenance": {"source": "frozen seven-row BLIND_SOURCE; original SHA verified; no primary table reacquisition",
                       "blind_source_sha256": BLIND_SHA, "original_source_sha256": ORIGINAL_SHA,
                       "theory_contract_sha256": CONTRACT_SHA,
                       "toys": "separate analytic three-row and two-row controls, never source observations"},
        "coordinate_order": ["b", "kappa"], "units": ["dex", "dex per redshift"],
        "prerequisites": model.prerequisites, "A": model.A, "V": model.V, "a0": model.a0,
        "g": model.g, "center": model.center, "G": model.G, "coordinate_intervals": intervals,
        "quantiles": qs, "endpoint_witnesses": witnesses, "deltaQ": model.delta_q_range(),
        "positive_slope": {"deterministic": intervals["deterministic"][1][0] > 0,
                           "conditional_scalar95": intervals["scalar95"][1][0] > 0,
                           "conditional_joint2_95": intervals["joint2_95"][1][0] > 0,
                           "criterion": "corresponding lower kappa bound > 0; scalar and joint assumptions apply"},
        "coverage_assumptions": ["d=m+X*a_star-theta_star*v-j_star+epsilon; epsilon~N(0,C)",
            "true nuisance lies in fixed H; C known and fixed; X,m,v,H fixed or legitimately conditioned independently of epsilon",
            "additive affine mean correctly specified; no unmodeled template discrepancy"],
        "claim_limits": ["Gaussian sampling assumptions are additional conditions, not established by covariance alone",
            "union coverage can exceed 95%; scalar95 does not establish joint2 coverage",
            "no probability prior on nuisance box; no residual-variance scaling",
            "source correction relative to frozen template, no new IVP or physical closure", "coordinate extrema need not share one nuisance witness"],
        "test_evidence": test_evidence,
        "figures": "NOT_RUN_BUDGET_DEPENDENCY: presentation allowance zero",
        "budget_scope": "main source-analysis; no planning/presentation debit transfer; historical UNKNOWN_NOT_ZERO retained"})
