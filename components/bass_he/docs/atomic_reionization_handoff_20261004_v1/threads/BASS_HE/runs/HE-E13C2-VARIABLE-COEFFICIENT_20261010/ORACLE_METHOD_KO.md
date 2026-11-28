# E13C2 독립 Decimal 연속계수 photon oracle

## 결과와 범위

첫 실행은 Python process exit 0이었다. 실제 capture에서 결과를 보기 전에 선택한 6개 local segment 모두 12점과 20점 Gauss collocation의 사전 수렴 기준을 만족했다. 근거 상태는 `numerically checked / implementation-verified`이고 국소 계산 판정은 `PASS_SCOPED`다. 독립 decision review 및 물리적 전체 trajectory 승격을 뜻하지 않는다.

원 입력은 `BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1`의 OFF/GM `SEGMENTS.csv`, `OFF_STAGES.csv`, `GM_STAGES.csv`다. 각 입력 파일의 byte size와 SHA-256, 읽은 `code/photon_green.py`의 SHA-256을 `ORACLE_RESULTS.json`에 보존했다. coefficient parameter 값과 단위는 해당 pinned 코드와 부모가 지정한 source constants를 사용했다. 원래 계산 함수를 import하거나 호출하지 않았다.

| mode | step | node | segment | 내부 에너지 (eV) | 활성 absorber |
|---|---:|---:|---:|---:|---|
| OFF | 1 | 0 | 0 | 13.700004359094578 | HI |
| OFF | 1 | 1162 | 0 | 35.013816014805165 | HI, HeI |
| OFF | 1 | 1976 | 0 | 69.99510922146612 | HI, HeI, HeII |
| GM | 2 | 1727 | 0 | 54.99016804717483 | HI, HeI, HeII |
| GM | 2 | 2333 | 0 | 98.98837964370455 | HI, HeI, HeII |
| OFF | 2 | 700 | 1 | 24.589994306580035 | HI |

선택 규칙은 `source_on=1` 중 OFF step 1의 13.7, 35, 70 eV에 가장 가까운 `e_mid`, GM step 2의 55, 99 eV에 가장 가까운 `e_mid`, 그리고 OFF step 1의 첫 segment 1이었다. 마지막 조건에 해당하는 레코드는 없어 미리 지정한 fallback인 OFF step 2의 첫 segment 1을 선택했다. 소스 입력만으로 선택했으며 결과 크기로 사례를 고르지 않았다. 전체 약 14,000 segment 재실행, native 실행 및 gas advancement는 수행하지 않았다.

## 정확하게 고정한 입력 의미

CSV의 각 숫자 문자열은 `float(string)`으로 원 binary64 값을 읽은 뒤 `Decimal.from_float`로 정확하게 lift한다. 물리 상수와 fit parameter도 source binary64 값을 같은 방식으로 lift한다. 이후 계산 정밀도는 Decimal 70자리다. `math.pi`의 binary64 값도 정확 lift하므로 임의의 고정밀 π로 교체하지 않는다.

각 레코드에서

\[
s=a+ht,\qquad E(t)=E_0e^{-ht},\qquad t\in[0,1]
\]

이며, gas는 해당 stage의 old/new 값을 선형 보간한다.

\[
g(t)=g_{\rm old}+(g_{\rm new}-g_{\rm old})
\frac{a-s_0+ht}{s_1-s_0}.
\]

여기서 `a`, `h`, `E0`, `s0`, `s1`은 각자 source에 저장된 값을 lift한다. 즉 `h`를 `b-a`로 다시 계산하거나 `a+h/2`를 captured `mid`로 대체하지 않는다. 초기 photon 수는 매 구간의 captured `f0`로 다시 시작한다. 이는 이전 구간의 연속해를 운반하는 global evolution이 아닌 local control이다.

배경과 density 정의는

\[
\rho_{c0}=\frac{3H_0^2}{8\pi G},\quad
n_{H0}=\frac{(1-Y)\Omega_b\rho_{c0}}{m_p},\quad
n_{He0}=\frac{Y\Omega_b\rho_{c0}}{4m_p},
\]

\[
n_H(s)=n_{H0}e^{-3s},\quad n_{He}(s)=n_{He0}e^{-3s},\quad
H(s)=H_0\sqrt{\Omega_re^{-4s}+\Omega_me^{-3s}+\Omega_\Lambda}.
\]

