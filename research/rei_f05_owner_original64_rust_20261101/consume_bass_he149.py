#!/usr/bin/env python3
"""REI project-owner bounded ORIGINAL native tick160 photochannel admission.

Reads immutable BASS_HE #149 native H/He four-group original F05 output;
recomputes every 12-channel χ, excess-heat identity and species/group/total
conservation, emits REI-owned original photon source diagnostic, not a new IVP.
No cross-clock mix with original first [0,64] interval or tick161.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from decimal import Decimal,localcontext
from pathlib import Path
SOURCE_SHA="d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8"
SRC_HEAD="64e121a1980358134e59b303414c2d54964360de"
SRC_BLOB="6953e9e343c483ae3ba442aa0c752f795e5ae7e2"
TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
CHI={"HI":Decimal("13.598434599702"),"HeI":Decimal("24.587389011"),"HeII":Decimal("54.417760")}
EV=Decimal("1.602176634e-12")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def D(x):return Decimal(str(x))
def intersects(a,b):
    return a[0]<=b[1] and b[0]<=a[1]
def m(x):return (D(x[0])+D(x[1]))/2
def main(source,out):
    if sha(source)!=SOURCE_SHA:raise ValueError("BASS_HE149_SOURCE_SHA")
    j=json.loads(Path(source).read_text())
    if j["schema"]!="BASS_HE_SOURCE_NATIVE_F05_T160_PHOTON_BINDING_ENERGY_V1" or j["nodes_read"]!=46080:
        raise ValueError("BASS_HE149_NATIVE_SCHEMA")
    if (j["original_REI_archive_sha256"]!=TAR or j["original_REI_array_sha256"]!=STATE or
        j["original_accepted_tick"]!="160/131072" or j["official_tick161"] is not False or
        j["production"]!="HOLD"):
        raise ValueError("REI_ORIGINAL_SOURCE_BOUNDARY")
    if len(j["source_photochannels"])!=12 or len(j["native_four_groups"])!=4:
        raise ValueError("REI_ORIGINAL_FOUR_GROUP_CHANNELS")
    pergroup={i:[] for i in range(4)}
    species={"HI":[],"HeI":[],"HeII":[]}
    for row in j["source_photochannels"]:
        g=row["group"];s=row["species"]
        if g not in pergroup or s not in species:raise ValueError("BAD_NATIVE_GROUP_SPECIES")
        lo,hi=(D(x) for x in row["photo_events_per_s"])
        if not(lo<=hi):raise ValueError("INVALID_ORIGINAL_INTERVAL")
        # Outward interval representations of exact zero can include
        # negative binary subnormal endpoints. Do not promote to an actual
        # negative photon count. For the physical moment use nonnegative core.
        physical_low=max(Decimal(0),lo);physical_high=max(Decimal(0),hi)
        chi=CHI[s]
        excess=D(row["source_excess_eV"])
        if excess<0:raise ValueError("INVALID_PHOTOELECTRON_EXCESS")
        expected_binding=[physical_low*chi*EV,physical_high*chi*EV]
        expected_heat=[physical_low*excess*EV,physical_high*excess*EV]
        published_binding=[D(x) for x in row["chemical_binding_power_erg_s"]]
        published_heat=[D(x) for x in row["primary_heat_power_erg_s"]]
        if not intersects(expected_binding,published_binding):
            raise AssertionError(f"CHEM_BINDING_NOT_EQUIVALENT {g} {s}")
        if not intersects(expected_heat,published_heat):
            raise AssertionError(f"EXCESS_HEAT_NOT_EQUIVALENT {g} {s}")
        energy=[expected_binding[0]+expected_heat[0],expected_binding[1]+expected_heat[1]]
        pub_material=[D(x) for x in row["material_electronic_power_erg_s"]]
        if not intersects(energy,pub_material):
            raise AssertionError(f"PHOTOENERGY_INCOMPATIBLE {g} {s}")
        pergroup[g].append((row["photo_events_per_s"],row["chemical_binding_power_erg_s"],row["primary_heat_power_erg_s"]))
        species[s].append((row["photo_events_per_s"],row["chemical_binding_power_erg_s"],row["primary_heat_power_erg_s"]))
    def sum_intervals(rows,key):
        return [sum((D(x[key][0]) for x in rows),Decimal(0)),
                sum((D(x[key][1]) for x in rows),Decimal(0))]
    for s in species:
        rows=[x for x in j["source_photochannels"] if x["species"]==s]
        src=j["species_aggregate"][s]
        for field,a in (("photo_events_per_s","photo_events_per_s"),
                        ("chemical_binding_power_erg_s","chemical_binding_power_erg_s"),
                        ("primary_heat_power_erg_s","primary_heat_power_erg_s")):
            if not intersects(sum_intervals(rows,a),[D(x) for x in src[field]]):
                raise AssertionError(f"SPECIES_{s}_{field}")
    for g in pergroup:
        rows=[x for x in j["source_photochannels"] if x["group"]==g]
        src=j["native_four_groups"][g]
        for field,a in (("resolved_rate_per_s","photo_events_per_s"),
                        ("binding_power_erg_s","chemical_binding_power_erg_s"),
                        ("primary_photoheat_erg_s","primary_heat_power_erg_s")):
            if not intersects(sum_intervals(rows,a),[D(x) for x in src[field]]):
                raise AssertionError(f"GROUP_{g}_{field}")
    allrows=j["source_photochannels"]
    for field,a in (("total_original_photoionization_per_s","photo_events_per_s"),
                    ("total_chemical_binding_power_erg_s","chemical_binding_power_erg_s"),
                    ("total_primary_heat_power_erg_s","primary_heat_power_erg_s")):
        if not intersects(sum_intervals(allrows,a),[D(x) for x in j[field]]):
            raise AssertionError(f"TOTAL_{field}")
    B=[D(x) for x in j["total_chemical_binding_power_erg_s"]]
    Q=[D(x) for x in j["total_primary_heat_power_erg_s"]]
    F=[D(x) for x in j["total_material_electronic_power_erg_s"]]
    if not intersects([B[0]+Q[0],B[1]+Q[1]],F):
        raise AssertionError("PHOTON_ENERGY_CHEM_PLUS_HEAT")
    rate=[D(x) for x in j["total_original_photoionization_per_s"]]
    if not(B[0]>0 and Q[0]>0 and rate[0]>0):raise AssertionError("ORIGINAL_SOURCE_POSITIVE")
    binding_share=[B[0]/(B[0]+Q[1]),B[1]/(B[1]+Q[0])]
    rec={"schema":"REI_OWNER_F05_ORIGINAL_T160_BASS_HE149_ACCEPTED_PHOTOCHANNEL_V1",
        "source":"cosmosapjw-quantum/BASS_HE#149","source_head":SRC_HEAD,
        "source_github_blob_sha1":SRC_BLOB,
        "source_physics_ci":{"run_id":41317989284,"conclusion":"success"},
        "source_science_json_sha256":SOURCE_SHA,
        "original_REI_tar_sha256":TAR,"original_REI_accepted_state_sha256":STATE,
        "original_frozen_tick":"160/131072","original_cells":46080,
        "original_groups":4,"original_channels_checked":12,
        "original_source_times_not_mixed_with_rei_0_to_64":True,
        "consumed_original_photoevents_per_s":[float(rate[0]),float(rate[1])],
        "consumed_chemical_binding_power_erg_s":[float(B[0]),float(B[1])],
        "consumed_primary_photoelectron_heat_power_erg_s":[float(Q[0]),float(Q[1])],
        "binding_fraction_of_binding_plus_primary_heat":[float(v) for v in binding_share],
        "owner_admission":"PROMOTE_FOR_SPECIFIED_USE_ORIGINAL_F05_T160_PHOTOCHANNEL_DIAGNOSTIC",
        "not_claimed":["net_chemical_dBdt","net_gas_dUdt","photon_occupation_equivalence",
            "tick160_to_161_accepted","full_rust_26event_solver","CMB_observable"],
        "central_DAG":"28/88","working_DAG":"33/88","fast_DAG":"4/7",
        "canonical_delta":0,"production":"HOLD","native_subagent":"NOT_RUN"}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"accepted":rec["owner_admission"],"channels":12,
        "B_erg_s":rec["consumed_chemical_binding_power_erg_s"],
        "Q_erg_s":rec["consumed_primary_photoelectron_heat_power_erg_s"],
        "fraction":rec["binding_fraction_of_binding_plus_primary_heat"],
        "owner_output_sha256":sha(out)},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with localcontext() as dc:
        dc.prec=60
        main(a.source,a.out)
