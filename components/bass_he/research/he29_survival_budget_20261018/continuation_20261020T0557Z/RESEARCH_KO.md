# HE29: 공유 기준해를 보존하는 signed budget과 부분 반환 분석

## 결과와 연구 위치

저장된 transport 결과와 동일 model/table의 독립 기준 후보를 연결하는 분석식을 구현했다. 핵심은 reference key를 공유한 상태로 선형 계수를 합치고, 마지막 단계에서만 후보 범위를 투영하는 것이다. 이 방식은 기준해 항의 정확한 상쇄를 유지하며, Radau·DOP853 두 후보의 선택 규칙을 출력에 명시한다. 원래 적분기·물리식·반응률·허용치는 바꾸지 않는다.

2026-10-20 05:57 UTC 재개 시 최신 GitHub·관련 저장소·백업·로컬 반환을 먼저 확인했다. HE29에 채택한 새 기준해는 0/4다. REI LRS 등 관련 연구의 새 native·합성·감사 결과는 source/binary/model identity가 다른 근거로 보존했다. 이 분석의 실제 reference-dependent 행은 입력이 들어올 때까지 HOLD다. 전체 intake의 관측 시점과 접근 한계는 `evidence/*INTAKE*` 및 `evidence/*DELTA*`에 있다.

### 유지한 identity와 완료 근거

| 대상 | 현재 연결 |
|---|---|
| 원래 HE29 science/test source | `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f` |
| HE28 parent | `a41dd37124e34cb22bb9782aaf687a0da91640b7` |
| native owner | `f7830e2f55e7a1938bc3c98f61b60651f8dae474` |
| 완성된 ABI2 최적화 | `a5d4711460c09b310b78c9692aa62534b7a843d3` |
| VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |
| 이번 시작 publication | `1765522318438e966e61d8a72f12084550da399d` |
| 기존 transport audit DATA | `evidence/reused/NATIVE_RETURN_AUDIT.json`, SHA256 `2bcd94edde08854599597ea8b962683a86cb5ca4af1ad0e1c3bec09b9e3c20cc` |

HE28 pilot·6/6 transport, HE29 90개 finite-donor 사례·720개 bound, 기존 50개 source/input 검사, VigilODE·Schur·ABI2의 완료 검사와 측정은 재사용한다. 이번에는 이 계산들을 실행하지 않았다. 원래 `analyze_return.py`에 존재하는 time difference·mixed difference·sign-change 계산도 반복하지 않았다. 원본 `a70` archive에서 저장 audit의 bytes만 복원했다.

## 1. 정의와 전제

모형 key를 $i=(r,N)$로 둔다. $r$은 strip refinement, $N$은 source table node 수다. 고정된 네 key는 $(2,512),(4,512),(8,512),(4,1024)$이며 모든 경우 m8/GL4/q0다. 저장 transport는 $N=512$에서 $r=2,4,8$, 시간 격자 $n=32,64$에 있다.

- $T_{i,n}^{\mathrm{tr}}$: 저장된 transport 최종 온도, 단위 K.
- $\theta_i^{R},\theta_i^{D}$: 동일 finite model/table에서 반환된 Radau·DOP853 최종 온도 후보, 단위 K.
- $T_i^*$: 해당 finite ODE 문제의 정확한 해를 나타내는 해석적 기호. 코드 입력이나 현재 확보된 수치 결과가 아니다.
- $\eta_i^m=\theta_i^m-T_i^*$: 기준 후보의 미지 적분 오차.
- $\tau_{i,n}=T_{i,n}^{\mathrm{tr}}-T_i^*$: transport와 해당 finite ODE 해의 차이.

실제 구현의 입력은 저장된 finite binary64 값이다. source·owner·binary receipt·table·parent/input manifest·numerical threads와 runtime provenance를 확인한 pair만 후보로 사용한다. 다른 case와의 대비에는 같은 provenance cohort를 요구한다. 같은 수치가 우연히 나타난 것과 같은 reference 변수를 구별한다.

