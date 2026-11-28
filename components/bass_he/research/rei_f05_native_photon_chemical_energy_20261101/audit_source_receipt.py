#!/usr/bin/env python3
"""Independent source-receipt cross-check of original REI #355 group allocation.
Only compares already source-derived receipts, NOT replay of original 26-event kernel.
"""
import argparse,hashlib,json,math
from pathlib import Path
from decimal import Decimal,localcontext

SOURCE_ORIGINAL_SHA="5f050d6c57cfc06a80af5e02c2c64f2cba25776f618dd2b3890cbfa4dcb57fd9"
SPECIES=("HI","HeI","HeII")
SOURCE_FIELDS=("HI_opacity_share_interval","HeI_opacity_share_interval","HeII_opacity_share_interval")
EV=Decimal("1.602176634e-12")
CHI=(Decimal("13.598434599702"),Decimal("24.587389011"),Decimal("54.41776"))

def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dec(x):return Decimal(str(x))
def bounds_mul(a,b):
    vals=[dec(x)*dec(y) for x in a for y in b]
    return min(vals),max(vals)
def encloses_with_roundoff(a,b,rtol=Decimal("4e-15")):
    """Two independent interval results need overlap, allowing <=4e-15 source float serialization."""
    xa,xb=map(dec,a);ya,yb=map(dec,b)
    tol=rtol*max(abs(xa),abs(xb),abs(ya),abs(yb),Decimal("1e-290"))
    return xa<=yb+tol and ya<=xb+tol
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original",type=Path,required=True)
    ap.add_argument("--derived",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    assert file_sha(args.original)==SOURCE_ORIGINAL_SHA,"ORIGINAL_REI355_RECEIPT_DRIFT"
    ref=json.loads(args.original.read_text())
    out=json.loads(args.derived.read_text())
    assert ref["original_accepted_tick"]==out["original_accepted_tick"]=="160/131072"
    assert ref["original_archive_sha256"]==out["original_REI_archive_sha256"]
    assert ref["original_state_sha256"]==out["original_REI_array_sha256"]
    assert ref["original_kernel_sha256"]==out["original_REI_native_kernel_sha256"]
    assert ref["original_continuous_rhs_sha256"]==out["original_REI_RHS_sha256"]
    assert ref["original_nodes"]==out["nodes_read"]==46080
    assert len(out["source_photochannels"])==12 and len(out["native_four_groups"])==4
    rows={(int(x["group"]),x["species"]):x for x in out["source_photochannels"]}
    with localcontext() as c:
        c.prec=70
        for group in ref["photon_groups"]:
            g=int(group["group"])
            J=group["original_j_photon_current_native_interval"]
            ours=out["native_four_groups"][g]
            assert encloses_with_roundoff(group["resolved_photon_rate_original_units_interval"],ours["resolved_rate_per_s"])
            assert encloses_with_roundoff(group["primary_photoheat_erg_s_interval"],ours["primary_photoheat_erg_s"])
            for i,s in enumerate(SPECIES):
                x=rows[(g,s)]
                JQ=bounds_mul(J,group[SOURCE_FIELDS[i]])
                assert encloses_with_roundoff([float(JQ[0]),float(JQ[1])],x["photo_events_per_s"]),f"GROUP_SPECIES_RATE_{g}_{s}"
                if s=="HeII" and g==3: assert abs(x["photo_events_per_s"][1])<1e-320
                if not x["supported"]: assert max(map(abs,x["photo_events_per_s"]))<1e-320
                chi=CHI[i]*EV
                E=bounds_mul([float(JQ[0]),float(JQ[1])],[float(chi),float(chi)])
                assert encloses_with_roundoff([float(E[0]),float(E[1])],x["chemical_binding_power_erg_s"]),f"GROUP_SPECIES_ENERGY_{g}_{s}"
    assert encloses_with_roundoff(ref["original_native_46080_node_resolved_rate_total_interval"],out["total_original_photoionization_per_s"])
    for s in SPECIES:
        assert out["direct_native_overlap"]["species"][s]
    assert encloses_with_roundoff(ref["original_native_46080_node_primary_heat_erg_s_interval"],out["total_primary_heat_power_erg_s"])
    assert out["direct_native_overlap"]["heat"]
    assert out["three_moment_finite_difference_max_scaled_error"]<1e-7
    assert out["canonical_delta"]==0 and out["production"]=="HOLD"
    assert not out["photon_transport_admitted"] and not out["official_tick161"]
    assert out["native_G3_photon_current_upper_subnormal"]<1e-320
    receipt={"schema":"BASS_HE_REI355_NATIVE_GROUP_ENERGY_INDEPENDENT_RECEIPT_V1",
      "original_ref_sha256":SOURCE_ORIGINAL_SHA,"derived_sha256":file_sha(args.derived),
      "original_ref_group_count":len(ref["photon_groups"]),
      "source_material_energy_rate_pairs_checked":12,
      "direct_original_field_overlap":"4_OF_4_PASS",
      "source_receipt_group_overlap":"4_OF_4_PASS",
      "source_receipt_species_rate_and_binding_interval_overlap":"12_OF_12_PASS",
      "moment_derivative_finite_difference":"PASS_SCOPED",
      "canonical_delta":0,
      "scope":"INDEPENDENT_ALGORITHM_SAME_AUTHOR_NOT_FULL_ORIGINAL_SOURCE_REPLAY",
      "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN"}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS_SOURCE_RECEIPT_INDEPENDENT_SCOPED",
        "source_checks":12,"receipt_sha256":file_sha(args.out)},sort_keys=True))
if __name__=="__main__":main()
