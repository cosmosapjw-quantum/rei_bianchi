#!/usr/bin/env python3
"""Independent, bounded verification of the new PHYS83 finite H I implementation.

This is not the scientific 132/324/732-row study.  It never calls its runner.
The rate reference integrates raw-source W-linear cells directly with QUADPACK;
the population reference uses an 80-decimal 6x6 augmented generator exponential.
No production cell-moment helper or production spectral solution is a reference.

Run only under the session's shared resource lease, with one worker/thread.
Each invocation requires a new output directory.  A failed attempt is preserved.
For a repair, select affected or unfinished case IDs; completed, unaffected cases
may be explicitly reused with --reuse-passed-from, never silently overwritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from types import SimpleNamespace

UNIT = Path(__file__).resolve().parents[1]
SOURCE = UNIT / "source"
RAW = UNIT / "source_data"
TEMPERATURES = (255.0, 777.0, 3500.0, 12000.0, 25370.66308424773, 50000.0)
GAP = 10.20435
# Constants are stated independently here, rather than imported from production.
K_B = 1.380649e-23 / 1.602176634e-19
AREA = (100.0 * 5.29177210544e-11) ** 2
PREF = 100.0 * math.sqrt(8.0 * 1.602176634e-19 / (math.pi * 9.1093837139e-31))
A_TWO, A_M1, A_E1 = 8.229, 2.496e-6, 626000000.0
PINNED_RAW = {
    "CCC_2S.1S": "e8e0092e7be97abe4a90ce100e3101d1f6f225eee2d4ad1ba740f57de819997b",
    "CCC_2P.1S": "12cf46fa0904a5b227092a0a6a3ae6d8a20c041cf11c2981d3bb8bd1f6ac313d",
    "CCC_1S.2S": "f4afdbdeccc49a58055ab86750b14ce10dd2091da55bd380a19f3d7a13c337d0",
    "CCC_1S.2P": "00857e46838c5538da8b047363105b306bc1ba5c827700161749d5d712fa0e5a",
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def label(x):
    return format(x, ".17g").replace("+", "")


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


class GateFailure(AssertionError):
    pass


class Recorder:
    def __init__(self, path):
        self.path = path
        self.stream = (path / "checks.jsonl").open("x", encoding="utf-8")
        self.checks = 0
        self.current = None
        self.results = []
        self.metrics = {}
        self.counters = Counter()
        self.checked_steps = {}

    def emit(self, obj):
        self.stream.write(json.dumps(safe(obj), ensure_ascii=False, allow_nan=False) + "\n")
        self.stream.flush()

    def check(self, name, condition, **details):
        self.checks += 1
        passed = bool(condition)
        row = {"case": self.current, "check": name, "pass": passed, **details}
        self.emit(row)
        if not passed:
            raise GateFailure(json.dumps(safe(row), ensure_ascii=False))

    def absolute(self, name, actual, expected, bound):
        error = abs(float(actual) - float(expected))
        self.check(name, math.isfinite(error) and error <= bound,
                   actual=actual, reference=expected, absolute_error=error, bound=bound)
        self.maximum(name + ":abs", error)

    def relative(self, name, actual, expected, bound, zero_abs=0.0):
        actual, expected = float(actual), float(expected)
        if expected == 0:
            return self.absolute(name + ":exact_zero", actual, 0.0, zero_abs)
        error = abs(actual / expected - 1.0)
        self.check(name, math.isfinite(error) and error <= bound,
                   actual=actual, reference=expected, relative_error=error, bound=bound)
        self.maximum(name + ":rel", error)

    def maximum(self, name, value):
        self.metrics[name] = max(self.metrics.get(name, 0.0), float(value))

    def reject(self, name, callback, expected=(ValueError, TypeError)):
        try:
            callback()
        except expected as exc:
            self.check(name, True, rejection=type(exc).__name__, reason=str(exc))
        else:
            self.check(name, False, reason="invalid input was admitted")

    def run(self, case, group, callback):
        self.current = case
        before = self.checks
        start = time.monotonic()
        self.emit({"case": case, "event": "START", "utc": utc()})
        try:
            callback()
            status = "PASS"
            reason = None
        except Exception as exc:
            status = "FAIL"
            reason = str(exc)
            self.emit({"case": case, "event": "EXCEPTION", "type": type(exc).__name__,
                       "reason": reason, "traceback": traceback.format_exc()})
        result = {"case": case, "group": group, "status": status,
                  "checks": self.checks - before,
                  "elapsed_seconds": time.monotonic() - start, "reason": reason}
        self.results.append(result)
        self.emit({"event": "CASE_RESULT", **result})
        print(json.dumps({"case": case, "status": status, "checks": result["checks"]}), flush=True)
        return status == "PASS"


def read_forward(level):
    """Independent raw-column parser, with decimal source-knot subtraction."""
    content = (RAW / f"CCC_{level}.1S").read_text(encoding="utf-8")
    points = []
    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split()
        energy, sigma = Decimal(columns[0]), Decimal(columns[1])
        points.append((float(energy - Decimal("10.20435")),
                       float(energy) * float(sigma) * AREA))
    return points


def quadrature_reference(points, temperature, quad):
    """Integrate epsilon^n W(epsilon) exp(-epsilon/theta), n=0,1.

    The linear polynomial is evaluated inside each quadrature integrand.  No
    incomplete gamma function, production Jn helper, or moment recurrence occurs.
    Scaling W and factoring a positive cell-left exponential avoid tiny epsabs
    failures; the returned physical moments remain in eV and cm^2 units.
    """
    theta = K_B * temperature
    scale = max(w for _, w in points)
    terms = [[], []]
    errors = [[], []]
    active = 0
    for (left, wl), (right, wr) in zip(points, points[1:]):
        h = right - left
        left_weight = math.exp(-left / theta)
        if left_weight == 0:
            continue
        active += 1
        w0, dw = wl / scale, (wr - wl) / scale
        for order in (0, 1):
            def integrand(u):
                e = left + h * u
                return (w0 + dw * u) * e ** order * math.exp(-h * u / theta)
            integral, error = quad(integrand, 0.0, 1.0, epsabs=0.0,
                                   epsrel=2e-12, limit=100)
            multiplier = scale * h * left_weight
            terms[order].append(multiplier * integral)
            errors[order].append(multiplier * error)
    m0, m1 = (math.fsum(row) for row in terms)
    return m0, m1, [math.fsum(row) for row in errors], active


def mp_generator_reference(rate_s, rate_p, ne, t, mp):
    """Independent Markov generator plus occupation-integral augmentation.

    Rates are the float64 operands supplied to production.  They have a separate
    independent raw-source quadrature test.  Converting operands exactly to mp80
    separates population algorithm error from uncertainty in the collision data.
    """
    density, duration = mp.mpf(ne), mp.mpf(t)
    a_s = density * mp.mpf(rate_s.q_up_cm3_s)
    a_p = density * mp.mpf(rate_p.q_up_cm3_s)
    c_s = density * mp.mpf(rate_s.q_down_cm3_s)
    c_p = density * mp.mpf(rate_p.q_down_cm3_s)
    atwo, am1, ae1 = map(mp.mpf, (A_TWO, A_M1, A_E1))
    ds, dp = c_s + atwo + am1, c_p + ae1
    g = mp.matrix([[-a_s-a_p, ds, dp], [a_s, -ds, 0], [a_p, 0, -dp]])
    augmented = mp.zeros(6)
    for i in range(3):
        for j in range(3):
            augmented[i, j] = g[i, j]
        augmented[i + 3, i] = 1
    initial = mp.matrix([1, 0, 0, 0, 0, 0])
    state = mp.expm(duration * augmented) * initial
    pg, ps, pp, jg, js, jp = state
    ups, upp = a_s*jg, a_p*jg
    downs, downp = c_s*js, c_p*jp
    two, m1, e1 = atwo*js, am1*js, ae1*jp
    gap = mp.mpf(GAP)
    atomic, radiation = gap*(ps+pp), gap*(two+m1+e1)
    thermal = -gap*(ups+upp-downs-downp)
    return {
        "population_ground": pg, "population_2s": ps, "population_2p": pp,
        "integral_ground_s": jg, "integral_2s_s": js, "integral_2p_s": jp,
        "excitation_2s_events": ups, "excitation_2p_events": upp,
        "deexcitation_2s_events": downs, "deexcitation_2p_events": downp,
        "two_photon_events": two, "M1_events": m1, "E1_events": e1,
        "emitted_photons": 2*two+m1+e1,
        "atomic_excitation_eV": atomic, "escaped_radiation_eV": radiation,
        "thermal_change_eV": thermal, "heat_withdrawal_eV": -thermal,
        "raw_event_thermal_change_eV": thermal,
        "gross_energy_scale_eV": gap*(ups+upp+downs+downp+two+m1+e1+ps+pp),
        "reference_residual_eV": thermal+atomic+radiation,
    }


def build_cases(rec, np, mp, quad, ce, star):
    cases = []
    channels = ce.load_channels()
    raw_points = {level: read_forward(level) for level in ("2S", "2P")}
    rate_cache = {}
    completed_steps = {tuple(row["parameters"]):SimpleNamespace(**row["values"])
                       for row in rec.checked_steps.values()}

    def add(case, group, callback):
        cases.append((case, group, callback))

    def get_rates(temperature):
        if temperature not in rate_cache:
            rate_cache[temperature] = tuple(channels[level].evaluate(temperature) for level in ("2S", "2P"))
            rec.counters["production_rate_evaluations_for_population_inputs"] += 2
        return rate_cache[temperature]

    def source_case():
        for filename, expected in PINNED_RAW.items():
            rec.check("raw_identity:" + filename, sha(RAW / filename) == expected)
        for level, channel in channels.items():
            points = raw_points[level]
            rec.check("forward_row_count:" + level, len(points) == 452)
            rec.absolute("finite_support_left", points[0][0], 0.0, 0.0)
            rec.absolute("finite_support_right", points[-1][0], 958.40145, 0.0)
            rec.absolute("forward_threshold_zero_W", points[0][1], 0.0, 0.0)
            for name in ("energy_eV", "sigma_a0sq", "sigma_cm2", "epsilon_eV", "W_eV_cm2"):
                array = getattr(channel, name)
                rec.check("one_dimensional_source:" + name, array.shape == (452,))
                rec.check("source_readonly:" + name, not array.flags.writeable)
                rec.reject("source_no_write_flag:" + name,
                           lambda array=array: array.setflags(write=True), (ValueError,))
            rec.check("reverse_shape", channel.reverse_energy_eV.shape == (451,))
            rec.check("raw_decimal_knots", np.max(np.abs(channel.epsilon_eV - np.array([p[0] for p in points]))) < 2e-13)
            rec.check("W_is_incident_times_forward_sigma", np.allclose(
                channel.W_eV_cm2, np.array([p[1] for p in points]), rtol=1e-14, atol=0.0))
            rec.reject("channel_attribute_immutable", lambda channel=channel: setattr(channel, "gap_eV", 9.0),
                       (FrozenInstanceError, AttributeError))
            rec.reject("source_element_immutable", lambda channel=channel: channel.W_eV_cm2.__setitem__(1, 9.0),
                       (ValueError,))
        corrupt = rec.path / "deliberately_corrupt_source_guard"
        corrupt.mkdir()
        (corrupt / "CCC_2S.1S").write_bytes((RAW / "CCC_2S.1S").read_bytes() + b" ")
        rec.reject("altered_raw_identity_rejected", lambda: ce.MatchedCEChannel("2S", corrupt), (ValueError,))
        rec.counters["parent_print_rounding_checks_reexecuted"] = 0
    add("source_geometry_identity_immutability", "guards", source_case)

    def rate_case(level, temperature):
        channel = channels[level]
        actual = channel.evaluate(temperature)
        rec.counters["production_rate_evaluations_in_rate_cases"] += 1
        m0, m1, error, active = quadrature_reference(raw_points[level], temperature, quad)
        rec.counters["independent_rate_reference_pairs"] += 1
        rec.counters["direct_cell_scalar_quadratures"] += 2*active
        for field, expected in (("M0_eV2_cm2", m0), ("M1_eV3_cm2", m1)):
            rec.relative("M0_M1_direct_quadrature", getattr(actual, field), expected, 1e-10)
        rec.check("quadrature_estimated_error", max(error[0]/m0, error[1]/m1) < 1e-10,
                  relative_error_estimates=[error[0]/m0, error[1]/m1], active_cells=active)
        theta, mean = K_B*temperature, m1/m0
        logcommon = math.log(PREF) - 1.5*math.log(theta) + math.log(m0)
        weight = 1.0 if level == "2S" else 3.0
        logup, logdown = logcommon-GAP/theta, logcommon-math.log(weight)
        rec.relative("q_up_direct_quadrature", actual.q_up_cm3_s, math.exp(logup), 1e-10)
        rec.relative("q_down_direct_quadrature", actual.q_down_cm3_s, math.exp(logdown), 1e-10)
        rec.absolute("log_q_up_reference", actual.log_q_up_cm3_s, logup, 2e-12)
        rec.absolute("log_q_down_reference", actual.log_q_down_cm3_s, logdown, 2e-12)
        rec.absolute("log_detailed_balance", actual.log_q_up_cm3_s-actual.log_q_down_cm3_s,
                     math.log(weight)-GAP/theta, 2e-12)
        rec.relative("mean_incoming_up", actual.mean_incoming_up_eV, GAP+mean, 1e-10)
        rec.relative("mean_incoming_down", actual.mean_incoming_down_eV, mean, 1e-10)
        rec.check("scalar_outputs_no_broadcast", all(isinstance(getattr(actual, key), float) for key in (
            "q_up_cm3_s", "q_down_cm3_s", "M0_eV2_cm2", "M1_eV3_cm2")))
        rec.check("finite_source_scope", actual.finite_source_only is True)
        rec.check("underflow_flags_coherent", actual.float64_underflow_up == (actual.q_up_cm3_s == 0.0)
                  and actual.float64_underflow_down == (actual.q_down_cm3_s == 0.0))
        h = temperature*1e-4
        if temperature == 255.0:
            offsets, weights, stencil = (0,1,2,3,4), (-25,48,-36,16,-3), "forward_domain_edge"
        elif temperature == 50000.0:
            offsets, weights, stencil = (0,-1,-2,-3,-4), (25,-48,36,-16,3), "backward_domain_edge"
        else:
            offsets, weights, stencil = (-2,-1,1,2), (1,-8,8,-1), "centered_interior"
        nearby = [actual if offset == 0 else channel.evaluate(temperature+offset*h) for offset in offsets]
        rec.counters["production_rate_evaluations_for_derivative_stencils"] += sum(offset != 0 for offset in offsets)
        for direction, incoming in (("up", GAP+mean), ("down", mean)):
            field = "dlogq_" + direction + "_dT_K_inv"
            derivative = getattr(actual, field)
            reference = (incoming/theta - 1.5)/temperature
            scaled = abs(derivative-reference)/max(abs(reference), 1.0/temperature)
            rec.check("derivative_reference", scaled <= 1e-7, direction=direction, scaled_error=scaled)
            rec.maximum("derivative_quadrature_scaled", scaled)
            fd = math.fsum(weight*getattr(value, "log_q_"+direction+"_cm3_s")
                           for value,weight in zip(nearby,weights))/(12.0*h)
            scaled_fd = abs(fd-derivative)/max(abs(derivative), 1.0/temperature)
            rec.check("derivative_finite_difference", scaled_fd <= 1e-7, direction=direction,
                      stencil=stencil, step_K=h, scaled_error=scaled_fd)
            rec.maximum("derivative_fd_scaled", scaled_fd)
            q = getattr(actual, "q_"+direction+"_cm3_s")
            dq = getattr(actual, "dq_"+direction+"_dT_cm3_s_K")
            scaled_dq = abs(dq-q*reference)/max(abs(q*reference),abs(q)/temperature)
            rec.check("dq_chain_rule_scaled",scaled_dq<=1e-7,direction=direction,scaled_error=scaled_dq)
            rec.maximum("dq_scaled",scaled_dq)
    for level in ("2S", "2P"):
        for temperature in TEMPERATURES:
            add("rate_"+level+"_T"+label(temperature), "rates",
                lambda level=level,temperature=temperature: rate_case(level,temperature))

    def pop_case(temperature, density, duration):
        rates = get_rates(temperature)
        model = star.FrozenHIStar(*rates, density)
        actual = model.step(duration)
        reference = mp_generator_reference(*rates, density, duration, mp)
        rec.counters["mp80_augmented_6x6_expm"] += 1
        rec.counters["production_transient_verification_calls"] += 1
        for field in ("population_ground", "population_2s", "population_2p"):
            value, ref = getattr(actual, field), reference[field]
            rec.absolute("population_absolute", value, ref, 2e-12)
            # Stronger than a macroscopic population floor: all representable
            # positive references >=1e-280 are also required to pass relative.
            if abs(ref) >= mp.mpf("1e-280"):
                rec.relative("population_resolved_relative", value, ref, 1e-8)
            rec.check("population_nonnegative_no_clipping", value >= 0.0)
        for field, ref in reference.items():
            if field.startswith("population_") or field == "reference_residual_eV":
                continue
            value = getattr(actual, field)
            if ref == 0:
                rec.absolute("zero_count_or_ledger:"+field, value, 0.0, 0.0)
            elif abs(ref) >= mp.mpf("1e-280"):
                rec.relative("count_integral_energy_relative", value, ref, 1e-8)
            rec.check("finite_count_or_ledger", math.isfinite(value), field=field)
        gross = reference["gross_energy_scale_eV"]
        residual = abs(reference["reference_residual_eV"] / gross) if gross else mp.mpf(0)
        rec.check("mp80_reference_internal_conservation", residual < mp.mpf("1e-50"),
                  normalized_residual=mp.nstr(residual, 20))
        rec.absolute("nuclei_residual", actual.nuclei_residual, 0.0, 2e-13)
        rec.absolute("raw_energy_normalized", actual.normalized_raw_energy_residual, 0.0, 2e-11)
        rec.absolute("thermal_withdrawal_opposite_sign", actual.thermal_change_eV,
                     -actual.heat_withdrawal_eV, 0.0)
        rec.check("population_scope", actual.finite_star_only is True and actual.prescribed_bath is True)
        for upper, population, up, down, radiation in (
            ("2s",actual.population_2s,actual.excitation_2s_events,actual.deexcitation_2s_events,
             actual.two_photon_events+actual.M1_events),
            ("2p",actual.population_2p,actual.excitation_2p_events,actual.deexcitation_2p_events,actual.E1_events)):
            scale = max(abs(up),abs(down),abs(radiation),abs(population))
            normalized = abs(math.fsum((up,-down,-radiation,-population)))/scale if scale else 0.0
            rec.check("upper_event_balance", normalized <= 2e-11, upper=upper, normalized_residual=normalized)
        completed_steps[(temperature,density,duration)] = actual
        rec.checked_steps[rec.current] = {
            "parameters":[temperature,density,duration], "values":asdict(actual)}
        rec.emit({"case":rec.current,"reference_algorithm":"mp80 expm augmented 6x6", 
                  "production_branch":actual.numerical_branch,
                  "representative_values":{key:float(reference[key]) for key in (
                      "population_2s","population_2p","escaped_radiation_eV","thermal_change_eV")}})
    # 28 transient cases, plus 6 steady and 6 root-helper references below: 40 bounded
    # numerical population-related references; no requested science grid loop.
    density_times = (
        (0.0, (0.0, 1e3)),
        (1.0, (1e-20, 1e-8, 1e3)),
        (1e8, (1e-12, .1)),
        (1e12, (1e-8, .1, 1e3)),
        (1e18, (1e-20, 1e-12, .1, 1e3)),
    )
    for temperature in (3500.0,25370.66308424773):
        for density,times in density_times:
            for duration in times:
                key = (temperature,density,duration)
                add("star_T"+label(temperature)+"_ne"+label(density)+"_t"+label(duration), "populations",
                    lambda key=key: pop_case(*key))

    def steady_case(temperature,density):
        rs,rp = get_rates(temperature)
        model = star.FrozenHIStar(rs,rp,density)
        actual = model.steady()
        ne = mp.mpf(density)
        ass,app = ne*mp.mpf(rs.q_up_cm3_s), ne*mp.mpf(rp.q_up_cm3_s)
        css,cpp = ne*mp.mpf(rs.q_down_cm3_s), ne*mp.mpf(rp.q_down_cm3_s)
        a_s = mp.mpf(A_TWO)+mp.mpf(A_M1)
        a_p = mp.mpf(A_E1)
        ds,dp = css+a_s,cpp+a_p
        # Solve independent generator balance plus nuclei sum, rather than use
        # the implementation's ratios rs/(1+rs+rp).
        balance = mp.matrix([[ass,-ds,0],[app,0,-dp],[1,1,1]])
        pg,ps,pp = mp.lu_solve(balance,mp.matrix([0,0,1]))
        refs = {
            "population_ground":pg,"population_2s":ps,"population_2p":pp,
            "critical_density_2s_cm3":a_s/mp.mpf(rs.q_down_cm3_s),
            "critical_density_2p_cm3":a_p/mp.mpf(rp.q_down_cm3_s),
            "radiative_events_2s_per_s":a_s*ps,"radiative_events_2p_per_s":a_p*pp,
            "escaped_power_eV_per_s":mp.mpf(GAP)*(a_s*ps+a_p*pp),
            "emitted_photons_per_s":(2*mp.mpf(A_TWO)+mp.mpf(A_M1))*ps+a_p*pp,
            "coronal_reference_power_eV_per_s":mp.mpf(GAP)*(ass+app),
        }
        for field,ref in refs.items():
            value = getattr(actual,field)
            if field.startswith("population_"):
                rec.absolute("steady_population_absolute",value,ref,2e-12)
            rec.relative("steady_reference_relative",value,ref,1e-8)
        if density:
            for upper,flux,excitation in (("2s",a_s*ps,ass),("2p",a_p*pp,app)):
                rec.relative("steady_coronal_ratio",getattr(actual,"exact_to_coronal_"+upper),flux/excitation,1e-8)
                rec.relative("steady_coronal_overestimate",getattr(actual,"coronal_relative_overestimate_"+upper),
                             excitation/flux-1,1e-8)
        rec.counters["mp80_steady_generator_linear_solves"] += 1
        rec.counters["production_steady_verification_calls"] += 1
    for temperature in (3500.0,25370.66308424773):
        for density in (0.0,1e8,1e18):
            add("steady_T"+label(temperature)+"_ne"+label(density),"steady",
                lambda temperature=temperature,density=density: steady_case(temperature,density))

    def root_case(slow,fast,duration):
        h,g,h2,h3,branch = star._divided_integrals(slow,fast,fast-slow,duration)
        s,f,t = map(mp.mpf,(slow,fast,duration))
        h_ref = mp.quad(lambda u: mp.exp(-f*u),[0,t])
        g_ref = mp.quad(lambda u: (t-u)*mp.exp(-f*u),[0,t])
        if s == f:
            kernel = lambda u: u*mp.exp(-s*u)
        else:
            kernel = lambda u: mp.exp(-s*u)*(-mp.expm1(-(f-s)*u))/(f-s)
        h2_ref = mp.quad(kernel,[0,t])
        h3_ref = mp.quad(lambda u:(t-u)*kernel(u),[0,t])
        for name,value,ref in (("h_fast",h,h_ref),("G_fast",g,g_ref),("H2",h2,h2_ref),("H3",h3,h3_ref)):
            rec.relative("root_limit:"+name,value,ref,1e-10)
        rec.emit({"case":rec.current,"production_branch":branch,
                  "reference":"mp80 direct smooth-kernel quadrature; repeated-root derivative limit"})
        rec.counters["synthetic_root_limit_cases"] += 1
        return h,g,h2,h3,branch
    for index,roots in enumerate(((1.0,1.0,1e-20),(1.0,1.0,3.0))):
        add("synthetic_root_limit_"+str(index),"synthetic",lambda roots=roots:root_case(*roots))
    def root_boundary(left,right,boundary):
        left_values=root_case(*left)
        right_values=root_case(*right)
        rec.check("branch_boundary_crossed",left_values[4]!=right_values[4],boundary=boundary,
                  left_branch=left_values[4],right_branch=right_values[4])
        for index,name in ((2,"H2"),(3,"H3")):
            rec.relative("branch_boundary_continuity:"+name,left_values[index],right_values[index],1e-10)
    add("synthetic_root_limit_2","synthetic",lambda:root_boundary(
        (1.0,2.0,.25*(1-1e-12)),(1.0,2.0,.25*(1+1e-12)),"fast*t=1/2"))
    add("synthetic_root_limit_3","synthetic",lambda:root_boundary(
        (1.0,1.25-1e-12,3.0),(1.0,1.25+1e-12,3.0),"gap/slow=1/4"))

    def domain_guards():
        channel=channels["2S"]
        for value in (True,False,float("nan"),float("inf"),-1.0,254.999,50000.001,0.0,"3500",[3500],complex(3500,0),np.array([3500,12000]),np.array(3500)):
            rec.reject("temperature_domain_or_shape",lambda value=value:channel.evaluate(value))
        for value in ("He1","Li1","H2",None,1,True):
            rec.reject("species_guard",lambda value=value:channel.evaluate(3500,species=value))
        for value in (True,1,"false",None):
            rec.reject("full_rate_scope_guard",lambda value=value:channel.evaluate(3500,full_physical_rate=value))
        for value in ("2s","3S","1S",None,2):
            rec.reject("level_scope_guard",lambda value=value:ce.MatchedCEChannel(value))
        rs,rp=get_rates(3500.0)
        for value in (True,-1.0,1e18+1e5,float("nan"),float("inf"),[1.0],np.array([1.0]),"1"):
            rec.reject("density_domain_or_shape",lambda value=value:star.FrozenHIStar(rs,rp,value))
        for owner,flag in (("native",False),("detached_own_spontaneous",True),("detached_own_spontaneous",1),
                           (None,False),("detached_own_spontaneous",None)):
            rec.reject("radiative_owner_guard",lambda owner=owner,flag=flag:star.FrozenHIStar(rs,rp,1,
                       radiative_owner=owner,native_radiative_owner=flag))
        model=star.FrozenHIStar(rs,rp,1)
        for value in (True,-1e-20,1000.001,float("nan"),float("inf"),np.array([1]),"1",complex(1,0)):
            rec.reject("time_domain_or_shape",lambda value=value:model.step(value))
        rec.reject("channel_order_guard",lambda:star.FrozenHIStar(rp,rs,1))
        rec.reject("common_temperature_guard",lambda:star.FrozenHIStar(rs,replace(rp,temperature_K=3501),1))
        rec.reject("rate_object_type_guard",lambda:star.FrozenHIStar(object(),rp,1))
        for mutation in (
            {"q_up_cm3_s":2*rs.q_up_cm3_s},
            {"log_q_up_cm3_s":float("nan")},
            {"log_q_down_cm3_s":float("nan")},
            {"q_up_cm3_s":-rs.q_up_cm3_s},
            {"q_down_cm3_s":0.0},
            {"float64_underflow_up":True},
            {"finite_source_only":False},
        ):
            rec.reject("forged_rate_contract_guard",lambda mutation=mutation:star.FrozenHIStar(replace(rs,**mutation),rp,1))
        rec.reject("common_out_of_domain_rate_temperature",lambda:star.FrozenHIStar(
            replace(rs,temperature_K=100000),replace(rp,temperature_K=100000),1))
        for obj,field in ((rs,"q_up_cm3_s"),(model,"electron_density_cm3")):
            rec.reject("public_dataclass_immutable",lambda obj=obj,field=field:setattr(obj,field,9),
                       (FrozenInstanceError,AttributeError))
        rec.counters["scientific_grid_callbacks"] = 0
        rec.counters["cosmological_ODE_callbacks"] = 0
    add("domain_owner_rate_object_guards","guards",domain_guards)

    def mutant_checks():
        # Reuse already computed reference-checked steps; never add a transient
        # call only to manufacture an attractive mutant example.
        prompt_candidates=[]
        pair_candidates=[]
        for key,result in completed_steps.items():
            prompt=GAP*(result.excitation_2s_events+result.excitation_2p_events)
            correct=result.escaped_radiation_eV
            if prompt>0:
                prompt_candidates.append((abs(prompt-correct)/prompt,key))
            if result.two_photon_events>0:
                wrong=GAP*(2*result.two_photon_events+result.M1_events+result.E1_events)
                # The per-event error is exactly one extra gap, even if the
                # two-photon branch is swamped in a total high-density ledger.
                pair_candidates.append((abs((wrong-correct)/(GAP*result.two_photon_events)-1),key))
                rec.relative("two_gamma_number_not_energy",result.emitted_photons,
                             2*result.two_photon_events+result.M1_events+result.E1_events,1e-14)
        rec.check("prompt_cooling_mutant_discriminated",bool(prompt_candidates)
                  and max(x[0] for x in prompt_candidates)>1e-2,
                  strongest=max(prompt_candidates) if prompt_candidates else None)
        rec.check("double_gap_two_photon_mutant_discriminated",bool(pair_candidates)
                  and min(x[0] for x in pair_candidates)<1e-8,
                  best=min(pair_candidates) if pair_candidates else None)
        rec.counters["physical_mutants_discriminated"] = 2
    add("prompt_cooling_and_double_gap_mutants","mutants",mutant_checks)
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True,help="New create-only attempt directory")
    parser.add_argument("--groups",default="guards,rates,populations,steady,synthetic,mutants")
    parser.add_argument("--case",action="append",default=[])
    parser.add_argument("--reuse-passed-from",type=Path,action="append",default=[])
    parser.add_argument("--lease-receipt",type=Path)
    args=parser.parse_args()
    output=args.output.resolve()
    if UNIT / "verification" not in output.parents:
        raise ValueError("Verification outputs must remain inside this unit/verification")
    output.mkdir(parents=True,exist_ok=False)
    thread_variables=("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS")
    thread_env={key:os.environ.get(key) for key in thread_variables}
    if any(value != "1" for value in thread_env.values()):
        raise RuntimeError("Explicit single-thread environment required: "+str(thread_env))
    files=[UNIT/"CONTRACT.json",SOURCE/"matched_ce.py",SOURCE/"frozen_star.py",SOURCE/"vendor"/"ci_finite_c22d.py",Path(__file__)]
    files.extend(RAW/name for name in PINNED_RAW)
    identity={str(path.relative_to(UNIT)):sha(path) for path in files}
    start={"schema":"PHYS83_INDEPENDENT_VERIFICATION_ATTEMPT_V1","utc":utc(),"input_sha256":identity,
           "workers":1,"thread_environment":thread_env,"python":platform.python_version(),
           "lease_receipt":str(args.lease_receipt) if args.lease_receipt else None,
           "lease_receipt_sha256":sha(args.lease_receipt) if args.lease_receipt and args.lease_receipt.exists() else None,
           "lease_receipt_status":"PRESENT_AT_START" if args.lease_receipt and args.lease_receipt.exists()
               else "WRAPPER_WRITES_AFTER_CHILD_EXIT" if args.lease_receipt else "LINKED_BY_CALLER",
           "completed_scientific_identity_reruns":0,"parent_symbolic_7":"REUSED_NOT_REEXECUTED",
           "parent_print_rounding_902":"REUSED_NOT_REEXECUTED",
           "science_grid_132_324_732":"NOT_EXECUTED_BY_VERIFIER"}
    (output/"START.json").write_text(json.dumps(start,indent=2)+"\n",encoding="utf-8")
    sys.path.insert(0,str(SOURCE))
    import numpy as np
    import mpmath as mp
    import scipy
    from scipy.integrate import quad
    import matched_ce as ce
    import frozen_star as star
    mp.mp.dps=80
    recorder=Recorder(output)
    reused={}
    for prior in args.reuse_passed_from:
        data=json.loads(prior.read_text(encoding="utf-8"))
        for prior_case,receipt in data.get("reused_cases",{}).items():
            reused[prior_case]={"via_result":str(prior),"via_result_sha256":sha(prior),**receipt}
            if prior_case in data.get("reference_checked_transient_results",{}):
                recorder.checked_steps[prior_case]=data["reference_checked_transient_results"][prior_case]
        for result in data["cases"]:
            if result["status"] == "PASS":
                reused[result["case"]]={"prior_result":str(prior),"prior_result_sha256":sha(prior),
                                       "prior_input_sha256":data["input_sha256"]}
                if result["case"] in data.get("reference_checked_transient_results",{}):
                    recorder.checked_steps[result["case"]] = data["reference_checked_transient_results"][result["case"]]
    cases=build_cases(recorder,np,mp,quad,ce,star)
    requested_groups=set(args.groups.split(","))
    if requested_groups-{group for _,group,_ in cases}:
        raise ValueError("Unknown groups: "+str(requested_groups-{group for _,group,_ in cases}))
    known={case for case,_,_ in cases}
    if set(args.case)-known:
        raise ValueError("Unknown case IDs: "+str(set(args.case)-known))
    selected=[row for row in cases if row[1] in requested_groups and (not args.case or row[0] in args.case)]
    if not selected:
        raise ValueError("No verification cases selected")
    executed=[]
    success=True
    begin=time.monotonic()
    for case,group,callback in selected:
        if case in reused:
            recorder.emit({"case":case,"event":"EXPLICIT_REUSE",**reused[case]})
            continue
        executed.append(case)
        if not recorder.run(case,group,callback):
            success=False
            break
    outcome={**start,"schema":"PHYS83_INDEPENDENT_VERIFICATION_RESULT_V1","finished_utc":utc(),
             "status":"PASS_SCOPED" if success else "FAIL_PRESERVED", "checks":recorder.checks,
             "cases":recorder.results,"selected_cases":[row[0] for row in selected],
             "reused_cases":{case:receipt for case,receipt in reused.items() if case in {row[0] for row in selected}},
             "unfinished_cases":[row[0] for row in selected if row[0] not in executed and row[0] not in reused],
             "counters":dict(recorder.counters),"maximum_errors":recorder.metrics,
             "reference_checked_transient_results":recorder.checked_steps,
             "runtime_versions":{"numpy":np.__version__,"scipy":scipy.__version__,"mpmath":mp.__version__},
             "elapsed_seconds":time.monotonic()-begin,
             "methods":{"rate":"Independent raw-source decimal knots, cellwise direct exponential-polynomial QUADPACK integration",
                        "population":"mpmath 80-decimal 6x6 augmented 3-state generator exponential",
                        "steady":"mpmath 80-decimal generator balance linear solve",
                        "root_limits":"mpmath 80-decimal direct smooth-kernel quadrature",
                        "resolved_relative_floor":"1e-280 for transient populations/counts; also enforce population absolute2e-12",
                        "derivative":"Direct-quadrature mean energy and independent five-point log-rate finite differences"},
             "limitations":["Finite sampled verification, not a continuum certificate",
                            "Source/interpolation/tail physical uncertainty remains open",
                            "Prescribed bath and high-density star subset do not certify coupled thermal/charge history",
                            "No native radiation owner, production admission, nuclear rates, or stopping enabled"]}
    (output/"RESULT.json").write_text(json.dumps(safe(outcome),indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    recorder.stream.close()
    print(json.dumps({"status":outcome["status"],"checks":recorder.checks,"output":str(output),
                      "cases":len(recorder.results),"counters":outcome["counters"]}),flush=True)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
