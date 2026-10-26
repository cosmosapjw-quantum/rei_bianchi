# PW19 비열적 전자의 입자수–에너지 결합 연구

2026-10-27, 기준 commit `413729993919d21895e2196cc65f0c1c007e8614`.

실제 native REC 광이온화 항을 25좌표 source 연산자로 연결했다. 기존 21종 abundance에 비열적 전자수, 비열적 운동에너지, 외부 광자 에너지 전달량, log 온도를 추가한다. 이번 결과는 **REC-COUPLED의 검증된 부분 구성요소**이며 전체 원본 DAG는 **32/88 → 32/88(+0)**이다. 원래 노드의 전체 열적 결합·물리 불확실성·수렴 의무는 남아 있다. 검사 수를 원본 DAG 완료 수로 바꾸지 않는다.

현재 위치는 완료된 REC-EXP-SPECTRAL/REC-FIELD의 source를 REC-COUPLED에 연결하는 경계다. REC-EXP-COUPLED와 REI-L4, 최종 all-selected physical history pilot은 아직 열린 상태다. 중앙 통합본27/88과 미통합 작업 브랜치32/88도 구분한다.

## 이번에 유도하고 구현한 것

저장된 z=2.479 donor 상태와 승인된 PW19 He II 계수를 재사용했다. baryon 밀도는 n_b=10.669321142818111 m⁻³, 기체 온도는 T_g=14919.863839279506 K다. source 범위는 광자54.42–50000 eV, primary 전자 운동에너지0–49945.58 eV다. He3/He4의 전자 반응률 동일성은 기존 선택 모델의 조건으로 유지한다.

Y_i=n_i/n_b, ζ=n_nt/n_b, w_nt=u_nt/n_b, ℓ=log(T_g/1 K)로 둔다. w_ext는 J/baryon 단위의 부호 있는 외부 광자 전달 ledger다. 새 primary에 대한 초기 누적량 ζ=w_nt=w_ext=0은 이 source 삽입의 기준점이다. 실제 우주의 비열적 population이 모두 없다는 가정으로 확장하지 않는다.

전하 벡터 q에 대해 전체 자유전자수와 열적 입자수는

\[
x_{e,\mathrm{tot}}=q^TY,\qquad x_{e,\mathrm{th}}=q^TY-\zeta,
\qquad \chi_{\mathrm{th}}=(\mathbf1+q)^TY-\zeta.
\]

native `AtomicNetwork.evaluate(...)["photo_rhs"]`가 P=λGY를 실제로 계산한다. 두 HeII→HeIII 사건에서 S=Y_8+Y_11, e=qᵀP=λΓS다. 승인된 K_J, A_J는 target당 primary/흡수 power다. 구현한 proper-time source는

\[
F_Z=(P,\ e,\ \lambda K_JS,\ -\lambda A_JS,\ 0).
\]

핵종 수와 이온 개수는 보존되고 자유전자가 하나 생긴다. 그 전자를 비열적 subset ζ에 한 번 기록하면

\[
\dot\chi_{\mathrm{th}}=(\mathbf1+q)^TP-\dot\zeta
=\mathbf1^TP=0,\qquad
\dot x_{e,\mathrm{th}}=q^TP-\dot\zeta=0.
\]

비상대론적 단원자 열적 기체의 U_th=(3/2)n_b k_B T_g χ_th에서, 열화 이전의 선택 source는 Q_th=0이므로

\[
\dot\ell\big|_\gamma=
\frac{2Q_{\mathrm{th}}/(3n_bk_BT_g)-\dot\chi_{\mathrm{th}}}
{\chi_{\mathrm{th}}}=0.
\]

이는 충돌·열화 연산자를 제외한 순간 광이온화 source의 결과다. 열화 뒤의 온도 진화는 실제 number/energy assimilation 공급자가 결정해야 한다. 기존 REC124의 단일 열적 전자 가정은 별도 closure다. ζ를 도입한 뒤에도 그 코드의 x_e=qᵀY와 전체 열적 입자수를 그대로 사용하는 것을 허용하지 않았다.

직접 비교한 잘못된 조합은 동일한 비열적 입자 정의를 유지하면서 새 전자를 열적 입자수에도 넣는 경우다. 이때 생기는 가짜 희석항은 실제 상태에서
\(\dot\ell_{bad}=-1.377035638582512\times10^{-20}\,\mathrm{s^{-1}}\)다.
다른 closure 전체가 잘못되었다는 주장이 아니라, 선택한 입자 분할과 일치하지 않는 조합을 판별한 것이다.

