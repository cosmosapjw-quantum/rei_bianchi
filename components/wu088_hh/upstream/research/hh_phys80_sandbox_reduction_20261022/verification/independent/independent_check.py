#!/usr/bin/env python3
"""Independent bounded PHYS80 review. No ODE and no old-suite execution.

The ordinary event operator is an independent oracle for the reduced tangent;
five-point differences use public rates/RHS, not copied derivative formulae.
Every fixture mutation is confined to /tmp/phys80_review.
"""
from __future__ import annotations
import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_name] = "1"
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import traceback
from datetime import datetime, timezone
import numpy as np
import scipy
import scipy.integrate

ROOT = Path("/tmp/hh_phys79_work/WU088_HH/research/hh_phys80_sandbox_reduction_20261022")
OUT = Path("/tmp/phys80_review")
OUT.mkdir(parents=True, exist_ok=True)
RESULT = OUT / "check_result_001.json"
if RESULT.exists():
    raise SystemExit("CREATE_ONLY: this verification batch already has a receipt")
ODE_CALLS = 0
def forbidden_ode(*args, **kwargs):
    global ODE_CALLS
    ODE_CALLS += 1
    raise AssertionError("INDEPENDENT_REVIEW_FORBIDS_ALL_ODE_CALLS")
scipy.integrate.solve_ivp = forbidden_ode
sys.path.insert(0, str(ROOT / "source"))
import reduced
import phys79_bridge as bridge
import run_reduced as runner

FILES = ["source/reduced.py", "source/phys79_bridge.py", "source/run_reduced.py",
         "theory/PHYSICS_TO_CODE_GATE_KO.md", "inputs/REDUCTION_PLAN.json",
         "vendor/PHYS79_PROVENANCE.json"]
def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
HASHES_BEFORE = hashes()
START = datetime.now(timezone.utc).isoformat()
COUNTS = {}
RESULTS = []
ATOMIC, COLL = bridge.atomic, bridge.collisions
IX = ATOMIC.SPECIES_INDEX
PHYSICS = {k: copy.deepcopy(v["binding"]["physics"]) for k, v in bridge.CASES.items()}
MODELS = {}
POINTS = []
PLAN = json.loads((ROOT/"inputs/REDUCTION_PLAN.json").read_text())
MANIFEST = runner.source_manifest()
TASKS = [runner.prepare(s, PLAN, MANIFEST) for s in PLAN["tasks"]]

def bump(name, amount=1):
    COUNTS[name] = COUNTS.get(name, 0) + amount

def check(condition, explanation):
    if not condition:
        raise AssertionError(explanation)

def rejects(function, label, exceptions=(ValueError, RuntimeError, ArithmeticError, TypeError)):
    try:
        function()
    except exceptions as exc:
        bump("expected_guard_rejections")
        return type(exc).__name__ + ":" + str(exc)
    raise AssertionError("EXPECTED_REJECTION:" + label)

def test(name, function):
    try:
        data = function()
        RESULTS.append({"name": name, "status": "PASS", "details": data})
    except Exception as exc:
        RESULTS.append({"name": name, "status": "FAIL", "error": repr(exc),
                        "traceback": traceback.format_exc()})

def normalized(error, scale):
    error, scale = np.asarray(error), np.asarray(scale)
    zero = scale == 0
    check(not np.any(np.abs(error)[zero] > 0), "nonzero error in structurally absent component")
    return float(np.max(np.abs(error[~zero])/scale[~zero])) if np.any(~zero) else 0.

def sync_ic(p, fractions):
    y = np.array(p["initial_Y_per_H"])
    for isotope, fraction in fractions.items():
        n = float(p["isotope_inventory_per_H"][isotope])
        y[IX[isotope+"_I"]] = n*(1-fraction)
        y[IX[isotope+"_II"]] = n*fraction
    p["initial_Y_per_H"] = y.tolist()
    net = COLL.CollisionNetwork(ci_rows=p["ci_rows"], d_cx=True)
    p["initial_u_eV_per_H"] = net.thermal_energy(p["T_initial_K"], y)
    return p

