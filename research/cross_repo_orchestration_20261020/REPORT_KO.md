# 원자·재결합·재이온화 저장소 통합 연구 루프 — 2026-10-20

이번 루프는 최근 결과를 먼저 합류시킨 뒤, 다음 외부 실행에 필요한 소규모 코드를 구현하고 독립 검토하는 범위로 완료했다. 새 물리 수치 실행은 REC의 저장 h4 상태 이후 2단계이다. HE 실행 제어기, BASS 에너지 전달 어댑터와 REI 고정 배경 반응률 오차 커널도 구현·검증했다. bass_cr의 기존 C21H/I는 정확한 백업으로 복원해 실제 게시했다. 전체 재이온화, 연속상태·완전기저·시간/각도 수렴이 완료됐다는 결론은 내리지 않는다.

## 1. 조사 범위와 실제 새 결과

요청 시각은 2026-10-20T09:55:50Z, 요청한 72시간 창의 시작은 2026-10-17T09:55:50Z다. 이후 게시/검토 시각은 별도로 기록했다. 여섯 관련 저장소의 현존 브랜치 목록과 각 고유 HEAD commit timestamp를 읽었다. branch의 최근 이동을 과거 commit timestamp만으로 복원할 수는 없으며, 지워진 브랜치·공유되지 않은 대화까지 포함한 계정 전체 완전성은 주장하지 않는다.

| 저장소 | 브랜치 | 고유 HEAD | 창 안 HEAD | 채택한 최신 기존 결과 |
|---|---:|---:|---:|---|
| BASS_HE | 83 | 82 | 4 | HE29 정확 예산/partial classifier, ABI2 구현; native reference 관측 0/4 |
| WU088_HH | 130 | 130 | 13 | PHYS71 단일 D3 전각·전반경 완료; PHYS70 최적화 L64 준비 |
| bass_cr | 163 | 160 | 8 | 기존 6개와 이번 복원 게시 2개 구별; C21H/I 완료 제조계 증거 회수 |
| bass | 259 | 251 | 7 | S9 8개 이력과 S10 최적화 완료; 추가 두 sibling 이론/구현 채택 |
| rec_bianchi | 128 | 126 | 10 | R3M h2 U6 5,210단계, R3O h4 시작, R3P 실제 16단계 및 최신 CI 성공 |
| rei_bianchi | 252 | 249 | 33 | RUN13 M2 회수, R9 terminal 회수, RUN19, LRS 최적화, age64, BR06 |
| 합계 | **1,015** | **998** | **75** | 각 lane의 조회 시각·범위가 inventory에 있음 |

모든 고유 HEAD metadata 조회는 성공했다. 최근 PR 본문과 중요한 source/result/검토/DAG 파일을 추가로 읽었고, 모든 브랜치의 모든 파일 본문을 읽었다고 주장하지 않는다. 대화 검색은 연결 오류로 완료하지 못했다. 이 대화에서 제공된 결과와 접근 가능한 GitHub·백업 영수증을 결합했다. 현재 NCP의 실제 프로세스·남은 할당은 직접 관측하지 못했으므로 모든 인계의 첫 단계는 현지 최신 결과·실행중 작업 확인이다. `wu088_cr`라는 별도 저장소는 확인되지 않았고, 확인된 `WU088_HH`를 명시적으로 사용했다.

Dropbox/Drive는 exact object ID, 검색 결과와 소유자 영수증을 구분했다. CR은 실제 archive bytes·payload를 복원 검증했고, REC는 최종 metadata ZIP을 새로 내려받아 CRC/8개 member hash를 확인했다. REI의 주요 7개 archive는 양쪽 provider metadata/size를 새로 대조했으며 대형 raw 전체를 다시 해시하지 않았다. HE 최신 budget archive의 Drive, HH PHYS70/71 Drive, BASS S10 Drive의 미확인/미완료 기록을 성공으로 바꾸지 않았다. 이번 새 전달물의 이중 백업은 별도 실제 ACK로 기록한다.

중요하게 갱신한 오래된 판단은 다음과 같다.

