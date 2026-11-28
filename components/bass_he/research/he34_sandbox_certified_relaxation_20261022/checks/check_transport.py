#!/usr/bin/env python3
"""Affected HE34 neutral-transport checks, saved-state diagnostic and timing.

No HE32 integration module is imported. Only one pinned saved trajectory is
read. A subprocess receipt preserves the actual command, stdout, stderr and
exit status, including a failure. The 40-case source-stage prototype is reused;
this executable checks the new vector path and the saved-state connection.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                         "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import numpy as np
import scipy
from scipy.constants import atomic_mass

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "src"))
from neutral_transport import (DATA_PATH, DATA_SHA256, KB_J_K, collision_integral,
                               prepare_neutral_transport)

BACKGROUND_SHA256 = "c97ffa6a793c092b6b559b32581a7996a82b85a8e725b0e5893be9ae1e7bf30a"
T_K = 20000.0
PARITY_REL = 5e-13
G_SI = 6.67430e-11
CSV_NAME = "NEUTRAL_H_HE_s07_m03_r03.csv"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path, value):
    atomic_write(path, (json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def relative_difference(left, right):
    left, right = np.asarray(left), np.asarray(right)
    if np.any(right <= 0.0) or not np.all(np.isfinite(right)):
        raise ValueError("Reference values must be finite and positive")
    return float(np.max(np.abs(left - right) / right))


def record_check(records, name, passed, **details):
    record = dict(name=name, passed=bool(passed), **details)
    records.append(record)
    if not passed:
        raise AssertionError(json.dumps(record))


def environment():
    """Read topology/limits before the bounded numerical workload."""
    limits = {}
    for name in ("memory.max", "memory.current", "cpu.max", "cpuset.cpus.effective"):
        path = Path("/sys/fs/cgroup") / name
        if path.exists():
            limits[name] = path.read_text().strip()
    memory = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.split(":")[0] in {"MemTotal", "MemAvailable", "SwapTotal"}:
            key, value = line.split(":", 1)
            memory[key] = value.strip()
    topology = {}
    try:
        query = subprocess.run(["lscpu", "--json"], capture_output=True, text=True,
                               check=True, timeout=3)
        wanted = {"Architecture:", "CPU(s):", "Model name:", "Thread(s) per core:",
                  "Core(s) per socket:", "Socket(s):", "NUMA node(s):"}
        topology = {row["field"].rstrip(":"): row["data"]
                    for row in json.loads(query.stdout)["lscpu"] if row["field"] in wanted}
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        topology = {"query_unavailable": str(error)}
    try:
        from threadpoolctl import threadpool_info
        pools = threadpool_info()
    except ImportError:
        pools = "threadpoolctl unavailable; thread environment recorded"
    return dict(python=sys.version, executable=sys.executable, numpy=np.__version__,
                scipy=scipy.__version__, platform=platform.platform(), topology=topology,
                logical_cpus=os.cpu_count(), affinity_cpu_count=len(os.sched_getaffinity(0)),
                memory=memory, cgroup_limits=limits, threadpools=pools,
                thread_environment={key: os.environ[key] for key in
                    ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
                timer=dict(implementation=time.get_clock_info("perf_counter").implementation,
                           resolution_s=time.get_clock_info("perf_counter").resolution),
                arithmetic="binary64; no fast-math or mixed precision")


def load_background(path, he32_unit, checks):
    """Reconstruct physical neutral densities from the pinned HE32 census."""
    path, he32_unit = Path(path).resolve(), Path(he32_unit).resolve()
    actual_hash = sha256(path)
    record_check(checks, "pinned_background_sha256", actual_hash == BACKGROUND_SHA256,
                 expected=BACKGROUND_SHA256, actual=actual_hash)
    with np.load(path, allow_pickle=False) as archive:
        epoch = archive["x"].copy()
        observables = archive["observables"].copy()
        observable_names = list(archive["observable_names"])
        abundances = archive["abundance_per_H"].copy()
        species = list(archive["species_names"])
        metadata = json.loads(str(archive["metadata_json"]))
    record_check(checks, "saved_201_epochs", epoch.shape == (201,)
                 and abundances.shape == (21, 201)
                 and observables.shape == (201, len(observable_names))
                 and metadata["config"]["samples"] == 201,
                 epochs=int(epoch.size), abundance_shape=list(abundances.shape))
    dependency_hashes = {}
    for relative_path in ("src/primordial_network.py", "src/coupled_pilot.py",
                          "data/ISOTOPE_SCENARIO.json", "vendor/REI_BACKGROUND_FAMILY_LOCK.json"):
        actual = sha256(he32_unit / relative_path)
        expected = metadata["executor"]["files"][relative_path]
        record_check(checks, "he32_dependency_" + relative_path, actual == expected,
                     actual_sha256=actual, saved_executor_sha256=expected)
        dependency_hashes[relative_path] = actual
    scenario = json.loads((he32_unit / "data/ISOTOPE_SCENARIO.json").read_text())
    cosmology = json.loads((he32_unit / "vendor/REI_BACKGROUND_FAMILY_LOCK.json").read_text())["cosmology"]
    record_check(checks, "same_saved_scipy_constant_provider",
                 scipy.__version__ == metadata["executor"]["scipy"],
                 installed=scipy.__version__, saved=metadata["executor"]["scipy"],
                 atomic_mass_kg=float(atomic_mass))
    record_check(checks, "source_temperature_is_fixed_20000_K", scenario["temperature_K"] == T_K,
                 temperature_K=scenario["temperature_K"])

    # This is the formula in the hash-verified HE32 PrimordialNetwork.__init__.
    composition = scenario["composition"]
    rd, r3, r6, r7 = (float(composition[key]) for key in ("DoH", "He3oH", "Li6oH", "Li7oH"))
    y4 = float(composition["YPBBN"])
    r4 = y4 * (1.0 + 2.0 * rd + 3.0 * r3 + 6.0 * r6 + 7.0 * r7) / (4.0 * (1.0 - y4))
    nuclide_ratios = np.array([0.0, 1.0, rd, 0.0, r3, r4, r6, r7])
    baryons_per_H = float(np.array([1, 1, 2, 3, 3, 4, 6, 7]) @ nuclide_ratios)
    rho_critical = 3.0 * cosmology["H0_per_s"] ** 2 / (8.0 * math.pi * G_SI)
    nH0_m3 = rho_critical * cosmology["Omega_b"] / (atomic_mass * baryons_per_H)

    column = {name: observables[:, index] for index, name in enumerate(observable_names)}
    scale_factor, hubble = column["a"], column["H_per_s"]
    a_ref = 1.0 / (1.0 + float(scenario["redshift"][0]))
    scale_factor_error = relative_difference(scale_factor, a_ref * np.exp(epoch))
    record_check(checks, "saved_scale_factor_clock", scale_factor_error <= 5e-15,
                 maximum_relative_difference=scale_factor_error)
    nH_reference = nH0_m3 / scale_factor ** 3
    charges = np.array([int(name.rsplit("_q", 1)[1]) for name in species])
    electrons_per_H = charges @ abundances
    saved_electrons_m3 = column["ne_cm3"] * 1e6
    charge_error = relative_difference(nH_reference * electrons_per_H, saved_electrons_m3)
    record_check(checks, "density_matches_independent_saved_charge_census", charge_error <= PARITY_REL,
                 maximum_relative_difference=charge_error,
                 comparison="nH0/a^3 * sum(q_i*abundance_i) vs saved ne_cm3*1e6")
    saved_baryon_peak = metadata["metrics"]["proper_baryon_max_cm3"]
    baryon_peak_error = abs(nH0_m3 * baryons_per_H * 1e-6 / a_ref ** 3 / saved_baryon_peak - 1.0)
    record_check(checks, "density_matches_saved_baryon_peak", baryon_peak_error <= PARITY_REL,
                 relative_difference=baryon_peak_error)
    selected = ["H1_q0", "He4_q0"]
    record_check(checks, "unique_selected_species", all(species.count(name) == 1 for name in selected))
    hydrogen_abundance = abundances[species.index("H1_q0")]
    helium_abundance = abundances[species.index("He4_q0")]
    hydrogen_density = nH_reference * hydrogen_abundance
    helium_density = nH_reference * helium_abundance
    record_check(checks, "actual_selected_inputs_are_interior", bool(np.all(hydrogen_density > 0.0)
                 and np.all(helium_density > 0.0) and np.all(hubble > 0.0)
                 and np.all(np.isfinite([hydrogen_density, helium_density, hubble]))),
                 minimum_n_H1_q0_m3=float(hydrogen_density.min()),
                 minimum_n_He4_q0_m3=float(helium_density.min()))
    return dict(epoch=epoch, scale_factor=scale_factor, redshift=column["z"], hubble=hubble,
                hydrogen_abundance=hydrogen_abundance, helium_abundance=helium_abundance,
                nH_reference=nH_reference, hydrogen_density=hydrogen_density,
                helium_density=helium_density,
                provenance=dict(path=str(path), sha256=actual_hash, case_id=metadata["case_id"],
                    case_identity=metadata["identity"], he32_unit=str(he32_unit),
                    source_dependency_sha256=dependency_hashes,
                    selected_species=selected, excluded_species=[name for name in species if name not in selected],
                    abundance_definition="n_i / fixed reference H1 nucleus density; not a neutral-H fraction denominator",
                    density_formula="nH_reference(a)=3*H0^2*Omega_b/(8*pi*G*m_u*baryons_per_H*a^3)",
                    nH0_m3=float(nH0_m3), baryons_per_H=baryons_per_H,
                    source_H0_per_s=cosmology["H0_per_s"], source_Omega_b=cosmology["Omega_b"],
                    source_G_SI=G_SI, saved_charge_census_max_relative_difference=charge_error,
                    saved_baryon_peak_relative_difference=baryon_peak_error))


def matrix_reference_vectorized(prepared, n_hydrogen, n_helium):
    """Independent direct G solve; no reduced numerator/determinant is used."""
    arrays = []
    for value in (n_hydrogen, n_helium):
        raw = np.asarray(value)
        if raw.dtype.kind not in "biuf":
            raise ValueError("Number weights must contain real numeric values")
        array = np.asarray(raw, dtype=np.float64)
        if not np.all(np.isfinite(array)) or np.any(array < 0.0):
            raise ValueError("Number weights must be finite and nonnegative")
        arrays.append(array)
    hydrogen, helium = np.broadcast_arrays(*arrays)
    scale = np.maximum(hydrogen, helium)
    if np.any(scale == 0.0):
        raise ValueError("A zero-density pair has no defined mixture composition")
    x, y = hydrogen / scale, helium / scale
    interior = (x > 0.0) & (y > 0.0)
    result = np.where(y == 0.0, prepared.eta_H_Pa_s, prepared.eta_He_Pa_s)
    if np.any(interior):
        xi, yi = x[interior], y[interior]
        factor = xi * yi * prepared.u
        matrix = np.empty((xi.size, 2, 2), dtype=np.float64)
        matrix[:, 0, 0] = xi * xi / prepared.eta_H_Pa_s + factor * (1.2 * prepared.Astar * prepared.r + 2.0)
        matrix[:, 1, 1] = yi * yi / prepared.eta_He_Pa_s + factor * (1.2 * prepared.Astar / prepared.r + 2.0)
        matrix[:, 0, 1] = factor * (1.2 * prepared.Astar - 2.0)
        matrix[:, 1, 0] = matrix[:, 0, 1]
        weights = np.stack((xi, yi), axis=-1)
        solution = np.linalg.solve(matrix, weights[..., None])[..., 0]
        result[interior] = np.sum(weights * solution, axis=-1)
    if not np.all(np.isfinite(result)) or np.any(result <= 0.0):
        raise ValueError("eta_mix_Pa_s is not finite and positive")
    return result


def affected_formula_checks(prepared, background, checks):
    hydrogen, helium = background["hydrogen_density"], background["helium_density"]
    vectorized = prepared.viscosity_vectorized(hydrogen, helium)
    scalar = np.array([prepared.viscosity(h, he) for h, he in zip(hydrogen, helium)])
    matrix = matrix_reference_vectorized(prepared, hydrogen, helium)
    vector_scalar_error = relative_difference(vectorized, scalar)
    matrix_error = relative_difference(vectorized, matrix)
    record_check(checks, "new_vector_vs_scalar_on_actual_201_inputs", vector_scalar_error <= PARITY_REL,
                 cases=201, maximum_relative_difference=vector_scalar_error, tolerance=PARITY_REL)
    record_check(checks, "new_rational_vs_direct_matrix_on_actual_201_inputs", matrix_error <= PARITY_REL,
                 cases=201, maximum_relative_difference=matrix_error, tolerance=PARITY_REL)

    endpoints = prepared.viscosity_vectorized([1.0, 0.0, 1e-300, 0.0], [0.0, 1.0, 0.0, 1e200])
    expected = np.array([prepared.eta_H_Pa_s, prepared.eta_He_Pa_s,
                         prepared.eta_H_Pa_s, prepared.eta_He_Pa_s])
    record_check(checks, "vector_exact_pure_endpoints", np.array_equal(endpoints, expected), cases=4)
    record_check(checks, "scalar_exact_pure_endpoints",
                 prepared.viscosity(1.0, 0.0) == prepared.eta_H_Pa_s
                 and prepared.viscosity(0.0, 1.0) == prepared.eta_He_Pa_s, cases=2)
    trace = prepared.viscosity_vectorized([1e-300, 1.0], [1.0, 1e-300])
    trace_error = relative_difference(trace, [prepared.eta_He_Pa_s, prepared.eta_H_Pa_s])
    record_check(checks, "vector_trace_limits_without_floor", trace_error <= 1e-15,
                 maximum_relative_difference=trace_error, trace_weight=1e-300)
    for scaling in (1e-200, 1e200):
        error = relative_difference(prepared.viscosity_vectorized(hydrogen * scaling, helium * scaling), vectorized)
        record_check(checks, "vector_number_weight_homogeneity_" + str(scaling), error <= 2e-15,
                     maximum_relative_difference=error, common_scale=scaling)
    h_grid, he_grid = np.array([[1.0], [2.0]]), np.array([0.0, 1.0, 4.0])
    broadcast = prepared.viscosity_vectorized(h_grid, he_grid)
    broadcast_reference = np.array([[prepared.viscosity(h, he) for he in he_grid] for h in h_grid[:, 0]])
    record_check(checks, "vector_broadcasting", broadcast.shape == (2, 3)
                 and relative_difference(broadcast, broadcast_reference) <= PARITY_REL)

    # Check imported normalization against the source-stage result, without
    # rerunning its 40-composition matrix suite or assuming the old mass value.
    expected_q = np.array([5.669771561765608e-20, 2.8378312527861555e-20,
                           3.8072634581480334e-20, 4.64303606744764e-20])
    actual_q = np.array([prepared.QHH22_m2, prepared.QHHe11_m2,
                         prepared.QHHe22_m2, prepared.QHeHe22_m2])
    normalization_error = relative_difference(actual_q, expected_q)
    record_check(checks, "imported_pi_angstrom2_normalization", normalization_error <= 1e-15,
                 maximum_relative_difference=normalization_error,
                 reference="source-stage PROTOTYPE_EXECUTION.json T20000 collision integrals")
    boundary_values = [collision_integral(temperature, ("H", "H"), "Q22") for temperature in (50.0, 50000.0)]
    record_check(checks, "inclusive_fit_temperature_boundaries", all(value > 0.0 for value in boundary_values),
                 temperatures_K=[50.0, 50000.0])

    invalid_calls = [
        ("scalar_zero_pair", lambda: prepared.viscosity(0.0, 0.0)),
        ("scalar_negative_trace", lambda: prepared.viscosity(-1e-300, 1.0)),
        ("scalar_nan", lambda: prepared.viscosity(float("nan"), 1.0)),
        ("scalar_infinity", lambda: prepared.viscosity(1.0, float("inf"))),
        ("vector_zero_pair", lambda: prepared.viscosity_vectorized([1.0, 0.0], [1.0, 0.0])),
        ("vector_negative_trace", lambda: prepared.viscosity_vectorized([-1e-300], [1.0])),
        ("vector_nan", lambda: prepared.viscosity_vectorized([float("nan")], [1.0])),
        ("vector_infinity", lambda: prepared.viscosity_vectorized([0.0], [float("inf")])),
        ("vector_complex", lambda: prepared.viscosity_vectorized([1.0 + 2.0j], [1.0])),
        ("vector_bad_broadcast", lambda: prepared.viscosity_vectorized([1.0, 2.0], [1.0, 2.0, 3.0])),
        ("temperature_below_domain", lambda: prepare_neutral_transport(49.0, atomic_mass, 4.0 * atomic_mass)),
        ("temperature_above_domain", lambda: prepare_neutral_transport(50001.0, atomic_mass, 4.0 * atomic_mass)),
        ("temperature_nan", lambda: prepare_neutral_transport(float("nan"), atomic_mass, 4.0 * atomic_mass)),
        ("zero_mass", lambda: prepare_neutral_transport(T_K, 0.0, 4.0 * atomic_mass)),
        ("negative_mass", lambda: prepare_neutral_transport(T_K, atomic_mass, -atomic_mass)),
        ("infinite_mass", lambda: prepare_neutral_transport(T_K, atomic_mass, float("inf"))),
    ]
    rejected = []
    for name, call in invalid_calls:
        try:
            call()
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError("Invalid input was accepted: " + name)
    record_check(checks, "explicit_invalid_input_rejections", len(rejected) == len(invalid_calls),
                 count=len(rejected), cases=rejected)
    return vectorized, matrix, matrix_error


def diagnostic_workload(lane, background):
    """Identical per-sweep preparation, physical inputs and four output columns.

    Each timed call prepares all temperature/mass factors, validates physical
    arrays, executes the chosen viscosity interface including its weight
    validation and allocations, constructs p/nu/chi, and validates outputs.
    Only file I/O and immutable JSON loading at module import are excluded.
    """
    prepared = prepare_neutral_transport(T_K, atomic_mass, 4.0 * atomic_mass)
    hydrogen = np.asarray(background["hydrogen_density"], dtype=np.float64)
    helium = np.asarray(background["helium_density"], dtype=np.float64)
    hubble = np.asarray(background["hubble"], dtype=np.float64)
    if not (hydrogen.shape == helium.shape == hubble.shape == (201,)):
        raise ValueError("The matched diagnostic workload requires 201 saved epochs")
    if not np.all(np.isfinite([hydrogen, helium, hubble])) or np.any(hubble <= 0.0):
        raise ValueError("Finite densities and positive H are required")
    if lane == "scalar_rational":
        viscosity = np.array([prepared.viscosity(h, he) for h, he in zip(hydrogen, helium)])
    elif lane == "vector_rational":
        viscosity = prepared.viscosity_vectorized(hydrogen, helium)
    elif lane == "vector_matrix":
        viscosity = matrix_reference_vectorized(prepared, hydrogen, helium)
    else:
        raise ValueError("Unknown benchmark lane")
    pressure = (hydrogen + helium) * KB_J_K * T_K
    nu_match = pressure / viscosity
    chi_match = nu_match / hubble
    outputs = np.column_stack((viscosity, pressure, nu_match, chi_match))
    if not np.all(np.isfinite(outputs)) or np.any(outputs <= 0.0):
        raise ValueError("All diagnostic outputs must be finite and positive")
    return outputs


def matched_benchmark(background, repeats, checks):
    lanes = ["scalar_rational", "vector_rational", "vector_matrix"]
    start = time.perf_counter()
    warm = {lane: diagnostic_workload(lane, background) for lane in lanes}
    accuracy = {lane: relative_difference(warm[lane], warm["vector_matrix"]) for lane in lanes}
    record_check(checks, "matched_benchmark_output_accuracy", max(accuracy.values()) <= PARITY_REL,
                 maximum_relative_difference_by_lane=accuracy, tolerance=PARITY_REL)
    trials = []
    for trial in range(5):
        order = lanes[trial % len(lanes):] + lanes[:trial % len(lanes)]
        times, checksums = {}, {}
        for lane in order:
            if time.perf_counter() - start > 25.0:
                raise TimeoutError("Bounded benchmark exceeded its 25-second admission budget")
            before = time.perf_counter()
            for _ in range(repeats):
                result = diagnostic_workload(lane, background)
            times[lane] = time.perf_counter() - before
            checksums[lane] = float(np.sum(result))
        trials.append(dict(trial=trial + 1, execution_order=order,
                           total_wall_seconds=times, output_checksums=checksums))
    elapsed = time.perf_counter() - start
    record_check(checks, "benchmark_under_30_seconds", elapsed < 30.0, elapsed_wall_seconds=elapsed)
    medians = {lane: statistics.median(row["total_wall_seconds"][lane] for row in trials) for lane in lanes}
    return dict(trials=5, sweeps_per_trial=repeats, epochs_per_sweep=201,
                output_columns=["eta_neutral_Pa_s", "p_neutral_Pa", "nu_match_per_s", "chi_match"],
                preparation="All collision integrals and temperature/mass factors prepared once per 201-epoch sweep in every lane",
                included="Input conversion/validation, weight scaling, array allocation and endpoint masks, solve/evaluation, all four outputs and finite/positive output validation",
                excluded="File I/O, source JSON loading at module import, warmup/accuracy comparison from individual lane times",
                vectorization_overhead_included=True,
                warmup_sweeps_per_lane=1, trial_order="rotating order; no assumed speedup",
                raw_trials=trials, total_benchmark_wall_seconds=elapsed,
                median_seconds_per_trial=medians,
                median_seconds_per_201_epoch_sweep={lane: value / repeats for lane, value in medians.items()},
                vector_rational_speedup_over_vector_matrix=medians["vector_matrix"] / medians["vector_rational"],
                vector_rational_speedup_over_scalar_rational=medians["scalar_rational"] / medians["vector_rational"],
                maximum_relative_output_difference_by_lane=accuracy,
                claim_scope="This host and the 201-epoch neutral diagnostic only; no HE32 IVP or campaign speedup")


def summary(values):
    values = np.asarray(values)
    return dict(minimum=float(values.min()), maximum=float(values.max()),
                initial=float(values[0]), final=float(values[-1]))


def run_worker(args):
    env = environment()
    checks = []
    background = load_background(args.background, args.he32_unit, checks)
    prepared = prepare_neutral_transport(T_K, atomic_mass, 4.0 * atomic_mass)
    eta, matrix_eta, matrix_error = affected_formula_checks(prepared, background, checks)
    outputs = diagnostic_workload("vector_rational", background)
    benchmark = matched_benchmark(background, args.repeats, checks)
    columns = ["N", "a", "z", "H_per_s", "nH_reference_m3", "H1_q0_per_H", "He4_q0_per_H",
               "n_H1_q0_m3", "n_He4_q0_m3", "eta_neutral_Pa_s", "p_neutral_Pa",
               "nu_match_per_s", "chi_match", "eta_matrix_Pa_s", "eta_matrix_relative_difference"]
    table = np.column_stack((background["epoch"], background["scale_factor"], background["redshift"],
                             background["hubble"], background["nH_reference"],
                             background["hydrogen_abundance"], background["helium_abundance"],
                             background["hydrogen_density"], background["helium_density"],
                             outputs, matrix_eta, np.abs(eta - matrix_eta) / matrix_eta))
    stream = io.StringIO()
    np.savetxt(stream, table, delimiter=",", header=",".join(columns), comments="", fmt="%.17g")
    csv_path = UNIT / "results" / CSV_NAME
    atomic_write(csv_path, stream.getvalue().encode())
    source_hashes = {"src/neutral_transport.py": sha256(UNIT / "src/neutral_transport.py"),
                     "checks/check_transport.py": sha256(Path(__file__)),
                     "data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json": sha256(DATA_PATH)}
    result = dict(schema="he34.neutral_transport.saved_background.v1",
                  workflow_version="1.0.0", approval_version="0.2", status="passed",
                  scope="Instantaneous prescribed-common-T H1_q0/He4_q0 neutral transport diagnostic",
                  temperature_K=T_K, temperature_domain_K=[50.0, 50000.0],
                  background=background["provenance"], epochs=201,
                  mass_model=dict(convention="HE32 A*m_u baryon census applied to selected neutral transport",
                      H1_mass_kg=float(atomic_mass), He4_mass_kg=float(4.0 * atomic_mass),
                      atomic_mass_constant_kg=float(atomic_mass), provider="scipy.constants.atomic_mass",
                      scipy_version=scipy.__version__,
                      limitation="Mass-number approximation; not precision neutral atomic isotope masses; electron binding and nuclear mass defects omitted"),
                  matching=dict(pressure="p_neutral=(n_H1_q0+n_He4_q0)*k_B*T",
                      nu_match="p_neutral/eta_neutral", chi_match="nu_match/H_saved",
                      interpretation="Hydrodynamic viscosity matching; not an exact transient collision-operator relaxation eigenvalue",
                      used_as_prescribed_mechanical_chi=False, full_gas_closure=False,
                      missing=["electron/ion and other isotope transport", "reactive tensor source moments",
                               "momentum/energy common-state validity checks", "self-consistent temperature and metric feedback"]),
                  coefficients={key: value for key, value in asdict(prepared).items() if not key.startswith("_")},
                  ranges={"eta_neutral_Pa_s": summary(outputs[:, 0]), "p_neutral_Pa": summary(outputs[:, 1]),
                          "nu_match_per_s": summary(outputs[:, 2]), "chi_match": summary(outputs[:, 3]),
                          "n_H1_q0_m3": summary(background["hydrogen_density"]),
                          "n_He4_q0_m3": summary(background["helium_density"])},
                  diagnostic_flags=dict(epochs_chi_below_1=int(np.sum(outputs[:, 3] < 1.0)),
                      epochs_chi_below_10=int(np.sum(outputs[:, 3] < 10.0)),
                      meaning="Flags describe this matching diagnostic; no hydrodynamic validity certificate is inferred"),
                  numerical_comparison=dict(reference="direct independent batched 2x2 G solve on 201 actual interior inputs",
                      maximum_relative_viscosity_difference=matrix_error, acceptance_relative=PARITY_REL),
                  csv=dict(path="results/" + CSV_NAME, sha256=sha256(csv_path), rows=201, columns=columns),
                  checks=checks, benchmark=benchmark, environment=env, source_sha256=source_hashes,
                  reused_evidence=dict(source_stage="neutral_viscosity_prototype.py / PROTOTYPE_EXECUTION.json",
                      prototype_source_sha256="bb3e7bb493b62a373b2055db82b985200b90ac5c4c8229d579f833d2197b7dc6",
                      data_sha256=DATA_SHA256, prior_matrix_cases=40,
                      prior_maximum_relative_difference=5.111955429020404e-16,
                      original_40_case_suite_rerun=False,
                      reuse_scope="Source derivation and original scalar prototype evidence only; newly written paths checked above"),
                  new_HE32_IVPs=0, new_HE32_renders=0)
    atomic_json(UNIT / "results/NEUTRAL_TRANSPORT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--background", type=Path, required=True)
    parser.add_argument("--he32-unit", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=200)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 500:
        parser.error("--repeats must be between 1 and 500 for the bounded diagnostic")
    if args.worker:
        print(json.dumps(run_worker(args), indent=2, allow_nan=False))
        return 0

    command = [sys.executable, str(Path(__file__).resolve()), "--background", str(args.background.resolve()),
               "--he32-unit", str(args.he32_unit.resolve()), "--repeats", str(args.repeats), "--worker"]
    child_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    started_utc = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    try:
        completed = subprocess.run(command, capture_output=True, text=True, env=child_env, timeout=45)
        execution = dict(command=command, cwd=os.getcwd(), started_utc=started_utc,
                         exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr,
                         wall_time_seconds=time.perf_counter() - start, timed_out=False)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        execution = dict(command=command, cwd=os.getcwd(), started_utc=started_utc, exit_code=124,
                         stdout=stdout, stderr=stderr, wall_time_seconds=time.perf_counter() - start,
                         timed_out=True, timeout_seconds=45)
    evidence_path = UNIT / "evidence/TRANSPORT_VALIDATION.json"
    history = []
    if evidence_path.exists():
        previous = json.loads(evidence_path.read_text())
        history = previous.get("previous_executions", []) + [previous["execution"]]
    result = json.loads(execution["stdout"]) if execution["exit_code"] == 0 else None
    evidence = dict(schema="he34.neutral_transport.validation_execution.v1", workflow_version="1.0.0",
                    approval_version="0.2", status="passed" if execution["exit_code"] == 0 else "failed",
                    launcher_command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                    execution=execution, previous_executions=history,
                    result_sha256=sha256(UNIT / "results/NEUTRAL_TRANSPORT.json") if result else None,
                    checks_count=len(result["checks"]) if result else 0,
                    source_sha256=result["source_sha256"] if result else
                        {"checks/check_transport.py": sha256(Path(__file__)),
                         "src/neutral_transport.py": sha256(UNIT / "src/neutral_transport.py")})
    atomic_json(evidence_path, evidence)
    print(json.dumps(dict(status=evidence["status"], exit_code=execution["exit_code"],
                         checks=evidence["checks_count"], wall_time_seconds=execution["wall_time_seconds"],
                         evidence=str(evidence_path),
                         numerical_comparison=result["numerical_comparison"] if result else None,
                         ranges=result["ranges"] if result else None,
                         benchmark=result["benchmark"] if result else None), indent=2, allow_nan=False))
    if execution["stderr"]:
        print(execution["stderr"], file=sys.stderr, end="")
    return execution["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
