#!/usr/bin/env python3
"""Same-author independent numerical path: 120000-bin dlnE midpoint x frozen REI counts.
Does not import the primary bridge code. Original PW19 spectrum and native REI
accepted neutral counts are verified by independent stored identities.
"""
from __future__ import annotations
import hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
import independent_audit as s
EV=1.602176634e-12
def run():
    s.audit()
    source=json.loads((HERE/"INDEPENDENT_SOURCE_AUDIT.json").read_text())
    output=json.loads((HERE/"NATIVE_T160_PW19_SPECTRAL_DONOR_PHYSICS.json").read_text())
    report=json.loads((REPO/"research/rei_igm_p19_native_receiver_20261101/results/SCIENCE_RESULTS.json").read_text())
    if report["native_source_state_array_sha256"]!="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01":
        raise ValueError("REI accepted state changed")
    native=report["native_global_neutral_counts"]
    primary=output["source_scenarios"]["z5p95_log"]
    rows={}
    for species in ("HI","HeI","HeII"):
        if output["neutral_counts"][species]!=native[species]:
            raise ValueError("BASS_HE source neutral counts mismatch")
        n=native[species]
        r=source["results"][species]
        expected_count=n*r["independent_midpoint_gamma"]
        expected_heat=n*r["independent_midpoint_heat_eV_s"]*EV
        expected_bind=expected_count*{"HI":13.598434599702,"HeI":24.587389011,"HeII":54.41776}[species]*EV
        model=primary["species"][species]
        count_rel=abs(expected_count-model["photoionizations_per_s"])/expected_count
        heat_rel=abs(expected_heat-model["photo_excess_heat_erg_s"])/expected_heat
        if count_rel>0.00030 or heat_rel>0.00030:
            raise AssertionError((species,count_rel,heat_rel))
        energy_rel=abs(r["energy_absorption_erg_per_atom_s"]*n -
                       (model["photo_excess_heat_erg_s"]+model["ionization_binding_energy_storage_erg_s"]))/(r["energy_absorption_erg_per_atom_s"]*n)
        if energy_rel>0.00030:raise AssertionError(("photon energy closure",species,energy_rel))
        rows[species]={"independent_events_s":expected_count,
                       "primary_events_s":model["photoionizations_per_s"],
                       "relative_events_disagreement":count_rel,
                       "relative_heat_disagreement":heat_rel,
                       "relative_absorbed_energy_disagreement":energy_rel}
    # Independent dual from exact serialized source rather than primary computation.
    from fractions import Fraction as F
    c=json.loads((REPO/"research/rei_rux04_p19_native_source_cone_20261101/source/REI_FOUR_GROUP_SOURCE_SHARES.json").read_text())
    q=[(F(v["p"]["HeI"]),F(v["p"]["HI"])) for v in c["rows"]]
    witness=min(a/b for a,b in q if b>0)
    target=F(str(rows["HeI"]["independent_events_s"]))/F(str(rows["HI"]["independent_events_s"]))
    if not (witness>target and witness>F("0.69") and target<F("0.031")):
        raise AssertionError("Native four-group source current-only incompatibility not verified")
    summary={"status":"PASS_SAME_AUTHOR_DIFFERENT_SPECTRAL_MIDPOINT_AND_NATIVE_DUAL",
             "methods":"120k uniform dlnE midpoint vs native 16-substep segmented Simpson; Fraction exact native group ratio",
             "native_cells_reused":46080,"z":5.95,"rows":rows,
             "independent_target_HeI_over_HI":float(target),
             "fractional_native_min_HeI_over_HI":float(witness),
             "source_hash":hashlib.sha256((HERE/"source_original_v1.zip").read_bytes()).hexdigest(),
             "canonical_DAG":"28/88_REPORTED","BASS_HE_DAG":"14/18_REPORTED","canonical_delta":0,
             "independent_author":"NOT_RUN"}
    target_file=HERE/"INDEPENDENT_NATIVE_AUDIT.json"
    target_file.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print(json.dumps(summary,sort_keys=True))
    print("AUDIT_SHA256",hashlib.sha256(target_file.read_bytes()).hexdigest())
if __name__=="__main__":run()