- HH의 예전 `D3_AND_HIGHER_REMAINDER=OPEN`은 D3 완료/고차 remainder 미완료로 분리했다. 확정된 값은 D3(21,20), m=0의 한 DtN 계수이며 절대 오차 상계 7.121295358370e-79 a0^-1이다. 단면적이나 열평균 반응률이 아니다.
- R9 Unit5 terminal은 이미 회수됐다. exit -9/wall limit, wall 1647.067초와 원래 만료 deadline을 유지하며 terminal 재회수나 동일 allocation 재시작을 지시하지 않는다. T4 spectrum/CDF refinement의 HOLD도 그대로다.
- RUN13 M2 standard/tight와 source 복원은 완료다. 6,241 intervals/40,357 variables, 원 integrator 누적 650.891853577초 기록을 재사용한다. finite-pair 차이는 continuum 인증을 대신하지 않는다.
- REC의 과거 CI 실패 알림은 최신 PR110 HEAD의 세 CI 성공으로 갱신했다. 완료 R3M U6/R3P smoke를 다시 계산하지 않는다.
- CR의 과거 publication rejected 기록은 보존했다. 새 사용자 게시 지시에 따라 C21H 595파일과 C21I 1,674파일을 복원 게시했고, 원격 각 파일 Git blob/size가 복원 map과 일치했다. 새 native 화학 실행은 없다.

## 2. 이론 연구의 결과

### 2.1 반응률 계수 오차에서 전하 분포 오차로

처방된 전자·온도·복사 배경에서 핵 하나당 population column p는 p'=Kp+b를 만족한다. 비대각 K_ij>=0, 각 column 합 0이면 전이 연산자 U(t,s)는 양의 column-stochastic이고 유도 l1 norm은 1이다. 연속 piecewise-C1 근사 p_hat에 대해 r=p_hat'-Kp_hat-b로 두면

\[
e(t)=U(t,t_0)e(t_0)-\int_{t_0}^t U(t,s)r(s)ds,
\qquad \|e(t)\|_1\leq\|e(t_0)\|_1+\int\|r(s)\|_1ds.
\]

원래 시간의 panel 폭 Δt와 증명된 연속 supremum R_l을 사용하면 E<=E0+sum_l Δt_l R_l+sum_event J_event다. 표본 trapezoid는 별도의 진단이며 certificate로 바꾸지 않는다. x=ln a를 쓰면 dt=dx/H를 정확히 한 번 적용한다.

양방향 i↔j의 계수 차이를 Δk로 쓰면 d_ij=Δk_f p_hat_i-Δk_b p_hat_j이고 정확한 defect는 sum d_ij(e_j-e_i)다. 이를 O(E+N)으로 조립하며 l1 norm은 2 sum|d_ij| 이하이다. 독립 절대 상계만 있으면 2 sum(η_f|p_i|+η_b|p_j|)를 사용한다. 두 방향의 **실제 동일 상대 섭동**이 증명된 경우에만 d=ε(k_f p_i-k_b p_j)의 순 flux 상쇄를 사용할 수 있다. 같은 오차 한도나 detailed balance만으로 이를 가정하지 않는다.

질량 오차가 0이면 관측량 w의 오차는 osc(w)E/2 이하이다. 질량 오차 상계 M이 있으면 |mid(w)|M을 더한다. 따라서 한 charge fraction에는 E/2, Li 평균 charge에는 3E/2가 적용되지만, source mass와 에너지 단위를 함께 보존해야 한다. 음수 population을 잘라서 정상화하지 않는다.

이 연결은 RUN19의 계수 수준 검증과 수치 residual의 역할을 명확히 한다. 현재 RUN19는 ln T 위의 value cubic이며 log-Hermite가 아니다. 15개 Grackle T-only 채널의 이상적 interpolation bound와 rounded stored-cell 검사는 재사용하지만, source/node/query rounding 및 feedback tube는 별도다. evolving T, n_e, opacity와 source가 K를 바꾸면 추가 Lipschitz/Gronwall 항이 필요하다. 새 커널의 float 결과는 outward-rounded machine enclosure도 아니고 full RUN19 궤적 승인도 아니다.

수학적 residual framework의 1차 출처는 Kormann–MacNamara, *Error Control for Exponential Integration of the Master Equation*, arXiv:1610.03232, https://arxiv.org/abs/1610.03232 이다. Exa로 원 논문을 확인했고 위 프로젝트용 edge/source/observable 식은 직접 유도했다. SciSpace 검색 결과 중 직접 맞지 않는 moment/SDP 논문은 채택하지 않았다. Wolfram은 Lagrange weight 합·Lebesgue factor·3/128 상수와 두 상태 column-generator/paired defect 대수를 확인했다. 원 응답의 Symbol 경고도 저장했다. xAct 실행 결과는 없으며 이번 스칼라 보존식·유한 행렬 계산에 xAct 검증을 주장하지 않는다.

### 2.2 BASS와 REI의 공통 에너지 전달

source owner가 eV/(H nucleus s)로 q_H를 제공하면 물리적 n_H[m^-3]를 써서 Q=n_H q_H eV_J [J m^-3 s^-1]로 변환한다. ln a당 값과 초당 값은 H를 정확히 한 번 적용해 변환한다. f_esc, spectral band, tilt/frame와 comoving/proper density를 별도 기록한다.

