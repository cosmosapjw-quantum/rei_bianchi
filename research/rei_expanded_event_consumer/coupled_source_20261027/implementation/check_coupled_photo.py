"""One bounded native-snapshot check. Run only after root scientific GO."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
UNIT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/rei_expanded_event_consumer/blocker_closure_20261026"
CALLBACK = BASE / "implementation/run01/CALLBACK.json"
NATIVE = BASE / "implementation/pw19_rec_callback.py"
MAP = UNIT / "theory/GATE_INPUT_MAP.json"
sys.path.insert(0, str(BASE / "implementation"))
from pw19_rec_callback import PW19HeIINetwork, ROUTE, ISOTOPE_POLICY, EVENT_OWNER
from coupled_photo_source import augmented_photo_source, reference_state, EV_J

ALG = 2e-14
FD = 2e-8
HSTEP = .01
checks = []


def check(name, residual, limit=ALG):
    if not math.isfinite(residual) or residual > limit:
        raise AssertionError(f"{name}: residual={residual!r}, limit={limit!r}")
    checks.append({"name": name, "residual": float(residual), "limit": limit})


def relative(actual, expected, scale):
    assert scale > 0
    return abs(actual-expected)/scale


def vector_relative(actual, expected, scale):
    assert scale > 0
    return float(np.max(np.abs(actual-expected)))/scale


def mixed_check(name, actual, expected, count_scale, energy_scale, limit=ALG):
    """Keep tiny energy residuals visible beside the count-rate components."""
    actual, expected = np.asarray(actual), np.asarray(expected)
    check(name+"_counts", vector_relative(actual[:22], expected[:22], count_scale), limit)
    check(name+"_energy", vector_relative(actual[22:24], expected[22:24], energy_scale), limit)
    if actual[24] != 0 or expected[24] != 0:
        raise AssertionError(f"{name}: nonzero pre-assimilation thermal row")
    checks.append({"name":name+"_thermal_exact_zero", "residual":0.0,"limit":0.0})


def reject(name, operation):
    try:
        operation()
    except ValueError:
        checks.append({"name": name, "rejected": True})
    else:
        raise AssertionError(f"{name}: invalid domain accepted")


def main():
    mapping = json.loads(MAP.read_text())
    for item in mapping["inputs"]:
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"immutable input mismatch: {item['path']}")
    saved = json.loads(CALLBACK.read_text())
    snap = saved["snapshot"]
    assert saved["source"]["route"] == ROUTE
    assert saved["source"]["isotope_policy"] == ISOTOPE_POLICY
    assert saved["source"]["event_owner"] == EVENT_OWNER
    net = PW19HeIINetwork(source_z=2.479, source_route=ROUTE,
                          isotope_policy=ISOTOPE_POLICY, photo_owners=(EVENT_OWNER,))
    Y = np.asarray(snap["Y"])
    T, nb, H = snap["temperature_K"], snap["nb_m3"], snap["geometry"]["H_s_inverse"]
    beta, r = snap["beta_baryons_per_Href"], snap["reference_density_m3"]
    x = np.asarray(snap["x_per_Href"])
    mapped = reference_state(net, x)
    check("reference_state", vector_relative(mapped["Y"], Y, float(np.max(Y))))
    check("reference_beta", relative(mapped["beta"], beta, beta))
    check("physical_density", relative(r*beta, nb, nb))
    v = np.zeros(21)
    for lower, upper in ((8,9),(11,12)):
        v[lower] = -.1*Y[lower]
        v[upper] = .1*Y[lower]
    # h=.01 and dnb/nb=.01 leave ~7e-9 cubic product error in density FD.
    # dH/H=.001 keeps eta quotient truncation well under the fixed 2e-8.
    dlambda, dnb, dH, dbeta = .07, .01*nb, .001*H, .03*beta
    got = augmented_photo_source(net, Y, T, nb, 1., H_s_inverse=H, v=v,
                                  dlambda=dlambda, dnb=dnb, dH=dH,
                                  beta_baryons_per_reference=beta, dbeta=dbeta)
    source, tangent = got["source"], got["jvp"]
    event = float(source[21]); power = float(source[22]); absorbed = -float(source[23])
    assert event > 0 and power > 0 and absorbed > 0
    # Two explicit event columns; no production native matrix or ledger is reused.
    p = np.zeros(21)
    dp = np.zeros(21)
    for lo, hi in ((8,9),(11,12)):
        g = math.fsum(row["Gamma_s"] for row in net.admitted_moments["partition_moments"])
        p[lo], p[hi] = -g*Y[lo], g*Y[lo]
        dp[lo], dp[hi] = -g*(v[lo]+dlambda*Y[lo]), g*(v[lo]+dlambda*Y[lo])
    check("native_component_vs_oracle", vector_relative(source[:21], p, event))
    check("native_jvp_vs_event_oracle", vector_relative(tangent[:21], dp, event))
    check("saved_native_component", vector_relative(source[:21], saved["native_on"]["photo_rhs"], event))
    check("saved_on_off", vector_relative(saved["source_on_off_dY_dt"], p, event), FD)
    check("native_photo_action", vector_relative(source[:21], got["native_photo_rhs"], event))
    check("charge_electron_count", relative(float(net.q@p), event, event))
    check("charge_tangent", relative(float(net.q@dp), tangent[21], event))
    for name, indices in net.isotope_groups.items():
        check(f"{name}_nuclei", abs(math.fsum(p[list(indices)]))/event)
        check(f"{name}_nuclei_jvp", abs(math.fsum(dp[list(indices)]))/event)
    check("baryon_source", abs(float(net.A@p))/event)
    check("baryon_jvp", abs(float(net.A@dp))/event)
    assert got["dthermal_count_source"] == 0 and got["dthermal_count_jvp"] == 0
    assert source[24] == 0 and tangent[24] == 0
    assert got["bad_allthermal_logT_s"] < 0
    check("adverse_allthermal", relative(got["bad_allthermal_logT_s"],
          -event/float(np.dot(1+net.q,Y)),event/float(np.dot(1+net.q,Y))))
    for row, source_row in zip(got["band_ledger"], net.admitted_moments["partition_moments"]):
        scale = row["absorbed_J_per_baryon_s"]
        binding = 54.42*EV_J*row["events_per_baryon_s"]
        check("band_energy", abs(math.fsum((binding,row["primary_J_per_baryon_s"],-scale)))/scale)
        tangent_scale = abs(row["tangent_absorbed_J_per_baryon_s"])
        check("band_energy_jvp", abs(math.fsum((54.42*EV_J*row["tangent_events_per_baryon_s"],
              row["tangent_primary_J_per_baryon_s"],-row["tangent_absorbed_J_per_baryon_s"])))/tangent_scale)
        check("band_gamma", relative(row["events_per_baryon_s"],
              (Y[8]+Y[11])*source_row["Gamma_s"], row["events_per_baryon_s"]))
    for index, key in ((21,"events_per_baryon_s"),(22,"primary_J_per_baryon_s"),
                       (23,"absorbed_J_per_baryon_s")):
        sign = -1 if index == 23 else 1
        scale = event if index == 21 else absorbed
        check(f"source_band_total_{index}",relative(source[index],
              sign*math.fsum(row[key] for row in got["band_ledger"]),scale))
        tkey = "tangent_"+key
        check(f"jvp_band_total_{index}",relative(tangent[index],
              sign*math.fsum(row[tkey] for row in got["band_ledger"]),scale))
    # Independent two-event oracle in reference normalization, with nonzero dbeta.
    parts = net.admitted_moments["partition_moments"]
    S = math.fsum((float(Y[8]),float(Y[11])))
    dS = math.fsum((float(v[8]),float(v[11])))+dlambda*S
    K = math.fsum(part["K_eV_s"] for part in parts)*EV_J
    A = math.fsum(part["A_eV_s"] for part in parts)*EV_J
    oracle = np.concatenate((p,[float(net.q@p),K*S,-A*S,0.]))
    oracle_jvp = np.concatenate((dp,[float(net.q@dp),K*dS,-A*dS,0.]))
    mixed_check("augmented_source_oracle",source,oracle,event,absorbed)
    mixed_check("augmented_jvp_oracle",tangent,oracle_jvp,event,absorbed)
    mixed_check("reference_jvp_oracle",got["reference_jvp"],
                dbeta*oracle+beta*oracle_jvp,beta*event,beta*absorbed)
    check("binding_source", relative(got["binding_J_per_baryon_s"],54.42*EV_J*event,absorbed))
    check("energy_total",abs(got["energy_residual_J_per_baryon_s"])/absorbed)
    check("energy_jvp",abs(got["energy_jvp_residual"])/absorbed)
    mixed_check("physical_source",got["physical_density_source"],nb*source,nb*event,nb*absorbed)
    mixed_check("physical_jvp",got["physical_density_jvp"],dnb*source+nb*tangent,nb*event,nb*absorbed)
    mixed_check("reference_source",got["reference_source"],beta*source,beta*event,beta*absorbed)
    mixed_check("reference_physical",r*got["reference_source"],got["physical_density_source"],nb*event,nb*absorbed)
    mixed_check("clock_source",got["eta_source"],source/H,event/H,absorbed/H)
    mixed_check("clock_jvp",got["eta_jvp"],tangent/H-source*dH/H**2,event/H,absorbed/H)
    lo,hi=got["pressure_source_interval_W_m3"]
    check("pressure_lower",relative(lo,nb*power/3,nb*power))
    check("pressure_upper",relative(hi,2*nb*power/3,nb*power))
    assert got["isotropic_pressure_STF_source"] == 0
    # One changed aggregate direction, positive trials; no old native suite.
    h=HSTEP
    plus=augmented_photo_source(net,Y+h*v,T,nb+h*dnb,1+h*dlambda,
                               H_s_inverse=H+h*dH)
    minus=augmented_photo_source(net,Y-h*v,T,nb-h*dnb,1-h*dlambda,
                                H_s_inverse=H-h*dH)
    assert all((Y+h*v)[i]>0 and (Y-h*v)[i]>0 for i in (8,11))
    assert min(nb-h*dnb,H-h*dH,1-h*dlambda)>0
    mixed_check("aggregate_source_FD",(plus["source"]-minus["source"])/(2*h),
                tangent,event,absorbed,FD)
    mixed_check("density_FD",(plus["physical_density_source"]-minus["physical_density_source"])/(2*h),
                got["physical_density_jvp"],nb*event,nb*absorbed,FD)
    mixed_check("clock_FD",(plus["eta_source"]-minus["eta_source"])/(2*h),
                got["eta_jvp"],event/H,absorbed/H,FD)
    zero=augmented_photo_source(net,Y,T,nb,0,H_s_inverse=H,dlambda=1)
    assert np.count_nonzero(zero["source"])==0 and zero["jvp"][21]>0
    boundary=Y.copy()
    for lo, neutral in ((8,7),(11,10)):
        boundary[neutral]+=boundary[lo]
        boundary[lo]=0
    boundary_result=augmented_photo_source(net,boundary,T,nb,1)
    assert np.count_nonzero(boundary_result["source"])==0
    reject("lambda_negative",lambda: augmented_photo_source(net,Y,T,nb,-1))
    reject("density_zero",lambda: augmented_photo_source(net,Y,T,0,1))
    reject("temperature_zero",lambda: augmented_photo_source(net,Y,0,nb,1))
    reject("H_zero",lambda: augmented_photo_source(net,Y,T,nb,1,H_s_inverse=0))
    reject("zeta_negative",lambda: augmented_photo_source(net,Y,T,nb,1,zeta_per_baryon=-1e-4))
    reject("zeta_exceeds_electrons",lambda: augmented_photo_source(net,Y,T,nb,1,zeta_per_baryon=float(net.q@Y)+1e-4))
    reject("full_thermal_activation",lambda: augmented_photo_source(net,Y,T,nb,1,full_rr_dr_thermal=True))
    reject("nonfinite",lambda: augmented_photo_source(net,Y,T,nb,float("nan")))
    old=net.photo_owners
    try:
        net.photo_owners=(EVENT_OWNER,EVENT_OWNER)
        reject("duplicate_owner",lambda: augmented_photo_source(net,Y,T,nb,1))
    finally:
        net.photo_owners=old
    return {"status":"PASS_SCOPED_IF_EXECUTED", "checks":checks,
            "snapshot":{"T_K":T,"nb_m3":nb,"H_s_inverse":H,"beta":beta,"Y":Y.tolist()},
            "source":source.tolist(),"jvp":tangent.tolist(),
            "physical_density_source":got["physical_density_source"].tolist(),
            "eta_source":got["eta_source"].tolist(),
            "energy":{"binding_J_per_baryon_s":got["binding_J_per_baryon_s"],
                      "primary_J_per_baryon_s":power,"external_J_per_baryon_s":-absorbed},
            "thermal":{"count":got["thermal_count"],"electrons":got["thermal_electrons"],
                       "correct_logT_source_s":source[24],
                       "bad_allthermal_logT_s":got["bad_allthermal_logT_s"]},
            "pressure_interval_W_m3":got["pressure_source_interval_W_m3"],
            "uncertainties":got["uncertainties"]}


if __name__=="__main__":
    try:
        print(json.dumps(main(),indent=2,allow_nan=False))
    except Exception as exc:
        print(json.dumps({"status":"FAIL", "checks_completed":checks,
                          "exception_type":type(exc).__name__,"exception":str(exc)},
                         indent=2,allow_nan=False),flush=True)
        raise
