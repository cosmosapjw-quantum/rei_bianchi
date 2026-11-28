# HE29 후속 분석: 공유 기준해와 부분 반환

2026-10-20 05:57 UTC 재개 단위다. 최신 GitHub·관련 저장소·백업·로컬 반환을 먼저 읽은 뒤, 공유 기준해를 보존하는 정확한 signed 분해와 부분 반환 분석기를 구현했다. **새 테스트 28개 첫 PASS, 분담 독립 검토 PASS, 실제 로컬 분석은 기준해 0/4·HOLD**다. 이번 작업은 원래 solver·물리식·반응률·허용치를 변경하지 않는다.

## 실제 상태

| 축 | 상태와 근거 |
|---|---|
| DAG | 이번 분석 단위의 R1–R10 및 C1–C10 완료. native와 Drive의 외부 HOLD 유지. 조건부 산술 검증과 실제 native 미완료를 분리한 `DAG_STATUS.json` 참고 |
| 게시 | intake `3b125fc3cf80ce715353be17f640f2d9a5fb9f4a`, 실제 12/12 Git readback PASS. 새 구현 및 후속 인계의 실제 commit은 `DELIVERY.json`과 publication receipt에 기록 |
| 백업 | intake `f6efa95f…`: Dropbox raw bytes·내부 검증 PASS, Drive 단일 업로드 UNKNOWN·재시도 없음. 기존 COMPLETE `77f1c73e…`와 CLOSEOUT `3380c7c4…`의 dual raw PASS 재사용. 새 통합7a86d5bb는 Dropbox full raw·70 payload PASS, Drive UNKNOWN |
| 새 실행 | HE29 native 0, NCP 제출/시작 0, HE28 transport 0, 기존 science·source·최적화 검사 재실행 0 |

Remote Desktop Commander의 기존 월간 quota 및 재시도·재연결 금지 상태를 유지한다. 미게시 NCP 프로세스는 관측하지 못했다. 로컬 경로가 없다는 사실을 원격 프로세스 부재로 확대하지 않는다.

## 최종 보존과 인계 상태

이번 분석 단위의 구현·경량 검증·독립 검토·Git 게시·Dropbox 보존을 마쳤다. 실제 HE29 기준해는 0/4·HOLD이고 Drive 업로드 결과는 UNKNOWN이다. 이 두 외부 상태를 분석 구현의 실패나 새 과학 계산 완료로 바꾸지 않는다.

현재 통합 보존본은 `BASS_HE_HE29_REFERENCE_BUDGET_COMPLETE_20261020_7a86d5bb.tar.gz`, **6,621,294 bytes**, SHA256 `7a86d5bbe27da9da52584edb27145b626c6954455729c9af3365147fc4802c08`다. Dropbox **`id:BSpOijBcT10AAAAAAD_SUQ`**의 실제 단일 GET에서 전체 SHA와 content_hash `014e6096765e924b44a28ac25a6469ff1718be83c306cd37e72df68ff91bfdb2`, outer payload **70/70** 및 manifest 포함 member **71/71**이 일치했다. 보존 범위는 문서 commit `a143b08eeeb37e7f8cdbc78d84f750c321a220be`의 현재 분석·canonical 문서62개, publication metadata, 이전77f·3380·f6 archive 세 개다. 기존 archive의 내부 검사나 과학 계산은 반복하지 않았다.

Drive 첫 업로드는43초 안에 접수 ID나 완료 응답을 주지 않았다. canonical parent의 한 번의 제한된 조회에서 해당 이름은 관측되지 않았으며, 이는 불완전한 업로드 결과의 확정 실패 증명이 아니다. 상태를 **UNKNOWN**으로 유지하고 재시도·우회 업로드는0이다. 앞선 intake f6의 Drive UNKNOWN도 그대로 유지한다. NCP의 기존 월간 quota/no-retry와는 다른 제공자 상태다.

실제 영수증은 `evidence/FINAL_BACKUP_RECEIPT.json`과 `evidence/DROPBOX_RAW_READBACK.json`에 있다. 이 통합 archive 뒤에 작성한 최종 metadata·두 인계 문서는 별도의 작은 handoff 보존본과 PR78 closeout 영수증으로 연결한다. 실제 최종 commit·archive identity는 Git/PR 및 detached 영수증을 읽으며, 자기 자신을 포함하는 SHA나 미관측 provider 완료를 만들지 않는다.

## 새 구현

`src/linear_budget.py`는 입력 binary64를 각각 정확한 유리수로 변환하고, 반복 사용된 기준해의 계수를 먼저 합쳐 소거한다. key별 독립 Radau/DOP853 선택의 `product_hull`과 모든 key의 동일 method 선택인 `coherent_hull`을 따로 계산한다. exact width와 표시용 binary64 outward width를 구분한다.

`src/partial_returns.py`는 준비됨·method-only·실패·timeout·완성 상태를 구분하고 원래 admission contract를 재사용한다. method JSON, RESULT, source/binary/table identity와 실행 cohort를 연결하며, method 적분 시간과 전체 process 시간을 분리한다. 일부 잘못된 반환 때문에 다른 유효 부분을 폐기하지 않는다.

