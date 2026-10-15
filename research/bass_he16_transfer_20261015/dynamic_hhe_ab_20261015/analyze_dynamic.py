"""Source-scoped dynamic H/He, gas internal energy and photon ledger verifier.

This is a 4-variable photoionization+adiabatic-heating control, NOT a
recombination/thermal-feedback-calibrated reionization solver. All reported
bounds refer to the original Rust rlib's frozen atomic reference rates.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

F_HE=0.2454/(4*(1-.2454))
N0=1e-6
T0=8.098143045064857
KB_EV_PER_K=1.380649e-16/1.602176634e-12
Q=(-.005,0.,.005)
ETAS=(0.,1e-5,1e-4)
INDICES=(5,32,33)
STEPS=(1,16,128)
ARMS=("PROJECTED","COVARIANT")
FIELDS=("q_ref","eta_initial","energy_index","substeps")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for x in iter(lambda:f.read(2**20),b""):h.update(x)
    return h.hexdigest()

def load(path):
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    expected=len(Q)*len(ETAS)*len(INDICES)*len(STEPS)*len(ARMS)
    if len(rows)!=expected:
        raise ValueError(f"Expected {expected} A/B source rows; got {len(rows)}")
    keyed={}
    for r in rows:
        if None in r or None in r.values():
            raise ValueError("Unaligned output CSV")
        q,eta,idx,n=float(r["q_ref"]),float(r["eta_initial"]),int(r["energy_index"]),int(r["substeps"])
        arm=r["transport"]
        if q not in Q or eta not in ETAS or idx not in INDICES or n not in STEPS or arm not in ARMS:
            raise ValueError("Unexpected source runtime/configuration")
        key=(q,eta,idx,n)
        keyed.setdefault(key,{})
        if arm in keyed[key]:raise ValueError("Duplicate physical result")
        keyed[key][arm]=r
    if len(keyed)!=expected/2 or any(set(v)!=set(ARMS) for v in keyed.values()):
        raise ValueError("Incomplete A/B source cases")
    return keyed

def parity(path_a,path_b):
    a=load(path_a);b=load(path_b)
    if a.keys()!=b.keys():raise ValueError("A/B case identity mismatch")
    for k in a:
        for arm in ARMS:
            x=a[k][arm];y=b[k][arm]
            for name in x:
                if name=="case_runtime_ms":continue
                if x[name]!=y[name]:
                    raise ValueError(f"Nonidentical numerical result: {k} {arm} {name}")
    return True

def check_gas(r):
    q=float(r["q_ref"]);eta=float(r["eta_initial"]);idx=int(r["energy_index"])
    def get(k):return float(r[k])
    H_abs=get("HI_absorbed_fraction")*N0
    HeI_abs=get("HeI_absorbed_fraction")*N0
    HeII_abs=get("HeII_absorbed_fraction")*N0
    hii=1-eta+H_abs
    y=eta/2+(HeI_abs-HeII_abs)/F_HE
    z=1-eta+HeII_abs/F_HE
    for key,expect in (("x_HII_final",hii),("x_HeII_final",y),
                       ("x_HeIII_final",z)):
        if abs(get(key)-expect)>8e-13:
            raise ValueError(f"Atomic species counter mismatch: {key} {q} {eta}")
    ne=hii+F_HE*(y+2*z)
    if abs(get("electron_per_H_final")-ne)>8e-13:
        raise ValueError("Charge-census error")
    if not 0<=hii<=1+1e-12 or not -1e-12<=y or not 0<=z or y+z>1+1e-12:
        raise ValueError("Species positivity/nuclei simplex failed")
    if get("Tgas_final_K")<=0 or get("u_thermal_final_eV_per_H")<=0:
        raise ValueError("Unphysical gas T or energy")
    tfromu=get("u_thermal_final_eV_per_H")/(1.5*KB_EV_PER_K*(1+F_HE+ne))
    if abs(tfromu-get("Tgas_final_K"))>2e-11:
        raise ValueError("Kinetic thermal EOS mismatch")
    xe_init=(1-eta)+F_HE*(eta/2+2*(1-eta))
    gas_initial_energy=1.5*KB_EV_PER_K*(1+F_HE+xe_init)*T0
    gas_lhs=gas_initial_energy+get("gas_deposited_photoheat_eV_per_H")
    gas_rhs=get("u_thermal_final_eV_per_H")+get("gas_adiabatic_loss_eV_per_H")
    if abs(gas_lhs-gas_rhs)>1e-12:
        raise ValueError("Gas adiabatic/absorption energy ledger")
    if abs(get("gas_deposited_photoheat_eV_per_H")-get("photoheat_eV_per_initial")*N0)>1e-12:
        raise ValueError("Photon photoheat vs gas internal-energy ledger")
    for k in ("photon_number_residual_relative","photon_energy_residual_relative",
              "photon_event_residual_relative"):
        if abs(get(k))>5e-9:raise ValueError("Photoevent ledger residual")
    if abs(get("gas_thermal_residual_eV_per_H"))>1e-11:
        raise ValueError("Thermal/expansion residual")
    if get("gas_max_charge_residual")>2e-13:
        raise ValueError("Charged particle/event source residual")
    if eta==0:
        if any(get(k)!=0. for k in
               ("HI_absorbed_fraction","HeI_absorbed_fraction",
                "HeII_absorbed_fraction","photoheat_eV_per_initial")):
            raise ValueError("Transparent gas erroneously absorbs")
    if idx in (5,):
        if get("HeII_absorbed_fraction")!=0.:
            raise ValueError("Below-threshold HeII event")
    if idx==32 and r["transport"]=="COVARIANT" and get("HeII_absorbed_fraction")!=0.:
        raise ValueError("Covariant sub-threshold photon ionizes HeII")
    if idx==32 and r["transport"]=="PROJECTED" and eta>0 and get("HeII_absorbed_fraction")<=0:
        raise ValueError("Canonical grid ghost HeII event not reproduced")
    if idx==33 and eta>0 and get("HeII_absorbed_fraction")<=0:
        raise ValueError("True above-threshold positive control failed")
    return True

def analyze(serial,parallel=None):
    s=load(serial)
    if parallel is not None:parity(serial,parallel)
    for arms in s.values():
        for rec in arms.values():check_gas(rec)
    cases=[]
    for q in Q:
        for eta in ETAS:
            for idx in INDICES:
                differences=[]
                for steps in STEPS:
                    a=s[q,eta,idx,steps]["PROJECTED"]
                    b=s[q,eta,idx,steps]["COVARIANT"]
                    diffs={
                        "steps":steps,
                        "delta_xHeIII_projected_minus_covariant":
                            float(a["x_HeIII_final"])-float(b["x_HeIII_final"]),
                        "delta_xHII_projected_minus_covariant":
                            float(a["x_HII_final"])-float(b["x_HII_final"]),
                        "delta_temperature_K_projected_minus_covariant":
                            float(a["Tgas_final_K"])-float(b["Tgas_final_K"]),
                        "HeII_projected_per_photon":float(a["HeII_absorbed_fraction"]),
                        "HeII_covariant_per_photon":float(b["HeII_absorbed_fraction"]),
                        "gas_u_projected":float(a["u_thermal_final_eV_per_H"]),
                        "gas_u_covariant":float(b["u_thermal_final_eV_per_H"]),
                    }
                    differences.append(diffs)
                cases.append({"q":q,"eta":eta,"initial_energy_index":idx,"levels":differences})
    chosen=next(x for x in cases if x["q"]==0 and x["eta"]==1e-5 and x["initial_energy_index"]==32)
    result={
        "schema":"he18.axbi.dynamic_photo_only_source_ab.v1",
        "status":"NUMERICALLY_VERIFIED_PHOTO_ONLY_DYNAMIC_GAS_GLOBAL_EOR_HOLD",
        "original_source":"rei_microphysics rust original source compiled reference rlib; selected atomic/transport bodies pinned separately",
        "physical_scope":"LRS non-tilted Bianchi I, photoionization HII HeII HeIII, photoheating and gas adiabatic cooling, no recombination/emissivity/atomic collisional cooling or thermal feedback on source rates",
        "cases":len(s),"lane_records":2*len(s),
        "gas_initial_T_K":T0,"photon_initial_per_H":N0,"helium_to_H_number_ratio":F_HE,
        "q_values":list(Q),"eta_initial_values":list(ETAS),"energy_bins":list(INDICES),"substeps":list(STEPS),
        "source_refinement_goal":"Distinguish 54.42eV threshold ghost events in dynamic H/He state, not a complete reionization calculation",
        "reported_sample":chosen,
        "all_cases":cases,
        "serial_sha256":sha(serial),"parallel_sha256":sha(parallel) if parallel else None,
        "physics_identity_across_workers":parallel is not None,
        "scientific_admission":"HOLD_FULL_EOR_NATIVE",
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--serial",type=Path,required=True)
    p.add_argument("--parallel",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    o=analyze(args.serial,args.parallel)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(o,indent=2)+"\n")
    print(json.dumps({"cases":o["cases"],"records":o["lane_records"],
                      "physics_parity":o["physics_identity_across_workers"],
                      "sample":o["reported_sample"]},indent=2))
if __name__=="__main__":main()
