# HE29 HPC64 반환의 수치 판정과 성능 해석

## 1. 이번에 완료한 범위

`physmath-research-loop` 1.3.0의 이미 완료된 연구·구현 단계를 재사용하고, 실제 반환에 의존하던 C7/C8/C10 판정과 보존을 이어갔다. 새로운 이론 가정이나 solver 구현은 추가하지 않았다. 따라서 기존 SciSpace/Exa/Wolfram 조사와 62개 HPC64 검증을 반복하지 않았다. 새 코드는 solver를 호출하지 않는 `inspect_saved_return.py`이며, 실제 반환 JSON·raw gzip의 판독과 비교 보고서를 만든다.

원래 reference 네 pair `(r2,512), (r4,512), (r8,512), (r4,1024)`의 admission은 4/4 그대로다. 이번에 수령한 생산자 실행은 **m8/GL4/q0/r4/table512 packed canary 한 개**다. 이 문서의 소비자 실행은 과학 적분 0, native 호출 0, 기존 tests 재실행 0이다. 저장된 09929 분석도 다시 실행하지 않았다.

## 2. 실행 identity와 반환 bytes

| 역할 | 고정 identity |
|---|---|
| HPC64 실행 code | `802a32361288bf5aa0e0d1f63c912768f1a1d407` |
| ABI2 packed core | `a5d4711460c09b310b78c9692aa62534b7a843d3` |
| VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |
| native owner source | `f7830e2f55e7a1938bc3c98f61b60651f8dae474` |
| native binary SHA256 | `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9` |
| 새 bridge SHA256 | `28d637a9011ad0e23c087659cd07574cfb0ddc55511380c4c807165aee3123eb` |
| table SHA256 | `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd` |
| native gzip SHA256 | `2e917706b6a17c928ed6df1eb2271897d68f8de6070d839313c4a98a01c9acc8` |

소비자가 새로 읽은 bridge bytes의 SHA는 반환 BUILD_IDENTITY와 일치했다. 30,722,603-byte gzip 전체는 handshake 1개 + point 182,280개이며, 모든 record의 source/binary identity와 유한 wire 값을 확인했다. point마다 요청 11 field, 응답 23 field가 있었다. 정상 EOF와 gzip CRC를 통과했고, 생산자의 durable/verified count와 모두 일치했다. 이 182,281 record는 새 독립 test method 수가 아니다.

원래 owner 실행 파일과 table NPY 배열 및 원래 22 DATA bytes는 새 archive에 포함되지 않는다. owner는 이전 native admission에서 실제 bytes를 확인한 SHA와 이번 생산자 identity/handshake를 연결했고, table은 생산자의 고정 full digest 검사 및 이전 r4/table512 digest를 연결했다. DATA·parent/source·thread·runtime 계약도 이전 admitted baseline과 같은 것을 확인했다. 여섯 HPC64 adapter의 실제 Git source bytes는 이번 반환의 source map과 일치했다.

Python 3.12.3, NumPy 2.3.5, SciPy 1.17.0 및 기록된 platform 문자열이 baseline과 같다. 이는 수치 cohort 연결 근거다. 동일 host 부하, cache 상태, CPU affinity의 전후 성능 대조를 증명하지는 않는다.

## 3. 원래 수치 gate 판정

| 항목 | 새 canary 또는 두 기준해 대비 최댓값 | 원래 허용값 | 판정 |
|---|---:|---:|---|
| absolute fraction 차이 | 7.962109704190423e-20 | 1e-11 | PASS |
| 방법 간 온도 차이 | 1.1191048088221578e-13 K | 1e-9 K | PASS |
| photon number defect | 1.3129010682441655e-20 /H | 3e-15 /H | PASS |
| energy defect | 1.0625181290357943e-17 eV/H | 3e-12 eV/H | PASS |
| species defect 최댓값 | 7.030373462210693e-20 | 3e-12 | PASS |
| gas 양성성 / 최소 photon | true / 5.566682144744897e-20 | 원래 양성성 gate | PASS |

