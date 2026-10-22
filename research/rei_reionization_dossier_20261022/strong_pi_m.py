"""Five bounded matched hot-family IVPs, and four passive nuclear postprocesses.

This adapter reuses the immutable atomic and transport equations. It changes
only the explicitly contracted collisionless component and numerical grid.
"""
from __future__ import annotations

import hashlib
import json
import math
import resource
import signal
import sys
import time
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PILOT = RESEARCH / "rei_isotope_quotient_pilot_20261022" / "pilot"
NETWORK = RESEARCH / "rei_tritium_production_audit_20261022"
UNIT = HERE / "strong_pi_m"
OUT = UNIT / "results"
CONTRACT = HERE / "STRONG_PI_M_CONTRACT.json"
sys.path.insert(0, str(PILOT / "code"))
sys.path.insert(0, str(NETWORK))
from atomic_quotient import AtomicQuotient, CHARGE_NAMES, OFFSETS  # noqa: E402
from compact_transport import (CompactTransport, KAPPA_T, SQRT6,
                               unit_matter_pi, verify_vendor)  # noqa: E402
from run import (Coupled, XEND, amplitudes_to_axes, verify_sources,
                 sha as inherited_sha)  # noqa: E402
import nuclear_network as NN  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MatchedCoupled(Coupled):
    def __init__(self, target_pi, *, ellmax=16, radial_cells=24,
                 angular_cells=12, gauss_order=3, rtol=2e-9,
                 atol=2e-12, max_step=.04, fm=.3, mass=3., deadline=120.):
        # The old amplitudes_to_axes() hardcodes fm=.1 and m/Tref=30; bypass it.
        self.transport = CompactTransport(0., float(target_pi), 0., ellmax=ellmax,
                            radial_cells=radial_cells, angular_cells=angular_cells,
                            gauss_order=gauss_order, mass_fraction=fm,
                            mass_over_Tref=mass, orientation=1)
        self.atomic = AtomicQuotient(self.transport.source)
        self.reference = False
        self.sizechem = 9
        self.ntrans = self.transport.size
        self.y0 = np.r_[self.transport.initial_state(), self.atomic.y0, 0.]
        self.target = (0., float(target_pi), 0.)
        self.rtol, self.atol, self.max_step = rtol, atol, max_step
        self.deadline = deadline
        self.started = time.monotonic()
        self.calls = self.jcalls = 0
        self.radial_cells, self.angular_cells, self.gauss_order = (
            radial_cells, angular_cells, gauss_order)
        self.fm, self.mass = fm, mass


def parity():
    old = Coupled(0., 1.6, 0., ellmax=16, deadline=120.)
    new = MatchedCoupled(old.target[1], fm=.1, mass=30., deadline=120.)
    if not np.allclose(old.y0, new.y0, rtol=0, atol=0):
        raise AssertionError("cold adapter initial state differs")
    with np.load(PILOT/"results"/"quotient_L16_S0_Am1.6_Ar0.npz",
                 allow_pickle=False) as d:
        states = [old.y0, d["state"][85], d["state"][170]]
        xs = [0., float(d["x"][85]), float(d["x"][170])]
    maximum = 0.
    for x, y in zip(xs, states):
        g0 = old.transport.geometry(x, y[:old.ntrans])
        g1 = new.transport.geometry(x, y[:new.ntrans])
        vals0 = np.array(g0[:6],float)
        vals1 = np.array(g1[:6],float)
        geometry = np.max(abs(vals0-vals1)/(1+np.maximum(abs(vals0),abs(vals1))))
        rhs0, rhs1 = old.rhs(x,y), new.rhs(x,y)
        rhs = np.max(abs(rhs0-rhs1)/(1+np.maximum(abs(rhs0),abs(rhs1))))
        maximum = max(maximum,float(geometry),float(rhs))
    if maximum > 1e-11:
        raise AssertionError("cold adapter parity exceeds 1e-11")
    return maximum