source constants의 원 binary64 literals는 `H0=2.2e-18`, `Ωr=9e-5`, `Ωm=.3`, `ΩΛ=.69991`, `Ωb=.048`, `Y=.24`, `G=6.67430e-8`, `mp=1.67262192595e-24`, `c=2.99792458e10`, `source_rate=1e-15`, `Emin=13.7`, `Emax=100.`이다. 밀도는 cgs, Hubble rate는 s⁻¹, cross section은 cm², 에너지는 eV다.

HI, HeI, HeII target은 순서대로 `nH*(1-x)`, `nHe*(1-y-z)`, `nHe*y`이다. 각 λ는 `c*target*σ(E)/H`이며 로그 redshift 변수 s에 대한 차원 없는 opacity다. Source는

\[
q(t)=\frac{\dot N}{(1/E_{\min}-1/E_{\max})E(t)H(t)}.
\]

source support와 absorber support는 열린 segment 내부의 captured `source_on`, `e_mid`로 고정한다. fit 문턱은 13.6, 24.59, 54.42 eV다. 마지막 선택 사례는 HeI 문턱 아래쪽 내부이므로 이 segment의 HeI branch는 꺼진다. 경계 endpoint의 IEEE 반올림에 따라 branch를 다시 평가하지 않는다. 이 처리는 선택한 branch의 유한 수치 oracle 규약이며 threshold anchor 전체의 정확성을 별도로 증명하지 않는다.

## Collocation 유도와 계산량

\[
\frac{dP}{dt}=h\left[q(t)-\Lambda(t)P(t)\right],\qquad
\Lambda=\lambda_{HI}+\lambda_{HeI}+\lambda_{HeII}.
\]

n개의 [0,1] Gauss–Legendre node를 `c_i`, weight를 `w_i`라 하고 Lagrange basis를 `L_j`라 쓴다. `I_ij=∫_0^{c_i}L_j(t)dt`로 놓으면 collocation stage 값은 선형계

\[
\sum_j\left[\delta_{ij}+hI_{ij}\Lambda(c_j)\right]P_j
=P_0+h\sum_jI_{ij}q(c_j)
\]

로 얻는다. Newton으로 Legendre root를 Decimal에서 정밀화하고, Lagrange polynomial의 계수를 직접 곱셈으로 구성하여 적분행렬을 만든다. 선형계는 Decimal partial-pivot Gaussian elimination으로 푼다. 끝점과 적분들은

\[
P_1=P_0+h\sum_jw_j(q_j-\Lambda_jP_j),\quad
A_i=h\sum_jw_j\lambda_{ij}P_j,
\]

\[
B_i=h\sum_jw_jE_j\lambda_{ij}P_j,\quad
Z=h\sum_jw_jE_jP_j,\quad
Q_N=h\sum_jw_jq_j,\quad Q_E=h\sum_jw_jE_jq_j
\]

로 계산한다. 모든 `B`, `Z`, `QE`는 eV 기반이다. 원 capture의 erg 출력과 비교할 때만 exactly lifted `1.602176634e-12` erg/eV로 나눈다.

전체 작업은 12점 및 20점 선형계 각 6회이며 scientific external package를 전혀 import하지 않는다. 실제 process는 1초 미만으로 종료했다. 원 source coefficient interpolation이나 ODE solver는 공유하지 않았으나, 과학적 정의·고정된 데이터·source literals는 부모 계산과 의도적으로 공유한다.

## 정확 frozen control

captured `q`, 세 `lambda`, `h`, `e0`, `f0`를 각각 정확 lift한 수학적 frozen 해와 비교한다. captured native `n`을 참해로 대신하지 않는다.

\[
J(k)=\int_0^h e^{-ku}du,\qquad L=\sum_i\lambda_i,
\]

\[
P_f(h)=P_0e^{-Lh}+qJ(L),\quad
C=P_0J(L)+q\frac{h-J(L)}{L},
\]

\[
R=E_0\left[P_0J(L+1)+q\frac{J(1)-J(L+1)}{L}\right],
\]

\[
A_{f,i}=\lambda_iC,\quad B_{f,i}=\lambda_iR,\quad Z_f=R,
\quad Q_{N,f}=qh,\quad Q_{E,f}=E_0qJ(1).
\]

선택된 6개 구간은 모두 `L>0`이며 `J`는 안정적인 convergent Taylor series로 평가한다. 이 source에 없는 zero-opacity 제어 lane으로 확장하지 않았다. 보고하는 signed defect는 모두 `continuous − exact frozen`이고, native IEEE output 차이는 JSON의 별도 `captured_ieee_minus_exact_frozen`에 저장했다.

## 사전 acceptance와 관측값

