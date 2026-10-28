"""Exact represented-input caloric maps; no ODE, provider execution or activation.

Authority: R5_FINITE_CALORIC_DERIVATION_20261028.md and the source-bath
addendum. C5 is code authoring only: tests and scientific admission are pending.
N denotes thermal particles per common V0; U/Q/W are J per common V0.
cv is J/K per particle, NOT the speed of light. Temperatures are kelvin.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction as F
import hashlib
import json
import math
import re
import sys
from typing import Any

Exact = F | str
ZERO = F(0)
K_B_SI = F("1.380649e-23")
MONATOMIC_CV = F(3, 2) * K_B_SI
UNIT = "finite_thermal_endpoint_20261028"
SOURCE_PIN = "634c3046ffccc5d00f1ab7588b5834a6eb8053ad"
SOURCE_BYTES = 3554206
SOURCE_SHA256 = "a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac"
SOURCE_BLOB = "a9ea559f123da6c8f1fe070139bc80145d4582fc"
LITERAL_BYTES = 8281
LITERAL_SHA256 = "b77aba9612584ffd74e2cdd951c0b9e2b573113bd7195c04d8cc857354cfe34f"
LITERAL_BLOB = "ea4bd58d394a421533407b5d12acf2468b32fdcd"
FINE_ORDER = ("ground", "2s", "2p", "continuum")
ENERGY_ORDER = ("rest_dust", "atomic_internal", "gas_thermal", "ambient_radiation", "outgoing_Lyalpha")
_DECIMAL = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")
_RATIONAL = re.compile(r"[+-]?\d+/\d+\Z")
_HEX = re.compile(r"[+-]?0x[0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?p[+-]?\d+\Z")


def exact(value: Exact) -> F:
    """Reject accidental int/bool/float; decimal strings keep decimal meaning."""
    if type(value) is F:
        return value
    if type(value) is not str:
        raise TypeError("Fraction or explicit decimal/rational string required")
    if not (_DECIMAL.fullmatch(value) or _RATIONAL.fullmatch(value)):
        raise ValueError("invalid exact numeric spelling")
    return F(value)


def _positive(value: Exact, name: str) -> F:
    q = exact(value)
    if q <= 0:
        raise ValueError(name + " must be positive")
    return q


def _nonnegative(value: Exact, name: str) -> F:
    q = exact(value)
    if q < 0:
        raise ValueError(name + " must be nonnegative")
    return q


def _vector(values: tuple[F, ...], n: int) -> tuple[F, ...]:
    if type(values) is not tuple or len(values) != n:
        raise ValueError("immutable tuple of the declared dimension required")
    if any(type(v) is not F for v in values):
        raise TypeError("vector entries must be Fractions")
    return values


@dataclass(frozen=True)
class Endpoint:
    Na: F
    Ta: F
    cv: F
    dN: F
    Q: F
    W: F

    def __post_init__(self) -> None:
        _vector((self.Na, self.Ta, self.cv, self.dN, self.Q, self.W), 6)
        for name in ("Na", "Ta", "cv", "N", "U"):
            if getattr(self, name) <= 0:
                raise ValueError(name + " must be positive")

    @property
    def N(self) -> F:
        return self.Na + self.dN

    @property
    def U(self) -> F:
        return self.cv * self.Na * self.Ta + self.Q + self.W

    @property
    def T(self) -> F:
        return self.U / (self.cv * self.N)

    @property
    def temperature_ratio(self) -> F:
        return self.T / self.Ta

    @property
    def log_energy_argument(self) -> F:
        return self.U / (self.cv * self.Na * self.Ta)

    @property
    def log_count_argument(self) -> F:
        return self.N / self.Na


def finite_endpoint(*, Na: Exact, Ta: Exact, cv: Exact, dN: Exact, Q: Exact, W: Exact) -> Endpoint:
    """R5 sections 1-2. Q and W are signed integrated gas ports, used once."""
    return Endpoint(*(exact(v) for v in (Na, Ta, cv, dN, Q, W)))


@dataclass(frozen=True)
class SavedDiagnostics:
    Ua: F
    Ub: F
    Nb: F
    r0: F
    r_balance: F
    rE: F
    rN: F
    T: F
    temperature_difference: F
    identity_difference: F


def saved_endpoint_diagnostics(p: Endpoint, *, Ua: Exact, Ub: Exact, Nb: Exact) -> SavedDiagnostics:
    """Preserve initial-EOS and interval-balance residuals; never repair them."""
    ua = exact(Ua)  # Independent saved initial value, including a diagnostic mismatch.
    ub, nb = _positive(Ub, "Ub"), _positive(Nb, "Nb")
    r0 = ua - p.cv * p.Na * p.Ta
    rb = ub - ua - p.Q - p.W
    re, rn = r0 + rb, nb - p.N
    t = ub / (p.cv * nb)
    identity = (re * p.N - p.U * rn) / (p.cv * p.N * (p.N + rn))
    return SavedDiagnostics(ua, ub, nb, r0, rb, re, rn, t, t - p.T, identity)


@dataclass(frozen=True)
class EndpointDirection:
    dN: F
    dU: F
    dT: F
    dlogT: F


def endpoint_jvp(p: Endpoint, *, dNa: Exact, dTa: Exact, dcv: Exact, ddN: Exact, dQ: Exact, dW: Exact) -> EndpointDirection:
    a, t, c, n, q, w = map(exact, (dNa, dTa, dcv, ddN, dQ, dW))
    dn = a + n
    du = p.cv * p.Ta * a + p.cv * p.Na * t + p.Na * p.Ta * c + q + w
    dlog = du / p.U - c / p.cv - dn / p.N
    return EndpointDirection(dn, du, p.T * dlog, dlog)


@dataclass(frozen=True)
class Coordinates:
    energy: F
    particles: F


def proper_coordinates(*, U: Exact, N: Exact, R: Exact) -> Coordinates:
    u, n, r = _positive(U, "U"), _positive(N, "N"), _positive(R, "R")
    return Coordinates(u / r, n / r)


def proper_coordinates_jvp(*, U: Exact, N: Exact, R: Exact, dU: Exact, dN: Exact, dR: Exact) -> Coordinates:
    base = proper_coordinates(U=U, N=N, R=R)
    r, du, dn, dr = map(exact, (R, dU, dN, dR))
    return Coordinates(du / r - base.energy * dr / r, dn / r - base.particles * dr / r)


def normalized_coordinates(*, U: Exact, N: Exact, R: Exact, b: Exact) -> Coordinates:
    base = proper_coordinates(U=U, N=N, R=R)
    baryons = _positive(b, "supplied right baryon density")
    return Coordinates(base.energy / baryons, base.particles / baryons)


def normalized_coordinates_jvp(*, U: Exact, N: Exact, R: Exact, b: Exact, dU: Exact, dN: Exact, dR: Exact, db: Exact) -> Coordinates:
    base = proper_coordinates(U=U, N=N, R=R)
    tangent = proper_coordinates_jvp(U=U, N=N, R=R, dU=dU, dN=dN, dR=dR)
    baryons, dbaryons = _positive(b, "b"), exact(db)
    return Coordinates(tangent.energy / baryons - base.energy * dbaryons / baryons**2,
                       tangent.particles / baryons - base.particles * dbaryons / baryons**2)


@dataclass(frozen=True)
class TemperatureInterval:
    lower: F
    upper: F
    scope: str = "CARTESIAN_ENCLOSURE_NOT_PHYSICAL_CERTIFICATE"


def temperature_interval(*, Ulo: Exact, Uhi: Exact, Nlo: Exact, Nhi: Exact, cv: Exact) -> TemperatureInterval:
    ul, uh, nl, nh, c = (_positive(v, k) for v, k in ((Ulo, "Ulo"), (Uhi, "Uhi"), (Nlo, "Nlo"), (Nhi, "Nhi"), (cv, "cv")))
    if ul > uh or nl > nh:
        raise ValueError("reversed interval")
    return TemperatureInterval(ul / (c * nh), uh / (c * nl))


def _radii(p: Endpoint, eE: Exact | None, eN: Exact | None) -> tuple[F, F] | None:
    ee = None if eE is None else _nonnegative(eE, "energy radius")
    en = None if eN is None else _nonnegative(eN, "count radius")
    if en is not None and en >= p.N:
        raise ValueError("count radius must be smaller than positive endpoint count")
    if ee is None or en is None:
        return None
    return ee, en


def temperature_error_bound(p: Endpoint, *, eE: Exact | None, eN: Exact | None) -> F | None:
    radii = _radii(p, eE, eN)
    if radii is None:
        return None
    ee, en = radii
    return (ee * p.N + p.U * en) / (p.cv * p.N * (p.N - en))


def endpoint_interval(p: Endpoint, *, eE: Exact | None, eN: Exact | None) -> TemperatureInterval | None:
    radii = _radii(p, eE, eN)
    if radii is None:
        return None
    ee, en = radii
    return temperature_interval(Ulo=p.U-ee, Uhi=p.U+ee, Nlo=p.N-en, Nhi=p.N+en, cv=p.cv)


@dataclass(frozen=True)
class Segment:
    ratio: F
    count: F
    heat: F
    work: F

    def __post_init__(self) -> None:
        _vector((self.ratio, self.count, self.heat, self.work), 4)
        _positive(self.ratio, "segment volume ratio")


@dataclass(frozen=True)
class SegmentDirection:
    ratio: F
    count: F
    heat: F
    work: F

    def __post_init__(self) -> None:
        _vector((self.ratio, self.count, self.heat, self.work), 4)


def compose_local_segments(a: Segment, b: Segment) -> Segment:
    """Only UNWEIGHTED increments per V0 then V1; J2 is not an input port."""
    return Segment(a.ratio*b.ratio, a.count+a.ratio*b.count,
                   a.heat+a.ratio*b.heat, a.work+a.ratio*b.work)


def compose_local_segments_jvp(a: Segment, b: Segment, da: SegmentDirection, db: SegmentDirection) -> SegmentDirection:
    return SegmentDirection(da.ratio*b.ratio+a.ratio*db.ratio,
                            da.count+da.ratio*b.count+a.ratio*db.count,
                            da.heat+da.ratio*b.heat+a.ratio*db.heat,
                            da.work+da.ratio*b.work+a.ratio*db.work)


def selected_h_thermal_count(stocks: tuple[F, ...], electrons: Exact) -> F:
    values = _vector(stocks, 4)
    if any(x < 0 for x in values):
        raise ValueError("saved H stocks must be nonnegative")
    return sum(values, ZERO) + _nonnegative(electrons, "saved thermal electrons")


def selected_h_event_count(events: tuple[F, ...]) -> F:
    values = _vector(events, 4)
    return sum(values, ZERO) + values[3]


@dataclass(frozen=True)
class BathCounts:
    initial_H: F
    final_H: F
    inert_He: F
    Na: F
    Nb: F
    dN: F
    stock_residuals: tuple[F, ...]
    electron_residual: F
    rN: F


def source_bath_counts(*, initial_stocks: tuple[F, ...], final_stocks: tuple[F, ...], events: tuple[F, ...], electrons_initial: Exact, electrons_final: Exact, NH: Exact, fHe: Exact) -> BathCounts:
    ha = selected_h_thermal_count(initial_stocks, electrons_initial)
    hb = selected_h_thermal_count(final_stocks, electrons_final)
    dn = selected_h_event_count(events)
    inert = _positive(NH, "source reference NH") * _nonnegative(fHe, "source fHe")
    na, nb = _positive(ha+inert, "Na"), _positive(hb+inert, "Nb")
    residuals = tuple(y-x-d for x, y, d in zip(initial_stocks, final_stocks, events))
    electron_residual = exact(electrons_final)-exact(electrons_initial)-events[3]
    return BathCounts(ha, hb, inert, na, nb, dn, residuals, electron_residual, nb-na-dn)


@dataclass(frozen=True)
class BathCountDirection:
    dNa: F
    dNb: F
    ddN: F
    dB: F


def source_bath_counts_jvp(*, NH: Exact, fHe: Exact, dNH: Exact, dfHe: Exact, d_initial_stocks: tuple[F, ...], d_final_stocks: tuple[F, ...], d_events: tuple[F, ...], d_electrons_initial: Exact, d_electrons_final: Exact) -> BathCountDirection:
    nh, fhe = _positive(NH, "NH"), _nonnegative(fHe, "fHe")
    db = fhe*exact(dNH) + nh*exact(dfHe)
    dna = sum(_vector(d_initial_stocks, 4), ZERO) + exact(d_electrons_initial) + db
    dnb = sum(_vector(d_final_stocks, 4), ZERO) + exact(d_electrons_final) + db
    return BathCountDirection(dna, dnb, selected_h_event_count(d_events), db)


def gas_ports(event: tuple[F, ...], work: tuple[F, ...], *, sector_order: tuple[str, ...]) -> tuple[F, F]:
    if type(sector_order) is not tuple or sector_order != ENERGY_ORDER:
        raise ValueError("exact source energy-sector order required")
    return _vector(event, 5)[2], _vector(work, 5)[2]


def decode_source_literal(lexeme: str, encoding: str) -> F:
    """Opt-in source bridge. Does not relax exact() for accidental floats."""
    if type(lexeme) is not str or lexeme.strip() != lexeme:
        raise TypeError("original literal string required")
    if encoding == "SAVED_MP_DECIMAL_STRING":
        if not _DECIMAL.fullmatch(lexeme):
            raise ValueError("saved MP decimal string required")
        return F(lexeme)
    if (sys.float_info.radix, sys.float_info.mant_dig, sys.float_info.max_exp) != (2, 53, 1024):
        raise RuntimeError("source decoder requires binary64 float semantics")
    if encoding == "JSON_NUMBER_VIA_BINARY64":
        value = json.loads(lexeme)
        if type(value) is int:
            return F(value)
        if type(value) is not float:
            raise TypeError("JSON numeric value required")
    elif encoding == "BINARY64_HEX_STRING":
        if not _HEX.fullmatch(lexeme):
            raise ValueError("explicit binary64 hexadecimal spelling required")
        value = float.fromhex(lexeme)
    else:
        raise ValueError("unknown source encoding")
    if not math.isfinite(value):
        raise ValueError("nonfinite source number")
    return F.from_float(value)


def _verify_bytes(raw: bytes, size: int, sha256: str, blob: str) -> None:
    if type(raw) is not bytes:
        raise TypeError("original bytes required")
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != sha256:
        raise ValueError("BYTE_IDENTITY_MISMATCH: immutable scientific input")
    actual_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if actual_blob != blob:
        raise ValueError("BYTE_IDENTITY_MISMATCH: Git blob")


def load_literal_binding(raw: bytes) -> tuple[dict[str, Any], dict[str, F]]:
    """Pin the transcribed 11-field packet; not a substitute for full source."""
    _verify_bytes(raw, LITERAL_BYTES, LITERAL_SHA256, LITERAL_BLOB)
    packet = json.loads(raw)
    if packet["schema"] != "REI_FINITE_THERMAL_LITERAL_BINDING_V1" or packet["source_commit"] != SOURCE_PIN or packet["unit"] != UNIT:
        raise ValueError("literal binding schema/source/unit mismatch")
    rows = packet["literal_readback"]
    names = [row["name"] for row in rows]
    if len(names) != 11 or len(set(names)) != 11:
        raise ValueError("exactly eleven unique literal fields required")
    values = {row["name"]: decode_source_literal(row["lexeme"], row["decoder"]) for row in rows}
    return packet, values


@dataclass(frozen=True)
class TemperatureBridge:
    particle_energy_J: F
    energy_temperature_K: F
    native_temperature_K: F
    energy_minus_native_K: F
    kBoltz_EV_over_kB_SI: F
    theta_minus_kBoltz_native_eV: F


def source_temperature_bridge(*, theta_eV: Exact, EV_J: Exact, kBoltz_source: Exact, native_T_K: Exact) -> TemperatureBridge:
    theta, ev, kb, native = (_positive(v, k) for v, k in ((theta_eV, "theta_eV"), (EV_J, "EV_J"), (kBoltz_source, "kBoltz_source"), (native_T_K, "native_T_K")))
    energy = theta * ev
    temp = energy / K_B_SI
    return TemperatureBridge(energy, temp, native, temp-native, kb*ev/K_B_SI, theta-kb*native)


def _saved_vector(values: Any, n: int) -> tuple[F, ...]:
    if type(values) is not list or len(values) != n:
        raise ValueError("source vector dimension mismatch")
    return tuple(decode_source_literal(x, "SAVED_MP_DECIMAL_STRING") for x in values)


def _saved_rows(values: Any) -> tuple[F, ...]:
    if type(values) is not list or len(values) != 4 or any(type(x) is not list or len(x) != 1 for x in values):
        raise ValueError("four singleton source stock rows required")
    return _saved_vector([x[0] for x in values], 4)


def physical_output_boundary() -> dict[str, Any]:
    """The algebraic module has no operation that activates a physical client."""
    return dict(actual_REI_recipient_bath=None, actual_recipient_nb=None,
                actual_native25=None, actual_temperature_update=None, physical_radii=None,
                full_state_update=False, L4_ready=False, global_physical_completion=None)


def consume_saved_source(raw_source: bytes, raw_literal_packet: bytes) -> dict[str, Any]:
    """Complete opt-in byte-pinned source path. No provider imports or solves.

    Calling this is a new scientific evaluation and needs separate authorization.
    The returned caloric temperatures are source-model diagnostics, not target
    temperature updates. Original decimal residual lexemes are returned intact.
    """
    _verify_bytes(raw_source, SOURCE_BYTES, SOURCE_SHA256, SOURCE_BLOB)
    packet, v = load_literal_binding(raw_literal_packet)
    document = json.loads(raw_source)
    if document.get("schema") != "BASS_QSS_FINITE_SOURCE_CHANNEL_TRANSACTION_V1":
        raise ValueError("source transaction schema mismatch")
    owner = document["finite_owners"]
    if tuple(owner["inventory_order"]) != FINE_ORDER:
        raise ValueError("source fine-stock order mismatch")
    initial, final, events = (_saved_rows(owner[key]) for key in ("initial_stocks", "final_stocks", "stock_change_from_events"))
    ea = decode_source_literal(owner["electrons_initial"], "SAVED_MP_DECIMAL_STRING")
    eb = decode_source_literal(owner["electrons_final"], "SAVED_MP_DECIMAL_STRING")
    counts = source_bath_counts(initial_stocks=initial, final_stocks=final, events=events,
                               electrons_initial=ea, electrons_final=eb,
                               NH=v["NH_reference"], fHe=v["fHe_left"])
    energies = _saved_vector(owner["event_sector_energy_J_m3"], 5)
    work = _saved_vector(owner["geometry_work_J_m3"], 5)
    q, w = gas_ports(energies, work, sector_order=tuple(owner["sector_order"]))
    ua = _saved_vector(owner["initial_sector_energy_J_m3"], 5)[2]
    ub = _saved_vector(owner["final_sector_energy_common_V0_J_m3"], 5)[2]
    ub_proper_saved = _saved_vector(owner["final_sector_energy_J_m3"], 5)[2]
    ratio = _positive(decode_source_literal(owner["right_volume_ratio"], "SAVED_MP_DECIMAL_STRING"), "R")
    bridge = source_temperature_bridge(theta_eV=v["Tm_energy_left"], EV_J=v["EV_J_source"],
                                       kBoltz_source=v["kBoltz_source"], native_T_K=v["Tm_K_left"])
    point = finite_endpoint(Na=counts.Na, Ta=bridge.energy_temperature_K, cv=MONATOMIC_CV,
                            dN=counts.dN, Q=q, W=w)
    saved = saved_endpoint_diagnostics(point, Ua=ua, Ub=ub, Nb=counts.Nb)
    driver_count = v["NH_reference"] * (1 + v["fHe_left"] + v["xe_left"])
    eta_h = sum(initial, ZERO) - v["NH_reference"]
    eta_e = ea - v["NH_reference"] * v["xe_left"]
    rho_u = ua - F(3, 2) * driver_count * bridge.particle_energy_J
    return dict(
        scope="FROZEN_BASS_SOURCE_CALORIC_DIAGNOSTIC_NOT_COUPLED_REI_UPDATE",
        source_identity=dict(commit=SOURCE_PIN, bytes=SOURCE_BYTES, sha256=SOURCE_SHA256, git_blob=SOURCE_BLOB),
        literal_packet_identity=dict(bytes=LITERAL_BYTES, sha256=LITERAL_SHA256, git_blob=LITERAL_BLOB),
        source_literal_records=packet["literal_readback"], decoded_source_values=v,
        representation="Exact rationals of declared binary64 inputs and saved MP-decimal outputs; not exact unprinted MP internals",
        source_energy_encoding=document["energy_unit_encoding"],
        counts=counts, temperature_bridge=bridge, reconstructed_endpoint=point, saved_endpoint=saved,
        source_driver_count=driver_count, eta_H=eta_h, eta_e=eta_e, rho_U=rho_u,
        r0_decomposition=rho_u-F(3, 2)*bridge.particle_energy_J*(eta_h+eta_e),
        NH_minus_endpoint_density_diagnostic=v["NH_reference"]-F(10**6)*v["endpoint_density_diagnostic"],
        gas_event_Q=q, gas_geometry_W=w, source_event_ports_reference_only=energies,
        source_geometry_ports_reference_only=work,
        right_volume_ratio=ratio, saved_proper=proper_coordinates(U=ub, N=counts.Nb, R=ratio),
        gas_energy_volume_encoding_residual=ub/ratio-ub_proper_saved,
        saved_source_residual_lexemes=dict(interface_storage=owner["interface_storage_residual"],
            event_sum=owner["event_energy_sum_residual"], total_work=owner["total_energy_work_identity_residual"]),
        inherited_physical_radii=owner["physical_radii"],
        source_model_temperature_is_not_rate_feedback=True,
        physical=physical_output_boundary(),
    )


def to_wire(value: Any) -> Any:
    """Lossless Fraction records; no float formatting of scientific outputs."""
    if type(value) is F:
        return {"num": str(value.numerator), "den": str(value.denominator)}
    if isinstance(value, Endpoint):
        result = {field.name: to_wire(getattr(value, field.name)) for field in fields(value)}
        result.update({name: to_wire(getattr(value, name)) for name in
                       ("N", "U", "T", "temperature_ratio", "log_energy_argument", "log_count_argument")})
        return result
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: to_wire(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(k): to_wire(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [to_wire(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise TypeError("unsupported scientific serialization type: " + type(value).__name__)
