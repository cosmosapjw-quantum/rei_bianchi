# REI↔BASS 전자기체·광이온화 source의 적색편이별 rank 호환성

**단위:** `REI_BASS_FULL_EVENT_RATE_COMPAT_20261029`, 2026-10-29. 원본 REI working **33/88**, central **28/88**, physical fast **4/7**. 신규 물리 DAG 기여 **0**. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`. 부모 PR266 `a3470c88b4bddb38a08623d37ff6aa61210e04ae`, 형제 PR267 `779192ec55daf21e006b34bbc859681c9d2643ab`은 원본을 수정하지 않는 참고 입력이다.

## 1. 소스 및 모델의 구별

* BASS PR234 원본 `input/atomic_network.py`: SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, 모델 `input/atomic_model.json`: SHA256 `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614`. `AtomicNetwork._prepare_spectrum`에서 시간 의존 없는 `self._Gphoto`를 생성한다. `rates(T,uv_scale)`의 광원은 **`G0 = uv_scale * self._Gphoto`**. 고정 photon_field power index = −2.5, 에너지 지지집합 5–200 eV, HI 기준 광이온화율 1e−12/s. `_Gphoto` 자체를 재구성하는 원본 `data/atomic_coefficients.json` 및 `provenance/atomic_sources.json`은 **현재 PR234 SOURCE ZIP에 없어서** source-native BASS 계수와 full21 수치 RHS 실행은 인증하지 못한다. 이는 공통 u에 의한 비율 불변성의 구조적 증명을 막지 않는다.
* REI PR262 원본 `code/source17.py` (SHA256 `3e8735874b53516dfe2df781598aaf77407fd12e64b72c048f257982cbb2812f`)는 일곱 frozen ON_refined 상태에서 PR261 Puchwein 2019 여섯 source moments의 공통 (β,κ) scaling을 사용한다. Puchwein 13행 projection SHA256 `dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff`. **원본 59행 raw file의 바이트 복사본이 아니라 13행 손실 선택 투영**이다. Puchwein 수치는 비평형(`rates_fiducial`)이고 등가평형 rate와 다르다. calibration domain 2.4≤z≤4.75, 이번 exact knot 11개는 2.48≤z≤4.62.
* 별개의 오래된 REI `research/rei_external_sources_20261028/implementation/model.py` Git blob `1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc`, `config.json` Git blob `64c551f5ec23580e19ad1177375ae65e8c1c542f`는 `illustrative_uncalibrated=true`인 원래의 핵반응·CR·fast source/시야. 이것은 Puchwein six-moment 재이온화 모델 전체와 같지 않다. 본 연구는 **PR262에서 명시한 일곱 이벤트에 한정**한다. 이전 PR265의 pilot inventory mismatch 0.4943–0.5186% 및 T>0 vs BASS T=0은 변하지 않는다.

## 2. 정리 1: 단일 UV amplitude의 비율 불변성

BASS의 photo-generator `G_B(z)=u(z)G_B^0`에서 

\[ (\Gamma_{\mathrm{HI}},\Gamma_{\mathrm{HeI}},\Gamma_{\mathrm{HeII}})_B(z)=u(z)(b_H,b_I,b_{II}),\quad b_H,b_I,b_{II}\ge0.\]

비영 채널의 `Γ_HeII/Γ_HI=b_II/b_H`는 `u(z)`가 임의의 양수 함수여도 상수이다. PR261의 공통 `10^[β+κ(z−3.6)]`도 모든 P19 모멘트를 동일 배율로 곱해, P19 HeII/HI 비율을 바꾸지 못한다.

고정 Puchwein 13행 중 calibration 내부 두 실제 원소는 다음과 같다.

| z | Γ_HI (s^-1) | Γ_HeII (s^-1) | Γ_HeII/Γ_HI |
|---|---:|---:|---:|
|2.48|1.17e-12|5.30e-15|53/11700|
|4.62|7.58e-13|2.98e-17|149/3790000|

두 유리수의 차는 `1991267/443430000 ≠ 0`이고 비율 간 배율은 `115.2240004588997877…`이다. 따라서 BASS의 **그 고정 shape**를 사용하는 단일 amplitude만으로는 두 redshift의 HI·HeII 두 rate를 동시에 정확히 맞출 수 없다. 이는 구조가 한정된 소스 모형에 관한 반례이며 모든 cosmological UV field에 대한 보편 불가능성 주장이 아니다.

## 3. 정리 2: 최적 상태별 amplitude까지 허용한 날카로운 상대오차 하한

임의 고정 `k=b_II/b_H>0`, source-projected 목표 비율 `r_i=Γ_II,i/Γ_H,i>0`, 각 시점의 임의 amplitude `t_i=(u_i b_H)/Γ_H,i>0`에 대해

\[e_i(k,t_i)=\max\bigl(|t_i-1|,|t_ik/r_i-1|\bigr).\]

고정 k에서 두 절대오차를 균형시키는 `t_i=2r_i/(k+r_i)`가 최적이며 `min_t e_i=|k-r_i|/(k+r_i)`. 두 시점의 최적 공통 `k=\sqrt{r_1r_2}`에서

\[\boxed{\inf_{k>0,t_1>0,t_2>0}\max_i e_i=\frac{\sqrt{r_{\max}}-\sqrt{r_{\min}}}{\sqrt{r_{\max}}+\sqrt{r_{\min}}}=0.8295586873156143629955885231\ldots}\]

`k*=0.00042200591004792022894353…`, `t_hi*=1.8295586873…`, `t_lo*=0.17044131268…`. **2 epoch × 2 채널 상대 광이온화율 오차의 날카로운 하한(82.9559%)**일 뿐, 열역학·광학깊이·우주론 모형의 물리 오차나 일곱 상태 진화 오차가 아니다. BASS 본래 `k`의 숫자를 알 필요 없이 모든 가능한 양의 k에 성립한다. zero channel이면 상대오차가 1 이상이므로 역시 하한을 피하지 못한다.

## 4. 정리 3: 정확한 rate-space 선형 span 하한 및 구성적 수선

calibration 범위에 놓인 11개 P19 원소에서 

\[R_3=[\Gamma_{HI},\Gamma_{HeI},\Gamma_{HeII}]_{11\times3},\quad R_6=[\Gamma_{HI},h_{HI},\Gamma_{HeI},h_{HeI},\Gamma_{HeII},h_{HeII}]_{11\times6}\]

를 **원본 JSON의 십진 표현을 유리수로 exactify**하여 구성했다. 실제 SymPy `rank(R3)=3`, `rank(R6)=6`. `R3`의 2.48,3.64,4.62 세 행의 determinant는

`235010831/2500000000000000000000000000000000000000000000000` (s^-3), 따라서 정확히 비영이다. 다른 11행을 추가해도 3보다 높은 rank는 없다. 따라서 고정된 rate-channel shape 벡터의 선형결합을 시간에 따라 바꾸는 방법에서는 모든 11행을 exact하게 재현하려면 **최소 3개의 선형독립 rate-space 방향**이 필요하다. 6개 광이온화+가열 moment 전체를 exact하게 복원하는 추상 선형 span에서는 6개 필요하다. 공통 `β,κ` 배율은 각 row에 0 아닌 배율을 곱해 rank를 바꾸지 않는다.

**양의 수선:** 3개의 source rate `γ_H(z),γ_I(z),γ_II(z)>0`를 직접 독립 함수로 허용하면 REI 일곱 UVB 사건의 정적 source를 완전히 맞출 수 있다. 구체적 17상태 이벤트 `S` 및 neutral/ion source 선택기 `E`를 쓰면

\[F^{\rm photo}_{17}=S\,\operatorname{diag}(Ey)P_7\gamma,\quad J^{\rm photo}_{17}=S\operatorname{diag}(P_7\gamma)E,\]

`P7`은 HI를 3회, HeI를 2회, HeII를 2회 선택한다. 이 3-rate adapter는 비음수 사건률, 각 핵종 총량 및 핵자수 보존, photo-event 전자 생성 `q17^T F=Σ_j γ_j y_{src,j}`를 유지한다. REI PR262의 실제 `source17` frozen 7행을 동일 source와 (β,κ)로 재계산해 `F,J_y` max 상대차 각각 `1.20e−16`, `1.15e−16`을 얻었다. **일반적인 3개 independent atomic photo rates가 실제 양의 photon spectrum으로부터 실현 가능하다는 증명은 아니다.** 실제 흡수 에너지/가열/secondary electrons는 6모멘트 또는 photon spectral closure를 별도로 필요로 한다.

## 5. 독립성·물리적 진척

정적 Python 소스 원전 replay, SymPy Exact Fraction, C++20 independent long double, Wolfram CAS 유리수는 서로 다른 검산 수준이다. **native different-author R6/C9 = NOT_RUN**. BASS PR234의 `atomic_coefficients.json`이 본 백업 내 존재하지 않고, 실제 공통 inventory, BASS `K,H,nHref/nb`, REI full `J_y`, nucleus+CR+fast state, 실제 photon SED 및 thermal closure가 맞춰지지 않았다. `F4 PARTIAL`, `L4 false`, working33/88, central28/88, physical fast4/7, delta0, 이전 예산/실패·`NO_MORE_IVPs` 유지. parent PR266 `cargo fmt --check`의 CI failure는 따로 보존한다.

**문헌:** Puchwein et al. (2019), *MNRAS*, DOI 10.1093/mnras/stz222; 원본 표 https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt . Ovchinnikov et al. (2021), *Bioinformatics*, DOI 10.1093/bioinformatics/btab010 (exact constrained ODE lumping 정의), 이 두 source가 이번 수학적 determinant/minimax 수치를 직접 주장하는 것은 아니다. 이 수치는 해당 locked 입력에 대한 새 유도다.
