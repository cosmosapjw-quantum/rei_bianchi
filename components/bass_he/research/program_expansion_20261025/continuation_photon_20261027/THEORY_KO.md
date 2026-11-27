# HE-EXP-PHOTON-05 — 광자 입사와 두 유한질량 딸핵의 반동

## R1–R3: 연구 위치, 입력, 적용 범위

STATE04 source `2addfab8c8975febd69d2c88eecc09afea508fbe`, delivery `30924d902187777fbff02687639c91d65cf53191`의 완료 근거를 재사용한다. 이번 문제는 정지 bare ground-state alpha와 입사 광자에서 두 bare ground-state deuteron으로 가는 exclusive 사건의 에너지·운동량·응력 가중치다. EVENT03의 두 massive 비상대론적 반응물 및 고정 총 조성질량 계약 밖에 있는 초기 광자를 직접 다룬다. 기존 커널·검사·예산을 변경하지 않는다.

NIST 2022 CODATA 원문에서 선택한 rest energies는 `A=m_alpha c^2=3727.3794118 MeV`, `M=m_d c^2=1875.61294500 MeV`다. 인쇄 표준불확도는 각각 `0.0000012`와 `0.00000058 MeV`다. 원문 `allascii.txt` 40801 bytes의 SHA256은 `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`이다. MeV 행을 canonical input으로 사용하며 별도로 반올림된 kg/J 행과 수치상 exact equality를 동시에 강제하지 않는다. 정확한 상수는 `c=299792458 m/s`, `1 eV=1.602176634e-19 J`다. 원문: https://physics.nist.gov/cuu/Constants/Table/allascii.txt .

기존 WU R3 packet `PROVIDER_ROWS.json`, SHA256 `d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2`의 `EXFOR_M0475002`를 재사용한다. 공식 원전은 `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4`다. 12개 native 행은 lab incident energy 213/258/330 MeV와 CM angle 46/61/73/87도이며, DATA-CM 및 통계 ERR-S는 NB/SR다. 이 좌표에서 조건부 운동학을 계산하고 native DCS/오차는 그대로 보존한다.

측정은 reaction-particle-tagged bremsstrahlung, liquid-He target, 두 D coincidence/TOF다. 현재 packet에서 incident response/bin width, angular acceptance, polarization/azimuth, full/half sphere와 particle/event normalization 및 bare nuclei로의 electronic-spectator 사영은 미결속이다. 따라서 이 단위는 이 좌표에서의 bare-nuclear 운동학 사상이다. native DCS로 event flux를 정하거나 각도 적분·보간·임의 1/2를 적용하지 않는다. Native 그림의 phi=0은 명시적인 대표 평면이다. 두 딸핵의 +/-는 수학적 label이며 detector-arm 식별을 주장하지 않는다.

WU R5의 general-N 조건부 이론, REC139 source/history 진단, CR107/108 scalar zero-recoil 및 finite-age 결과는 최신 실제 owner 관측에 결속한다. 이들은 이번 유한 광자 반동의 수치 입력을 공급하지 않으며 이전 근거를 반복 실행하지 않는다. Global WU 104/138/155 source inventory와 STATE04 scalar adapter는 불변이다.

## R4–R5: CM 운동학과 안정적인 계산식

Metric은 (-,+,+,+)다. 에너지 단위의 4-vector를 `q^mu=(E,c p)`로 쓰며 invariant squared energy는 `s=-eta_mu_nu q_tot^mu q_tot^nu`다. Photon 방향 `n`과 CM daughter 방향 `u`는 단위 3-vector, `mu=n dot u`다. Target은 선택 lab에서 정지하고 photon energy `e>0`이다. Source 채널은 `0<A<2M`인 endothermic channel이다. 일반 수학 커널도 이 조건을 사용한다.

\[
 s=A^2+2Ae,\quad W=\sqrt{s},\quad
 \Delta=2M-A,\quad e_{th}=\frac{4M^2-A^2}{2A}
 =\Delta+\frac{\Delta^2}{2A}.
\]

`e>=e_th`에서 CM daughter energy는 `E_*=W/2`이고 momentum의 에너지 상당량은

\[
 \kappa=cp_* =\frac12\sqrt{s-4M^2}
 =\sqrt{\frac A2(e-e_{th})}.
\]

두 표현의 동치는 threshold recoil 항을 보여준다. `e_th`와 단순 rest-energy deficit `Delta`는 다르다. 계산에서는 Delta와 threshold excess를 fsum으로 구성하고 후자의 kappa 식을 사용한다. 음의 excess는 거부하며 물리적으로 열린 범위를 수치 clip으로 만들지 않는다. 실제 source 3개 에너지는 threshold에서 떨어져 있다. Floating-point threshold 자체의 정확한 상대 kappa를 주장하지 않고, exact synthetic boundary/near-boundary와 invariant residual로 그 수치 동작을 검증한다.

\[
 \gamma=\frac{A+e}{W},\quad \eta=\gamma\beta=\frac eW,
 \quad g=\gamma-1=\frac{\eta^2}{\gamma+1}.
\]

마지막 식은 작은 boost에서 gamma-1의 cancellation을 피한다. CM의 `(W/2,+kappa u)`와 `(W/2,-kappa u)`를 n 방향으로 boost하면

\[
 E_\pm=\frac{A+e}{2}\pm\eta\kappa\mu,\qquad
 \mathbf q_\pm=\pm\kappa\mathbf u+
 \left(\pm g\kappa\mu+\frac e2\right)\mathbf n.
\]

