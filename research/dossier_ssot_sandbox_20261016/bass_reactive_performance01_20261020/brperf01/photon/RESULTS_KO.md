# BRPERF01 photon 하위 단위 결과

**판정: `COMPLETE_VERIFIED_FROZEN_REFERENCE_CONTROL`.** 원 BR06의 동결 기체
광자 경로 연산을 유지하면서 실제 작업 재사용과 순서 보존 병렬화를 구현했다.
원 물리 owner, CX half-flow, four-corner 제어기는 수정하지 않았다.

## 최종 코드에서 직접 확인한 결과

아래 두 경우 모두 원 MD14/BB50k **384개 spectral/angular label**, 실제 출생
시각과 기하, 3,648개 labelled birth, 기존 반사 대칭에 따른 1,824개 unique
path를 사용했다. 출생 refinement 1, path slabs 2, opacity GL2, event GL4를
세 구현에 동일하게 적용했다. 표의 속도비는 각 baseline/candidate 쌍의
`log(baseline/candidate)` 중앙값을 지수화한 값이며, 두 시간 중앙값의 비와는
다를 수 있다.

| BASS 경우 | Baseline 시간 중앙값 | 2-worker 시간 중앙값 | 2-worker paired 속도비 | 개별 쌍 범위 | Cached serial 속도비 |
|---|---:|---:|---:|---:|---:|
| SIGNED_MINUS | 1.412278 s | 0.758894 s | **1.804729** | 1.708902–1.916326 | 1.018480 |
| SIGNED_PLUS | 1.471339 s | 0.807587 s | **1.775069** | 1.524901–1.960954 | 0.985805 |

각 경우 독립 프로세스 하나에서 2회 warmup, 7개 순서 교대 paired 비교,
3개 A/A 비교를 수행했다. 따라서 **위 병렬 속도 향상은 이 샌드박스의 탐색적
관찰**이다. VigilODE의 6개 독립 세션·30쌍·bootstrap/Monte-Carlo 확인 gate를
통과했다는 판정은 내리지 않는다. Serial 속도 개선은 관찰 변동과 구별되지
않으므로 `NOT_ADMITTED`다.

기하 캐시는 각 측정 직전에 비웠다. 두 worker는 각각 원 fixture와 기존
8,192-entry geometry cache를 소유한다. 원 fixture의 `Rc<RefCell>`를 억지로
공유하지 않는다. source 준비 시간은 각각 0.009753/0.008600 s, worker
초기화 시간은 0.030025/0.023312 s로 별도 기록했다. 전체 benchmark
프로세스 peak RSS는 14,160/14,248 KiB였으며, 이는 구현별 분리된 peak RSS가
아니므로 메모리 peak 감소의 증거로 쓰지 않는다.

## 실제로 제거된 반복 작업

| 작업 | SIGNED_MINUS | SIGNED_PLUS |
|---|---:|---:|
| 원 virtual path sample 수 | 111,873 | 110,706 |
| 제거한 opacity 임시 heap allocation | 37,194 | 36,811 |
| 제거한 누적 allocation payload | 1,190,208 bytes | 1,177,952 bytes |
| EOS 호출 | 111,873 → 1 | 110,706 → 1 |
| Gauss rule 생성 | 3,648 → 2 | 3,648 → 2 |

EOS·density·threshold는 immutable frozen context에 묶어 준비하고, 실제
시간별 photon energy에 대한 cross section은 매번 원 owner로 계산한다.
원 birth-ray 생성의 첫 정규화만 재사용하고, 이후 Killing pullback은 원
구현을 호출한다. 적분 내부의 합산 순서, 양의 경쟁 흡수 사건, heat·chemical·
geometry-work 계산, inverse iteration과 virtual work count는 그대로다.
배열 scratch는 active path당 1,024 bytes이며, peak 메모리와 누적 allocation
churn을 구분했다. 출생 기록의 합치기나 source opacity의 에너지 보간은 없다.

## 검증과 독립 검산

**최종 Rust 11/11 PASS, strict Clippy all-targets PASS, scoped rustfmt PASS.**
최종 두 경우에서 모든 unique path의 **41개 semantic word**와 최종 ordered
ledger의 **33개 word**를 원본·cached·parallel 사이에서 실제 바이트로
대조했다. f64 값, 방향, species별 사건과 heat, chemical energy, geometry
work, residual, iteration/sample count, underflow flag가 포함된다.

별도 Python 검산은 raw 파일의 전체 바이트와 SHA-256, source label 완전성,
출생시각·age, Killing 성분, 비음수 사건수, number/energy/age moments를
검사했다. 원 BR06 `run`의 처음 8개 template에 해당하는 **112개 birth 행**의
입력 metadata도 비교 가능한 모든 f64 비트가 일치했다. 최대 path number
residual은 두 경우 모두 4.44e-16이었다. Python Killing 성분 재구성의 최대
상대 차이는 0이었다. 작은 보존 잔차를 별도의 시간·분광 정확도 증거로
사용하지 않았다.

독립 reviewer는 가스/owner 의존성, 원본 적분과 변환 스크립트의 산술,
reflection key와 reduction 순서를 대조했다. 이 과정에서 prepared context
사이의 입력 identity가 충분히 묶이지 않은 API 틈을 발견하여, fixture
lifetime·pointer identity·worker semantic identity 거부를 추가했다. 이
수정 전 측정도 모두 올바른 fixture를 사용했지만, **최종 코드의 속도는 위
두 최종 재측정만 근거로 제시**한다. worker 사망 뒤 자동 복구는 주장하지
않으며, 정상 worker가 반환하는 `REFERENCE_WORK_LIMIT` 뒤 재사용은 테스트했다.

Fresh restore는 새 crate, BR06, parent, native 입력, 고정 VigilODE source의
**640개 payload**를 ZIP에서 꺼내 각각 SHA-256을 확인한 뒤 새 source 경로를
실제로 컴파일하여 **11/11 테스트**를 통과했다. 검증된 Rust1.94.1과 99개
registry package 환경은 별도로 재사용했다.

복원 ZIP SHA-256:

`12984e45b9cffff4a20a3afbe08c8d4d30b507692148ae4c991c0c4ebaf5f299`

## 판정의 한계와 다음 DAG

현재 결과는 기록된 0–5e11 s step의 frozen reference-comoving gas와
시간가변 BASS 기하에서의 성능·동일성 검증이다. 진화하는 H/He/D gas 계산,
longspan 정확도, 출생연령·분광 수렴, 일반적인 2차 정확도, Einstein 양방향
feedback을 새로 입증하지 않았다. 이 하위 단위에서 추가 핵종을 활성화하지
않았다.

다음 작업은 unchanged donor inversion을 실제로 profile하여 serial 시간의
주원인을 정량화하는 것, 충분한 독립 세션을 확보한 성능 확인 gate, 그리고
별도 native evolving-gas admission이다. `LONGSPAN_SOLUTION`은 계속
`NOT_ADMITTED`로 유지한다. GitHub·Drive·Dropbox 게시와 전체 연구 DAG는 root
단위가 통합한다.