온도는 **8.239220060997875 K**, photon number는 **3.851175483221473e-8 /H**, photon energy는 **9.546047635593837e-7 eV/H**다. 19개 number/energy/species/binding/heating/escape/CMB/work ledger를 유지했다. 원래 rtol=1e-10, scaled atol=1e-12, solver thread 1과 663차원 상태(640 photon + 4 gas + 19 ledger)가 기록되어 있다. 허용치를 완화하지 않았다.

83개 segment가 원래 시간 범위를 연결하여 완료됐다. 저장된 counters는 accepted 7,889, attempts 12,565, rejected 4,676이며 native calls는 182,280이다. 선형 반복 2,968,046, JVP vectors 3,334,290 등이 기록되어 있지만, operation count만으로 각 내부 연산의 wall time을 정하지 않는다.

### 저장 후보 hull의 해석

저장된 두 reference 온도는 Radau 8.239220060997987 K, DOP853 8.239220060997964 K다. binary64 입력을 정확한 유리수로 읽은 signed 차이는 다음과 같다.

| 차이 | 정확한 binary64 입력 차이 | 표시값 |
|---|---|---:|
| packed − Radau | `-63/562949953421312` K | -1.1191048088221578e-13 K |
| packed − DOP853 | `-25/281474976710656` K | -8.881784197001252e-14 K |

기존 두 후보 hull의 폭은 2.3092638912203256e-14 K였다. 새 packed 후보는 그 아래에 있으며 세 저장 후보를 포함한 폭은 1.1191048088221578e-13 K다. 원래 방법 일치 gate를 통과한다는 사실과 기존 두 후보 hull 밖에 있다는 사실은 동시에 성립한다. 이 hull은 유한 후보들의 범위이며 참 ODE 해를 포함하는 증명이나 전역 오차반경을 제공하지 않는다. 기존 shared-reference closure 계산을 다시 실행하거나 그 과학적 범위를 확대하지 않았다.

## 4. 실제 측정한 시간과 64-core 활용

| 단계 | 실제 시간 | 포함 관계 |
|---|---:|---|
| bridge compile, build jobs 8 | 104.118856 s | canary worker 시작 전 별도 단계 |
| table pool, workers 48 | 2.790717 s | table/model/cache 단계 내부 |
| table diagnostics | 3.753131 s | pool 외 cache publication/readback 등 포함 |
| source model/cache | 3.808606 s | canary worker 내부 |
| packed solve/checkpoints | 710.211015 s | canary worker 내부 |
| owner close/gzip readback | 2.196970 s | canary worker 내부 |
| canary worker | 717.158505 s | 위 내부 단계들의 상위 timer |
| canary watchdog | 717.331125 s | 프로세스 감독의 전체 timer |

중첩 timer들을 합산하지 않는다. 원래 전체 canary 900초 예산 안에서 완료했다. 실제 affinity 64 CPU 중 CPU55를 보호하고 8 CPU reserve를 남겼으며, table은 관측된 서로 다른 48 worker, compile은 8 job, solver는 1 thread였다. memory available 131,378,446,336 bytes 및 reserve 27,010,105,344 bytes는 계획 시점 관측값이며, 47,351,952-byte table allocation estimate를 전체 RSS 상한으로 쓰지 않는다.

이전 직렬 table diagnostics 45.139469 s와 새 table diagnostics 3.753131 s의 저장 시간 비는 **12.0271**이다. 새 pool 2.790717 s만 분모로 삼은 16.1749는 timer 경계가 더 좁다. 둘 다 이전 실행과 이번 실행의 역사적 phase 비교다. 통제된 worker scaling 측정이나 전체 packed solver 속도향상 배율로 승격하지 않는다.

이전 1190.317610 s는 Radau+DOP853 두 기준해와 table/qualification을 포함한다. 한 packed canary 717.331125 s와 나눈 값을 speedup으로 사용하지 않는다. 이전 CSR 8.35–8.78배, 제조 IVP 1.38–1.53배, 제조 trace I/O 3.242배도 서로 곱하지 않는다.

현재 직접 관측한 병목 단계는 worker 시간의 **99.0312%**를 차지하는 packed solve/checkpoints다. 이 단계 내부의 native I/O, Python callbacks, GMRES/JVP, orthogonalization 시간은 분리 측정되지 않았다. 다음 최적화 질문은 이 내부 비용을 구분하는 것이며, 이번 완료 canary를 자동 재실행하거나 대규모 grid를 새로 배정하는 근거로 쓰지 않는다.

