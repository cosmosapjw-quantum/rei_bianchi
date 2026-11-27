"""B1 actual prescribed-history Liouville/Thomson computation.

Explicit existing Python Thomson backend; no automatic Rust fallback.
All outputs are fresh, scope-labelled and tied to frozen input identities.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import time

import numpy as np
from scipy.interpolate import CubicSpline
from numpy.polynomial.legendre import leggauss

from native.python_thomson import PythonThomson

ROOT = Path(__file__).resolve().parent
CASES = ("F", "M", "B", "B0", "B_F", "M_F")
REPORT_Y = np.array([0.1, 0.3, 1.0, 3.0, 6.0, 10.0])


def atomic_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def angular_grid(nmu, nphi=8):
    mu, wmu = leggauss(nmu)
    phi = 2 * np.pi * np.arange(nphi) / nphi
    m, p = np.meshgrid(mu, phi, indexing="ij")
    st = np.sqrt(1 - m*m)
    e = np.stack([st*np.cos(p), st*np.sin(p), m], axis=-1).reshape(-1, 3)
    et = np.stack([m*np.cos(p), m*np.sin(p), -st], axis=-1).reshape(-1, 3)
    ep = np.stack([-np.sin(p), np.cos(p), np.zeros_like(p)], axis=-1).reshape(-1, 3)
    w = np.repeat(wmu, nphi) * (2*np.pi/nphi)
    return mu, wmu, e, et, ep, w


def packed_dyad(v):
    d = v[:, :, None] * v[:, None, :]
    return np.stack([d[:, 0, 0], d[:, 1, 1], d[:, 2, 2],
                     d[:, 0, 1], d[:, 0, 2], d[:, 1, 2],
                     np.zeros(len(v)), np.zeros(len(v)), np.zeros(len(v))], axis=-1)


def screen_component(j, left, right):
    return (j[..., 0]*left[:, None, 0]*right[:, None, 0]
            + j[..., 1]*left[:, None, 1]*right[:, None, 1]
            + j[..., 2]*left[:, None, 2]*right[:, None, 2]
            + j[..., 3]*(left[:, None, 0]*right[:, None, 1]+left[:, None, 1]*right[:, None, 0])
            + j[..., 4]*(left[:, None, 0]*right[:, None, 2]+left[:, None, 2]*right[:, None, 0])
            + j[..., 5]*(left[:, None, 1]*right[:, None, 2]+left[:, None, 2]*right[:, None, 1]))


class LRSBridge:
    def __init__(self, nmu, lny, nphi=8):
        self.mu, self.wmu, self.e, self.et, self.ep, self.w = angular_grid(nmu, nphi)
        self.nmu, self.nphi, self.lny = nmu, nphi, lny
        self.theta_dyad = packed_dyad(self.et)
        self.phi_dyad = packed_dyad(self.ep)
        self.collision = PythonThomson(self.e, self.w)
        self.diagnostics = dict(max_collision_number_relative=0.0,
                                max_screen_U_over_I=0.0, max_screen_V_over_I=0.0,
                                max_azimuth_relative=0.0,
                                max_mu_extrapolation=0.0, max_lny_extrapolation=0.0,
                                min_occupation=float("inf"), liouville_stages=0)

    def liouville(self, f, db):
        self.diagnostics["liouville_stages"] += 1
        if db == 0.0:
            return f.copy()
        if np.any(f <= 0) or not np.isfinite(f).all():
            raise FloatingPointError("Nonpositive/nonfinite coherency before logarithmic pullback")
        m = self.mu
        d = np.sqrt((1-m*m)*np.exp(-2*db) + m*m*np.exp(4*db))
        old_mu = m*np.exp(2*db)/d
        old_lny = self.lny[None, :] + np.log(d)[:, None]
        if np.any(np.abs(old_mu) > 1+2e-15):
            raise FloatingPointError("Characteristic left the physical unit sphere")
        self.diagnostics["max_mu_extrapolation"] = max(
            self.diagnostics["max_mu_extrapolation"],
            float(max(0.0, np.max(old_mu)-m[-1], m[0]-np.min(old_mu))))
        self.diagnostics["max_lny_extrapolation"] = max(
            self.diagnostics["max_lny_extrapolation"],
            float(max(0.0, np.max(old_lny)-self.lny[-1], self.lny[0]-np.min(old_lny))))
        stage = CubicSpline(m, np.log(f), axis=0, extrapolate=True)(old_mu)
        spline = CubicSpline(self.lny, stage.swapaxes(0, 1), axis=0, extrapolate=True)
        idx = np.searchsorted(self.lny, old_lny, side="right") - 1
        # Choose endpoint polynomial pieces for explicit cubic extrapolation.
        idx = np.minimum(np.maximum(idx, 0), len(self.lny)-2)
        dm = old_lny-self.lny[idx]
        mi = np.arange(self.nmu)[:, None]
        c = spline.c
        result_log = (((c[0, idx, mi]*dm[..., None]+c[1, idx, mi])*dm[..., None]
                       + c[2, idx, mi])*dm[..., None]+c[3, idx, mi])
        result = np.exp(result_log)
        if not np.isfinite(result).all() or np.any(result <= 0):
            raise FloatingPointError("Pullback positivity/finiteness failure; no clipping")
        return result

    def scatter(self, f, depth):
        ft = np.repeat(f[..., 0], self.nphi, axis=0)
        fp = np.repeat(f[..., 1], self.nphi, axis=0)
        j = (ft[..., None]*self.theta_dyad[:, None, :]
             + fp[..., None]*self.phi_dyad[:, None, :])
        before = self.w @ (j[..., 0]+j[..., 1]+j[..., 2])
        out = self.collision.collide(j, depth)
        after = self.w @ (out[..., 0]+out[..., 1]+out[..., 2])
        loss = float(np.max(np.abs(after/before-1)))
        self.diagnostics["max_collision_number_relative"] = max(
            self.diagnostics["max_collision_number_relative"], loss)
        a = screen_component(out, self.et, self.et)
        b = screen_component(out, self.ep, self.ep)
        intensity = a+b
        u = 2*screen_component(out, self.et, self.ep)
        anti = np.linalg.norm(out[..., 6:9], axis=-1)
        ru = float(np.max(np.abs(u)/intensity))
        rv = float(np.max(2*anti/intensity))
        self.diagnostics["max_screen_U_over_I"] = max(self.diagnostics["max_screen_U_over_I"], ru)
        self.diagnostics["max_screen_V_over_I"] = max(self.diagnostics["max_screen_V_over_I"], rv)
        pair = np.stack([a, b], axis=-1).reshape(self.nmu, self.nphi, len(self.lny), 2)
        mean = pair.mean(axis=1)
        az = float(np.max(np.abs(pair/mean[:, None, :, :]-1)))
        self.diagnostics["max_azimuth_relative"] = max(self.diagnostics["max_azimuth_relative"], az)
        if loss > 2e-12 or ru > 2e-12 or rv > 2e-12 or az > 2e-12:
            raise FloatingPointError("Collision conservation or LRS symmetry failure")
        if not np.isfinite(mean).all() or np.any(mean <= 0):
            raise FloatingPointError("Collision screen positivity/finiteness failure")
        self.diagnostics["min_occupation"] = min(self.diagnostics["min_occupation"], float(mean.min()))
        return mean

    def observables(self, f):
        it = f.sum(axis=-1)
        qt = f[..., 0]-f[..., 1]
        den = self.wmu @ it
        if np.any(den <= 0):
            raise FloatingPointError("Undefined intensity denominator")
        q2 = (self.wmu*(3*self.mu**2-1)/2) @ it / den
        p = np.abs(qt)/it
        y = np.exp(self.lny)
        # These quantities are dimensionless spectra normalized to T_iso(a).
        return dict(q2=q2, Ibar_y3=y**3*den/2,
                    Qbar_over_I=(self.wmu @ qt)/den,
                    pL_max=p.max(axis=0),
                    pL_weighted=(self.wmu @ np.abs(qt))/den,
                    pL_equator=np.abs(CubicSpline(self.mu, qt, axis=0)(0.0)
                                      / CubicSpline(self.mu, it, axis=0)(0.0)))


def execute(case, nsteps, nmu, nenergy, outdir, log_min=-8.0, log_max=5.0):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=False)
    input_path = ROOT/"inputs/B1_FROZEN_PROJECTED_INPUTS.npz"
    data = dict(np.load(input_path, allow_pickle=False))
    nfine = len(data["depth_B"])
    if nfine % nsteps != 0 or nsteps < 8:
        raise ValueError("Time steps must divide the frozen fine grid and be >=8")
    stride = nfine//nsteps
    if stride % 2:
        raise ValueError("Need frozen half edges for symmetric splitting")
    lny = np.unique(np.r_[np.linspace(log_min, log_max, nenergy), np.log(REPORT_Y)])
    bridge = LRSBridge(nmu, lny)
    y = np.exp(lny)
    # Exactly the upstream isotropic Planck functional form; coherency trace f.
    f = np.broadcast_to((0.5/np.expm1(y))[None, :, None], (nmu, len(y), 2)).copy()
    bsrc = data["b_B"] if case in ("B", "B0", "B_F") else data["b_F"]
    depth_key = "depth_F" if case == "F" else ("depth_F_on_B" if case in ("B_F", "M_F") else "depth_B")
    depths = data[depth_key].reshape(nsteps, stride).sum(axis=1)
    if case == "B0":
        depths = np.zeros_like(depths)
    times = data["t_F_s"] if case == "F" else data["t_B_s"]
    sample_step = max(1, nsteps//32)
    snapshots = []
    def save_sample(step):
        i = step*stride
        rec = dict(step=step, u=float(data["u"][i]), z_mean=float(data["z_mean"][i]),
                   proper_elapsed_s=float(times[i]), b=float(bsrc[i]))
        rec.update(bridge.observables(f))
        snapshots.append(rec)
    save_sample(0)
    start = time.perf_counter()
    cpu_start = time.process_time()
    atomic_json(outdir/"RUN_STATE.json", dict(status="RUNNING", case=case, nsteps=nsteps,
        nmu=nmu, nenergy_actual=len(y), backend=bridge.collision.backend,
        native_rust_invocations=0, command=sys.argv))
    try:
        for step in range(nsteps):
            lo, mid, hi = step*stride, step*stride+stride//2, (step+1)*stride
            f = bridge.liouville(f, float(bsrc[mid]-bsrc[lo]))
            f = bridge.scatter(f, float(depths[step]))
            f = bridge.liouville(f, float(bsrc[hi]-bsrc[mid]))
            if (step+1) % sample_step == 0 or step+1 == nsteps:
                save_sample(step+1)
        wall = time.perf_counter()-start
        cpu = time.process_time()-cpu_start
        coll = bridge.collision
        report_idx = np.array([int(np.argmin(abs(y-v))) for v in REPORT_Y])
        arrays = {k:np.stack([s[k] for s in snapshots]) for k in snapshots[0]}
        np.savez_compressed(outdir/"result.npz", **arrays, y=y, lny=lny, mu=bridge.mu,
                            wmu=bridge.wmu, final_screen=f, report_indices=report_idx)
        columns = ["case","z_mean","u","proper_elapsed_s","y","E_over_kBT_i",
                   "q2","Ibar_y3","Qbar_over_I","pL_max","pL_weighted","pL_equator"]
        with (outdir/"observables.csv").open("w", newline="") as fd:
            writer = csv.DictWriter(fd, fieldnames=columns)
            writer.writeheader()
            for sample in snapshots:
                for j in np.flatnonzero((y>=0.1*(1-1e-14)) & (y<=10*(1+1e-14))):
                    row = dict(case=case,z_mean=sample["z_mean"],u=sample["u"],
                               proper_elapsed_s=sample["proper_elapsed_s"],y=y[j],
                               E_over_kBT_i=y[j]*math.exp(-sample["u"]))
                    row.update({k:sample[k][j] for k in columns[6:]})
                    writer.writerow(row)
        receipt = dict(status="EXECUTED_SCOPED_PYTHON",case=case,nsteps=nsteps,
            nmu=nmu,nphi=bridge.nphi,nenergy_base=nenergy,nenergy_actual=len(y),
            log_y_domain=[log_min,log_max],claimed_y_domain=[0.1,10.0],
            backend=coll.backend,native_rust_invocations=0,
            collision_stages=coll.calls,positive_depth_stages=coll.positive_depth_calls,
            upstream_energy_slice_calls=coll.upstream_energy_slice_calls,
            integrated_depth=coll.depth_sum,wall_seconds=wall,cpu_seconds=cpu,
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
            python=sys.version,numpy=np.__version__,platform=platform.platform(),
            diagnostics=bridge.diagnostics,
            output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [outdir/"result.npz",outdir/"observables.csv"]},
            final_report_y={str(float(y[j])):{k:float(snapshots[-1][k][j])
                for k in ("q2","Ibar_y3","Qbar_over_I","pL_equator")}
                for j in report_idx})
        atomic_json(outdir/"RECEIPT.json", receipt)
        atomic_json(outdir/"RUN_STATE.json", dict(status="COMPLETED",receipt="RECEIPT.json"))
        print(json.dumps({k:receipt[k] for k in ("status","case","nsteps","nmu","nenergy_actual",
            "wall_seconds","cpu_seconds","peak_rss_kib","integrated_depth","final_report_y")}), flush=True)
        return receipt
    except Exception as exc:
        atomic_json(outdir/"FAILURE.json",dict(status="FAILED",failure_type=type(exc).__name__,
            message=str(exc),case=case,completed_collision_stages=bridge.collision.calls,
            native_rust_invocations=0))
        raise


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--case",choices=CASES,required=True)
    ap.add_argument("--nsteps",type=int,default=128)
    ap.add_argument("--nmu",type=int,default=24)
    ap.add_argument("--nenergy",type=int,default=129)
    ap.add_argument("--log-min",type=float,default=-8.0)
    ap.add_argument("--log-max",type=float,default=5.0)
    ap.add_argument("--out",type=Path,required=True)
    args = ap.parse_args()
    execute(args.case,args.nsteps,args.nmu,args.nenergy,args.out,args.log_min,args.log_max)
