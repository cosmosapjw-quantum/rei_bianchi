#!/usr/bin/env python3
"""Preserve the user's 19 listed reactions and map selected owner capabilities."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = "research/atomic_nuclear_ssot_20261017/run13/recovered/code/rei_bass_coupled/"
COMMIT = "99e07bcff126d0a73a03bafc4b71e0b735dbcc3e"
REACTIONS = [
    (1, "H I + γ ↔ H II + e⁻", "electronic_photo_recombination", {}, {}, True),
    (2, "He I + γ ↔ He II + e⁻", "electronic_photo_recombination", {}, {}, True),
    (3, "He II + γ ↔ He III + e⁻", "electronic_photo_recombination", {}, {}, True),
    (4, "⁴He + γ ↔ ³He + n", "photonuclear", {"He4": 1}, {"He3": 1, "n": 1}, True),
    (5, "⁴He + γ ↔ T + p", "photonuclear", {"He4": 1}, {"T": 1, "p": 1}, True),
    (6, "⁴He + γ ↔ D + D", "photonuclear", {"He4": 1}, {"D": 2}, True),
    (7, "³He + γ ↔ D + p", "photonuclear", {"He3": 1}, {"D": 1, "p": 1}, True),
    (8, "D + γ ↔ p + n", "photonuclear", {"D": 1}, {"p": 1, "n": 1}, True),
    (9, "T → ³He + e⁻ + ν̄ₑ", "beta_minus", {"T": 1}, {"He3": 1}, False),
    (10, "n → p + e⁻ + ν̄ₑ", "beta_minus", {"n": 1}, {"p": 1}, False),
    (11, "⁷Li + γ ↔ ⁴He + T", "photonuclear", {"Li7": 1}, {"He4": 1, "T": 1}, True),
    (12, "p(n,γ)D", "radiative_capture", {"p": 1, "n": 1}, {"D": 1}, False),
    (13, "D(p,γ)³He", "radiative_capture", {"D": 1, "p": 1}, {"He3": 1}, False),
    (14, "D(D,p)T", "nuclear_transfer", {"D": 2}, {"T": 1, "p": 1}, False),
    (15, "D(D,n)³He", "nuclear_transfer", {"D": 2}, {"He3": 1, "n": 1}, False),
    (16, "T(D,n)⁴He", "nuclear_fusion", {"T": 1, "D": 1}, {"He4": 1, "n": 1}, False),
    (17, "³He(D,p)⁴He", "nuclear_fusion", {"He3": 1, "D": 1}, {"He4": 1, "p": 1}, False),
    (18, "³He(n,p)T", "nuclear_transfer", {"He3": 1, "n": 1}, {"T": 1, "p": 1}, False),
    (19, "T(α,γ)⁷Li; α ≡ ⁴He", "radiative_capture", {"T": 1, "He4": 1}, {"Li7": 1}, False),
]
NUCLEI = {"n": (1, 0), "p": (1, 1), "D": (2, 1), "T": (3, 1),
          "He3": (3, 2), "He4": (4, 2), "Li7": (7, 3)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    raw = a.image.read_bytes()
    image = a.output / "primordial_target_network.png"
    image.write_bytes(raw)
    entries = []
    table = []
    for number, equation, kind, lhs, rhs, reversible in REACTIONS:
        entry = {"id": number, "equation_as_listed": equation, "kind": kind,
                 "right_hand_list_is_authoritative": True, "reversible_arrow_as_listed": reversible,
                 "target_obligation_retained": True}
        if number <= 3:
            entry.update(
                current_status="EXISTING_ELECTRONIC_COEFFICIENT_AND_PHOTO_OWNERS_SCOPED",
                owner_paths=[BASE + "owner_src/atomic_provider.rs", BASE + "owner_src/igm_rates.rs",
                             BASE + "src/full_network.rs", BASE + "src/spectral_native.rs"],
                full_target_network_status="UNRESOLVED",
                scope="Existing H/He photo fits and collisional/RR rates; source-specific finite tests/history are not a full isotope-resolved primordial/EoR solution.",
                forward_electron_bookkeeping={"nuclear_charge_change": 0, "ionic_charge_change": 1,
                    "bound_electron_change": -1, "free_electron_change": 1},
                isotope_extension="Requires an explicit coefficient policy and charge-state projection; nuclear isotope evolution is separate.")
            status = "기존 H/He 전자계수·photo owner; 전체 목표망 미완료"
        else:
            delta_a = sum(NUCLEI[s][0] * n for s, n in rhs.items()) - sum(NUCLEI[s][0] * n for s, n in lhs.items())
            delta_z = sum(NUCLEI[s][1] * n for s, n in rhs.items()) - sum(NUCLEI[s][1] * n for s, n in lhs.items())
            free_e = 1 if kind == "beta_minus" else 0
            assert delta_a == 0 and delta_z - free_e == 0
            entry.update(
                current_status="UNRESOLVED_NATIVE_COUPLING_IN_SELECTED_LINEAGE",
                implemented_by_run19_metals=False, owner_paths=[],
                nuclear_stoichiometry={"reactants": lhs, "products": rhs,
                    "delta_baryon_number": delta_a, "delta_nuclear_charge_number": delta_z,
                    "listed_free_electrons_created": free_e,
                    "delta_nuclear_charge_minus_listed_free_electrons": delta_z - free_e,
                    "scope": "Formal nucleus-level stoichiometry only; no ionic product charge state or binding-energy/thermal assignment."},
                missing_for_target=["pinned source coefficient/cross section and validity domain",
                    "coupled isotope and electronic charge-state projection",
                    "photon/particle/binding/rest-mass and escaped-energy ledgers",
                    "scoped numerical validation on the actual background"])
            if kind == "beta_minus":
                entry["missing_for_target"].extend(["decay lifetime/rate owner and daughter branching",
                    "electron/neutrino energy disposition and atomic-shell response"])
            status = "선택한 native 계보 결합 미완료; metals에서 구현하지 않음"
        entries.append(entry)
        table.append(f"| {number} | {equation} | {status} |")
    document = {
        "schema": "rei-run19-user-target-network-19-v1",
        "source_image": {"original_path": str(a.image), "preserved_file": image.name,
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
        "transcription": "Manually read the supplied image. Its right-hand list, not all left-hand arrow labels, defines these 19 target IDs.",
        "baseline_commit": COMMIT,
        "reaction_count": len(entries), "reactions": entries,
        "shared_forward_reverse_processes": [
            {"listed_ids": [7, 13], "pair": "He3 ↔ D+p+photon"},
            {"listed_ids": [8, 12], "pair": "D ↔ p+n+photon"},
            {"listed_ids": [11, 19], "pair": "Li7 ↔ He4+T+photon"}],
        "overlap_rule": "All 19 user IDs remain. Forward/reverse overlaps are annotations, not a reduced task list; inverse coefficients require source-specific detailed balance assumptions.",
        "metals_delta": {"Li": "Existing PR150 elemental CI/RR/DR and Li6/Li7 number-only forwardport, explicit ElementalElectronicEquality.",
            "Be": "New native selected VF1996 total-RR contributions forming BeII/III/IV, optional Be7/Be9 labels, no nuclear evolution.",
            "does_not_complete_target_reactions": [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
            "original_13_state_registry_changed": False},
        "remaining_dag_obligations": ["all incomplete target reactions above", "original nuclear T1-T8", "Li/Be full coupling",
            "continuous spectral refinement", "angular convergence", "birth-time continuum", "whole donor domain",
            "full EoR", "Einstein feedback", "FLRW-CONV", "BI-SIGNED", "ISO-COUPLE full"],
        "full_bbn_integration_performed": False,
    }
    (a.output / "TARGET_NETWORK_19.json").write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    text = """# 사용자 지정 19반응 목표망과 현재 provider 범위

