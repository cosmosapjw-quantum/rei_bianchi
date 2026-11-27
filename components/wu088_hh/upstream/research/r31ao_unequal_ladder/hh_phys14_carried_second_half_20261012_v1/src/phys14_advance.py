#!/usr/bin/env python3
"""PHYS14: one source-aligned, isotropic, carried second-half family.

All enclosures use exact rational input endpoints and directed dyadic rounding.
No native root, atomic source callback, new grid, or history restart is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import struct
import time
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q

BITS = 256
ROOT = pathlib.Path(__file__).resolve().parents[1]
SLOTS = ("value", "U", "V", "W")
COORDS = ("x_HII", "y_HeII", "y_HeIII", "w_eV_per_H")


def dyadic(x: Q, upward: bool) -> Q:
    """Round to BITS significant binary digits, with unbounded exponent."""
    if not x:
        return Q(0)
    a = abs(x)
    k = a.numerator.bit_length() - a.denominator.bit_length()
    if (a.numerator < (a.denominator << k)) if k >= 0 else ((a.numerator << -k) < a.denominator):
        k -= 1
    e = k - BITS + 1
    unit = Q(1 << e) if e >= 0 else Q(1, 1 << -e)
    z = x / unit
    n = -((-z.numerator) // z.denominator) if upward else z.numerator // z.denominator
    return n * unit


class I:
    __slots__ = ("lo", "hi")

    def __init__(self, lo=0, hi=None):
        if isinstance(lo, I):
            self.lo, self.hi = lo.lo, lo.hi
            return
        lo, hi = Q(lo), Q(lo if hi is None else hi)
        assert lo <= hi, "unordered interval"
        self.lo, self.hi = dyadic(lo, False), dyadic(hi, True)

    def __add__(self, other):
        other = I(other)
        return I(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -I(other)

    def __rsub__(self, other):
        return I(other) + -self

    def __mul__(self, other):
        other = I(other)
        p = [self.lo * other.lo, self.lo * other.hi,
             self.hi * other.lo, self.hi * other.hi]
        return I(min(p), max(p))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I(other)
        assert not other.lo <= 0 <= other.hi, "interval division by zero"
        return self * I(1 / other.hi, 1 / other.lo)

    def __rtruediv__(self, other):
        return I(other) / self

    def __pow__(self, n):
        assert isinstance(n, int) and n >= 0
        if n == 0:
            return I(1)
        if n % 2 == 0:
            ends = [self.lo ** n, self.hi ** n]
            return I(0 if self.lo <= 0 <= self.hi else min(ends), max(ends))
        return I(self.lo ** n, self.hi ** n)

    def meet(self, other):
        other = I(other)
        return I(max(self.lo, other.lo), min(self.hi, other.hi))

    def mag(self):
        return max(abs(self.lo), abs(self.hi))

    def within(self, other, strict=False):
        other = I(other)
        return (other.lo < self.lo and self.hi < other.hi) if strict else (other.lo <= self.lo and self.hi <= other.hi)

    def contains_zero(self):
        return self.lo <= 0 <= self.hi


def exact_bits(s):
    return Q(struct.unpack(">d", bytes.fromhex(s))[0])


def from_raw(d):
    if "exact" in d:
        e = d["exact"]
        return I(Q(*map(int, e["lo"])), Q(*map(int, e["hi"])))
    return I(exact_bits(d["lo_bits"]), exact_bits(d["hi_bits"]))


def dec(x, rounding, precision=13):
    with localcontext() as c:
        c.prec, c.rounding = precision, rounding
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def out(x):
    if isinstance(x, I):
        return {"exact": {"lo": [str(x.lo.numerator), str(x.lo.denominator)],
                          "hi": [str(x.hi.numerator), str(x.hi.denominator)]},
                "outward_decimal": [dec(x.lo, ROUND_FLOOR), dec(x.hi, ROUND_CEILING)],
                "sign": "STRICT_POSITIVE" if x.lo > 0 else "STRICT_NEGATIVE" if x.hi < 0 else "EXACT_ZERO" if x.lo == x.hi == 0 else "ZERO_CONTAINING"}
    if isinstance(x, Q):
        return out(I(x))
    if isinstance(x, dict):
        return {str(k): out(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [out(v) for v in x]
    return x


def short(x):
    z = out(x)
    if isinstance(x, I):
        return z["outward_decimal"]
    if isinstance(x, dict):
        return {k: short(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [short(v) for v in x]
    return x


def read(rel):
    return json.loads((ROOT / "inputs" / rel).read_text())


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), I(0))


def matvec(a, v):
    return [dot(row, v) for row in a]


def vadd(a, b):
    return [x + y for x, y in zip(a, b)]


def scale(c, v):
    return [c * x for x in v]


def jet(raw):
    return {"value": from_raw(raw["value"]),
            "g": [from_raw(x) for x in raw["gradient"][:4]],
            "gg": [[from_raw(x) for x in row[:4]] for row in raw["signed_hessian"][:4]]}


def taylor_jet(whole, centre, delta):
    # The segment from the captured centre to each Z is inside convex X.
    return {"value": whole["value"].meet(centre["value"] + dot(whole["g"], delta)),
            "g": [whole["g"][j].meet(centre["g"][j] + dot(whole["gg"][j], delta)) for j in range(4)],
            "gg": whole["gg"]}


def exp_minus_enclosure(z, degree=14):
    assert 0 <= z < 1 and degree % 2 == 0
    term, even = Q(1), Q(1)
    for k in range(1, degree + 1):
        term *= -z / k
        even += term
    odd = even + term * -z / (degree + 1)
    assert odd <= even
    return I(odd, even)


def read_binary_value(blob, header_words, jet_index):
    off = (header_words + 114 * jet_index) * 8
    lo, hi = struct.unpack_from("<dd", blob, off)
    assert math.isfinite(lo) and math.isfinite(hi) and lo <= hi
    return I(Q(lo), Q(hi))


def transport(vec, guard_n, guard_u, energies, rho):
    result = [I(0) for _ in energies]
    gn, gu = guard_n, rho * guard_u
    for j, (en, n) in enumerate(zip(energies, vec)):
        en_new = rho * en
        if en_new.hi < energies[0]:
            gn, gu = gn + n, gu + en_new * n
        else:
            assert j >= 1 and en_new.lo > energies[j - 1] and en_new.hi < en
            a = (en - en_new) / (en - energies[j - 1])
            assert a.lo > 0 and a.hi < 1
            result[j - 1] += a * n
            result[j] += (1 - a) * n
    return result, gn, gu


class Source:
    def __init__(self, box, comp, centre, ccomp, native, incoming, h, X, z0):
        self.np = [jet(j) for j in comp["nonphoto"]]
        self.npc = [jet(j) for j in ccomp["nonphoto"]]
        self.q, self.qc = jet(box["q"]), jet(centre["q"])
        self.nH = I(exact_bits(box["nH_bits"]))
        self.f = I(exact_bits(box["fHe_bits"]))
        self.fhat = I(exact_bits(box["nHe_stored_bits"])) / self.nH
        self.H = I(exact_bits(box["Hmean_bits"]))
        self.chi = I(exact_bits(native["CHI_bits"][0]))
        self.C = 2 * I(exact_bits(native["ev_erg_bits"])) / (3 * I(exact_bits(native["kb_bits"])))
        self.energy = [exact_bits(s) for s in box["energy_bits"]]
        self.a = [I(exact_bits(native["c_bits"])) * self.nH * exact_bits(s[0]) for s in box["sigma_bits"]]
        self.heat = [I(exact_bits(s[0])) for s in box["heat_bits"]]
        self.active = [j for j, a in enumerate(self.a) if a.hi > 0]
        assert self.active == list(range(16, 33))
        assert all(exact_bits(s[1]) == exact_bits(s[2]) == 0 for s in box["sigma_bits"])
        self.N, self.h, self.X, self.z0 = incoming, h, X, z0
        self.hh = [I(1), I(0), I(0), -self.chi]

    def evaluate(self, Z, tighten=True):
        assert all(z.within(x) for z, x in zip(Z, self.X))
        delta = [z - zc for z, zc in zip(Z, self.z0)]
        np = [taylor_jet(j, jc, delta) for j, jc in zip(self.np, self.npc)] if tighten else self.np
        q = taylor_jet(self.q, self.qc, delta) if tighten else self.q
        la = I(0, 1)
        F = [np[i]["value"] + la * q["value"] * self.hh[i] for i in range(4)]
        J = [[np[i]["g"][k] + la * q["g"][k] * self.hh[i] for k in range(4)] for i in range(4)]
        H = [[[np[i]["gg"][k][l] + la * q["gg"][k][l] * self.hh[i] for l in range(4)] for k in range(4)] for i in range(4)]
        direct_u = scale(q["value"], self.hh)
        memory_u, Fb, Fulb = [I(0) for _ in range(4)], [I(0) for _ in range(4)], [I(0) for _ in range(4)]
        Jla = [[q["g"][k] * self.hh[i] for k in range(4)] for i in range(4)]
        Jb = [[I(0) for _ in range(4)] for _ in range(4)]
        Kdata = []
        for j, a in enumerate(self.a):
            D = 1 + self.h * a * (1 - Z[0])
            assert D.lo > 0
            K = a * (1 - Z[0]) / D
            Kp = -a / D ** 2
            Kpp = -2 * self.h * a ** 2 / D ** 3
            Kdata.append((D, K, Kp, Kpp))
            for i, coeff in ((0, I(1)), (3, self.heat[j])):
                F[i] += coeff * K * self.N["value"][j]
                J[i][0] += coeff * Kp * self.N["value"][j]
                H[i][0][0] += coeff * Kpp * self.N["value"][j]
                memory_u[i] += coeff * K * self.N["U"][j]
                Fb[i] += coeff * K * self.N["V"][j]
                Fulb[i] += coeff * K * self.N["W"][j]
                Jla[i][0] += coeff * Kp * self.N["U"][j]
                Jb[i][0] += coeff * Kp * self.N["V"][j]
        F[3] -= 2 * self.H * Z[3]
        J[3][3] -= 2 * self.H
        return {"F": F, "Fg": J, "Fgg": H, "F_lambda": vadd(direct_u, memory_u),
                "F_b": Fb, "F_g_lambda": Jla, "F_g_b": Jb, "F_lambdab": Fulb,
                "q": q, "nonphoto": np, "direct_HH": direct_u,
                "photon_memory_HH": memory_u, "kernels": Kdata}


def contraction(L, scales):
    rows = [sum((I(L[i][j].mag()) * scales[j] / scales[i] for j in range(4)), I(0)) for i in range(4)]
    return max(row.hi for row in rows), rows


def neumann(L, rhs, scales, q, degree=8):
    assert 0 <= q < 1
    total, term = list(rhs), list(rhs)
    for _ in range(degree):
        term = matvec(L, term)
        total = vadd(total, term)
    bnorm = max((I(v.mag()) / s).hi for v, s in zip(rhs, scales))
    tail0 = (I(q) ** (degree + 1) * bnorm / (1 - I(q))).hi
    tails = [I(s * tail0).hi for s in scales]
    value = [v + I(-t, t) for v, t in zip(total, tails)]
    return value, {"degree": degree, "scaled_rhs_norm_upper": I(bnorm),
                   "contraction_upper": I(q), "absolute_tail": [I(0, t) for t in tails]}


def readouts(g, U, V, W, source):
    f, C = source.fhat, source.C
    e = g[0] + f * (g[1] + 2 * g[2])
    p = 1 + f + e
    w = g[3]
    T = C * w / p
    def em(z):
        return z[0] + f * (z[1] + 2 * z[2])
    ue, ve, we = em(U), em(V), em(W)
    ut = C * (U[3] / p - w * ue / p ** 2)
    vt = C * (V[3] / p - w * ve / p ** 2)
    wt = C * (W[3] / p - U[3] * ve / p ** 2 - V[3] * ue / p ** 2
              - w * we / p ** 2 + 2 * w * ue * ve / p ** 3)
    Tg = [-C * w / p ** 2, -C * w * f / p ** 2, -2 * C * w * f / p ** 2, C / p]
    return {"value": {"electron_per_H": e, "particle_per_H": p, "temperature_K": T,
                       "electron_density_cm3": source.nH * e, "thermal_eV_per_H": w},
            "U": {"electron_per_H": ue, "temperature_K": ut, "electron_density_cm3": source.nH * ue, "thermal_eV_per_H": U[3]},
            "V": {"electron_per_H": ve, "temperature_K": vt, "electron_density_cm3": source.nH * ve, "thermal_eV_per_H": V[3]},
            "W": {"electron_per_H": we, "temperature_K": wt, "electron_density_cm3": source.nH * we, "thermal_eV_per_H": W[3]},
            "temperature_gradient": Tg}


def outgoing_carry(source, g, U, V, W, evaluated):
    photons, absorbed = {s: [] for s in SLOTS}, {s: [] for s in SLOTS}
    for j, (D, K, Kp, Kpp) in enumerate(evaluated["kernels"]):
        n, nu, nv, nw = [source.N[s][j] for s in SLOTS]
        a, h = source.a[j], source.h
        z = n / D
        zu = nu / D + h * a * n * U[0] / D ** 2
        zv = nv / D + h * a * n * V[0] / D ** 2
        zw = nw / D + h * a * (nu * V[0] + nv * U[0] + n * W[0]) / D ** 2 + 2 * (h * a) ** 2 * n * U[0] * V[0] / D ** 3
        ab = [h * K * n,
              h * (K * nu + Kp * n * U[0]),
              h * (K * nv + Kp * n * V[0]),
              h * (K * nw + Kp * (nu * V[0] + nv * U[0] + n * W[0]) + Kpp * n * U[0] * V[0])]
        for s, zslot, abslot in zip(SLOTS, (z, zu, zv, zw), ab):
            photons[s].append(zslot)
            absorbed[s].append(abslot)
            assert (source.N[s][j] - zslot - abslot).contains_zero()
    return photons, absorbed


def remap_defect(energies, rho, common):
    # Compute the operator difference first, then apply the SAME input interval.
    # This preserves the exact common-input cancellation absent in R(R(N))-R2(N).
    n = len(energies)
    d = [I(0) for _ in range(n)]
    columns = []
    a = [I(0)] + [(1 - rho) * energies[j] / (energies[j] - energies[j - 1]) for j in range(1, n)]
    for j in range(2, n):
        assert (rho ** 2 * energies[j]).lo > energies[j - 1]
        ratio = Q(energies[j - 1] - energies[j - 2], energies[j] - energies[j - 1])
        pref = a[j] * a[j - 1]
        co = [pref, -pref * (1 + ratio), pref * ratio]
        for k, c in zip((j - 2, j - 1, j), co):
            d[k] += c * common[j]
        columns.append({"input_node": j, "energy_eV": I(energies[j]), "a_j": a[j],
                        "affected_nodes": [j - 2, j - 1, j], "coefficients": co,
                        "L1": 2 * pref * (1 + ratio),
                        "number_moment": "exact zero by linked polynomial coefficients",
                        "energy_moment": "exact zero on captured nonuniform nodes"})
    d[1] += a[1] * (a[1] + rho - 1) * common[1]
    d[0] -= a[1] * (a[1] + rho) * common[1]
    gn, gu = a[1] * common[1], rho * energies[0] * a[1] * common[1]
    assert (sum(d, I(0)) + gn).contains_zero()
    assert (dot([I(e) for e in energies], d) + gu).contains_zero()
    active_delta = sum(d[16:], I(0))
    return {"comparison": "transport-only R(rho)^2 - R(rho^2), identical COMMON spectrum, absorption and birth excluded from this operator diagnostic",
            "rho": rho, "columns_j_ge_2": columns,
            "common_weighted_group_difference": d, "common_weighted_guard_number_difference": gn,
            "common_weighted_guard_energy_difference_eV_per_H": gu,
            "common_weighted_HI_active_photon_number_difference": active_delta,
            "max_column_L1_enclosure": I(max(c["L1"].lo for c in columns), max(c["L1"].hi for c in columns)),
            "moments": {"photon_number": "exact zero including lower guard", "energy": "exact zero including lower guard"},
            "endpoint_defect_attribution": "operator-level mechanism only; not total gas endpoint error or order evidence"}


def main(output_dir):
    started = time.time()
    box = read("ncp07/results/full/SOURCE_BOX.json")
    centre = read("ncp07/results/full/SOURCE_CENTRE.json")
    comp = read("ncp07/results/full/SOURCE_BOX_COMPONENTS.json")
    ccomp = read("ncp07/results/full/SOURCE_CENTRE_COMPONENTS.json")
    native = read("ncp07/results/full/NATIVE_CONSTANT_LEAVES.json")
    p9 = read("phys09/PROJECTED_RESULTS.json")
    p11 = read("phys11/CARRY_RESULTS.json")
    p13 = read("phys13/THERMO_RESULTS.json")
    stage9 = next(r for r in p9["stages"] if r["stage"] == "first_half")
    detail9 = next(r for r in p9["details"] if r["stage"] == "first_half")
    stage11 = next(r for r in p11["stages"] if r["stage"] == "first_half")
    stage13 = next(r for r in p13["rows"] if r["stage"] == "first_half")
    half_box = read("ncp07/results/first_half/SOURCE_BOX.json")
    prebe = read("ncp07/results/first_half/PREBE.json")
    X = [from_raw(r) for r in read("ncp07/results/full/C2_DOMAIN.json")["X"]]
    z0 = [from_raw(r) for r in detail9["Banach_ball_center"]]
    g1 = [from_raw(r) for r in stage13["root_image"]["intervals"]]
    U1, V1, W1 = [[from_raw(r) for r in stage9[s]] for s in ("U", "V", "W")]
    assert all(g.within(x, strict=True) for g, x in zip(g1, X))
    h = I(exact_bits(half_box["dt_bits"]))
    assert h.lo == h.hi == 625000000 and exact_bits(box["dt_bits"]) == 2 * h.lo
    input_blob = (ROOT / "inputs/ncp07/results/first_half/prebe_input_words.bin").read_bytes()
    input_header = struct.unpack_from("<5d", input_blob)
    assert len(input_blob) == 4090360 and input_header[:3] == (1e-14,) * 3
    Hgeom, t0 = Q(input_header[0]), Q(input_header[3])
    assert Q(input_header[4]) == h.lo and t0 == 160000000000
    assert t0 + 2 * h.lo == 161250000000
    rho = exp_minus_enclosure(Hgeom * h.lo)
    M = I(exact_bits(prebe["fl_dt_SOURCE_bits"]))
    energy = [exact_bits(x) for x in box["energy_bits"]]
    assert box["energy_bits"] == half_box["energy_bits"]
    for leaf in ("sigma_bits", "heat_bits", "fHe_bits", "Hmean_bits"):
        assert box[leaf] == half_box[leaf]
    for leaf in ("nH_bits", "nHe_stored_bits", "fHe_bits", "Hmean_bits", "energy_bits", "sigma_bits", "heat_bits"):
        assert box[leaf] == centre[leaf]
    previous = {s: [from_raw(row["outgoing_joint"][s]) for row in stage11["groups"]] for s in SLOTS}
    # The previous guard is untouched by future parameters before the first source.
    # Its raw signed Jet slots remain archived; exact derivative zero is structural.
    pre_blob = (ROOT / "inputs/ncp07/results/first_half/prebe_words.bin").read_bytes()
    assert len(pre_blob) == 4123688
    guard0n = sum((read_binary_value(pre_blob, 6, 4 + 4224 + r) for r in range(128)), I(0))
    guard0u = sum((read_binary_value(pre_blob, 6, 4 + 4224 + 128 + r) for r in range(128)), I(0))
    incoming, guard = {}, {}
    for s in SLOTS:
        mapped, gn, gu = transport(previous[s], guard0n if s == "value" else I(0), guard0u if s == "value" else I(0), energy, rho)
        if s == "value":
            mapped[24] += I(0, 1) * M
        elif s == "V":
            mapped[24] += M
        incoming[s] = mapped
        guard[s] = {"number": gn, "energy_eV_per_H": gu}
    # Nonnegative value cone is inherited; no signed derivative is clipped.
    assert all(v.lo >= 0 for v in incoming["value"])
    src = Source(box, comp, centre, ccomp, native, incoming, h, X, z0)
    whole = src.evaluate(X, tighten=False)
    P = vadd(g1, scale(h, whole["F"]))
    strict = [p.within(x, strict=True) for p, x in zip(P, X)]
    assert all(strict), "second-half image fails original X self-map"
    scales = [Q(1), Q(1), Q(1), Q(27, 2)]
    Lwhole = [scale(h, row) for row in whole["Fg"]]
    qwhole, qrows = contraction(Lwhole, scales)
    assert qwhole < 1, "second-half contraction fails"
    refinements = []
    Z = [x.meet(p) for x, p in zip(X, P)]
    for _ in range(4):
        fz = src.evaluate(Z)
        image = vadd(g1, scale(h, fz["F"]))
        Z = [z.meet(p) for z, p in zip(Z, image)]
        refinements.append(Z)
    F = src.evaluate(Z)
    L = [scale(h, row) for row in F["Fg"]]
    q, rows = contraction(L, scales)
    rhsU = vadd(U1, scale(h, F["F_lambda"]))
    rhsV = vadd(V1, scale(h, F["F_b"]))
    U, eu = neumann(L, rhsU, scales, q)
    V, ev = neumann(L, rhsV, scales, q)
    bilinear = [sum((F["Fgg"][i][j][k] * U[j] * V[k] for j in range(4) for k in range(4)), I(0)) for i in range(4)]
    wterms = {"F_gg_U_V": bilinear, "F_g_lambda_V": matvec(F["F_g_lambda"], V),
              "F_g_b_U": matvec(F["F_g_b"], U), "F_lambdab_incoming": F["F_lambdab"]}
    rhsW = vadd(W1, scale(h, [sum((v[i] for v in wterms.values()), I(0)) for i in range(4)]))
    W, ew = neumann(L, rhsW, scales, q)
    ro = readouts(Z, U, V, W, src)
    decompositions = {}
    for name, rhs in (("inherited_gas", U1), ("direct_second_half_HH", scale(h, F["direct_HH"])),
                      ("inherited_photon_memory", scale(h, F["photon_memory_HH"]))):
        du, proof = neumann(L, rhs, scales, q)
        decompositions[name] = {"gas_U": du, "temperature_U_K": dot(ro["temperature_gradient"], du),
                                "electron_U_per_H": du[0] + src.fhat * (du[1] + 2 * du[2]),
                                "linear_tail": proof}
    nout, absorbed = outgoing_carry(src, Z, U, V, W, F)
    common = [sum((read_binary_value(input_blob, 5, 4 + r * 33 + j) for r in range(128)), I(0)) for j in range(33)]
    remap = remap_defect(energy, rho, common)
    finite = {"HH_lambda_0_to_1_at_fixed_b": ro["U"],
              "birth_b_0_to_1_at_fixed_lambda": ro["V"],
              "rectangle_interaction_11_minus_10_minus_01_plus_00": ro["W"],
              "proof": "C2 uniform family; one-dimensional FTC for U,V and two-dimensional FTC for W, on the same global parameters in both halves"}
    result = {"schema": "WU088_HH_PHYS14_CARRIED_SECOND_HALF_V1", "status": "CANDIDATE_COMPUTED",
              "scientific_cases": 1, "semantic_cases": ["one carried isotropic two-half history", "original-grid transport-only split operator"],
              "arithmetic": {"method": "Fraction with outward dyadic rounding after every interval operation", "significand_bits": BITS,
                             "exponent": "unbounded integer", "input_authority": "captured binary64 bits and PHYS09/11/13 exact rational intervals",
                             "signed_tails": "all incoming signed U/V/W endpoints retained; structural gas-independent source slots reconstructed from source graph"},
              "scope": {"same_COMMON": True, "past_HH_ON_retained": True, "same_global_lambda_b_both_steps": True,
                        "lambda": [0, 1], "b": [0, 1], "coefficient_family": "geometric isotropic subfamily of inherited fixed-coefficient enclosures",
                        "source_aligned_denominator": True, "native_authority": False, "native_state_emitted": False,
                        "new_native_or_atomic_callbacks": 0, "new_validated_implicit_stages": 1, "NCP_jobs": 0,
                        "global_acceptance_or_order_nodes_completed": []},
              "chronology": {"t0_s": I(t0), "h_s": h, "t1_s": I(t0) + h, "t2_s": I(t0) + 2 * h,
                             "endpoint_stage_leaf_source": "original Full source stage, identical terminal time"},
              "constants": {"nH": src.nH, "f_stage": src.f, "fhat_source": src.fhat, "Hmean": src.H,
                            "H_geometry": I(Hgeom), "rho": rho, "birth_amount_M": M, "CHI_H": src.chi, "C_T": src.C,
                            "energy_bits": box["energy_bits"], "HI_active_nodes": src.active},
              "root_certificate": {"domain_X": X, "input_g1": g1, "whole_domain_self_map_image": P,
                                   "strict_interior_coordinates": strict, "scaled_inf_scales": scales,
                                   "whole_domain_contraction_upper": I(qwhole), "whole_domain_row_bounds": qrows,
                                   "refinement_images": refinements, "root_image": Z,
                                   "refined_contraction_upper": I(q), "denominators": [k[0] for k in F["kernels"]],
                                   "uniqueness": "Banach self-map and contraction on original convex X for each fixed family member"},
              "gas_response": {"coordinates": COORDS, "U": U, "V": V, "W": W},
              "linear_certificates": {"L_hFg": L, "rhs_U": rhsU, "rhs_V": rhsV, "rhs_W": rhsW,
                                      "U": eu, "V": ev, "W": ew, "mixed_rhs_terms_per_second": wterms},
              "readouts": ro, "finite_response": finite, "HH_U_decomposition": decompositions,
              "photon_state": {"incoming": incoming, "outgoing": nout, "absorbed": absorbed, "guard": guard,
                               "number_balance": "each exact function Nin=Nout+Nabs; all four interval residuals contain zero",
                               "source_birth_M": M, "source_birth_energy_eV_per_H": M * energy[24]},
              "remap_split_defect": remap,
              "reuse": {"PHYS09": "first-half U,V,W and root-domain centre", "PHYS11": "first-half group joint carry and source-aligned definition",
                        "PHYS13": "first-half root image and readout definition", "NCP07_Full": "nonphoto/q value/gas-gradient/gas-Hessian on X and centre"},
              "elapsed_scientific_seconds": time.time() - started}
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "ADVANCE_RESULTS.json").write_text(json.dumps(out(result), ensure_ascii=False, indent=2) + "\n")
    digest = hashlib.sha256((output_dir / "ADVANCE_RESULTS.json").read_bytes()).hexdigest()
    summary = {"status": result["status"], "scientific_cases": 1, "elapsed_seconds": result["elapsed_scientific_seconds"],
               "contraction_whole": short(I(qwhole)), "contraction_refined": short(I(q)), "root": short(Z),
               "readouts": short(ro), "HH_decomposition_K": {k: short(v["temperature_U_K"]) for k, v in decompositions.items()},
               "max_remap_column_L1": short(remap["max_column_L1_enclosure"]),
               "remap_HI_active_common_delta": short(remap["common_weighted_HI_active_photon_number_difference"]),
               "results_sha256": digest}
    (output_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    main(args.output_dir)
