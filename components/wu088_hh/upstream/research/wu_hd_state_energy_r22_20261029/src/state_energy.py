"""R22 provenance-locked independent spectroscopy energy candidate.

Physically corrected spectroscopy is NOT the authenticated GL2022 SQM PES
energy convention; this package never emits an admitted physical reaction Q.
"""
from __future__ import annotations
from decimal import Decimal, localcontext, InvalidOperation
import json
from pathlib import Path

C_CM_PER_S=Decimal("29979245800")  # exact SI c *100
H_J_S=Decimal("6.62607015e-34")  # exact SI
EV_J=Decimal("1.602176634e-19")  # exact SI
TERMS=("ionization_H_cm1","ionization_D_cm1","dissociation_HD_00_cm1",
       "dissociation_H2_00_cm1","rotation_H2_01_cm1","rotation_HD_02_kHz")
LABEL="H+ + HD(v=0,j=2) -> D+ + H2(v=0,j=1)"
# Frozen exact literal+DOI+publication-year reference inventory. Updating an
# input requires a source review, not merely changing a JSON field.
EXPECTED_SOURCE={
 "ionization_H_cm1":("109678.77174307","0.00000010",2023,"https://doi.org/10.1103/PhysRevA.108.022811"),
 "ionization_D_cm1":("109708.61455294","0.00000017",2023,"https://doi.org/10.1103/PhysRevA.108.022811"),
 "dissociation_HD_00_cm1":("36405.78253","0.00007",2023,"https://doi.org/10.1103/PhysRevA.108.022811"),
 "dissociation_H2_00_cm1":("36118.0696646","0.0000058",2026,"https://doi.org/10.1103/42c4-pc1s"),
 "rotation_H2_01_cm1":("118.48684","0.00010",2011,"https://doi.org/10.1103/PhysRevLett.107.043005"),
 "rotation_HD_02_kHz":("8006533168","26",2022,"https://doi.org/10.1140/epjd/s10053-022-00552-x"),
}

EXPECTED_STATES={
 "entrance":"HD(X, v=0, J=2), H+(1s ion)",
 "exit":"H2(X, v=0, J=1, ortho), D+(1s ion)",
}
EXPECTED_LOCKS={
 "GL2022_DOI":"10.1063/5.0128598",
 "GL2022_supp_pdf_sha256":"a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754",
 "R21_HEAD":"fd351d0ff97ef0d7a9cf710bdecad922af7e885e",
 "R21_SOURCE_ZIP_SHA256":"5ace176fdba1b1ed01cedbd11e381b98ee242475ef1a401d89dcfcf0b7a3d220",
}

class SpectroscopyContractError(ValueError):
    pass


def _dec(s, kind):
    if type(s) is not str:
        raise SpectroscopyContractError(f"{kind} requires an explicitly written decimal string")
    try:
        value=Decimal(s)
    except InvalidOperation as e:
        raise SpectroscopyContractError(f"invalid {kind}") from e
    if not value.is_finite() or value < 0:
        raise SpectroscopyContractError(f"{kind} must be finite nonnegative")
    return value