def t01_pinned_sources():
    checked = 0
    for relative, expected in bridge.PROVENANCE["files"].items():
        raw = (ROOT/relative).read_bytes()
        check(len(raw) == expected["bytes"], "pin byte count:"+relative)
        check(hashlib.sha256(raw).hexdigest() == expected["sha256"], "pin SHA:"+relative)
        checked += 1
    for name in ("collisional", "run_controls", "phys78_bridge"):
        want = (ROOT/"vendor/phys79/source"/(name+".py")).resolve()
        check(Path(sys.modules[name].__file__).resolve() == want, "loaded module path:"+name)
    check(PHYSICS["C01_BASE"] == PHYSICS["C01_REFINED"], "parent refinement must preserve actual physics")
    bump("pinned_files_checked", checked)
    return {"pin_count": checked, "actual_import_paths_checked": 3,
            "parent_C01_baseline_refinement_physics_equal": True}

def t02_saved_initial_lifts():
    result = []
    for name in ("C01_BASE", "C02_BASE"):
        model = reduced.ExactReduction(PHYSICS[name])
        MODELS[name] = model
        y, u, t, xe, N = model.state(model.z0)
        rel = normalized(y-model.y0, np.abs(model.y0))
        check(rel <= 5e-15, "initial species relative error")
        check(abs(u/model.u0-1) <= 5e-15, "initial thermal energy error")
        check(abs(t/PHYSICS[name]["T_initial_K"]-1) <= 5e-15, "initial T error")
        check(np.isfinite(np.r_[model.he_lift, model.li_lift]).all(), "nonfinite initial lift weights")
        check(np.allclose(model.encode(y, u), model.z0, rtol=5e-15, atol=0), "initial encode")
        check(np.allclose(ATOMIC.ISOTOPE_SUM@y, ATOMIC.ISOTOPE_SUM@model.y0, rtol=5e-15, atol=0), "initial isotope totals")
        result.append({"parent_task": name, "dimension": len(model.z0),
                       "max_relative_species_error": rel, "relative_u_error": abs(u/model.u0-1),
                       "relative_T_error": abs(t/PHYSICS[name]["T_initial_K"]-1),
                       "finite_initial_lift_weights": True})
        bump("initial_states_checked")
    return result

def t03_unequal_isotope_initial_fractions():
    variations = [
        {"He3": .30, "He4": .02, "Li6": .90, "Li7": .003},
        {"He3": 1., "He4": .10, "Li6": 0., "Li7": .40},
    ]
    result = []
    for i, fractions in enumerate(variations):
        p = sync_ic(copy.deepcopy(PHYSICS["C01_BASE"]), fractions)
        model = reduced.ExactReduction(p)
        MODELS["UNEQUAL_"+str(i)] = model
        y, u, *_ = model.state(model.z0)
        check(np.allclose(y, model.y0, rtol=5e-15, atol=0), "unequal IC lift mismatch")
        check(np.isfinite(np.r_[model.he_lift, model.li_lift]).all(), "unequal nonfinite weights")
        result.append({"fractions": fractions, "max_species_absolute_error": float(np.max(abs(y-model.y0)))})
        bump("initial_states_checked")
    return result

def build_points():
    if POINTS:
        return
    for name, model in MODELS.items():
        if model.only_cx:
            zs = [model.z0, np.array([.1]), np.array([.3]), np.array([.45])]
        else:
            zs = [model.z0,
                  model.z0+np.array([.015, .010, .008, .10]),
                  model.z0+np.array([.040, .040, .020, .30])]
        for i, z in enumerate(zs):
            POINTS.append((name+":"+str(i), model, z))

