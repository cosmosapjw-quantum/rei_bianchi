"""Bounded NEW manufactured HE36 adapter checks; no IVP or old-test replay.

Run this file with --output a fresh directory. Every attempted run writes its
own receipt, including failed groups; never overwrite an earlier attempt.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import operator
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback

import numpy as np


ROOT = Path(__file__).resolve().parent
NAME = "he36_checked_package"
spec = importlib.util.spec_from_file_location(NAME, ROOT / "__init__.py",
                                           submodule_search_locations=[str(ROOT)])
pkg = importlib.util.module_from_spec(spec)
sys.modules[NAME] = pkg
spec.loader.exec_module(pkg)
from he36_checked_package import (
    attach_event_tensor, NET_TENSOR_SCOPE, CENTRAL_FRAME, ALL_RETAINED_THERMAL,
    NEUTRAL_21_STATE_CENSUS, Coefficient, ResolvedEvent, Unresolved,
    from_finite_evaluation, RADIAL_DIAGNOSTIC, MANUFACTURED_PAIR,
    validate_source_lift, SourceLiftDefect,
)
from he36_checked_package.reactive_moments import MomentDomainError, MomentRepresentabilityError
from he36_checked_package.maxwellian_moments import PreparedMaxwellianMoments, ME_KG
from he36_checked_package.vendor.rei_resolved_local import ENERGY


# Explicit fixture registry, matching the donor's 21-state primordial census:
# n; H0,H+; D0,D+; T0,T+; He3(0,+,++); He4(0,+,++);
# Li6(0,+,++,+++); Li7(0,+,++,+++). No negative ions or positrons.
A = np.array([1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7])
CHARGE = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3])
Y = np.arange(1, 22, dtype=float)
Y /= float(A @ Y)  # positive, exactly normalized up to binary64 rounding
NB = 3.25e5
LABELS = dict(energy_unit="J/event", tensor_scope=NET_TENSOR_SCOPE,
              central_frame=CENTRAL_FRAME,
              tensor_provenance="manufactured signed net tensor; no physical daughter/energy provider",
              thermal_inventory_scope=ALL_RETAINED_THERMAL,
              charge_census_scope=NEUTRAL_21_STATE_CENSUS)


def close(actual, expected, relative=5e-13, absolute=0.0):
    np.testing.assert_allclose(actual, expected, rtol=relative, atol=absolute)


def raises(exception, function, contains=None):
    try:
        function()
    except exception as exc:
        if contains is not None and contains not in str(exc):
            raise AssertionError((type(exc).__name__, str(exc), contains)) from exc
        return str(exc)
    raise AssertionError("expected " + exception.__name__)


def ledger(dEth):
    # ALL values are arbitrary manufactured J/event numbers. Neither Q0 nor
    # the beta coefficient is asserted to be an actual physical measurement.
    result = dict(Q0=0.0, W=0.0, dI=0.375e-19, dEth=float(dEth),
                  dEfast=0.0, dEexc=0.125e-19, dEgamma_ret=0.25e-19,
                  Egamma_esc=0.625e-19, Enu=0.875e-19)
    result["Q0"] = math.fsum(result[key] for key in ENERGY[2:])
    return result


def event(left, right, dEth, name, coefficient=None, custom_energy=None):
    order = sum(left.values())
    return ResolvedEvent(name, left, right,
        Coefficient.positive(0.125 if order == 1 else 2.5e-13) if coefficient is None else coefficient,
        "s^-1" if order == 1 else "m^3/s",
        "MANUFACTURED rate and all energy partitions; not an actual nuclear/atomic provider",
        "adapter fixture only; neutral 21-state census; all retained particles thermal",
        ledger(dEth) if custom_energy is None else custom_energy, A, CHARGE)


def tensor(heat, anisotropy=0.2):
    stf = abs(heat) * anisotropy * np.array([[1.0, 0.2, -0.3],
                                           [0.2, -0.4, 0.15],
                                           [-0.3, 0.15, -0.6]])
    return stf + (2.0 / 3.0) * heat * np.eye(3)


def run_donor_identity_and_portability():
    expected = "d0998261323609901f0cf9636d71282e7848bac6c00c1e5f7240ed7fc540e88a"
    actual = hashlib.sha256((ROOT / "vendor/rei_resolved_local.py").read_bytes()).hexdigest()
    assert actual == expected
    # Isolated import from an arbitrary cwd proves no /tmp source directory or
    # repository import fallback is needed. This does not replay donor checks.
    command = [sys.executable, "-I", "-c",
        "import importlib.util,sys;from pathlib import Path;p=Path(sys.argv[1]);"
        "s=importlib.util.spec_from_file_location('portable_he36',p/'__init__.py',submodule_search_locations=[str(p)]);"
        "m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);"
        "assert callable(m.attach_event_tensor);print('portable import PASS')", str(ROOT)]
    result = subprocess.run(command, cwd="/", capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return dict(donor_sha256=actual, isolated_import=result.stdout.strip())


def run_manufactured_census_and_energy():
    cases = [
        ("H0_to_Hplus", {1: 1}, {2: 1}, -0.3e-19, 0, 1, 1),
        ("Dplus_pplus_to_He3plusplus", {4: 1, 2: 1}, {9: 1}, 0.7e-19, -1, 0, -1),
        ("neutron_to_pplus_beta_census", {0: 1}, {2: 1}, 0.45e-19, 0, 1, 1),
    ]
    details = []
    for name, left, right, heat, dN, dE, dP in cases:
        e = event(left, right, heat, name)
        c = tensor(heat)
        out = attach_event_tensor(e, Y, NB, per_event_tensor_J=c, **LABELS)
        # Event count is independently evaluated from the supplied monomial;
        # no binary identical-reactant symmetry factor is needed in these cases.
        k = 0.125 if e.order == 1 else 2.5e-13
        count_per_baryon = k * (NB if e.order == 2 else 1.0)
        for index, power in left.items():
            count_per_baryon *= Y[index] ** power / math.factorial(power)
        count = NB * count_per_baryon
        assert sum(int(a)*int(n) for a, n in zip(A, e.nu)) == 0
        assert int(CHARGE @ e.nu) == dE
        assert int(np.sum(e.nu)) == dN
        assert int((1 + CHARGE) @ e.nu) == dP
        close(out.volumetric_event_rate, count)
        close(out.Rnucleus, dN * count)
        close(out.Relectron, dE * count)
        close(out.Rpart, dP * count)
        close(out.Rpart, out.Rnucleus + out.Relectron)
        close(out.R_species, count * e.nu)
        close(out.S, count * c)
        close(out.Q, count * heat)
        close(out.Q, out.reservoir_sources_W_m3["dEth"])
        close(out.J, count * (c - np.trace(c) * np.eye(3) / 3), absolute=1e-35)
        close(out.S, out.J + 2 * out.Q / 3 * np.eye(3))
        close(float(A @ out.R_species), 0.0, absolute=count * 2e-14)
        assert out.stf_trace_normalized_to_source <= 128 * np.finfo(float).eps
        raises(ValueError, lambda: out.S.setflags(write=True))
        raises(TypeError, lambda: operator.setitem(out.row, "rate", 123))
        details.append(dict(name=name, nucleus_delta=dN, inferred_electron_delta=dE,
            thermal_particle_delta=dP, volumetric_events_per_m3_s=count,
            Q_W_m3=out.Q, energy_normalized_defect=out.volume_energy_normalized_defect,
            arbitrary_manufactured_energy_partition=True, actual_nuclear_rate_claim=False))
    return dict(cases=details)


def run_net_ownership_and_missing_guards():
    e = event({1: 1}, {2: 1}, 0.3e-19, "manufactured_net_gain_minus_loss")
    incoming = tensor(-0.5e-19, 0.4)
    gain = tensor(0.8e-19, 0.1)
    net = incoming + gain
    assert abs(np.trace(net) / 2 - 0.3e-19) <= 1e-34
    out = attach_event_tensor(e, Y, NB, per_event_tensor_J=net, **LABELS)
    close(out.Q, out.volumetric_event_rate * (np.trace(incoming)/2 + np.trace(gain)/2))
    errors = {}
    errors["missing_birth_or_net_tensor"] = raises(Unresolved,
        lambda: attach_event_tensor(e, Y, NB, **LABELS), "MISSING_COMPLETE_NET")
    errors["twice_heating"] = raises(MomentDomainError,
        lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=net + (2/3)*0.3e-19*np.eye(3), **LABELS),
        "TENSOR_TRACE_DOES_NOT_MATCH_DETH")
    errors["incoming_only"] = raises(MomentDomainError,
        lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=incoming, **LABELS),
        "TENSOR_TRACE_DOES_NOT_MATCH_DETH")
    wrong = dict(LABELS, energy_unit="eV/event")
    errors["wrong_energy_unit"] = raises(MomentDomainError,
        lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=net, **wrong))
    wrong = dict(LABELS, tensor_scope="incoming_loss_only")
    errors["wrong_scope"] = raises(Unresolved,
        lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=net, **wrong))
    missing = {k: v for k, v in LABELS.items() if k != "thermal_inventory_scope"}
    errors["missing_thermal_inventory"] = raises(Unresolved,
        lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=net, **missing))
    fast = ledger(0.3e-19)
    fast["dEfast"] = 0.1e-19
    fast["Q0"] += fast["dEfast"]
    e_fast = event({1: 1}, {2: 1}, 0.3e-19, "manufactured_fast_energy_missing_number", custom_energy=fast)
    errors["fast_energy_cannot_define_thermal_count"] = raises(Unresolved,
        lambda: attach_event_tensor(e_fast, Y, NB, per_event_tensor_J=net, **LABELS),
        "FAST_ENERGY_RESERVOIR")
    return dict(negative_controls=errors,
                net_heat_per_event_J=float(np.trace(net)/2),
                independent_signed_heat_sum_J=float(np.trace(incoming)/2 + np.trace(gain)/2))


def run_rate_statuses_and_projection():
    e_zero = event({1: 1}, {2: 1}, 1e-19, "structural_zero", Coefficient("SUPPORT_ZERO"))
    zero = attach_event_tensor(e_zero, Y, NB, per_event_tensor_J=tensor(1e-19), **LABELS)
    assert zero.row["status"] == "SUPPORT_ZERO"
    assert np.count_nonzero(zero.S) == 0 and zero.Q == zero.Rpart == 0
    raises(Unresolved, lambda: attach_event_tensor(e_zero, Y, NB, **LABELS))
    e = event({1: 1}, {2: 1}, 1e-19, "state_zero")
    yzero = Y.copy(); yzero[1] = 0
    absent = attach_event_tensor(e, yzero, NB, per_event_tensor_J=tensor(1e-19), **LABELS)
    assert absent.row["status"] == "ZERO_REACTANT" and absent.Q == 0
    e_under = event({1: 1}, {2: 1}, 1e-19, "rate_underflow", Coefficient("POSITIVE", -1000.0))
    rate_error = raises(MomentRepresentabilityError,
        lambda: attach_event_tensor(e_under, Y, NB, per_event_tensor_J=tensor(1e-19), **LABELS),
        "RATE_UNDERFLOW_NOT_SUPPORT_ZERO")
    tiny = {key: 0.0 for key in ENERGY}; tiny["dEth"] = tiny["Q0"] = 1e-100
    e_reservoir = event({1: 1}, {2: 1}, 1e-100, "reservoir_underflow",
        Coefficient.positive(1e-300), custom_energy=tiny)
    reservoir_error = raises(MomentRepresentabilityError,
        lambda: attach_event_tensor(e_reservoir, Y, 1e100, per_event_tensor_J=tensor(1e-100), **LABELS),
        "DONOR_RESERVOIR_UNDERFLOW")
    # Isotropic supplied net heating is an explicit input, not a default. The
    # trace-projection roundoff is measured against S, including when J≈0.
    iso = attach_event_tensor(e, Y, NB, per_event_tensor_J=(2/3)*1e-19*np.eye(3), **LABELS)
    assert np.max(np.abs(iso.J)) <= 128*np.finfo(float).eps*np.max(np.abs(iso.S))
    # A supplied pure shear has zero donor dEth but nonzero, signed J.
    e_shear = event({1: 1}, {2: 1}, 0.0, "manufactured_zero_heat_shear")
    shear = np.array([[1.0, 0.2, 0.0], [0.2, -1.0, 0.0], [0.0, 0.0, 0.0]])*1e-19
    pure = attach_event_tensor(e_shear, Y, NB, per_event_tensor_J=shear, **LABELS)
    assert pure.Q == 0 and np.max(np.abs(pure.J)) > 0
    close(pure.J, pure.S)
    bad = tensor(1e-19).astype(complex)
    raises(MomentDomainError, lambda: attach_event_tensor(e, Y, NB, per_event_tensor_J=bad, **LABELS))
    return dict(rate_underflow_rejected=rate_error, reservoir_underflow_rejected=reservoir_error,
                explicit_structural_zero_accepted=True, explicit_zero_heat_shear_nonzero=True,
                isotropic_projection_source_scaled_residual=iso.stf_trace_normalized_to_source)


def _finite_fixture(mapping="manufactured_relative_energy", mass=1.2e-27):
    return PreparedMaxwellianMoments(np.array([0.1, 1.0, 3.0, 8.0]),
        np.array([0.0, 1.0, 0.7, 0.2])*1e-21, 0.1,
        "manufactured finite table for adapter identity tests; not CCC data",
        reduced_mass_kg=mass, energy_mapping=mapping)


def run_finite_identity_mapping_and_pair():
    prepared = _finite_fixture()
    evaluated = prepared.evaluate([10000.0, 20000.0])
    record = from_finite_evaluation(prepared, evaluated, 1,
        acknowledge_finite_source_partial=True, usage=MANUFACTURED_PAIR,
        pair_masses_kg=(2e-27, 3e-27))
    assert record.temperature_K == record.raw_moments.temperature_K == 20000.0
    assert record.original_evaluation_type == type(evaluated).__module__ + "." + type(evaluated).__qualname__
    assert record.finite_source_partial and not record.full_physical_rate
    assert not record.physical_tail_bound_established
    assert record.energy_mapping == "manufactured_relative_energy"
    assert record.raw_moments.cauchy_normalized_defect <= 128*np.finfo(float).eps
    out = record.binary_loss(1e3, 2e3, 2e-27, 3e-27, 20000.0,
                            np.zeros((3,3)), np.zeros((3,3)), linear_response=True)
    assert out.Q_a < 0 and out.Q_b < 0 and out.Rn_a == out.Rn_b < 0
    errors = {}
    for idx in (-1, 2, True, 0.0):
        errors["index_"+str(idx)] = raises(MomentDomainError,
            lambda idx=idx: from_finite_evaluation(prepared, evaluated, idx,
                acknowledge_finite_source_partial=True, usage=RADIAL_DIAGNOSTIC))
    errors["unacknowledged_partial"] = raises(Unresolved,
        lambda: from_finite_evaluation(prepared, evaluated, 0,
            acknowledge_finite_source_partial=False, usage=RADIAL_DIAGNOSTIC))
    errors["changed_T"] = raises(MomentDomainError, lambda: record.for_pair(2e-27, 3e-27, 10000.0),
                                  "TEMPERATURE_IDENTITY_MISMATCH")
    errors["changed_mu"] = raises(MomentDomainError, lambda: record.for_pair(3e-27, 3e-27, 20000.0),
                                   "REDUCED_MASS_IDENTITY_MISMATCH")
    errors["wrong_identity"] = raises(MomentDomainError,
        lambda: from_finite_evaluation(prepared, replace(evaluated, identity="not-original"), 0,
            acknowledge_finite_source_partial=True, usage=RADIAL_DIAGNOSTIC))
    fixed = _finite_fixture("heavy_fixed_target_incident_electron", ME_KG)
    fixed_eval = fixed.evaluate([20000.0])
    diag = from_finite_evaluation(fixed, fixed_eval, 0,
        acknowledge_finite_source_partial=True, usage=RADIAL_DIAGNOSTIC)
    assert diag.energy_mass_kg == ME_KG
    errors["fixed_target_pair_conversion"] = raises(Unresolved,
        lambda: from_finite_evaluation(fixed, fixed_eval, 0,
            acknowledge_finite_source_partial=True, usage=MANUFACTURED_PAIR,
            pair_masses_kg=(2*ME_KG, 2*ME_KG)), "INCIDENT_LAB_ENERGY")
    errors["diagnostic_pair_bypass"] = raises(Unresolved,
        lambda: diag.binary_loss(1, 1, 2*ME_KG, 2*ME_KG, 20000.0,
            np.zeros((3,3)), np.zeros((3,3)), linear_response=True))
    return dict(negative_controls=errors, original_evaluation_type=record.original_evaluation_type,
        finite_pair_mapping=record.energy_mapping, partial_moment_values=list(evaluated.moments_SI[1,:3]),
        actual_CCC_data_recomputed=False)


def run_finite_underflow_and_declared_zero():
    high = PreparedMaxwellianMoments([1e6, 1e6+1, 1e6+2], [0.0, 1e-21, 1e-21], 1e6,
        "manufactured high-energy underflow sentinel", reduced_mass_kg=1.2e-27)
    evaluation = high.evaluate([2000.0])
    assert np.all(evaluation.underflow[0,:3])
    error = raises(MomentRepresentabilityError,
        lambda: from_finite_evaluation(high, evaluation, 0,
            acknowledge_finite_source_partial=True, usage=RADIAL_DIAGNOSTIC),
        "UNDERFLOW_CANNOT_BECOME_PHYSICAL_ZERO")
    zero = PreparedMaxwellianMoments([0.1, 1.0], [0.0, 0.0], 0.1,
        "manufactured declared-zero finite table", reduced_mass_kg=1.2e-27)
    zero_eval = zero.evaluate([20000.0])
    record = from_finite_evaluation(zero, zero_eval, 0,
        acknowledge_finite_source_partial=True, usage=RADIAL_DIAGNOSTIC)
    assert record.raw_moments.alpha == record.raw_moments.beta == record.raw_moments.gamma == 0
    assert "finite" in record.raw_moments.zero_reason and not record.full_physical_rate
    return dict(positive_underflow_rejected=error,
        declared_zero_scope=record.raw_moments.zero_reason,
        positive_underflow_log_moments=list(evaluation.log_moments_SI[0,:3]))


def run_source_lift_compatibility_and_defect():
    # Two full isotopic entries share a reduced electronic population in a
    # 1:3 fixed ratio. Equal-rate loss respects this lift; an isotope-selective
    # source can conserve their sum while breaking the source commutator.
    L = np.array([[0.25, 0.0], [0.75, 0.0], [0.0, 1.0]])
    z = np.array([0.4, 0.6])
    k = 0.25
    calls = [0,0]
    def full(y):
        calls[0] += 1
        assert not y.flags.writeable
        return np.array([-k*y[0], -k*y[1], k*(y[0]+y[1])])
    def reduced(state):
        calls[1] += 1
        assert not state.flags.writeable
        return np.array([-k*state[0], k*state[0]])
    report = validate_source_lift(L, z, full, reduced,
        atol=[1e-15]*3, rtol=5e-13, source_unit="s^-1 in absolute abundance per baryon")
    assert calls == [1,1] and report.passed
    close(report.full_state, [0.1,0.3,0.6])
    def isotope_selective(y):
        return full(y) + np.array([1e-4,-1e-4,0.0])
    caught = None
    try:
        validate_source_lift(L, z, isotope_selective, reduced,
            atol=[1e-15]*3, rtol=5e-13, source_unit="s^-1 in absolute abundance per baryon")
    except SourceLiftDefect as exc:
        caught = exc.report
    assert caught is not None and caught.failing_indices == (0,1)
    close(caught.defect, [1e-4,-1e-4,0], absolute=1e-17)
    assert abs(float(np.sum(caught.defect))) < 1e-16
    before = calls.copy()
    positive_error = raises(MomentDomainError,
        lambda: validate_source_lift(L, [0.0,1.0], full, reduced,
            atol=0.0, rtol=0.0, source_unit="s^-1"), "STRICTLY_POSITIVE")
    assert calls == before
    # The same explicit defect is admitted only if the caller actually widens
    # its componentwise absolute gate. This tests the gate, not a source model.
    loose = validate_source_lift(L, z, isotope_selective, reduced,
        atol=[2e-4,2e-4,0.0], rtol=1e-12, source_unit="s^-1")
    assert loose.passed
    return dict(commuting_defect=report.defect.tolist(),
        selective_source_defect=caught.defect.tolist(),
        gate=caught.absolute_gate.tolist(), failing_indices=list(caught.failing_indices),
        positivity_control=positive_error, callbacks_per_checked_state=[1,1],
        global_closure_or_IVP_claim=False)


CHECKS = [
    ("donor_identity_and_portable_import", run_donor_identity_and_portability),
    ("manufactured_21state_census_and_energy", run_manufactured_census_and_energy),
    ("net_tensor_ownership_and_missing_guards", run_net_ownership_and_missing_guards),
    ("rate_statuses_and_STF_projection", run_rate_statuses_and_projection),
    ("finite_source_identity_mapping_and_pair", run_finite_identity_mapping_and_pair),
    ("finite_underflow_and_declared_partial_zero", run_finite_underflow_and_declared_zero),
    ("source_lift_compatibility_and_defect", run_source_lift_compatibility_and_defect),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    started = datetime.now(timezone.utc).isoformat()
    results = []
    for name, check in CHECKS:
        before = time.perf_counter()
        try:
            detail = check()
            result = dict(name=name, passed=True, detail=detail)
        except Exception as exc:
            result = dict(name=name, passed=False, error_type=type(exc).__name__,
                          error=str(exc), traceback=traceback.format_exc())
        result["wall_seconds"] = time.perf_counter()-before
        results.append(result)
        print(name + ": " + ("PASS" if result["passed"] else "FAIL"), flush=True)
    failures = sum(not item["passed"] for item in results)
    receipt = dict(schema="he36.new_event_bridge_checks.v1", workflow="workflow1.0.0",
        approval="approval0.2", started_utc=started, ended_utc=datetime.now(timezone.utc).isoformat(),
        command=[sys.executable, *sys.argv], exit_code=int(failures != 0),
        Python=sys.version, numpy=np.__version__, platform=platform.platform(),
        wall_seconds=time.perf_counter()-start_wall, cpu_seconds=time.process_time()-start_cpu,
        maximum_resident_set_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        checks=results, passed_groups=len(results)-failures, total_groups=len(results),
        source_hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in sorted(ROOT.rglob("*.py"))},
        scope=dict(new_IVP=0, old_donor_tests_replayed=0, old_HE32_replays=0,
                   actual_CCC_evaluation_replays=0, independent_6D_checks_replayed=0,
                   new_rate_or_nuclear_energy_admission=False,
                   new_checks="three manufactured 21-state events, supplied tensor ownership, tiny manufactured finite-source adapter controls, pointwise source-lift gates"))
    (args.output/"RESULT.json").write_text(json.dumps(receipt, indent=2, allow_nan=False)+"\n")
    print(json.dumps(dict(passed_groups=len(results)-failures,total_groups=len(results),exit_code=receipt["exit_code"])))
    return int(failures != 0)


if __name__ == "__main__":
    raise SystemExit(main())