def evaluate_candidate(data: dict) -> dict:
    """Exact-decimal candidate decomposition, no rate/evolution/bath mutation.

    Validates the expected source identity but intentionally does not claim that
    a bibliographic link authenticates the underlying SQM PES energy zero.
    """
    if type(data) is not dict or data.get("schema") != "wu.r22.spectroscopic_state_energy_inputs.v1":
        raise SpectroscopyContractError("wrong source schema")
    if data.get("reaction") != LABEL or data.get("source_native_GL2022_energy_zero_authenticated") is not False:
        raise SpectroscopyContractError("source-specific channel/PES hold mismatch")
    if data.get("production_admission") is not False:
        raise SpectroscopyContractError("no production admission")
    if data.get("state_labels") != EXPECTED_STATES:
        raise SpectroscopyContractError("state-resolved label binding mismatch")
    source=data.get("source_locks")
    if source != EXPECTED_LOCKS:
        raise SpectroscopyContractError("immutable PDF/ZIP/HEAD source lock mismatch")
    q=data.get("quantities")
    if type(q) is not dict or set(q)!=set(TERMS):
        raise SpectroscopyContractError("exact six source quantities required")
    for name in TERMS:
        row=q[name]
        if type(row) is not dict or not row.get("url","").startswith("https://doi.org/"):
            raise SpectroscopyContractError("source DOI provenance required")
        if (row.get("value"),row.get("quoted_abs_uncertainty"),row.get("year"),row.get("url")) != EXPECTED_SOURCE[name]:
            raise SpectroscopyContractError("spectroscopy primary literal or DOI provenance mismatch")
    with localcontext() as ctx:
        ctx.prec=60
        v={name:_dec(q[name]["value"],name) for name in TERMS}
        u={name:_dec(q[name]["quoted_abs_uncertainty"],name+" uncertainty") for name in TERMS}
        rot_hd=v["rotation_HD_02_kHz"]*Decimal(1000)/C_CM_PER_S
        rot_hd_unc=u["rotation_HD_02_kHz"]*Decimal(1000)/C_CM_PER_S
        parts={
          "isotopic_atomic_ionization_cm1":v["ionization_D_cm1"]-v["ionization_H_cm1"],
          "molecular_ground_dissociation_cm1":v["dissociation_HD_00_cm1"]-v["dissociation_H2_00_cm1"],
          "state_rotational_correction_cm1":v["rotation_H2_01_cm1"]-rot_hd,
        }
        deltaE=sum(parts.values())  # product minus reactant, positive=endothermic
        q_cm1=-deltaE
        q_J=q_cm1*H_J_S*C_CM_PER_S
        q_meV=q_J/EV_J*Decimal(1000)
        uncert_abs_sum_cm1=sum(u[name] for name in TERMS if name!="rotation_HD_02_kHz")+rot_hd_unc
        q_unc_meV=uncert_abs_sum_cm1*H_J_S*C_CM_PER_S/EV_J*Decimal(1000)
        # Atomic IP_H/D and HD-D0 (and H2-D0) are correlated through shared cycles;
        # root-sum-square would wrongly assert independent observation errors.
        def ds(x):return format(x,"f")
        return {
          "schema":"wu.r22.spectroscopic_candidate_result.v1",
          "reaction":LABEL,
          "state_labels":data["state_labels"],
          "source_identity":source,
          "components_cm1":{k:ds(z) for k,z in parts.items()},
          "HD_02_rotation_cm1":ds(rot_hd),
          "delta_E_products_minus_reactants_cm1":ds(deltaE),
          "candidate_Q_release_cm1":ds(q_cm1),
          "candidate_Q_release_J_per_event":ds(q_J),
          "candidate_Q_release_meV_per_event":ds(q_meV),
          "sum_reported_uncertainty_magnitudes_cm1":ds(uncert_abs_sum_cm1),
          "sum_reported_uncertainty_magnitudes_meV":ds(q_unc_meV),
          "uncertainty_semantics":"not_covariance_adjusted_not_confidence_interval_not_certified_bound",
          "physical_Q_event_J_per_event":None,
          "physical_bath_delta_J_per_ref_m3":None,
          "GL2022_PES_native_Q_J_per_event":None,
          "GL2022_PES_energy_zero_authenticated":False,
          "owner_ACK":"NOT_OBTAINED",
          "HH_R10":"OFF","production":"NOT_ISSUED","L4":False,
          "canonical_DAG":"34/49_UNCHANGED",
          "R21_workflow":"18/20_R6_C9_NOT_RUN",
        }


def main(argv=None):
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    args=a.parse_args(argv)
    data=json.loads(args.source.read_text(encoding="utf8"))
    result=evaluate_candidate(data)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    # Never replace earlier original evidence.
    with args.out.open("x",encoding="utf8") as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write("\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
