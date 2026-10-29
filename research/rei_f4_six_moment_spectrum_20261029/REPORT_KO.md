# REI Physical Fast F4: P19의 6개 H/He 모멘트를 만족하는 양의 photon-spectrum 구성 및 Li 식별성

2026-10-29 · 새 단위 `REI_F4_SIX_MOMENT_POSITIVE_SPECTRUM_20261029` · 직접 유도/수치검산 `DERIVED + NUMERICALLY_CHECKED`, 학술적 독립 R6/C9 `NOT_RUN`.

**원본 DAG:** Working 33/88, Central 28/88, Physical fast 4/7, 완료노드 추가 0. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`. 기존 ON_refined 300 K bath, 원본 361행 및 17종과 PR259 그림은 미변경. PR269의 7개 저장 mean-z 표본을 **입력 좌표로만** 이용했으며 새로운 IVP/생산 모델 실행은 0.

## 1. 실제 해소된 질문과 계산 범위

PR269는 BASS original power-law 광원과 Puchwein 2019(P19) nominal 3개 광전리율의 서로 다른 source-shape를 확인했다. 이 사실은 **새로운 비음수 단일 광원장이 원리적으로 가능한가**라는 질문과 구분해야 한다. 이번 연구는 P19의 H I, He I, He II 광전리율 3개와 photoheating rate 3개, 총 6개 모멘트를 동시에 만족하는 새로운 positive **piecewise-bin photon-number flux**를 **BASS 원본의 71개 spectral bin centre, 5–200 eV 지원 구간과 원본 광전리 σ**로 구성했다. 에너지 bin의 범위, cross section, thresholds, 13개 P19 원본 knot, β/κ nominal 모두 명시적으로 고정. BASS 원래 power law/UV history를 교체하지 않았고 이 spectral field는 **counterfactual construction**이다.

`E_j`와 `Φ_j >=0`는 각각 eV, bin-integrated m⁻²s⁻¹. 반응률 Γ_i[s⁻¹], 흡수 후 가열 모멘트 \mathcal{H}_i[eV/s]로 정의:

\[ Γ_i=\sum_j σ_i(E_j)Φ_j,\qquad \mathcal{H}_i=\sum_j σ_i(E_j)(E_j-I_i)_+Φ_j. \]

행렬 \(M\in\mathbb{R}^{6\times71}\)에 대한 \(MΦ=m_{P19}(z),\;Φ\ge0\)를 원래 이산 bin에서 푼다. P19 \(m\)은 13 knot의 strictly positive 값들에 log-rate piecewise 보간을 적용하고 nominal \(10^{β+κ(z-3.6)}\)을 6개 모멘트 공통으로 곱한다. 단위 혼합을 방지하기 위해 각 row를 그 모멘트 target으로 나눠 선형계획(HiGHS, 최소 총 photon 수)을 푼다. 이 최소화는 수학적 witness 선택 규칙일 뿐 source spectrum의 물리적 교정이나 posterior가 아니다.

## 2. 7개 실제 저장점에서의 구성적 존재 증명

| 저장 mean-z | 구성 spectrum 총 flux [m⁻²s⁻¹] | H/He 6개 모멘트 max relative residual | Li I Γ 하한 [s⁻¹] | Li I Γ 상한 |
|---:|---:|---:|---:|---|
| 2.404494 | 3.0613e+09 | 2.22e-16 | 1.7882135e-13 | UNBOUNDED |
| 2.789073 | 2.8922e+09 | 2.22e-16 | 1.7181163e-13 | UNBOUNDED |
| 3.217095 | 2.7259e+09 | 2.22e-16 | 1.6332247e-13 | UNBOUNDED |
| 3.603020 | 2.6394e+09 | 1.11e-16 | 1.5820437e-13 | UNBOUNDED |
| 4.024262 | 2.6190e+09 | 1.11e-16 | 1.5646111e-13 | UNBOUNDED |
| 4.378370 | 2.6551e+09 | 1.11e-16 | 1.5803167e-13 | UNBOUNDED |
| 4.701690 | 2.7363e+09 | 0.00e+00 | 1.6205120e-13 | UNBOUNDED |

7개 모두 71개 중 **정확히 6개 비음수 bin**만 활성화하는 해를 찾았다. 반환값을 원래 M 행렬로 직접 재적용했고 6차원 선형시스템을 **75자리 mpmath**로 별도 재구성해, *represented binary64 coefficient* 수준에서 residual을 10⁻⁵⁸ 이내로 확인했다. 원본 P19 전체 59행이나 관측된 방향별 radiation field에 대한 동일성 주장은 아니다.

## 3. Li source의 식별성: 유한한 하한·무한한 상한의 명확한 분기

BASS 원본 Li I 문턱은 5.392 eV, H I/He I/He II 문턱은 각각 13.6/24.59/54.42 eV. 고정 original grid에서 E_*=10.2771417431 eV의 bin은 Li I photo σ=1.31170466404e-22 m² >0이지만 H/He 6개 관측 행의 모든 계수가 **정확히 0**이다. 임의의 λ≥0에 대해

\[ M(Φ+λe_*)=MΦ,\qquad Γ_{LiI}(Φ+λe_*)=Γ_{LiI}(Φ)+λσ_{LiI}(E_*).\]

따라서 6개 H/He 모멘트만 고정하고 photon-number/energy budget을 별도로 주지 않으면 Li I rate의 **유한 상한은 없다**. 예시 λ=10⁹ m⁻²s⁻¹를 더하면 H/He 변화 0, Li I rate는 **+1.31170466404e-13 s⁻¹**, 원래 저장된 중앙 REI Li7 neutral row에서 source는 **+1.46295645576e-27 Href⁻¹s⁻¹** 변화한다. 이는 같은 cosmological evolution이 아니라 동결 상태 counterfactual source 응답이다.

**새 positive 결과:** finite BASS grid에서 `min σ_LiI·Φ` subject to 6 positive moment equalities를 dual LP로 풀면 중앙 z=3.603019593에서 Γ_LiI ≥ **1.58204374698e-13 s⁻¹**이다. 7개 모두 primal+dual active 6-bin 시스템을 mpmath 75-digit으로 재구성하여 represented-value dual feasibility gap ≲10⁻⁷⁵를 확인. 원래 실제 P19 continuous source에 대한 directed interval bound로 주장하지 않는다.

또 Li II(문턱 75.64 eV) 및 Li III(122.5 eV)의 양의 cross-section은 He II(54.42eV) support 안에만 있으므로, 원본 finite bins에서 \(R_q=\max_j σ_{Li,q}(E_j)/σ_{HeII}(E_j)\)라 놓으면 \(Γ_{Li,q}≤R_q Γ_{HeII}\). 중앙 z에서 각각 Li II ≤ **5.68957728733e-16 s⁻¹**, Li III ≤ **4.19854489827e-16 s⁻¹**. 이들은 임의의 음이 아닌 bin flux에 대한 **유효하지만 반드시 sharp하지는 않은** 상한이다.

이 결과는 H/He 모멘트가 Li 전체 source를 유일하게 결정하지 못한다는 **이 제한된 모형 안의 식별성 정리**다. 보편적인 Bianchi 모델이나 모든 물리 UV 스펙트럼의 강한 no-go로 승격하지 않는다. 전자 pool, Li6 isotope charging, thermal/CR/capture/decay, 가스와 복사의 실제 상태시간 결합은 따로 필요하다.

## 4. 검증과 문제 분류

- 실제 Python `scipy.optimize.linprog`의 7개 비음수 해 + 6개 모멘트, original BASS `AtomicNetwork.photo_cross_sections` 실행, 12/12 `unittest` PASS. Independent numerical verification: 75-digit `mpmath.lu_solve`로 7개 witness·7개 Li I dual certificate 재구성.
- 첫 test run에서 `max_absolute_HHe_moment_change`의 테스트 키를 잘못 쓴 `KeyError` 1건이 발생. test-only로 키 수정했고, 방정식·source·허용오차는 변경하지 않았다. 원래 RED log와 최종 GREEN log 모두 보존.
- 입력: 원본 PR269 ZIP SHA256 `cecc0920ed52124d04a7ec3224d8f7862e9f3730dbf96058bd8d95ec910f9179`를 통째 보존. BASS native atomic source SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, P19 numeric projection Git blob `3472e57abebb55e94f8c4436f2867bfc58e9feb9` 등은 기존 byte/numeric identity를 계승해 현재 파일을 별도로 확인한다.
- Native subagent spawn/collect 도구 없음: 실제 다른 작성자 R6/C9 **NOT_RUN**. `Wolfram`의 수학적 check와 mpmath 계산은 native blind reviewer를 대신하지 않는다. BASS 62-state solver·새 IVP·전경로 수렴성·관측 CMB 구현 모두 NOT_RUN.

## 5. 과학적 의의와 다음 action

**해소한 blocker:** H/He 6개 모멘트가 BASS 원본 단면적을 갖는 **어떤 비음수 finite-band source**와도 양립할 수 없는 것은 아니다. 7개 z에 대해 실제 positive spectral witness가 존재한다.

**그대로 남은 blocker:** BASS 원래 power-law bath, REI 원래 300 K bath, P19 original radiative transfer가 서로 같은 모델이라는 증거는 없다. 원본 REI↔BASS isotope initial inventory mismatch(약 0.5%)와 양의 T, hidden Li6/fast source, full chemical Jacobian, nHref/n_b, H,K, directional redshift도 변하지 않았다. 원래 17상태 source와 새로운 스펙트럼 사이의 실제 self-consistent IVP/τ 연결을 수행하거나 기존 source를 몰래 교체하지 않는다.

**다음 최소 물리 작업:** 추가 source priors(5.392–13.6 eV photon number/energy, LiI LiII ionization, H/He line profile, spectral smoothness)를 source-owner가 승인해 LiI 자유도를 규정한다. 필요 시 고정 입력에서 full21 BASS 내부 Li6 lift와 REI17 7-event source에 대한 정확한 reduced source/Jacobian operator를 계산하되, 동일 IC/clock/bath 승격은 분리한다. Full F4, L4, physical τ/CMB는 미승격.

원전 지원: Puchwein et al. (2019), MNRAS 485, doi:10.1093/mnras/stz222; Tóth et al. (1997), SIAM J. Appl. Math., doi:10.1137/S0036139995293294. 위 LP 수치 결과는 원전 주장 인용이 아니라 source-pinned 독립 계산이다.