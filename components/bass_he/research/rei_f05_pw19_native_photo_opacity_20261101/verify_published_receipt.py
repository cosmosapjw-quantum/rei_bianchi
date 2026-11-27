#!/usr/bin/env python3
"""Published derived-receipt replay only. DOES NOT replace full original REC191 readback.
Uses stdlib to validate every emitted H/He proper-opacity row, positivity, units,
the source-conditional energy bands and non-promotion status.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPECIES=("HI","HeI","HeII")
BANDS=("HI_only","HI_HeI","all_three")

def run():
    receipt=json.loads((HERE/"results/SCIENCE_RESULT.json").read_text())
    if (receipt["node_count"]!=46080 or receipt["central_DAG"]!="28/88_REPORTED"
        or receipt["BASS_HE_physical_DAG"]!="14/18_REPORTED"
        or receipt["official_tick161"] is not False or receipt["canonical_delta"]!=0
        or receipt["production"]!="HOLD" or receipt["original_owner_mutation"]):
        raise AssertionError("derived-source claim promoted or inconsistent")
    path=HERE/"results/ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz"
    if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt["data_csv_sha256"]:
        raise AssertionError("published 46080-cell physical CSV byte corruption")
    means=[receipt["bands"][b]["sigma_mean_cm2"] for b in BANDS]
    volsum=0.; heii=0.; opacity=0.;n=0
    with gzip.open(path,"rt") as file:
        for row in csv.DictReader(file):
            if int(row["node"])!=n:raise AssertionError(("source cell order",n))
            V=float(row["volume_cm3"])
            if not math.isfinite(V) or V<=0:raise AssertionError("proper native cell volume")
            volsum+=V
            lo=[float(row[f"n_{s}_lo_cm3"]) for s in SPECIES]
            hi=[float(row[f"n_{s}_hi_cm3"]) for s in SPECIES]
            if any(not (0<=a<=b and math.isfinite(b)) for a,b in zip(lo,hi)):
                raise AssertionError(("source native population",n))
            mid=[(a+b)*.5 for a,b in zip(lo,hi)]
            for band,mu in zip(BANDS,means):
                k0=sum(lo[i]*mu[i] for i in range(3))
                k1=sum(hi[i]*mu[i] for i in range(3))
                tab0=float(row[f"{band}_kappa_lo_inv_cm"])
                tab1=float(row[f"{band}_kappa_hi_inv_cm"])
                if not (0<k0<=k1 and math.isclose(tab0,k0,rel_tol=3e-12)
                        and math.isclose(tab1,k1,rel_tol=3e-12)):
                    raise AssertionError(("photo opacity cell closure",n,band))
                if not (math.isclose(1/float(row[f"{band}_mfp_lo_cm"]),k1,rel_tol=3e-12)
                        and math.isclose(1/float(row[f"{band}_mfp_hi_cm"]),k0,rel_tol=3e-12)):
                    raise AssertionError(("proper photon MFP",n,band))
                if float(row[f"{band}_CV2_mid"])<-1e-14:
                    raise AssertionError(("physical spectral variance",n,band))
            m=means[2]
            hm=mid[2]*m[2];km=sum(mid[i]*m[i] for i in range(3))
            s=float(row["HeII_hard_opacity_fraction_mid"])
            if not (0<=s<=1 and math.isclose(s,hm/km,rel_tol=3e-12)):
                raise AssertionError(("HeII hard photo-opacity",n))
            heii+=V*hm;opacity+=V*km
            n+=1
    if n!=46080 or not math.isclose(volsum,receipt["native_total_proper_volume_cm3"],rel_tol=1e-13):
        raise AssertionError("complete source volume and node count")
    hard=heii/opacity
    if not math.isclose(hard,receipt["helium_HeII_hard_band_volume_weighted_share"],rel_tol=2e-12):
        raise AssertionError("native hard HeII opacity fraction mismatch")
    for diagnostic in receipt["Jensen_one_local_mfp_diagnostics"]:
        if not (math.isclose(diagnostic["grey_transmission"],math.exp(-1),rel_tol=1e-14)
                and diagnostic["grey_transmission"]<=diagnostic["frequency_resolved_transmission"]<=1):
            raise AssertionError("Jensen finite-column counterexample")
    print("PASS_PUBLISHED_RECEIPT_ONLY",json.dumps({"rows":n,
        "hard_HeII_volume_weighted_fraction":hard,"original_native_volume_cm3":volsum,
        "original_CSV_sha256":receipt["data_csv_sha256"],
        "central":"28/88_REPORTED","BASS_HE":"14/18_REPORTED","canonical_delta":0}))
    return True
if __name__=="__main__":run()
