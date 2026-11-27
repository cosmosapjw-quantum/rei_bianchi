"""Paired, bounded assembly benchmark on original HE29 photon geometries.

The five RHS evaluations use a deterministic manufactured affine gas map to
isolate assembly.  This is not a native chemistry or end-to-end solver timing.
The original Model.jac is the baseline; no copy of its sparse loop is used.
"""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import os
from pathlib import Path
import platform
import pstats
import statistics
import sys
import time
import tracemalloc

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[_key] = "1"

import numpy as np
import scipy

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
from optimized_model import prepare_jacobian
from refined_source import RefinedSourceModel, GridSpec
from physics import Model, Y_HE


class DensityOnlyOwner:
    """Reuse saved native handshake density; refuse every native point call."""

    def density(self, a):
        return 1.89819845071402689e-7 / a**3, 1.54326099855957528e-8 / a**3

    def point(self, *args):
        raise AssertionError("assembly-only fixture cannot run native chemistry")


class AssemblyFixture:
    def __init__(self, model):
        self.K, self.scale = model.K, model.scale.copy()
        self.rates = model.rates
        n = self.K + 23
        rng = np.random.default_rng(290020)
        self.affine = rng.standard_normal((n, 4)) * self.scale[:, None] / self.scale[:4] * 1e-12
        self.affine[4:4+self.K, 3] = 0.
        self.affine[4+self.K:6+self.K] = 0.
        self.calls = 0

    def rhs(self, t, y):
        self.calls += 1
        return self.affine @ y[:4]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bench(function, repeat):
    start = time.perf_counter_ns()
    for _ in range(repeat):
        function()
    return (time.perf_counter_ns() - start) / repeat / 1e9


def peak(function):
    tracemalloc.start()
    out = function()
    _, size = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return int(size), out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--rounds", type=int, default=9)
    args = parser.parse_args()
    if not 3 <= args.rounds <= 31:
        parser.error("rounds must be in [3,31]")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for strips in (2, 4, 8):
        model = RefinedSourceModel(DensityOnlyOwner(), GridSpec(m=8, strips=strips), tabulate=False)
        t = float(model.t_end * .431)
        bounds = np.r_[0., model.breakpoints, model.t_end]
        i = int(np.searchsorted(bounds, t) - 1)
        model.set_interval(float(bounds[i]), float(bounds[i+1]))
        fixture, state = AssemblyFixture(model), model.initial_state()
        original = lambda: Model.jac(fixture, t, state)
        packed = lambda: prepare_jacobian(fixture, t, state)
        vectorized = lambda: packed().csr()
        before_calls = fixture.calls
        baseline, candidate = original(), vectorized()
        assert fixture.calls - before_calls == 10
        same = all(np.array_equal(getattr(baseline, a), getattr(candidate, a))
                   for a in ("indptr", "indices", "data"))
        assert same, "CSR byte/value/order mismatch"
        assert baseline.has_canonical_format and candidate.has_canonical_format
        for f in (original, vectorized, packed):
            f()
        timings = []
        for j in range(args.rounds):
            pair = {}
            for name, fn in (("original_lil", original), ("packed_csr", vectorized)) if j % 2 == 0 else (("packed_csr", vectorized), ("original_lil", original)):
                pair[name] = bench(fn, 3)
            pair["packed_only"] = bench(packed, 3)
            timings.append(pair)
        old_peak, _ = peak(original)
        csr_peak, _ = peak(vectorized)
        packed_peak, packed_value = peak(packed)
        speedups = [x["original_lil"] / x["packed_csr"] for x in timings]
        rows.append(dict(strips=strips, k=model.K, n=state.size, native_calls=0,
            csr_nonzeros=int(baseline.nnz), csr_exact_structure_and_values=same,
            csr_data_sha256=hashlib.sha256(baseline.data.tobytes()).hexdigest(),
            packed_bytes=packed_value.nbytes,
            csr_owned_array_bytes=sum(getattr(candidate, a).nbytes for a in ("data", "indices", "indptr")),
            peak_tracemalloc_bytes=dict(original_lil=old_peak, packed_csr=csr_peak, packed_only=packed_peak),
            timing_seconds=timings, median_speedup_packed_csr=float(statistics.median(speedups)),
            median_seconds={key:statistics.median(x[key] for x in timings) for key in timings[0]}))
        if strips == 4:
            profile = cProfile.Profile()
            profile.runcall(original)
            profile.dump_stats(str(out / "baseline_640.pstats"))
            with (out / "baseline_640_profile.txt").open("w") as log:
                pstats.Stats(profile, stream=log).sort_stats("cumulative").print_stats(30)
    result = dict(schema="he29.optimization.assembly.v1", status="COMPLETED_SCOPED",
        scope="original photon geometry; manufactured affine RHS; no native physics or end-to-end speed claim",
        original_science_revision="1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f",
        environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
            platform=platform.platform(), affinity=sorted(os.sched_getaffinity(0)),
            cpu_max=Path("/sys/fs/cgroup/cpu.max").read_text().strip(),
            thread_environment={k:os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "RAYON_NUM_THREADS")}),
        files={str(p.relative_to(LANE)):digest(p) for p in [Path(__file__), LANE / "src/optimized_model.py"]},
        rows=rows, old_scientific_tests_rerun=0, native_calls=0)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status":result["status"], "rows":[{k:v for k,v in x.items() if k not in ("timing_seconds",)} for x in rows]}, indent=2))


if __name__ == "__main__":
    main()