def t04_full_event_operator_tangent():
    build_points()
    result = []
    for label, model, z in POINTS:
        y, u, t, xe, N = model.state(z)
        independent = COLL.CollisionNetwork(ci_rows=model.ci_rows, d_cx=True, d_cx_closure="detailed_balance")
        ref = independent.rhs(t, model.nH, y, H_per_s=0.)
        got = model.lifted_rhs(0., z)
        reference = np.r_[ref.d_species_per_H_dt, ref.heat_eV_per_H_s]
        # Reaction-constituent magnitudes remain meaningful at CX equilibrium.
        scale = np.r_[np.abs(independent.stoichiometry)@np.abs(ref.event_per_H_s),
                      np.abs(independent.delta_binding_eV)@np.abs(ref.event_per_H_s)]
        err = normalized(got-reference, scale)
        check(err <= 1e-10, "full event-operator tangent mismatch:"+label)
        check(abs(xe-float(ATOMIC.CHARGE@y)) <= 5e-15*max(1., abs(xe)), "electron lift mismatch")
        check(abs(N-float(y.sum()+ATOMIC.CHARGE@y)) <= 5e-15*max(1., abs(N)), "particle lift mismatch")
        result.append({"point": label, "temperature_K": t, "reaction_constituent_normalized_error": err})
        bump("full_operator_points")
    return {"points": result, "maximum_error": max(r["reaction_constituent_normalized_error"] for r in result)}

def t05_state_and_tangent_conservation():
    build_points()
    worst_iso = worst_energy = worst_diso = worst_denergy = 0.
    for label, model, z in POINTS:
        y, u, *_ = model.state(z)
        totals = ATOMIC.ISOTOPE_SUM@model.y0
        iso = normalized(ATOMIC.ISOTOPE_SUM@y-totals, np.abs(totals))
        energy0 = math.fsum([model.u0, *[float(a*b) for a,b in zip(model.eps, model.y0)]])
        energy = math.fsum([u, *[float(a*b) for a,b in zip(model.eps, y)]])
        energyerr = abs(energy-energy0)/abs(energy0)
        tangent = model.lifted_rhs(0., z)
        diso = normalized(ATOMIC.ISOTOPE_SUM@tangent[:-1], ATOMIC.ISOTOPE_SUM@np.abs(tangent[:-1]))
        eres = math.fsum([float(tangent[-1]), *[float(a*b) for a,b in zip(model.eps, tangent[:-1])]])
        escale = abs(tangent[-1])+np.abs(model.eps*tangent[:-1]).sum()
        denergy = abs(eres)/escale if escale else abs(eres)
        worst_iso, worst_energy = max(worst_iso, iso), max(worst_energy, energyerr)
        worst_diso, worst_denergy = max(worst_diso, diso), max(worst_denergy, denergy)
        check(max(iso, energyerr, diso, denergy) <= 2e-13, "finite invariant mismatch:"+label)
        bump("conservation_points")
    return {"isotope_relative_max": worst_iso, "energy_relative_max": worst_energy,
            "isotope_tangent_normalized_max": worst_diso, "energy_tangent_normalized_max": worst_denergy,
            "scope": "finite arithmetic checks; energy construction is not an independent physical certificate"}

def five_point(function, point, index=None):
    point = np.asarray(point, dtype=float)
    if index is None:
        h = float(point)*np.finfo(float).eps**.2
        bump("finite_difference_function_evaluations", 4)
        return (function(point-2*h)-8*function(point-h)+8*function(point+h)-function(point+2*h))/(12*h)
    h = max(abs(float(point[index])), 1e-4)*np.finfo(float).eps**.2
    d = np.zeros_like(point); d[index] = h
    bump("finite_difference_function_evaluations", 4)
    return (function(point-2*d)-8*function(point-d)+8*function(point+d)-function(point+2*d))/(12*h)