따라서 `E_++E_-=A+e`, `q_++q_-=e n`이고 각 daughter는 `E_\pm^2-|q_\pm|^2=M^2`를 만족한다. CM boost의 역변환은 `E_* = gamma E-eta(q dot n)`, `q_* = q+[g(q dot n)-eta E]n`이므로 독립 검사에 사용할 수 있다. `u->-u`는 두 동일한 딸핵을 교환한다.

운동에너지는 작은 차를 직접 빼는 대신

\[
 K_\pm=\frac{|\mathbf q_\pm|^2}{E_\pm+M}
\]

로 계산한다. 정확한 mass shell 위에서 이는 `E_\pm-M`과 같다. 동일한 momentum에 비상대론적 식을 적용한 진단량은

\[
 K_{NR}=\frac{|q|^2}{2M}=K+\frac{K^2}{2M}
\]

이다. 이 차이를 native 좌표에서 저장·표시하여 이번 상대론적 결속의 영향을 확인한다. 이는 새로운 비상대론적 solver benchmark가 아니라 동일 momentum에서 두 energy formula를 비교한 양이다.

## 에너지–운동량 텐서 가중치

한 입자의 energy-unit kinetic stress weight는

\[
 S^{ij}(q)=\frac{q^iq^j}{E}=\frac{c^2p^ip^j}{E}.
\]

`T00`의 입자 가중치는 E, `T0i`는 q_i이며 Tij의 가중치는 Sij다. 두 daughter의 S를 합친 값과 photon loss `-e n_i n_j`를 기록한다. 정지 target의 spatial stress는 0이다. 각 massive daughter에 대해 `tr S=E-M^2/E`; incoming photon에는 `tr S=e`다. 이 상대론적 stress는 raw `p_i p_j`와 다르다. Net stress source 자체의 양의 준정부호성은 요구하지 않는다. 각도 평균은 하지 않고 입력된 u의 pointwise weight를 제공한다.

## 입자수와 단일 에너지 소유권

한 사건의 count 변화는 photon -1, alpha -1, deuteron +2다. Baryon4와 nuclear charge2가 보존되고 material nucleus count는 +1이다. 두 daughter를 같은 deuteron ID로 합치되 factor1/2를 추가하지 않는다. Native DA의 particle/event normalization은 이 count identity와 별도 문제다.

\[
 \delta E_\gamma=-e,\quad
 \delta U_{rest}=2M-A=\Delta,\quad
 \delta K_{material}=K_++K_-=e-\Delta.
\]

따라서 세 항의 합은 0이다. Physical nuclear rest masses가 nuclear binding을 이미 포함하므로 이 representation에서 `population_rest_energy_witness`가 유일한 rest/binding owner다. 별도 binding RHS를 더하지 않는다. EVENT03의 조성질량+명시적 internal-energy representation과 값만 섞지 않는다.

호출자가 명시한 사건 flux `J [m^-3 s^-1]`로 per-event count·energy·momentum·stress weights를 곱할 수 있다. `1 MeV=1.602176634e-13 J`, `p[kg m/s]=q[MeV]*(1.602176634e-13)/c`를 사용한다. 그 J는 이번 단위가 native DCS에서 산출한 물리 rate가 아니다. 값0에서도 모든 입력의 유효성을 먼저 검사한다.

Material count source는 J이지만 thermal particle-count source는 아직 정해지지 않았다. `Gamma_thermal`, Cv, species heating, thermal deposition 및 독립 binding RHS는 null, birth pool은 UNASSIGNED다. Daughter kinetic energy를 곧바로 thermal heating으로 배정하지 않는다. Global species/consumer와 physical rate admission도 별도 의존성이다.

## 질량 불확도와 정확도 범위

질량 중앙값의 수치 사상과 실제 질량 불확도를 구별한다. 예를 들어 `Var(Delta)=4 Var(M)+Var(A)-4 Cov(A,M)`이며 threshold의 미분은 `d e_th/dM=4M/A`, `d e_th/dA=-2M^2/A^2-1/2`다. 필요한 공분산은 확보하지 않았으므로 결합 physical error bar를 새로 만들지 않는다. CODEX 검증 오차는 구현의 수치 일치 기준이며 source physical uncertainty를 인증하지 않는다.

## 실제 검증과 다음 연결

독립 Decimal80 계산은 literal MeV masses와 Decimal trigonometric series/긴 pi 상수에서 native12 좌표를 구성하고 직접 Lorentz matrix를 적용한다. 구현식, invariant residual, exact synthetic threshold, 방향 회전·daughter 교환, count/energy ledger, stress trace, 단위, invalid/representation 경계 및 native DCS 보존을 함께 확인한다. 한 bounded 테스트와 별도 saved-data-only 그림을 실행하고 독립 이론·코드 검토 및 root 시각 판독을 수행한다. 기존 검사는 재실행하지 않는다.

획득할 제품은 source-coordinate relativistic recoil and moment supplier다. 다음 입력은 실험 source의 electronic/response/normalization 사영, complete differential angular law 및 실제 photon encounter distribution/flux, 그리고 named deposition consumer다. 알려진 Lorentz 두 입자 운동학을 실제 source/질량/단일-owner 구현에 연결하는 기여이며 새 일반 no-go나 신규성 정리를 주장하지 않는다.
