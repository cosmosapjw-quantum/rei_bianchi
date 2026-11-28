"""Source-verified GL2022 one-channel isothermal four-species exchange.

Scoped exact-flow consumer for one printed nominal SQM rate at T=105 K.
Physical number densities in m^-3, proper time in s, rate in m^3/s.
n=(H+, HD(v0,j2), D+, H2(v0,j1)); nu=(-1,-1,+1,+1).
No reverse reaction, other levels, thermal populations, physical energy defect,
cosmological history or rate uncertainty is supplied.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
import sys
from typing import Sequence
from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    NativeGrid, PDF_SHA256, SourceContractError, load_native_grid,
)

T_SOURCE_K = 105
STATE_ORDER = ("H+", "HD(v=0,j=2)", "D+", "H2(v=0,j=1)")
NU = (-1, -1, 1, 1)
H_NUCLEI = (1, 1, 0, 2)
D_NUCLEI = (0, 1, 1, 0)
CHARGE = (1, 0, 1, 0)
K_PRINTED_SI = Fraction(23, 200000000000000000)

class ModelContractError(ValueError):
    """Invalid finite model, state, clock or source-domain request."""

def _nonnegative_finite(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelContractError(f"{name}: finite nonnegative real required")
    x = float(value)
    if not math.isfinite(x) or x < 0.0:
        raise ModelContractError(f"{name}: finite nonnegative real required")
    return x

def _finite_real(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelContractError(f"{name}: finite real required")
    x = float(value)
    if not math.isfinite(x):
        raise ModelContractError(f"{name}: finite real required")
    return x

def _state(state: Sequence[float]) -> tuple[float, float, float, float]:
    if len(state) != 4:
        raise ModelContractError("exactly four ordered state densities required")
    return tuple(_nonnegative_finite(v, f"n[{i}]") for i, v in enumerate(state))  # type: ignore[return-value]

def _rate_si_from_verified_grid(grid: NativeGrid) -> Fraction:
    if type(grid) is not NativeGrid or grid.source_sha256 != PDF_SHA256:
        raise SourceContractError("verified original R18 NativeGrid required")
    k = grid.lookup(T_SOURCE_K, initial_v=0, initial_j=2,
                    product_v=0, product_j=1, method="SQM").nominal_m3_s
    if k != K_PRINTED_SI:
        raise SourceContractError("original 105 K printed source rate mismatch")
    return k

@dataclass(frozen=True)
class FlowResult:
    state_m3: tuple[float, float, float, float]
    extent_m3: float
    proper_seconds: float
    effective_seconds: float
    volume_ratio: float
    rate_m3_s: Fraction
    source_sha256: str
    source_temperature_K: int = T_SOURCE_K
    source_value_kind: str = "SOURCE_NATIVE_PRINTED_NOMINAL"
    physical_source_uncertainty: None = None
    physical_consumer_admitted: bool = False

    def as_json(self) -> dict:
        return {"schema": "wu.r19.nominal_exchange_flow.v1",
                "state_order": list(STATE_ORDER),
                "state_number_density_m_minus3": list(self.state_m3),
                "extent_per_reference_volume_m_minus3": self.extent_m3,
                "proper_seconds": self.proper_seconds,
                "effective_seconds": self.effective_seconds,
                "volume_ratio": self.volume_ratio,
                "source": {"temperature_K": self.source_temperature_K,
                           "rate_m3_s_exact": {"numerator": str(self.rate_m3_s.numerator),
                                               "denominator": str(self.rate_m3_s.denominator)},
                           "pdf_sha256": self.source_sha256,
                           "value_kind": self.source_value_kind,
                           "physical_uncertainty": None},
                "admission": {"conditional_four_state_model": True,
                              "physical_consumer": False,
                              "production": "NOT_ISSUED", "HH_R10": "OFF", "L4": False}}

def _extent_and_remainders(a: float, b: float, k: float, effective_seconds: float
                           ) -> tuple[float, float, float]:
    """Stable analytic extent and two reactant survivors; expm1 near degeneracy."""
    if a == 0 or b == 0 or effective_seconds == 0 or k == 0:
        return 0.0, a, b
    m, M = min(a, b), max(a, b)
    delta = M - m
    if delta == 0:
        q = k * m * effective_seconds
        if not math.isfinite(q):
            raise ModelContractError("dimensionless exposure overflows float")
        remain = m / (1.0 + q)
        xi = m * q / (1.0 + q)
        return xi, remain, remain
    q = k * delta * effective_seconds
    if not math.isfinite(q):
        raise ModelContractError("dimensionless exposure overflows float")
    e = math.exp(-q)
    z = -math.expm1(-q)
    den = delta + m * z
    xi = m * (M / den) * z
    small_rem = m * (delta / den) * e
    large_rem = M * (delta / den)
    if not all(math.isfinite(x) and x >= 0 for x in (xi, small_rem, large_rem)):
        raise ModelContractError("floating-point state overflow or invalid result")
    if a <= b:
        return xi, small_rem, large_rem
    return xi, large_rem, small_rem


def flow_nominal(grid: NativeGrid, initial_m3: Sequence[float], proper_seconds: float,
                 *, volume_ratio: float = 1.0,
                 integrated_inverse_volume_seconds: float | None = None) -> FlowResult:
    """Exact one-channel flow for prescribed V/V0>0 and I=int dt/(V/V0)."""
    k = _rate_si_from_verified_grid(grid)
    n0 = _state(initial_m3)
    t = _nonnegative_finite(proper_seconds, "proper_seconds")
    v = _nonnegative_finite(volume_ratio, "volume_ratio")
    if v == 0:
        raise ModelContractError("positive physical volume ratio required")
    if integrated_inverse_volume_seconds is None:
        if v != 1.0:
            raise ModelContractError("nontrivial volume requires its integrated inverse-volume clock")
        eff = t
    else:
        eff = _nonnegative_finite(integrated_inverse_volume_seconds, "effective_seconds")
        if t == 0 and (eff != 0 or v != 1):
            raise ModelContractError("initial clock/volume must be (0,1)")
        if t > 0 and eff == 0:
            raise ModelContractError("positive-time positive-volume clock must have positive integral")
    xi, h, hd = _extent_and_remainders(n0[0], n0[1], float(k), eff)
    result = (h / v, hd / v, (n0[2] + xi) / v, (n0[3] + xi) / v)
    if not all(math.isfinite(q) and q >= 0 for q in result):
        raise ModelContractError("invalid diluted number densities")
    return FlowResult(result, xi, t, eff, v, k, grid.source_sha256)

def flow_constant_expansion(grid: NativeGrid, initial_m3: Sequence[float],
                            proper_seconds: float, expansion_theta_s: float) -> FlowResult:
    """Prescribed theta=d ln(V/V0)/dt (s^-1), including contraction.

    V/V0=exp(theta*t); I=-expm1(-theta*t)/theta, with I=t at theta=0.
    This is not a solved Bianchi/Einstein system or thermal history.
    """
    t = _nonnegative_finite(proper_seconds, "proper_seconds")
    theta = _finite_real(expansion_theta_s, "expansion_theta_s")
    arg = theta * t
    if not math.isfinite(arg) or abs(arg) > 650:
        raise ModelContractError("expansion exponent exceeds guarded floating range")
    v = math.exp(arg)
    eff = -math.expm1(-arg) / theta if theta != 0 else t
    return flow_nominal(grid, initial_m3, t, volume_ratio=v,
                        integrated_inverse_volume_seconds=eff)


def source_rhs(grid: NativeGrid, state_m3: Sequence[float],
               dt_ds_seconds: float = 1.0, expansion_theta_s: float = 0.0
               ) -> tuple[float, float, float, float]:
    """dn/ds=(dt/ds)*(nu*k*nH*nHD - theta*n), fixed T=105K.

    s is increasing integration coordinate, dt/ds>0. Not full-A.
    """
    k = float(_rate_si_from_verified_grid(grid))
    n = _state(state_m3)
    g = _nonnegative_finite(dt_ds_seconds, "dt/ds")
    if g == 0:
        raise ModelContractError("clock Jacobian dt/ds must be strictly positive")
    theta = _finite_real(expansion_theta_s, "expansion_theta_s")
    flux = k * n[0] * n[1]
    if not math.isfinite(flux):
        raise ModelContractError("flux overflow")
    y = tuple(g * (nu * flux - theta * ni) for nu, ni in zip(NU, n))
    if not all(math.isfinite(v) for v in y):
        raise ModelContractError("RHS overflow")
    return y  # type: ignore[return-value]


def source_jacobian(grid: NativeGrid, state_m3: Sequence[float],
                    dt_ds_seconds: float = 1.0, expansion_theta_s: float = 0.0
                    ) -> tuple[tuple[float, ...], ...]:
    """Exact 4x4 Jacobian of this isolated chemical+prescribed-dilution RHS.

    J_ij=g*(nu_i*k*[nHD,nH,0,0]_j-theta*delta_ij).
    Chemical part has rank <=1, one eigenvalue -g*k*(nH+nHD).
    """
    k = float(_rate_si_from_verified_grid(grid))
    n = _state(state_m3)
    g = _nonnegative_finite(dt_ds_seconds, "dt/ds")
    if g == 0:
        raise ModelContractError("clock Jacobian must be strictly positive")
    theta = _finite_real(expansion_theta_s, "expansion_theta_s")
    grad = (k * n[1], k * n[0], 0.0, 0.0)
    out = tuple(tuple(g * (NU[i] * grad[j] - (theta if i == j else 0.0))
                      for j in range(4)) for i in range(4))
    if not all(math.isfinite(q) for row in out for q in row):
        raise ModelContractError("Jacobian overflow")
    return out


def conserved_totals(state_m3: Sequence[float]) -> dict[str, float]:
    n = _state(state_m3)
    return {"H_nuclei_m3": sum(w*x for w,x in zip(H_NUCLEI,n)),
            "D_nuclei_m3": sum(w*x for w,x in zip(D_NUCLEI,n)),
            "positive_charge_number_m3": sum(w*x for w,x in zip(CHARGE,n))}


def conditional_event_energy(extent_per_reference_volume_m3: float,
                             energy_release_joule_per_event: float) -> dict[str,float]:
    """FORMAL ledger: E_chem=-Q*extent, E_bath=+Q*extent.

    Q must be separately source-qualified. No actual physical heat deposition.
    """
    extent = _nonnegative_finite(extent_per_reference_volume_m3, "extent")
    Q = _finite_real(energy_release_joule_per_event, "Q_event")
    e = Q * extent
    if not math.isfinite(e):
        raise ModelContractError("energy ledger overflow")
    return {"chemical_energy_change_J_per_reference_m3": -e,
            "bath_energy_change_J_per_reference_m3": e,
            "formal_total_J_per_reference_m3": 0.0,
            "physical_Q_admitted": False}


def nominal_rate_sensitivity(grid: NativeGrid, initial_m3: Sequence[float],
                             effective_seconds: float) -> dict[str,float]:
    """Mathematical d extent/dk=I*(a-xi)*(b-xi) for fixed clock.

    This is NOT a physical source-error interval. K uncertainty is unspecified.
    """
    n = _state(initial_m3)
    eff = _nonnegative_finite(effective_seconds, "effective_seconds")
    xi, a_rem, b_rem = _extent_and_remainders(n[0],n[1],float(_rate_si_from_verified_grid(grid)),eff)
    return {"extent_m3":xi,"d_extent_d_k_SI":eff*a_rem*b_rem,
            "d_extent_d_effective_seconds":float(K_PRINTED_SI)*a_rem*b_rem,
            "source_uncertainty":None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--initial-m3", type=float, nargs=4, required=True,
                        metavar=("HPLUS", "HD02", "DPLUS", "H201"))
    parser.add_argument("--proper-seconds", type=float, required=True)
    parser.add_argument("--expansion-theta-s", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        grid = load_native_grid(args.source_pdf)
        result = flow_constant_expansion(grid, args.initial_m3,
                                         args.proper_seconds, args.expansion_theta_s)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise ModelContractError("output already exists: create-only")
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result.as_json(), stream, indent=2)
            stream.write("\n")
    except FileExistsError:
        print("ModelContractError: output already exists: create-only", file=sys.stderr)
        return 2
    except (SourceContractError, ModelContractError, OSError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
