# REI F4 | BASS21 saved193 native event-rate atlas + Puchwein19 same-state source defect

**날짜:** 2026-10-30. **범위:** BASS owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`의 저장된 193개 시점, **NO NEW IVP**. READ-ONLY parent REI #274 HEAD `aa3447078e47d776896e4a21f258ea4f28e4fdef`; sibling #273 HEAD `aa24d25b3e8874f7c4b851b110ec9cefcb1e03ec`. Donor VigilODE #121 original SOURCE-full 3,151,209 bytes SHA256 `19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907`. 193-epoch `trajectory.npz` SHA256 `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`.

## 1. 모형과 물리적 단위

원본 BASS `AtomicNetwork`는 H1/D/T/He3/He4/Li6/Li7 21종을 수소 등가 아닌 **baryon 기준** `Y_i=n_i/n_b`로 추적한다. 핵자수 A, 이온전하 q, proper baryon density n_b [m^-3], `n_e=n_b q^T Y`. 보존 baryon는 `A^T Y=1`. x=ln(a/a_start), a_start=1/21, H=d(ln a)/dt >0 [s^-1]. 진화는 이미 저장된 original BDF의 데이터이며 이번에는 F(Y_i,t_i), J(Y_i,t_i)만 평가한다. BASS의 T(t), UV(t)는 prescribed source; photon transport나 T의 Y 민감도는 native `J`에 포함되지 않음.

35개 반응 이벤트는 photo 13, RR 13, DR 6, weak n/T decay 3개다. 각 이벤트 e는 source i_e, target j_e와 stoichiometric column `S_e=e_{j_e}-e_{i_e}`를 갖고, q^T S_e=+1 (photo/weak) 또는 -1 (RR/DR), A^T S_e=0. Weak 변화는 BASS 원래 `(n -> HII), (T0 -> He3+), (T+ -> He3++)`인 전자/핵종 coarse-graining을 그대로 쓴다.

외부 T,UV,n_b를 고정하는 source 평가에서

\[
 n_e=n_bq^TY,\quad w_e(Y)= k_e(t)Y_{i_e}n_e^{\chi_e},\quad
 \chi_e=\begin{cases}0&(\mathrm{photo,weak}),\\1&(\mathrm{RR,DR}),\end{cases}
\]

여기서 `k_e` 단위는 photo/weak [s^-1], RR/DR [m^3 s^-1]. **분해된 전체 화학벡터장과 전자-feedback Jacobian**은

\[
 F(Y,t)=\sum_e S_e w_e(Y,t),\quad
 J_Y=\sum_e S_e\!\left[
 k_e n_e^{\chi_e}e_{i_e}^{\mathsf T}
 +\chi_e k_eY_{i_e}n_bq^{\mathsf T}\right].
\]

전체 차원 [s^-1]. `A^T F=A^TJ=0`는 각 이벤트마다 성립하고, `n_b q^T F`는 **화학적** 자유전자 소스 [m^-3 s^-1]이지 총 `dn_e/dt`는 아니다. 후자는 baryon expansion에 따른 `dot n_b q^T Y`를 포함한다. 열적/photo-energy ledger는 별도 native output이며 광자 흡수 에너지를 곧바로 가스 열로 간주하지 않는다.

## 2. 원본 193개 시점에서 수행한 고정상태 계산

모든 epoch에서 원본 native `AtomicNetwork.evaluate(Y,T,UV,n_b)`와 독립적인 35-event stoichiometric reconstruction을 대조했다. 이는 이전 VigilODE #121이 제공한 native full `F,J`의 총합을 **사건별 flux와 반응별 gradient**로 재구성한 새 데이터이다. 개별 이벤트 intensity `w_e` [events/baryon/s], proper volume rate `n_b w_e` [events/m^3/s]를 6,755행 CSV로 보존했다. 전체 193×21 F, 193×21×21 J, 193×35 event flux는 별도 NPZ로 보존한다.

후처리 노출량은
\[
 \mathcal N_e^{\mathrm{saved}}\approx\sum_{193\ \mathrm{knots}}\frac{w_e(x)}{H(x)}\,\Delta x,
\]

비균질 적분을 원래 저장된 격자에서 composite Simpson으로 평가한다. 이는 움직이는 baryon fluid element에 대한 **저장 경로상의 계산**이며 새 IVP, 원래 적응 BDF 경로의 정확한 사건 횟수, Eulerian 고정체적 총 생성량 또는 오차 상한이 아니다. 네 가지 채널의 합은 photo 4.986531593057092, RR 4.109226145829892, DR 2.5741774676657008e-18, weak 0 events/baryon이다. Weak=0은 BASS original pilot의 n/T가 0이기 때문이지 weak Jacobian=0이라는 뜻은 아니다.

Li6/Li7 전하이동 four-state M_Li는 각 고정 epoch에서 column sum 0인 birth-death generator다. 계산된 **순간적인 비영 고유값 gap**은 1.0157388961778173e-18 .. 5.221476979410086e-15 s^-1. `1/gap`을 **고정계수 국소시간**으로만 읽는다. 시간 의존 M_Li들이 서로 가환한다고 가정하거나 global exponential contraction certificate를 만들지 않는다. 원본 저장 이력 Li6−gamma Li7 상대 L1 차이는 <=2.1553860904538517e-16 (floating representation), 물리적 Li6 결합의 오류 측정은 아님.

## 3. 실제 동일 상태 H/He source 비교, P19 ↔ BASS

원본 Puchwein et al. (2019), MNRAS 485, 47, doi:10.1093/mnras/stz222, Appendix D1의 13개 수치 knot projection을 이전 REI PR269 소스에서 재사용한다. 저장된 **BASS** 21-state Y_i, BASS proper density/time을 그대로 두고 H1/D/T에 HI, He3/He4에 HeI/HeII photo rate family를 가정한 7-event source만 교체한다. 이는 P19 Table D1 fiducial (log-interpolated) 및 PR269의 nominal GLS tilt 두 경우다. 원래의 REI 17-state ON_refined 저장 상태를 쓰지 않으며 Li rate는 P19 data가 없으므로 교체하지 않는다.

`S_7`을 21×7 photo incidence matrix라 하면 **동일 frozen BASS Y에서의 사건별 소스 차**는
\[
 \Delta F_{\rm photo,7}=S_7\,\operatorname{diag}(Y_{i_e})\,[\Gamma^{B}_{e}-\Gamma^{P19}_{e}],\qquad
 q^T\Delta F_{\rm photo,7}=\sum_e Y_{i_e}(\Gamma^B_e-\Gamma^{P19}_e),\quad A^T\Delta F_{\rm photo,7}=0.
\]

기존 source contract의 `2.4 <= z <= 4.75` 구간에 속하는 52 저장 시점만 사용했다. 두 모델 × 52 = 104 source-comparison rows. P19 **fiducial** 전자 생산률 차 `B−P19`는 이 52개 시점에서 [4.089065630775931e-19, 7.850541009956676e-18] events/baryon/s, 모든 시점 양수. PR269 **nominal GLS** 차는 [1.199216322786665e-18, 7.169362737520797e-18]. 전하·핵자수 재구성 잔차는 부동소수점 수준. photo source만의 차이지 REI full chemistry, nuclear/CR/injection/fast reservoir, UV RT, P19 evolved history, thermal closure 또는 관측 잔차가 아니다.

## 4. 금지되는 물리 승격과 남은 과학 문제

REI #273의 H I collisional ionization 누락 및 H II RR rate mismatch, #274의 BASS off-manifold exact forcing은 그대로 성립한다. 외부 P19 photo rate를 교체해도 BASS native RR/DR+electron pool은 잔존하고 REI full17 chemistry의 J_y와 일치하지 않는다. 원래 REI/BASS isotope inventory mismatch, `rho=nHref/nb`, source H/K, T/heating, Li6/T/fast reservoirs, primordial nuclear+CR+injection, Bianchi directional Thomson frame 등이 확립되지 않았다. No new IVP. Physical F4 PARTIAL, L4_ready=false, production HOLD; working DAG33/88, central28/88, physical-fast4/7 delta0. 현재 새 **보조 실물 데이터 산출물 1/1**만 인정한다. 독립 다른 작성자 R6/C9는 NOT_RUN.

관련 원전: Verner, Ferland, Korista & Yakovlev (1996), doi:10.1086/177435; Verner & Ferland (1996), doi:10.1086/192284; Badnell (2006), doi:10.1086/508465; Puchwein et al. (2019), doi:10.1093/mnras/stz222; Tóth et al. (1997), doi:10.1137/S0036139995293294. 원전은 fit의 과학적 출처이고, 위 계산의 실제 숫자는 source-pinned 코드 실행에서 나온다.
