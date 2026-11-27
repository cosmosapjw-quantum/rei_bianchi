"""Paired ABI2 timing of a manufactured HE29-shaped nonautonomous IVP.

Same n=K+23, physical coefficient layout, full state norm, input, solver and
tolerances for Python-CSR and packed threads1/2/4. This contains no native
chemistry, source table or physical HE29 solution. Each row is written before
the next size starts; failure preserves earlier rows and raw telemetry.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import traceback

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
import scipy

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
from optimized_model import PackedJacobian, PHOTON_LEDGER_ROWS
from packed_reference import PackedBridge, PackedSegmentCallbacks
from vigilode_reference import VigilODEFailure


class ManufacturedStructure:
    """Fixed Jacobian and analytic y*(t); all ledger inputs remain passive."""
    def __init__(self, k):
        self.K, self.n = k, k+23
        n = self.n
        # Powers of two expose nontrivial physical scaling without reordering.
        self.scale = np.exp2((np.arange(n) % 13)-6.)
        self.base = 1. + .07*np.cos(np.arange(n))
        self.amplitude = .03*np.sin(np.arange(n)+.3)
        gas, photon = np.zeros((n,4)), np.zeros((12,k))
        for j in range(4):
            gas[j,j] = -(j+1.)
            gas[4:4+k,j] = .005*np.cos(np.arange(k)+j) * self.scale[4:4+k]/self.scale[j]
            gas[4+k:,j] = .001*(j+1)*self.scale[4+k:]/self.scale[j]
            photon[j] = (.003*(j+1)/k)*self.scale[j]/self.scale[4:4+k]
        photon[4] = -(2.+np.arange(k)%5)
        for j, ledger in enumerate(PHOTON_LEDGER_ROWS):
            photon[j+5] = .001*(j+1)/k*self.scale[4+k+ledger]/self.scale[4:4+k]
        self.packed = PackedJacobian(gas, photon)
        self.matrix = self.packed.csr()

    def exact(self, t):
        return self.scale*(self.base+self.amplitude*np.sin(t))

    def rhs(self, t, y):
        return self.matrix @ (y-self.exact(t)) + self.scale*self.amplitude*np.cos(t)

    def jac(self, t, y):
        return self.matrix

    def prepare_jacobian(self, t, y):
        return self.packed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--library", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--rounds", type=int, default=7)
    args = ap.parse_args()
    if not 3 <= args.rounds <= 15:
        ap.error("rounds must be 3..15")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    rows = []
    modes = (("python_csr",1), ("rust_packed",1), ("rust_packed",2), ("rust_packed",4))
    try:
        bridge = PackedBridge(args.library, args.receipt)
        for k in (512,640,896):
            model = ManufacturedStructure(k)
            initial = model.exact(0.)/model.scale
            # Reuse the same callback object for one extra call: this is a
            # regression for invocation-vs-lifetime telemetry accounting.
            reused = PackedSegmentCallbacks(model, 0., 1., model.scale)
            first, first_ev = bridge.segment(reused, initial)
            again, again_ev = bridge.segment(reused, initial)
            assert np.array_equal(first.view(np.uint64), again.view(np.uint64))
            assert first_ev["python_callbacks"]["packed_preparations"] == again_ev["python_callbacks"]["packed_preparations"]
            samples, evidence, endpoints = [], {}, {}
            for mode, threads in modes:
                cb = PackedSegmentCallbacks(model, 0., 1., model.scale)
                z, ev = bridge.segment(cb, initial, mode=mode, threads=threads)
                key = f"{mode}_{threads}"
                evidence[key], endpoints[key] = ev, z
            oracle = endpoints["python_csr_1"]
            for key,z in endpoints.items():
                assert np.array_equal(oracle.view(np.uint64), z.view(np.uint64)), key
                assert evidence[key]["stats"]["attempts"] == evidence["python_csr_1"]["stats"]["attempts"]
            error = float(np.max(np.abs(oracle-model.exact(1.)/model.scale)))
            assert error <= 2e-9, (k,error)
            for index in range(args.rounds):
                record = {}
                order = modes[index%4:]+modes[:index%4]
                for mode, threads in order:
                    callback = PackedSegmentCallbacks(model,0.,1.,model.scale)
                    start = time.perf_counter_ns()
                    z, ev = bridge.segment(callback,initial,mode=mode,threads=threads)
                    record[f"{mode}_{threads}"] = (time.perf_counter_ns()-start)/1e9
                    assert np.array_equal(oracle.view(np.uint64), z.view(np.uint64))
                    assert ev["stats"]["attempts"] == evidence["python_csr_1"]["stats"]["attempts"]
                samples.append(record)
            row = dict(k=k,n=model.n,all_endpoint_bits_equal=True,
                analytic_max_scaled_abs_error=error,full_state_error_norm=True,
                repeated_callback_regression="PASS",round_seconds=samples,
                median_seconds={key:statistics.median(x[key] for x in samples) for key in samples[0]},
                median_paired_speedup_over_python={key:statistics.median(x["python_csr_1"]/x[key] for x in samples) for key in samples[0]},
                median_paired_speedup_over_packed1={key:statistics.median(x["rust_packed_1"]/x[key] for x in samples) for key in samples[0]},
                evidence=evidence, packed_bytes=model.packed.nbytes)
            write(out/f"K{k}.json", row); rows.append(row)
            print(json.dumps({key:row[key] for key in ("k","n","analytic_max_scaled_abs_error","median_seconds","median_paired_speedup_over_python","median_paired_speedup_over_packed1")}),flush=True)
        sources = (Path(__file__),LANE/"src/optimized_model.py",LANE/"src/packed_reference.py")
        result = dict(schema="he29.optimization.paired_ffi.v1",status="PASS_SCOPED",rows=rows,
            scope="manufactured nonautonomous HE29-shaped IVP; cached fixed Jacobian; no native owner/source table",
            source_files={str(p.relative_to(LANE)):digest(p) for p in sources},
            library_sha256=digest(args.library),build_receipt_sha256=digest(args.receipt),
            environment=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
                affinity=sorted(os.sched_getaffinity(0)),cpu_max=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
                thread_environment={key:os.environ[key] for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS')}),
            native_owner_calls=0,inherited_scientific_tests_rerun=0,
            claims=dict(native_speedup="NOT_MEASURED",hardware_simd="NOT_CLAIMED",parallelism="independent photon output rows; fixed within-row accumulation"))
        write(out/"RESULT.json",result)
    except BaseException as exc:
        write(out/"FAILURE.json",dict(status="FAILED_PRESERVED",error=repr(exc),traceback=traceback.format_exc(),completed_sizes=len(rows),
            evidence=getattr(exc,"evidence",None),state=getattr(exc,"state",None),native_owner_calls=0))
        raise


if __name__ == "__main__":
    main()