## 불변량·미분·물리량

누적 이온화 에너지 I에 대해 IᵀP+dot(w_nt)+dot(w_ext)=0을 검사했다. 결합 에너지는 IᵀY가 소유하며 별도 중복 state로 추가하지 않았다. source의 Jacobian-vector product는

\[
\delta P=\lambda Gv+(GY)\delta\lambda,\quad
\delta e=q^T\delta P,\quad
\delta\dot w_{nt}=K_J[\lambda(v_8+v_{11})+S\delta\lambda].
\]

물리 밀도 source는 n_bF_Z, reference source는 βF_Z, η clock은 F_Z/H다. 각각 δn_b F_Z+n_bδF_Z, δβ F_Z+βδF_Z, δF_Z/H−F_ZδH/H²를 실제 source에 적용했다. n_b,T_g,H>0, Y≥0, AᵀY=1, λ≥0, 0≤ζ≤qᵀY, χ_th>0의 정의역을 유지한다. 확장·수송·충돌 항은 이번 순간 source 연산자의 외부에 있다.

| 축 | 이번 결과 |
|---|---|
| 대칭성·게이지 | 선택한 normal tetrad에서 등방 PW19 bath. 회전 대칭으로 primary pressure source의 STF 부분0. 고정 reference 정규화는 변수 변환이며 새 gauge 대칭으로 취급하지 않음 |
| 불변량 | 핵종별 핵수·baryon, 총 전하에 대응하는 전자수, 열적/비열적 전자 partition, binding+primary+external 에너지 및 접선 항 |
| 실제 계산량·관측 연결 | 순간 native21 abundance/전자 생성률, 에너지 source, 열적 응답 및 pressure source 경계. 관측 신호를 얻으려면 추가 history·transport·관측 연산자가 필요 |

| 실제 국소량 | 값 |
|---|---:|
| 전체 전자 생성 = 비열적 primary 생성 | 2.484719529390961×10⁻¹⁹ m⁻³ s⁻¹ |
| 열적 전자 생성 source | 0 |
| primary kinetic power | 7.949751527088791×10⁻³⁷ W m⁻³ |
| 올바른 pre-assimilation dot(log T_g) | 0 s⁻¹ |
| 선택 isotropic primary pressure-source 경계 | [2.6499171756962638, 5.2998343513925276]×10⁻³⁷ Pa s⁻¹ |

pressure 경계는 E를 전자의 운동에너지, M=m_ec²로 놓고 p v=E(E+2M)/(E+M)를 이용해 유도했다. 양의 source measure에서 dot(P_nt)=∫p v dS/3이므로 Q_nt/3≤dot(P_nt)≤2Q_nt/3이다. 유한 E_max로 더 좁은 하한 α(E_max)Q_nt, α=(E+2M)/[3(E+M)]도 유도했지만 새 상수 입력 없이 표의 보편 경계를 구현했다. 이 구간은 압력 closure나 진화된 Einstein source를 대신하지 않는다. 단일 평균 에너지로 spectrum을 대체하지 않았다.

## 실제 실행과 실패의 처리

| 실행 | 관측 결과 | 처리 |
|---|---|---|
| attempt01 | 28개 검사통과 후 부동소수점 상쇄를 정확한0으로 요구한 검사에서 exit1 | 원본 checker·manifest·출력·traceback 보존 |
| attempt02 | 검사 시작 전 보조 CPU 감시기가 종료; child0.001726 CPU s, wall0.002408 s, 새 검사0개 | /proc 감시 결과와 실제 rusage/wall의 불일치로 분류. 원인 하부환경은 미확정 |
| attempt03 | 동일 과학 입력·모델로 68개 새 검사통과, exit0 | 앞의28개 PASS 재사용, 실패·미실행 부분만 이어서검증 |

첫 교정은 원래 계약의 자연스러운 operand 크기 정규화와 2×10⁻¹⁴ 기준을 사용했다. 실제 signed thermal-count residual3.009265538105056×10⁻³⁶을 1.397307005458456×10⁻¹⁹로 나누어 약2.15×10⁻¹⁷을 얻었고 접선 잔차도 약2.24×10⁻¹⁷이다. 물리적으로 정의된 logT source의 정확한0과, 서로 다른 부동소수점 합의 상쇄 진단값을 구분했다.

