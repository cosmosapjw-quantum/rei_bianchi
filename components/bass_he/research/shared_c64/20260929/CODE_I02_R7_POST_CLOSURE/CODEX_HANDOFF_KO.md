# BASS_HE R7 handoff: closure 보존, 원문 회수, 다음 과학 범위 명세

## 목표

CODE-I02를 처음부터 다시 감사하지 않는다. 이번 사용자 제공 재심사는 current accepted domain/process-local runtime admission을 닫았다. 다음 작업은 원시 재심사 기록의 durable 회수와 source-normalization inventory다. Eq55 계산·물리적 승격은 이 prompt가 승인하지 않는다.

## 고정 identity

repo: cosmosapjw-quantum/BASS_HE
PR15 branch: audit11/dr11h-certificate-binding
expected HEAD: b8b2fe47a367459f6faf6796eb2f251feacbbd7c
expected tree: f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8
spectral.py blob: c41dc2bfacff6140fc130a787a856eae389a23b4
source/test predecessor: 8bf9ce27a39be06d2487fffd40c2b97a2cdb3e1a
PR17 branch: research/shared-c64-crossrepo-20260928
R7 이전 기준: 7b276609e828078826ad1969a264c5604c332c3f
R7 namespace: research/shared_c64/20260929/CODE_I02_R7_POST_CLOSURE/

root AGENTS.md와 최신 refs를 먼저 읽는다. PR15가 변경되었으면 강제 reset하지 말고 source diff를 확인한다. 이미 같은 closeout이 게시되었으면 반복하지 않는다. 기존 사용자 worktree의 reset/clean/stash/delete 금지.

## 상속하는 판정과 출처

사용자 스크린샷에 보고된 결과:
- Critical=0, Important=0, Minor=2
- invalid 24개 첫 anchor 전 거부, valid control 4개 허용, unexpected 0
- R5/DR11H 57 PASS, DR11G 3 PASS
- CODE_I02_CLOSED=true
- full_certificate_fail_closed=true
- scientific_PROMOTE=HOLD
- Eq55_next_node_authorized=false, Eq55=NOT_RUN
- outcome-blind=false: 검토자는 이전 구현 대화 맥락을 알고 있었다.

ChatGPT R7에서는 이 스크린샷을 읽었지만 원시 RETURN_REPORT.json을 읽거나 해시 검증하지 못했다. 이 구별을 지우지 않는다.

## 1. 원문 회수와 게시

원 실행 환경에서 다음 경로를 read-only로 확인한다:
/tmp/BASS_HE_CODE_I02_INDEPENDENT_REREVIEW_20260929T024343Z/
특히 RETURN_REPORT.json, ATTACK_MATRIX.json, 기존 명령/환경/로그를 회수한다. 파일 목록을 실제로 열거하고 없는 파일을 만들거나 원문으로 재구성하지 않는다.

있으면 target/source identity와 true/false gate를 대조하고 SHA256/크기/UTC를 manifest에 적는다. PR17의 새 timestamped namespace에 append-only 게시한다. 없으면 RAW_REVIEW_NOT_FOUND를 보고하고 사용자 제공 screenshot intake를 별도 근거로 보존한다. 이것만으로 CODE_I02_CLOSED를 false로 되돌리거나 동일 공격 행렬을 재실행하지 않는다.

## 2. 과학적 승격의 정확한 대상을 명세한다

PR15의 evidence/DR9B_EXPONENT_CHANNEL_AUDIT.json과 source-authority 문서를 읽는다. 기존 식/정규화 관련 기록을 SOURCE, DERIVED, BENCHMARK, OPEN으로 분리해 표로 반환한다. 과거 벤치마크를 다시 실행하지 않는다. 원 논문이 필요하면 authorized source의 정확한 파일/판/페이지/해시를 찾되 이 prompt에서는 Eq55 수치 계산·기본값 변경을 하지 않는다.

SCIENCE_SCOPE_DECISION.json에 아래를 반환한다:
- target_scope: SOURCE_NORMALIZATION_INVENTORY_ONLY
- runtime_gate: CLOSED_SCOPED
- current scientific_PROMOTE: HOLD
- current Eq55_next_node_authorized: false
- unresolved source-normalization claims and exact evidence references
- prerequisites explicitly present in authoritative project sources
- unsupported or ambiguous prerequisites: separately marked, not invented
- proposed next audit scope, with no implicit execution approval

Minor 두 개가 scientific HOLD의 원인 전부라고 추정하지 않는다. L2/Krawczyk, 모든 Nmax 수렴, 전체 물리 이론 증명을 새로운 필수 조건으로 삽입하지 않는다. 또한 "Critical/Important=0"만으로 scientific_PROMOTE를 PASS로 올리지 않는다.

## 3. 이식성 설계 방향

R7 제안은 원본 기록 O_A를 변경하지 않고, 다른 환경에서 명시적인 별도 재검증으로 O_B를 생성하는 두-record 방식이다. 기존 exact validator를 isclose로 완화하지 않는다. O_B에는 parent raw SHA256, exact input/policy/source identity, numerical-environment metadata, fresh fold/pair/error를 기록한다. 오류를 catch한 뒤 임의의 record를 조용히 덮어써서 통과시키는 fallback은 금지다.

이 prompt에서는 production wrapper를 구현하지 않는다. 필요한 최소 입력/output schema와 영향 파일, 승인·실행 한계를 설계 기록으로 확정한다. 동일 호스트 OpenBLAS thread 수 변화의 PASS를 cross-host PASS로 바꾸지 않는다. 새 환경을 만들거나 패키지를 교체하거나 paid cloud job을 실행하지 않는다.

## 4. SSOT

상수와 literal defaults의 현재 값 일치를 기록한다. 수치는 바꾸지 않는다. 다음 별도 maintenance patch가 필요하면 한 정책 선언을 constructor와 verifier가 공유하도록 제안한다. Python default의 definition-time binding 때문에 dynamic-global update 기능으로 잘못 설계하지 않는다. 이번 closeout에서는 production code를 수정하지 않는다.

## 실행/반환 계약

원문 회수 및 근거 inventory 외에 기존 24개 attack, 57/3 focused tests, 189 full tests를 반복하지 않는다. 새 코드 변경이 없으므로 compile/build도 이 작업의 통과 조건이 아니다. 연구 formula check는 이미 R7에서 실행됐으며 그 증거를 재사용한다.

금지: Eq55, production Eq50/54, 56-action replay, worker sweep, R1/R2 replay, bass_cr, HH, interval/Krawczyk L2 runtime, force-push, merge, user-worktree 정리.

최종 산출물: 원문 recovery manifest 또는 명시적 blocker, 원문 review record(실제 존재할 때만), scoped GATE_LEDGER, SCIENCE_SCOPE_DECISION.json, 다음 source-normalization audit용 독립 handoff. 실패 및 미확인 항목을 보존한다.

새 산출물은 기존 Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI와 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only 이중백업한다. 기존 동일 archive 중복 업로드 금지. provider ACK/object ID/size/checksum와 restore 여부를 분리한다. R0/R1/R2 충분한 경우 같은 바이트의 반복 다운로드를 하지 않는다.

성공은 모든 검사를 다시 돌렸다는 것이 아니라, 이미 닫힌 runtime gate를 보존하고 과학적 다음 단계의 범위와 남은 source authority를 명시적으로 확정했다는 것이다.
