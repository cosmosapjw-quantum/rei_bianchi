# C9 독립 코드·과학 검토 — borrowed-cell v2

## 판정과 검토 범위

**PASS: 명시적 실험용 `cell-borrowed` 경로의 유한 수치 동등성 및 지정한 clone 제거. SPEEDUP_NOT_ESTABLISHED: 속도 향상 승격은 발행하지 않는다.** Legacy 기본값과 기존 cell-cache 경로를 유지한다. root가 선택한 최종 후보는 v2이며, v1의 느려진 측정도 보존한다.

검토자는 이 코드를 구현하지 않았다. 동결 계약·원본 대비 diff·v1→v2 추가 diff·실제 빌드 입력/출력/종료코드·실행별 source/binary identity·원시 JSON·정상 복원과 forwarding receipt를 한 번의 C9 pass 안에서 읽었다. 직접 수행한 것은 읽기, 기존 JSON의 구조/수치 대조 및 검토 기록 작성이다. 빌드·native 재실행·코드 수정·Git 게시·업로드를 수행하지 않았다.

최종 binary SHA256은 `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`이다. final addon SHA256은 `1ae79973906390cf7966b415334c7f1ed17a86028d37226f2f03ebd33d727657`이며, 실제 빌드 입력·현재 compiled source·배송 patch가 일치한다.

## 코드와 실패 계약

원본 rate body에서 `self.template`를 `template`, `&self.nodes`를 iterator로 바꾼 것 외에 v1 helper의 산술 본문이 같음을 문자열 단위로 직접 확인했다. v2는 그 helper의 바깥 `for`만 `for_each`로 바꾼 두 줄 변경이다. closure 내부의 종 순서, 곱셈 결합, photo/binding/heat 누적, 세 compensated_add와 최종 nonfinite 검사는 동일하다. 이 closure에는 return/break에 해당하는 제어 흐름이 없고 같은 노드열을 끝까지 순회한다.

Borrowed view는 cache와 현재 state의 불변 참조 및 replacement 하나를 보유한다. 같은 짧은 lifetime으로 두 참조를 묶어 rate 평가 동안 유효성을 유지한다. 셀 오름차순 enumerate/map에서 해당 셀을 치환하고 flat_map이 셀 내부 순서를 유지한다. 빈 노드열은 그대로 비어 있다. replacement를 끝에 붙이거나 원래 셀을 함께 남기는 경로는 없다.

prepare_borrowed는 기존과 같은 shape 검증, changed 범위, 모든 support 및 미변경 셀 N/U stale 검사, 원본 prepare_cell 호출 순서를 유지한다. diagnostics의 세 max와 세 tail += 역시 같은 셀 순서이다. node_count는 replacement의 현재 길이를 반영한다. Context geometry 범위와 cache 생성 방식을 바꾸지 않았다. FD epsilon, charge/admissibility 순서, fatal/domain 구분, 단측 차분 정책, provider, tolerance, transaction/commit 코드는 그대로이다.

**노드 수 변화는 기존 threshold/steep 사례가 다룬다.** base mean은 lo+1e-4·width이고 replacement는 midpoint이다. 원본 알고리즘상 base는 steep branch의 16개 이상 패널(패널당 8노드), replacement는 regular branch의 threshold 분할(최대 4개 패널)을 사용한다. 따라서 새 endpoint fixture를 더할 필요가 없다. 이 수치 경계는 읽은 source에서 유도한 분기 설명이며, before/after 노드 수 자체가 stdout에 별도 기록된 실측값이라는 주장은 하지 않는다.

## 원시 실행과 수치 비교

| 항목 | v1 | 최종 v2 |
|---|---:|---:|
| Release build exit | 0 | 0 |
| Build process wall | 17.7511 s | 17.7851 s |
| Native focused suite | 4 unit + 6 integration PASS | 4 unit + 6 integration PASS |
| 기존 fixture replay | 19개 | 같은 19개 |
| 그중 Radau / SSPRK | 10 / 9 | 10 / 9 |
| 직접 읽은 raw 출력 | 60개 | 60개 |
| 그중 profile-off paired 실행 | 30개 | 30개 |
| 공유 물리 값·구조 차이 | 0 | 0 |
| 실행/모드/source/binary/counter metadata 문제 | 0 | 0 |

각 버전의 60건은 continuity control 2, 기존 설정 replay 19, warmup 6, paired 측정 30, 단일 profile attribution 2, forwarding smoke 1이다. 이는 같은 설정의 반복 실행 자료이며 새로운 물리 문제나 우주론 이력 60개를 뜻하지 않는다. 9개 SSPRK 설정은 native-evaluation budget 계수가 0으로, 새 borrowed Jacobian의 실행 증거로 세지 않는다.

독립 대조는 root의 두 시간/구현 메타데이터 항목만 제외하고 **나머지 전체 JSON 구조와 값**을 읽었다. 버전당 numeric leaves 2,272,828개, other leaves 360개, container 174,120개를 비교했으며 차이는 0이었다. 이 집계는 비교 대상 수이지 새 과학 실험 수가 아니다. null은 완료 실행의 `$.failure`에만 있었다. finite 비교이므로 signed-zero IEEE 비트 동일성을 주장하지 않는다.

