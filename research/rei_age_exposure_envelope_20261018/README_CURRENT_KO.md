# REI age-exposure/source-age 현재 상태 | 2026-10-19 VigilODE 연결

진입: 이 파일, `RESEARCH_UPDATE_20261019_VIGILODE_KO.md`, `HANDOFF_CODEX_CURRENT_KO.md`, `HANDOFF_NEW_CHAT_KO.md`, `contracts/NEXT_DAG_CURRENT.json`, `DELIVERY_RECEIPT_CURRENT.json`.

Repo `cosmosapjw-quantum/rei_bianchi`, draft PR199, branch `research/rei-age-exposure-envelope-20261018`. 이번 실제 intake HEAD는 `0ae749e9fdb179729c018706dbd59c4f61732b6a`. 원 native physics는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. 이전 CURRENT5는 `evidence/current_entries_before_vigilode_20261019/`에 원래 bytes로 보존했다.

## 먼저 읽은 새 결과

REI branch 247개/PR metadata 205개 전체 페이지와 관련 PR·최신 workflow, Drive 52회/Dropbox 18회 폴더 목록을 실제 읽었다. BR05·LRS·RUN16의 새 archive 3개를 전체 다운로드하여 payload 1,204개를 검증했다. 이들은 별도 연구 lane의 결과이며 새 age32 결과는 발견되지 않았다. 기존 age64 block-max와 spectral128은 완료 결과로 재사용한다.

VigilODE도 branch 147개/PR metadata 71개와 실제 source/CSV를 읽었다. 작업 중 PR71에 새 strict comparison 결과가 올라와 `9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858`까지 추가 조사했다. 새 756-cell campaign의 aggregate를 재집계했으며 empirical accuracy와 실제 source identity를 구분했다. 상세 coverage와 누락된 raw gzip/184MB bundle은 `vigilode_age_transport_20261019/intake/`에 명시한다. 계정 전체의 오래된 모든 파일을 읽었다고 주장하지 않는다.

## 이번에 추가한 이론·코드·실제 계산

`vigilode_age_transport_20261019/`에 원래 source packet 64개/57,344 nodes를 사용하는 고정 gas·endpoint geometry·고정 node 모형을 완성했다. VigilODE `ee65d4db…`의 `affine_transport.rs`와 `directed.rs`를 변경 없이 재사용하고, exact dyadic `num-rational`/`num-bigint`, Rayon, locked dependency 22개를 실제 적용했다.

- 원 native 153개 입력에서 별도 사본으로 읽기 전용 node export 1회, 약 11.8 s. 출생·physical source·encoded source·inventory는 원래 setup과 동일. 새 transformed RHS/ODE history 0회.
- Birth clocks만 8/16/32/64로 비교한 고유 4개 설정. 전역 최소 hazard bound를 실제 확인한 뒤, 같은 hazard tuple의 sensitive group 1,112개로 보완했다. 첫 결과도 보존한다.
- 최종 grouped 계산 약 53.733 s. Number-error upper는 8/16/32 순서로 1.292312768972707e-9, 1.2882258655815744e-9, 1.25025157367156e-9 photons/H. 기존 global bound보다 약 1,356–1,437배 좁다.
- **전체 N의 32→64 차이는 −0.815145%지만, 흡수가 있는 node만의 survivor 차이는 약 −82.574593%다.** Zero-hazard 4,096개의 공통 mass가 전체 정규화에서 차이를 가린다. Exact Fraction 재합산과 양의 분모 interval을 함께 기록했다.
- 고유 Rust tests 4개(새 task 3개+원본 upstream 1개), exp 17 fixtures, 전체 node Decimal100 검산, ledger 0 포함, thread 1/2/4 일치, offline locked 검증. 기존 전체 suite/24-case/NCP 완료 캠페인은 반복하지 않았다.
- R6/C9 독립 검토 및 처리한 finding은 `reviews/`에 있다. 고정 모형 N64≈1.30931e-7/H는 실제 nonlinear native endpoint≈1.29091e-9/H와 다르며 native reference로 수용하지 않는다.

정리·증명·단위·원본 code 대응은 `THEORY_KO.md`, 실제 명령과 실패 기록은 `IMPLEMENTATION.json`/`results/`, raw 계수는 `inputs/`에 있다. 실제 nonlinear Grackle response bound는 NOT_ESTABLISHED다.

## 이전 과학 상태와 다음 NCP

완료된 native age64 block-max: exit 0, 19,756 RHS, case 782.731 s, photon 2.002711130429069e-10/energy 1.929660553608937e-13, 원 1e-8 gate PASS. Source jumps는 MISSING_DATA, 18개 관측은 9개 고유 상태다. Spectral64→128 HeI 누적 photoevent 차이 0.2660778682%는 유한 이웃 결과로만 재사용한다.

N4의 고정 positive support/정확 count 아래 10개 1η 가중치가 유일해 stored energy 246η와 target 245η/tol 0를 맞추지 못한 native time8 결과는 HOLD로 유지한다. 새 affine 모형이 이 저장 문제를 고쳤다는 주장은 없다.

**READY는 단일 q0 age32 block-max/binary64, source8/n_mu8/transport16/time1, passive diagnostics ON, transport48, case/total cap1800 s다.** 완료된 age64의 원 binary·computational base·runtime에 binding해 비교한다. Age32 코드·진단·compactB1 복원·비교기는 이전에 구현 및 tiny-native 검증을 끝냈다. 복사 가능한 프롬프트는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다.

현재 NCP connector 실제 호출은 월 사용량 중지 응답이었다. 이번 NCP 실행은 NOT_RUN. Local Rust compile/계산과 양쪽 백업 읽기는 작동했다. 다음 세션에서는 다시 실제 도구 상태를 확인한다.

## 게시·백업과 보호 범위

이번 source snapshot과 C8/C10 v6의 실제 commit/provider/readback 상태는 `DELIVERY_RECEIPT_CURRENT.json`이 기준이다. Archive 생성 이후 작성되는 final receipt와 별도 delivery confirmation이 archive 내부의 생성 시점 pending 상태를 대체한다. 자기 commit/hash를 자기 안에 재귀적으로 기록하지 않는다.

Owner checkout, PR150/R9, LRS, BASS HHeD는 보존한다. PR199 draft 유지, no merge/no force-push. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.

## v6 최종 배송 확인

VigilODE source는 `50bc41f6b6aea05f67c03ab3ad23bb118d574622`에 게시했고, C8/C10 v6의 Drive·Dropbox 네 전체 readback에서 bytes/SHA/CRC/payload와 source·native153/B1·vendor identity를 확인했다. 상세는 `DELIVERY_RECEIPT_CURRENT.json`과 `evidence/delivery_v6_20261019/`이다. 최종 receipt commit은 별도 confirmation과 PR199 actual HEAD에서 확인한다.

Source CI 두 workflow는 이 task 밖의 기존 top-level native crate `cargo fmt --check`에서 실패했고 후속 테스트는 skipped였다. Scoped task 검증 PASS와 구별하며, full-PR CI가 green이라고 주장하지 않는다. `evidence/delivery_v6_20261019/SOURCE_CI_READBACK.json`에 실제 job/log 확인을 보존했다.
