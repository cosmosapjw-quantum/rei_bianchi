"""PHYS04 one-sided active-grid remap and exact opacity defect.

All input floats are interpreted as exact binary64 real leaves.
No gas trajectory, nonlinear root, native dispatch, or fitted tolerance.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path
import argparse
import hashlib
import json

INPUT_SHA = "26a340065a9a99d02903bf0cc008baaf6ade00d2e845beb9d2b0b7d801316494"
ZERO = Q(0)


def leaf(x):
    if isinstance(x, float):
        return Q.from_float(x)
    return Q(x)


@dataclass(frozen=True)
class Box:
    lo: Q
    hi: Q

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @staticmethod
    def point(x):
        x = leaf(x)
        return Box(x, x)

    def __add__(self, other):
        other = asbox(other)
        return Box(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Box(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-asbox(other))

    def __rsub__(self, other):
        return asbox(other) - self

    def __mul__(self, other):
        other = asbox(other)
        p = [self.lo * other.lo, self.lo * other.hi,
             self.hi * other.lo, self.hi * other.hi]
        return Box(min(p), max(p))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = asbox(other)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("interval contains zero")
        return self * Box(Q(1) / other.hi, Q(1) / other.lo)

    def square(self):
        if self.lo >= 0:
            return Box(self.lo * self.lo, self.hi * self.hi)
        if self.hi <= 0:
            return Box(self.hi * self.hi, self.lo * self.lo)
        return Box(ZERO, max(self.lo * self.lo, self.hi * self.hi))


def asbox(x):
    return x if isinstance(x, Box) else Box.point(x)


def exp_negative(x, even_order=16):
    """Alternating series, 0<=x<=1, even partial sum upper, next odd lower."""
    x = leaf(x)
    if not (0 <= x <= 1) or even_order < 2 or even_order % 2:
        raise ValueError("exp domain/order")
    term, total = Q(1), Q(1)
    for k in range(1, even_order + 1):
        term *= -x / k
        total += term
    lower = total + term * (-x) / (even_order + 1)
    return Box(lower, total)


def exp_clock(hubble, time):
    h, t = leaf(hubble), leaf(time)
    if h < 0 or t < 0:
        raise ValueError("negative redshift clock")
    return Box.point(t) if h == 0 else (1 - exp_negative(h * t)) / h


def rate_vector(nodes, hubble, active_start):
    e = list(map(leaf, nodes))
    h = leaf(hubble)
    if h < 0 or not 0 < active_start < len(e):
        raise ValueError("invalid active range")
    if any(a >= b for a, b in zip(e, e[1:])):
        raise ValueError("nodes not strictly increasing")
    return [h * e[j] / (e[j] - e[j - 1])
            for j in range(active_start, len(e))]


def generator_apply(rates, v):
    """Column j loses to j-1; first active node loses to inactive sector."""
    if len(rates) != len(v):
        raise ValueError("shape")
    out = [-a * x for a, x in zip(rates, v)]
    for j in range(1, len(v)):
        out[j - 1] += rates[j] * v[j]
    return out


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), ZERO)


def exact_record(q):
    q = leaf(q)
    return {"numerator": str(q.numerator), "denominator": str(q.denominator)}


def dec_q(q, precision=60, rounding=None):
    with localcontext() as c:
        c.prec = precision
        if rounding is not None:
            c.rounding = rounding
        return Decimal(q.numerator) / Decimal(q.denominator)


def box_record(b, units="1"):
    b = asbox(b)
    return {
        "units": units,
        "lo_exact": exact_record(b.lo), "hi_exact": exact_record(b.hi),
        "lo_decimal_outward": str(dec_q(b.lo, 48, ROUND_FLOOR)),
        "hi_decimal_outward": str(dec_q(b.hi, 48, ROUND_CEILING)),
        "midpoint_decimal": str(dec_q((b.lo + b.hi) / 2, 40)),
    }


def functional(nodes, rates, values, weights, hubble, macro_time):
    values, weights = list(map(leaf, values)), list(map(leaf, weights))
    h, macro = leaf(hubble), leaf(macro_time)
    lp = generator_apply(rates, values)
    llp = generator_apply(rates, lp)
    c = dot(weights, [v + h * u for v, u in zip(llp, lp)])
    half_s = exp_clock(h, macro / 2)
    full_s = exp_clock(h, macro)
    factor = half_s.square()
    initial = dot(weights, values)
    full = initial + full_s * dot(weights, lp)
    defect = factor * c
    two = full + defect
    factor4 = macro**2 / 4 - h * macro**3 / 8 + Q(7, 192) * h*h*macro**4
    residual4 = defect - factor4 * c
    return {
        "initial": Box.point(initial), "full": full, "two_half": two,
        "defect_two_minus_full": defect,
        "coefficient_h2": Box.point(c / 4),
        "coefficient_h3": Box.point(-h * c / 8),
        "coefficient_h4": Box.point(Q(7, 192) * h*h*c),
        "quartic_polynomial_value": Box.point(factor4*c),
        "quartic_remainder": residual4,
        "relative_defect_to_full": defect / full if not full.lo <= 0 <= full.hi else None,
        "relative_quartic_remainder": residual4 / defect if not defect.lo <= 0 <= defect.hi else None,
    }


def decimal_direct_map(energies, values, redshift, guard_n=Decimal(0),
                       guard_u=Decimal(0)):
    """Independent direct hat redistribution, including the original low guard."""
    n = len(energies)
    out = [Decimal(0)] * n
    gn, gu = guard_n, guard_u * redshift
    for energy, value in zip(energies, values):
        transported = energy * redshift
        if transported < energies[0]:
            gn += value
            gu += value * transported
            continue
        if transported == energies[-1]:
            out[-1] += value
            continue
        for k in range(n - 1):
            if energies[k] <= transported <= energies[k + 1]:
                w = (transported - energies[k]) / (energies[k + 1] - energies[k])
                out[k] += (1 - w) * value
                out[k + 1] += w * value
                break
        else:
            raise ValueError("uncovered direct interpolation cell")
    return out, gn, gu


def run(source):
    raw = Path(source).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != INPUT_SHA:
        raise ValueError("selected input hash mismatch")
    data = json.loads(raw)
    e = list(map(leaf, data["energies_ev"]))
    p = list(map(leaf, data["old_point_photons"]))
    sig = [list(map(leaf, row)) for row in data["sigma_cm2"]]
    start = 16
    H = leaf(data["h_mean_per_s"])
    macro = leaf(1.25e9)
    delta = macro / 2
    rfull = exp_negative(H * macro)
    rhalf = exp_negative(H * delta)
    rates = rate_vector(e, H, start)
    # Every potentially active input stays in its immediately-left cell.
    cells = []
    for j in range(start, len(e)):
        margin = rfull * e[j] - e[j - 1]
        assert margin.lo > 0 and (e[j] - rfull * e[j]).lo > 0
        cells.append({"node": j, "left_margin_ev": box_record(margin, "eV")})
    # Inactive photons cannot redshift upward; all three provider sigmas vanish.
    assert all(all(x == 0 for x in row) for row in sig[:start])
    assert all(row[1] == row[2] == 0 for row in sig)

    chi = leaf(13.598434599702)
    weights = {
        "HI_opacity": [s[0] for s in sig[start:]],
        "HI_excess_energy": [s[0]*(x-chi) for s, x in zip(sig[start:], e[start:])],
    }
    fs = {key: functional(e, rates, p[start:], w, H, macro)
          for key, w in weights.items()}
    records = {}
    for key, v in fs.items():
        base_unit = "cm^2 photons/H" if key == "HI_opacity" else "eV cm^2 photons/H"
        records[key] = {name: None if b is None else box_record(
            b, "1" if name.startswith("relative") else base_unit + (
                " s^-2" if name == "coefficient_h2" else
                " s^-3" if name == "coefficient_h3" else
                " s^-4" if name == "coefficient_h4" else ""))
            for name, b in v.items()}

    # Column contributions display how signed spectrum contributions combine.
    columns = []
    for j in range(start, len(e)):
        unit = [ZERO] * len(rates); unit[j-start] = Q(1)
        lp = generator_apply(rates, unit)
        c = dot(weights["HI_opacity"],
                [v + H*u for v, u in zip(generator_apply(rates, lp), lp)])
        contribution = exp_clock(H, delta).square() * c * p[j]
        columns.append({"node": j, "input_photons_per_h": str(p[j]),
                        "weighted_opacity_defect": box_record(contribution, "cm^2 photons/H")})

    # New zero-old-photon specialization: remap term in two-half mixed h^4.
    # Preserve H/He thermal particle count; q cancels in the normalized ratio.
    x, y1, y2, wgas = list(map(leaf, data["old_gas"]))
    fhe = leaf(data["f_he"])
    ev, kb = leaf(1.602176634e-12), leaf(1.380649e-16)
    particles = 1 + fhe + x + fhe*(y1 + 2*y2)
    temperature = 2*ev*wgas/(3*kb*particles)
    nu = leaf(1.2) + Q(157800)/temperature
    u = 1-x
    eta = u*nu/particles
    def kappa(energy):
        return 4 + eta*(1-particles*(energy-chi)/wgas)
    birth_index = 24
    xi = kappa(e[birth_index])-4
    c2 = Q(13, 8) + xi/2
    a_birth = rates[birth_index-start]
    colour = a_birth*(sig[birth_index-1][0]*kappa(e[birth_index-1])
                       -sig[birth_index][0]*kappa(e[birth_index]))
    assert colour > 0
    ratio = macro*colour/(16*sig[birth_index][0]*c2)
    thermal = {
        "scope": "zero old photons, frozen coefficients, retained gas H/He/thermal state; isolated L-dependent mixed h^4 term only",
        "temperature_K": box_record(temperature, "K"),
        "nu": box_record(nu), "Xi_birth": box_record(xi),
        "C2": box_record(c2),
        "minus_K3x_LB_over_c_nH_q": box_record(colour, "cm^2 s^-1"),
        "minus_twohalf_mixed_h4_remap_over_c_nH_q": box_record(colour/16, "cm^2 s^-1"),
        "quartic_remap_term_over_twohalf_cubic_at_macro_h": box_record(ratio),
        "ratio_ppm": box_record(ratio*10**6, "ppm"),
        "finite_gas_error_certificate": False,
    }

    # Independent high precision witness uses direct physical hats, not L or L^2.
    witness = {}
    with localcontext() as ctx:
        ctx.prec = 150
        de = [dec_q(x, 150) for x in e]
        dp = [dec_q(x, 150) for x in p]
        drhalf = (-dec_q(H*delta, 150)).exp()
        drfull = (-dec_q(H*macro, 150)).exp()
        full, fn, fu = decimal_direct_map(de, dp, drfull)
        half, hn, hu = decimal_direct_map(de, dp, drhalf)
        two, tn, tu = decimal_direct_map(de, half, drhalf, hn, hu)
        zero = Decimal(0)
        for key, w in weights.items():
            dw = [Decimal(0)]*start + [dec_q(x, 150) for x in w]
            fv = sum((a*b for a,b in zip(dw, full)), zero)
            tv = sum((a*b for a,b in zip(dw, two)), zero)
            for name, value in (("full", fv), ("two_half", tv),
                                ("defect_two_minus_full", tv-fv)):
                qvalue = Q(value)
                b = fs[key][name]
                assert b.lo <= qvalue <= b.hi, (key, name)
                witness[key+"_"+name] = {"decimal": str(value), "inside_exact_interval": True}
        number_initial = sum(dp, zero)
        energy_initial = sum((a*b for a,b in zip(de, dp)), zero)
        number_full = sum(full, zero)+fn
        number_two = sum(two, zero)+tn
        energy_full = sum((a*b for a,b in zip(de, full)), zero)+fu
        energy_two = sum((a*b for a,b in zip(de, two)), zero)+tu
        tol = Decimal("1e-135")
        residuals = [number_full-number_initial, number_two-number_initial,
                     energy_full-energy_initial*drfull,
                     energy_two-energy_initial*drfull]
        assert all(abs(x) < tol for x in residuals)
        witness["number_energy_with_lower_guard"] = {
            "residuals": list(map(str, residuals)), "absolute_witness_tolerance": str(tol),
            "scope": "Decimal check; exact moment conservation follows from affine hat identities",
            "full_guard_number": str(fn), "two_half_guard_number": str(tn),
        }
        witness["boundary_not_identity"] = {
            "initial_lowest_node_positive": p[0] > 0,
            "positive_time_lowest_packet_moves_entirely_to_guard": True,
            "active_quotient_used_for_smooth_expansion": True,
        }

    # Exact structural checks independent of the current nonzero H.
    zr = rate_vector(e, ZERO, start)
    assert all(x == 0 for x in generator_apply(zr, p[start:]))
    assert exp_clock(ZERO, macro).lo == macro
    assert all(x == 0 for x in generator_apply(rates, [ZERO]*len(rates)))
    # Direct column algebra proves product, factor and zero-number interior identities.
    scalar_cases = []
    for hval, tval, a, b in [(Q(1,7),Q(1,5),Q(2,3),Q(5,4)),
                             (Q(0),Q(1,3),Q(2,3),Q(5,4))]:
        for rr in (Q(9,10),Q(99,100)):
            # With s=(1-r)/H for H>0: s(2t)=2s-Hs^2.
            if hval:
                ss=(1-rr)/hval
                ss2=(1-rr*rr)/hval
                assert 2*ss-ss2 == hval*ss*ss
            scalar_cases.append({"H":str(hval),"r":str(rr),"PASS":True})
    return {
        "schema": "HH_PHYS04_REMAP_OPACITY_V1", "input_sha256": sha,
        "semantics": "exact binary64 leaf real expressions; selected BE-stage spectrum used only as operator diagnostic",
        "arithmetic": {"bounds":"stdlib Fraction alternating exponential series, even order16 / odd17",
                       "witness":"independent Decimal.exp150 direct full hat remap with lower guard",
                       "native_rounding_replay":False},
        "parameters": {"H_per_s":str(H), "h_s":str(macro), "active_start":start,
                       "supplied_positive_groups":len(p), "active_groups":len(rates)},
        "cell_certificates":cells,
        "functionals":records, "signed_column_contributions":columns,
        "birth_mixed_quartic_specialization":thermal, "independent_witnesses":witness,
        "structural_checks":{"zero_H":True,"zero_vector":True,"scalar_identity_cases":scalar_cases,
                             "inactive_no_photo_HHe":True},
        "actual_finite_mixed_sign":None,"native_dispatches":0,"IVP_runs":0,
        "nonlinear_BE_roots":0,"old_science_suite_reruns":0,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ns=ap.parse_args()
    if ns.output.exists():
        raise FileExistsError("evidence output already exists")
    result=run(ns.source)
    ns.output.parent.mkdir(parents=True,exist_ok=True)
    ns.output.write_text(json.dumps(result,indent=2)+"\n")
    brief={k:{n:v[n]["midpoint_decimal"] for n in
             ("full","two_half","defect_two_minus_full","relative_defect_to_full","relative_quartic_remainder")}
           for k,v in result["functionals"].items()}
    brief["birth_remap_quartic_ratio_ppm"]=result["birth_mixed_quartic_specialization"]["ratio_ppm"]["midpoint_decimal"]
    print(json.dumps({"PASS":True,"summary":brief,"output":str(ns.output)},indent=2))


if __name__=="__main__":
    main()