공간적으로 평탄한 해당 signed geometry의 constraint를 C=H²-s²-κ(U_d+U_gamma)-Λc²/3, κ=8πG/(3c²)로 두고 같은 Q를 donor와 radiation에 반대 부호로 적용하면 Cdot+2HC=0이다. radiation 주입과 donor 제거의 차이 δQ를 남기면 Cdot+2HC=-κδQ이다. Wolfram의 대수 검증을 저장했다. frozen-volume event의 실제 ΔU를 두 sector에 같이 넣고, floating-point 잔차는 TwoSum으로 추적한다. donor=1e20, radiation=1, transfer=1e19의 제조 예에서 단순 rounded debit/credit 차이가 감추는 총 에너지 손실 -1도 보고한다.

현재 REI `source_injected_energy_j_com3`는 누적 reference-comoving 양이다. 이를 실제 proper event ΔU로 대체하지 않는다. MD14 sourceID `MD14_Z002_FESC_BB50K_13P6_100_V1`는 처방된 방사원이며 물리 donor reservoir/pressure/초기조건을 정하지 않는다. C99 어댑터는 완료했지만 실제 paired proper-energy export와 donor closure가 준비되어야 coupled physical history를 실행할 수 있다.

### 2.3 HH의 다음 고차 remainder

원래 B=27a0, k=0.7, E=49/200Eh, R0=0.7과 outgoing Green G_D^+를 유지한다. K=V^(1/2)G_D^+V^(1/2), p_b=V^(1/2)f_b이면 복소 bilinear B에 대해 Z_lambda-Z_0=lambda B(p_a,(I-lambda K)^-1p_b)다. 실제 ||K||<=q, |lambda|q<1가 얻어지면 D1–D3 뒤 remainder는 |lambda|^4||p_a||||p_b||q^3/(1-|lambda|q) 이하이다. finite angular block과 infinite tail의 네 block norm을 weighted Schur estimate로 결합하는 구현 경로를 도출했다. 그 무한모드 상수는 아직 미계산이며 finite-L64 수치를 대입해 완성된 것으로 처리하지 않는다. HH_R10=OFF를 유지한다.

## 3. 실제 구현과 검증

| 저장소/변경 | 이번에 실제 수행한 검증 | 독립 검토/승인 범위 | 다음 외부 계산 |
|---|---|---|---|
| BASS_HE absent-only controller·fresh launcher·bootstrap overlay | 14개 focused 검사, 실제 source import/plan, zero-fuzz patch와 shell syntax; native 0회 | watchdog descendant 누수 수정 뒤 PASS_SCOPED | 기존 결과 조사 후 실제 미시작 reference만; 모두 admit된 뒤 ABI2 한 canary |
| WU088_HH | 완료 proof/panel/31측정 재사용, 새 물리 실행 0회 | PHYS71 단일 D3 기존 판정 그대로 | 기존 최적화 L64 runner의 아직 없는 현지 결과 |
| bass_cr C21H/I 복원 | 2,269파일 원격 blob/size 일치; 기존 32제조 ODE+2FD·Rust/stub 근거 재사용 | 게시 복원 완료; native 성능 아직 미평가 | G reference, H base→I vectorized 동등 fixture pilot |
| bass shared_q_bridge C99 | Decimal/Fraction 등 독립 oracle를 쓰는 11개 검사 | source review PASS_SCOPED; native dynamics 활성화 없음 | 컴파일/ABI 확인; physical input이 있으면 별도 paired pilot |
| rec_bianchi R3Q | 최종 실제 iz72900→72902,8FULL eval; original-C parity; 100파일 closure; 10개 집중검사 | 네 review 지적 교정, PASS_SCOPED; event 도달 미실행 | h4 첫 event+2; 기존 h2 low-z153,327단계 별도 |
| rei_bianchi rate_defect | 11제조 수학 검사; dense2/4/17 최대 차이 약2e-15 | fresh review PASS_SCOPED; 고정 bath 참조 계산 | 준비된 LRS cell-cache matrix와 age32 단일 사례 |

REC의 최종 smoke는 process-tree CPU 2.418778164초/wall 2.522254687초였다. 앞선 두 smoke는 산술 순서 교정 전 증거로 별도 보존했고 최종 판정은 smoke_003이다. 첫 event, 전체 h4, 원 U5 gate와 h/h2/h4 convergence는 HOLD다.

REI 두 상태 분석 제어에서 실제 오차 0.0862663 <= 해석적 적분 상계 0.548945 <= panel 상계 0.554294였다. 이 값들은 제조 제어계의 값이며 실제 Li 수치로 제시하지 않는다. 구현은 pure Python O(E+N) reference이며 native Rust/Fortran provider를 대체하지 않았다. REI의 지정 역할은 root 이론 계약→요청된 gpt-6.1-sol coder→fresh 독립 검토로 지켰고, 실제 backend model identity는 도구가 증명하지 않으므로 UNKNOWN이다.

