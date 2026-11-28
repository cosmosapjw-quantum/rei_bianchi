"""No eigensolves: sparse direct operator parity, rejection seams, timings."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"code"), str(ROOT/"reference")]
import partialwave_centered as reference
import fast_observables as fast

KEYS = ("L_center_over_minus_i_hbar", "L_O_over_minus_i_hbar", "p_x_over_minus_i_hbar", "dipole_x")
TOL = 2e-10
FIXTURE = ROOT/"fixtures/C1B_B_l96"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_pair(folder):
    path = Path(folder)/"B_l96.json"
    record = json.loads(path.read_text())
    expected_reference = record["identities"]["code_sha256"]["partialwave_centered.py"]
    if sha(reference.__file__) != expected_reference:
        raise ValueError("reference solver byte identity mismatch")
    config = record["config"]
    if (config["R"], config["center"], config["lmax"]) != (2., "B", 96):
        raise ValueError("unexpected frozen physical configuration")
    states, identities = [], {"B_l96.json": {"sha256": sha(path), "bytes": path.stat().st_size}}
    for m, item in enumerate(record["states"]):
        p = Path(folder)/Path(item["array_file"]["path"]).name
        ident = {"sha256": sha(p), "bytes": p.stat().st_size}
        if any(ident[k] != item["array_file"][k] for k in ident):
            raise ValueError("frozen state byte identity mismatch")
        identities[p.name] = ident
        with np.load(p, allow_pickle=False) as arr:
            states.append(reference.PartialWaveState(config["R"], 1., 2., m,
                arr["ls"], arr["boundaries"], config["degree"], arr["coefficients"],
                item["energy"], item["residual"], item["mass_norm"], item["phase_probe"], item["metadata"]))
    if len(states) != 2:
        raise ValueError("frozen fixture must contain exactly two states")
    return states, identities


def random_pair(seed=8731, center="B"):
    rng = np.random.default_rng(seed)
    states = []
    # Unequal partitions and degree, absent angular channels, same physical box.
    for m, mesh, degree, ls in ((0, [0., .13, .6, 1.2, 2., 3.7, 5.], 4, [0, 1, 3, 4, 7]),
                               (1, [0., .08, .4, 1.7, 2., 3., 4.3, 5.], 3, [1, 2, 4, 6, 7])):
        c = rng.normal(size=(len(ls), (len(mesh)-1)*degree+1))
        c[:, [0, -1]] = 0.
        states.append(reference.PartialWaveState(2., 1., 2., m, np.array(ls), np.array(mesh), degree, c,
            -1., 0., 1., 1., {"origin_center": center,
            "origin_shift_center_to_O": 2./3. if center == "B" else 0.}))
    return states


class OperatorParity(unittest.TestCase):
    def assert_parity(self, g, b, quadrature):
        before = [s.coefficients.copy() for s in (g, b)]
        norms = [s.mass_norm for s in (g, b)]
        expected = reference.direct_observables(g, b, quadrature)
        actual = fast.direct_observables(g, b, quadrature)
        for key in KEYS:
            self.assertLessEqual(abs(expected[key]-actual[key]), TOL, key)
        for state, coeff, norm in zip((g, b), before, norms):
            np.testing.assert_array_equal(state.coefficients, coeff)
            self.assertEqual(state.mass_norm, norm)
        self.assertEqual(actual["origin_center"], expected["origin_center"])
        self.assertEqual(actual["origin_shift_center_to_O"], expected["origin_shift_center_to_O"])

    def test_mismatched_partitions_and_default_orders(self):
        for center in ("O", "B"):
            for seed in (8731, 11):
                for q in (None, 5, 14):
                    self.assert_parity(*random_pair(seed, center), q)

    def test_frozen_l96(self):
        states, _ = frozen_pair(FIXTURE)
        self.assert_parity(*states, 14)

    def test_fail_closed_physics_origin_domain_and_shapes(self):
        g, b = random_pair()
        mutations = [lambda s: setattr(s, "R", np.nextafter(s.R, 3.)),
                     lambda s: s.metadata.update(origin_center="O"),
                     lambda s: s.metadata.update(origin_shift_center_to_O=1.),
                     lambda s: s.boundaries.__setitem__(-1, 6.),
                     lambda s: s.boundaries.__setitem__(2, s.boundaries[1]),
                     lambda s: s.ls.__setitem__(1, s.ls[0]),
                     lambda s: setattr(s, "coefficients", s.coefficients[:, :-1]),
                     lambda s: s.coefficients.__setitem__((0, 1), np.nan)]
        for mutate in mutations:
            changed = copy.deepcopy(b)
            mutate(changed)
            with self.assertRaises(ValueError):
                fast.direct_observables(g, changed, 14)
        with self.assertRaises(ValueError):
            fast.direct_observables(g, b, 4)

    def test_exact_sparse_cache_key_and_empty_pairs(self):
        fast.clear_caches()
        a = fast._angular_sparse((0, 1, 3, 7), (1, 2, 4, 8))
        b = fast._angular_sparse((0, 1, 3, 7), (1, 2, 4, 8))
        self.assertIs(a, b)
        changed = fast._angular_sparse((0, 1, 3, 8), (1, 2, 4, 8))
        self.assertIsNot(a, changed)
        for array in a:
            self.assertFalse(array.flags.writeable)
        g, b = random_pair()
        g.ls = np.array([0]); g.coefficients = g.coefficients[:1]
        b.ls = np.array([7]); b.coefficients = b.coefficients[:1]
        self.assert_parity(g, b, 14)

    def test_independence_from_energy_gap(self):
        g, b = random_pair()
        first = fast.direct_observables(g, b, 14)
        g.energy = -123.; b.energy = 999.
        second = fast.direct_observables(g, b, 14)
        self.assertEqual(first, second)


def benchmark(folder, repeats=7):
    states, inputs = frozen_pair(folder)
    # Warm radial polynomial cache in both paths, then measure coefficient-cache
    # cold costs separately. No state solves or normalization changes occur.
    reference._polynomials(states[0].degree)
    fast.clear_caches()
    t0 = time.perf_counter(); baseline = reference.direct_observables(*states, 14); ref_cold = time.perf_counter()-t0
    t0 = time.perf_counter(); candidate = fast.direct_observables(*states, 14); fast_cold = time.perf_counter()-t0
    timings = {"reference": [], "optimized": []}
    for rep in range(repeats):
        order = (("reference", reference.direct_observables), ("optimized", fast.direct_observables))
        if rep % 2:
            order = tuple(reversed(order))
        for key, fn in order:
            t0 = time.perf_counter(); fn(*states, 14); timings[key].append(time.perf_counter()-t0)
    diffs = {k: abs(candidate[k]-baseline[k]) for k in KEYS}
    medians = {k: statistics.median(v) for k, v in timings.items()}
    speedup = medians["reference"]/medians["optimized"]
    return {"scope": "frozen C1b R2 B_l96; direct operators only; NO_EIGENSOLVES",
        "quadrature": 14, "repeats": repeats,
        "input_identity": inputs, "reference_solver_sha256": sha(reference.__file__),
        "optimized_code_sha256": sha(fast.__file__), "test_code_sha256": sha(__file__),
        "contract_sha256": sha(ROOT/"CONTRACT.json"),
        "reference": baseline, "optimized": candidate, "max_abs_tolerance": TOL,
        "absolute_differences": diffs, "accuracy_pass": max(diffs.values()) <= TOL,
        "cold_after_common_radial_cache_seconds": {"reference": ref_cold, "optimized": fast_cold},
        "cold_speedup": ref_cold/fast_cold,
        "warm_seconds": timings, "warm_median_seconds": medians, "warm_median_speedup": speedup,
        "all_warm_optimized_faster_than_all_reference": max(timings["optimized"]) < min(timings["reference"]),
        "retain_optimized_research_default": max(diffs.values()) <= TOL and max(timings["optimized"]) < min(timings["reference"]),
        "norms_unchanged": [s.mass_norm for s in states], "norm_claim": "input property retained, not recertified",
        "thread_environment": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        "limitations": ["No 64-core host scaling measured", "Floating reduction ordering changes; no bitwise identity claim", "No scientific gate promotion"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-dir", type=Path, default=FIXTURE)
    ap.add_argument("--benchmark-output", type=Path)
    args = ap.parse_args()
    FIXTURE = args.fixture_dir
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OperatorParity))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.benchmark_output:
        if args.benchmark_output.exists():
            raise FileExistsError("existing evidence retained")
        measured = benchmark(FIXTURE)
        measured["tests_run"] = result.testsRun
        measured["test_status"] = "PASS"
        args.benchmark_output.write_text(json.dumps(measured, indent=2, ensure_ascii=False)+"\n")
        print(json.dumps(measured, indent=2, ensure_ascii=False))
