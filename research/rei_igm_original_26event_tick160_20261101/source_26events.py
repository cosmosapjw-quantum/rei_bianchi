#!/usr/bin/env python3
"""Read-only, original 26-event REI H/He source diagnostic at t0 and accepted tick 160.

Source: immutable 46,080-node first-canonical-interval archive, exact SHA256.
The interval midpoints in output are independent flux bounds, NOT a coherent
physical 26-event realization or a replacement for the joint local-error gate.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, json, struct, sys, tarfile
from pathlib import Path
import numpy as np

ARCHIVE_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
NODE_COUNT = 46080
TICK = 160
TOTAL = 131072
MAGIC = b"REIADP1\x00"
KB = 1.380649e-16
LANES = ("LOCAL_NEUTRAL_HAZARD_PRIMARY", "RECOMBINATION_WEIGHTED_AUDITOR", "SCRIPT_SELF_SHIELDING_AUDITOR")
PRED = ("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
        "R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK")
STAGE = ("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
         "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unpack_state(data):
    if not data.startswith(MAGIC):
        return None
    size = struct.unpack_from("<Q", data, len(MAGIC))[0]
    if not 0 < size < 65536:
        raise ValueError("bad original state metadata size")
    offset = len(MAGIC) + 8
    header = json.loads(data[offset:offset+size].decode("ascii"))
    if header.get("population_shape") != [NODE_COUNT, 5]:
        raise ValueError("incorrect original state node count")
    if header.get("log_temperature_shape") != [NODE_COUNT]:
        raise ValueError("incorrect original temperature shape")
    order = ["population_lower", "population_upper", "log_temperature_lower", "log_temperature_upper"]
    if header.get("array_order") != order:
        raise ValueError("different original state array order")
    raw = data[offset+size:]
    a = np.frombuffer(raw, dtype="<f8")
    k = NODE_COUNT * 5
    if a.size != 2*k + 2*NODE_COUNT or not np.isfinite(a).all():
        raise ValueError("invalid state payload")
    lo, hi = a[:k].reshape(NODE_COUNT, 5), a[k:2*k].reshape(NODE_COUNT, 5)
    tl, th = a[2*k:2*k+NODE_COUNT], a[2*k+NODE_COUNT:]
    if (lo <= 0).any() or (hi < lo).any() or (th < tl).any():
        raise ValueError("invalid state physical enclosure")
    return dict(metadata=header.get("metadata", {}), lo=lo, hi=hi, tl=tl, th=th,
                array_sha=hashlib.sha256(raw).hexdigest())


def archived_tick160(path):
    if sha256(path) != ARCHIVE_SHA:
        raise ValueError("immutable original archive SHA256 mismatch")
    states = {}
    with tarfile.open(path, "r:gz") as ar:
        for member in ar:
            if not member.isfile():
                continue
            q = Path(member.name)
            if q.is_absolute() or ".." in q.parts:
                raise ValueError("unsafe source archive member")
            if member.size > 8_000_000 or member.size < 64:
                continue
            found = unpack_state(ar.extractfile(member).read())
            if found is None or found["metadata"].get("endpoint_tick") != TICK:
                continue
            lane = found["metadata"].get("lane")
            if lane not in LANES:
                raise ValueError("unrecognized original lane")
            if lane in states and states[lane]["array_sha"] != found["array_sha"]:
                raise ValueError("conflicting original accepted states")
            states[lane] = found
    if set(states) != set(LANES):
        raise ValueError("source archive lacks original accepted tick160 states")
    return states


def representative(lo, hi, h_total, he_total):
    """An in-box positive representative, preserving nuclei, NOT coherent dynamics."""
    out = np.empty_like(lo)
    for columns, total in ((slice(0, 2), h_total), (slice(2, 5), he_total)):
        lower, upper = lo[:, columns], hi[:, columns]
        capacity = np.sum(upper-lower, axis=1)
        extra = total-np.sum(lower, axis=1)
        slope = np.zeros_like(extra)
        mask = capacity > 0
        slope[mask] = extra[mask] / capacity[mask]
        if ((slope[mask] < -1e-10) | (slope[mask] > 1+1e-10)).any():
            raise ValueError("no in-box nuclei conserving point")
        if (np.abs(extra[~mask]) > 1e-10 * np.maximum(1.0, np.abs(total[~mask]))).any():
            raise ValueError("inconsistent zero-width nuclei")
        out[:, columns] = lower+(upper-lower)*slope[:, None]
    if (out < -1e-12*np.maximum(1, abs(lo))).any() or (out > hi+1e-12*np.maximum(1, abs(hi))).any():
        raise ValueError("constructed point outside source box")
    return out


def stoich_flux(f):
    """F[dest,source] in particle/s, so dotN = rowSum-colSum."""
    return np.sum(f, axis=2)-np.sum(f, axis=1)


def percentile(a):
    if not np.isfinite(a).all():
        raise ValueError("nonfinite output")
    return {str(q): float(np.percentile(a,q)) for q in (0,5,50,95,100)}


def physical_snapshot(m, model, base, poplo, pophi, tlo, thi, time_s, name, lane):
    start = base.inputs.state0.mutable_copy()
    nuclei = np.asarray(start.values[:5].T, float)
    total_h = nuclei[:,0]+nuclei[:,1]
    total_he = np.sum(nuclei[:,2:5], axis=1)
    if (total_h<=0).any() or (total_he<=0).any():
        raise ValueError("nonpositive source nuclei")
    # Evaluate ORIGINAL 26-event OTS source with full uncertain input state.
    ev = m.event_box(model, m._I(poplo, pophi),
                     m.iv.exp(m._I(tlo, thi)), float(time_s))
    flo, fhi = np.asarray(ev.flux.lo), np.asarray(ev.flux.hi)
    if flo.shape != (NODE_COUNT,5,5) or fhi.shape != flo.shape:
        raise ValueError("unexpected original source flux shape")
    if not np.isfinite(flo).all() or not np.isfinite(fhi).all() or (fhi<flo).any():
        raise ValueError("nonfinite or malformed event interval")
    point=representative(poplo,pophi,total_h,total_he)
    # IMPORTANT: midpoint of independently enclosed F_ij can be physically
    # incompatible across shared source variables; diagnostic ONLY.
    flux=0.5*(flo+fhi)
    dot=stoich_flux(flux)
    norm=np.maximum(np.sum(np.abs(flux),axis=(1,2)),1e-300)
    h_err=(dot[:,0]+dot[:,1])/norm
    he_err=np.sum(dot[:,2:5],axis=1)/norm
    if np.max(np.abs(h_err))>5e-13 or np.max(np.abs(he_err))>5e-13:
        raise ValueError("original source stoichiometry violates nuclei")
    ledger=ev.resolved_heat+ev.unresolved_energy+ev.escaped_energy+ev.chemical_energy
    if not np.all(np.asarray(ledger.lo)<=0) or not np.all(np.asarray(ledger.hi)>=0):
        raise ValueError("source OTS energy identity does not contain zero")
    if not np.all(np.asarray(ev.photon_identity.lo)<=0) or not np.all(np.asarray(ev.photon_identity.hi)>=0):
        raise ValueError("source OTS photon identity does not contain zero")
    T=np.exp(0.5*(tlo+thi))
    electrons=point[:,1]+point[:,3]+2*point[:,4]
    heating=lambda a: 0.5*(np.asarray(a.lo)+np.asarray(a.hi))/total_h
    fields=dict(
      x_HII=point[:,1]/total_h,
      x_HeII=point[:,3]/total_he,
      x_HeIII=point[:,4]/total_he,
      temperature_K=T,
      free_electrons_per_H=electrons/total_h,
      thermal_erg_per_H=1.5*KB*T*(total_h+total_he+electrons)/total_h,
      dx_HII_dt_mid_per_s=dot[:,1]/total_h,
      dx_HeII_dt_mid_per_s=dot[:,3]/total_he,
      dx_HeIII_dt_mid_per_s=dot[:,4]/total_he,
      dxe_dt_mid_per_s=(dot[:,1]+dot[:,3]+2*dot[:,4])/total_h,
      photoheat_erg_per_H_s_mid=heating(ev.photo_heat),
      resolved_OTS_heat_erg_per_H_s_mid=heating(ev.resolved_heat),
      escaped_OTS_erg_per_H_s_mid=heating(ev.escaped_energy))
    result=dict(lane=lane,snapshot=name,time_s_from_interval_begin=float(time_s),
      nodes=NODE_COUNT,source="unmodified_original_26event_MPRK22_OTS",
      source_flux_meaning="independent interval midpoint diagnostic, NOT a physical trajectory",
      extrema_and_equal_node_percentiles={key:percentile(a) for key,a in fields.items()},
      max_H_nuclei_stoich_relative=float(np.max(np.abs(h_err))),
      max_He_nuclei_stoich_relative=float(np.max(np.abs(he_err))),
      OTS_energy_zero_included=True,OTS_photon_identity_zero_included=True)
    return result,fields


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def run(repo, out):
    repo,out=Path(repo).resolve(),Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    archive=repo/"stages"/STAGE/"local_results"/"first_interval_r2_blocked_minimum_step.tar.gz"
    states=archived_tick160(archive)
    module=load_module("rei_26event_original_source",repo/"stages"/PRED/"analysis"/"interval_discrete_map.py")
    model=module.rim.ReducedIntervalModel.from_repo(repo)
    results=[]
    for lane in LANES:
        base=module.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
        original=base.inputs.state0.mutable_copy()
        p=np.asarray(original.values[:5].T,float)
        logt=np.log(np.asarray(original.temperature_K,float))
        duration=float(base.forcing.duration_seconds(0))
        state=states[lane]
        inputs=[
          ("initial",p,p,logt,logt,0.0),
          ("accepted_tick160",state["lo"],state["hi"],state["tl"],state["th"],duration*TICK/TOTAL)]
        for snapshot,lo,hi,tl,th,time_s in inputs:
            row,fields=physical_snapshot(module,model,base,lo,hi,tl,th,time_s,snapshot,lane)
            row["accepted_state_array_sha256"]=state["array_sha"]
            path=out/("original_26event_"+lane+"_"+snapshot+".csv.gz")
            with gzip.open(path,"wt",newline="",encoding="utf-8",compresslevel=6) as stream:
                writer=csv.writer(stream)
                keys=list(fields)
                writer.writerow(["node",*keys])
                for i in range(NODE_COUNT):
                    writer.writerow([i,*[format(float(fields[k][i]),".17g") for k in keys]])
            row["csv_file"]=path.name
            row["csv_sha256"]=sha256(path)
            results.append(row)
            print("REAL_26_EVENT_SUMMARY",json.dumps({
              "lane":lane,"snapshot":snapshot,
              "x_HII_median":row["extrema_and_equal_node_percentiles"]["x_HII"]["50"],
              "T_median_K":row["extrema_and_equal_node_percentiles"]["temperature_K"]["50"],
              "photoheat_median_erg_per_H_s":row["extrema_and_equal_node_percentiles"]["photoheat_erg_per_H_s_mid"]["50"],
              "dxe_dt_median_s_inv":row["extrema_and_equal_node_percentiles"]["dxe_dt_mid_per_s"]["50"],
              "source_hash":state["array_sha"]},sort_keys=True),flush=True)
    report=dict(schema="REI_IGM_26EVENT_ORIGINAL_SOURCE_T0_TICK160_V1",
      original_archive_sha256=ARCHIVE_SHA,physical_nodes_per_lane=NODE_COUNT,
      saved_model_diagnostic_rows=NODE_COUNT*len(results),independent_observed_rows=0,
      accepted_tick=TICK,first_interval_total_ticks=TOTAL,
      whole_first_interval_closed=False,original_minimum_step_blocker_preserved=True,
      canonical_new_nodes=0,REI_central_reported="28/88",production="HOLD",merge="HOLD",
      scientific_claim="original state-conditioned source diagnostics; no new IVP or full local-error certificate",
      rows=results)
    final=out/"ORIGINAL_26EVENT_PHYSICS.json"
    final.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("REAL_26_EVENT_RESULT",str(final),"ROWS",report["saved_model_diagnostic_rows"],flush=True)
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[3])
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    run(a.repo,a.out)