acceptance는 실행 전에 `evidence/ORACLE_TASK_CONTRACT.json`에 기록했다. 두 차수의 절대차 허용치는 `P/A/QN ≤ 1e-25`, `B/Z/QE ≤ 1e-23 eV`, number ledger 및 frozen energy ledger `≤1e-45`, continuous energy ledger `≤1e-25 eV`다. Gauss polynomial moments는 degree 2n−1까지 `≤1e-50`로 확인했다. 수렴 차수를 올리거나 허용치를 수정하는 재실행은 필요하지 않았다.

관측된 두 차수의 최대 절대차는 photon/absorption/source number에서 `3.0633264815e-42`, energy 적분에서 `4.1967541098e-41 eV`였다. 최대 number ledger는 `3e-75`, 최대 연속 energy ledger는 `2.9472e-69 eV`였다. 20점 integrated Lagrange 행합 잔차는 `7.13045092149e-58`, Gauss moment 잔차는 `6e-70`이었다. 고차의 행합 잔차가 더 큰 것은 monomial Lagrange 구성에서의 유한 정밀도 취소와 일치하며 수렴 허용치를 훨씬 밑돈다.

| mode / step / node / segment | ΔP1 = continuous − frozen |
|---|---:|
| OFF / 1 / 0 / 0 | +6.0767271127727007e-13 |
| OFF / 1 / 1162 / 0 | +2.1723104078302636e-14 |
| OFF / 1 / 1976 / 0 | −5.4127456942579817e-15 |
| GM / 2 / 1727 / 0 | −1.0515816406834375e-14 |
| GM / 2 / 2333 / 0 | −1.2936699243839301e-15 |
| OFF / 2 / 700 / 1 | +1.1808729259388336e-13 |

`ORACLE_RESULTS.json`에는 signed species별 `ΔA`, `ΔB_eV`, `ΔZ_eV`, `ΔQN`, `ΔQE_eV` 및 각 차수의 값을 모두 남겼다. 최초 실행에서 실패가 없으므로 `failures=[]`다. 실패를 덮어쓰거나 사후 tolerance를 완화하지 않았다.

Ledger는

\[
P_1-P_0+\sum_i A_i-Q_N=0,
\]

\[
E_1P_1-E_0P_0+\sum_i B_i+Z-Q_E=0
\]

로 정의했다. 첫 항등식은 같은 collocation quadrature에서 구성하므로 좋은 number ledger만으로 근사 오차가 작다고 결론 내리지 않는다. 두 차수 수렴은 별도 truncation 진단이며, 부모의 다른 수치 경로와의 비교가 독립 reference 일치 검사를 담당한다. 여기에 기록한 매우 작은 잔차나 많은 유효 숫자를 물리적 정확도 또는 rigorous error bound로 해석하면 안 된다.

## 재현 및 claim ceiling

```bash
python3 oracle_work/decimal_collocation.py \
  --source intake_drive/physics/BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1 \
  --output oracle_work/ORACLE_RESULTS.json
```

실제 사용한 명령의 stdout/stderr는 `ORACLE_RUN.stdout`, `ORACLE_RUN.stderr`다. 결과 자체에 Python version, platform, oracle 코드 hash 및 source hashes를 보존했다.

이 산출물은 선택된 6개 local segment에서 고정 gas path를 따라 연속계수 photon 해가 frozen-coefficient 해와 어떻게 다른지에 대한 소규모 독립 수치 reference다. Interval certificate, atomic fit uncertainty, 초기조건 물리적 승인, 모든 segment에 대한 오차 경계, coupled gas solve, provider-bound physical dataset 또는 전체 BASS_HE/rei_bianchi 프로그램의 완결을 주장하지 않는다.

## 전달 패키지에서 재현하기

위 명령은 원 실행 작업 디렉터리의 historical command다. 전달 패키지의 루트에서는 기존 evidence를 덮어쓰지 않는 새 출력 경로를 지정한다.

```bash
python3 -B code/decimal_collocation.py --source inputs/upstream_e13c1 --output ../e13c2_oracle_new/ORACLE_RESULTS.json
```

이 명령은 독립 oracle 여섯 local control만 새로 계산한다. 기본 verification은 `code/reproduce.py`를 사용한다. 패키지 안의 실제 경로는 `evidence/ORACLE_RESULTS.json`, `evidence/ORACLE_RUN.stdout`, `evidence/ORACLE_RUN.stderr`다. 사전 선택과 검사 계약은 `evidence/ORACLE_TASK_CONTRACT.json`이다.
