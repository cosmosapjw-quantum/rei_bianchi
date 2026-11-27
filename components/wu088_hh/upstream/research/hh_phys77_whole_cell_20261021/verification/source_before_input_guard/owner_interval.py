"""Outward box extension of the captured finite-L8 real-coefficient IVP.

This is the exact-real algebra defined in THEOREM_KO.md, not a claim about
all intermediate NumPy roundoff or the unrecorded historic constructor table.
No ODE integrator or float elementary function is used by this module.
"""
from __future__ import annotations

from decimal import Decimal
import hashlib
import importlib.util
from pathlib import Path
import sys

from export_owner import validate_table

HERE = Path(__file__).resolve().parent
TRANSPORT_PATH = HERE.parents[1] / "hh_phys76_time_transport_20261021/source/interval_transport.py"
TRANSPORT_SHA256 = "c8b21a2dfdb7ec5810710d2fda6d98922656ecf6d6ae86c82632caab3e227ce6"
if hashlib.sha256(TRANSPORT_PATH.read_bytes()).hexdigest() != TRANSPORT_SHA256:
    raise ValueError("PHYS76_INTERVAL_DEPENDENCY_IDENTITY")
_spec = importlib.util.spec_from_file_location("_phys77_pinned_transport", TRANSPORT_PATH)
transport = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = transport
_spec.loader.exec_module(transport)
Interval = transport._Interval
decimal = transport._decimal
parse_interval = transport._interval


