"""Same-workload public-API microbenchmark, never a molecular/NCP scaling test."""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import statistics
import time
import numpy as np
from projector import weighted_overlap
from native_overlap import identity
from runtime_support import atomic_create, host_preflight, file_identity


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-library', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise SystemExit('CREATE_ONLY output already exists')
    host = host_preflight()
    results = []
    for n, k in ((4096, 5), (65536, 5), (131072, 6)):
        rng = np.random.default_rng(61002000+n+k)
        weights = np.exp(rng.uniform(-1, 1, n)).astype(np.float64)
        # Identical arrays, same explicit precision, same public wrapper path.
        u = np.asarray((rng.normal(size=(n,k))+1j*rng.normal(size=(n,k)))/np.sqrt(n), dtype=np.complex128)
        v = np.asarray((rng.normal(size=(n,k))+1j*rng.normal(size=(n,k)))/np.sqrt(n), dtype=np.complex128)
        digest = hashlib.sha256()
        for array in (u, v, weights):
            digest.update(array.tobytes())
        times = {'reference': [], 'native': []}
        answers = {}
        for backend in times:
            answers[backend] = weighted_overlap(u, v, weights, backend=backend,
                native_library=a.native_library if backend == 'native' else None)
        error = float(np.max(abs(answers['reference']-answers['native'])))
        if error > 2e-11:
            raise AssertionError(f'native/reference parity failed {error}')
        # Alternate order to reduce warm-cache/order bias; seven samples per backend.
        for sample in range(7):
            for backend in (('reference','native') if sample % 2 else ('native','reference')):
                start = time.perf_counter()
                weighted_overlap(u, v, weights, backend=backend,
                    native_library=a.native_library if backend == 'native' else None)
                times[backend].append(time.perf_counter()-start)
        medians = {b: statistics.median(t) for b,t in times.items()}
        results.append({'n_rows':n,'left_rank':k,'right_rank':k,
                        'input_sha256':digest.hexdigest(),'parity_max_abs':error,
                        'seconds':times,'median_seconds':medians,
                        'reference_over_native_median_ratio':medians['reference']/medians['native'],
                        'faster_observed_backend':min(medians,key=medians.get)})
    result = {'schema':'bass-he.c2f.overlap-benchmark.v1','scope':'same-input overlap public API only',
              'physical_evaluations':0,'NCP64_actual_scaling':'NOT_RUN','host':host,
              'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),
              'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),
              'native':identity(a.native_library),'benchmark_code':file_identity(__file__),
              'projector_code':file_identity(Path(__file__).with_name('projector.py')),
              'results':results,'production_default_changed':False}
    atomic_create(a.output,result)
    print(a.output)


if __name__ == '__main__':
    main()
