#!/usr/bin/env python3
"""Independent local-sky 128-point GL check of real Bianchi-I radiation-stress CSV.

The production C++/Rust helper integrates INITIAL mu using composite Simpson;
this independently integrates EVOLVED local mu of an initially isotropic
collisionless massless-radiation distribution. Only the conditional background.
"""
import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("AX08_SOURCE_ROOT",str(HERE.parents[3])))
G_SI=6.67430e-11
C_SI=299792458.0
H0=67.4e3/(3.0856775814913673e22)
OMEGA_R=9.2e-5
COEFF=3.0*H0**2*C_SI**2*OMEGA_R/(8.0*np.pi*G_SI)
MU,W=np.polynomial.legendre.leggauss(128)
W_P2=(W/2)*((3*MU*MU-1)/2)
M2=MU*MU
CASES={
    "ZERO":"flrw/32d11e733155/ZERO_composed_001",
    "SHEAR_MINUS":"paired/32d11e733155/SHEAR_MINUS_composed_001"
}

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def case_run(case, rel):
    p=ROOT/"research/axbi_goal_20261014/runs"/rel
    receipt=json.loads((p/"COMPOSITION_RECEIPT.json").read_text())
    if receipt.get("status")!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
        raise AssertionError("CASE_NOT_COMPOSED")
    for name in ("feedback.csv","history.csv"):
        if digest(p/name)!=receipt["output_sha256"][name]:
            raise AssertionError("FROZEN_INPUT_DRIFT:"+name)
    history=np.loadtxt(p/"history.csv",delimiter=",",skiprows=1,usecols=(3,4,6),ndmin=2)
    feedback=np.loadtxt(p/"feedback.csv",delimiter=",",skiprows=1,usecols=(1,2,4),ndmin=2)
    if history.shape!=(312238,3) or feedback.shape!=(312238,3):
        raise AssertionError("HOLD_ROW_SHAPE")
    t,a,b=history.T
    ft,fa,pressure=feedback.T
    if not np.array_equal(t,ft) or not np.array_equal(a,fa):
        raise AssertionError("SAVED_ROW_CLOCK_MISMATCH")
    rho=COEFF/a**4
    # Numerically stable: integrate the anisotropic correction to isotropy,
    # for which the angular P2 integral is zero.
    predicted=np.empty_like(pressure)
    chunk=4096
    for i in range(0,len(b),chunk):
        bx=b[i:i+chunk,None]
        den=(1.0-M2[None,:])*np.exp(-2*bx)+M2[None,:]*np.exp(4*bx)
        anis=1.0/den**2-1.0
        predicted[i:i+chunk]=rho[i:i+chunk]*np.sum(anis*W_P2[None,:],axis=1)
    scaled=np.abs(pressure-predicted)/rho
    best=int(np.argmax(scaled))
    endpoint=len(b)-1
    p_series=(-8*b/5 + 8*b*b/7 - 16*b*b*b/35)*rho
    return {
        "case":case,"rows":len(b),
        "max_abs_pressure_difference_J_m3":float(np.max(np.abs(pressure-predicted))),
        "max_abs_pressure_difference_over_rho_iso":float(scaled[best]),
        "witness_row":best,
        "endpoint_b":float(b[endpoint]),
        "endpoint_pressure_saved_J_m3":float(pressure[endpoint]),
        "endpoint_pressure_independent_GL128_J_m3":float(predicted[endpoint]),
        "endpoint_pressure_series_cubic_J_m3":float(p_series[endpoint]),
        "endpoint_rho_iso_J_m3":float(rho[endpoint]),
        "endpoint_normalized_deltaP_over_rho_iso":float(pressure[endpoint]/rho[endpoint]),
        "pass_scoped":bool(scaled[best]<1e-8),
        "physics_scope":"no directional source, effective Omega_r initially isotropic free streaming, no shear feedback coupling"
    }

if __name__=="__main__":
    out={case:case_run(case,rel) for case,rel in CASES.items()}
    doc={"schema":"rei.axbi.effective_radiation_stress_crosscheck.v1",
         "status":"PASS_STORED_SIMPSON_VS_INDEPENDENT_LOCAL_GL128" if all(r["pass_scoped"] for r in out.values()) else "FAIL_PRESSURE_REPRODUCTION",
         "formula":"DeltaP/rho_iso = (1/2) int_{-1}^{1} P2(mu)/[(1-mu^2)*exp(-2b)+mu^2*exp(4b)]^2 dmu",
         "series":"-8b/5+8b^2/7-16b^3/35+O(b^4)",
         "source_coordinate":"current physical local mu, NOT saved initial reference mu integration",
         "numerical_tolerance":"max absolute error / rho_iso <1e-8",
         "units":"SI (J m^-3), c,G explicit","scientific_admission":"NOT_ISSUED",
         "results":out}
    (HERE/"quadrupole_minus_crosscheck.json").write_text(json.dumps(doc,indent=2)+"\n")
    for k,v in out.items():
        print(k,"scaled_max_error",v["max_abs_pressure_difference_over_rho_iso"],
              "end_p",v["endpoint_pressure_saved_J_m3"],
              "GL128",v["endpoint_pressure_independent_GL128_J_m3"],
              "PASS",v["pass_scoped"])
    if not all(v["pass_scoped"] for v in out.values()):
        raise SystemExit(3)