두 번째 교정은 실행기만 바꾸었다. OS RLIMIT_CPU1 s, wall8 s, memory512 MiB와 단일 BLAS worker를 유지하고 모순된 보조 감시기를 제거했다. 실제 final child+측정 wrapper 사용량은0.133290770 CPU s다. 한도를 없애거나 물리 계산의 실패를 숨긴 교정이 아니다.

최대 대수 잔차는3.009182361116041×10⁻¹⁶(기준2×10⁻¹⁴), 최대 FD 잔차는7.00000026614723×10⁻⁹(기준2×10⁻⁸)다. h=.01과 δH/H=.001, δn_b/n_b=.01을 실행 전에 정했다. 입자수와 에너지 행은 서로 다른 단위·크기로 검사하고, 별도 두 사건의 oracle을 승인된 band Γ/K/A 값으로 만들었다. 원래 quadrature, donor 보간, IVP, 과거 성공 suite는 재실행하지 않았다. 독립 검토 결과와 그림 검토는 `review/VALIDATION.json` 및 `review/INDEPENDENT_REVIEW.md`에 연결한다.

## 재사용·문헌·전체 DAG 진행

작업 공간 정리로 사라진 파일은 기존 이중백업의 정확한2,792,870-byte ZIP/SHA256에서251개를 복구하고, 이후 게시된 영수증2개를 별도로 읽었다. 최신7repo 각2PR와 지정 중앙/예약 ref를 조사했다. 여섯 외부 producer head는 변하지 않았다. 모든 대화·모든 브랜치를 열람했다고 주장하지 않는다. HE101 예약과 기존 실패, H5 coverage0/313, H6의 실제 source-matched history 의무를 보존했다.

SciSpace·Exa로 확인한 Hui–Gnedin1997의 기체 입자수 항과 Furlanetto–Stoever2010의 fast/ambient 전자·열 전달 구분을 문헌 맥락으로 사용했다. 여기서 ζ를 통한 상쇄와 source/JVP는 직접 유도한 결과다. 기존 tritium DDEP 자료는 평가된 branch·수명·운동에너지 moment의 근거이며 finite-time stopping·완전한 daughter joint law의 근거로 확대하지 않았다. n/T 생성과 inverse-beta의 실제 공급자 의무는 열린 상태다. 자세한 원전 URL·검색 범위는 `intake/SOURCE_FINDINGS.md`에 있다.

| 내부 단계 | 이번 산출물 | 전체 원본 DAG |
|---|---|---:|
| R1–R2 / C1–C2 | 실제 백업복구, 최신source·예약·예산 확인 | 32/88 |
| R3–R5 / C3–C5 | source-only 선택, 입자수·에너지·pressure 경계 유도, 25좌표 구현 | 32/88 |
| R6–R7 / C6–C8 | Wolfram exact check, 실제28재사용+68신규 검증, 두 실패의 원인별 교정 | 32/88 |
| R8–R9 / C9 | 독립 검토와 구성요소의 scoped 채택; 원래REC-COUPLED는PARTIAL | 32/88 |
| R10 / C10 | plot·canonical 상태·보고서·handoff·게시·백업 | 32/88 |

known scientific planning 누적은 **12.196274495 CPU s**다. 실제 측정값과 각 phase의0.05 s startup/tail 보수적 reserve를 포함하며 미측정 비용은 UNKNOWN_NOT_ZERO로 남긴다. 일시14 CPU s(+40%) 한도는 종료했고 원래10 CPU s로 복귀했으며 debit을 초기화하지 않았다. main595.225063/600과 NO_MORE_IVPs를 유지한다. 그림·포장에는 별도 presentation 원래30→일시36 CPU s(+20%) 정책을 적용하고 완료 뒤30으로 복귀한다. 실제 최종 비용·게시 commit·두 provider 확인은 `FINAL_DELIVERY_RECEIPT.json`을 읽는다.

다음 물리 의무는 열적 전자에 들어가는 number와 energy 전달을 함께 주는 실제 assimilation/stopping 공급자 또는 명시적으로 승인된 선택 closure다. 이를 native RR/DR·Compton의 열적 전자 밀도와 연결한 뒤 full coupled residual/JVP 및 원래 observable error/convergence gate를 충족해야 한다. 이번 압력 구간과 순간 source는 그 연결의 검증된 입력으로 재사용한다.