def t06_analytic_jacobians():
    build_points()
    report = []
    for label, model, z in POINTS:
        if model.only_cx and label.endswith(":0"):
            continue  # tiny C02 initial fraction would straddle a strict boundary
        jac = model.jacobian(0., z)
        fd = np.column_stack([five_point(lambda zz: model.rhs(0., zz), z, j) for j in range(len(z))])
        error = np.abs(jac-fd)
        component = float(np.max(error/(1+np.abs(jac))))
        row = float(np.max(np.max(error,axis=1)/np.maximum(np.max(np.abs(jac),axis=1),1e-30)))
        check(component <= 2e-6 and row <= 2e-6, "Jacobian finite-difference mismatch:"+label)
        report.append({"point": label, "dimension": len(z), "component_normalized_error": component,
                       "row_relative_error": row})
        bump("jacobian_points")
        bump("jacobian_columns", len(z))
    return {"points": report, "maximum_component_error": max(r["component_normalized_error"] for r in report),
            "maximum_row_error": max(r["row_relative_error"] for r in report),
            "formula": "independent five-point central difference; h=max(abs(z_j),1e-4)*eps^(1/5)"}

def t07_rate_derivatives():
    result = []
    for row in range(6):
        temperatures = [100000., 199000.]
        if row in (0,1,3):
            temperatures += [12000., PHYSICS["C01_BASE"]["T_initial_K"]]
        for t in temperatures:
            value, derivative = reduced.ci_value_derivative(row, t)
            check(value == COLL.ci_rate(row,t), "CI value must exactly retain parent")
            fd = float(five_point(lambda tt: COLL.ci_rate(row,float(tt)), t))
            err = abs(derivative-fd)/max(abs(derivative),abs(fd),1e-300)
            check(err <= 2e-7, "CI rate derivative mismatch")
            result.append({"kind":"CI","row":row,"T_K":t,"relative_error":err})
            bump("rate_derivative_points")
    for t in (3., 43., 300., 25370.66308424773, 199000.):
        kf, kr, df, dr = reduced.cx_value_derivatives(t)
        check((kf,kr) == COLL.d_cx_rates(t,"detailed_balance"), "CX values must exactly retain parent")
        fd = five_point(lambda tt: np.array(COLL.d_cx_rates(float(tt),"detailed_balance")), t)
        err = float(np.max(abs(np.array([df,dr])-fd)/np.maximum(abs(fd),1e-300)))
        check(err <= 2e-7, "CX rate derivative mismatch")
        result.append({"kind":"CX_pair","T_K":t,"relative_error":err})
        bump("rate_derivative_points")
    return {"points":result,"maximum_relative_error":max(r["relative_error"] for r in result)}

def t08_constructor_rejections():
    base = PHYSICS["C01_BASE"]
    cases = []
    for key,value in [("H_per_s",1e-20),("PI",True),("RR",True),
                      ("external_heat_bath",True),("proper_volume_and_density","variable"),
                      ("gas_anisotropic_stress",1.),("d_cx",False),("d_cx","true"),
                      ("PI",0),("RR",0),("external_heat_bath",0),
                      ("d_cx_closure","raw_fit"),("ci_rows",[0,1,2,3]),
                      ("nH_cm3",0.),("nH_cm3",float("inf")),
                      ("theta_per_proper_second",0.),("theta_per_proper_second",1.),
                      ("initial_u_eV_per_H",0.),("initial_u_eV_per_H",float("nan")),
                      ("T_initial_K",float("nan")),("k_ref_cm3_s",-1.)]:
        p=copy.deepcopy(base);p[key]=value;cases.append((key+":"+repr(value),p))
    for species in ("He4_III","Li7_III","T_I","n"):
        p=copy.deepcopy(base);p["initial_Y_per_H"][IX[species]]=1e-12;cases.append(("forbidden:"+species,p))
    for label,mutate in [
        ("negative species",lambda p:p["initial_Y_per_H"].__setitem__(IX["Li6_I"],-1e-14)),
        ("NaN species",lambda p:p["initial_Y_per_H"].__setitem__(IX["H1_I"],float("nan"))),
        ("wrong potential",lambda p:p["ionic_potential_eV"].__setitem__(IX["D_II"],13.6)),
        ("wrong inventory",lambda p:p["isotope_inventory_per_H"].__setitem__("D",2.5e-5)),
        ("wrong length",lambda p:p.__setitem__("initial_Y_per_H",p["initial_Y_per_H"][:-1])),
    ]:
        p=copy.deepcopy(base);mutate(p);cases.append((label,p))
    for isotope in ("H1","D","He3","He4","Li6","Li7"):
        if isotope in ("He3","Li6"):
            continue
        p=copy.deepcopy(base)
        group = [isotope] if isotope in ("H1","D") else (["He3","He4"] if isotope=="He4" else ["Li6","Li7"])
        for iso in group:
            p["initial_Y_per_H"][IX[iso+"_I"]]=p["initial_Y_per_H"][IX[iso+"_II"]]=0.
            p["isotope_inventory_per_H"][iso]=0.
        cases.append(("zero inventory:"+isotope,p))
    logs=[]
    for label,p in cases:
        logs.append({"case":label,"error":rejects(lambda p=p:reduced.ExactReduction(p),label)})
    return logs

