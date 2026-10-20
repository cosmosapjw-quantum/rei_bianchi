# REI 현재 상태 | 2026-10-20 v8 관측량별 source-age 경계

기존 57,344 labels와 birth clocks 8/16/32/64에서 energy, HI/HeI/HeII photoevents, age moments, population별 normalized survivor age의 outward 경계를 구현·계산했다. Sensitive32−64 평균 age 차이는 `130812976009.628 s`, 선택 상한은 `135852646019.94653 s`다. 기존 전역 상한보다 `315380.621117배` 좁다. 전체32−64 차이는 `88822856290.8 s`, 상한은 `237111181117.59164 s`다. Passive32−64는 number 차이 0이지만 평균 age 차이 `-2058109991.46399 s`가 남는다.

## 먼저 읽을 결과

`RESEARCH_UPDATE_20261020_OBSERVABLES_KO.md`, `observable_certificates_20261020/README.md`, `THEORY_KO.md`, `results/STUDY.json`, `results/DECIMAL_REFERENCE.json`, `results/NORMALIZED_MEAN_BOUNDS.csv`, `reviews/R6_RECEIPT.json`, `reviews/c9/C9_RECEIPT.json`. 이론 R6는 PASS이며 C9 최종 구현 검토는 PASS(열린 지적 0개)다. R1–R9/C1–C8 완료, R10/C10과 source·backup 배송은 DAG의 실제 상태를 따른다.

새 Rust fixtures10개와 Decimal100 독립 직접식 612개 aggregate checks가 PASS다. 실제 node 요청만 preload하도록 한 번 수정한 결과 scientific float bits는 모두 동일했고 unique exponentials는 346,945→34,625다. 수정 후 Rust subprocess wall은 13.421518592 s, Decimal wall은 12.855201847 s이며 누적 분석은 68.545581187/240 s다. 2 Rayon workers를 사용했다. 반복 benchmark나 전체 역사 suite를 새로 실행하지 않았다.

## 게시·백업

이번 baseline PR199 HEAD는 `cf00684741eb612e35f987713c28937513d44d57`(task tree `c5127608ba4e4344da45d685b9cd78aa3861cd13`)다. v8 source 게시·C8/C10 이중 백업·전체 readback은 아직 PENDING이다. 기존 v7 source/Drive·Dropbox 네 전체 readback 완료 기록은 `observable_certificates_20261020/baseline_current/DELIVERY_RECEIPT_CURRENT.json` 및 `evidence/delivery_v7_20261020/`에 보존했다. 이 문서의 준비 상태를 게시·업로드 완료로 해석하지 않는다.

## 다음 실행과 제한

다음 native READY는 원래 단일 q0 age32/source8/n_mu8/transport16/time1, block-max/binary64, passive diagnostics ON, transport48, case/total cap1800 s다. 원 B1 binary·computational base·runtime binding과 rtol/atol·RK·source schedule·photon/energy1e-8를 유지한다. 사용자 수동 파일 복원 없는 복사 프롬프트는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다. 완료 age64·spectral128·v7 benchmark·이번 고정 모형 계산은 반복하지 않는다. Native age/time HOLD, age64 source jumps MISSING_DATA, nonlinear response bound NOT_ESTABLISHED를 유지한다.

현재 NCP device listing은 성공했으며 이번 unit에서 NCP SSH probe나 native RHS/trajectory 실행은 하지 않았다. 과거 월 사용량 중지는 역사 기록이다. Owner checkout, PR150/R9/LRS/BASS HHeD 보호, PR199 draft/no merge/no force-push를 유지한다. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.
