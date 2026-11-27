# HE-EXP-EVENT-03: 반응성 두 입자 사건의 유한질량 모멘트

## 질문과 범위

WU R4의 새 LiH/HD source records를 기존 HE source inventory에 연결한다. 새 계산은 지정된 비상대론적 `a+b -> c+d` 사건의 미분 단면적 모멘트에서 입자수, 운동량, 운동에너지 및 2차 모멘트를 함께 만드는 조건부 공급자이다. WU의 열적 계수를 미분 단면적으로 역산하지 않는다. REC/WU의 상태·branching, CR의 분포·cascade·stopping 소유권을 소비한다.

기존 INTAKE01의 `AngularTransport`, `ConservativeSource`, caloric adapter를 재사용한다. DRIFT02의 같은-law 유한 드리프트 계산과24검사, HE101의열린C8와예산은 그대로 둔다. 아래는 기존 탄성식을 반응성 `2 -> 2`로 확장하는 직접 유도이며 새로운 일반 불가능성 정리나 최초성 주장이 아니다.

### 고정 가정

- 한 사건의 정확한 네 species/state IDs와 labelled-pair-once count convention을 준다. 같은 ID의 gain/loss는 합한다.
- 관성질량은 조성에 따른 고정 비상대론적 질량으로, `m_a+m_b=m_c+m_d=M`이다. 실제 rest masses의 결합 에너지 차이를 이 가정에 조용히 넣지 않는다. 질량합 검사는 binary64 반올림 범위만 허용하며 관측된 residual을 기록한다.
- 상태 에너지 `epsilon_s`는 같은 조성 영점에 대한 내부 에너지이다. `Delta=epsilon_c+epsilon_d-epsilon_a-epsilon_b`이고 양의 Delta는 흡열이다. 관성질량에 이미 넣은 결합/내부 에너지를 다시 epsilon에 넣지 않는다. 이 모델은 `v/c << 1`, 상태 에너지의 mass-energy correction을 무시하는 정밀도에서만 사용한다. 실제 질량/상태 오차의 물리 배정은 별도 의무다.
- 이 단위의 내부 에너지 소유권은 `population_derived_internal_witness`로 고정한다. `sum epsilon_s Gamma_s`는 population 변화의 에너지 증거이며 독립 내부 에너지 RHS로 또 가산하지 않는다.
- CM에서 입사 상대속도 축에 대해 축대칭인 완전각 공급자를 준다. 편광/외부축/비축대칭 또는 다체·광자 생성에는 별도 공급자가 필요하다. 특히 Li+H radiative association은 이 커널의 적용 대상이 아니다.
- 입력/출력은 유한 binary64로 표현되는 범위다. 물리 support 밖 입력, 음의 measure, 부정합 질량합, 불가능한 각모멘트, overflow/의미있는 양의 곱의 underflow는 명시적 오류다. 테스트 tolerances는 algebra/roundoff용이며 물리 source uncertainty가 아니다.

## 1. 두 입자 운동학

`g=v_a-v_b`, `V=(m_a v_a+m_b v_b)/M`, `mu_in=m_a m_b/M`, `mu_out=m_c m_d/M`로 둔다.

\[
E_{in}=\frac{\mu_{in}}2 |g|^2,\quad E_{out}=E_{in}-\Delta,\quad
p=\sqrt{2\mu_{out}E_{out}},\quad e=g/|g|.
\]

열린 branch는 `E_out >= 0`이다. 반응 후 `v_c=V+(p/m_c)n`, `v_d=V-(p/m_d)n`, `|n|=1`이다. 따라서 각 사건에서 운동량은 보존되고 운동에너지 증분은 `-Delta`다. 임계점 `E_out=0`에서는 두 생성물의 상대속도가0이다. `g=0`일 때 입사축은 정의되지 않으므로 이 인터페이스에서는 등방 모멘트만 허용한다. 이는 실제 저에너지 cross section 또는 `g sigma`의 극한을 대신하지 않는다.

## 2. 최소 각모멘트와 양성성

기존 표기와 같이 `sigma_0=int d sigma`, `sigma_l=int(1-P_l(cos chi)) d sigma`, `l=1,2`를 쓴다. 다음 weighted moments를 둔다.

\[
L_1=\sigma_0-\sigma_1,\quad L_2=\sigma_0-\sigma_2,\qquad
N=\int nn^T d\sigma=\frac{\sigma_2}{3}I+L_2 ee^T.
\]

`int n d sigma = L_1 e`. `sigma_0>0`이면 `h=L_1/sigma_0`와 `z=(1+2L_2/sigma_0)/3`는 `-1<=h<=1`, `h^2<=z<=1`를 만족한다. 이 조건은 기존 `AngularTransport.validate()`가 검사한다. 각모멘트는 측정/선택된 law의 입력이지 열적 반응률로 채우는 기본값이 아니다.

## 3. 생성물의 raw 모멘트

생성물c의 단면적 가중 입자수는 `sigma_0`이고 다음과 같다.