## 4. NCP 조정과 남은 물리 의존성

서로 다른 repo의 프롬프트는 각각 복사해 실행할 수 있다. 각 Codex는 먼저 같은 host의 실제 CPU/RAM/디스크·기존 작업·source-bound 완료 receipt를 읽고 공동 할당표에 반영한다. 64core/128GiB라는 사양만으로 모든 capacity가 비어 있다고 가정하지 않는다. 특히 age32의48transport workers와 다른 대형 작업을 겹치지 않는다. 기존 process를 중단하거나 원 deadline을 초기화하지 않는다.

| lane | 제한과 선행조건 |
|---|---|
| HE29 | numerical thread1, case≤3600s 및 기존 DESIGN/전체 deadline, table≤600s; partial/실패 case 재시작 금지 |
| HH L64 | 기존 request, solver child900s/4GiB, build child900s; matching 완료 결과 우선 |
| CR G/H/I | native job300s, RHS/native calls200000, concurrency1, 보호CPU55 제외; H 동등 base가 I에 선행 |
| BASS | adapter1core; physical closure/export가 없으면 compile·입력대조까지만; 기존 paired job cap 유지 |
| REC | h4 event600CPU/900wall, 첫 event+2; 신규 명명 allocation. h2 low-z도 별도 원 runner의 유효 allocation |
| REI LRS | 새 optimized source만 19settings, case40s/native합180s; borrowed N2한개만 추가 |
| REI age32 | transport48/BLAS1, 한 사례1800s; 완료 age64 재사용 |

핵종/이온 확장은 기존 dossier·owner catalog의 provenance와 실제 rate/source provider를 연결해야 한다. 기존 17ion chemistry, Li/Be 후보, 넓은 핵종 inventory, molecular level과 HH scattering 채널은 서로 다른 모델이다. inventory에 존재함을 계산된 coefficient 또는 활성 production network로 해석하지 않는다. 새 dossier attachment의 byte는 이번 요청에 직접 제공되지 않았으므로 읽지 않은 새 첨부판을 확인했다고 하지 않는다.

다음 미완료 항목은 계속 명시한다: 물리적 daughter continuum·electron capture와 완전기저 closure, 저온 채널의 실제 threshold/provider·유효온도 범위, HH sigma(E)/k(T), source-driven xi, REC 전체 격자 coverage, RUN19 nonlinear gas/radiation tube, BR07 moment-energy admission, BRPERF01의 아직 checkpoint뿐인 부분, 실제 BASS donor model/paired ledger, full EoR/FLRW-CONV/BI-SIGNED/angular/time continuum. 이번 고정 배경 bound와 source adapter는 이들의 일부를 연결하는 준비이며 자동 승인 규칙이 아니다.

## 5. 연구 루프·게시·백업

이론 R1–R10은 문제/최신근거 정리, 재사용 판단, 모델·단위 계약, 잔차·보존식 유도, 계산 경량화, 반례와 조건, Wolfram 대수, 구현 연결, 독립 심사, 보고·인계로 수행했다. 코딩 C1–C10은 실제 source inventory, 좁은 delta, 역할 배정, 구현, 실패 원인 교정, focused 검증, 실제 REC smoke, source closure, 독립 review, 게시·백업으로 수행했다. 완료 표시는 이번 정의된 증분의 완료이며 전체 물리 프로젝트의 완료 수로 환산하지 않는다.

공개 변경은 기존 owner branch를 덮지 않는 별도 draft PR에 놓았다. CR의 복원 H/I branch는 content와 receipt commit을 분리했다. 공개 파일은 source/검토/요약/manifest/인계이며 대형 raw는 백업에 둔다. 초기 S0 intake snapshot, S1 검토 완료 code/evidence, S2 통합 결과·배송 기록을 구분한다. 새 archive 검증은 local manifest/CRC와 provider upload ACK/size 수준을 기록하며, 하지 않은 전체 remote readback을 성공으로 표시하지 않는다. Git content 생성과 현재 remote head 대조도 영수증에 기록했다.

정확한 실제 commit, 여섯 장문 인계, provider object와 단계 상태는 `INDEX_KO.md`, `CONTENT_PUBLICATIONS.json`, `DAG.json`, `BACKUP_DELIVERY.json` 및 저장소별 `DELIVERY.json`을 따른다. 현재 source와 실제 job context를 유지하면서 완료 산출물을 재사용하는 것이 다음 실행의 시작점이다.