def t09_strict_reduced_state_guards():
    model=MODELS["C01_BASE"]
    cases=[("shape",np.zeros(3)),("NaN",np.array([np.nan,*model.z0[1:]]))]
    for label,index,value in [("negative D fraction",1,-1e-24/model.D),
                              ("negative h",2,-1e-20),("negative l",3,-1e-20),
                              ("D above inventory",1,1.000001),
                              ("h above one",2,1.000001),("l above one",3,1.000001)]:
        z=model.z0.copy();z[index]=value;cases.append((label,z))
    z=model.z0.copy();z[0]=z[1]*model.D/model.S-1e-12;cases.append(("negative HII",z))
    z=model.z0.copy();z[0]=1.1;cases.append(("negative HI",z))
    z=model.z0.copy();z[0]+=.4;cases.append(("nonpositive thermal energy",z))
    logs=[]
    for label,z in cases:
        logs.append({"case":label,"error":rejects(lambda z=z:model.state(z),label)})
    p=sync_ic(copy.deepcopy(PHYSICS["C01_BASE"]),{"D":0.,"He3":0.,"He4":0.,"Li6":0.,"Li7":0.})
    neutral_other = reduced.ExactReduction(p)
    z=np.array([-1e-18/neutral_other.S,0.,0.,0.])
    logs.append({"case":"tiny negative Q hidden by anchored subtraction", "error":rejects(lambda:neutral_other.state(z),"negative raw Q")})
    return logs

def t10_source_domains_at_rhs_and_jacobian():
    logs=[]
    for name,t in [("C01_BASE",10000.),("C01_BASE",200001.),("C02_BASE",2.6),("C02_BASE",200001.)]:
        p=copy.deepcopy(PHYSICS[name]);p["T_initial_K"]=t
        p["initial_u_eV_per_H"] = COLL.CollisionNetwork(ci_rows=p["ci_rows"],d_cx=True).thermal_energy(t,p["initial_Y_per_H"])
        logs.append({"case":name+":"+str(t),"error":rejects(lambda p=p:reduced.ExactReduction(p),"out-of-domain IC")})
    model=MODELS["C01_BASE"]
    _,u,_,_,N=model.state(model.z0)
    target=10000.
    deltaQ=(u-reduced.CV*target*N)/(model.IH+reduced.CV*target)
    z=model.z0.copy();z[0]+=deltaQ/model.S
    check(abs(model.state(z)[2]/target-1)<5e-15,"source guard fixture must be physically positive at 10000K")
    for callback in (model.rhs,model.jacobian):
        logs.append({"case":callback.__name__+":physical state outside CI source domain",
                     "error":rejects(lambda callback=callback:callback(0.,z),"active source domain")})
    return logs

