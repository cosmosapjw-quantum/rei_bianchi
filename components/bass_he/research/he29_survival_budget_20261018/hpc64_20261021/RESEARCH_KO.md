# HE29: 64코어 자원 배분, exact table, native 기록 비용

## 연구 질문과 실제 출발점

이번 질문은 고정된 HE29 유한 모형과 a5/a21 solver를 유지한 상태에서 64코어/128 GB NCP의 독립 계산 구간과 기록 비용을 줄일 수 있는가이다. `a02ae998570d5a0a4fffdf46299ee77b1c738759`의 완료 근거를 재사용한다. 네 Radau+DOP853 pair는 이미 4/4 admitted, 같은 runtime cohort이며 저장된 09929 분석은 exit0이다. 기존 time/mixed/sign audit, finite-donor 90사례/720구간, HE28 transport6, 기존50 tests, VigilODE96 Python/3 Rust, Schur23, ABI2 clean build/benchmark, 분석28 tests, watchdog14 tests, dd wrapper9 tests를 다시 실행하지 않았다.

새 GitHub/관련 repo/백업/다른 대화 intake를 먼저 수행했다. 다른 대화는 실제 서비스 오류였고, 백업과 관련 repo의 조회 범위는 제한돼 있다. `evidence/GITHUB_DELTA_64C.json`, `BACKUP_DELTA_64C.json`, `PERSONAL_CONTEXT_RAW.json`, `PENDING_INVENTORY.json`이 실제 범위와 실패를 보존한다. 그 범위에서 새 HE29 반환은 없었다. 과거 ABI1/ABI2 canary를 중복 제거하면 현재 실행 준비가 된 미완료 HE29 과학 작업은 r4/table512 한 개다. 다른 분자·재결합·우주선 모형의 NOT_RUN은 같은 실행 계약이 아니다.

## 문헌과 도구가 기여한 범위

