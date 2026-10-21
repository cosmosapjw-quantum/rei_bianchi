# C9 독립 구현 검토 — 관측량별 source-age certificate

## 판정

**PASS — 열린 차단 지적 0개.** 검토 시각: 2026-10-20 06:17:13 UTC.

검토자는 이 단위의 구현·실행을 작성하지 않은 `/root/fresh_cloud_intake_v8`다. 앞선 역할은 외부 결과의 읽기 전용 intake였고, 이번 역할은 고정된 구현과 원자료의 독립 검토다. 별도 agent에 의한 독립성이지 다른 모델 계열의 검토를 뜻하지 않는다.

검토 범위는 동일 57,344 labels, clocks 8/16/32/64, all/sensitive/passive population의 고정-opacity 관측량과 해당 재현 runner다. 원 native 물리 소스, NCP 실행 및 nonlinear gas bound는 이 판정의 대상에 포함하지 않는다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다.

최종 Rust source SHA256:
`e4be362d8bb0c2920ea11465c3c194279ca75f155220656a67d7c62e2de9fc3a`.

## 수학과 구현의 대응

1. `lambda`, clock age와 age 차이는 입력 binary64의 정확한 유리수로 계산된다. 종별 share도 정확한 lambda 합으로 나눈 뒤 outward 변환한다. 기존 S18/S19 exponential enclosure와 directed arithmetic의 내용·hash를 읽고 재사용했다.
2. `k0/k1/k2`는 older-minus-younger 식을 평가한 뒤 A/B 방향을 정확히 반전한다. Energy와 species-event는 동일 `k0`에 각각 E와 -p를 곱한다. Signed moment에 비음수 clamp를 적용하지 않는다.
3. `kc`는 공통 생존인자를 분리한 centered 식이다. 두 방향의 centered upper에는 radius 보정과 signed-total DeltaN의 절댓값 상한 E0가 모두 들어간다. 양의 분모는 같은 population의 해당 방향 survivor mass 하한이다.
4. C와 2 Amax C의 global fallback, 두 centered upper와 global mean upper의 최소 선택은 각각 유효한 상한으로 구성된다. 저장된 binary64 endpoint를 정확한 Fraction으로 변환해 외향 산술 방향과 center radius·분모 대응을 독립 확인했다.
5. Passive lambda=0에서는 number·energy·event 차이가 0이며 age moment는 변할 수 있다. 64/64 stable kernel과 chosen bound는 정확히 0이다. 빈/분리 불가능한 분모는 UNRESOLVED로 남는다.
6. 수정된 cache는 각 실제 node가 사용하는 네 endpoint age와 세 delta age만 요청한다. Pair에서 필요한 min age는 두 endpoint 중 하나라 이 집합에 포함된다. Exact rational tau로 deduplicate하고 Rayon의 indexed map 결과를 직렬 삽입한다. 관측량 fold 순서는 node 입력 순서를 유지한다.

## 독립 reference와 원자료 읽기

Python verifier는 각 endpoint의 생존량·moment를 직접 계산하여 차를 구한다. Rust의 공통인자 stable kernel을 복사하지 않는다. Decimal100은 독립 고정밀 수치 검산이며 일반적인 초월함수 enclosure의 증명은 기존 exact-rational exponential 구성에 의존한다.

보존된 최초 연구의 612개 aggregate 검산과 revised 연구 사이에 scientific field의 bit parity가 성립함을 확인했다. C9 자체의 `check_saved_arithmetic.py`는 새 exponential이나 solver를 실행하지 않고 다음을 확인했다.

- 저장된 Decimal reference와 Rust interval의 포함관계 324개.
- 저장된 label·moment·centered upper와 reference의 대소관계 192개.
- 정확한 Fraction으로 계산한 최종 bound 산술 48개.
- Center radius 24개와 같은 population의 분모 연결 24개.
- Cache 수정 전후 scientific float **1,044개**의 packed IEEE64 bit equality.

이 수는 원자료의 별도 읽기 조건 수다. 새 물리 설정·새 native 실행 수로 세지 않는다. `SAVED_ARITHMETIC_READBACK.json`에 결과와 입력 해시가 있다.

최종 10개 Rust fixture의 stdout·exit·source binding을 읽었다. 마지막 fixture는 실제 tiny node assignments의 Cache, case, pair 전체를 Rayon 1/2 workers로 비교한다. 최종 binary와 실제 scratch compiled source를 각각 receipt hash 및 `observable.rs + cfg(test) include`와 바이트 비교했다. 입력 2개, 기존 Cargo.lock, 기존 library source 4개의 hash도 일치했다.

현재 plot을 직접 열어 확인했다. 세 population의 로그 초 단위 축에서 actual 차이와 chosen upper 및 global fallback의 관계가 CSV 값과 일치한다. 실제 변화가 비단조인 all population도 그대로 표시된다.

## 구체적 지적과 교정

### C9-01 — 새 output을 선택한 검산 연결

- **대상:** 새 `run.py`의 RUNTIME/results 또는 --out 경로와 기존 `verify.py`의 고정 HERE/results.
- **관측:** 초기 runner 변경 뒤 verifier는 새 실행 대신 보존된 이전 STUDY를 읽을 수 있었다.
- **영향:** 재현 명령이 새 source 실행을 검산했다고 오인할 수 있었다.
- **교정:** `verify.py`와 `summarize.py`에 --results를 추가하고 README의 세 명령을 같은 output으로 연결했다.
- **닫힘:** C9가 두 CLI를 존재하지 않는 별도 sentinel output으로 호출했다. 각각 기대한 exit 1과 지정 경로의 STUDY.json FileNotFoundError를 반환했다. 새 연구·exponential·plot 계산은 시작하지 않았다.

### C9-02 — 실패 로그의 output 재사용

- **대상:** --out에 STUDY가 없는 실패 attempt directory를 전달하는 경우.
- **관측:** 최초 guard는 STUDY 존재만 확인해 과거 BUILD 로그를 덮어쓸 수 있었다.
- **영향:** 실패한 실행의 원자료 보존이 깨질 수 있었다.
- **교정:** output은 부재하거나 비어 있어야 한다.
- **닫힘:** 구현자의 작은 filesystem preflight에서 비어 있는 경로 생성 및 실패 BUILD 로그가 있는 경로의 거절·원본 보존을 확인했고, C9가 실제 source guard를 읽었다.

별도 controller 지적이었던 불필요한 Cartesian exponent preload는 actual-node cache로 교정되어 346,945개에서 34,625개 unique tau로 줄었다. 이 교정 전후 raw 결과를 위 bit parity로 연결했다. 새 benchmark 반복이나 Decimal 재실행을 요구하지 않았다.

## 종료 범위

최종 wrapper의 경로·출력 guard·plot 표시 변경은 revised Rust 실행 이후에 적용됐다. C9는 source inspection, 실제 CLI 경로 negative controls 및 보존된 실행 identity로 이 변경을 검증했다. 전체 build/study/Decimal을 다시 반복하지 않았다.

Native age32는 별도 NCP READY이고 native age/time HOLD 및 original tolerance/gates는 유지된다. 현재 fixed-label 관측량 certificate 구현과 해당 검증 자료에 대해 승인 가능한 열린 구현 지적은 없다.

