#!/usr/bin/env python3
"""P03A finite-grid screen of the P01-validated frozen research baseline's escape ENERGY ledger.

No spectrum or photon multiplicity is assigned to recombinations.  The only
transfer calculation is a diagnostic on 17 archived states: positive opacity
samples are joined by straight lines, and each archived escape-energy increment
is placed at its segment's left endpoint.  Maxima range over the existing 2904
photon cells only.  This defines an envelope for that finite frozen-state
surrogate, not an actual diffuse ON history, continuum bound, or error budget.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

PACKET = Path(__file__).resolve().parents[1]
REPOSITORY = PACKET.parents[1]
CRATE = REPOSITORY / "rust/rei_microphysics"
sys.path.insert(0, str(CRATE / "python"))
from source_bound_interval import (  # noqa: E402
    C, CHI, EV, NativeConsumer, ProductionInterval, characteristics, preflight,
)


def tail_optical_depth(times, opacity):
    """Exact integral of the defined piecewise-linear opacity surrogate."""
    times = np.asarray(times, dtype=float)
    opacity = np.asarray(opacity, dtype=float)
    if (times.ndim != 1 or len(times) < 2 or opacity.ndim != 2 or
            opacity.shape[0] != len(times) or opacity.shape[1] == 0 or
            not np.isfinite(times).all() or not np.isfinite(opacity).all() or
            np.any(np.diff(times) <= 0) or np.any(opacity < 0)):
        raise ValueError("FINITE_GRID_OPACITY_DOMAIN")
    segments = .5 * (opacity[:-1] + opacity[1:]) * np.diff(times)[:, None]
    tail = np.vstack([np.cumsum(segments[::-1], axis=0)[::-1], np.zeros(opacity.shape[1])])
    if not np.isfinite(tail).all():
        raise ValueError("FINITE_GRID_OPTICAL_DEPTH_OVERFLOW")
    return tail


def escape_energy_screen(cumulative_escape, absorption_probability):
    """Energy-only caps; photon emission count and spectrum remain undefined."""
    escape = np.asarray(cumulative_escape, dtype=float)
    probability = np.asarray(absorption_probability, dtype=float)
    if (escape.ndim != 1 or probability.ndim != 2 or len(escape) < 2 or
            probability.shape[0] != len(escape) or probability.shape[1] == 0 or
            not np.isfinite(escape).all() or not np.isfinite(probability).all() or
            escape[0] != 0 or np.any(np.diff(escape) < 0) or
            np.any(probability < 0) or np.any(probability > 1)):
        raise ValueError("FINITE_GRID_ESCAPE_DOMAIN")
    increments = np.diff(escape)
    # Each segment's whole energy is placed at its left endpoint.  No emission
    # history within the segment, spectral weighting, or branch ratio is known.
    maxima = np.max(probability[:-1], axis=1)
    return increments, increments * maxima


def run_screen(packet: Path, binary: Path):
    verified = preflight(packet)
    consumer = NativeConsumer(binary, verified["identities"])
    try:
        interval = ProductionInterval(packet, verified, consumer)
        with np.load(packet / "evidence/extended_dataset.npz", allow_pickle=False) as data:
            times, states = data["times_s"].copy(), data["states"].copy()
        if (states.shape != (interval.n + 9, 17) or
                not np.array_equal(times, interval.times) or
                not np.isfinite(states).all()):
            raise ValueError("FROZEN_HISTORY_SHAPE_OR_FINITE")
        opacities, energies, rows = [], [], []
        all_expanding = True
        max_number_residual = max_energy_residual = 0.
        for i, t in enumerate(times):
            state = states[:, i]
            g = interval.background.at(t)
            energy, mu, _ = characteristics(interval.q, interval.mu0, g)
            sigma = consumer.call("SIGMA", energy, 3*interval.n).reshape(-1, 3)
            lower = np.array([g["nH"]*(1-state[0]),
                              g["nHe"]*(1-state[1]-state[2]), g["nHe"]*state[1]])
            opacity = C * (sigma @ lower)
            values, source = interval.stage(t, state)
            rhs = consumer.call("RHS", values, 14+interval.n)
            max_number_residual = max(max_number_residual, abs(rhs[12]))
            max_energy_residual = max(max_energy_residual, abs(rhs[13]))
            all_expanding &= g["H"]-g["s"] > 0 and g["H"]+2*g["s"] > 0
            if np.any(lower < 0) or np.any(sigma < 0) or np.any(source < 0):
                raise ValueError("FROZEN_STAGE_POSITIVITY")
            # Thermal and binding energies are kept separate; both are per
            # initial reference volume, as is the archived escape counter.
            thermal = interval.nh0 * EV * state[3]
            binding = EV * (interval.nh0*CHI[0]*state[0] + interval.nhe0*(
                CHI[1]*state[1] + (CHI[1]+CHI[2])*state[2]))
            photoheat = C*EV*np.sum(
                state[4:4+interval.n, None] * sigma * lower * (energy[:, None]-CHI))
            rows.append(dict(time_s=float(t), T_K=float(rhs[11]),
                thermal_erg_cm3_reference=float(thermal),
                binding_erg_cm3_reference=float(binding),
                escape_energy_rate_erg_cm3_reference_s=float(rhs[4]),
                primary_photoheat_erg_cm3_reference_s=float(photoheat),
                external_source_erg_cm3_reference_s=float(rhs[6]),
                escape_erg_cm3_reference=float(state[4+interval.n]),
                energy_min_eV=float(energy.min()), energy_max_eV=float(energy.max()),
                opacity_min_s=float(opacity.min()), opacity_max_s=float(opacity.max())))
            opacities.append(opacity)
            energies.append(energy)
        opacities, energies = np.asarray(opacities), np.asarray(energies)
        tau = tail_optical_depth(times, opacities)
        probability = -np.expm1(-tau)
        escape = states[4+interval.n]
        increments, energy_cap = escape_energy_screen(escape, probability)
        segment_rows = []
        for i, amount in enumerate(energy_cap):
            k = int(np.argmax(probability[i]))
            segment_rows.append(dict(left_time_s=float(times[i]), right_time_s=float(times[i+1]),
                escape_increment_erg_cm3_reference=float(increments[i]),
                finite_node_absorption_probability_max=float(probability[i, k]),
                maximizing_node=k, initial_q_eV=float(interval.q[k]),
                emission_epoch_energy_eV=float(energies[i, k]), initial_mu=float(interval.mu0[k]),
                energy_cap_erg_cm3_reference=float(amount)))
        all_retained = float(escape[-1])
        finite_cap = float(energy_cap.sum())
        minimum_thermal = min(row["thermal_erg_cm3_reference"] for row in rows)
        escape_rate = np.array([row["escape_energy_rate_erg_cm3_reference_s"] for row in rows])
        escape_trapezoid = float(np.trapezoid(escape_rate, times))
        checks = dict(
            epochs_and_nodes=states.shape == (2913, 17),
            original_temperature_guard=all(30000 <= row["T_K"] <= 110000 for row in rows),
            frozen_energy_band=bool(np.all((energies > 0) & (energies <= 50000))),
            photon_positivity=bool(np.all(states[4:4+interval.n] >= 0)),
            opacity_positivity=bool(np.all(opacities >= 0)),
            escaped_energy_monotone=bool(np.all(increments >= 0)),
            all_directional_expansion_positive=bool(all_expanding),
            characteristic_energy_nonincreasing=bool(np.all(np.diff(energies, axis=0) <= 0)),
            finite_envelope_within_retained_energy=0 <= finite_cap <= all_retained,
            local_photon_ledger=max_number_residual <= 1e-9,
            local_energy_ledger=max_energy_residual <= 1e-9)
        files = [Path(__file__), CRATE/"python/source_bound_interval.py",
                 CRATE/"Cargo.toml", CRATE/"Cargo.lock", *sorted((CRATE/"src").rglob("*.rs"))]
        result = dict(
            task_id="REI-PHYSINPUT-01-P03A", status="PASS_DIAGNOSTIC" if all(checks.values()) else "FAIL",
            checks={key: bool(value) for key, value in checks.items()}, inputs=verified["identities"],
            implementation_sha256={str(p.relative_to(REPOSITORY)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in files},
            binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), native_calls=consumer.calls,
            scope="Finite 17-epoch frozen-state, 2904-node escape-energy sensitivity screen",
            conventions=dict(time="proper elapsed seconds", photon="N_rel=a_rel^3 n",
                energy="E=qR", source_direction_jacobian="R^-3", energy_density="erg per reference cm^3",
                closure=verified["contract"]["closure"]["id"], optional_CR_RCT_HH="OFF",
                recombination_emission_photon_count="UNDEFINED",
                optical_depth="trapezoid of frozen-state opacity samples at each existing q,mu0 cell",
                energy_placement="whole archived segment escape energy at left endpoint",
                maximization="independent energy allocation among finite existing cells per segment"),
            summary=dict(all_retained_energy_erg_cm3_reference=all_retained,
                finite_grid_reabsorption_energy_cap_erg_cm3_reference=finite_cap,
                finite_grid_cap_over_all_retained=finite_cap/all_retained if all_retained else 0.,
                all_retained_over_minimum_frozen_thermal=all_retained/minimum_thermal,
                finite_grid_cap_over_minimum_frozen_thermal=finite_cap/minimum_thermal,
                all_retained_ionization_energy_equivalent_per_initial_H=(all_retained/(EV*CHI*interval.nh0)).tolist(),
                finite_grid_ionization_energy_equivalent_per_initial_H=(finite_cap/(EV*CHI*interval.nh0)).tolist(),
                ionization_equivalent_meaning="Energy/threshold/initial nH; separate single-species allocations, not simultaneous ionizations or predicted fractions",
                escape_rate_trapezoid_erg_cm3_reference=escape_trapezoid,
                escape_trapezoid_relative_difference=(escape_trapezoid-all_retained)/all_retained if all_retained else 0.,
                max_local_photon_ledger=max_number_residual, max_local_energy_ledger=max_energy_residual),
            history=rows, segments=segment_rows,
            decision=dict(actual_diffuse_ON_effect="NOT_MEASURED", ionization_history_materiality="NOT_EVALUABLE",
                combined_numerical_model_uncertainty_budget="MISSING", diffuse_spectrum="MISSING",
                emission_multiplicity="UNDEFINED", full_photon_history="HOLD", global_EoR_admission="HOLD",
                next_minimum_input="Source-backed differential recombination photon spectrum and branching/multiplicity with atomic/energy consistency; choose explicit transport or OTS before production ON",
                limitations=["No continuum or temporal error bound from trapezoid snapshots",
                    "Frozen state omits feedback and extra recombination cycles",
                    "Finite q cells omit off-grid, outside-band photons and boundary inflow",
                    "An energy envelope is not a bound on coupled state/observable change",
                    "Secondary, Compton and high-energy boundary remain separate model contracts"]))
        return result, dict(times_s=times, q_eV=interval.q, mu0=interval.mu0,
                            opacity_s=opacities, tail_optical_depth=tau,
                            absorption_probability=probability, energies_eV=energies)
    finally:
        consumer.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--binary", type=Path, default=CRATE/"target/release/axisym_conditional")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("P03A_OUTPUT_ALREADY_EXISTS")
    result, nodes = run_screen(args.packet.resolve(), args.binary.resolve())
    args.output.mkdir(parents=True)
    (args.output/"VALIDATION.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    np.savez_compressed(args.output/"finite_grid.npz", **nodes)
    print(json.dumps(dict(status=result["status"], summary=result["summary"],
                          native_calls=result["native_calls"]), indent=2, allow_nan=False))
    if result["status"] != "PASS_DIAGNOSTIC":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
