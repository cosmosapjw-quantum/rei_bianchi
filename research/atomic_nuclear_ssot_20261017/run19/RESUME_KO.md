# RUN19 durable resume — 2026-10-20

## 최신 결과 선택

- Repository: `cosmosapjw-quantum/rei_bianchi`.
- Branch: `research/rei-run19-rate-acceleration-20261020`; draft [PR211](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/211).
- Fixed physics/source parent: `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e` (RUN18). 새 스레드에서는 원격 ref를 다시 읽는다.
- 완료된 A source: `f2996d02908e5a2e678fab0dc0efb3424fa86a99`; C source: `ffcb3709c3d19d577b1e6eb69dd0ce4d4d94d85a`.
- A/B/C bounded 구현·검증·게시·백업 완료. 최종 과학/source commit은 `e540256ecf77df1c88fccb57b81d5d60110f367c`; 이후 commit은 delivery·RESUME 문서만 추가한다. `delivery/UNIT_B_FINAL_DELIVERY.json`과 `DAG_PROGRESS_FINAL_DELIVERY.json`을 현재 상태로 읽는다.
- 우선 읽기: `README_KO.md`, `UNIT_B_FINAL_KO.md`, `DAG_PROGRESS_UNIT_B.json`, `REPRODUCE_UNIT_B_FINAL.json`, `metals/network/TARGET_NETWORK_19.json`.

최종 ZIP: [Drive](https://drive.google.com/file/d/1pRPhitdAFfEU8HrSC02uXXVXwRI1U8wk/view); Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN19_FINAL_T_RATE_ACCELERATION_LI_BE_20261020.zip`, file ID `id:BSpOijBcT10AAAAAAD_SVw`. 실제 25,344,988 bytes, SHA-256 `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62`. 두 백업 모두 별도 전체 다운로드 후 같은 SHA를 확인했다. 이전 A/C 개별 ZIP은 업로드 완료만 확인했으며, 최종 aggregate의 byte readback을 과거 개별 ZIP의 검산으로 바꾸어 쓰지 않는다.

## 완료해서 반복하지 않을 것

RUN13 m2 standard/tight, RUN16 prefix A/B/C, RUN17 A/B controls, RUN18 완료 adapter/reference, RUN19 완료 tests/benchmarks를 복원 목적으로 자동 재실행하지 않는다. RUN19 native IVP 수는 0이다. 원래 RUN13 91파일은 그대로다. main/production·atomic physics owner를 조용히 변경하지 않는다.

Native prepared HHeD 공유/exact-T cache/batch, opt-in 32769-node cubic와 source-bound disk cache, 실제 coefficient/RHS/병렬 측정, safe Rust kernel의 scoped SIMD compiler 증거를 완료했다. Default cache source ID는 `53f101a30c0d6fdae246eb6ca545660e8bab5aaf22e34787c6ba15fd1ec8fcc4`, cache SHA256은 `dcfa521f60165632e6fa1c0d10473b194c8aab73844ee0a44ed2454e18f7a23b`다. Source를 바꾸면 이전 identity를 우회하지 말고 새 cache를 만든다.

선택 cubic의 coefficient finite 최대 상대차 `1.5329094455e-8`, H net `3.827730095e-9`, chemical net `1.399808165e-8`; payload `4,358,273 bytes`. Ideal exact-source bound `8.5126148138e-8`와 selected stored-input rounding upper `8.8248025547e-16`는 별도 범위다. Full f64 source/IVP/spectral bound로 합쳐 선언하지 않는다. Rounding JSON domain metadata는 `execution/unit_b_final/ROUNDING_DOMAIN_METADATA_ADDENDUM.json`을 적용한다.

Li6/Li7은 기존 PR150의 explicit elemental electronic equality와 domain을 보존한 호환 이식이다. 10,000K에서 full Li bundle이 허용된다고 가정하지 않는다. Be는 VF1996 RR 중 BeII/III/IV를 형성하는 세 채널만 구현했으며 BeI missing은 zero가 아니다. 원래 13-state coupled registry는 바꾸지 않았다. 전자 재결합을 Li7 광핵·포획이나 Be7 붕괴의 구현으로 세지 않는다.

## 복원 계약

전체 패키지는 repo-relative RUN19, 원래 RUN13 native91파일, RUN18 directed.rs/LICENSE, 원래45/26DAG, root LICENSE, vendor10packages/614files, 원시 결과·cache·실제 실행 binary를 보존한다. Rust1.94.1 toolchain 및 과거 m2 전체 이력은 기존 durable 위치를 사용한다. 새 local SOURCE/BACKUP offline build+META는 실제 성공했지만 binary hash가 달라 byte-reproducible binary/전체 Git-only 복원으로 주장하지 않는다. 최소 실행은 `REPRODUCE_UNIT_B_FINAL.json`의 명령과 source closure를 따른다.

## 다음 실제 미완료 DAG 노드

**P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION → 동일 first-birth panel의 original-owner continuous interval RHS와 admissible gas/depth feedback tube.**

먼저 보존한 native source/first-birth 상태에서 하나의 bounded branch에 대해 실제 source-node 및 ln/exp grid/query interval 오차를 제공하고 기존 M4 보간항·VigilODE stored-input arithmetic enclosure와 결합한다. 이어 interval gas/depth Jacobian, whole-time residual, tube-wide log norm, prefix 초기 오차, 물리 event map·photo spectral forcing이 필요하다. Finite point 검사를 whole-time enclosure로 승격하지 않는다.

기존 m1/m2 sub-H-fit-edge `3.963580101474543e-12` / `8.255385244169650e-12 comoving m^-3` 및 약51.99% 차이는 archived evidence다. 이번 table 가속으로 수렴했다고 쓰지 않는다. M4 NOT_RUN, spectral continuum NOT_ESTABLISHED. Continuous spectral/angular/birth-time/whole donor/full EoR/Einstein/FLRW-CONV/BI-SIGNED/ISO-COUPLE full/Li-Be/nuclear T1–T8 및 이미지 전체19반응 목표를 유지한다.