이 단계는 endpoint 온도의 선형 후처리다. 새로운 closure, IC/BC, 반응률, metric convention 또는 단위 변환이 없다. 원래 full state와 19개 ledger를 다루는 적분 경로는 그대로 유지된다.

## 2. 부호를 보존하는 정확한 분해

방법 $m$을 고정하고 다음 잔차를 정의한다.

$$e_{i,n}^{m}=T_{i,n}^{\mathrm{tr}}-\theta_i^m=\tau_{i,n}-\eta_i^m.$$

같은 $N$에서 두 strip key $a,b$의 transport 차이는

$$\Delta T_n=T_{b,n}^{\mathrm{tr}}-T_{a,n}^{\mathrm{tr}}.$$

기준 후보의 차이를 $\Delta\theta^m=\theta_b^m-\theta_a^m$로 놓으면

$$\boxed{\Delta T_n=\Delta\theta^m+e_{b,n}^{m}-e_{a,n}^{m}}.$$

우변을 전개하면 $\theta_b^m$와 $\theta_a^m$의 계수가 각각 0이다. 따라서 같은 저장 입력에 대한 유리수 산술에서 closure residual은 정확히 0이다. 각 항의 절댓값을 먼저 취하면 이러한 부호와 상쇄 정보를 잃는다. 기존 `reference_runner.parent_comparisons`의 `temperature_error_K`는 절대 차이이므로 이번 signed residual은 원본 저장 온도에서 계산한다.

이 식의 물리적 사용은 두 부분을 나란히 읽는 것이다. $\Delta\theta^m$는 같은 방법으로 적분한 finite strip/table 모형의 대비이며, $e_{b,n}^m-e_{a,n}^m$는 그 기준 후보를 선택했을 때 남는 transport 대비다. $\eta_i^m$의 별도 상한이 없으므로 잔차를 참 시간 오차의 인증값으로 이름 붙이지 않는다.

같은 $r=4$에서 $N=512\to1024$의 경우에는 $\theta_{4,1024}^m-\theta_{4,512}^m$를 출력한다. 원래 transport DATA는 table512에 있으므로 table1024용 transport 결과를 만들어 넣지 않는다.

두 시간 격자에서 같은 reference key가 쓰이면 $e_{i,64}^m-e_{i,32}^m=T_{i,64}^{\mathrm{tr}}-T_{i,32}^{\mathrm{tr}}$이다. 이 cancellation은 코어의 대수 계약을 설명한다. 실제 HE28의 time/mixed 값은 이미 계산된 audit에서 읽으며, 이번 코드가 새로운 시간 수렴 차수나 mixed-difference 결과를 생산한 것으로 세지 않는다.

## 3. 두 후보 집합의 차이

각 model key의 후보 집합을 $C_i=\{\theta_i^R,\theta_i^D\}$로 정의한다. 이는 저장된 두 숫자의 집합이다. 참 ODE 해가 두 수치 사이에 놓인다는 전제를 추가하지 않는다. 원래 method agreement는 $|\eta_i^R-\eta_i^D|$를 제한하며 두 오차의 공통 성분을 측정하지 않는다.

후보를 결합하는 방식에는 두 가지가 있다.

### 3.1 Key마다 독립적으로 후보를 고르는 product 집합

$$C_{\mathrm{prod}}=\prod_i C_i.$$

공유 key의 계수를 합친 선형식을

$$L(\theta)=c+\sum_i a_i\theta_i$$

로 쓰자. $\ell_i=\min C_i$, $u_i=\max C_i$이면 정확한 최소·최대는

$$L_{\min}=c+\sum_i\min(a_i\ell_i,a_i u_i),\qquad
L_{\max}=c+\sum_i\max(a_i\ell_i,a_i u_i).$$

각 항은 그 key에만 의존하고, 유한 집합에 최솟값·최댓값을 달성하는 후보가 있으므로 모든 항의 선택을 동시에 실현할 수 있다. 따라서 이 결과는 주어진 product 집합의 tight hull이다. 계산은 key 수에 선형이고, $2^k$개 조합을 실제 열거할 필요가 없다. 작은 제조계 검사에서는 독립 corner enumeration을 oracle로 사용했다.

