"""R20 exact GL2022 source-grid, single forward reactive exchange.

(H+, HD(v0,j2), D+, H2(v0,j1)), original printed nominal SQM rates.
External piecewise temperature and volume; no thermal, reverse or full-A claim.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
import argparse
import json
import math
from pathlib import Path
import sys
from typing import Callable, Sequence

from research.wu_hd_source_bound_r18_20261029.src.native_rates import (
    NativeGrid, PDF_SHA256, SourceContractError, load_native_grid,
)
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import (
    _extent_and_remainders, _state, ModelContractError, STATE_ORDER,
)

_GRID_ISSUANCE = object()

CR_CLOCK_SOURCE = {
    "repo": "cosmosapjw-quantum/bass_cr",
    "commit": "5a8e4ac85a19151a3f9625c91d8e87b38f7a32e7",
    "path": "research/cr_c15_duhamel_20261015/src/continuous_source.py",
    "git_blob": "b60f3ef6487b340ecb519f9dd77445caf2975833",
    "function": "proper_dt(model,a0:float,a1:float,q:float)->float",
    "binding": "SIGNATURE_AND_FORMULA_ONLY; owner namespace and HD chemistry NOT_BOUND",
}


def _finite(x: object, label: str, *, positive: bool = False) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)):
        raise ModelContractError(f"{label}: finite real required")
    y = float(x)
    if not math.isfinite(y) or (positive and y <= 0):
        raise ModelContractError(f"{label}: invalid finite value")
    return y


def _rate(grid: NativeGrid, temperature_K: int) -> Fraction:
    if type(grid) is not NativeGrid or grid.source_sha256 != PDF_SHA256:
        raise SourceContractError("R18 verified native PDF grid required")
    return grid.lookup(temperature_K, initial_v=0, initial_j=2,
                       product_v=0, product_j=1, method="SQM").nominal_m3_s


@dataclass(frozen=True)
class Segment:
    temperature_K: int
    duration_s: float
    theta_s: float = 0.0

    def __post_init__(self) -> None:
        if type(self.temperature_K) is not int:
            raise ModelContractError("source temperature must be an exact integer node")
        _finite(self.duration_s, "duration_s", positive=True)
        _finite(self.theta_s, "theta_s")


def _inverse_volume_clock(duration_s: float, theta_s: float, v_start: float) -> tuple[float, float]:
    """I=int_0^dt ds/[v_start*exp(theta*s)], v_end=v_start exp(theta*dt)."""
    dt = _finite(duration_s, "duration_s", positive=True)
    th = _finite(theta_s, "theta_s")
    v = _finite(v_start, "v_start", positive=True)
    z = th * dt
    if not math.isfinite(z) or abs(z) > 650.0:
        raise ModelContractError("guarded expansion exponent exceeded")
    ratio = math.exp(z)
    phi = -math.expm1(-z) / z if z != 0.0 else 1.0
    I = dt / v * phi
    end = v * ratio
    if not (math.isfinite(I) and I > 0 and math.isfinite(end) and end > 0):
        raise ModelContractError("inverse-volume clock/volume overflow or underflow")
    return I, end


@dataclass(frozen=True)
class GridFlow:
    final_state_m_minus3: tuple[float, float, float, float]
    extent_reference_m_minus3: float
    exposure_m3: float
    proper_seconds: float
    volume_ratio: float
    source_rates: tuple[Fraction, ...]
    temperature_nodes_K: tuple[int, ...]
    inverse_volume_seconds: tuple[float, ...]
    segment_exposures_m3: tuple[float, ...]
    source_pdf_sha256: str
    _issuance: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._issuance is not _GRID_ISSUANCE or self.source_pdf_sha256 != PDF_SHA256:
            raise SourceContractError("GridFlow must be issued by verified source-grid solver")

    def as_json(self) -> dict:
        return {
            "schema": "wu.r20.source_grid_exact_flow.v1",
            "state_order": list(STATE_ORDER),
            "state_number_density_m_minus3": list(self.final_state_m_minus3),
            "extent_reference_m_minus3": self.extent_reference_m_minus3,
            "exposure_m3": self.exposure_m3,
            "proper_seconds": self.proper_seconds,
            "volume_ratio": self.volume_ratio,
            "source": {
                "pdf_sha256": self.source_pdf_sha256,
                "method": "SQM",
                "reaction": "H+ + HD(v0,j2) -> D+ + H2(v0,j1)",
                "temperature_nodes_K": list(self.temperature_nodes_K),
                "rates_m3_s_exact": [
                    {"numerator": str(k.numerator), "denominator": str(k.denominator)}
                    for k in self.source_rates],
                "value_kind": "SOURCE_NATIVE_PRINTED_NOMINAL",
                "uncertainty": None,
                "interpolation": False,
                "thermal_spin_applied": False,
                "Boltzmann_population_applied": False,
            },
            "clock": {"inverse_volume_seconds": list(self.inverse_volume_seconds),
                      "segment_exposures_m3": list(self.segment_exposures_m3)},
            "admission": {"owner_HD_consumer": False, "full_A": False,
                          "HH_R10": "OFF", "production": "NOT_ISSUED", "L4": False},
        }


def evolve_source_grid(grid: NativeGrid, initial_m_minus3: Sequence[float],
                       segments: Sequence[Segment]) -> GridFlow:
    """Exact nonautonomous flow for an externally prescribed segment schedule.

    Comoving N=v*n: dN/dt=nu*k(T(t))*N_H*N_HD/v(t).
    All scalar time-dependent generators commute; exposure A=sum k_i*I_i.
    """
    n0 = _state(initial_m_minus3)
    segs = tuple(segments)
    if not segs:
        raise ModelContractError("nonempty source-grid schedule required")
    if any(type(seg) is not Segment for seg in segs):
        raise ModelContractError("only typed Segment entries are supported")
    v = 1.0
    times: list[float] = []
    ks: list[Fraction] = []
    inv: list[float] = []
    exposure_terms: list[float] = []
    for seg in segs:
        k = _rate(grid, seg.temperature_K)
        I, v = _inverse_volume_clock(seg.duration_s, seg.theta_s, v)
        exposure = float(k) * I
        if not math.isfinite(exposure) or exposure < 0:
            raise ModelContractError("exposure overflow")
        times.append(seg.duration_s)
        ks.append(k)
        inv.append(I)
        exposure_terms.append(exposure)
    A = math.fsum(exposure_terms)
    t = math.fsum(times)
    if not math.isfinite(A) or not math.isfinite(t):
        raise ModelContractError("exposure/time sum overflow")
    xi, rem_h, rem_hd = _extent_and_remainders(n0[0], n0[1], 1.0, A)
    out = (rem_h / v, rem_hd / v, (n0[2] + xi) / v, (n0[3] + xi) / v)
    if not all(math.isfinite(x) and x >= 0 for x in out):
        raise ModelContractError("final density overflow")
    return GridFlow(out, xi, A, t, v, tuple(ks),
                    tuple(s.temperature_K for s in segs), tuple(inv),
                    tuple(exposure_terms), grid.source_sha256, _issuance=_GRID_ISSUANCE)


def rate_sensitivities(flow: GridFlow) -> tuple[float, ...]:
    """Conditional d extent/d k_i = I_i N_H(final) N_HD(final).

    These are mathematical tangents, NOT source-rate error intervals.
    """
    if type(flow) is not GridFlow or flow._issuance is not _GRID_ISSUANCE:
        raise SourceContractError("verified GridFlow required for sensitivities")
    h, hd = flow.final_state_m_minus3[:2]
    survivors_product = (h * flow.volume_ratio) * (hd * flow.volume_ratio)
    result = tuple(I * survivors_product for I in flow.inverse_volume_seconds)
    if not all(math.isfinite(x) and x >= 0 for x in result):
        raise ModelContractError("sensitivity overflow")
    return result


@dataclass(frozen=True)
class LogScaleClock:
    temperature_K: int
    proper_seconds_quadrature: float
    inverse_volume_seconds_quadrature: float
    exposure_m3: float
    nodes: int
    cr_source_git_blob: str = CR_CLOCK_SOURCE["git_blob"]
    owner_chemistry_bound: bool = False
    _issuance: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._issuance is not _GRID_ISSUANCE:
            raise SourceContractError("LogScaleClock must be issued by verified clock interface")


def clock_from_hubble(grid: NativeGrid, temperature_K: int, a0: float, a1: float,
                      q: float, hubble: Callable[[float, float], float],
                      volume_ratio: Callable[[float], float], *, nodes: int = 16) -> LogScaleClock:
    """Read-only CR-compatible H(a,q) signature, GLn integration in ln(a).

    dt = d ln a/H(a,q), A = int k(T) d ln a/[H(a,q) v(a)].
    Quadrature is approximate except in special integrands; not an error certificate.
    No actual CR owner model or HD species state is bound by this function.
    """
    from numpy.polynomial.legendre import leggauss
    k = _rate(grid, temperature_K)
    lo = _finite(a0, "a0", positive=True)
    hi = _finite(a1, "a1", positive=True)
    qq = _finite(q, "q")
    if hi <= lo or type(nodes) is not int or not 2 <= nodes <= 128:
        raise ModelContractError("positive increasing scale interval and nodes in [2,128] required")
    if not callable(hubble) or not callable(volume_ratio):
        raise ModelContractError("callable H(a,q) and v(a) required")
    x, w = leggauss(nodes)
    left, right = math.log(lo), math.log(hi)
    half = 0.5 * (right-left)
    middle = 0.5 * (right+left)
    clock_terms: list[float] = []
    weighted_terms: list[float] = []
    for xj, wj in zip(x, w):
        aa = math.exp(middle+half*float(xj))
        H = _finite(hubble(aa, qq), "owner-compatible H(a,q)", positive=True)
        v = _finite(volume_ratio(aa), "external v(a)", positive=True)
        clock_terms.append(float(wj)/H)
        weighted_terms.append(float(wj)/(H*v))
    proper = half * math.fsum(clock_terms)
    inv = half * math.fsum(weighted_terms)
    E = float(k)*inv
    if not all(math.isfinite(z) and z > 0 for z in (proper, inv, E)):
        raise ModelContractError("quadrature time/exposure invalid")
    return LogScaleClock(temperature_K, proper, inv, E, nodes, _issuance=_GRID_ISSUANCE)


def cr_gl2_formula(model: object, a0: float, a1: float, q: float) -> float:
    """Formula-matched, NOT imported, CR proper_dt GL2 reference for audit.

    Actual CR source is pinned in CR_CLOCK_SOURCE. This function does not execute
    the owner module and cannot establish a physical owner-model binding.
    """
    from numpy.polynomial.legendre import leggauss
    lo = _finite(a0, "a0", positive=True)
    hi = _finite(a1, "a1", positive=True)
    qq = _finite(q, "q")
    if hi <= lo or not callable(getattr(model, "hubble", None)):
        raise ModelContractError("owner-compatible model.hubble and increasing a required")
    x, w = leggauss(2)
    la, lb = math.log(lo), math.log(hi)
    aa = [math.exp(0.5*(la+lb)+0.5*(lb-la)*float(xj)) for xj in x]
    result = 0.5*(lb-la)*math.fsum(float(wj)/_finite(model.hubble(aj,qq),"H",positive=True)
                                     for wj,aj in zip(w,aa))
    if not math.isfinite(result) or result <= 0:
        raise ModelContractError("invalid GL2 proper time")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--schedule-json", type=Path, required=True)
    parser.add_argument("--initial-m3", type=float, nargs=4, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.schedule_json.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") != "wu.r20.schedule.v1":
            raise ModelContractError("schedule schema mismatch")
        rows = data.get("segments")
        if not isinstance(rows, list):
            raise ModelContractError("segments must be a list")
        segments = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"temperature_K", "duration_s", "theta_s"}:
                raise ModelContractError("exact segment fields required")
            segments.append(Segment(**row))
        grid = load_native_grid(args.source_pdf)
        out = evolve_source_grid(grid, args.initial_m3, segments)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as f:
            json.dump(out.as_json(), f, indent=2)
            f.write("\n")
    except (OSError, ValueError, SourceContractError, ModelContractError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
