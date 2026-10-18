"""Run the one prescribed bounded suite and one performance comparison."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("test_residual_qr",ROOT/"tests/test_residual_qr.py")
tests=importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
OUT=ROOT/"results/laneA"
OUT.mkdir(parents=True,exist_ok=True)


def direct_reference(V,KV,u,W,grid,etas):
    start=time.perf_counter()
    C=V.conj().T@KV
    J=(C+C.conj().T)/2
    nodes,Y=np.linalg.eigh(J)
    e1=np.zeros(J.shape[0]);e1[0]=1
    coefficients=Y.conj().T@e1
    d,E=u-V[:,0],KV-V@J
    delta_row=u.conj()@V-e1.conj()
    norm_u=np.linalg.norm(u)
    setup_s=time.perf_counter()-start
    start=time.perf_counter()
    residuals=np.empty((len(etas),len(grid)))
    bounds=np.empty_like(residuals)
    scalars=np.empty(residuals.shape,dtype=complex)
    for i,eta in enumerate(etas):
        for j,omega in enumerate(grid):
            t=Y@(coefficients/(omega+1j*eta-nodes))
            rn=np.linalg.norm(d+E@t)
            residuals[i,j]=rn
            bounds[i,j]=norm_u*rn/eta+abs(delta_row@t)
            scalars[i,j]=t[0]
    density=W*bounds/np.pi
    evaluation_s=time.perf_counter()-start
    return {"setup_s":setup_s,"evaluation_s":evaluation_s,"total_s":setup_s+evaluation_s,
            "residual_norm":residuals,"scalar_bound":bounds,"scalar_resolvent":scalars,"density_bound":density}


def performance_once():
    K,V,KV,u=tests.hermitian_fixture(N=512,m=32)
    grid=np.linspace(0.,20.,2001)
    etas=np.array([.05,.1,.2])
    direct=direct_reference(V,KV,u,1.,grid,etas)
    output=tests.qr.residual_diagnostic_qr(V,KV,u,1.,grid,etas,64,256)
    summary=output["summary"]
    record={"seed":tests.SEED,"N":512,"m":32,"dtype":"float64","P":6003,"block_rows":64,"batch_points":256,
            "direct":{k:direct[k] for k in ("setup_s","evaluation_s","total_s")},
            "QR":{k:summary[k] for k in ("setup_s","evaluation_s","total_s","cache_storage_bytes","workspace_estimate_bytes")},
            "direct_total_over_QR_total":direct["total_s"]/summary["total_s"],
            "max_abs_norm_difference":float(np.max(np.abs(direct["residual_norm"]-output["residual_norm"]))),
            "max_abs_bound_difference":float(np.max(np.abs(direct["scalar_bound"]-output["scalar_bound"]))),
            "performance_pass_requires_speedup":False,"production_performance":"NOT_MEASURED","physical_H_actions":0}
    # Same frozen tolerances at every benchmark point, using the direct eigensolve t.
    C=V.T@KV;J=(C+C.T)/2
    nodes,Y=np.linalg.eigh(J)
    c=Y.T@np.eye(32)[:,0]
    d=u-V[:,0];E=KV-V@J
    scaled=[]
    for i,eta in enumerate(etas):
        T=Y@(c[:,None]/(grid[None,:]+1j*eta-nodes[:,None]))
        tn=np.linalg.norm(T,axis=0)
        alpha=np.linalg.norm(d)+np.linalg.norm(E)*tn
        rho=np.linalg.norm(u)+np.linalg.norm(V[:,0])+(np.linalg.norm(KV)+np.linalg.norm(V)*np.linalg.norm(J,2))*tn
        slack=5e-12*np.maximum(1.,alpha)+50*np.finfo(float).eps*np.maximum(1.,rho)
        nerr=np.abs(direct["residual_norm"][i]-output["residual_norm"][i])
        berr=np.abs(direct["scalar_bound"][i]-output["scalar_bound"][i])
        if not np.all(nerr<=slack):raise AssertionError("benchmark norm tolerance failed")
        if not np.all(berr<=np.linalg.norm(u)*slack/eta+1e-11*np.maximum(1.,np.abs(direct["scalar_bound"][i]))):raise AssertionError("benchmark B tolerance failed")
        scaled.append(float(np.max(nerr/slack)))
    record["max_scaled_norm_difference"]=max(scaled)
    np.savez(OUT/"performance_arrays.npz",grid=grid,etas=etas,qr_residual_norm=output["residual_norm"],direct_residual_norm=direct["residual_norm"],qr_scalar_bound=output["scalar_bound"],direct_scalar_bound=direct["scalar_bound"])
    return record


def main():
    runtime={"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),
             "requested_executor_model":"gpt-6.1-sol","observed_runtime_model":"UNKNOWN",
             "thread_environment":{name:os.environ.get(name) for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS")},
             "limits":{"N_max":512,"m_max":32,"physical_H_actions":0,"NCP_actions":0,"actual_checkpoint_execution":"NOT_RUN"}}
    (OUT/"runtime.json").write_text(json.dumps(runtime,indent=2)+"\n")
    with (OUT/"numpy_config.txt").open("w") as f:
        with contextlib.redirect_stdout(f):np.show_config()
    started=time.perf_counter()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    report={"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"suite_wall_s":time.perf_counter()-started,
            "observations":tests.OBSERVATIONS,"scientific_admission":"PENDING_INDEPENDENT_REVIEW"}
    (OUT/"test_observations.json").write_text(json.dumps(report,indent=2)+"\n")
    if not result.wasSuccessful():return 1
    performance=performance_once()
    (OUT/"performance.json").write_text(json.dumps(performance,indent=2)+"\n")
    print(json.dumps({"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"performance":performance},indent=2))
    return 0


if __name__=="__main__":sys.exit(main())