\[
P_c=\sigma_0m_cV+pL_1e,\qquad
K_c=\sigma_0\left(\frac{m_cV^2}{2}+\frac{p^2}{2m_c}\right)+pL_1 V\cdot e,
\]
\[
S_c=\sigma_0m_c VV^T+pL_1(Ve^T+eV^T)+\frac{p^2}{m_c}N.
\]

d는 `m_c -> m_d`, 선형p항의 부호를 반대로 둔다. `S_s=int m_s v_s v_s^T d sigma`이고 `tr S_s=2K_s`다. 반응물a,b에서는 각각 `sigma_0`, `sigma_0 m_s v_s`, `sigma_0 m_s |v_s|^2/2`, `sigma_0 m_s v_s v_s^T`를 뺀다. 같은 species ID로 gain/loss를 모으면 `Delta N_s,Delta P_s,Delta K_s,Delta S_s`를 얻는다.

\[
\sum_s m_s\Delta N_s=0,\quad \sum_s\Delta P_s=0,\quad
\sum_s\Delta K_s=-\sigma_0\Delta,\quad
\sum_s\epsilon_s\Delta N_s=\sigma_0\Delta.
\]

이들은 같은 사건에서 함께 나온다. 생성물 marginal들을 독립 추출하는 절차를 쓰지 않는다. 각각의 단위는 `m^2`, `(kg m/s)m^2`, `J m^2`, `J m^2`이다. 속도분포 소유자가 `int f_a f_b |g| (...) d^3v_a d^3v_b`를 공급한 뒤에야 부피·시간당 source가 된다. 단일 입력속도 pair에 대한 명시적 encounter flux는 `n_a n_b |g| [m^-5 s^-1]`이다. 동일 입자 count convention 및 대안적 provider 선택은 그 사건 소유자가 한 번 처리한다.

## 4. 열적 에너지와 입자수의 분리

부피·시간당 raw source `Gamma_s,R_s,E_s`, 고정종 질량 `m_s`, 소비자 bulk `u_s`에 대해 기존 어댑터를 그대로 쓴다.

\[
Q_s=E_s-u_s\cdot R_s+\frac12m_su_s^2\Gamma_s,
\quad F_s=R_s-m_su_s\Gamma_s.
\]

반응에서는 마지막 입자수/질량 생성항이 필요하다. `v'=v-w`의 Galilean 변환 아래 `R'_s=R_s-m_s w Gamma_s`, `E'_s=E_s-w·R_s+m_s w^2 Gamma_s/2`이고 `Q'_s=Q_s`다. 검증은 상대속도·에너지법칙을 유지한 독립 direct-event average와 이 변환으로 수행한다.

열적 상태를 실제로 할당한 소비자에서만 `C_V dot T=Q-sum epsilon_th(T) Gamma` 등의 기존 caloric chain rule을 적용한다. 모멘트에서 계산한 birth kinetic energy를 즉시 thermal deposition으로 부르지 않는다. 회전·진동 상태를 explicit populations로 풀면 그 상태 에너지를 partition heat capacity에 중복 넣지 않는다. 비열적 종의 moments는 CR 분포/열화 소비자에 남긴다.

## 5. 어떤 추가 입력이 무엇을 정하는가

고정된 한 branch·입사에너지와 고정 Delta에서 CM 생성물 평균 에너지는 `K_c(CM)=sigma_0 p^2/(2m_c)`라 각분포에 독립이다. 그러나 움직이는 frame의 에너지에는 `p L_1 V·e`, 운동량에는 `p L_1 e`, 응력에는 `L_2`가 필요하다. 따라서 같은 total sigma를 가진 두 각 law가 다른 momentum/stress source를 만들 수 있다. 이는 공급자 계약의 구체적 입력 구분이며 새로운 no-go 정리로 취급하지 않는다.

R4의 ensemble thermal k(T)는 위의 energy-resolved `sigma_0`, `L_1`, `L_2`, state별 Delta를 자동 공급하지 않는다. source state labels, method 대안, spin weights와 whole branch selection을 보존하고 각 missing input을 후속 공급자 표에 둔다. 원전의 primary photon count1과 실제 cascade/escape energy도 따로 둔다.

## 6. 유한 검증과 정지 조건

새 함수만 독립 discrete-angle/azimuth event average, 기존 탄성커널의 정확한 limit, 질량비·흡열/발열/임계점, tensor trace, 종별 Galilean/rotation/product relabelling, caloric particle-count와 ownership, 잘못된 source/표현범위 입력으로 검증한다. 임의 scan/IVP/물리 rate 계산은 실행하지 않는다. R4의 28/28·1138assertions와 이전 HE suite는 saved evidence를 소비한다. 한 번의 측정된 test process와 필요할 때 한 번의 원인 특정 repair만 새 배정에 포함한다.

실제 physical provider admission, global physical completion, common T/u·thermalization 승인은 이 단위 결과에서 자동 발생하지 않는다. 새로운 결과는 정확한 조건부 반응 모멘트 식, 구현, 독립 검증과 source intake이다.
