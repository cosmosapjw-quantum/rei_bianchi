# BRPERF01 — 완료된 bounded optimization 연구

**COMPLETE_VERIFIED_BOUNDED_OPTIMIZATION_AND_FULL_BACKUPS**

원 물리 owner와 S10/CX 제어기를 보존한 opt-in 구현이다. T-only compact 표와 native H/He/D 계수 재사용, 동결 BASS 광자 영속 작업자, Li/C/N/O 원자 계수 catalog를 완료했다. 정량 결과와 적용 범위는 [한국어 보고서](brperf01/docs/REPORT_KO.md), [정량 결과 JSON](brperf01/evidence/SCIENCE_RESULTS.json), [검증 색인](brperf01/evidence/VERIFICATION.json)을 따른다.

## 최종 상태

- [완료 게시·백업 영수증](PUBLICATION_RECEIPT.json)
- [최종 DAG](contracts/DAG_FINAL.json)
- [양쪽 raw ZIP 검증](closeout/RAW_RESTORATION.json)
- [새 경로 전체 안전 복원](closeout/FULL_ARCHIVE_LOCAL_RESTORE_R1.json)

기존 `contracts/DAG_PROGRESS.json`과 `brperf01/contracts/DAG_PROGRESS.json`은 각 checkpoint/ZIP 동결 시점을 기록한다. 위 `DAG_FINAL.json`과 완료 영수증이 그 이후의 게시 완료를 닫는다.

## 전체 복원본

[Google Drive FULL_r1](https://drive.google.com/file/d/1PSMb23VRTOdeJr3rS95tz_mE6zS9rVPl/view)

`REI_BRPERF01_OPTIMIZATION_20261020_FULL_r1.zip` — 102,524,314 bytes, 1,435 payload / 1,436 entries.

```text
SHA-256 8cbdad4a1f888e003b18714fc147a13769f40f0b675fd5ae44b7eab1d763f818
```

Dropbox에도 같은 ZIP을 보관했다. 정확한 경로, provider hash와 두 raw download의 payload 검증 결과는 영수증에 있다. 첫 FULL의 Git binding metadata는 원문 개행을 보존한 게시 repair 후 R1으로 교체됐으며, 이전본은 superseded 기록으로 남겼다.

원 parent/input, offline registry, 구현·CSV·실패 로그, 독립 source ZIP/patch/bundle을 포함한다. 확인되지 않은 새 외부 reference 원문의 재배포는 URL/hash fetch 계약으로 표현했다. Compiler installer는 포함하지 않으며 pinned 복원 계약을 제공한다.

Git 소스만으로 재구성할 경우 [workspace 복원 지침](brperf01/README.md)과 [GIT_RESTORE_CONTRACT.json](GIT_RESTORE_CONTRACT.json)을 사용한다. Source artifact bundle은 원 저장소 Git 이력과 별개인 독립 snapshot이다.

## 검증 범위

282 unique Rust tests, strict Clippy, scoped rustfmt 및 실제 source fresh-restore가 통과했다. Native direct reuse는 원 이력과 비트 일치했고, compact 8193은 표본 최대 coefficient 상대오차 1.30017e-5에서 native RHS 약 2.918배를 관측했다. Frozen ±shear 2-worker는 각각 약 1.805/1.775배였다. 서로 다른 측정 범위의 가속률은 전체 solver 가속률이 아니다.

다음 노드는 `PERF05_BASS_NATIVE_COMBINED`다. `LONGSPAN_SOLUTION=NOT_ADMITTED`, `ISO_COUPLE_P4=PARTIAL`, `FULL_EOR=HOLD`를 유지한다. 추가 원자 catalog는 활성 population/동위원소·핵반응망이 아니며 양방향 Einstein feedback도 남아 있다.