`src/analyze_budget.py`는 기존 transport DATA 18개를 고정 SHA와 model/table/owner/thread/source 계약에 대조해 읽는다. admit된 기준해에 대해서만 signed residual과 strip/table 대비를 만든다. 기존 `NATIVE_RETURN_AUDIT.json`은 원래 SHA를 확인한 bytes와 값을 그대로 포함하며 기존 time/mixed/sign 계산을 반복하지 않는다. 입력은 baseline checkout의 `--data-root`에서 재사용할 수 있고, code/manifest는 분석 Git revision에 고정된다. 출력은 create-only·atomic·fsync다.

finite-candidate hull은 저장된 두 수치 후보가 만드는 범위다. 참 ODE 해의 오차반경이나 연속 스펙트럼 인증을 뜻하지 않는다. 수식·전제·구성적 증명·원전 채택 위치는 `RESEARCH_KO.md`와 `THEORY_REVIEW_KO.md`에 있다.

## 이번 검증과 기존 근거 재사용

| 범위 | 이번 결과 | 근거 |
|---|---|---|
| 선형식 코어 | 새 10개 test method 첫 PASS | `evidence/LINEAR_BUDGET_CHECKS/` |
| 부분 반환 분류기 | 새 12개 test method 첫 PASS | `evidence/PARTIAL_RETURN_CHECKS/` |
| CLI·외부 DATA 연결 | 새 6개 test method 첫 PASS | `evidence/ANALYZE_BUDGET_CHECKS/` |
| 독립 제조 이론 | 20개 사례 PASS, 새 native 0 | `evidence/THEORY_REVIEW.json` |
| Wolfram | signed closure 0, 공유 reference 소거 0, 제조 product [9,11]/coherent [10,10] | `evidence/WOLFRAM_BUDGET.json` |
| 한 번의 분담 C9 | core/classifier와 CLI 연결 PASS, 중대 finding 0 | `evidence/CODE_REVIEW.json`, `evidence/CLI_CODE_REVIEW.json` |
| 실제 로컬 분석 | 18 DATA SHA 일치, admitted 0/4, reference-dependent rows 0, exit 1/HOLD, 오류 없음 | `evidence/LOCAL_NO_RETURN_BUDGET.json`, `evidence/LOCAL_NO_RETURN_CHECK/` |
| 새 인계 Bash | 구문 PASS, 실제 명령 미실행 | `evidence/NCP_HANDOFF_SYNTAX/` |

원래 HE29 science/test revision은 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner는 `f7830e2f55e7a1938bc3c98f61b60651f8dae474`다. 완성된 ABI2 최적화 코드는 `a5d4711460c09b310b78c9692aa62534b7a843d3`, VigilODE는 `a21d573980f66fe02891bd216153443b5352f921`을 유지한다. 이전 검증·가속 측정·clean build는 완료 근거로 재사용하고 다시 실행하지 않았다. 이번 새 분석기는 Python 표준 라이브러리를 사용하며 새 Rust 의존성을 추가하지 않았다.

## intake 근거와 한계

- `evidence/BASS_GITHUB_DELTA.json`: 83개 BASS_HE branch의 변경 대조, PR78 및 반환 채널.
- `evidence/RELATED_GITHUB_DELTA.json`: VigilODE·REI·REC·HH·BASS·bass_cr의 새 source/binary/result identity.
- `evidence/BACKUP_DELTA_INTAKE.json`: 이전 전체 census를 재사용한 최신 provider 변경분 및 실제 읽기 범위.
- `evidence/PERSONAL_CONTEXT_INTAKE.json`: 다른 대화 검색 오류 및 이전 파일 결과를 새 실행 완료로 사용하지 않은 근거.
- `evidence/LOCAL_INTAKE_AND_GAPS.json`: 로컬 native 부재 관측과 기존 분석 연결의 공백.

관련 프로젝트에는 새 실행 결과가 있지만 HE29 네 pair의 계약과 다르다. 다른 대화 검색은 실제 오류를 반환했고, provider 색인은 누락·날짜 필터의 한계가 있었다. 확인된 범위에서 새 HE29 기준해는 0/4이며 모든 대화·미게시 원격 실행의 완전한 부재를 증명하지 않는다.

## 다음 실제 실행과 인계

원래 m8/GL4/q0의 `(r2,512)`, `(r4,512)`, `(r8,512)`, `(r4,1024)`에서 각각 Radau+DOP853를 수행한다. 새 반환이 있으면 identity를 읽고 분석부터 하며, 완료 case는 다시 실행하지 않는다. 네 pair가 모두 admit된 뒤에만 단일 r4/table512 packed canary가 선택 가능하다. `NCP_HANDOFF_KO.md`의 분석 명령은 적분기를 호출하지 않는다.

실행 source는 Git의 고정 revision에서 가져오고 archive에서는 검증 DATA만 사용한다. 원래 baseline 인계의 두 overlay patch를 유지한다. 사용자에게 파일 다운로드·업로드·터미널 작업을 요구하지 않는다. 새 대화에서는 canonical `../NEW_CHAT_HANDOFF_KO.md`, 현재 `DELIVERY.json`, DAG 및 PR78의 실제 최신 상태를 먼저 읽는다.

연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 범위 검증 전까지 HOLD다.