def t11_encode_off_manifold():
    logs=[]
    for name in ("C01_BASE","C02_BASE"):
        model=MODELS[name]
        y,u,*_=model.state(model.z0)
        yy=y.copy();yy[IX["H1_I"]]+=1e-5
        logs.append({"case":name+":inventory", "error":rejects(lambda yy=yy:model.encode(yy,u),"off-inventory")})
        logs.append({"case":name+":energy", "error":rejects(lambda:model.encode(y,u*1.01),"off-energy")})
        yy=y.copy();yy[IX["He3_I"]]*=.9;yy[IX["He3_II"]]+=y[IX["He3_I"]]*.1
        logs.append({"case":name+":isotope partition", "error":rejects(lambda yy=yy:model.encode(yy,u),"off-neutral-isotope ratio")})
        yy=y.copy();yy[IX["T_I"]]=1e-30
        logs.append({"case":name+":forbidden tracer", "error":rejects(lambda yy=yy:model.encode(yy,u),"forbidden off-manifold tracer")})
    return logs

def t12_identity_bindings():
    ids=[t["science_id"] for t in TASKS]
    check(len(set(ids))==3,"three new algorithm identities must be distinct")
    check(not set(ids)&{r["science_id"] for r in bridge.CASES.values()},"old scientific identity must never be reused")
    for task in TASKS:
        check(task["binding"]["parent_physics_id"]==task["parent"]["physics_id"],"parent physics identity mismatch")
        check(task["binding"]["physics"]==task["parent"]["binding"]["physics"],"physics changed during reduction")
    alias=copy.deepcopy(PLAN["tasks"][0]);alias["id"]="ALIAS_ONLY"
    check(runner.prepare(alias,PLAN,MANIFEST)["science_id"]==ids[0],"display label must not create another scientific identity")
    changed=copy.deepcopy(PLAN);changed["solver"]["baseline"]["rtol"]*=2
    check(runner.prepare(PLAN["tasks"][0],changed,MANIFEST)["science_id"]!=ids[0],"changed numerical setting must change identity")
    return {"new_science_ids":ids,"parent_physics_preserved":True,"display_alias_identity_preserved":True}

def fixture_dir(name):
    path=OUT/"fixtures"/name
    path.mkdir(parents=True,exist_ok=False)
    return path

def fixture_receipt(output,task,status="COMPLETE",binding=None):
    key=task["science_id"]
    folder=output/"cases";folder.mkdir(parents=True,exist_ok=True)
    npz=folder/(key+".npz")
    with npz.open("xb") as stream:np.savez(stream,finite_test_data=np.array([1.,2.]))
    record={"science_id":key,"binding":task["binding"] if binding is None else binding,
            "status":status,"npz":{"path":str(npz.relative_to(output)),"bytes":npz.stat().st_size,
                                     "sha256":hashlib.sha256(npz.read_bytes()).hexdigest()}}
    raw=json.dumps(record,sort_keys=True,separators=(",",":"),allow_nan=False).encode()+b"\n"
    receipt=folder/(key+".json");receipt.write_bytes(raw)
    receipt.with_suffix(".json.sha256").write_text(hashlib.sha256(raw).hexdigest()+"\n")
    return receipt,npz

