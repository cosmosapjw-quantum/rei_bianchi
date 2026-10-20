# 2026-10-20 정확 산술·캐시·독립 prefix 검증 최적화

같은 57,344 source nodes와 birth clocks 8/16/32/64에서 warm executable
중앙값을 원 47.413 s에서 **3.532 s(2 task threads)**로 줄였다. 원 입력과
과학 출력은 유지하며, 같은 2 task threads에서 13.424배다. 8 task threads의
중앙값은 1.560 s로, 2-thread baseline 대비 30.383배다. 이 두 번째 비율에는
task-thread 배분 증가가 포함된다. Compiler 설치·cold build는 별도 비용이다.

| 경로 | Task threads | 3회 중앙값 (s) | 원 baseline 대비 |
|---|---:|---:|---:|
| 원 구현 | 2 | 47.413 | 1.000배 |
| A: integer denominator Taylor | 2 | 10.461 | 4.532배 |
| B: indexed cache preload | 2 | 6.619 | 7.164배 |
| C: exact oracle 공유·모든 prefix parity | 2 | 3.532 | 13.424배 |
| C: 동일 경로 | 8 | 1.560 | 30.383배 |

## 식과 구현

`optimization_20261020/THEORY_KO.md`에 exact recurrence, Taylor enclosure,
cache independence와 prefix proof 재사용의 정당화를 연결했다. Reduced
optical depth `p/q`에서 `D_j=j*q*D_(j-1)`, `P_j=(-p)*P_(j-1)`,
`N_j=j*q*N_(j-1)+P_j`이므로 `N_j/D_j`는 원 S_j와 같다. S18/S19에서만
BigRational normalize를 수행하며 원 zero/752 guard·halving·directed
conversion/squaring은 유지한다. Public API는 일반 nonnegative rational을 받는다.

B는 같은 rate/later/earlier bit key의 실제 cache miss만 deduplicate하고
immutable rate에서 indexed Rayon map으로 계산한 뒤 serial insert한다.
Node reduction, affine tree, group 순서와 마지막 directed fold를 바꾸지 않았다.
C는 canonical 1-thread prefix의 exact rational inequalities를 한 번 확인하고
thread2/4의 모든 prefix bit와 비교해 같은 inequalities를 이전한다. 원 B의
반복 oracle 실행도 선택 가능하다. 원 VigilODE 두 모듈과 dependency vendor는
변경하지 않았다.

## 실제 확인과 교정

142개의 deterministic rational/경계 fixture에서 S18/S19의 exact rational 값과
최종 interval bits를 원 구현과 비교했다. 관련 Rust tests 4개가 통과했고,
전체 실제 입력에서 53,408 cached exp와 220 direct global-prefix exp, 합계
**53,628 endpoint-bit 비교**가 일치했다. 모든 B/C thread scaling과 반복의
scientific numeric JSON은 baseline과 일치했다. C는 4,448 exact group recurrences,
27,552 leaf inequalities, 64,000 all-prefix thread-bit 비교를 실제 수행했다.

초기 reference helper 추출의 중복 borrow compile 오류는 같은 수식을 유지해
교정하고 실패를 보존했다. 독립 C9는 요청 flag만으로 mode 활성화를 인정하던
runner 결함을 발견했다. 실제 출력의 flags/counters를 확인하도록 교정했고,
네 보존 출력 regression을 통과했다. Feature-free C에 reference mode를 요청한
실제 negative control은 numeric parity를 보존하면서 0/53,628 checks를 기록하고
`MODE_NOT_ACTIVATED`/exit1로 예상대로 실패했다. 최종 독립 C9는 PASS이며 C9-01 finding을 닫았다. 실제 범위와 근거는
`optimization_20261020/reviews/c9/C9_RECEIPT.json`에 보존했다.

누적 executable wall은 reference·wrapper·negative control까지 253.924 s/600 s,
각 command는 240 s 이하다. 과거 전체 test suite와 24-case/native 캠페인은
반복하지 않았다. 공식 Rust/cargo1.94.1, 22 locked vendor의 offline build가
작동한다. 원 baseline build13.556 s, fresh frozen-B source rebuild13.127 s다.
표준 최적 wrapper 실제 실행도 1.681 s/동일 scientific outputs를 확인했다.

## 자원과 벡터화 판단

B8의 preload0.931 s/전체4.597 s와 pair phases4.077 s를 보고 exact-oracle
공유와 독립 group 병렬화를 선택했다. C8에서는 preload0.855 s/전체1.456 s다.
Preload는 case/pair phase에 포함되므로 중복 합산하지 않는다. Hot exp는
arbitrary-precision integer polynomial과 proof-directed interval 변환이다.
Approximate SIMD exp/fast-math로 이 contract를 바꾸지 않았다. 추후 SIMD는
구체적 hot kernel과 같은 enclosure 증명을 갖춘 별도 최적화 대상으로 남긴다.

C2 median CPU6.581 s와 C8 9.132 s는 8 threads의 latency 감소가 이 표본에서
약38.8% 더 많은 CPU를 쓰는 선택임을 보인다. `--threads 2`는 economy,
`--threads 8`은 latency 선택이다. Standard-launch peakRSS는 baseline27,648 KiB,
C27,776 KiB이며 launch high-water를 포함한다. 메모리 감소나 kernel allocation
증가율을 추론하지 않는다.

## Intake·과학 범위·배송

새 REI BR06/LRS C11/RUN17/RUN18 및 VigilODE banded/JVP/residual-first 관련
parent intake의 선택 source/CSV/receipt 25개,331,424 bytes를 보존했다. Parent가
실제 읽은 upstream workflow39360079278은 2026-10-20 02:43:13Z에 completed/failure다.
이 run에서 새 완료 numerical result는 확인되지 않았다. 새 age32 완료 결과도
발견되지 않아 원 single age32 READY를 유지한다. 별도 upstream 실패를 이
고정 exp 모형의 실패로 취급하거나 그 lane을 재실행하지 않았다.

원 source labels·weights·fixed opacity/gas/geometry·정확도·B1 binary는 유지했다.
이 결과는 nonlinear native history/age 수렴 인증을 추가하지 않는다. Native
age/time HOLD, age64 source jumps MISSING_DATA, 원 age32 prompt/gates/cap을 유지한다.
현재 NCP는 DEVICE_LIST_SUCCEEDED이며 SSH는 NCP_SSH_NOT_PROBED_THIS_TURN이다.
원 월 사용량 중지는 역사로 보존한다. NCP 과학 실행은 NOT_RUN이다.

진입은 `optimization_20261020/run_optimized.py`, 상세 재현은 같은 subtree의
README/BUILD_MANIFEST/BENCHMARK다. 완료 benchmark는 재개 때문에 반복하지 않는다.
현재 source·v7 C8/C10은 PREPARED, GitAPI/provider 응답 전 게시·백업은 PENDING이다.
CURRENT5 원문은 baseline_current에 보존했고 최종 delivery receipt/confirmation은
source-bound archive 뒤에 생성한다. PR199 draft/no merge/no force-push,
owner checkout·PR150/R9·LRS·BASS·원 B1 보호를 유지한다.
**PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.