class Arithmetic(transport._Arithmetic):
    """Reuse PHYS76 directed arithmetic; add monotone sqrt and square."""

    def point(self, value):
        if isinstance(value, str):
            value = decimal(value)
        elif not isinstance(value, Decimal) or not value.is_finite():
            raise ValueError("FINITE_DECIMAL_POINT_REQUIRED")
        return Interval(value, value)

    def integer(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("INTEGER_REQUIRED")
        return self.point(Decimal(value))

    def multiply(self, x, y):
        # Exact sign-based interval shortcut. No reassociation of a float sum.
        if x.lo >= 0 and y.lo >= 0:
            return Interval(self.down.multiply(x.lo, y.lo), self.up.multiply(x.hi, y.hi))
        return super().multiply(x, y)

    def square(self, x):
        products_lo = [self.down.multiply(v, v) for v in (x.lo, x.hi)]
        products_hi = [self.up.multiply(v, v) for v in (x.lo, x.hi)]
        return Interval(Decimal(0) if x.lo <= 0 <= x.hi else min(products_lo), max(products_hi))

    def sqrt(self, x):
        if x.lo < 0:
            raise ValueError("SQRT_NONNEGATIVE_DOMAIN")
        # Decimal.sqrt is correctly rounded. Adjacent representable numbers
        # surround that result even when the rounding direction is ignored.
        lo = Decimal(0) if x.lo == 0 else self.near.sqrt(x.lo).next_minus(context=self.down)
        hi = Decimal(0) if x.hi == 0 else self.near.sqrt(x.hi).next_plus(context=self.up)
        if (not lo.is_finite() or not hi.is_finite() or lo < 0
                or lo.is_subnormal(context=self.down) or hi.is_subnormal(context=self.up)):
            raise ArithmeticError("SQRT_ENCLOSURE_OUTSIDE_REPRESENTABLE_RANGE")
        return Interval(lo, hi)

    def scale(self, integer, interval):
        return self.multiply(self.integer(integer), interval)

    def sum(self, values):
        total = self.zero
        for value in values:
            total = self.add(total, value)
        return total

    def absolute(self, value):
        lo = Decimal(0) if value.lo <= 0 <= value.hi else min(value.lo.copy_abs(), value.hi.copy_abs())
        return Interval(lo, max(value.lo.copy_abs(), value.hi.copy_abs()))


def _valid_box(value):
    if not isinstance(value, Interval) or not (value.lo.is_finite() and value.hi.is_finite()) or value.lo > value.hi:
        raise ValueError("FINITE_ORDERED_BOX_REQUIRED")


class FiniteOwner:
    """One immutable table and one arithmetic precision per instance.

    Constant packet products are outward-precomputed once. Every box uses
    shared exponentials and a fused streaming reduction over the exact
    2592 packet rule; no cells are dropped except exact zero populations.
    """

    def __init__(self, table, precision=50):
        validate_table(table)
        self.identity = table["table_sha256"]
        self.a = a = Arithmetic(precision)
        self.c = {key: a.point(value) for key, value in table["constants"].items()}
        self.matrix = [[a.point(v) for v in row] for row in table["arrays"]["M"]]
        c = self.c
        self.gamma = a.divide(c["h_ref"], c["h0"])
        self.gamma2 = a.square(self.gamma)
        self.mass2 = a.square(c["mass"])
        self.sqrt3, self.sqrt2 = a.sqrt(a.integer(3)), a.sqrt(a.integer(2))
        aref2 = a.square(c["a_ref"])
        self.dust0 = a.divide(a.multiply(a.subtract(a.one, c["f_m"]), c["omega_m"]),
                              a.multiply(aref2, c["a_ref"]))
        self.rad0 = a.divide(c["omega_r"], a.square(aref2))
        # Algebraic collection keeps the captured nonzero monopole defect.
        self.delta_row = [a.add(v, a.integer(2)) if i == 1 else v
                          for i, v in enumerate(self.matrix[0])]
        self.packets = []
        arrays = table["arrays"]
        for i, radial in enumerate(arrays["q"]):
            radial2 = a.square(a.point(radial))
            for j, mu2 in enumerate(arrays["mu2"]):
                population = a.point(arrays["numbers"][i][j])
                if population.hi == 0:
                    continue
                mu = a.point(mu2)
                self.packets.append((a.divide(population, c["reference_energy_norm"]),
                                     a.multiply(radial2, a.subtract(a.one, mu)),
                                     a.multiply(radial2, mu)))

    def moments(self, x, b):
        a = self.a
        # All physical momentum terms in one cell share these exponentials.
        perp_scale = a.exp(a.add(a.scale(-2, x), a.scale(2, b)))
        para_scale = a.exp(a.add(a.scale(-2, x), a.scale(-4, b)))
        volume = a.exp(a.scale(-3, x))
        totals = [a.zero for _ in range(5)]
        for weight, perp0, para0 in self.packets:
            up, uz = a.multiply(perp0, perp_scale), a.multiply(para0, para_scale)
            momentum2 = a.add(up, uz)
            energy = a.sqrt(a.add(self.mass2, momentum2))
            weighted_inverse = a.divide(weight, energy)
            values = (
                a.multiply(weight, energy),
                a.divide(a.multiply(weighted_inverse, up), a.integer(2)),
                a.multiply(weighted_inverse, uz),
                a.divide(a.multiply(weighted_inverse, a.subtract(uz, a.divide(up, a.integer(2)))), a.integer(3)),
                a.divide(a.multiply(weighted_inverse, a.add(a.scale(3, self.mass2), a.scale(2, momentum2))), a.integer(3)),
            )
            totals = [a.add(old, new) for old, new in zip(totals, values)]
        values = [a.multiply(volume, value) for value in totals]
        return dict(zip(("rho", "pressure_perp", "pressure_parallel", "pi", "rho_minus_pbar"), values))

    def evaluate(self, x, y):
        _valid_box(x)
        if len(y) != 8:
            raise ValueError("EIGHT_STATE_BOX_REQUIRED")
        for item in y:
            _valid_box(item)
        if x.lo < 0 or y[1].lo <= -1 or y[1].hi >= 1 or y[3].lo <= 0:
            raise ValueError("FINITE_OWNER_REGULAR_CHART_REQUIRED")
        a, c = self.a, self.c
        m = self.moments(x, y[1])
        dust = a.multiply(self.dust0, a.exp(a.scale(-3, x)))
        rad = a.multiply(self.rad0, a.exp(a.scale(-4, x)))
        shear_energy = a.multiply(self.gamma2, a.square(y[2]))
        total = a.sum([dust, a.multiply(c["mpref"], m["rho"]),
                       a.multiply(rad, y[3]), c["omega_lambda"], shear_energy])
        if total.lo <= 0:
            raise ValueError("POSITIVE_H2_BOX_REQUIRED")
        sqrt_total = a.sqrt(total)
        v = a.divide(a.multiply(self.gamma, y[2]), sqrt_total)
        pressure = a.add(a.multiply(c["mpref"], m["pi"]), a.divide(a.multiply(rad, y[4]), a.integer(3)))
        matrix_e = [a.sum(a.multiply(coeff, e) for coeff, e in zip(row, y[3:])) for row in self.matrix]
        rhs = [a.divide(self.gamma, sqrt_total), v,
               a.add(a.scale(-3, y[2]), a.divide(a.scale(3, pressure), a.multiply(self.gamma, sqrt_total)))]
        rhs.extend(a.multiply(v, entry) for entry in matrix_e)
        delta0 = a.sum(a.multiply(coeff, e) for coeff, e in zip(self.delta_row, y[3:]))
        alpha_numerator = a.sum([
            a.divide(a.scale(3, dust), a.integer(2)),
            a.divide(a.scale(3, a.multiply(c["mpref"], m["rho_minus_pbar"])), a.integer(2)),
            a.multiply(rad, y[3]), a.scale(3, c["omega_lambda"]),
            a.divide(a.multiply(a.multiply(rad, v), delta0), a.integer(2)),
        ])
        alpha = a.divide(alpha_numerator, total)
        pm = a.divide(a.multiply(self.sqrt3, a.scale(3, a.multiply(c["mpref"], m["pi"]))), total)
        pr = a.divide(a.multiply(self.sqrt3, a.multiply(rad, y[4])), total)
        signed_total = a.add(pm, pr)
        shear = a.multiply(self.sqrt3, v)
        # Independent unsimplified chain-rule extension, useful for checks.
        pbar = a.divide(a.add(a.scale(2, m["pressure_perp"]), m["pressure_parallel"]), a.integer(3))
        rho_prime = a.subtract(a.scale(-3, a.add(m["rho"], pbar)), a.scale(6, a.multiply(v, m["pi"])))
        total_prime = a.sum([a.scale(-3, dust), a.multiply(c["mpref"], rho_prime),
                            a.multiply(rad, a.add(a.scale(-4, y[3]), rhs[3])),
                            a.scale(2, a.multiply(self.gamma2, a.multiply(y[2], rhs[2])))])
        alpha_chain = a.add(a.integer(3), a.divide(total_prime, a.scale(2, total)))
        return {"rhs": rhs, "A": alpha, "P_m": pm, "P_r": pr,
                "S": shear, "Pi_total_F": a.multiply(self.sqrt2, a.absolute(signed_total)),
                "Sigma_F": a.multiply(self.sqrt2, a.absolute(shear)),
                "H": a.multiply(c["h0"], sqrt_total), "H2_over_h0_squared": total,
                "delta_monopole": delta0, "A_chain_rule": alpha_chain, **m}


def serialize_evaluation(value):
    return {key: ([v.strings() for v in item] if isinstance(item, list) else item.strings())
            for key, item in value.items()}
