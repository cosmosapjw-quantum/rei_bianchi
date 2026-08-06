#!/usr/bin/env python3
"""Replay the canonical B2C2A-R1 BDF history and lock dense forcing nodes.

This is a research extraction, not a production chemistry implementation.
It reuses the exact canonical source, tolerances, and interval data and then
compresses each dense OdeSolution with a globally predeclared stable
Chebyshev-Lobatto/Clenshaw-Curtis schedule.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

# Limit thread oversubscription before importing numerical libraries.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("XLA_FLAGS", "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1")

import jax.numpy as jnp
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

GROUPS = ("G1", "G2a", "G2b", "G3")
CANDIDATE_N = (9, 17, 33, 65)
DENSE_GATE = 2.0e-4
NESTED_GATE = 2.0e-4


def load_module(path: Path):
    source_dir = path.parent
    sys.path.insert(0, str(source_dir))
    spec = importlib.util.spec_from_file_location("r1b_r1_gamma_replay", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clenshaw_curtis_nodes_weights(n_points: int) -> tuple[np.ndarray, np.ndarray]:
    """Stable Clenshaw-Curtis nodes/weights on [0,1]."""
    if n_points < 2:
        raise ValueError("n_points must be >= 2")
    n = n_points - 1
    theta = np.pi * np.arange(n_points, dtype=float) / n
    x = np.cos(theta)
    w = np.zeros(n_points, dtype=float)
    if n == 1:
        w[:] = 1.0
    else:
        interior = np.arange(1, n)
        v = np.ones(n - 1, dtype=float)
        if n % 2 == 0:
            w[0] = w[-1] = 1.0 / (n * n - 1.0)
            for k in range(1, n // 2):
                v -= 2.0 * np.cos(2.0 * k * theta[interior]) / (4.0 * k * k - 1.0)
            v -= np.cos(n * theta[interior]) / (n * n - 1.0)
        else:
            w[0] = w[-1] = 1.0 / (n * n)
            for k in range(1, (n - 1) // 2 + 1):
                v -= 2.0 * np.cos(2.0 * k * theta[interior]) / (4.0 * k * k - 1.0)
        w[interior] = 2.0 * v / n
    # Map x in [1,-1] to xi in [0,1]. The ordering becomes ascending.
    xi = (1.0 - x) / 2.0
    return xi, w / 2.0


def relative(a: float, b: float, scale: float | None = None) -> float:
    if scale is None:
        scale = max(abs(a), abs(b), 1.0e-300)
    return abs(a - b) / max(scale, 1.0e-300)


def compare_frames(actual: pd.DataFrame, expected: pd.DataFrame, key: str) -> tuple[pd.DataFrame, float]:
    common = [c for c in actual.columns if c in expected.columns and c != key]
    left = actual.sort_values(key).reset_index(drop=True)
    right = expected.sort_values(key).reset_index(drop=True)
    if len(left) != len(right):
        raise RuntimeError(f"row count mismatch for {key}: {len(left)} != {len(right)}")
    rows=[]; maximum=0.0
    for i in range(len(left)):
        if not np.isclose(float(left.loc[i,key]), float(right.loc[i,key]), rtol=0, atol=1e-12):
            raise RuntimeError(f"key mismatch {left.loc[i,key]} {right.loc[i,key]}")
        for c in common:
            av=left.loc[i,c]; ev=right.loc[i,c]
            if isinstance(av,(str,bool,np.bool_)) or isinstance(ev,(str,bool,np.bool_)):
                continue
            try:
                af=float(av); ef=float(ev)
            except Exception:
                continue
            if not (math.isfinite(af) and math.isfinite(ef)):
                continue
            r=relative(af,ef)
            maximum=max(maximum,r)
            rows.append({key:left.loc[i,key],"column":c,"actual":af,"expected":ef,"relative_residual":r})
    return pd.DataFrame(rows),maximum


def sample_quantities(mod: Any, interval: Any, fraction: float) -> dict[str,float]:
    t = float(fraction) * float(interval.duration_s)
    zz = np.asarray(interval.solution.sol(t), dtype=float)
    state_j = mod.state_from_z7(jnp.asarray(zz), interval.p)
    state = mod.state_numpy(zz, interval.p)
    kappa = np.asarray(mod.opacity_cMpc_inv(state_j, interval.p), dtype=float)
    vchi = mod.C_LIGHT * (1.0 + interval.z_mid) / mod.MPC_CM
    absorption = vchi * state["N"] * kappa
    red_out = np.asarray(interval.p["redshift_coeff"], dtype=float) * float(interval.p["Hubble"])
    therm = {k: float(v) for k,v in mod.thermal_components(state_j, interval.p).items()}
    result: dict[str,float] = {
        "fraction":float(fraction),
        "time_s":t,
        "z_start":interval.z_start,
        "z_mid":interval.z_mid,
        "z_end":interval.z_end,
        "N1":float(state["N"][0]),"N2":float(state["N"][1]),"N3":float(state["N"][2]),"N4_exact":float(state["N"][3]),
        "xHII":float(state["xHII"]),"xHeI":float(state["xHeI"]),"xHeII":float(state["xHeII"]),"xHeIII":float(state["xHeIII"]),
        "u_erg_cm3":float(state["u"]),"T_K":float(state["T"]),
        "Gamma_HI_s-1":float(state["GammaHI"]),"Gamma_HeI_s-1":float(state["GammaHeI"]),"Gamma_HeII_exact_s-1":float(state["GammaHeII"]),
        "redshift_threshold_loss_rate_s-1_cMpc-3":float(red_out[0] * state["N"][0]),
        "emission_rate_s-1_cMpc-3":float(interval.emission_rate),
        "front_absorption_rate_s-1_cMpc-3":float(np.sum(interval.front_sink[:3])),
    }
    for gi,g in enumerate(GROUPS):
        result[f"N_{g}_cMpc-3"] = float(state["N"][gi])
        result[f"kappa_{g}_cMpc-1"] = float(kappa[gi])
        result[f"absorption_{g}_s-1_cMpc-3"] = float(absorption[gi])
    for k,v in therm.items():
        result[f"thermal_{k}_erg_cm-3_s-1"] = v
    return result


def integration_columns(row: dict[str,float]) -> list[str]:
    keep=[]
    for k in row:
        if k.startswith("absorption_") or k == "redshift_threshold_loss_rate_s-1_cMpc-3" or k.startswith("thermal_"):
            keep.append(k)
    return keep


def integrate_rows(rows: list[dict[str,float]], weights: np.ndarray, columns: list[str]) -> tuple[dict[str,float],dict[str,float]]:
    values={}; variations={}
    for c in columns:
        arr=np.array([r[c] for r in rows],dtype=float)
        values[c]=float(np.dot(weights,arr))
        variations[c]=float(np.dot(weights,np.abs(arr)))
    return values,variations


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--inputs",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    root=args.inputs
    p04=root/"Bianchi_Reionization_Stage_P0_4_PAPER_CODE_CHECKPOINT_REGRESSION"
    b2b=root/"Bianchi_Reionization_Stage_P0_5_B2B_PHYSICAL_HISTORY_DT_BRANCH_LOCK"
    b2c1c=root/"Bianchi_Reionization_Stage_P0_5_B2C1C_PRIMARY_HEIII_DECAY_LOCK"
    r1=root/"Bianchi_Reionization_Stage_P0_5_B2C2A_R1_GAMMA_CONDITIONED_DIRECT_OPACITY_RECONCILIATION"
    mod=load_module(r1/"src/gamma_conditioned_reconciliation.py")
    import primary_exact_zero_model as primary_model
    mod.thermal_components = primary_model.thermal_components
    public=pd.read_csv(p04/"data/public_repo_exact_checkpoint_global.csv")
    public=public[(public["source"]=="PUBLIC_REPO_EXACT_CHECKPOINT") & (public["mode"]=="public_continuous_joint")].copy()
    raw_path=mod.find_one(b2b,"environment_mfp_energies.txt")
    density_path=mod.find_one(b2b,"density_mapping_colossus_1_3_10_port.csv")
    started=time.time()
    history,ledger,intervals,fit=mod.re_evolve_direct_history(b2b,b2c1c,public,raw_path,density_path)
    solve_seconds=time.time()-started
    history.to_csv(args.output/"canonical_bdf_replayed_history.csv",index=False)
    ledger.to_csv(args.output/"canonical_bdf_replayed_photon_ledger.csv",index=False)
    fit.to_csv(args.output/"canonical_bdf_replayed_group_fit_tables.csv",index=False)
    exp_history=pd.read_csv(r1/"data/canonical_direct_history.csv")
    exp_ledger=pd.read_csv(r1/"data/canonical_direct_photon_ledger.csv")
    hcmp,hmax=compare_frames(history,exp_history,"z")
    lcmp,lmax=compare_frames(ledger,exp_ledger,"interval_index")
    hcmp.to_csv(args.output/"canonical_history_replay_comparison.csv",index=False)
    lcmp.to_csv(args.output/"canonical_ledger_replay_comparison.csv",index=False)

    # Reference and predeclared candidate representations.
    gl256_x,gl256_w=leggauss(256); gl256_frac=(gl256_x+1.0)/2.0; gl256_w=gl256_w/2.0
    gl512_x,gl512_w=leggauss(512); gl512_frac=(gl512_x+1.0)/2.0; gl512_w=gl512_w/2.0
    candidate_rows=[]; audit=[]; selected_rows_by_n={}
    reference_by_interval={}; variation_by_interval={}; candidate_integrals={}
    columns=None
    for interval in intervals:
        ref_rows=[sample_quantities(mod,interval,float(x)) for x in gl256_frac]
        if columns is None: columns=integration_columns(ref_rows[0])
        ref,var=integrate_rows(ref_rows,gl256_w,columns)
        reference_by_interval[interval.index]=ref; variation_by_interval[interval.index]=var
        for n in CANDIDATE_N:
            xi,w=clenshaw_curtis_nodes_weights(n)
            rows=[sample_quantities(mod,interval,float(x)) for x in xi]
            for j,r in enumerate(rows):
                r.update({"interval_index":interval.index,"node_count":n,"node_index":j,"weight":float(w[j])})
                candidate_rows.append(r)
            integ,ivar=integrate_rows(rows,w,columns)
            candidate_integrals[(interval.index,n)]=(integ,ivar)
    pd.DataFrame(candidate_rows).to_csv(args.output/"candidate_dense_forcing_nodes.csv.gz",index=False,compression="gzip")

    for interval in intervals:
        ref=reference_by_interval[interval.index]; var=variation_by_interval[interval.index]
        for n in CANDIDATE_N:
            integ,_=candidate_integrals[(interval.index,n)]
            for c in columns:
                scale=max(abs(ref[c]),var[c]*1e-14,1e-300)
                audit.append({"interval_index":interval.index,"node_count":n,"quantity":c,"candidate_average":integ[c],"GL256_average":ref[c],"absolute_variation_average":var[c],"dense_relative_residual":abs(integ[c]-ref[c])/scale})
    audit_df=pd.DataFrame(audit)
    # Nested residuals N -> next N.
    next_map={9:17,17:33,33:65}
    nested=[]
    for interval in intervals:
        for n,n2 in next_map.items():
            a,_=candidate_integrals[(interval.index,n)]; b,bvar=candidate_integrals[(interval.index,n2)]
            for c in columns:
                scale=max(abs(b[c]),bvar[c]*1e-14,1e-300)
                nested.append({"interval_index":interval.index,"node_count":n,"next_node_count":n2,"quantity":c,"nested_relative_delta":abs(a[c]-b[c])/scale})
    nested_df=pd.DataFrame(nested)
    audit_df=audit_df.merge(nested_df,on=["interval_index","node_count","quantity"],how="left")
    audit_df.to_csv(args.output/"dense_quadrature_audit.csv",index=False)
    # Global selection, with no per-row node count.
    selected=None
    selection_rows=[]
    for n in CANDIDATE_N:
        max_dense=float(audit_df[audit_df.node_count==n].dense_relative_residual.max())
        if n in next_map:
            max_nested=float(audit_df[audit_df.node_count==n].nested_relative_delta.max())
        else:
            max_nested=math.nan
        passed_dense=max_dense<=DENSE_GATE
        passed_nested=(n in next_map and max_nested<=NESTED_GATE)
        selection_rows.append({"node_count":n,"max_dense_relative_residual":max_dense,"max_nested_relative_delta":max_nested,"passes_dense":passed_dense,"passes_nested":passed_nested,"globally_selected":False})
        if selected is None and passed_dense and passed_nested:
            selected=n
    if selected is None:
        selected=65
    for r in selection_rows:
        r["globally_selected"]=(r["node_count"]==selected)
    pd.DataFrame(selection_rows).to_csv(args.output/"global_quadrature_selection.csv",index=False)
    selected_df=pd.DataFrame(candidate_rows)
    selected_df=selected_df[selected_df.node_count==selected].copy()
    selected_df.to_csv(args.output/"canonical_time_resolved_forcing_nodes.csv",index=False)

    # Independent GL512 audit for every selected quantity; the stage report can highlight worst rows.
    gl512_records=[]
    for interval in intervals:
        rows=[sample_quantities(mod,interval,float(x)) for x in gl512_frac]
        ref512,var512=integrate_rows(rows,gl512_w,columns)
        chosen,_=candidate_integrals[(interval.index,selected)]
        for c in columns:
            scale=max(abs(ref512[c]),var512[c]*1e-14,1e-300)
            gl512_records.append({"interval_index":interval.index,"selected_node_count":selected,"quantity":c,"selected_average":chosen[c],"GL512_average":ref512[c],"absolute_variation_average":var512[c],"relative_residual":abs(chosen[c]-ref512[c])/scale})
    gl512_df=pd.DataFrame(gl512_records)
    gl512_df.to_csv(args.output/"selected_vs_GL512_audit.csv",index=False)

    summary={
        "classification":"CANONICAL_BDF_DENSE_REPLAY_SUMMARY",
        "solve_wall_seconds":solve_seconds,
        "interval_count":len(intervals),
        "history_replay_max_relative_residual":hmax,
        "ledger_replay_max_relative_residual":lmax,
        "canonical_ledger_max_relative_residual":float(np.max(np.abs(ledger.relative_photon_ledger_residual))),
        "selected_global_node_count":int(selected),
        "selected_dense_GL256_max_relative_residual":float(audit_df[audit_df.node_count==selected].dense_relative_residual.max()),
        "selected_nested_max_relative_delta":float(audit_df[audit_df.node_count==selected].nested_relative_delta.max()) if selected in next_map else None,
        "selected_GL512_max_relative_residual":float(gl512_df.relative_residual.max()),
        "primary_G3_exact_zero":bool((history.N4_exact==0.0).all() and (history.Gamma_HeII_exact==0.0).all()),
    }
    (args.output/"canonical_bdf_dense_replay_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