def source_check(contract):
    for name, expected in contract["source_identity"].items():
        p = RESEARCH.parent / name
        if sha(p) != expected:
            raise RuntimeError("frozen source bytes differ: " + name)
    verify_vendor()
    verify_sources()


def initial_moments(model):
    t = model.transport
    a,h,s,pm,pg,pn,tower,m = t.geometry(0.,model.y0[:model.ntrans])
    obs = t.observables(0.,model.y0[:model.ntrans])
    return dict(rho0=m.rho,pbar0=m.pbar,P_parallel0=m.pressure_parallel,
                P_perp0=m.pressure_perp,reference_energy_norm=t.moments.reference_energy_norm,
                particle_number0=m.ncell_number,H0=h,
                actual_Pi_m0=obs["Pi_m"],actual_P_m0=obs["P_m"],
                actual_P_r0=obs["P_r"],actual_Sigma_F0=obs["Sigma_F"],
                A_m=t.am, minimum_W=min(1+t.am,1-t.am/2))


def run_one(model, case, contract, adapter_hash):
    if (OUT/(case+".npz")).exists() or (OUT/(case+".json")).exists():
        raise FileExistsError("already produced " + case)
    t0, cpu0 = time.perf_counter(), time.process_time()
    record = dict(case=case, status="RUNNING", target_Pi_m0=model.target[1],
                  mass_fraction=model.fm,mass_over_Tref=model.mass,
                  model=dict(mass_fraction=model.fm,mass_over_Tref=model.mass,
                             A_m=model.transport.am,Sigma_F0=0.,
                             target_Pi_m0=model.target[1],ellmax=model.transport.ellmax),
                  quadrature=dict(radial_cells=model.radial_cells,
                                  angular_cells=model.angular_cells,gauss_order=model.gauss_order),
                  solver_settings=dict(method="Radau",ellmax=model.transport.ellmax,
                                       rtol=model.rtol,atol=model.atol,max_step=model.max_step,
                                       samples=257,per_case_wall_limit_s=model.deadline),
                  adapter_hash=adapter_hash,
                  source_hashes=contract["source_identity"],
                  initial=initial_moments(model))
    try:
        if (abs(record["initial"]["actual_Pi_m0"]-model.target[1]) > 1e-12
                or abs(record["initial"]["actual_P_r0"]) > 1e-14
                or abs(record["initial"]["actual_Sigma_F0"]) > 1e-14
                or record["initial"]["minimum_W"] <= 0):
            raise AssertionError("initial target/fixed-axis/continuous W gate")
        x=np.linspace(0,XEND,257)
        sol=solve_ivp(model.rhs,(0,XEND),model.y0,method="Radau",jac=model.jac,
                      rtol=model.rtol,atol=model.atol,max_step=model.max_step,t_eval=x)
        if not sol.success or sol.y.shape!=(len(model.y0),257):
            raise RuntimeError("new hot-family integration failed: "+sol.message)
        rows=[model.diagnostics(float(xi),sol.y[:,i]) for i,xi in enumerate(x)]
        names=list(rows[0]);diag=np.array([[r[k] for k in names] for r in rows],float)
        f=sol.y[model.ntrans:-1].T
        census=np.array([model.atomic.lift(row) for row in f])
        col={k:i for i,k in enumerate(names)}
        cons={e:float(np.max(abs(np.sum(f[:,sl],axis=1)-1))) for e,sl in OFFSETS.items()}
        init=np.array([rows[0][k] for k in ("signed_Sigma","P_m","P_r")])
        target=np.array(model.target)
        number_drift=float(max(abs(sol.y[3+model.transport.n,:]-1).max(),
                               abs(sol.y[3+3*model.transport.n,:]-1).max()))
        mn=diag[:,col["matter_number_comoving"]]
        massive_drift=float(np.max(abs(mn/mn[0]-1)))
        bounds=dict(endpoint=bool(sol.t[-1]==XEND),
                    finite=bool(np.isfinite(sol.y).all() and np.isfinite(diag).all()),
                    min_fraction=bool(np.min(f)>=-2e-9),
                    isotope_sum=bool(max(cons.values())<=2e-9),
                    initial_axis=bool(np.max(abs(init-target))<=1e-12),
                    fixed_initial_axes=bool(abs(init[0])<=1e-14 and abs(init[2])<=1e-14),
                    number_drift=bool(number_drift<=2e-9),
                    massive_number_drift=bool(massive_drift<=2e-9),
                    canonical_cells=bool(np.min(diag[:,col["min_canonical_cell"]])>=0),
                    angular_257=bool(np.min(diag[:,col["min_angular_257"]])>=-2e-8))
        record.update(gates=bounds, conservation=cons,initial_axes=init.tolist(),
                      initial_axis_error=float(np.max(abs(init-target))),
                      number_drift=number_drift,massive_number_drift=massive_drift,
                      min_fraction=float(np.min(f)),
                      min_angular_257=float(np.min(diag[:,col["min_angular_257"]])),
                      min_canonical_cell=float(np.min(diag[:,col["min_canonical_cell"]])),
                      nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,
                      rhs_calls=model.calls,jac_calls=model.jcalls)
        if not all(bounds.values()):
            raise AssertionError("inherited full-history gate failed")
        path=OUT/(case+".npz")
        massive=np.array([(lambda m:(m.rho,m.pbar))(
            model.transport.geometry(float(xi),sol.y[:model.ntrans,i])[-1])
            for i,xi in enumerate(x)],dtype=float)
        np.savez_compressed(path,x=x,z=21*np.exp(-x)-1,state=sol.y.T,
                            conditional=f,census=census,census_names=np.array(CHARGE_NAMES),
                            diagnostics=diag,diagnostic_names=np.array(names),
                            massive_rho=massive[:,0],massive_pbar=massive[:,1])
        record["npz_sha256"]=sha(path)
        record["status"]="PASS_SCOPED"
    except Exception as exc:
        record["status"]="FAILED"
        record["error"]=repr(exc)
        raise
    finally:
        record["wall_s"]=time.perf_counter()-t0
        record["cpu_s"]=time.process_time()-cpu0
        record["peak_rss_kib"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (OUT/(case+".json")).write_text(json.dumps(record,indent=2,allow_nan=False)+"\n")
    return record


def load_one(case):
    with np.load(OUT/(case+".npz"),allow_pickle=False) as d:
        dn=d["diagnostic_names"].tolist()
        return dict(x=d["x"].copy(),z=d["z"].copy(),f=d["conditional"].copy(),
                    diag=d["diagnostics"].copy(),dn=dn)


def comparisons(cases, contract, initial):
    rows=[load_one(c) for c in cases]
    ref=rows[0]; summary={}
    for case,r in zip(cases[1:4],rows[1:4]):
        delta=r["f"]-ref["f"]
        per=np.max(abs(delta),axis=0)
        idx=np.unravel_index(np.argmax(abs(delta)),delta.shape)
        nb=lambda row:row["diag"][:,row["dn"].index("nB_m3")]
        ne=lambda row:row["diag"][:,row["dn"].index("ne_m3")]
        tau=lambda row:row["diag"][:,row["dn"].index("tau_T")]
        summary[case]=dict(max_abs_delta_f=float(np.max(per)),
                          per_channel_max_abs_delta_f=per.tolist(),
                          peak_channel=int(idx[1]),peak_z=float(r["z"][idx[0]]),
                          peak_signed_delta=float(delta[idx]),
                          endpoint_delta_f=delta[-1].tolist(),
                          max_abs_delta_ne_per_baryon=float(np.max(abs(ne(r)/nb(r)-ne(ref)/nb(ref)))),
                          endpoint_delta_tau=float(tau(r)[-1]-tau(ref)[-1]))
    high,control=rows[3],rows[4]
    f_err=np.max(abs(high["f"]-control["f"]),axis=0)
    def field(row,name):return row["diag"][:,row["dn"].index(name)]
    control_info=dict(max_abs_f=float(np.max(f_err)),per_channel_max_abs_f=f_err.tolist(),
                      max_relative_H=float(np.max(abs(field(high,"H_per_s")/field(control,"H_per_s")-1))),
                      max_relative_elapsed=float(np.max(abs(field(high,"elapsed_s")[1:]/field(control,"elapsed_s")[1:]-1))),
                      max_abs_signed_Sigma=float(np.max(abs(field(high,"signed_Sigma")-field(control,"signed_Sigma")))),
                      max_abs_P_m=float(np.max(abs(field(high,"P_m")-field(control,"P_m")))))
    refscale=max(control_info["max_abs_f"],3.3929270504273745e-9)
    for value in summary.values():
        ratio=value["max_abs_delta_f"]/refscale
        value["amplitude_over_reference_scale"]=ratio
        value["classification"]=("separated_from_observed_control_discrepancy" if ratio>=10
                                  else "unresolved_at_observed_accuracy" if ratio<1
                                  else "numerically_marginal")
    peak=np.unravel_index(np.argmax(abs(high["f"]-ref["f"])),high["f"].shape)
    nominal_effect=float(high["f"][peak]-ref["f"][peak])
    controlled_effect=float(control["f"][peak]-ref["f"][peak])
    control_info["leading_effect_peak"]={"index":list(map(int,peak)),
        "z":float(high["z"][peak[0]]),"nominal_signed":nominal_effect,
        "control_signed":controlled_effect,
        "same_sign":bool(nominal_effect*controlled_effect>0),
        "absolute_peak_difference":abs(nominal_effect-controlled_effect)}
    for key,limit in (("max_abs_f",1e-7),("max_relative_H",1e-7),
                      ("max_relative_elapsed",1e-7),("max_abs_signed_Sigma",1e-7),
                      ("max_abs_P_m",1e-7)):
        if control_info[key]>limit:
            control_info["status"]="HOLD_CONTROL_DISCREPANCY"
    control_info.setdefault("status","PASS_SCOPED_CONTROL")
    control_info["reference_scale_f"]=refscale
    return summary,control_info


def nuclear_four(cases):
    dest=UNIT/"STRONG_PI_M_NUCLEAR_HISTORIES.npz"
    if dest.exists():raise FileExistsError(dest)
    contract=json.loads(NN.CONTRACT.read_text())
    NN._stoichiometry_checks(contract["families"])
    backgrounds=[NN.inventory(OUT/(c+".npz")) for c in cases[:4]]
    if not all(np.array_equal(b["T"],backgrounds[0]["T"]) for b in backgrounds):
        raise AssertionError("new matched family temperature grids differ")
    kf,kr,meta=NN.rate_table(contract,backgrounds[0]["T"])
    logs=[]
    for bg in backgrounds:
        if np.max(abs(bg["Y"]@NN.A-1))>1e-8 or np.any(bg["Y"][:,[0,3]]!=0):
            raise AssertionError("passive network initial inventory")
        logs.append(NN.evaluate_case(bg,contract["families"],kf,kr)["log_fast"])
    arr=np.stack(logs)
    if arr.shape!=(4,257,2) or not np.isneginf(arr[:,0,:]).all() \
            or not np.isfinite(arr[:,1:,:]).all():
        raise AssertionError("four-case nuclear log output")
    np.savez_compressed(dest,case_names=np.array(cases[:4]),log_T_n=arr,
                        elapsed_s=np.stack([b["t"] for b in backgrounds]),
                        x=backgrounds[0]["x"],z=21*np.exp(-backgrounds[0]["x"])-1)
    return dict(path=str(dest.relative_to(HERE)),sha256=sha(dest),
                case_names=cases[:4],log_T_n_shape=[4,257,2],
                endpoint_log10_T_n=(arr[:,-1,:]/math.log(10)).tolist())


def main():
    start_wall,start_cpu=time.perf_counter(),time.process_time()
    # A soft CPU signal leaves a small margin to serialize an interruption.
    def cpu_stop(_sig,_frame):raise TimeoutError("180 CPU-second family budget approached")
    signal.signal(signal.SIGXCPU,cpu_stop)
    resource.setrlimit(resource.RLIMIT_CPU,(175,180))
    if (UNIT/"STRONG_RUN_RECEIPT.json").exists() or \
            (UNIT/"STRONG_PI_M_NUCLEAR_HISTORIES.npz").exists() or \
            (OUT.exists() and any(OUT.glob("*.npz"))):
        raise FileExistsError("strong production output exists; no duplicate attempts")
    UNIT.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    contract=json.loads(CONTRACT.read_text())
    if contract["status"]!="FROZEN_FOR_IMPLEMENTATION":raise ValueError("contract not frozen")
    receipt=dict(status="RUNNING",requested_executor="Sol/high",
                 observed_runtime_model=None,contract_sha256=sha(CONTRACT),
                 adapter_sha256=sha(__file__),source_identity=contract["source_identity"],
                 new_background_ivp_cap=5,additional_cpu_seconds_cap=180,
                 actual_background_attempts=0,old_background_reruns=0,cases=[],
                 compute_location="authorized sandbox process; no external NCP/job service")
    try:
        source_check(contract)
        receipt["cold_adapter_point_parity_max_scaled_error"]=parity()
        adapter_hash=sha(__file__)
        names=[]; initials=[]
        for cfg in contract["cases"]:
            if receipt["actual_background_attempts"]>=5:
                raise RuntimeError("five-IVP cap reached")
            ov=cfg.get("override",{})
            params=dict(ellmax=ov.get("ellmax",16),
                        radial_cells=ov.get("radial_cells",24),
                        angular_cells=ov.get("angular_cells",12),
                        gauss_order=ov.get("gauss_order",3),
                        rtol=ov.get("rtol",2e-9),atol=ov.get("atol",2e-12),
                        max_step=ov.get("max_step",.04),fm=.3,mass=3.,deadline=120.)
            model=MatchedCoupled(cfg["Pi_m0"],**params)
            names.append(cfg["case"]); initials.append(initial_moments(model))
            receipt["actual_background_attempts"]+=1
            result=run_one(model,cfg["case"],contract,adapter_hash)
            receipt["cases"].append(dict(case=cfg["case"],status=result["status"],
                                         cpu_s=result["cpu_s"],wall_s=result["wall_s"],
                                         npz_sha256=result["npz_sha256"]))
            if time.process_time()-start_cpu>160:
                raise TimeoutError("insufficient remaining CPU for bounded family")
        nominal=initials[:4]
        for key in ("rho0","pbar0","particle_number0","H0"):
            vals=np.array([v[key] for v in nominal])
            rel=float(np.max(abs(vals/vals[0]-1)))
            receipt[key+"_nominal_max_relative_difference"]=rel
            if rel>2e-12:raise AssertionError("nominal initial matching "+key)
        pressure_rel=abs(initials[4]["pbar0"]/initials[3]["pbar0"]-1)
        receipt["control_pbar_relative_difference"]=pressure_rel
        if pressure_rel>1e-7:raise AssertionError("control pressure quadrature mismatch")
        comparisons,control=comparisons_fn(names,contract,initials)
        receipt["atomic_response_vs_hot_zero"]=comparisons
        receipt["strong_control"]=control
        receipt["nuclear_nominal_four"]=nuclear_four(names)
        receipt["status"]="PASS_SCOPED_STRONG_FAMILY" if control["status"]=="PASS_SCOPED_CONTROL" else "HOLD_CONTROL_DISCREPANCY"
    except Exception as exc:
        receipt["status"]="FAILED_OR_INCOMPLETE"
        receipt["error"]=repr(exc)
        raise
    finally:
        receipt["wall_s"]=time.perf_counter()-start_wall
        receipt["cpu_s"]=time.process_time()-start_cpu
        receipt["peak_rss_kib"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (UNIT/"STRONG_RUN_RECEIPT.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":receipt["status"],"attempts":receipt["actual_background_attempts"],
                      "cpu_s":receipt["cpu_s"],"wall_s":receipt["wall_s"]}))


comparisons_fn=comparisons
if __name__=="__main__":main()
