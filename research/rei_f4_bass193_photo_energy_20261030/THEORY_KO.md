# REI F4 / BASS21: 193 저장시점 원본 광자흡수–1차 광전자–Li 내부껍질 에너지 장부

**연구 단위** `REI_F4_BASS193_PHOTO_ENERGY_LEDGER_20261030`; 2026-10-30. 부모 REI Draft PR276 `970175ffce1e1139b911a1f45bee9271a69153b9`; 원 BASS atomic owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. 모든 계산은 **원래 저장된** 193개 source 상태에 대한 정적 rate 재평가이며 새 IVP는 0이다.

## 1. 정의, 단위, source

BASS의 abundance `Y_i=n_i/n_b` (baryon당 핵종/전하상태 개수), proper baryon density `n_b` [m^-3], 원래 source UV 플럭스의 유한 구간 적분값 `Φ_b` [m^-2 s^-1], 광자 에너지 `E_b` [eV], source 광이온화 단면적 `σ_{ib}` [m^2]를 사용한다. `i`는 full21 중 photo-active 13개 전이 출발종, `b`는 5–200 eV의 원본 71개 스펙트럼 bin이다. 이것은 source의 *prescribed, optically thin, isotropic* 광자장이며 self-consistent photon transport는 아니다. 전이율은 `Γ_i=Σ_b σ_{ib} Φ_b` [s^-1].

정적 체적 사건 source는

\[
 r_{ib}=n_bY_i\sigma_{ib}\Phi_b\quad [\mathrm{m^{-3}s^{-1}}].
\]

이온화 threshold `χ_i` [eV] 및 Li I 1s 부분 단면적 `σ^{1s}_{ib}`에 대해 `r^{1s}_{ib}=n_bY_iσ^{1s}_{ib}Φ_b`. 모든 종에서 원본 source의 분해는

\[
\begin{split}
Q_{\rm abs}&=\sum_{i,b}r_{ib}E_b,\\
Q_{\rm ion}&=\sum_{i,b}r_{ib}\chi_i,\\
Q_{\rm core}&=\Delta_{\rm Li}\sum_{i\in\{^6\mathrm{LiI},^7\mathrm{LiI}\},b}r^{1s}_{ib},\quad\Delta_{\rm Li}=64.39-5.392=58.998\ \mathrm{eV},\\
Q_{\rm primary}&=\sum_{i,b}r_{ib}(E_b-\chi_i)-Q_{\rm core},\\
\boxed{Q_{\rm abs}&=Q_{\rm ion}+Q_{\rm primary}+Q_{\rm core}.}
\end{split}
\]

각 Q는 [eV m^-3 s^-1], 실제 출력의 체적 power [W m^-3]는 `1 eV=1.602176634×10^-19 J`를 곱한다. BASS 원본 `AtomicNetwork.evaluate`의 `photo_absorbed_power_W_m3`, `primary_kinetic_power_W_m3`, `unresolved_core_power_W_m3`, `li1s_photo_event_rate_m3_s`와 정확히 같은 정의로 비교한다. 이 식은 **전기적으로 중성인 광자 흡수와 공급된 단면적의 장부식**이지, 완결된 전자/열/광자 에너지 수송 방정식이 아니다.

BASS Li I `1s` 흡수는 명시적으로 `q→q+1` 한 전하만 생성하는 coarse-grained 모델 가정이다. Verner et al. (1996)의 원전에는 내부껍질 광이온화 후 Auger 전자 생성 가능성이 기록되어 있지만, 본 BASS finite model에는 실제 Auger/형광 charge yield·에너지 분기·electron thermalization이 source로 주어지지 않았다. 따라서 `Q_core`는 미분배 에너지, `Q_primary`는 source가 구분한 1차 광전자 운동에너지이며 **둘 모두 자동으로 gas heat로 승격하지 않는다**.

## 2. 저장 시계로의 사후노출량

