"""Scientific acceptance tests and derived data for frozen-gas H/He A/B transport.

A uses native geometry_map reprojecting onto fixed energy nodes; B retains
original covariant photon momentum. Both call the same reference frozen-gas
exponential collision at the same midpoint, fixed gas and clock. This does
NOT evolve H/He abundances or replace original production source.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import median

CASE_KEYS=("q_ref","eta_neutral","e_index","steps")
EVENTS=("HI_absorbed_per_initial","HeI_absorbed_per_initial",
        "HeII_absorbed_per_initial")
THRESHOLDS=(13.598434599702,24.587389011,54.41776)
SOURCE_PACKET_PER_H=1.0e-10
F_HE=0.2454/(4*(1-0.2454))


def hashfile(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""):h.update(b)
    return h.hexdigest()


def load(path):
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=216:
        raise ValueError(f"Expected 108 frozen-gas controls x2 arms, not {len(rows)}")
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("CSV field alignment failure")
    actual={}
    for r in rows:
        key=tuple(r[k] for k in CASE_KEYS)
        actual.setdefault(key,{})
        arm=r["arm"]
        if arm in actual[key]:
            raise ValueError("Repeated source identity in A/B")
        if arm not in ("PROJECTED","COVARIANT"):raise ValueError("Unknown transport lane")
        actual[key][arm]=r
    if len(actual)!=108 or any(set(arms)!={"PROJECTED","COVARIANT"} for arms in actual.values()):
        raise ValueError("Case key or arms coverage failure")
    return actual


def numeric_identity(source,path):
    x=load(source);y=load(path)
    cols=next(iter(next(iter(x.values())).values())).keys()
    if x.keys()!=y.keys():
        raise ValueError("Serial/parallel case identity mismatch")
    for key in x:
        for arm in ("PROJECTED","COVARIANT"):
            for col in cols:
                if col=="case_runtime_ms":continue
                if x[key][arm][col]!=y[key][arm][col]:
                    raise ValueError(f"Serial/parallel physics changed: {key} {arm} {col}")
    return True


def analyse(path, second=None):
    data=load(path)
    if second is not None:numeric_identity(path,second)
    max_resid={x:0.0 for x in
        ("number_residual_per_initial","energy_residual_per_initial_energy",
         "event_residual_per_initial")}
    threshold_sample=[]
    all_samples=[]
    for key,arms in data.items():
        q,eta,idx,steps=map(float,key)
        assert steps in (1.,32.,256.)
        eta=float(eta);idx=int(idx);steps=int(steps)
        a=arms["PROJECTED"];b=arms["COVARIANT"]
        for arm in (a,b):
            for field in max_resid:
                max_resid[field]=max(max_resid[field],abs(float(arm[field])))
            if float(arm["binding_eV_per_initial"])<-1e-14 or \
               float(arm["heating_eV_per_initial"])<-1e-14:
                raise ValueError("Negative binding energy or photoheating")
            arr=[float(arm[e]) for e in EVENTS]
            if any(v<-1e-14 for v in arr):
                raise ValueError("Negative species absorption count")
            pred=sum(n*x for n,x in zip(arr,THRESHOLDS))
            if abs(float(arm["binding_eV_per_initial"])-pred)>5e-12:
                raise ValueError("Physical species threshold/binding energy mismatch")
            if abs(float(arm["surviving_photons_per_initial"])+
                    sum(arr)+float(arm["grid_boundary_photons_per_initial"])-1.)>3e-12:
                raise ValueError("Photon number ledger mismatch")
            if float(arm["HeII_absorbed_per_initial"])*SOURCE_PACKET_PER_H > \
               eta*F_HE/2 + 1e-30:
                raise ValueError("Frozen HeII reservoir depleted beyond available nuclei")
        if max(abs(float(a[f])-float(b[f])) for f in
               ("initial_energy_eV","exact_final_energy_eV"))>1e-12:
            raise ValueError("Different physical initial/end characteristic")
        if eta==0.0:
            for arm in (a,b):
                if any(float(arm[f])!=0 for f in EVENTS) or \
                   float(arm["binding_eV_per_initial"])!=0 or \
                   float(arm["heating_eV_per_initial"])!=0:
                    raise ValueError("Transparent source absorbs photons")
            if float(b["grid_boundary_photons_per_initial"])!=0:
                raise ValueError("Exact unprojected photon violates boundary contract")
        if idx in (5,20):
            if float(a["HeII_absorbed_per_initial"])!=0 or \
               float(b["HeII_absorbed_per_initial"])!=0:
                raise ValueError("Below HeII threshold event")
        if idx==32:
            if float(a["initial_energy_eV"]) != 54.42:
                raise ValueError("Incorrect native source HeII threshold node")
            if float(b["exact_final_energy_eV"]) >= 54.42:
                raise ValueError("Exact characteristic must finish below HeII threshold")
            if float(b["HeII_absorbed_per_initial"])!=0:
                raise ValueError("Exact covariant ray falsely ionizes HeII")
            if eta>0 and float(a["HeII_absorbed_per_initial"])<=0:
                raise ValueError("Grid-threshold false HeII event not reproduced")
        if idx==33 and eta>0 and (float(a["HeII_absorbed_per_initial"])<=0 or
                                   float(b["HeII_absorbed_per_initial"])<=0):
            raise ValueError("Above-threshold physical HeII positive control failed")
        if steps==256 and idx==32 and eta>0:
            threshold_sample.append({
                "q_ref":q,"eta_neutral":eta,
                "initial_energy_eV":float(a["initial_energy_eV"]),
                "exact_characteristic_endpoint_energy_eV":float(b["exact_final_energy_eV"]),
                "HeII_absorb_PROJECTED_per_initial":float(a["HeII_absorbed_per_initial"]),
                "HeII_absorb_COVARIANT_per_initial":float(b["HeII_absorbed_per_initial"]),
                "HI_absorb_PROJECTED_per_initial":float(a["HI_absorbed_per_initial"]),
                "HI_absorb_COVARIANT_per_initial":float(b["HI_absorbed_per_initial"]),
                "binding_PROJECTED_eV_per_initial":float(a["binding_eV_per_initial"]),
                "binding_COVARIANT_eV_per_initial":float(b["binding_eV_per_initial"]),
                "heat_PROJECTED_eV_per_initial":float(a["heating_eV_per_initial"]),
                "heat_COVARIANT_eV_per_initial":float(b["heating_eV_per_initial"]),
                "spurious_HeII_events_per_H":
                    float(a["HeII_absorbed_per_initial"])*SOURCE_PACKET_PER_H,
                "HeII_available_per_H":eta*F_HE/2,
            })
        all_samples.append({"q":q,"eta":eta,"index":idx,"steps":steps,
            "delta_heat_eV_per_initial":float(a["heating_eV_per_initial"])-
                                        float(b["heating_eV_per_initial"]),
            "delta_HeII_absorbed_per_initial":float(a["HeII_absorbed_per_initial"])-
                                        float(b["HeII_absorbed_per_initial"]),
            "projected_boundary_photons":float(a["grid_boundary_photons_per_initial"])})
    if max(max_resid.values())>5e-13:
        raise ValueError(f"Native event/gas ledger exceeds 5e-13: {max_resid}")
    q0=next(r for r in threshold_sample if r["q_ref"]==0 and r["eta_neutral"]==1e-5)
    # The rho_i values are deliberately frozen; no rate-driven update of fractions.
    result={
        "schema":"he18.axbi.frozen_hhe_two_transport_ab.v1",
        "status":"FROZEN_GAS_REFERENCE_PHOTON_COLLISION_A_B_NUMERICALLY_CHECKED",
        "source_model":"Original rei_microphysics rlib; both arms use original Verner AtomicProvider/HHeModel, exponential species-resolved frozen absorption at the same physical midpoint; PROJECTED uses canonical stored grid E_i directly, COVARIANT uses reference absorb_frozen_gas and exact propagated energy",
        "transport_PROJECTED":"Driver::geometry_map at every geometric half-step, fixed-energy two-neighbor remap, direct AtomicProvider sigma(E_i) from immutable source signature cache",
        "transport_COVARIANT":"CovariantPhoton::energy_at exact conserved spatial covector, no intermediate fixed energy projection",
        "original_source_ODE_replayed":False,
        "frozen_gas":"HI=eta*nH, HeI=HeII=eta*nHe/2, HeIII fraction 1-eta; eta in {0,1e-6,1e-5}",
        "initial_photons_per_H":SOURCE_PACKET_PER_H,
        "q_ref":[-.005,0,.005],
        "native_energy_indices":[5,20,32,33],
        "native_steps":[1,32,256],
        "separate_ab_cases":108,
        "individual_lanes":216,
        "max_absolute_normalized_ledger_residuals":max_resid,
        "positive_threshold_controls_pass":True,
        "zero_opacity_controls_pass":True,
        "true_HeII_threshold_case":{
            "q_ref":0.0,"eta":1e-5,"initial_energy_eV":54.42,
            "covariant_HeII_absorbed_per_initial":0.,
            "projected_HeII_absorbed_per_initial":q0["HeII_absorb_PROJECTED_per_initial"],
            "projected_spurious_HeII_events_per_H":q0["spurious_HeII_events_per_H"],
            "projected_bound_energy_eV_per_initial":q0["binding_PROJECTED_eV_per_initial"],
            "covariant_bound_energy_eV_per_initial":q0["binding_COVARIANT_eV_per_initial"],
            "projected_heating_eV_per_initial":q0["heat_PROJECTED_eV_per_initial"],
            "covariant_heating_eV_per_initial":q0["heat_COVARIANT_eV_per_initial"],
        },
        "threshold_sample_256steps":threshold_sample,
        "serial_csv_sha256":hashfile(path),
        "parallel_csv_sha256":hashfile(second) if second else None,
        "serial_parallel_bitwise_equal_physical_columns":bool(second is not None),
        "scope_limitations":[
            "Tiny prescribed frozen neutral fractions at zbar~20 are a controlled hypothetical absorber, not predicted EoR gas state",
            "No dynamic xHII/xHeII/xHeIII, gas temperature, recombination, feedback or full photon emission is solved",
            "Reference frozen exponential absorber differs from the original production BE nonlinear chemistry solver",
            "The linked rlib full source epoch differs from original native nine-run binary; twelve tested atomic/transport function bodies were matched across original source/rlib bytes, but the reference absorber itself belongs to the separate rlib",
            "Measured artefactual HeII events are real to this reference A/B at the frozen H/He threshold; no fully coupled ionization-history causal claim is admitted",
        ],
    }
    return result,all_samples


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--serial",type=Path,required=True)
    p.add_argument("--parallel",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result, samples=analyse(args.serial,args.parallel)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in
       ("separate_ab_cases","individual_lanes","max_absolute_normalized_ledger_residuals",
        "true_HeII_threshold_case","serial_parallel_bitwise_equal_physical_columns")},indent=2))


if __name__=="__main__":main()
