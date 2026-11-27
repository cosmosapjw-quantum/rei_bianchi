#!/usr/bin/env python3
"""One new analytical case through the actual ABI2 PackedBridge wrapper."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import traceback

import numpy as np
from scipy.sparse import csr_matrix

LANE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LANE / 'src'))
from packed_reference import PackedBridge, PackedSegmentCallbacks
from optimized_model import PackedJacobian
from smoke_packed import (N, DT, SCALE, Y0, FORCING, LEDGER_ROWS,
                          physical_matrix, analytic, atomic_json)


class AnalyticModel:
    """Triangular physical model, unrelated to the HE29 reaction owner."""
    def __init__(self):
        self.matrix = np.array(physical_matrix())
        self.scale = np.array(SCALE)

    def rhs(self, t, y):
        result = self.matrix @ y
        result[0] += FORCING * t
        return result

    def jac(self, t, y):
        return csr_matrix(self.matrix)

    def prepare_jacobian(self, t, y):
        rows = list(range(4)) + [4] + [5+j for j in LEDGER_ROWS]
        return PackedJacobian(self.matrix[:, :4], self.matrix[rows, 4:5])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--library',required=True)
    ap.add_argument('--receipt',required=True)
    ap.add_argument('--output',required=True)
    args = ap.parse_args()
    source_paths = [Path(__file__), Path(__file__).with_name('smoke_packed.py'),
                    LANE/'src/packed_reference.py', LANE/'src/optimized_model.py',
                    LANE.parent/'vigilode_20261019/src/vigilode_callbacks.py']
    before = {str(p):sha(p) for p in source_paths}
    result = {'schema':'he29.optimized.wrapper_smoke.v1','status':'RUNNING',
        'source_before':before,'scope':'one new n24 analytical ABI2 wrapper case',
        'native_owner_calls':0,'old_suites_replayed':0,'thread_count':1,
        'library_sha256':sha(Path(args.library)), 'build_identity_sha256':sha(Path(args.receipt))}
    try:
        bridge = PackedBridge(args.library,args.receipt)
        model = AnalyticModel()
        callbacks = PackedSegmentCallbacks(model,0.0,DT,model.scale)
        start = time.perf_counter()
        output,evidence = bridge.segment(callbacks,np.array(Y0)/model.scale,
            threads=1,initial_step=0.01,max_step=0.25)
        result['wall_seconds'] = time.perf_counter()-start
        result['evidence'] = evidence
        result['analytic_max_abs_error'] = float(np.max(np.abs(output*model.scale-analytic(DT))))
        assert result['analytic_max_abs_error'] <= 1e-9
        assert evidence['returncode']==0 and evidence['stats']['abi_version']==2
        assert evidence['telemetry']['jvp_mode']=='rust-packed-exact-state'
        assert evidence['telemetry']['packed_prepare_successes']==callbacks.counts['packed_preparations']
        assert evidence['telemetry']['packed_cache_hits']>0
        assert evidence['stats']['callback_jvp_calls']==0
        result['source_after'] = {str(p):sha(p) for p in source_paths}
        assert result['source_after']==before
        result['status']='PASS_SCOPED'
    except BaseException:
        result['status']='FAILED_PRESERVED';result['failure']=traceback.format_exc()
    atomic_json(Path(args.output),result)
    print(json.dumps({k:result.get(k) for k in ['status','analytic_max_abs_error','failure']}))
    return 0 if result['status']=='PASS_SCOPED' else 1


if __name__=='__main__':sys.exit(main())