## 5. 실행 경계와 실패 보존

초기 준비에서 잘못된 packed checkout revision은 `HE29_HPC_GIT_REVISION`으로 실행 전 거절됐다. 그 기록의 build/canary/native 시작은 0이고 원본이 archive에 보존되어 있다. 이후 RUN_READY는 고정 code와 clean a5 checkout으로 한 번의 실제 canary를 완료했다.

사용자가 승인한 다섯 유휴 Codex process에 대해서는 PID + start_ticks + cmdline SHA가 모두 일치하는 일회성 예외를 사용했다. 원래 host_plan Git bytes는 바뀌지 않았지만, 외부 `sitecustomize.py` runtime shim이 존재했다는 사실을 명시한다. shim은 원래 scanner 결과와 raw allowed 목록을 보존하고 그 다섯 정확한 identity만 blocker에서 제외한다. 새 process나 identity 변경은 계속 차단된다. producer snapshot의 kill/signal count는 0이며, 이 소비자도 원격 process를 종료하거나 신호를 보내지 않았다. 해당 예외를 미래 실행에 재사용하지 않는다.

이전 SSH 인증 HOLD는 실행하지 못한 과거 시도다. 이번 실제 반환으로 current canary 상태를 COMPLETE로 갱신하며, 이전 authentication failure를 삭제하거나 전체 원격 process 부재로 해석하지 않는다. 현재 live NCP census는 이 소비자에서 수행하지 않았다.

## 6. Git 게시와 보존

원래 PR81 commit `d6c1cf97…`의 root tree는 결과 13개만 포함해 기존 base 파일을 누락했다. 결과 수치의 오류와 구분하여 처리했다. `fcdf56d9…`는 원본 결과 commit과 최신 base `4b7621…`를 모두 parent로 유지하고, base 6,189개 blob의 path/mode/SHA를 보존한 뒤 결과 13개 blob을 그대로 추가한 후속 commit이다. force push와 PR merge 없이 수정했다. 실제 PR readback은 changed files 13, deletions 0이며 결과 13/13 raw Git blob과 producer manifest 12/12가 일치했다. manifest 자체는 12개 entry 수에 포함되지 않는다.

생산자 archive a00990e5의 Dropbox·Drive raw PASS를 읽었고, 소비자 Dropbox raw SHA/content_hash도 일치했다. Outer payload20/member21 및 nested canonical payload39/member40 검증은 재사용한다. 중단 중 workspace pruning으로 사라진 로컬 사본은 같은 immutable Git과 archive에서 복원했고, 복원 GET은 새 과학 실행으로 세지 않았다. 한 차례 독립 수치 검토의 원본 임시 보고서도 pruning으로 없어졌으므로, byte-identical 보존을 주장하지 않고 실제 읽었던 범위만 별도 recovery 기록에 남겼다. 미완료였던 소비자 raw-gzip 판독은 이번에 실제 완료했다.

각 게시 단계의 readback 수와 archive member 수에는 중복 파일이 있으므로 합산하여 고유 파일 수를 만들지 않는다. 원본 데이터의 dual raw PASS는 과거 다른 archive의 Drive UNKNOWN을 해소하지 않는다. 이 단계 Drive/RDC 호출은 0이다.

## 7. 현재 다음 작업

**준비된 HE29 native 실행 queue는 비었다.** 네 reference pair와 한 packed canary를 반복하지 않는다. 새 실제 반환이 추가되면 그 identity와 변경분부터 읽고, 새 이론·코딩 연구가 필요해질 때만 SciSpace/Exa/Wolfram으로 다음 분별 가능한 질문을 진행한다. 새 solver, 격자 확대, thread 확대, 다른 모델의 미완료 campaign을 이번 queue에 자동 추가하지 않는다.

현재 수락 범위는 동일 유한 model/table의 packed canary와 원래 gate다. continuous spectrum, global temperature bound, full EoR, whole upstream Grackle equivalence, observational Bianchi/CMB 및 동일 packed 작업의 통제된 speedup 배율은 계속 HOLD다.
