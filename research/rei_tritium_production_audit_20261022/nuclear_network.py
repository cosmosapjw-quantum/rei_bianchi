"""Conditional passive nuclear-network postprocess on the 82 quotient histories.

The physical closure and accepted coefficient identities are pinned in
NUCLEAR_NETWORK_CONTRACT.json. This module does not advance the background.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import constants as C
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
NETWORK = HERE / "nuclear_intake" / "RUN19_target_network.json"
CONTRACT = HERE / "NUCLEAR_NETWORK_CONTRACT.json"
SPECIES = ("n", "H1", "D", "T", "He3", "He4", "Li6", "Li7")
A = np.array([1, 1, 2, 3, 3, 4, 6, 7], dtype=int)
Z = np.array([0, 1, 1, 1, 2, 2, 3, 3], dtype=int)


@dataclass(frozen=True)
class Channel:
    label: str
    ids: tuple[int, ...]
    left: tuple[tuple[str, int], ...]
    right: tuple[tuple[str, int], ...]
    kind: str

    def vector(self) -> np.ndarray:
        v = np.zeros(len(SPECIES), dtype=int)
        for name, count in self.right:
            v[SPECIES.index(name)] += count
        for name, count in self.left:
            v[SPECIES.index(name)] -= count
        return v


def channels() -> tuple[Channel, ...]:
    """Preserve all 16 source labels while representing three paired reactions once."""
    source = json.loads(NETWORK.read_text())
    rows = {r["id"]: r for r in source["reactions"] if 4 <= r["id"] <= 19}
    groups = ((4,), (5,), (6,), (7, 13), (8, 12), (9,), (10,),
              (11, 19), (14,), (15,), (16,), (17,), (18,))
    answer = []
    for ids in groups:
        row = rows[ids[0]]
        st = row["nuclear_stoichiometry"]
        left, right = st["reactants"], st["products"]
        for other in ids[1:]:
            reverse = rows[other]["nuclear_stoichiometry"]
            if reverse["reactants"] != right or reverse["products"] != left:
                raise ValueError(f"paired source labels disagree: {ids}")
        canon = lambda table: tuple(sorted(("H1" if k == "p" else k, v)
                                            for k, v in table.items()))
        answer.append(Channel(str(ids[0]), ids, canon(left), canon(right), row["kind"]))
    if tuple(sorted(i for c in answer for i in c.ids)) != tuple(range(4, 20)):
        raise ValueError("nuclear source labels incomplete")
    for c in answer:
        v = c.vector()
        if int(A @ v) != 0 or int(Z @ v) != 0:
            if c.ids not in ((9,), (10,)):
                raise ValueError(f"A or Z imbalance in {c.ids}")
            # Beta decays raise nuclear charge by one and emit one electron.
            if int(A @ v) != 0 or int(Z @ v) != 1:
                raise ValueError(f"beta bookkeeping mismatch in {c.ids}")
    return tuple(answer)


def log_constant_s_rate(temp_k: float, s_kev_b: float, mass1_kg: float,
                        mass2_kg: float, z1: int, z2: int) -> float:
    """Maxwellian constant-S charged-particle rate in log(m^3/s).

    S has units energy*area; sigma(E)=S/E*exp[-sqrt(E_G/E)]. Integration
    after shifting at the Gamow maximum retains subnormal physical rates.
    """
    if min(temp_k, s_kev_b, mass1_kg, mass2_kg) <= 0 or min(z1, z2) <= 0:
        raise ValueError("charged-particle input must be positive")
    mu = mass1_kg * mass2_kg / (mass1_kg + mass2_kg)
    kt = C.k * temp_k
    eg = 2 * mu * C.c**2 * (math.pi*C.alpha*z1*z2)**2
    e0 = (eg * kt * kt / 4) ** (1/3)
    a = e0 / kt

    def kernel(u):
        return 0.0 if u <= 0 else math.exp(-a*(u + 2/math.sqrt(u) - 3))

    integ = sum(quad(kernel, lo, hi, epsabs=0, epsrel=2e-10, limit=200)[0]
                for lo, hi in ((0, 1), (1, 4), (4, np.inf)))
    if not integ > 0:
        raise ArithmeticError("nonpositive Gamow integral")
    s_si = s_kev_b * 1e3 * C.electron_volt * 1e-28
    return (math.log(s_si) + .5*math.log(8/(math.pi*mu))
            - 1.5*math.log(kt) + math.log(e0) - 3*a + math.log(integ))


def log_binary_events(log_rate: np.ndarray, n_b: np.ndarray,
                      y1: np.ndarray, y2: np.ndarray,
                      identical: bool = False) -> np.ndarray:
    """Log events/(baryon s); -inf means a structurally absent reactant.

    A finite log is retained even if its linear rate lies below float64's
    smallest subnormal. The caller must report unresolved coefficients
    separately; passing a fictitious zero rate is never the fallback.
    """
    k, nb, a, b = np.broadcast_arrays(log_rate, n_b, y1, y2)
    if np.any(~np.isfinite(nb)) or np.any(nb <= 0) or np.any(a < 0) or np.any(b < 0):
        raise ValueError("invalid binary-event inputs")
    if np.any(np.isnan(k)) or np.any(np.isposinf(k)):
        raise ValueError("invalid rate coefficient")
    out = np.full(k.shape, -np.inf)
    mask = (a > 0) & (b > 0) & np.isfinite(k)
    out[mask] = (k[mask] + np.log(nb[mask]) + np.log(a[mask])
                 + np.log(b[mask]) - (math.log(2) if identical else 0))
    return out


def log_unary_events(log_rate: np.ndarray, inventory: np.ndarray) -> np.ndarray:
    """Log events/(baryon s) for a decay or photonuclear channel."""
    k, y = np.broadcast_arrays(log_rate, inventory)
    if np.any(y < 0) or np.any(np.isnan(k)) or np.any(np.isposinf(k)):
        raise ValueError("invalid unary-event inputs")
    out = np.full(k.shape, -np.inf)
    mask = (y > 0) & np.isfinite(k)
    out[mask] = k[mask] + np.log(y[mask])
    return out


def report_log_value(log_value: float) -> dict:
    """JSON-safe count with an explicit true-zero versus underflow state."""
    if math.isnan(log_value) or log_value == math.inf:
        raise ValueError("invalid logarithmic result")
    if log_value == -math.inf:
        return {"log10": None, "linear": 0.0, "state": "structural_zero"}
    smallest = math.log(np.nextafter(0., 1.))
    return {"log10": log_value/math.log(10),
            "linear": math.exp(log_value) if log_value > smallest else None,
            "state": "finite_underflow" if log_value <= smallest else "represented"}


def cumulative_log_events(time_s: np.ndarray, log_events: np.ndarray) -> np.ndarray:
    """Cumulative events from a log-linear proper-time flux reconstruction.

    A structurally zero endpoint uses a linear birth/death ramp for that
    interval. Both finite endpoints use exact exponential interpolation,
    including arbitrarily narrow endothermic inverse-rate endpoint layers.
    """
    t, r = np.asarray(time_s), np.asarray(log_events)
    if t.ndim != 1 or r.shape != t.shape or not np.all(np.diff(t) > 0):
        raise ValueError("ordered one-dimensional proper-time history required")
    out = np.full(t.shape, -np.inf)
    for i in range(1, len(t)):
        a, b = float(r[i-1]), float(r[i])
        dt = float(t[i]-t[i-1])
        if np.isneginf(a) or np.isneginf(b):
            interval = max(a, b)+math.log(dt/2) if np.isfinite(max(a, b)) else -math.inf
        else:
            gap = abs(b-a)
            interval = (math.log(dt)+max(a, b)
                        + (math.log(-math.expm1(-gap)/gap) if gap else 0.))
        out[i] = np.logaddexp(out[i-1], interval)
    return out


def signed_log_difference(a: float, b: float) -> tuple[int, float]:
    """Sign and natural log magnitude of e**a-e**b without premature linearization."""
    if a == b:
        return 0, -math.inf
    sign, large, small = (1, a, b) if a > b else (-1, b, a)
    return sign, large + math.log(-math.expm1(small-large))


def mass_table() -> dict[str, float]:
    pc = C.physical_constants
    return {"n": pc["neutron mass"][0], "H1": pc["proton mass"][0],
            "D": pc["deuteron mass"][0], "T": pc["triton mass"][0],
            "He3": pc["helion mass"][0], "He4": pc["alpha particle mass"][0],
            "Li6": 6.0151228874*C.atomic_mass-3*C.m_e,
            "Li7": 7.0160034366*C.atomic_mass-3*C.m_e}


def inventory(path: Path) -> dict:
    """Read saved isotope census and proper-time cosmological forcing only."""
    with np.load(path, allow_pickle=False) as d:
        c, cn = d["census"], d["census_names"].tolist()
        diag, dn = d["diagnostics"], d["diagnostic_names"].tolist()
        y = np.zeros((len(c), len(SPECIES)))
        for j, isotope in enumerate(SPECIES):
            prefix = "n_" if isotope == "n" else isotope + "_"
            ix = [i for i, name in enumerate(cn) if name.startswith(prefix)]
            if not ix:
                raise ValueError(f"missing census isotope {isotope}")
            y[:, j] = c[:, ix].sum(axis=1)
        return {"Y": y, "t": diag[:, dn.index("elapsed_s")].copy(),
                "T": diag[:, dn.index("T_K")].copy(),
                "nb": diag[:, dn.index("nB_m3")].copy(),
                "x": d["x"].copy()}


def _sym(items: dict[str, int]) -> int:
    return math.prod(math.factorial(int(v)) for v in items.values())


def _q_j(family: dict, masses: dict[str, float]) -> float:
    r, p = family["reactants"], family["products"]
    defect = (sum(masses[k]*v for k, v in r.items())
              - sum(masses[k]*v for k, v in p.items()))
    if family["kind"] == "beta_minus":
        defect -= C.m_e
    return defect*C.c*C.c


def rate_table(contract: dict, temp: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    """One temperature table shared across cases, with inverse in log units."""
    masses = mass_table()
    spins = dict(zip(contract["nuclear_state_order"], contract["spin_degeneracy"]))
    decay = json.loads((HERE / "EVALUATED_DECAY_INPUTS.json").read_text())
    lt = math.log(2)/(decay["tritium_half_life_years"]*decay["year_days"]
                      *decay["seconds_per_day"])
    ln = 1/decay["neutron_mean_lifetime_s"]
    forward = np.zeros((len(temp), len(contract["families"])))
    reverse = np.full_like(forward, -np.inf)
    qvals = {}
    for j, family in enumerate(contract["families"]):
        kind, model = family["kind"], family["model"]
        r, p = family["reactants"], family["products"]
        qvals[family["id"]] = _q_j(family, masses)
        if model == "constant_S":
            a, b = [name for name, multiplicity in r.items()
                    for _ in range(multiplicity)]
            forward[:, j] = [log_constant_s_rate(float(t), family["S0_keV_b"],
                                                   masses[a], masses[b],
                                                   int(Z[SPECIES.index(a)]),
                                                   int(Z[SPECIES.index(b)]))
                             for t in temp]
        elif model == "one_over_v":
            forward[:, j] = math.log(family["sigma2200_b"]*1e-28*2200.)
        elif model == "decay":
            forward[:, j] = math.log(lt if family["id"] == "t_beta" else ln)
        else:
            raise ValueError(f"unresolved coefficient model {model}")
        if family["reverse"] == "binary_detailed_balance":
            if sum(r.values()) != 2 or sum(p.values()) != 2:
                raise ValueError("binary inverse needs two-body sides")
            factor = (_sym(p)/_sym(r)
                      *math.prod(spins[k]**v for k, v in r.items())
                      /math.prod(spins[k]**v for k, v in p.items())
                      *(math.prod(masses[k]**v for k, v in r.items())
                        /math.prod(masses[k]**v for k, v in p.items()))**1.5)
            reverse[:, j] = forward[:, j]+math.log(factor)-qvals[family["id"]]/(C.k*temp)
        elif family["reverse"] not in ("external_photo_zero",
                                       "not_in_this_lowT_neutrino_free_model"):
            raise ValueError("unknown inverse model")
        if not np.isfinite(forward[:, j]).all():
            raise ArithmeticError(f"nonfinite forward log rate {family['id']}")
    return forward, reverse, {"masses_kg": masses, "Q_J": qvals,
                              "lambda_t_s-1": lt, "lambda_n_s-1": ln,
                              "scipy_constants_version": C.__version__ if hasattr(C, "__version__") else "scipy.constants"}


def _logflux(logk: np.ndarray, nb: np.ndarray, y: np.ndarray,
             reactants: dict[str, int], binary: bool,
             log_override: dict[str, np.ndarray] | None = None) -> np.ndarray:
    out = logk.copy() + (np.log(nb) if binary else 0) - math.log(_sym(reactants))
    for k, mult in reactants.items():
        if log_override is not None and k in log_override:
            out += mult*log_override[k]
        else:
            value = y[:, SPECIES.index(k)]
            out += mult*np.log(np.where(value > 0, value, 1.))
            out[value <= 0] = -np.inf
    return out


def _fast_coefficients(families: list[dict], kf: np.ndarray, kr: np.ndarray,
                       bg: dict) -> tuple[np.ndarray, np.ndarray]:
    """d(T,n)/dt = M(T,n)+s, with inherited bulk isotope reservoirs."""
    y, nb = bg["Y"], bg["nb"]
    m = np.zeros((len(nb), 2, 2))
    logs = np.full((len(nb), 2), -np.inf)
    fast = (SPECIES.index("T"), SPECIES.index("n"))
    for j, family in enumerate(families):
        nu = np.array([family["products"].get(name, 0)
                       -family["reactants"].get(name, 0) for name in ("T", "n")])
        for source, sink, logk in ((family["reactants"], family["products"], kf[:, j]),
                                   (family["products"], family["reactants"], kr[:, j])):
            if not np.isfinite(logk).any():
                continue
            direction = 1 if source == family["reactants"] else -1
            d = direction*nu
            count = sum(source.get(name, 0) for name in ("T", "n"))
            if count > 1:
                raise ValueError(f"fast subsystem is nonlinear: {family['id']}")
            tmp = y.copy()
            tmp[:, fast] = 1.
            logcoef = _logflux(logk, nb, tmp, source, sum(source.values()) == 2)
            if count:
                column = 0 if source.get("T", 0) else 1
                for row in range(2):
                    m[:, row, column] += d[row]*np.exp(logcoef)
            else:
                if np.any(d < 0):
                    raise ValueError("fixed reservoirs cannot directly deplete T or n")
                for row in range(2):
                    if d[row] > 0:
                        logs[:, row] = np.logaddexp(logs[:, row], logcoef+math.log(d[row]))
    return m, logs


def _forcing_weights(hazard: float, dt: float) -> tuple[float, float]:
    q = hazard*dt
    if q < 1e-4:
        ca = q*(.5-q/3+q*q/8-q**3/30+q**4/144)
        cb = q*(.5-q/6+q*q/24-q**3/120+q**4/720)
        return (dt*(.5-q/3+q*q/8-q**3/30+q**4/144),
                dt*(.5-q/6+q*q/24-q**3/120+q**4/720))
    f = -math.expm1(-q)/q
    return (f-math.exp(-q))/hazard, (1-f)/hazard


def propagate_fast(time_s: np.ndarray, m: np.ndarray,
                   log_source: np.ndarray) -> np.ndarray:
    """Positive 2x2 exact interval recurrence for frozen hazard, linear source.

    State/source arithmetic is logarithmic; each interval's hazard is the
    midpoint of endpoint matrices. This retains physical subnormal births.
    """
    out = np.full(log_source.shape, -np.inf)
    eye = np.eye(2)
    for i in range(1, len(time_s)):
        dt = float(time_s[i]-time_s[i-1])
        mat = (m[i-1]+m[i])/2
        a, b, c, d = -mat[0, 0], mat[0, 1], mat[1, 0], -mat[1, 1]
        if min(a, b, c, d) < 0 or a*d-b*c <= 0:
            raise ArithmeticError("fast hazard not positive stable")
        gap = math.hypot(a-d, 2*math.sqrt(b*c))
        fast = -(a+d+gap)/2
        slow = (a*d-b*c)/fast
        pslow = (mat-fast*eye)/(slow-fast)
        es, ef = math.exp(slow*dt), math.exp(fast*dt)
        e = ef*eye+(es-ef)*pslow
        w0s, w1s = _forcing_weights(-slow, dt)
        w0f, w1f = _forcing_weights(-fast, dt)
        w0 = w0f*eye+(w0s-w0f)*pslow
        w1 = w1f*eye+(w1s-w1f)*pslow
        if min(np.min(e), np.min(w0), np.min(w1)) < -1e-12:
            raise ArithmeticError("negative fast propagator")
        for row in range(2):
            terms = []
            for col in range(2):
                for weight, source in ((e[row, col], out[i-1, col]),
                                       (w0[row, col], log_source[i-1, col]),
                                       (w1[row, col], log_source[i, col])):
                    if weight > 0 and np.isfinite(source):
                        terms.append(math.log(weight)+source)
            if terms:
                out[i, row] = np.logaddexp.reduce(terms)
    return out


def evaluate_case(bg: dict, families: list[dict], kf: np.ndarray,
                  kr: np.ndarray) -> dict:
    m, source = _fast_coefficients(families, kf, kr, bg)
    log_fast = propagate_fast(bg["t"], m, source)
    overrides = {"T": log_fast[:, 0], "n": log_fast[:, 1]}
    logs = np.full((len(bg["t"]), len(families), 2), -np.inf)
    for j, f in enumerate(families):
        logs[:, j, 0] = _logflux(kf[:, j], bg["nb"], bg["Y"],
                                 f["reactants"], sum(f["reactants"].values()) == 2,
                                 overrides)
        logs[:, j, 1] = _logflux(kr[:, j], bg["nb"], bg["Y"],
                                 f["products"], sum(f["products"].values()) == 2,
                                 overrides)
    cumulative = np.stack([np.stack([cumulative_log_events(bg["t"], logs[:, j, s])
                                     for s in range(2)], axis=-1)
                           for j in range(len(families))], axis=1)
    return {"log_fast": log_fast, "log_source_fast": source,
            "log_flux": logs, "log_cumulative": cumulative}


def endpoint_ledger(record: dict, families: list[dict], qvals: dict,
                    initial: np.ndarray) -> dict:
    cumulative = record["log_cumulative"]
    gain = [[] for _ in SPECIES]
    loss = [[] for _ in SPECIES]
    family_report = []
    for j, f in enumerate(families):
        nu = {name: f["products"].get(name, 0)-f["reactants"].get(name, 0)
              for name in SPECIES}
        for direction in range(2):
            log_count = float(cumulative[-1, j, direction])
            for idx, name in enumerate(SPECIES):
                contribution = (1 if direction == 0 else -1)*nu[name]
                if contribution:
                    (gain if contribution > 0 else loss)[idx].append(
                        log_count+math.log(abs(contribution)))
        cf, cr = (float(v) for v in cumulative[-1, j])
        sign, net_log = signed_log_difference(cf, cr)
        q = qvals[f["id"]]
        family_report.append({"id": f["id"], "dossier_ids": f["dossier_ids"],
                              "forward": report_log_value(cf),
                              "reverse": (report_log_value(cr) if f["reverse"] ==
                                          "binary_detailed_balance" else
                                          {"state": f["reverse"], "log10": None,
                                           "linear": 0.0}),
                              "net_sign": sign, "net_log10_abs":
                              net_log/math.log(10) if sign else None,
                              "Q_J_per_event": q,
                              "signed_Q_J_per_baryon":
                              {"sign": sign*(1 if q >= 0 else -1),
                               **report_log_value(net_log+math.log(abs(q)))}
                              if q and sign else None})
    changes = []
    max_gross_change = -math.inf
    for i, name in enumerate(SPECIES):
        g = float(np.logaddexp.reduce(gain[i])) if gain[i] else -math.inf
        l = float(np.logaddexp.reduce(loss[i])) if loss[i] else -math.inf
        sign, net = signed_log_difference(g, l)
        if initial[i] > 0:
            max_gross_change = max(max_gross_change, g-math.log(initial[i]),
                                   l-math.log(initial[i]))
        item = {"species": name, "initial": float(initial[i]),
                "gain": report_log_value(g), "loss": report_log_value(l),
                "net_sign": sign, "net_abs": report_log_value(net)}
        if name in ("T", "n"):
            authoritative = float(record["log_fast"][-1, 0 if name == "T" else 1])
            item["event_reconstruction_net"] = {"sign": sign,
                                                 "absolute": report_log_value(net)}
            item["net_sign"] = 1 if np.isfinite(authoritative) else 0
            item["net_abs"] = report_log_value(authoritative)
            item["net_basis"] = "positive_coupled_fast_propagator"
            item["event_reconstruction_basis"] = "independent_loglinear_event_quadrature"
        changes.append(item)
    return {"families": family_report, "changes": changes,
            "max_relative_bulk_gross_change": (math.exp(max_gross_change)
                                               if max_gross_change > -745 else 0.),
            "max_relative_bulk_gross_change_log10": max_gross_change/math.log(10)}


def refine(bg: dict, factor: int) -> dict:
    if factor == 1:
        return bg
    from postprocess import temperature
    x = np.linspace(bg["x"][0], bg["x"][-1], factor*(len(bg["x"])-1)+1)
    y = np.stack([np.interp(x, bg["x"], bg["Y"][:, j])
                  for j in range(len(SPECIES))], axis=1)
    return {"x": x, "t": np.interp(x, bg["x"], bg["t"]),
            "T": temperature(x), "nb": np.interp(x, bg["x"], bg["nb"]),
            "Y": y}


def _stoichiometry_checks(families: list[dict]) -> dict:
    ids = sorted(i for f in families for i in f["dossier_ids"])
    if ids != list(range(4, 20)):
        raise AssertionError("source IDs missing or double counted")
    mat = []
    for f in families:
        nu = np.array([f["products"].get(s, 0)-f["reactants"].get(s, 0)
                       for s in SPECIES])
        if int(A@nu) != 0 or int(Z@nu) != f.get("electrons_created", 0):
            raise AssertionError(f"nuclear A/Z or emitted electron mismatch {f['id']}")
        mat.append(nu)
    return {"dossier_ids": ids, "family_count": len(families),
            "stoichiometry": np.array(mat)}


def _sweep(paths: list[Path], backgrounds: list[dict], families: list[dict],
           contract: dict, factor: int) -> tuple[list[dict], list[dict], dict, np.ndarray]:
    sample = refine(backgrounds[0], factor)
    kf, kr, meta = rate_table(contract, sample["T"])
    records = []
    ledgers = []
    for original in backgrounds:
        bg = refine(original, factor)
        if not np.array_equal(bg["T"], sample["T"]):
            raise ValueError("shared temperature table invalid")
        r = evaluate_case(bg, families, kf, kr)
        records.append(r)
        ledgers.append(endpoint_ledger(r, families, meta["Q_J"], bg["Y"][0]))
    return records, ledgers, meta, sample["T"]


def run() -> dict:
    wall0, cpu0 = time.perf_counter(), time.process_time()
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_FOR_BOUNDED_IMPLEMENTATION":
        raise ValueError("nuclear contract is not frozen")
    families = contract["families"]
    top = _stoichiometry_checks(families)
    paths = sorted((HERE.parent/"rei_isotope_quotient_pilot_20261022"/"pilot"/"results")
                   .glob("quotient_*.npz"))
    if len(paths) != contract["background_count"]:
        raise ValueError("background count changed")
    backgrounds = [inventory(p) for p in paths]
    for b in backgrounds:
        if (not np.all(np.diff(b["t"]) > 0) or np.any(b["nb"] <= 0)
                or np.any(b["Y"] < 0) or np.max(abs(b["Y"]@A-1)) > 1e-8
                or np.any(b["Y"][:, [SPECIES.index("T"), SPECIES.index("n")]] != 0)):
            raise ValueError("inherited background fails nuclear normalization/IC")
    if not all(np.array_equal(b["T"], backgrounds[0]["T"]) for b in backgrounds):
        raise ValueError("temperature backgrounds differ")
    nominal, ledgers, meta, temps = _sweep(paths, backgrounds, families, contract, 1)
    gross = max(l["max_relative_bulk_gross_change"] for l in ledgers)
    if gross >= contract["checks"]["each_bulk_isotope_relative_depletion_max"]:
        raise ArithmeticError("passive reservoir gross-change bound exceeded")
    refined, _, _, _ = _sweep(paths, backgrounds, families, contract, 2)
    def compare(old, new):
        pairs = []
        for a, b in zip(old, new):
            x, y = a["log_cumulative"][-1], b["log_cumulative"][-1]
            both = np.isfinite(x) & np.isfinite(y)
            if np.any(np.isfinite(x) != np.isfinite(y)):
                raise ArithmeticError("structural versus numerical zero changed on refinement")
            if np.any(both):
                pairs.append(float(np.max(abs(x[both]-y[both]))/math.log(10)))
        return max(pairs) if pairs else 0.
    delta12 = compare(nominal, refined)
    fourfold = None
    if delta12 > contract["checks"]["refinement_event_log10_difference_max_dex"]:
        four, _, _, _ = _sweep(paths, backgrounds, families, contract, 4)
        fourfold = compare(refined, four)
    arr = lambda key: np.stack([r[key] for r in nominal])
    result_path = HERE/"NUCLEAR_NETWORK_HISTORIES.npz"
    report_path = HERE/"NUCLEAR_NETWORK_REPORT.json"
    if result_path.exists() or report_path.exists():
        raise FileExistsError("existing network sweep results; preserve original evidence")
    np.savez_compressed(result_path, case_names=np.array([p.stem for p in paths]),
                        family_ids=np.array([f["id"] for f in families]),
                        species=np.array(SPECIES), x=backgrounds[0]["x"],
                        T_K=temps, elapsed_s=np.stack([b["t"] for b in backgrounds]),
                        nB_m3=np.stack([b["nb"] for b in backgrounds]),
                        log_T_n=arr("log_fast"), log_fast_source=arr("log_source_fast"),
                        log_forward_reverse_flux=arr("log_flux"),
                        log_forward_reverse_cumulative=arr("log_cumulative"))
    stable = (fourfold if fourfold is not None else delta12)
    report = {"status": ("PASS_CONDITIONAL_IMPLEMENTATION" if stable <=
                         contract["checks"]["refinement_event_log10_difference_max_dex"]
                         else "HOLD_REFINEMENT"),
              "scope": contract["scope"], "mode": contract["mode"],
              "base_head": contract["base_head"], "background_count": len(paths),
              "new_background_ivps": 0, "family_count": len(families),
              "dossier_ids": top["dossier_ids"],
              "models": {f["id"]: {"forward": f["model"], "reverse": f["reverse"],
                                      "provider": f["provider"]} for f in families},
              "constants": meta,
              "checks": {"max_relative_bulk_gross_change": gross,
                         "max_1x_to_2x_event_difference_dex": delta12,
                         "max_2x_to_4x_event_difference_dex": fourfold,
                         "exact_A_Z_and_beta_electron_stoichiometry": True,
                         "max_background_baryon_residual": max(
                             float(np.max(abs(b["Y"]@A-1))) for b in backgrounds)},
              "case_ledgers": {p.stem: l for p, l in zip(paths, ledgers)},
              "resources": {"wall_s": time.perf_counter()-wall0,
                            "cpu_s": time.process_time()-cpu0},
              "claim_boundary": contract["admission"]}
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if not args.run:
        parser.print_help()
        return
    if not CONTRACT.exists():
        raise FileNotFoundError("frozen nuclear-network physics contract is required")
    report = run()
    print(json.dumps({k: v for k, v in report.items() if k != "case_ledgers"},
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
