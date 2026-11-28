#!/usr/bin/env python3
"""BASS_HE supplied Puchwein D1 vs native original REI-I/IGM photon-owner.

Source-owned, frozen-gas counterfactual at z=5.95, no IVP and no global
reionization-history/observational tau. Requires original frozen REI physics
source artifacts and uses exact original owner excess-heating table bytes.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile

EV_ERG = 1.602176634e-12
THRESHOLD_HEII_EV = 54.4177655282  # NIST ionization energy; not extra heat
SPECIES = ("HI", "HeI", "HeII")
GROUPS = ("G1", "G2a", "G2b", "G3")
Z_TARGET = 5.95
Y_HE = 0.079  # original source moment ratio, independently audited nodewise
ARCHIVE_SHAS = {
    "P19": "cc62c1d046be912e50e712bf2ac94d46890a472896673c2407133bca9b0e3543",
    "REI_STATE": "48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7",
    "REI_SOURCE": "4f332c7a9c21f93dcfadb0d7e4e40ef4ec7ec7f150f6d4b8b39f309560155e17",
}
REI_HEATING_GITBLOB = "2dbcd3db376fcfad27a19a992814fdd33aea547b"
P19_PROJECTION_SHA256 = "67a601ed4486a1ac03bc5ac08929219c3ed7fbd59f94ec40f442137bd8896124"
SOURCE_STATE_ARRAY_SHA256 = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def filehash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def gitblob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def ensure_source_inputs(root: Path) -> dict:
    inp = root / "inputs"
    filenames = {
        "P19": "REI_IGM_P19_D1_HIGHZ_SOURCE_20261101.zip",
        "REI_STATE": "REI_PR320_ORIGINAL_TICK160_NODE_PHYSICS.zip",
        "REI_SOURCE": "REI_IGM_TICK160_GLOBAL_PHOTON_JACOBIAN_CI_20261101.zip",
    }
    for key, filename in filenames.items():
        got = filehash(inp / filename)
        if got != ARCHIVE_SHAS[key]:
            raise ValueError(f"original {key} artifact byte SHA identity mismatch: {got}")
    calfile = inp / "REI_original_heating_moment_owner.csv"
    if gitblob(calfile.read_bytes()) != REI_HEATING_GITBLOB:
        raise ValueError("original REI heating-table Git-blob identity mismatch")
    return {key: inp / v for key, v in filenames.items()} | {"CAL": calfile}


def p19_interpolate(rows: list[dict], z: float = Z_TARGET, kind: str = "log") -> dict:
    if kind not in ("log", "linear"):
        raise ValueError("unapproved source interpolation")
    lo, hi = next((a,b) for a,b in zip(rows[:-1], rows[1:])
                  if float(a["z"]) <= z <= float(b["z"]))
    f = (z - float(lo["z"])) / (float(hi["z"]) - float(lo["z"]))
    result = {}
    for sp in SPECIES:
        result[sp] = {}
        for key in (f"Gamma_{sp}_s", f"Heat_{sp}_eV_s"):
            u, v = float(lo[key]), float(hi[key])
            if min(u,v)<=0:
                raise ValueError("published positive rate unexpectedly nonpositive")
            val = math.exp((1-f)*math.log(u)+f*math.log(v)) if kind=="log" else (1-f)*u+f*v
            result[sp]["gamma_per_neutral_s" if key.startswith("Gamma") else "excess_heat_eV_per_neutral_s"] = val
        result[sp]["mean_excess_energy_eV"] = result[sp]["excess_heat_eV_per_neutral_s"]/result[sp]["gamma_per_neutral_s"]
    return {"z":z, "interp":kind, "source_bracket":[float(lo["z"]),float(hi["z"])],"fraction":f,"species":result}


def read_original(inputs: dict) -> tuple[list[dict], list[dict],dict,dict,dict]:
    with ZipFile(inputs["P19"]) as z:
        for x in z.infolist():
            if z.read(x) is None: raise ValueError("bad source ZIP")
        data=z.read("data/P19_D1_ORIGINAL_HIGHZ_13.csv")
        if digest(data)!=P19_PROJECTION_SHA256:raise ValueError("P19 Table D1 numeric projection drift")
        p19rows=list(csv.DictReader(io.StringIO(data.decode("utf-8"))))
        if len(p19rows)!=13 or not all(float(a["z"])<float(b["z"]) for a,b in zip(p19rows[:-1],p19rows[1:])):
            raise ValueError("P19 source redshifts invalid")
    with ZipFile(inputs["REI_STATE"]) as z:
        statefile="NODEWISE_LOCAL_NEUTRAL_HAZARD_PRIMARY_46080_PHYSICAL.csv.gz"
        with gzip.open(io.BytesIO(z.read(statefile)),"rt",encoding="utf8") as f:
            state=list(csv.DictReader(f))
        if len(state)!=46080:raise ValueError("wrong original REI node count")
        for lane in ("RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR"):
            name=f"NODEWISE_{lane}_46080_PHYSICAL.csv.gz"
            with gzip.open(io.BytesIO(z.read(name)),"rt",encoding="utf8") as f:
                for i,(reference,other) in enumerate(zip(state,csv.DictReader(f))):
                    # Node CSVs contain the exact same NUMERIC strings but not identical lane names.
                    if any(other[k]!=v for k,v in reference.items() if k!="lane"):
                        raise ValueError(f"source auditor lane numerical mismatch at node {i}")
    with ZipFile(inputs["REI_SOURCE"]) as z:
        result=json.loads(z.read("physical_output/RESULT.json"))
        with gzip.open(io.BytesIO(z.read("physical_output/ORIGINAL_26EVENT_GLOBAL_PHOTON_JACOBIAN_46080.csv.gz")),"rt") as f:
            photon=list(csv.DictReader(f))
        if len(photon)!=46080 or result["state_array_sha256"]!=SOURCE_STATE_ARRAY_SHA256:
            raise ValueError("REI actual source state mismatch")
        if result["nodewise_csv_sha256"]!=digest(z.read("physical_output/ORIGINAL_26EVENT_GLOBAL_PHOTON_JACOBIAN_46080.csv.gz")):
            raise ValueError("REI original source data SHA not validated")
    with inputs["CAL"].open(newline="",encoding="utf-8") as f:
        owners=list(csv.DictReader(f))
    if len(owners)!=12:raise ValueError("original heating owner table shape mismatch")
    excess={(r["species"],r["group"]):float(r["canonical_excess_eV"]) for r in owners}
    return p19rows,state,photon,result,excess


def calculate(root: Path, out: Path) -> dict:
    inputs=ensure_source_inputs(root)
    p19,state,photon,native,excess=read_original(inputs)
    out.mkdir(parents=True,exist_ok=True)
    plog=p19_interpolate(p19,kind="log")
    plin=p19_interpolate(p19,kind="linear")
    group=[r for r in native["group_rows"] if r["case"]=="accepted_at_tick160"]
    groups=sorted(group,key=lambda x:x["group"])
    if len(groups)!=4 or [g["group"] for g in groups]!=list(range(4)):
        raise ValueError("missing original four photon-owner groups")
    if not all(abs(float(g["z_mean"])-Z_TARGET)<1e-12 for g in groups):
        raise ValueError("P19/REI proper redshift mismatch")
    source=[x for x in native["snapshots"] if x["case"]=="accepted_at_tick160"]
    if len(source)!=1 or not source[0]["exact_source_operator_inclusion"]:
        raise ValueError("source owner not admitted even as conditional diagnostic")
    source=source[0]
    moment=[float(groups[0][f"source_sum_{s}"]) for s in SPECIES]
    photo=[float(x) for x in source["photo_species_photons_per_s"]]
    gamman=[f/n for f,n in zip(photo,moment)]
    if gamman[0]<=0 or gamman[1]<=0 or gamman[2]!=0:
        raise ValueError("unexpected native original photo source state")
    if any(g["source_sum_HI"]!=moment[0] for g in groups):
        raise ValueError("native source-groups don't share global neutral moments")
    photo_g=[[float(g["current_photons_per_s"])*float(p) for p in g["species_fraction"]] for g in groups]
    for j in range(3):
        tot=math.fsum(c[j] for c in photo_g)
        if abs(tot-photo[j])>1e-10*max(abs(tot),abs(photo[j]),1e-200):
            raise ValueError("native group moment source flux not closed")
    native_heat_sp=[math.fsum(photo_g[gi][sp]*excess[(name,GROUPS[gi])] for gi in range(4))*EV_ERG
                    for sp,name in enumerate(SPECIES)]
    native_heat_total=math.fsum(native_heat_sp)
    if abs(native_heat_total-float(source["source_photoheat_erg_per_s"]))>1e-12*abs(native_heat_total):
        raise ValueError("original photon heat owner not reproducible")
    native_energy_per_event=[native_heat_sp[i]/(photo[i]*EV_ERG) if photo[i]>0 else None for i in range(3)]
    interp={k:plog if k=="log" else plin for k in ("log","linear")}
    cases={}
    for kind,p in interp.items():
        events=[moment[i]*p["species"][sp]["gamma_per_neutral_s"] for i,sp in enumerate(SPECIES)]
        heat=[moment[i]*p["species"][sp]["excess_heat_eV_per_neutral_s"]*EV_ERG for i,sp in enumerate(SPECIES)]
        cases[kind]={"absorbed_events_per_s":dict(zip(SPECIES,events)),"source_excess_heat_erg_s":dict(zip(SPECIES,heat)),
                     "total_absorbed_events_per_s":math.fsum(events),"total_excess_heat_erg_s":math.fsum(heat),
                     "ratio_formal_P19_excess_heat_to_REI":math.fsum(heat)/native_heat_total}
    columns=["node","T_K","x_HII","x_HeII","x_HeIII","N_H_all","N_He_all", "N_HI","N_HeI","N_HeII",
           "native_HI_events_s","native_HeI_events_s","native_HeII_events_s",
           "P19log_HI_events_s","P19log_HeI_events_s","P19log_HeII_events_s",
           "P19linear_HI_events_s","P19linear_HeI_events_s","P19linear_HeII_events_s",
           "native_photoheat_erg_s","P19log_excess_heat_erg_s","P19linear_excess_heat_erg_s",
           "P19log_HeII_excess_heat_erg_s","P19log_total_photoheat_per_H_erg_s"]
    field_totals={k:[] for k in ("native_HI","native_HeI","native_HeII","P19log_HI","P19log_HeI","P19log_HeII",
                                  "P19linear_HI","P19linear_HeI","P19linear_HeII","native_heat","P19log_heat","P19linear_heat")}
    frac_y=[];global_h=[];global_hei=[];global_heii=[];heat_pairs=[];temp=[];witness=[]
    dataset=out/"REI_FROZEN_46080_BASS_HE_P19_SOURCE_CROSSWALK.csv.gz"
    with dataset.open("wb") as b:
        with gzip.GzipFile(filename="",mode="wb",fileobj=b,mtime=0,compresslevel=6) as comp:
            with io.TextIOWrapper(comp,encoding="utf-8",newline="") as stream:
                wr=csv.writer(stream);wr.writerow(columns)
                for i,(s,f) in enumerate(zip(state,photon)):
                    if int(s["node"])!=i or int(f["node"])!=i:raise ValueError("source node join grain mismatch")
                    xH=(float(s["x_HII_lo"])+float(s["x_HII_hi"]))*0.5
                    xHe=(float(s["x_HeII_lo"])+float(s["x_HeII_hi"]))*0.5
                    xHe3=(float(s["x_HeIII_lo"])+float(s["x_HeIII_hi"]))*0.5
                    t=(float(s["T_K_lo"])+float(s["T_K_hi"]))*0.5
                    nHI=float(f["original_photo_HI_events_per_s"])/gamman[0]
                    nHeI=float(f["original_photo_HeI_events_per_s"])/gamman[1]
                    nH=nHI/(1-xH)
                    # Exact original owner abundance, avoiding subtraction of near-unit helium fractions.
                    nHe=nH*Y_HE
                    nHeII=nHe*xHe
                    if min(nH,nHe,nHI,nHeI,nHeII)<=0 or not all(map(math.isfinite,(nH,nHe,nHI,nHeI,nHeII))):
                        raise ValueError("source frozen physical populations invalid")
                    # Independent He I photon-owner reconstruction is retained as an audit.
                    yi=nHeI/((1-xHe-xHe3)*nH);frac_y.append(yi)
                    if abs(yi-Y_HE)>Y_HE*1e-5:
                        raise ValueError("different original helium/hydrogen abundance or source population calibration")
                    native_event=[float(f[f"original_photo_{sp}_events_per_s"]) for sp in SPECIES]
                    counts=(nHI,nHeI,nHeII)
                    formal_log=[counts[j]*plog["species"][sp]["gamma_per_neutral_s"] for j,sp in enumerate(SPECIES)]
                    formal_linear=[counts[j]*plin["species"][sp]["gamma_per_neutral_s"] for j,sp in enumerate(SPECIES)]
                    nh0=math.fsum(native_event[j]*native_energy_per_event[j] for j in (0,1))*EV_ERG
                    qlog=[counts[j]*plog["species"][sp]["excess_heat_eV_per_neutral_s"]*EV_ERG for j,sp in enumerate(SPECIES)]
                    qlin=[counts[j]*plin["species"][sp]["excess_heat_eV_per_neutral_s"]*EV_ERG for j,sp in enumerate(SPECIES)]
                    heatlog=math.fsum(qlog);heatlin=math.fsum(qlin)
                    row=[i,t,xH,xHe,xHe3,nH,nHe,nHI,nHeI,nHeII,*native_event,*formal_log,*formal_linear,
                         nh0,heatlog,heatlin,qlog[2],heatlog/nH]
                    wr.writerow([i]+[format(float(q),".17g") for q in row[1:]])
                    for key,val in zip(field_totals,(*native_event,*formal_log,*formal_linear,nh0,heatlog,heatlin)):
                        field_totals[key].append(val)
                    global_h.append(nHI);global_hei.append(nHeI);global_heii.append(nHeII)
                    heat_pairs.append((t,heatlog/nH,nh0/nH));temp.append(t)
                    if i in (0,1,2,255,4095,12000,23039,35000,46079):witness.append(row)
    if len(frac_y)!=46080:raise ValueError("incomplete owner join")
    neutral_sums=[math.fsum(global_h),math.fsum(global_hei),math.fsum(global_heii)]
    for j in range(3):
        if abs(neutral_sums[j]-moment[j])>2e-7*moment[j]:
            raise ValueError(f"original source target population sum mismatch {SPECIES[j]}")
    numerical_totals={k:math.fsum(v) for k,v in field_totals.items()}
    for s in SPECIES:
        casekey="native_"+s
        if abs(numerical_totals[casekey]-photo[SPECIES.index(s)])>2e-9*max(1,abs(photo[SPECIES.index(s)])):
            raise ValueError("native source event total mismatch")
    for k in ("P19log","P19linear"):
        for sp in SPECIES:
            i=SPECIES.index(sp)
            if abs(numerical_totals[k+"_"+sp]-cases["log" if k=="P19log" else "linear"]["absorbed_events_per_s"][sp])>2e-7*max(1,cases["log" if k=="P19log" else "linear"]["absorbed_events_per_s"][sp]):
                raise ValueError("source counterfactual total mismatch")
    if abs(numerical_totals["native_heat"]-native_heat_total)>1e-12*native_heat_total:
        raise ValueError("native heating source per-node mismatch")
    if abs(numerical_totals["P19log_heat"]-cases["log"]["total_excess_heat_erg_s"])>1e-7*cases["log"]["total_excess_heat_erg_s"]:
        raise ValueError("P19 source heat total inconsistent")
    with (out/"NINE_ORIGINAL_NODE_WITNESSES.csv").open("w",newline="") as f:
        wr=csv.writer(f);wr.writerow(columns)
        for r in witness:wr.writerow([r[0]]+[format(float(q),".17g") for q in r[1:]])
    with (out/"ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv").open("w",newline="") as f:
        wr=csv.writer(f);wr.writerow(["group","current_photons_s","species_HI_photons_s","species_HeI_photons_s","species_HeII_photons_s","external_photons_s","source_excess_heat_erg_s"])
        for gi,g in enumerate(groups):
            rates=photo_g[gi]
            h=math.fsum(rates[j]*excess[(sp,GROUPS[gi])]*EV_ERG for j,sp in enumerate(SPECIES))
            wr.writerow([GROUPS[gi]]+[format(float(x),".17g") for x in [g["current_photons_per_s"],*rates,g["external_photons_per_s"],h]])
    ratios={sp:(plog["species"][sp]["gamma_per_neutral_s"]/gamman[j] if gamman[j]>0 else None)
            for j,sp in enumerate(SPECIES)}
    numerical={"schema":"BASS_HE_REI_P19_D1_NATIVE_FROZEN_46080_SOURCE_CROSSWALK_V1",
      "project_repo":"cosmosapjw-quantum/BASS_HE","central_owner":"cosmosapjw-quantum/rei_bianchi",
      "physical_claim":"Puchwein2019 published effective homogeneous neutral-weighted UVB vs ORIGINAL REI photon-owner per-frozen-neutral counterfactual at exactly z=5.95",
      "NO_LOCAL_UVB_RATE_SUBSTITUTION":True,"NO_NEW_COSMOLOGICAL_IVP":True,"physical_nodes":len(state),"source_group_count":len(groups),"measured_observations":0,
      "source_input_immutable_sha256":ARCHIVE_SHAS,"source_table_projection_sha256":P19_PROJECTION_SHA256,
      "native_heating_owner_blob":REI_HEATING_GITBLOB,"native_source_state_array_sha256":SOURCE_STATE_ARRAY_SHA256,
      "z":Z_TARGET,"P19_log":plog,"P19_linear":plin,
      "native_global_neutral_counts":dict(zip(SPECIES,moment)),"native_gammas_per_target_s":dict(zip(SPECIES,gamman)),
      "native_source_events_per_s":dict(zip(SPECIES,photo)),"native_source_excess_erg_s":dict(zip(SPECIES,native_heat_sp)),
      "native_mean_excess_ev_per_event":dict(zip(SPECIES,native_energy_per_event)),
      "native_total_photoheat_erg_s":native_heat_total,"owner_original_total_photoheat_erg_s":source["source_photoheat_erg_per_s"],
      "P19_log_counterfactual":cases["log"],"P19_linear_counterfactual":cases["linear"],
      "P19_rate_over_native_rate_log":ratios,"original_HeII_ionizing_events_per_s":photo[2],
      "P19_log_formal_HeII_event_demand_s":cases["log"]["absorbed_events_per_s"]["HeII"],
      "P19_log_formal_HeII_threshold_energy_erg_s":cases["log"]["absorbed_events_per_s"]["HeII"]*THRESHOLD_HEII_EV*EV_ERG,
      "REI_hard_group_G3_current_photons_s":float(groups[-1]["current_photons_per_s"]),
      "current_photon_total_per_s":source["photon_current_per_s"],
      "fraction_P19_log_events_vs_REI_total_current":cases["log"]["total_absorbed_events_per_s"]/source["photon_current_per_s"],
      "interpolation_gamma_ratios_linear_over_log":{sp:plin["species"][sp]["gamma_per_neutral_s"]/plog["species"][sp]["gamma_per_neutral_s"] for sp in SPECIES},
      "helium_to_hydrogen_from_independent_owner_routes":{"median":sorted(frac_y)[len(frac_y)//2],"min":min(frac_y),"max":max(frac_y),"expected":Y_HE},
      "source_neutral_counts_recomputed":dict(zip(SPECIES,neutral_sums)),
      "source_data_csv":"REI_FROZEN_46080_BASS_HE_P19_SOURCE_CROSSWALK.csv.gz","source_data_csv_sha256":filehash(dataset),
      "source_4_group_csv":"ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv","source_4_group_csv_sha256":filehash(out/"ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv"),
      "source_witness_csv":"NINE_ORIGINAL_NODE_WITNESSES.csv","source_witness_csv_sha256":filehash(out/"NINE_ORIGINAL_NODE_WITNESSES.csv"),
      "physics_scope":"effective rates × frozen neutral targets are formal counterfactual only, NOT an admitted local photon field or true radiation history",
      "RUX02":"P19_D1_EFFECTIVE_SOURCE_ONLY_CONTEXT_CANDIDATE","RUX03":"NATIVE_HIGH_ENERGY_HEII_PHOTON_CURRENT_MISMATCH", "RUX04":"NOT_ADMITTED",
      "REI_central_reported":"28/88","REI_working_reported":"33/88","REI_fast_reported":"4/7","BASS_HE_physical_reported":"14/18","canonical_delta":0,
      "L4":False,"PRODUCTION":"HOLD","NO_MERGE":True,"NO_FORCE_PUSH":True,"AUTO_NEXT_NODE":False}
    (out/"SCIENCE_RESULTS.json").write_text(json.dumps(numerical,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({"rows":len(state),"z":Z_TARGET,"native_gamma":numerical["native_gammas_per_target_s"],
      "p19_gamma_log":{s:plog["species"][s]["gamma_per_neutral_s"] for s in SPECIES},
      "ratio":ratios,"native_heating_erg_s":native_heat_total,"p19_formal_heating_erg_s":cases["log"]["total_excess_heat_erg_s"],
      "p19_native_heat_ratio":cases["log"]["ratio_formal_P19_excess_heat_to_REI"],
      "heii_formal_photons_s":numerical["P19_log_formal_HeII_event_demand_s"],
      "csv_sha256":numerical["source_data_csv_sha256"],"REI_DAG":"28/88","BASS_HE_DAG":"14/18"},sort_keys=True))
    return numerical


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument("--out",type=Path,default=Path(__file__).resolve().parent/"results")
    args=parser.parse_args()
    calculate(args.root,args.out)