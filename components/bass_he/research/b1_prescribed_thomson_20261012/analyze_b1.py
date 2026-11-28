"""Read completed B1 artifacts; do not rerun transport or producer histories."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent
OUT = ROOT/"analysis"
OUT.mkdir(exist_ok=True)


def read(group, case):
    candidates = list((ROOT/"runs").glob(f"{group}_{case}_t*/result.npz"))
    if len(candidates) != 1:
        raise ValueError(f"Ambiguous run {group}/{case}")
    return dict(np.load(candidates[0], allow_pickle=False))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def main():
    base = {c:read("base", c) for c in ("F","M","B","B0","B_F","M_F")}
    b, bf, m, mf = (base[c] for c in ("B","B_F","M","M_F"))
    y = b["y"]
    guard = np.flatnonzero((y>=.1*(1-1e-14)) & (y<=10*(1+1e-14)))
    points = b["report_indices"]
    hq = (b["q2"]-m["q2"])-(bf["q2"]-mf["q2"])
    hp = (b["pL_equator"]-m["pL_equator"])-(bf["pL_equator"]-mf["pL_equator"])
    components_q, components_p, components_primary = {}, {}, {}
    for group in ("time","angle","energy"):
        bb, ff = read(group,"B"), read(group,"B_F")
        idx = np.array([np.argmin(abs(bb["y"]-v)) for v in y])
        if not np.allclose(bb["y"][idx],y,rtol=1e-14,atol=0) or not np.array_equal(bb["u"],b["u"]):
            raise ValueError("Refinement output chart mismatch")
        components_q[group] = bb["q2"][:,idx]-ff["q2"][:,idx]-hq
        components_p[group] = bb["pL_equator"][:,idx]-ff["pL_equator"][:,idx]-hp
        components_primary[group] = bb["q2"][:,idx]-b["q2"]
    variation_q = sum(abs(a) for a in components_q.values())
    variation_p = sum(abs(a) for a in components_p.values())
    null_q = max(float(np.max(abs(base[c]["q2"][:,guard]))) for c in ("F","M","M_F"))
    null_p = max(float(np.max(abs(base[c]["pL_equator"][:,guard]))) for c in ("F","M","M_F"))
    # Empirical comparison scales, not confidence intervals or proved bounds.
    scale_q = variation_q + 4*null_q
    scale_p = variation_p + 4*null_p
    q_resolved = (np.abs(hq)>0) & (scale_q<=.1*np.abs(hq))
    p_resolved = (np.abs(hp)>0) & (scale_p<=.1*np.abs(hp))
    q_resolved[0,:] = False
    p_resolved[0,:] = False
    fields = ["z_mean","u","y","E_over_kBT_i","q2_B_minus_M","q2_B_minus_B0",
              "history_delta_q2","history_delta_pL_equator","q2_refinement_change_sum",
              "pL_refinement_change_sum","q2_comparison_scale_with_null","pL_comparison_scale_with_null",
              "q2_status","pL_status"]
    rows=[]
    for t in range(len(b["u"])):
        for j in guard:
            rows.append(dict(z_mean=float(b["z_mean"][t]),u=float(b["u"][t]),y=float(y[j]),
                E_over_kBT_i=float(y[j]*np.exp(-b["u"][t])),
                q2_B_minus_M=float(b["q2"][t,j]-m["q2"][t,j]),
                q2_B_minus_B0=float(b["q2"][t,j]-base["B0"]["q2"][t,j]),
                history_delta_q2=float(hq[t,j]),history_delta_pL_equator=float(hp[t,j]),
                q2_refinement_change_sum=float(variation_q[t,j]),pL_refinement_change_sum=float(variation_p[t,j]),
                q2_comparison_scale_with_null=float(scale_q[t,j]),pL_comparison_scale_with_null=float(scale_p[t,j]),
                q2_status="INITIAL_NULL" if t==0 else ("RESOLVED_SCOPED" if q_resolved[t,j] else "UNRESOLVED"),
                pL_status="INITIAL_NULL" if t==0 else ("RESOLVED_SCOPED" if p_resolved[t,j] else "UNRESOLVED")))
    for filename, chosen in [("B1_HISTORY_RESPONSE.csv",rows),
                             ("B1_REPORT_POINTS.csv",[r for r in rows if any(abs(r["y"]-v)<1e-13 for v in y[points])])]:
        with (OUT/filename).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(chosen)
    final=[]
    for j in guard:
        row=dict(y=float(y[j]),E_over_kBT_i=float(y[j]*np.exp(-b["u"][-1])))
        for c,a in base.items():
            for k in ("q2","Ibar_y3","pL_equator"):
                row[f"{c}_{k}"]=float(a[k][-1,j])
        row.update(history_delta_q2=float(hq[-1,j]),history_delta_pL_equator=float(hp[-1,j]),
                   observed_q2_variation=float(variation_q[-1,j]),observed_pL_variation=float(variation_p[-1,j]))
        final.append(row)
    with (OUT/"B1_FINAL_COMPARISON.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(final[0]));w.writeheader();w.writerows(final)
    rec_paths=sorted((ROOT/"runs").glob("*/RECEIPT.json"))
    receipts=[json.loads(p.read_text()) for p in rec_paths]
    campaign=json.loads((ROOT/"execution_logs/RUN001/CAMPAIGN.json").read_text())
    projection=json.loads((ROOT/"source_notes/HISTORY_PROJECTION_VALIDATION.json").read_text())
    oracle=json.loads((ROOT/"review/B1_ACTUAL_ORACLE_COMPARISON.json").read_text())
    summary=dict(
        status="OWNER_PROPOSED_PROMOTE_SCOPED_PYTHON_PENDING_INDEPENDENT_DECISION",
        original_native_gate="HOLD_RUNTIME_ENVIRONMENT",
        physical_scope="Frozen 16384-cell reduced histories, prescribed isotropic Planck IC, no subsequent emission, test-field cold elastic Thomson, LRS Bianchi I initial r=.1, mean-volume z20→4",
        candidate=dict(time_steps=128,mu_GL=24,azimuth=8,energy_base=257,energy_actual=len(y),
                       saved_times=len(b["u"]),guarded_energies=len(guard),guarded_y=[.1,10.0]),
        energy_definition="y=(a/a_i)E/(k_B*T_i); E/(k_B*T_i)=y*exp(-u); same physical E across all angles at fixed time; T_i is a benchmark scale, not gas T",
        refinements={"time":[128,256],"mu":[24,48],"energy_base":[257,513]},
        acceptance=dict(target_fraction=.1,metric="sum of absolute paired refinement changes plus empirical four-null floor; NOT a rigorous bound or statistical uncertainty",
            max_q2_fraction_all_noninitial_guard=float(np.max(scale_q[1:,guard]/abs(hq[1:,guard]))),
            max_pL_fraction_all_noninitial_guard=float(np.max(scale_p[1:,guard]/abs(hp[1:,guard]))),
            max_q2_fraction_final_guard=float(np.max(scale_q[-1,guard]/abs(hq[-1,guard]))),
            max_pL_fraction_final_guard=float(np.max(scale_p[-1,guard]/abs(hp[-1,guard]))),
            q2_resolved_noninitial_count=int(q_resolved[1:,guard].sum()),
            pL_resolved_noninitial_count=int(p_resolved[1:,guard].sum()),
            noninitial_guard_count=int((len(b["u"])-1)*len(guard)),initial="ABSOLUTE_NULL"),
        numerical_observations=dict(
            null_q2_max=null_q,null_pL_equator_max=null_p,
            B0_exact_q2_max_abs=oracle["B0"]["q2_max_abs_error"],
            B0_exact_Ibar_max_relative=oracle["B0"]["Ibar_y3_max_relative_error"],
            B0_pL_null_max=oracle["B0"]["max_pL_all_snapshots_guard"],
            independent_collision_max_relative=oracle["one_actual_B_collision_stage"]["max_relative_guard"],
            max_collision_conservation=max(r["diagnostics"]["max_collision_number_relative"] for r in receipts),
            max_U_over_I=max(r["diagnostics"]["max_screen_U_over_I"] for r in receipts),
            max_V_over_I=max(r["diagnostics"]["max_screen_V_over_I"] for r in receipts),
            min_positive_occupation=min(r["diagnostics"]["min_occupation"] for r in receipts)),
        final_report_points=[{**row, "q2_components":{g:float(a[-1,j]) for g,a in components_q.items()},
                              "pL_components":{g:float(a[-1,j]) for g,a in components_p.items()}}
                             for j in points for row in final if abs(row["y"]-y[j])<1e-13],
        compute=dict(full_transport_runs=len(receipts),pilot_runs=1,campaign_runs=len(campaign["jobs"]),
                     campaign_wall_seconds=campaign["wall_seconds"],concurrent_independent_jobs=3,
                     sum_transport_cpu_seconds=sum(r["cpu_seconds"] for r in receipts),
                     max_per_process_rss_kib=max(r["peak_rss_kib"] for r in receipts),
                     transport_collision_stages=sum(r["collision_stages"] for r in receipts),
                     transport_positive_depth_stages=sum(r["positive_depth_stages"] for r in receipts),
                     transport_upstream_energy_slice_calls=sum(r["upstream_energy_slice_calls"] for r in receipts),
                     targeted_smoke_stages=1,targeted_smoke_slice_calls=2,
                     targeted_oracle_stages=1,targeted_oracle_slice_calls=263,
                     reionization_ODE_runs=0,native_rust_runs=0,NCP_runs=0),
        runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
                     OpenBLAS_threads=1,OMP_threads=1,MKL_threads=1),
        evidence_files={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                        for p in [ROOT/"b1_transport.py",ROOT/"native/python_thomson.py",ROOT/"native/upstream_polarization.py",
                                  ROOT/"inputs/B1_FROZEN_PROJECTED_INPUTS.npz",*rec_paths]},
        claim_limits=["Actual Rust/native integration and parity NOT_RUN",
                      "No coupled ionizing radiation, gas feedback, heating evolution or RCT photon spectrum",
                      "Frozen producer discretization; no new continuum history accuracy admission",
                      "Observed refinement differences are not certified enclosures or statistical confidence intervals",
                      "No observer tail, observed-redshift mapping, total CMB tau or angular C_l prediction",
                      "Two prescribed histories do not quantify full source/closure/astrophysical uncertainty"])
    write_json(OUT/"B1_NUMERICAL_ASSESSMENT.json",summary)
    write_json(OUT/"B1_RUN_INDEX.json",dict(campaign=campaign,receipts=[str(p.relative_to(ROOT)) for p in rec_paths]))
    np.savez_compressed(OUT/"B1_COMMON_COMPARISONS.npz",y=y,u=b["u"],z_mean=b["z_mean"],guard_indices=guard,
                        history_delta_q2=hq,history_delta_pL_equator=hp,variation_q2=variation_q,
                        variation_pL=variation_p,comparison_scale_q2=scale_q,comparison_scale_pL=scale_p)
    print(json.dumps({k:summary[k] for k in ("status","candidate","acceptance","compute")},indent=2))


if __name__=="__main__":
    main()