SciSpace는 새 병렬화 질문에 논문 metadata/abstract 10개를 반환했다. 그중 extrapolation 논문 3개 표기는 동일 연구이며 검색 결과 수를 독립 근거 수로 세지 않는다. [Utkarsh et al., 2022](https://arxiv.org/abs/2207.08135)는 방법 내부 병렬화를 위해 별도의 extrapolation solver를 구성한다. 여기서는 그 solver나 보고된 속도배율을 가져오지 않는다. 현재 고정된 적응 segment의 끝상태가 다음 segment의 초기값을 정한다는 실제 코드 의존성을 출발점으로 삼았다. Explicit ODE 방법의 병렬성 한계를 고정 implicit solver 전반의 불가능 정리로 일반화하지 않았다. 새 strong no-go나 신규 방법 우선권을 주장하지 않는다.

Exa로 [Python3.12 multiprocessing](https://docs.python.org/3.12/library/multiprocessing.html), [concurrent.futures](https://docs.python.org/3.12/library/concurrent.futures.html), [NumPy2.3 load](https://numpy.org/doc/2.3/reference/generated/numpy.load.html)를 직접 읽었다. 최초 검색의 Python3.15 결과와 NumPy stable2.5 표시는 실행 API의 근거로 채택하지 않았다. 명시적 spawn, import 가능한 worker 함수, persistent pool과 chunk 크기, object pickle을 쓰지 않는 NPY 및 read-only mmap을 확인했다. 초기화 비용이 있는 spawn을 무료 병렬화로 취급하지 않는다.

Wolfram context 호출은 실제 `Mcp error -32603 Internal error`였다. 동일 호출 재시도 없이 별도의 language evaluator에서 아래 비용식과 기록 개수를 실제 계산했다. 그 반환은 `evidence/EXTERNAL_RESEARCH.json`에 있다. 새 이론 계산은 완료된 shared-reference 소거식 검증을 반복하지 않는다.

## 1. 수치 순서를 보존하는 독립 행 분배

원래 proper-time source table은 interval i마다 동일한 guard와 `linspace`로 만든 시각 t(i,j)에 대해 원래 `ExactSource.source_moments(model,t)[0]`를 저장한다. r4/table512에는 17개 tabulated interval, 각각513행, 총8721행과640열이 있다. 이 함수는 native owner를 부르지 않는다. 각 worker가 독립적인 원래 모형 상태를 가지고 한 행의 산술을 그대로 수행하면 서로 다른 행의 실행 순서는 그 행 값에 들어가지 않는다.

새 구현은 하나의 spawn pool에서 기본64행 chunk를 분배한다. 반환된 배열은 완료 순서가 아니라 원래 `(interval,row)` 위치에 배치한다. 행 내부의 부동소수점 덧셈·곱셈·지수·축약 순서를 바꾸지 않는다. table hash도 기존 spec, cut bounds, source count/nodes, interval index, time/values의 little-endian binary64 순서를 그대로 사용한다. 마지막 diagnostics는 마지막으로 도착한 worker가 아니라 마지막 canonical 행의 report로 복원한다.

이는 다음 조건부 동등성이다. 같은 source/runtime/grid에서 각 행의 원래 함수가 같은 binary64 bytes를 반환하고 조립 인덱스가 일대일이면 전체 canonical bytes와 기존 digest도 같다. 병렬 실행이 그 조건을 자동 증명하지 않으므로 NCP에서는 반드시 기존 전체 table SHA `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd`를 재현해야 한다. 실패하면 solver에 진입하지 않는다.

Cache key는 exact source/runtime/thread/grid identity를 담는다. create-only 폴더, manifest, 각 NPY의 실제 크기/SHA/dtype/shape/finite/positive 조건과 원래 전체 digest를 확인한다. 실패한 partial cache는 지우거나 덮어쓰지 않는다. HIT의 `source_table_execution`은 최초 build 당시 metadata이므로 현재 새 worker 실행으로 합산하지 않는다.

이번 sandbox에서는 256×640 실제 source-row subset을 직렬과 spawn2-worker로 한 번 계산했다. 배열 SHA는 양쪽 모두 `e8e9bc6da74de2bd28af1994196135823b844ffd80593493bd4ed333ee2f8696`, 마지막 diagnostics도 일치했다. 새 cache/table 검사11개 첫 실행 PASS. 행 평가 직렬0.71276551초, spawn·초기화를 포함한 병렬1.17711341초였다. 작은 workload에서는 병렬 쪽이 느렸고, 측정 경계도 완전히 같지 않다. 전체 table 또는 64코어 가속률을 이 숫자에서 추정하지 않는다. 로컬 Python3.12.14/Clang과 반환 Python3.12.3/GCC의 cohort 차이 때문에 전체 golden table은 이곳에서 재구축하지 않았다. 원래 geometry clock 구성과 physical/native ODE 실행은 구별한다.

## 2. 병렬 비용과 64코어의 적용 범위

행 계산의 총 work를 W, 가장 큰 chunk의 work를 L, worker 수를 p라 하면 이상적인 계산 시간은 적어도 max(W/p,L)이다. 실제 시간에는 worker 시작, 모델 초기화, 직렬 직렬화/전송/조립, 파일 기록이 더해진다. 간단한 비용 모형 T(p)=s+W/p+a p에서 a>0,W>0일 때 연속 stationary point는 sqrt(W/a)지만, a와 W를 NCP에서 측정하지 않았으므로 이 식으로 최적 worker 수를 선언하지 않는다.

원래 r4/table512 두-method pair의 기록은 table45.13946915100678초, pair1190.317610485974초다. 이 원래 pair에서 table 비율 f는0.037922205597359493이다. 다른 비용을 그대로 두고 table만 p배 빨라진다는 가정에서 S(p)=1/(1-f+f/p), 무한 worker 상한은1/(1-f)=1.0394169845910492다. Wolfram의 미분값 f/(f+p-fp)^2는 0<f<1,p>=1에서 양수다. 이 상한은 원래 두-method pair의 비용 분해에 대한 서술이며 packed canary의 시간 예측이 아니다.

따라서 새 controller는 table/build/solver 자원을 분리한다. 실제 affinity, cgroup CPU quota의 ancestor 최솟값, 메모리 한도·current·MemAvailable, physical-core topology를 읽는다. table 상한48 worker, build 상한8 job이며 기본8CPU와 메모리 reserve를 남긴다. worker 메모리 예산은 scheduling estimate이고 전체 RSS의 증명된 상한이 아니다. table 배열44,721,288 bytes와 기존 임시배열 포함 estimate47,351,952 bytes도 전체 worker RSS와 다르다. 기존 다른 프로젝트 계약의 CPU55는 기본 제외한다. 관측할 수 없는 자원, 접근 거부, 다른 활성 과학 작업은 HOLD로 기록한다.

이미 완료된 thread1/2/4 측정에서2/4가 느렸으므로 packed solver는 thread1을 유지한다. 여러 method나 같은 canary를 동시에 복제해 코어를 채우지 않는다. 실행 순서는 관측/lease → 기존 source·baseline 확인 → bridge 재사용 또는 필요한 compile → table/cache → 한 canary → 기록 close/readback/admission이다. 과학적으로 준비된 job이 하나라는 사실을 64코어라는 하드웨어 명세가 바꾸지는 않는다.

## 3. Native 기록의 배치 확정과 바뀐 내구성 계약

원래 NativeOwner는 매 request/response JSON 기록에서 gzip flush와 fsync를 호출한다. 새 BatchedNativeOwner는 원래 persistent stdio protocol, 응답 검증, density/point 수치 입력, 호출 순서와 횟수를 그대로 상속하고 `_record`의 확정 주기만 조절한다. B=256에서 성공 point256개마다 확정하고, handshake·failure·segment endpoint·RAW result 직전·close에서는 반드시 barrier를 수행한다.

N개의 성공 point가 있고 별도 경계 flush를 무시하면 batch flush 수는 ceil(N/B)이다. 이전 네 pair의1,161,446 calls를 단순 대입한 값은4537이지만 이것은 새 HE29 실행 횟수나 실제 fsync 수가 아니다. 실제 구현에는 startup/failure/segment/trailer/directory 경계가 추가된다. 마지막 성공 batch barrier 직후부터 다음 barrier 이전까지 완료 반환된 point는 최대 B−1개다. B256에서는 hard kill 시 마지막 완료 fsync 이후 성공 반환 기록255개까지 durable하지 않을 수 있다. 이 정책은 원래 매 호출 내구성과 다르며, OS·하드웨어 전원 장애에 대한 절대 보증을 만들지 않는다. `--sync-every 1`로 매 호출 확정 정책을 선택할 수 있다.

정상 종료 또는 제어된 실패에서는 남은 기록을 확정한다. 최종 RESULT admission은 전체 gzip readback 성공, publish 성공, sticky I/O error 없음, written/durable/verified counts 일치를 요구한다. 모든 segment checkpoint는 native barrier 다음에 endpoint write/flush/fsync를 한다. fsync/close/readback 오류가 있으면 RAW·partial·실패 영수증을 보존하고 RESULT를 쓰지 않는다.

새 native protocol fixture11개 첫 실행 PASS. B1/3/256에서 원래 point의 binary64 bytes 및 모든 request/response 의미가 같았고, EOF/ERROR, 경계 flush, overwrite/symlink/race, fsync 실패 및 corrupt gzip의 admission 차단을 확인했다. 실제 gzip/fsync 제조 I/O benchmark는4096point×3정책×3반복, 총9 sample이다. timestamp를 제외한 event semantic SHA가 모두 같았다. 중앙값은 원본1.977382622초, 새B1 2.009102초, B256 0.609952585초였다. 원본/B256=3.241862844배는 이 I/O 범위의 측정이다. sample fsync 횟수는 각각4099/4100/20이며 HE29 solver 속도나 NCP64 성능은 아직 미측정이다. 기존 CSR8.35–8.78배, 제조 IVP1.38–1.53배 및 이번 I/O 배율을 곱하지 않는다.

## 4. 실행 경계와 보존

새 adapter Git pin과 원래 a5 bridge pin, ed5 watchdog pin을 따로 기록한다. source/manifest는 clean Git에서 읽고 DATA22만 baseline checkout의 외부 data-root에서 SHA 검증한다. archive source를 실행하지 않는다. build는 원래 Rust/Cargo1.94.1, frozen lock, generic x86-64 및 no-fast-math 계약을 유지한다. 새 compiler adapter는 실제 `--jobs N`과 `CARGO_BUILD_JOBS=N`을 일치시키고 BUILD_IDENTITY의 build_jobs 및 adapter provenance를 수정하여 원래 hard-coded2를 실제값으로 오인하지 않게 한다. 기존 정확한 bridge가 있으면 compile도 재사용한다.

원격 submission 도구는 새로 발견되지 않았고 RDC는0회다. 이 문서 작성 중 NCP 제출/시작0, 실제 원격 프로세스 UNOBSERVED다. 준비한 entrypoint는 NCP에 접근 가능한 실행자가 직접 관측하도록 만든 코드다. bounded directory scan, 기존 canary/partial/command identity, shared flock, dispatch 직전 process 관측을 사용한다. 관측 범위 밖 실행의 부재를 증명하지 않는다. 기존 반환이 있으면 새 실행을 HOLD하고 source/binary/table·raw 결과를 먼저 읽도록 반환한다. 어떤 기존 프로세스나 결과도 삭제하지 않는다.

## 변경하지 않은 과학 계약

절대 fraction1e-11, 방법 간 온도차1e-9K, number3e-15/H, energy3e-12eV/H, species3e-12, 원래 positivity, rtol1e-10 및 scaled-atol1e-12를 유지한다. 원래 gas/photon 및19-ledger 전체 state norm과 네 baseline pair gate를 재사용한다. 두 solver의 일치를 참 ODE 해의 오차반경으로 해석하지 않는다. finite-candidate hull은 저장된 후보 범위다. 연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 HOLD다.

단계별 실제 검사/검토/게시/백업 결과는 `DAG_STATUS.json`, `DELIVERY.json`과 `evidence/*DELIVERY*`, `*PUBLICATION*`, `*BACKUP*`, `C9_REVIEW*`를 읽는다. 이론과 코딩 단위의 완료가 NCP 과학 실행의 완료를 대신하지 않는다.