제공 그림의 오른쪽 반응식 목록을 기준으로 19개 ID를 그대로 보존했다. 왼쪽 그림의 일부 번호/화살표는 오른쪽 식과 대응하지 않으므로 코드 반응 방향의 근거로 사용하지 않는다. 그림 원본과 SHA-256은 `TARGET_NETWORK_19.json`에 기록되어 있다.

| ID | 오른쪽 목록의 반응 | 현재 선택 계보의 범위 |
|---|---|---|
""" + "\n".join(table) + """

## 전자와 핵의 장부

전자 광이온화는 핵종·핵전하를 유지하면서 이온전하와 자유전자 수를 각각 하나 늘린다. 역방향 재결합은 자유전자를 하나 소비한다. 반면 β⁻ 반응은 핵전하를 하나 늘리고 전자·반중성미자를 방출한다. 이 둘을 같은 electronic rate 또는 binding-energy 항으로 처리할 수 없다.

핵반응의 원자 껍질과 생성물 이온전하는 별도 projection 문제다. 특히 n→p+e⁻+ν̄ₑ의 p를 곧바로 중성 H I로 배치하지 않는다. 핵 결합/정지질량 변화, 방출 입자, photon ledger, 열에 실제 남은 에너지도 원자 재결합계수만으로 채울 수 없다.

목록 7↔13, 8↔12, 11↔19에는 정·역방향의 물리적 중첩이 있다. 이는 19개의 사용자 목표를 줄이는 이유가 아니다. 계수의 상세평형 관계를 사용하려면 해당 핵 source, 통계 인자, 분포와 온도 전제를 따로 검증한다.

## 이번 선택형 Li/Be 코드의 의미

Li6/Li7 source는 이미 존재한 PR150의 전자 CI/RR/DR 구현을 고정99 grid로 호환 이식한다. Be의 세 계수는 VF1996 total-RR이며, Be III→Be II, Be IV→Be III, Be V→Be IV의 number contribution만 계산한다. 두 경우 isotope label은 `ElementalElectronicEquality`이고 isotope-specific 실험 계수라는 주장을 하지 않는다.

이 전자 과정들은 목록 11의 ⁷Li 광핵 분해나 19의 T+α 핵 포획을 구현하지 않는다. Be7 label도 전자계수 호출만 허용하며 electron capture·decay·daughter 모델을 가정하지 않는다. 모든 미구현 핵반응과 기존 T1–T8, 전체 EoR/배경 feedback/연속 수렴 의무는 그대로 남는다. 이번 작업에서 full BBN 적분은 실행하지 않았다.
"""
    (a.output / "TARGET_NETWORK_19_KO.md").write_text(text)
    print(json.dumps({"reaction_count": len(entries), "image_sha256": document["source_image"]["sha256"],
                      "formal_nuclear_stoichiometry_checks": 16, "full_bbn_integration_performed": False}))


if __name__ == "__main__":
    main()
