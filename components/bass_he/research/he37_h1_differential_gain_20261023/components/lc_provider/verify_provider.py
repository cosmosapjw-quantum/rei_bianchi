#!/usr/bin/env python3
"""Explicit affected verification of the new LC provider; no old-suite replay."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import tempfile
import time
import traceback

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import quad

from lc_ionization import (
    A0_M, EV_J, I_EV, I_J, KB_J_K, LCModel, ME_KG, MODEL_IDENTITY,
    MODEL_SCOPE, SOURCE_PDF_SHA256, sigma_m2, sdcs_m2_per_eV,
    tdcs_m2_per_eV_sr2, transfer_pdf_per_eV, transfer_u,
)

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.link(name, path)
        os.unlink(name)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def require_close(actual, reference, rtol, label):
    actual, reference = np.broadcast_arrays(actual, reference)
    absolute = np.abs(actual - reference)
    scale = np.maximum(np.abs(actual), np.abs(reference))
    rel = np.zeros_like(scale, dtype=float)
    np.divide(absolute, scale, out=rel, where=scale > 0)
    error = float(np.max(rel))
    assert np.isfinite(actual).all() and np.isfinite(reference).all(), label
    assert error <= rtol, (label, error, rtol)
    return error


def cross_section_normalization():
    mp.mp.dps = 80
    a = mp.mpf(str(A0_M)); ion = mp.mpf(str(I_EV))
    energies = [14.0, 2.0 * I_EV, 10.0 * I_EV, 100.0 * I_EV]
    rows = []
    for e in energies:
        em = mp.mpf(str(e))
        # Integrate original Eq85 directly; no total-cross-section formula oracle.
        target = mp.quad(lambda u: 4*mp.pi*a*a*ion*ion/(em*u*u), [ion, em])
        err = require_close(float(sigma_m2(e)), float(target), 3e-14, "sdcs->sigma")
        nodes = np.linspace(I_EV, e, 17)
        product = float(sigma_m2(e)) * transfer_pdf_per_eV(e, nodes)
        parity = require_close(sdcs_m2_per_eV(e, nodes), product, 3e-14, "conditional normalization")
        angle = require_close(tdcs_m2_per_eV_sr2(e, nodes)*(16*math.pi**2),
                              sdcs_m2_per_eV(e, nodes), 3e-14, "angular normalization")
        rows.append({"energy_eV": e, "sigma_m2": float(target),
                     "quadrature_relative_error": err, "conditional_error": parity,
                     "angle_normalization_error": angle})
    assert np.array_equal(sigma_m2([0., I_EV/2, I_EV]), np.zeros(3))
    edge = np.nextafter(I_EV, np.inf)
    # Exact binary64 inputs converted to arbitrary precision guard threshold subtraction.
    edge_ref = 4*mp.pi*a*a*mp.mpf(I_EV)*(mp.mpf(float(edge))-mp.mpf(I_EV))/mp.mpf(float(edge))**2
    edge_error = require_close(float(sigma_m2(edge)), float(edge_ref), 3e-14, "threshold neighbour")
    return {"rows": rows, "threshold_neighbour_relative_error": edge_error}


def energy_partition():
    rows = []
    qnodes = np.linspace(0., 1., 41)
    for e in [I_EV*(1+1e-7), 2*I_EV, 100*I_EV]:
        u = transfer_u(e, qnodes)
        assert np.all(np.diff(u) > 0) and u[0] == I_EV
        endpoint_error = abs(float(u[-1]) - e) / e
        assert endpoint_error < 3e-15
        # General CDF expression; near threshold use a tolerance for conditioning.
        cdf = e*(u-I_EV)/((e-I_EV)*u)
        cdf_abs = float(np.max(abs(cdf-qnodes)))
        cdf_gate = 5e-9 if e < 1.001*I_EV else 3e-14
        assert cdf_abs <= cdf_gate, (cdf_abs, cdf_gate)
        e1, e2 = e-u, u-I_EV
        assert np.min(e1) >= -3e-15*e and np.min(e2) >= -3e-15*e
        conservation = require_close(e1+e2, np.full_like(u,e-I_EV), 3e-14,
                                     "outgoing electron kinetic sum")
        if e > I_EV*1.001:
            norm, err = quad(lambda z: float(transfer_pdf_per_eV(e,z)), I_EV,e,
                             epsabs=3e-14,epsrel=3e-13)
            assert abs(norm-1) < 3e-13
            # Inclusive spectrum counts both electron labels and integrates to two.
            available=e-I_EV
            inclusive, _ = quad(lambda w: float(transfer_pdf_per_eV(e,w+I_EV))+
                                 float(transfer_pdf_per_eV(e,e-w)),0.,available,
                                 epsabs=3e-14,epsrel=3e-13)
            assert abs(inclusive-2) < 6e-13
        else:
            norm, err, inclusive = None,None,None
        rows.append({"energy_eV":e,"cdf_absolute_error":cdf_abs,
                     "cdf_gate":cdf_gate,"energy_relative_error":conservation,
                     "conditional_integral":norm,"integrator_estimate":err,
                     "inclusive_electron_count":inclusive})
    assert np.array_equal(transfer_u(I_EV, qnodes), np.full_like(qnodes,I_EV))
    return {"rows":rows,"zero_event_quantile_limit":I_EV}


def moments():
    mp.mp.dps=80
    me=mp.mpf(str(ME_KG)); a=mp.mpf(str(A0_M)); kb=mp.mpf(str(KB_J_K))
    ion=mp.mpf(str(I_EV))*mp.mpf(str(EV_J))
    temperatures=[2000.,20000.,200000.]
    output=LCModel().evaluate(temperatures)
    rows=[]
    for index,t in enumerate(temperatures):
        theta=kb*mp.mpf(str(t)); x=ion/theta; reference=[]
        for j in range(4):
            def original_integrand(y):
                energy=ion+theta*y
                cross=4*mp.pi*a*a*ion*(energy-ion)/(energy*energy)
                speed=mp.sqrt(2*energy/me)
                measure=2*mp.sqrt(energy)/(mp.sqrt(mp.pi)*theta**mp.mpf('1.5'))
                return (energy/theta)**j * speed*cross*measure*mp.exp(-y)*theta
            val=mp.quad(original_integrand,[0,1,5,20,100,mp.inf])
            reference.append(float(val*mp.exp(-x)*theta**j))
        error=require_close(output.moments_SI[index],reference,3e-13,"original sigma Maxwellian quadrature")
        rows.append({"temperature_K":t,"oracle_moments_SI":reference,
                     "observed_moments_SI":output.moments_SI[index].tolist(),
                     "maximum_relative_error":error})
    return {"arbitrary_precision_decimal_digits":80,"rows":rows,
            "maximum_relative_error":max(r["maximum_relative_error"] for r in rows),
            "oracle":"direct original sigma(E)*sqrt(2E/me)*Maxwell measure quadrature"}


def moment_relations():
    temperatures=np.array([2000.,20000.,200000.]); model=LCModel()
    outputs=model.evaluate(temperatures)
    alpha,beta,gamma,delta=outputs.moments_SI.T
    theta=KB_J_K*temperatures
    assert np.all(alpha*gamma >= beta*beta)
    assert np.all(outputs.conditional_mean_energy_J >= I_J)
    kerr=require_close(outputs.kappa2,4*gamma/(15*theta*theta),2e-15,"kappa2 units")
    logerr=float(np.max(abs(np.exp(outputs.log_moments_SI)/outputs.moments_SI-1)))
    assert logerr < 5e-14
    # New finite-difference check at interior T only; no old calculation repeated.
    t=20000.;h=2e-4
    values=model.evaluate(t*np.exp(np.array([-2*h,-h,h,2*h]))).moments_SI
    numerical=(values[0]-8*values[1]+8*values[2]-values[3])/(12*h)
    expected=outputs.moments_SI[1,1:]/(KB_J_K*t)-1.5*outputs.moments_SI[1,:3]
    derivative_error=require_close(numerical[:3],expected,3e-10,"moment ladder independent finite difference")
    return {"cauchy_schwarz_minimum_ratio":float(np.min(alpha*gamma/(beta*beta))),
            "mean_energy_eV":(outputs.conditional_mean_energy_J/EV_J).tolist(),
            "kappa2_error":kerr,"log_roundtrip_error":logerr,
            "moment_ladder_relative_error":derivative_error}


def guards():
    checks=0
    def rejected(call):
        nonlocal checks
        try:call()
        except (ValueError,TypeError,FloatingPointError):checks+=1
        else:raise AssertionError("invalid input accepted")
    model=LCModel()
    for value in [True,[True,False],20000+0j,[20000+1j],float('nan'),float('inf'),
                  [],[[20000.]],1999.99,200000.01,"20000",["20000"],None]:
        rejected(lambda value=value:model.evaluate(value))
    for fun,value in [(sigma_m2,-1.),(sigma_m2,True),(sigma_m2,complex(20,0))]:
        rejected(lambda fun=fun,value=value:fun(value))
    for e,q in [(I_EV-1,.5),(20.,-1e-9),(20.,1+1e-9),(20.,True),(np.inf,.5)]:
        rejected(lambda e=e,q=q:transfer_u(e,q))
    for e in [I_EV,I_EV-1.,0.]:
        rejected(lambda e=e:transfer_pdf_per_eV(e,I_EV))
    assert float(sdcs_m2_per_eV(I_EV,I_EV))==0
    assert float(transfer_pdf_per_eV(20.,I_EV-1))==0
    assert float(transfer_pdf_per_eV(20.,21.))==0
    assert not model.evaluate(2000.).moments_SI.flags.writeable
    return {"invalid_input_cases_rejected":checks,"outside_support_zero":True}


def immutable_and_batch():
    model=LCModel(); batch=model.evaluate([2000.,20000.,200000.])
    joined=np.concatenate([model.evaluate(t).moments_SI for t in batch.temperature_K])
    assert np.array_equal(joined,batch.moments_SI)
    for arr in [batch.temperature_K,batch.moments_SI,batch.log_moments_SI,
                batch.kappa2,batch.conditional_mean_energy_J,sigma_m2([20.])]:
        try:arr.setflags(write=True)
        except ValueError:pass
        else:raise AssertionError("array storage can be made mutable")
    try:model.identity="changed"
    except (AttributeError,TypeError):pass
    else:raise AssertionError("model is mutable")
    assert batch.identity==MODEL_IDENTITY and batch.model_scope==MODEL_SCOPE
    return {"scalar_vector_parity":"bitwise exact","immutable_arrays":6,
            "model_identity":batch.identity}


GROUPS={"cross_section_normalization":cross_section_normalization,
        "energy_partition":energy_partition,"moments":moments,
        "moment_relations":moment_relations,"guards":guards,
        "immutable_and_batch":immutable_and_batch}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--group",action="append",choices=list(GROUPS))
    parser.add_argument("--reason",default="new source-dependent provider implementation")
    args=parser.parse_args(); requested=args.group or list(GROUPS)
    identity_inputs={"model_identity":MODEL_IDENTITY,"code_sha256":digest(ROOT/"lc_ionization.py"),
                     "verifier_sha256":digest(__file__),"source_pdf_sha256":SOURCE_PDF_SHA256,
                     "numpy":np.__version__,"scipy":scipy.__version__,"mpmath":mp.__version__,
                     "python":platform.python_version()}
    identity=hashlib.sha256(json.dumps(identity_inputs,sort_keys=True).encode()).hexdigest()
    reused={}
    for path in sorted((ROOT/"attempts").glob("*/RESULT.json")):
        prior=json.loads(path.read_text())
        if prior.get("execution_identity")==identity:
            for name,item in prior.get("groups",{}).items():
                if item.get("status")=="PASS":reused[name]={"receipt":str(path),"item":item}
    pending=[name for name in requested if name not in reused]
    if not pending:
        print(json.dumps({"status":"REUSED_COMPLETE_PROVIDER_CHECKS",
                          "identity":identity,"groups":requested,"new_group_executions":0}))
        return
    start=datetime.now(timezone.utc); start_ns=time.perf_counter_ns()
    attempt=ROOT/"attempts"/("attempt_"+start.strftime("%Y%m%dT%H%M%S%fZ"))
    attempt.mkdir(parents=True,exist_ok=False)
    record={"schema":"he37.lc_provider_checks.v1","start_utc":start.isoformat(),
            "execution_identity":identity,"identity_inputs":identity_inputs,
            "reason":args.reason,"command":sys.argv,"new_group_executions":len(pending),
            "reused_groups":{g:reused[g]["receipt"] for g in requested if g in reused},
            "groups":{},"new_IVPs":0,"old_suite_replays":0,"new_benchmarks":0,
            "new_renders":0,"environment":{"python":sys.version,
             "platform":platform.platform(),"thread_env":{k:os.environ.get(k) for k in
             ["OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"]}}}
    atomic(attempt/"START.json",record)
    for group in pending:
        stamp=time.perf_counter_ns()
        try:
            result=GROUPS[group]()
            record["groups"][group]={"status":"PASS","details":result,
                                     "seconds":(time.perf_counter_ns()-stamp)*1e-9}
        except Exception:
            record["groups"][group]={"status":"FAIL","traceback":traceback.format_exc(),
                                     "seconds":(time.perf_counter_ns()-stamp)*1e-9}
    record["status"]="PASS" if all(r["status"]=="PASS" for r in record["groups"].values()) else "FAIL"
    record["end_utc"]=datetime.now(timezone.utc).isoformat()
    record["seconds"]=(time.perf_counter_ns()-start_ns)*1e-9
    record["maximum_resident_kib"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    atomic(attempt/"RESULT.json",record)
    print(json.dumps({"status":record["status"],"receipt":str(attempt/"RESULT.json"),
                      "groups":{k:v["status"] for k,v in record["groups"].items()},
                      "seconds":record["seconds"]}))
    if record["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
