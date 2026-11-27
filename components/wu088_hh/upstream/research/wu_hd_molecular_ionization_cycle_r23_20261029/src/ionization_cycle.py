"""R23 independent photoionization cycle, not a GL2022 PES threshold.

Reconstructs Q for H+ + HD(X,v0,J2) -> D+ + H2(X,v0,J1)
using four molecular ionization steps and two rotational intervals.
Only a spectroscopy-side candidate; no admitted physical Q, kinetic rate,
real bath or energy deposition output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from decimal import Decimal, localcontext
from zipfile import ZipFile

H = Decimal("6.62607015e-34")   # 2019 SI exact J s
C = Decimal("299792458")       # exact m/s
E = Decimal("1.602176634e-19") # exact J/eV
DOIS = {
    "EI_HD_cm1":"10.1103/PhysRevA.108.022811",
    "EI_HDp_cm1":"10.1103/PhysRevLett.118.233001",
    "EI_H2_cm1":"10.1103/42c4-pc1s",
    "EI_H2p_cm1":"10.1103/PhysRevLett.118.233001",
    "H2_X_v0_J1_minus_J0_cm1":"10.1103/PhysRevLett.107.043005",
    "HD_X_v0_J2_minus_J0_kHz":"10.1140/epjd/s10053-022-00552-x"
}
EXPECTED = {
    "EI_HD_cm1": ("124568.48466", "0.00007"),
    "EI_HDp_cm1": ("131224.6841650", "0.0000006"),
    "EI_H2_cm1": ("124417.4911573", "0.0000058"),
    "EI_H2p_cm1": ("131058.1219937", "0.0000006"),
    "H2_X_v0_J1_minus_J0_cm1": ("118.48684", "0.00010"),
    "HD_X_v0_J2_minus_J0_kHz": ("8006533168", "26")
}
SHA_R21 = "5ace176fdba1b1ed01cedbd11e381b98ee242475ef1a401d89dcfcf0b7a3d220"
SHA_R22 = "5d92267615c91e9c34c9c496956bdf58473ee41f1db6e58ccbbbfbf4fd95477c"
SHA_PDF = "a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754"
SOURCE_SCHEMA = "wu.r23.molecular_ionization_cycle_sources.v1"
SOURCE_TARGET = "H+ + HD(X,v=0,J=2) -> D+ + H2(X,v=0,J=1,ortho)"

class ContractError(ValueError):
    pass


def strict_literal_record(path: Path) -> tuple[dict, str]:
    raw = Path(path).read_bytes()
    r = json.loads(raw)
    if not isinstance(r, dict) or r.get("schema") != SOURCE_SCHEMA or r.get("target_reaction") != SOURCE_TARGET:
        raise ContractError("wrong schema or target ionic state labels")
    if r.get("physical_energy_source_admitted") is not False or r.get("GL2022_PES_native_threshold_cm1") is not None:
        raise ContractError("PES state threshold improperly issued")
    vals = {}
    for k in ("EI_HD_cm1", "EI_HDp_cm1", "EI_H2_cm1", "EI_H2p_cm1"):
        vals[k] = r["molecular_ionization"][k]
    for k in ("H2_X_v0_J1_minus_J0_cm1", "HD_X_v0_J2_minus_J0_kHz"):
        vals[k] = r["rotation"][k]
    for key, row in vals.items():
        v, u = EXPECTED[key]
        if not isinstance(row, dict) or row.get("value") != v or row.get("quoted_unc") != u or row.get("doi") != DOIS[key]:
            raise ContractError("source DOI/literal/uncertainty mismatch: "+key)
        if not Decimal(v).is_finite() or not Decimal(u).is_finite() or Decimal(u)<0:
            raise ContractError("nonfinite or negative source literal")
    s = r.get("status",{})
    for k in ("physical_Q_J_per_event","physical_bath_heat","source_rate_uncertainty","reverse_rate","REC_CR_owner_ACK"):
        if s.get(k,"missing") is not None:
            raise ContractError("false authority field "+k)
    if s.get("production") != "NOT_ISSUED" or s.get("HH_R10") != "OFF" or s.get("L4") is not False or s.get("canonical_WU_DAG") != "34/49":
        raise ContractError("production/DAG guard mismatch")
    z = r.get("independent_comparison",{})
    if z.get("R22_spectroscopic_dissociation_cycle_source_zip_sha256")!=SHA_R22 or z.get("R21_legacy_source_zip_sha256")!=SHA_R21 or z.get("GL2022_original_supplement_sha256")!=SHA_PDF or z.get("R21_git_head")!="fd351d0ff97ef0d7a9cf710bdecad922af7e885e":
        raise ContractError("original source/commit lineage mismatch")
    if r.get("PES_provenance",{}).get("exact_GL2022_isotope_offset_issued") is not False:
        raise ContractError("source PES native offset not established")
    return r,hashlib.sha256(raw).hexdigest()


def verify_archives(r21_zip: Path, r22_zip: Path) -> dict:
    expected=[(Path(r21_zip),SHA_R21),(Path(r22_zip),SHA_R22)]
    for p,sha in expected:
        if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
            raise ContractError("original ZIP byte identity mismatch: "+p.name)
    with ZipFile(r21_zip) as z:
        if z.testzip() is not None:
            raise ContractError("R21 source archive CRC failed")
        pdf=z.read("ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf")
        if len(pdf)!=273554 or hashlib.sha256(pdf).hexdigest()!=SHA_PDF:
            raise ContractError("GL2022 original PDF hash/size mismatch")
    with ZipFile(r22_zip) as z:
        if z.testzip() is not None:
            raise ContractError("R22 source archive CRC failed")
        ref=json.loads(z.read("results/SPECTROSCOPY_RESULT.json"))
        if ref.get("candidate_Q_release_meV_per_event") is None or ref.get("physical_Q_event_J_per_event") is not None:
            raise ContractError("old R22 reference candidate authority mismatch")
    return {"R21_zip_sha256":SHA_R21,"R22_zip_sha256":SHA_R22,"GL2022_supp_pdf_sha256":SHA_PDF,"GL2022_pdf_size":len(pdf),"R22_ref_candidate_meV":ref["candidate_Q_release_meV_per_event"]}


def compute(record: dict, data_sha: str, *, admit_physical=False) -> dict:
    if admit_physical:
        raise ContractError("GL2022 PES-native threshold and owner not authenticated")
    with localcontext() as ctx:
        ctx.prec=85
        m=record["molecular_ionization"]
        rot=record["rotation"]
        get=lambda k: Decimal(m[k]["value"])
        ion= get("EI_HD_cm1")+get("EI_HDp_cm1")-get("EI_H2_cm1")-get("EI_H2p_cm1")
        r_h2=Decimal(rot["H2_X_v0_J1_minus_J0_cm1"]["value"])
        r_hd=Decimal(rot["HD_X_v0_J2_minus_J0_kHz"]["value"])*Decimal(1000)/(C*100)
        delta=ion+r_h2-r_hd
        q_mev=-(delta*H*C*Decimal(100)*Decimal(1000)/E)
        old=Decimal(record["independent_comparison"]["R22_spectroscopic_dissociation_cycle_cm1"])
        residual=delta-old
        # These are marginal quoted uncertainties. The sum is an INPUT SENSITIVITY L1 diagnostic,
        # never a certified interval or confidence statement because source laws/covariances unknown.
        unc= (sum((Decimal(m[k]["quoted_unc"]) for k in ("EI_HD_cm1","EI_HDp_cm1","EI_H2_cm1","EI_H2p_cm1")), Decimal(0))
              +Decimal(rot["H2_X_v0_J1_minus_J0_cm1"]["quoted_unc"])
              +Decimal(rot["HD_X_v0_J2_minus_J0_kHz"]["quoted_unc"])*Decimal(1000)/(C*100))
        if delta<=0 or abs(residual)>=Decimal("0.00001"):
            raise ContractError("unexpected sign or source-candidate discrepancy")
        return {
            "schema":"wu.r23.molecular_ionization_cycle_result.v1",
            "source_literal_sha256":data_sha,
            "target_reaction":SOURCE_TARGET,
            "method":"independent molecular ionization cycle, exact printed-decimal arithmetic",
            "components_cm1":{"molecular_ground_ionic_difference":str(ion),"H2_rot_J1":str(r_h2),"HD_rot_J2":str(r_hd)},
            "delta_E_cm1":str(delta),"Q_spectroscopy_candidate_meV":str(q_mev),
            "Q_spectroscopy_candidate_J_per_event":str(q_mev*E/Decimal(1000)),
            "R22_dissociation_cycle_cm1":str(old),"inter_cycle_residual_cm1":str(residual),
            "marginal_uncertainty_L1_sensitivity_cm1_NOT_CONFIDENCE":str(unc),
            "uncertainty_type":"NOT_COVARIANCE_ADJUSTED_NOT_CONFIDENCE_INTERVAL_NOT_CERTIFIED_BOUND",
            "state_energy_source":"EXTERNAL_SPECTROSCOPY_CANDIDATE_NOT_GL2022_PES",
            "PES_native_threshold_cm1":None,"physical_Q_event_J_per_event":None,
            "physical_bath_delta_J_per_ref_m3":None,"real_rate_uncertainty":None,
            "reverse_rate":None,"owner_ACK":None,"L4":False,"HH_R10":"OFF",
            "production":"NOT_ISSUED","canonical_DAG":"34/49_UNCHANGED",
            "R6_distinct_author":"NOT_RUN","C9_distinct_author":"NOT_RUN",
            "refutation_target":"GL2022 BO/PES asymptotic difference and isotope offset not source authenticated"
        }


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source-json",type=Path,required=True)
    a.add_argument("--r21-zip",type=Path,required=True)
    a.add_argument("--r22-zip",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args(argv)
    record,digest=strict_literal_record(args.source_json)
    r=compute(record,digest)
    r["archive_integrity"]=verify_archives(args.r21_zip,args.r22_zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as h:
        json.dump(r,h,ensure_ascii=False,indent=2);h.write("\n")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