def t13_existing_identity_states():
    task=TASKS[0];key=task["science_id"];logs=[]
    empty=fixture_dir("empty");check(runner.existing(empty,task)=="READY","empty state")
    logs.append({"fixture":"empty","status":"READY"})
    for name,relative in [("orphan_npz","cases/"+key+".npz"),
                          ("orphan_checksum","cases/"+key+".json.sha256"),
                          ("claim","claims/"+key+".json")]:
        output=fixture_dir(name);p=output/relative;p.parent.mkdir(parents=True);p.write_bytes(b"fixture only\n")
        status=runner.existing(output,task)
        check(status=="BLOCKED_PREVIOUS_PARTIAL_IDENTITY","partial identity incorrectly READY:"+name)
        logs.append({"fixture":name,"status":status})
    output=fixture_dir("attempt");(output/"attempts"/key).mkdir(parents=True)
    check(runner.existing(output,task)=="BLOCKED_PREVIOUS_PARTIAL_IDENTITY","attempt must block replay")
    logs.append({"fixture":"attempt","status":"BLOCKED_PREVIOUS_PARTIAL_IDENTITY"})
    output=fixture_dir("complete");receipt,npz=fixture_receipt(output,task)
    check(runner.existing(output,task)=="SKIP_COMPLETE_VERIFIED","complete skip")
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()}
    skipped=runner.execute_one(output,task,PLAN,{}, {})
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()}
    check(skipped["status"]=="SKIP_COMPLETE_VERIFIED" and skipped["new_ODE_calls"]==0,"execute_one must skip complete")
    check(before==after,"complete reuse must preserve fixture bytes")
    logs.append({"fixture":"complete","status":skipped["status"],"new_ODE_calls":0,"unchanged_files":len(before)})
    output=fixture_dir("tampered_npz");receipt,npz=fixture_receipt(output,task);npz.write_bytes(npz.read_bytes()+b"tamper")
    logs.append({"fixture":"tampered_npz","error":rejects(lambda:runner.existing(output,task),"tampered NPZ")})
    output=fixture_dir("wrong_binding");fixture_receipt(output,task,binding={"wrong":True})
    logs.append({"fixture":"wrong_binding","error":rejects(lambda:runner.existing(output,task),"wrong binding")})
    output=fixture_dir("failed");fixture_receipt(output,task,status="FAILED")
    check(runner.existing(output,task)=="BLOCKED_PREVIOUS_FAILED_IDENTITY","failed identity must block")
    logs.append({"fixture":"failed","status":"BLOCKED_PREVIOUS_FAILED_IDENTITY"})
    bump("runner_identity_fixtures",len(logs))
    return logs

def t14_claim_race_no_owner_poison():
    task=TASKS[0];output=fixture_dir("claim_race");key=task["science_id"]
    original=runner.source_manifest
    def race_between_check_and_claim():
        claim=output/"claims"/(key+".json");claim.parent.mkdir(parents=True,exist_ok=True)
        claim.write_text('{"fixture":"independent owner claimed after READY check"}\n')
        return task["binding"]["source"]
    runner.source_manifest=race_between_check_and_claim
    try:
        record=runner.execute_one(output,task,PLAN,{"fixture":"no real lease"},{})
    finally:
        runner.source_manifest=original
    check(record["new_ODE_calls"]==0,"claim loser must not invoke ODE")
    check(not (output/"cases"/(key+".json")).exists(),"claim loser poisoned owner's final receipt")
    check(str(record["status"]).startswith("BLOCKED"),"claim loser needs blocked status")
    bump("runner_identity_fixtures")
    return {"status":record["status"],"new_ODE_calls":0,"no_science_receipt_written":True,
            "scope":"deterministic publication race injection; no ODE and no live lease operation"}

def t15_pinned_import_cache_rejection():
    # Fresh interpreter only; the fake module is never imported into this review.
    logs=[]
    for name in ("collisional","phys78_bridge","run_controls"):
        code=("import sys,types\n"
              "sys.path.insert(0,"+repr(str(ROOT/"source"))+")\n"
              "m=types.ModuleType("+repr(name)+");m.__file__='/tmp/unpinned_fixture.py'\n"
              "sys.modules["+repr(name)+"]=m\n"
              "try:\n import phys79_bridge\n"
              "except RuntimeError as e:\n"
              " assert 'PARENT_MODULE_CACHE_PATH_MISMATCH' in str(e), repr(e)\n"
              " print(str(e))\n"
              "else:\n raise AssertionError('un-pinned cached module accepted')\n")
        proc=subprocess.run([sys.executable,"-B","-c",code],capture_output=True,text=True,timeout=20)
        check(proc.returncode==0,"import identity guard failed:"+name+":"+proc.stderr)
        logs.append({"injected_module":name,"result":proc.stdout.strip(),"exit_status":proc.returncode})
    bump("independent_import_guard_processes",3)
    return logs