### 3.2 모든 key에서 동일 method label을 쓰는 coherent 집합

$$C_{\mathrm{coh}}=\{(\theta_i^R)_i,(\theta_i^D)_i\}.$$

이 집합의 hull은 두 완전한 방법별 선형식 $L(\theta^R)$, $L(\theta^D)$의 최소·최대다. $C_{\mathrm{coh}}\subseteq C_{\mathrm{prod}}$이므로 coherent hull은 product hull 안에 있다. 후보 방법 label이 공통으로 존재하지 않으면 coherent projection을 정의할 수 없다고 보고한다. HE29 production 경로는 원래 pair admission을 통과한 두 방법만 사용한다.

제조계에서 $C_a=\{1,2\}$, $C_b=\{11,12\}$이고 방법 label의 순서를 맞추면 $\theta_b-\theta_a$의 product hull은 $[9,11]$, coherent hull은 $[10,10]$이다. 어느 후보 집합을 사용했는지 명시하면 폭의 차이를 해석할 수 있다. 이 예시는 물리적 HE29 온도나 새 기준해가 아니다.

### 3.3 공유 key를 유지해야 하는 이유

같은 변수 $\theta$를 독립 interval 두 개로 바꿔 $\theta-\theta$를 계산하면 폭이 생길 수 있다. `LinearForm`은 key별 계수를 합산하고 0인 계수를 제거한 뒤 projection을 수행한다. 그 결과 동일한 key의 상쇄에는 후보의 폭이 영향을 주지 않는다. 반면 서로 다른 key가 같은 endpoint 값을 가진다는 이유로 두 변수를 합치지는 않는다.

공유 변수와 계수별 선형 연산은 affine arithmetic의 알려진 원리를 재사용한 것이다. Stolfi–de Figueiredo (2003)의 §3.2, §3.3.1–3.3.2가 직접 대응한다. 이번 코드는 비선형 AA·검증 적분기를 구현하는 대신, 저장된 유한 후보의 정확한 선형식만 다룬다.[1]

## 4. 저장 binary64와 최종 표시 반올림

온도 $T_a,T_b$를 각각 `Fraction.from_float`로 변환한 뒤 뺀다. `Fraction.from_float(T_b-T_a)`는 float 뺄셈이 먼저 수행된 다른 값을 나타낼 수 있다. Python의 `Fraction(float)`/`from_float`는 해당 float가 저장한 값을 정확히 나타내므로 각 operand에서 시작해야 한다.[2]

유리수 계수·상수·후보의 덧셈과 곱셈은 이 제한된 선형식에서 정확하다. 결과 JSON에는 exact numerator/denominator의 문자열을 보존한다. `nearest_float`는 편의용 수치 표시이며 경계 인증값으로 사용하지 않는다.

최종 exact lower $q$를 binary64로 변환한 값 $f$에 대해, $f>q$인 경우에만 `nextafter(f,-inf)`를 적용한다. upper는 $f<q$일 때만 `nextafter(f,+inf)`를 적용한다. 유한 범위에서 정확한 값의 이웃 표현으로 한 칸 이동하므로 바깥쪽 경계가 된다. 정확히 표현 가능한 endpoint는 움직이지 않는다. `math.nextafter`의 공식 정의를 사용한다.[3]

exact hull width와 float display width는 별도 필드다. exact point가 $1/3$처럼 binary64로 표현되지 않으면 표시 구간은 인접한 두 float가 될 수 있다. 반면 exact zero closure는 $[0,0]$이다. binary64 범위를 넘는 경우에는 exact 값을 보존하고 float 경계를 `null` 및 `OUTSIDE_FINITE_BINARY64`로 기록한다. 유리수는 signed zero를 동일한 0으로 취급하므로 이 후처리는 IEEE signed-zero bit identity를 주장하지 않는다.

## 5. 부분 반환의 의미와 admission

