# REI·REC source intake — 2026-10-05

실제 공개 Git 원문을 읽고 REI 45개, REC 16개 native 파일을 준비했다. 모든 바이트가 pinned tree의 Git blob 및 로컬 SHA-256과 일치한다. 이 조사에서는 컴파일·과학 검증·외부 게시를 새로 수행하지 않았다.

| Repo | Branch | HEAD | Commit tree | PR |
|---|---|---|---|---|
| rei_bianchi | forward/rust-reion-kernels-20260922 | b553698a114fbff05640ab6ecb95d260410de492 | 8144ffac066134b5cde1c507336e241eb31eca44 | 83, draft |
| rec_bianchi | forward/rust-he-sources-20260922 | cd68764aacfeae9fe794d7966604ac6fbb80ba7f | 174cedadd3175962832790771393577ef5478ead | 81, draft |

정확한 소스는 `../../source_rei/`, `../../source_rec/`; 인계 문서 15개는 `rei/`, `rec/`에 보존했다. `SOURCE_LOCK.json`, `DOC_SOURCE_LOCK.json`이 식별 근거다. 선택한 branch의 root/rust/native ancestors에는 적용할 AGENTS가 없다. 아카이브에 복제된 원자 repo AGENTS는 현 native crate의 상위 지침이 아니다.

## 최신 결과와 역사적 메타데이터 구분

- REI F04는 **완료된 static FT03 numerical-map certificate**다. actual source-site 세 개의 Krawczyk 포함, implicit J/H, observable Taylor, 계수 rounding, shared-parent two-half 합성을 다룬다. 수신 receipt는 3,591 Rust Jet witness/132 crate tests, 독립 MPFI200 checker PASS, 최대 local bound 약 9.535e-9/public width 약 1.587e-6을 보고한다. 이번 intake가 재실행한 결과는 아니다.
- 원 F04의 premature coefficient rounding 결함은 Host 수정으로 기록되고 최초 실패/원 PASS 문서가 보존된다. 수정된 마지막 bytes의 재독립 검토는 미실행이다. 이 물리 의미와 한계를 삭제하지 않는다.
- F04의 `next_task`는 **REI-F05 전체 첫 canonical interval**이다. live tree에는 아직 F05 runtime return이 없다. 실제 진행 여부를 별도 모니터하지 않은 상태에서 연구 스레드가 F05 소유 경로를 점유하면 안 된다.
- F06은 Bianchi-I characteristic/positive packet remap 구현 완료로 보고된다. 이는 collisionless/finite geometry 시험이며 coupled expanding source history가 아니다.
- F07은 compact 13.7 eV/5e-15 photon/H/s, 50,000 K, mean H=1e-14/s, epsilon=0.01, 1e13 s의 **prospective S0 preregistration** 완료다. paired history는 0이고 physical admission HOLD다. F07의 unresolved F04 항목은 이후 static F04 완료에 대해서만 역사적이다. expanding S0 인증으로 대체하면 안 된다.
- `threads/rei_bianchi/TASKS.json`의 F00..F09 `CODEX_READY_NOT_EXECUTED`는 최초 계획이다. runtime return과 source-bound latest state가 실제 완료 판단에 우선한다. 과거 TASKS를 역사자료로 보존하고 별도 current overlay로 조정하는 편이 충돌을 줄인다.
- REC Peebles `hydrogen_peebles.rs`는 PB02 바이트와 그대로 같다: blob `020940bca9fcca16d1f5d0a7955c206c2771d528`. 최신 REC HEAD 증분은 PB02 게시·백업 영수증 문서다.
- REI에는 아직 REC Peebles consumer가 없다. Cargo dependency가 없고 public lib에 Peebles export가 없으며 PB02 receiver packet은 인계만 있다. 이번 새 PB consumer를 separate crate로 만들면 REI 기존 Case-A/FT03 map과 F05 실행을 건드리지 않을 수 있다.
- He RCT native provider/RHS는 존재하지만 두 implicit stepper에 연결되지 않았다. 기존 RCT-STEP01은 별도 numerical-map/energy-ledger 작업으로 남긴다.

## REC original lane 상태

REC selected-He의 live `FORWARD_STATUS.json` V11은 d3cc6e... fixed-input source, 76 tests/251 records/3027 components와 scoped independent review PASS를 보고한다. 옛 PR81 본문과 일부 RETURN_HANDOFF의 source import pending/review HOLD는 이 상태보다 앞선 역사다. `Gate I=DEFERRED_CONSUMER`, physical gates는 그대로다. Pure-H Peebles reference 재사용에 이 He lane을 선행조건으로 추가하지 않는다.

REC `docs/CURRENT_STATE.md`의 v0.75 E1B0는 native diffusion과 COM atomic source의 중복 소유를 발견한 별도 full-HyRec lane이다. E1C split-domain replacement 미완료가 이번 prescribed one-T pure-H benchmark를 차단하지 않는다. 반대로 pure-H consumer 성공으로 E1C를 완료 처리할 수 없다.

## 충돌 없이 가능한 후속 일

| 작업 | 필요한 입력 | 소유/충돌 경계 | 이번 root 작업과 관계 |
|---|---|---|---|
| REI-PB03 separate consumer | REC live Peebles API, input/clock/unit lock | 새 crate만, 기존 FT03 code 변경 없음 | loop1 실행 후보로 root에 인계 |
| PB prescribed FLRW→BASS visibility | PB consumer pointwise evidence, 같은 H/nH/T/IC, BASS explicit SI/normal-clock API | 원자 Case-A history와 분리, pure-H one-T benchmark | loop2 실행 후보 |
| HE mixed native regression | frozen two cases, current homogeneous photo API | isolated test harness, 생산 source 변경 없음 | 다른 agent가 bounded 실행 준비 |
| REI-CHAT-FLRW06 spectral-stage | FLRW05 immutable ZIP의 3bin/96 positive-node vectors | 실제 homogeneous_photo_rates와 same-stage PhotonInput 호출; F06 collisionless 재구현 없음 | 별도 ready; 진행중 소유자 확인 후 착수 |
| Photon U/work ledger | FLRW05 coherent N/U measure + explicit edge-energy owner | photon_balance의 N budget과 별도 U closure, FT03 raw photo 중복 금지 | 독립 이론/계약 선행 가능; physics 의미 결정 필요 |
| RCT-STEP01 | 현재 RCT RHS + actual implicit residual/source-site | integration/certificate 도메인을 바꾸므로 F05 path와 동시 변경 금지 | isolated 설계/사전등록만 병렬 가능 |
| BASS opacity history return | accepted REI history with proper ne/time/frame | chemistry solver 소유권 없음 | F05/F08 결과 생길 때 converter만 연결 |

FLRW05의 common spectral-stage는 homogeneous photo node에 `P*nHc*MPC_CM^3`를 전달하고 PhotonInput에는 `P*nHc` reference comoving cm^-3를 전달한다. per-H source rate를 다시 nH로 나누면 안 된다. scalar N/U만으로 angular/occupation 또는 edge error authority를 생성하지 않는다.

기존 strict local <2e-4, public width <2e-3, [160,161] FAIL=2.1245050576368385e-4, prefix160 및 scientific HOLD는 보존한다. 원래 46080-node/3-lane history, expanding S0, full CMB/physical prediction의 인증은 이번 intake에 없다.

## 전달 상태

Root와 PB/HE 실행자에게 exact source paths와 live SHA를 전달했다. 외부 mutation은 하지 않았다. Git live PR collection·immutable source reads로 상태를 확인했으며 다른 ChatGPT 대화 본문을 직접 읽거나 보냈다고 주장하지 않는다.