원 BASS `x=ln(a/a_start)`, `dt/dx=1/H(x)` (H>0)이며, 배열의 `x`와 H는 원래 저장된 BASS 이력의 source 값이다. 시간적 물리 반응을 재진화하는 것이 아니라 보간/사후적분만 수행한다.

\[
 \mathcal E_k^{\rm saved}=\int_{x_0}^{x_1}\!dx\, \frac{Q_k(x)}{n_b(x) H(x)},
 \qquad k\in\{\mathrm{abs,ion,primary,core}\},
\]

단위는 [eV/baryon]. 고정된 193개 `x` 표본의 composite Simpson 사후적분은 원 BDF 적응식 누적상태나 연속시간 rigorous error bound가 아니다. 이 정의는 현재 original BASS pilot source에 대한 형식적 노출량이다.

## 3. 실제 정적 데이터

| 집계 | source-owned saved-grid 결과 |
|---|---:|
| `ΣΓ` 광이온화 사건 노출량 | 4.986531593057093 events/baryon |
| 흡수된 광자 에너지 | 121.1542586591429 eV/baryon |
| 이온화 threshold | 92.83563382986274 eV/baryon |
| 1차 전자 운동에너지 | 28.3186248272491 eV/baryon |
| Li 1s 미분배 core | 2.0310979599168846e-9 eV/baryon |
| Li 1s 사건 노출 | 3.4426556153037163e-11 /baryon |
| 원 BASS photo 사이트 수 | 13 |
| 원 광자 bin 수 | 71 |
| 사건별 물리 데이터 행 | 193 × 13 = 2509 |
| bin별 물리 데이터 행 | 193 × 71 = 13703 |

H I 흡수에너지 74.59308076716984, He4 II 38.80139288346634, He4 I 7.752180862193959 eV/baryon. 세 채널의 합이 광자 흡수 노출량을 지배한다. Li core가 작다는 것은 **현재 isotope inventory와 prescribed UV 모델에 한정**한 결과이며 Li의 실제 fluorescence/Auger 영향에 대한 보편적 무시 가능성 정리가 아니다.

## 4. 검증 및 적용 경계

원본 `AtomicNetwork.evaluate` 출력과 독립적인 bin×species 행렬 합산의 최대 상대 차: absorbed `5.37728964962056e-16`, primary `5.432538284724361e-16`, unresolved core `8.76969828494597e-16`. 가장 큰 3항 장부 절대 잔차 `2.3489527750041644e-46 W/m^3`. Python unittest 40/40 PASS, Wolfram symbolically `Q_abs-Q_ion-Q_primary-Q_core=0` 및 core per 1s event `58.998 eV` 0 residual. 원본 BASS와 직접 동치인 수학적 분해를 검산한 것이지 **다른 작성자의 R6/C9 review는 수행되지 않았다**.

배제: `gas heat=Q_primary`, Auger cascade, 형광/secondary excitation, ionization/recombination radiation balance, 에너지 이동/복사전달, 실제 REI `IgmPhotoInput.heat_erg_per_absorber_s` 물리 결속, Bianchi sky, `tau` history, posterior. REI의 온도·전자 pool·photon-source와 같은 입력을 소유했다는 증거가 없으므로 REI↔BASS full source-equivalence는 여전히 `UNRESOLVED`. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`, 원 Working 33/88, Central 28/88, F4 fast 4/7, canonical delta0.

## 5. 문헌과 provenance

- Verner, Ferland, Korista & Yakovlev (1996), *Atomic Data for Astrophysics II*, ApJ 465 487, DOI https://doi.org/10.1086/177435. Ground state photon absorption cross section fits. Original work notes subsequent Auger electron emission after inner-shell ionization; it does NOT establish BASS source's q+1 photon yield or thermal closure.
- Verner & Yakovlev (1995), A&AS 109 125, original shell-resolved fit, https://www.pa.uky.edu/~verner/photo.html.
- BASS owner source `atomic_network.py` SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, original model SHA256 `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614` in original immutable donor ZIP. Original 129 coefficients are **Git numeric projection**, not fresh byte-identical full native coefficient JSON.