원래 runner는 각 method 파일을 최종 `RESULT.json`보다 먼저 저장한다. 한 method만 끝난 반환이나 timeout 기록은 분석할 정보가 있지만 pair 완료를 뜻하지 않는다. `partial_returns.py`는 다음 축을 분리한다.

| 축 | 읽는 자료와 판정 |
|---|---|
| 물리적 pair admission | 원래 `check_result`·`admit_pair` 재사용 |
| provenance | source/input/parent maps, owner, binary build receipt, 6점 qualification, table hash, thread/runtime |
| 반환 내용의 일관성 | method JSON과 RESULT의 값·호출수·comparison, qualification 일치 |
| process 관측 | 별도 COMMAND/RECEIPT, timeout, return code, stdout/stderr hash |
| 부분 진행 | absent, identity/table-only, one/both methods, completion 존재 여부 |

원래 절대 fraction $10^{-11}$, 방법 간 온도차 $10^{-9}$ K, number defect $3\times10^{-15}$/H, energy defect $3\times10^{-12}$ eV/H, species defect $3\times10^{-12}$, 양성성 기준을 유지한다. 추가 일관성 검사는 반환 provenance를 판단하며 물리적 허용치를 바꾸지 않는다.

한 case의 invalid 데이터는 그 case와 그에 의존하는 대비를 HOLD로 둔다. 다른 valid case와 다른 독립 대비는 보존한다. binary 경로를 제공하지 않으면 기록된 SHA와 build receipt를 검증하고 `binary_bytes_readback=NOT_PROVIDED`를 명시한다. 실제 binary를 제공하면 bytes를 읽어 SHA를 비교한다.

서로 다른 source/binary/runtime cohort의 pair를 같은 대비로 섞지 않는다. 현재 source는 원래 pinned 과학 파일을 재사용하고, source/input manifest의 이전 교정 근거는 `optimization_20261020/DELIVERY.json`에 있다.

## 6. 비용과 최적화 결과의 연결

새 reducer는 원래 원시 JSON과 작은 유리수 선형식을 읽는 작업이다. 네 기준해를 실행하거나 Jacobian·native RHS를 호출하지 않는다. 선형 projection은 살아남은 key 수 $k$와 method 수 $M$에 대해 $O(kM)$이며 현재 $k\le4$, $M=2$다. 여기서 별도 Rust kernel·병렬 runtime을 추가하는 비용을 정당화할 hot loop는 없다.

VigilODE a21 기반 ABI2 packed JVP, vectorized CSR, 정확한 cache key, Rayon의 독립 행 병렬화는 이미 `optimization_20261020`에 구현·게시돼 있다. 기존 제조계 paired 측정과 단일 thread 선택을 재사용한다. 최신 VigilODE PR76과 hybrid branch의 다른 모형 측정을 HE29 속도 측정으로 옮겨 쓰지 않는다.

반환의 method별 `wall_s`는 해당 적분에 사용한 시간이고, 최종 case `wall_s`에는 source 확인·qualification·table·두 방법·출력이 포함된다. packed canary의 전체 시간과 한 baseline method 시간의 비를 동일 workload의 speedup으로 계산하지 않는다. 새 출력은 각 scope의 원시 시간을 따로 보존한다. 실제 HE29 native 속도는 여전히 미측정이다.

## 7. 실제 검증과 남은 실행

