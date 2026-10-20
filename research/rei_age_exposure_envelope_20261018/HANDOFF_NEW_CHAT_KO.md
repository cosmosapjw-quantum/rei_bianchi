# 새 대화 재개 | 2026-10-20 v8 관측량별 source-age 경계

## 현재 결과와 첫 읽기

기존 57,344 labels와 birth clocks 8/16/32/64에서 energy, HI/HeI/HeII photoevents, age moments, population별 normalized survivor age의 outward 경계를 구현·계산했다. Sensitive32−64 평균 age 차이는 `130812976009.628 s`, 선택 상한은 `135852646019.94653 s`다. 기존 전역 상한보다 `315380.621117배` 좁다. 전체32−64 차이는 `88822856290.8 s`, 상한은 `237111181117.59164 s`다. Passive32−64는 number 차이 0이지만 평균 age 차이 `-2058109991.46399 s`가 남는다.

새 Rust fixtures10개와 Decimal100 독립 직접식 612개 aggregate checks가 PASS다. 실제 node 요청만 preload하도록 한 번 수정한 결과 scientific float bits는 모두 동일했고 unique exponentials는 346,945→34,625다. 수정 후 Rust subprocess wall은 13.421518592 s, Decimal wall은 12.855201847 s이며 누적 분석은 68.545581187/240 s다. 2 Rayon workers를 사용했다. 반복 benchmark나 전체 역사 suite를 새로 실행하지 않았다.

최초에 CURRENT5(`README_CURRENT_KO.md`, `HANDOFF_CODEX_CURRENT_KO.md`, 이 문서, `contracts/NEXT_DAG_CURRENT.json`, `DELIVERY_RECEIPT_CURRENT.json`)와 `RESEARCH_UPDATE_20261020_OBSERVABLES_KO.md`, `observable_certificates_20261020/README.md`, `THEORY_KO.md`, `results/STUDY.json`, `results/DECIMAL_REFERENCE.json`, `results/NORMALIZED_MEAN_BOUNDS.csv`, `reviews/R6_RECEIPT.json`, `reviews/c9/C9_RECEIPT.json`를 읽는다. R6와 최종 C9는 PASS(열린 지적 0개)이며 source 게시·네 전체 backup readback·R10/C10은 완료됐다.

v8 source는 `02767dc5e6c4b47883f590834aee38530852568d`에 게시했으며 2,152개 Git blob/mode, task tree `8fce099de816bdebb1dbd7bb22f87817ff50e9f5`, root/research의 다른 subtree 보존을 확인했다. C8/C10의 Drive·Dropbox 네 upload 및 서로 다른 네 전체 readback이 완료됐다. Whole bytes/SHA256/CRC/모든 manifest payload/source blob·mode/C10 전체 task tree/native153/B1/deduplicated source/vendor22·865 검증은 모두 PASS다. 실제 provider IDs·크기·SHA와 원 receipt는 `DELIVERY_RECEIPT_CURRENT.json`, `evidence/delivery_v8_20261020/`에 있다. Immutable ZIP에는 source 준비 시점의 pending CURRENT가 남고 이 완료 기록이 이를 대체한다. 이 배송 metadata의 identity는 자신을 담은 Git commit이며 exact HEAD와 UTF-8 restore delta는 별도 post-commit v8 confirmation에 기록한다. Confirmation 자체의 두 provider upload/readback은 별도 후속 단계다.

## 재개 전 fresh intake

PR199 actual HEAD, 최신 Drive/Dropbox confirmation과 새 연구 결과부터 실제로 확인하고 선택 HEAD를 기록한다. 새 age32 결과가 이미 있으면 ingest하고 중복 실행하지 않는다. 이번 intake의 실제 범위는 `observable_certificates_20261020/intake/cloud/INTAKE_V8.json` 및 `intake/upstream/INTAKE.json`에 있다. REI251 branches·최근PR100, VigilODE153 branches·PR76·최근 workflows25, age Dropbox24·Drive119 목록과 v7 confirmation을 읽었다. VigilODE PR76 midcheck의39 CSV rows/312 cells/30 paired medians와 별도 RUN19/LRS/HE29 결과를 확보했으며 hybrid branch는 native compile failure다.

모든 과거 데이터를 읽었다고 가정하지 않는다. Dropbox38,285 recursive inventory는 변경 없는 부분의 이전 조회를 재사용했고 Drive 오래된 dossier는1,000개 조회 뒤가 부분적이다. VigilODE 원 raw full states를 독립 재계산하지 않았다. Conversation search는 실제 ERROR였으며 mail/file snippets는 새 age32 완료 결과가 아니었다. 알려진 범위에서는 새 native age32 완료 결과가 없었다.

## 다음 native 한 사례

다음 native READY는 원래 단일 q0 age32/source8/n_mu8/transport16/time1, block-max/binary64, passive diagnostics ON, transport48, case/total cap1800 s다. 원 B1 binary·computational base·runtime binding과 rtol/atol·RK·source schedule·photon/energy1e-8를 유지한다. 사용자 수동 파일 복원 없는 복사 프롬프트는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다. 완료 age64·spectral128·v7 benchmark·이번 고정 모형 계산은 반복하지 않는다. Native age/time HOLD, age64 source jumps MISSING_DATA, nonlinear response bound NOT_ESTABLISHED를 유지한다.

원 native commit `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, B1 SHA256 `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`, computational base `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`, prepared identity `e376b58ee3ef2b14cda70bc8d966d686db52aabc0a832cab0b8cc0ea8a430bfd`를 유지한다. 기존 age64 reference/native153/B1 자동 복원 및 실행 전체 지시는 `HANDOFF_CODEX_CURRENT_KO.md`의 복사 프롬프트를 사용한다.

현재 NCP device listing은 성공했으며 이번 unit에서 NCP SSH probe나 native RHS/trajectory 실행은 하지 않았다. 과거 월 사용량 중지는 역사 기록이다. Owner checkout, PR150/R9/LRS/BASS HHeD 보호, PR199 draft/no merge/no force-push를 유지한다. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.

## Source CI 실제 상태

Source commit의 push/PR 두 workflow는 기존 root `rust/rei_microphysics` cargo fmt에서 실패했고 workspace test는 skipped였다. 해당 root Rust와 `.github` tree는 baseline과 같다. Scoped10 fixture/Decimal/C9 PASS와 별개이며 full PR CI green은 아니다. 실제 run/job/log readback은 `evidence/delivery_v8_20261020/SOURCE_CI_READBACK.json`에 있다.
