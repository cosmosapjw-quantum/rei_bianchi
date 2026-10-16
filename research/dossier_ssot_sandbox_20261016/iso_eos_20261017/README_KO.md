# REI / ISO-EOS scoped sandbox theory and coding increment

2026-10-17 · Parent [PR178](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/178); separate add-only branch.

읽기 순서: `docs/THEORY_ISO_EOS_KO.md` → `docs/IMPLEMENTATION_ISO_EOS_KO.md` → `contracts/ISO_EOS_CONTRACT.json` → `contracts/DAG_PROGRESS.json` → `rust/rei_iso_eos_reference/`.

원본 소스와 native cargo를 실제 컴파일했지만 원래 production의 H/D-CX full-network restriction은 변경하지 않았다. Rust reference는 `IsotopeNumberState` 13상태 혼합기체 EOS 및 고정 부피 CX 단일 사건과 instantaneous Savin RHS만 구현한다. R1–R10 단계들을 새로 완주했다고 선언하지 않고, 이번 bounded `ISO-EOS`의 유도·코딩·검증 결과만 보존한다. `native_subagent: NOT_RUN` (현재 도구 없음).

스크립트: `bash scripts/RUN_STAGE.sh`, 신뢰 기초: `contracts/SOURCE_IDENTITY.json`. 원본 Rustfmt traversal 이슈는 `evidence/FAILURE_AND_REPAIR.md`에 보존한다.

근거: Savin 2002 DOI10.1086/324218, Stancil/Lepp/Dalgarno 1998 DOI10.1086/306473 및 사용자의 기존 dossier/SSOT, frozen PR150 source snapshots. 논문 데이터가 아닌 `δχ=0.0037 eV`는 수치 시험의 명시적 manufactured 입력일 뿐이다.