def t16_full_mesh_validation_primitive():
    model=MODELS["C01_BASE"]
    zs=np.stack([model.z0,model.z0+np.array([.015,.01,.008,.1])])
    full=runner.full_states(model,zs)
    check(full.shape==(2,ATOMIC.N_SPECIES+1),"accepted mesh lift shape")
    bad=zs.copy();bad[1,1]=-1e-20
    a=rejects(lambda:runner.full_states(model,bad),"accepted-mesh negative state")
    _,u,_,_,N=model.state(model.z0);target=10000.
    bad=zs.copy();bad[1]=model.z0
    bad[1,0]+=(u-reduced.CV*target*N)/(model.IH+reduced.CV*target)/model.S
    b=rejects(lambda:runner.full_states(model,bad),"accepted-mesh source domain")
    bump("mesh_validation_points",6)
    return {"valid_points":2,"negative_state_error":a,"out_of_source_domain_error":b,
            "scope":"full_states routine covers supplied points only; no actual solver mesh or continuum certificate"}

for _function in (t01_pinned_sources,t02_saved_initial_lifts,t03_unequal_isotope_initial_fractions,
                  t04_full_event_operator_tangent,t05_state_and_tangent_conservation,t06_analytic_jacobians,
                  t07_rate_derivatives,t08_constructor_rejections,t09_strict_reduced_state_guards,
                  t10_source_domains_at_rhs_and_jacobian,t11_encode_off_manifold,t12_identity_bindings,
                  t13_existing_identity_states,t14_claim_race_no_owner_poison,t15_pinned_import_cache_rejection,
                  t16_full_mesh_validation_primitive):
    test(_function.__name__,_function)

HASHES_AFTER=hashes()
if HASHES_AFTER!=HASHES_BEFORE:
    RESULTS.append({"name":"target_source_unchanged_during_review","status":"FAIL","error":"TARGET_CHANGED"})
check(ODE_CALLS==0,"forbidden ODE counter nonzero")
receipt={"schema":"PHYS80_INDEPENDENT_BOUNDED_REVIEW_V1","started_utc":START,
         "completed_utc":datetime.now(timezone.utc).isoformat(),
         "command":"python -B /tmp/phys80_review/independent_check.py",
         "versions":{"Python":platform.python_version(),"NumPy":np.__version__,"SciPy":scipy.__version__},
         "threads":{k:os.environ.get(k) for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS")},
         "test_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "source_hashes_before":HASHES_BEFORE,"source_hashes_after":HASHES_AFTER,
         "unique_check_groups":len(RESULTS),"passed":sum(r["status"]=="PASS" for r in RESULTS),
         "failed":sum(r["status"]=="FAIL" for r in RESULTS),"internal_counts":COUNTS,
         "actual_ODE_calls":ODE_CALLS,"old_suite_executions":0,"remote_mutations":0,"live_lease_mutations":0,
         "checks":RESULTS,"HH_R10":"OFF","production_admission":"NOT_ISSUED",
         "claim_scope":"finite algebra, selected source guards, external API and create-only identity behavior; no trajectory execution, no continuous positivity/convergence/rate-accuracy certificate"}
with RESULT.open("x") as stream:
    json.dump(receipt,stream,indent=2,sort_keys=True,allow_nan=False);stream.write("\n")
print(json.dumps({k:receipt[k] for k in ("unique_check_groups","passed","failed","internal_counts","actual_ODE_calls","versions")},indent=2))
for record in RESULTS:
    if record["status"]!="PASS":print(record["name"],record.get("error"))
raise SystemExit(1 if receipt["failed"] else 0)