P/C/R/D, CE/RR/DR/FF/CMB, photo binding/heat, escape와 cap/floor/excluded 진단, stage/endpoint 회계, 전체 photon/gas 상태와 모든 ledger를 비교에서 제외하지 않았다. 별도로 charged RHS, occupied-cell preparations, node visits의 불변성, 선택한 모드, profile 설정, CPU0 taskset 인자, 같은 binary SHA, stdout/stderr의 실제 완료 및 exit0을 확인했다. JSON의 mode/N/records 길이도 실제 argv와 맞췄다.

고정 N16의 실제 계수는 CellCache와 CellBorrowed 모두 RHS 2,992회, occupied-cell preparations 14,720회, node visits 1,914,880회이다. 그중 cached preparation의 state clone은 **2,704→0**, node clone은 **1,730,560→0**이다. 이는 지정된 두 clone 연산의 계수이며, 전체 할당·복사·bandwidth·RSS 측정이 아니다.

## 비용 판정

비율은 같은 binary의 \(t_{\rm cache}/t_{\rm borrowed}\)이며 1보다 작으면 borrowed가 느리다. 각 셀의 수치는 5개 pair의 비율 중앙값이다. 모드별 시간 중앙값을 나눈 수치와 혼동하지 않는다.

| 버전 | fixed | birth | disabled |
|---|---:|---:|---:|
| v1, external for | 0.760293 | 1.030526 | 0.979692 |
| v2, for_each | 0.932206 | 0.980651 | 0.879171 |

v2 pair별 native 비율 범위는 fixed **0.923228–0.955808**, birth **0.881621–1.117944**, disabled **0.678835–1.039799**이다. v2 process-wall 비율 중앙값은 각각 **0.999237, 0.876617, 0.940714**이다. 모든 원시 비율과 보고된 중앙값이 직접 재계산 결과와 일치한다.

두 버전은 별도의 측정 블록이므로 v1/v2 사이의 인과적 속도 향상도 이 표만으로 선언하지 않는다. profile-off 측정에도 항상 수행되는 계수 집계와 기존 progress 출력이 포함되며, process wall에는 실행·출력·부모 대기 비용도 포함된다. 단일 profile pair는 attribution 관측으로만 보존한다. inclusive Jacobian 시간을 exclusive 항목에 더하지 않는다. 단일 profile pair의 방향이 profile-off paired 결과를 대체하지 않는다. **이 데이터는 borrowed 경로의 일반적 가속이나 메모리 감소를 지지하지 않는다.**

## 원본 보존·배송과 발견 사항

- native original **152개**를 manifest와 직접 대조해 원본 바이트 차이 0을 확인했다. 이미 있던 **211-byte hook**과 parent 전체 파일도 이전 immutable 사본과 같다.
- VigilODE **477개** 파일은 고정 manifest와 일치한다. pin, Cargo.toml, Cargo.lock, batch source는 바뀌지 않았다.
- 정상 prepare-only 복원 receipt는 exit0이며, 복원된 native **153개**, adapter **7개**, VigilODE **477개**의 현재 바이트가 compiled source와 일치한다. 여기의 153개에는 additive addon이 포함된다.
- runner Python 기존 4개 시험은 v1에서 실제 exit0이었다. runner source가 v2에서 바뀌지 않았으므로 그 결과를 재사용했다. 최종 v2 forwarding smoke는 실제 CellBorrowed, exit0, 전체 물리 값·기존 작업 계수 차이 0이다.
- **C9-D1 문서 결함은 해결됐다.** v2 README가 처음에는 v1 timing을 버전 표지 없이 적었으나, 최종 문서에서 두 버전의 비율과 v2의 experimental-only 선택을 구분한 것을 읽었다. native 재실행은 필요하지 않았다.
- batch helper는 기존 cell-cache를 사용한다. 이번 수치/비용 증거를 borrowed batch 병렬 가속 결과로 표현하지 않는다.

원본 보존과 정상 복원 확인은 이번 C9의 변경 경로 검토이며, 백업 후 전체 과학 실행을 다시 요구하는 gate가 아니다.

## 유한 승인과 다음 전이

이 최종 diff에 대해 **지정 clone 제거와 기존 fixture의 finite numerical equivalence는 승인 가능**하다. 모든 과학적 HOLD — source-on 전체 2차, uniform stiff, 일반적 양수성·정확도, CaseB, fullEoR, signed Bianchi 및 넓은 CMB/boundary 범위, production — 를 유지한다. NCP 새 실행은 **NOT_RUN**이다.

**DAG: C9 COMPLETE → source/receipt 게시·양쪽 백업·인계.** 추가 native 실행, 선택적 재검증 또는 다른 최적화 변형을 승인 조건으로 요구하지 않는다. 독립 검토 원시 기록은 `C9_V1_RAW_READ.json`, `C9_V2_RAW_READ.json`, `C9_SOURCE_AND_DELIVERY_READ.json`이며 최종 구조화 판정은 `C9_VERDICT.json`이다.

