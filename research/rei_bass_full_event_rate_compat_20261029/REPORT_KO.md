# REI/BASS 실제 photo-event source 비호환과 3-rate 정적 수선

**관측된 출처:** BASS PR234 원래 `atomic_network.py`, REI PR262 `source17.py`/7 saved ON_refined, REI PR261 Puchwein2019 13행 projected source. 형제 REI PR267는 full21 self-electron rank-one Schur 정리이며 **병합되지 않은 별도 입력**. 2026-10-29 최신 PR266 소스에서 출발한다. 기존 원 DAG working **33/88**, central **28/88**, physical fast **4/7**, `F4 PARTIAL`, `L4_ready=false`, physical delta0, `NO_MORE_IVPs=true`.

## 정식 결과

원래 BASS는 `G0=uv_scale*Gphoto_const`; UV scale이 시간에 따라 임의 양수여도 photo-rate 비율들은 시간과 독립이다. 반면 Puchwein2019의 13행 **투영본**에서 z2.48과 z4.62의 HeII/HI 비율은 각각 `53/11700`과 `149/3790000`, 상대 변화 `115.22400045889979`배. 한 개의 고정 BASS photon spectral shape로 두 적색편이의 두 광이온화 채널을 정확히 재현할 수 없다.

더 강한 **날카로운 최적 오차**: 임의 정적 양의 `k=b_HeII/b_HI`와 두 epoch별 독립 가변 UV amplitude를 허용해도 HI,HeII rate의 네 상대오차 중 최소 가능한 최댓값은

`(sqrt(53/11700)-sqrt(149/3790000))/(sqrt(53/11700)+sqrt(149/3790000)) = 0.8295586873156143629955885231...`.

최적 `k=0.0004220059100479202`. 이는 해당 *광이온화 반응률 4개*의 조건부 상대오차 하한이다. 물리적인 `n_e`, `tau_T`, `CMB C_ell` 오차로 옮기지 않는다. P19 common `(beta,kappa)` scaling은 세 photo-rates에 같은 양의 row factor를 곱하므로 비율·rank가 그대로이다.

실제 P19 11개 calibration-domain knot의 정확 유리수 rank: `rank(11x3 [GammaHI,GammaHeI,GammaHeII])=3`, `rank(11x6 [Gamma/heat x3])=6`. 세 z `2.48,3.64,4.62` rate determinant exact `235010831/2500000000000000000000000000000000000000000000000` (s^-3), 1e36배 값 `0.0000940043324`. 적어도 3개의 고정 rate-space 벡터가 있어야 11개 3-channel P19 모멘트를 exact 선형결합으로 표현할 수 있다. 세 채널을 직접 독립 rate 입력으로 주면 REI PR262 일곱 photo 이벤트를 정확하게 재생하며 nucleon/family-count/charge source 항등식과 비음수 사건률을 보존한다. 이 조건부 **rate-space adapter는 물리적 photon spectrum의 존재성·흡수 광자 에너지·photoheat·Li 및 nuclear/CR channel의 일관성을 인증하지 않는다**.

## 실제 새 실행 결과

| 항목 | 결과 | 범위 |
|---|---|---|
| 원본 BASS/REI/P19 소스 5개 SHA | 5/5 PASS | BASS native atomic coefficient data는 이 SOURCE ZIP에 없음 |
| SymPy exact rational rank | 11x3 rank3, 11x6 rank6 | 고정 13행 P19 투영본 중 calibration 11행 |
| Wolfram CAS | exact determinant, 두 optimum 평형잔차 각각 0 | 독립 저자 검토 아님 |
| Python 3.13 unittest | 31/31 PASS | source-lock 음성, exact generator, 오차 bound 등 |
| 원본 PR262 saved-state source replay | 7/7 PASS, max `F` rel 1.19735e−16, `Jy` rel 1.14509e−16 | 이미 저장된 상태, 신규 IVP 0 |
| C++20 long-double 독립 공식 | 6/6 PASS, 최대 Decimal80 대비 rel 약1.25e−19 | rate ratio, best k/error, determinant |
| 새 그림 2개 | source-only PNG 생성·시각 점검 | 과학 posterior/시간진화 그림이 아님 |
| full BASS rate coefficient/FULL21 J/Puch spectrum | NOT_RUN | 데이터·동일 initial inventory/source 부족 |
| real different-author R6/C9 | NOT_RUN | native subagent tool 노출되지 않음 |

### 실제 진단 및 수리

1. 최초 `source_lock()`의 parent P19 Git blob 상수 전사에 단 2자 문자 차이가 있어 fail-closed로 첫 실행 실패. 올바른 SHA를 원본 P19 JSON과 대조해 수정. **원본 입력 바이트는 수정하지 않음.**
2. 최초 31 Python tests에서 2개 FAIL: `test_wrong_source_blob_refused`는 source-lock 검사와 P19 loader가 다른 path를 읽는 defect를 실제로 드러냈고, `test_source_changed_residual_neq_zero`는 He3++(state9) 한 사건의 target rate를 He4++(state12)까지 포함하는 잘못된 기대값을 사용했다. 검사/파서를 하나의 path로 묶고 target expected component만 수정한 후 31/31 PASS. Acceptance/tolerance 변경 없음.

## 입력별 판정

**MATCHED_SOURCE_REI_7PHOTO = PASS_SCOPED.** 동일 Puch source와 7 PR262 저장 상태에서 generator 및 Jacobian 등가. **SINGLE_BASS_UV_SCALAR_CROSS_Z = REFUTED_SCOPED.** 물리적 BASS photon shape가 fixed라는 원본 source 규칙 안에서는 두 시점 rate를 exact하게 함께 맞추지 못함. **THREE_INDEPENDENT_RATE_CHANNELS = MATHEMATICALLY_CONSTRUCTED_SCOPED.** 실제 양의 광자 스펙트럼으로 구현하려면 channel-dependent photon flux/spectrum source owner 및 photoheating까지 새로 결속해야 한다. **BASS_FULL21↔REI_FULL17 = INPUT_BLOCKED.** PR265의 H1/He4 및 T 재고 mismatch, PR266 Li6 hidden/electron feedback, PR267 chemical rank-one은 유지·재사용하지만 서로 자동 병합하지 않는다.

**진척**: 새 scoped 이론 9/10 + 코딩 9/10 =18/20, R6/C9 independent author NOT_RUN. **원 working 33/88, central28/88, F4 4/7, physical delta0**. 일반 화학 source/clock/thermal closure와 실제 온도 및 H,nHref,K 바인딩 없음. GitHub Actions inherited cargo fmt --check failure를 PASS라고 주장하지 않는다. 신규 IVP/old campaigns rerun 0, 예산 재할당 0, `unknown overhead UNKNOWN_NOT_ZERO`.

## 후속 과학 연구

아래 순서로 **물리적 photon source 공급자가 승인한 6-moment time-varying spectral lift**를 추가 연구하라. (i) BASS original `atomic_coefficients.json` 및 `provenance/atomic_sources.json` owner 데이터 source-lock 확보, (ii) 3 rate positive/source-event operator와 BASS photon intensity map 사이 realizability 조건 연구, (iii) Puchwein six heating moments의 별도 energy ledger 및 T/He3/Li6 reservoirs, (iv) 실제 공통 inventory와 e,H,clock, nHref/nb 결속, (v) static full-event/J commutator 및 independent R6/C9 검산, (vi) 물리 F4/L4는 별도 양성 조건 충족까지 HOLD. 자료가 없으면 새로운 UV 스펙트럼·tau·CMB 관측값을 만들지 말 것.
