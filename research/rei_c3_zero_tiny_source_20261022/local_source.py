"""Finite local absolute-abundance operator; no rate provider or IVP.

Coefficients/applicability and fixed positive slot scales are caller supplied.
Time is proper seconds. Unary k has s^-1; binary k has m^3/s.
"""
import math
from dataclasses import dataclass


class UnresolvedInput(ValueError):
    pass


@dataclass(frozen=True)
class Event:
    name: str
    reactants: dict
    products: dict
    log_k: float
    applicability: str = "ACTIVE"

    def validate(self, slots):
        if self.applicability not in {"ACTIVE", "SUPPORT_ZERO", "ABSENT", "UNRESOLVED"}:
            raise ValueError("unknown applicability")
        if not math.isfinite(self.log_k):
            raise ValueError("finite log(k) required")
        for side in (self.reactants, self.products):
            if any(type(j) is not int or not 0 <= j < len(slots)
                   or type(m) is not int or m <= 0 for j, m in side.items()):
                raise ValueError("integer in-range slots and positive multiplicities required")
        if sum(self.reactants.values()) not in (1, 2):
            raise ValueError("only unary/binary events")
        nu = {j: self.products.get(j, 0) - self.reactants.get(j, 0)
              for j in self.reactants.keys() | self.products.keys()}
        nu = {j: v for j, v in nu.items() if v}
        dot = lambda key: sum(slots[j][key] * v for j, v in nu.items())
        if dot("A") != 0:
            raise ValueError("nonconserving baryon stoichiometry")
        de, dz = dot("q"), dot("Z")
        db = sum((slots[j]["Z"] - slots[j]["q"]) * v for j, v in nu.items())
        dn = sum(nu.values())
        if de + db != dz:
            raise ValueError("inconsistent charge bookkeeping")
        return nu, {"A_dot_nu": 0, "delta_e": de, "delta_bound": db,
                    "Z_dot_nu": dz, "delta_N": dn, "delta_C": dn + de}


def _product_log(event, y, n_b, derivative_slot=None):
    """Reduced polynomial product handles multiplicity-one zero boundaries."""
    terms = [event.log_k, (sum(event.reactants.values()) - 1) * math.log(n_b)]
    for j, m in event.reactants.items():
        exponent = m - (j == derivative_slot)
        terms.append(-math.lgamma(m + 1))
        if exponent:
            if y[j] == 0:
                return None
            terms.append(exponent * math.log(y[j]))
    if derivative_slot is not None:
        terms.append(math.log(event.reactants[derivative_slot]))
    return math.fsum(terms)


def evaluate(events, slots, y, scales, n_b):
    """Return raw event projections, scaled sources, and fixed-scale Jacobian.

    Signed event contributions use fsum; scaled evaluations never first form
    an unscaled product. None log_rate means an exact-zero event only.
    """
    n = len(slots)
    if len(y) != n or len(scales) != n:
        raise ValueError("slot length mismatch")
    if not math.isfinite(n_b) or n_b <= 0:
        raise ValueError("positive finite n_B required")
    if any(not math.isfinite(v) or v < 0 for v in y):
        raise ValueError("finite nonnegative abundances required")
    if any(not math.isfinite(v) or v <= 0 for v in scales):
        raise ValueError("positive finite fixed scales required")
    log_s = [math.log(v) for v in scales]
    source_terms = [[] for _ in slots]
    jac_terms = [[[] for _ in slots] for _ in slots]
    records = []
    for event in events:
        nu, bookkeeping = event.validate(slots)
        if event.applicability == "UNRESOLVED":
            raise UnresolvedInput(event.name + ": UNRESOLVED")
        if event.applicability in {"SUPPORT_ZERO", "ABSENT"}:
            records.append({"name": event.name, "status": event.applicability,
                            "log_rate": None, "raw_rate": 0.0,
                            "bookkeeping": bookkeeping, "scaled_contributions": {}})
            continue
        ell = _product_log(event, y, n_b)
        raw = 0.0 if ell is None else math.exp(ell)
        status = "ZERO_REACTANT" if ell is None else ("UNDERFLOW" if raw == 0 else "ACTIVE")
        contributions = {}
        for i, v in nu.items():
            contribution = 0.0 if ell is None else v * math.exp(ell - log_s[i])
            source_terms[i].append(contribution)
            contributions[i] = contribution
        for j in event.reactants:
            derivative_log = _product_log(event, y, n_b, j)
            if derivative_log is not None:
                for i, v in nu.items():
                    jac_terms[i][j].append(v * math.exp(math.fsum(
                        [derivative_log, log_s[j], -log_s[i]])))
        records.append({"name": event.name, "status": status, "log_rate": ell,
                        "raw_rate": raw, "bookkeeping": bookkeeping,
                        "scaled_contributions": contributions})
    return {"events": records,
            "scaled_source": [math.fsum(t) for t in source_terms],
            "scaled_jacobian": [[math.fsum(t) for t in row] for row in jac_terms]}