- 독립 이론 검토: 원자료 대조, exact corner·outward rounding 제조계 20개 고유 사례. `evidence/THEORY_REVIEW.json`.
- Wolfram: signed decomposition closure 0, 공유 reference의 두 격자 cancellation 0, 제조계 product $[9,11]$/coherent $[10,10]$. 입력과 실제 반환은 `evidence/WOLFRAM_BUDGET.{wl,json}`.
- 새 선형식 코어: 10개 test method 첫 실행 PASS. `evidence/LINEAR_BUDGET_CHECKS/`.
- 새 부분 반환 분류기: 12개 test method 첫 실행 PASS. `evidence/PARTIAL_RETURN_CHECKS/`.
- 새 CLI 통합: 6개 test method 첫 실행 PASS. 외부 DATA 경로·공유 reference 소거·부분 반환·cohort·입력 거절·출력 보존을 확인했다. `evidence/ANALYZE_BUDGET_CHECKS/`.
- 새 test method는 총 28개(10+12+6)다. 독립 제조 이론 20개는 별도 범위이며 native 실행 횟수에 더하지 않는다.
- 독립 코드 검토: 한 번의 분담 C9 pass에서 코어·분류기와 나머지 CLI 연결을 검토했고 중대 finding 0이다. `evidence/CODE_REVIEW.json`, `evidence/CLI_CODE_REVIEW.json`. 검토자가 기존 검사를 반복하지 않았다.
- 실제 로컬 보존 DATA를 사용하는 새 CLI: 18개 입력의 SHA가 일치했고, 부재한 로컬 기준해 경로에서 admitted pair 0, reference-dependent row 0, 오류 목록 없음으로 exit 1/HOLD를 반환했다. wall time은 0.16578906699942308초다. 이 경로의 부재는 NCP 프로세스 관측이 아니다. `evidence/LOCAL_NO_RETURN_BUDGET.json`, `evidence/LOCAL_NO_RETURN_CHECK/`.
- 새 NCP 분석 Bash 블록의 구문 검사 PASS. 실제 인계 명령·적분기·기존 Bash suite는 실행하지 않았다. `evidence/NCP_HANDOFF_SYNTAX/`.

기준해가 없다는 사실은 현재 값이 필요한 reference-dependent 행에만 연결한다. 이론식·정확 산술·부분 반환 구현의 완료와 실제 HE29 native 실행의 미완료를 별도로 기록한다. NCP는 이미 준비된 네 기준해 작업만 수행하고, 반환 후 이 reducer를 실행할 수 있다. source는 Git에서 가져오며 원본 archive의 코드나 binary를 실행 출처로 사용하지 않는다.

## 원전·공식 문서와 채택 위치

[1] J. Stolfi and L. H. de Figueiredo, *An Introduction to Affine Arithmetic*, TEMA 4(3), 297–312 (2003), DOI [10.5540/TEMA.2003.04.03.0297](https://doi.org/10.5540/TEMA.2003.04.03.0297). [저자 원문](https://lhf.impa.br/ftp/papers/tema.pdf), §3.2, §3.3.1–3.3.2. SciSpace와 Exa로 찾은 원전 및 저자 프로젝트 페이지를 실제 읽었다. 공유 변수 보존 원리의 재사용 근거다.

[2] Python 3.12 official documentation, [fractions](https://docs.python.org/3.12/library/fractions.html), `Fraction(float)`와 `from_float`. 라이브러리 계약을 읽었으며 실제 실행 버전은 각 COMMAND/SCOPE receipt에 기록한다.

[3] Python 3.12 official documentation, [math.nextafter](https://docs.python.org/3.12/library/math.html#math.nextafter). 최종 표시 경계의 한 방향 이동에 사용한다.

Exa가 반환한 Comba–Stolfi (1993) 원논문의 검색 내용을 확인했고, author project의 선행 개발 계보를 읽었다. 일반 web 도구의 그 PDF 접근 오류도 보존한다. 위 유도는 정확 선형식에서 직접 증명되며, 원문 접근 오류를 성공으로 바꾸지 않았다. 추가 독립 문헌 대조는 `THEORY_REVIEW_KO.md`에 있다. 원전 PDF를 repository에 재배포하지 않는다.

## 절차의 현재 적용

초기 intake·분담은 당시 노출되어 실제 읽은 standalone 규약1.0.0을 사용했다. 이후 실행 환경이 명시 plugin1.3.0을 노출해 그 SKILL, selection, integrated policies, R/C 정의, subagent 및 evidence 계약을 읽고 이후 통합·검증·보존에 적용했다. 사용자의 명시 범위는 이론·경량 구현 검증·push·백업·두 handoff까지다. 이 전환 때문에 완료된 연구를 재실행하거나 현재 작업 범위를 줄이지 않는다. 한 번의 새 구현 검증과 한 번의 분담 독립 심사에서 실제 결함만 교정한 뒤 인계한다.
