# ISO-COUPLE-P3: MD14/BB50k 출생 광자, 정확한 Bianchi-I Killing 전파, H/He/D 결합의 범위

2026-10-17. 연구 판정 `PASS_SCOPED_SOURCE_BIRTH_GEOMETRY_AND_POSITIVE_OWNER_CELLS`; 우주론적 전체 이력 `HOLD`. 원본 production 파일 수정 없음. 본 문서는 `contracts/P3_RESULTS.json` 및 `rust/rei_iso_couple_p3/`와 쌍을 이룬다.

## 1. 원본 입력과 실제 claim scope

사용된 것은 PR150 고정 Rust `axbi_sources.rs`의 `MD14_Z002_FESC_BB50K_13P6_100_V1`로, MD14 별생성률 고적색편이 연장과 `T=50000 K` 절단 흑체의 **선택된 물리모형**이다. 출생 적색편이 지지 `4<=z<=20`, 출생 광자 에너지 지지 `13.6–100 eV`, fesc 기본 0.2, 조건부 비교 0.25. 데이터로 직접 보증된 영역보다 source model을 넓힌 곳은 관측적 적합이 아니다. 원본 `AxbiSource::new(nH0,.2,16,8)`는 3개 문턱 영역×각 16개 에너지 셀×8 방향, 즉 출생 시점마다 **384개 positive cohort**를 생성한다. 에너지 셀의 대표값은 원본 함수에 의한 단위 셀 photon-count weighted 에너지 평균이고 연속 광자 스펙트럼 그 자체는 아니다. `normalization_relative_residual=3.500755241248044e-12`; 절단 100eV 바깥 BB 광자 분율 `6.181087358312833e-8`로 기록한다.

검증 대상은 부호 있는/없는 *off-shell*, prescribed non-tilted 축대칭 Bianchi-I `a_⊥=a exp(-b)`, `a_∥=a exp(2b)`; 원본 `ConstantAxisymmetricBackground`와 `CharacteristicRay::pullback` 사용. `H=1.2e-16 s^-1, s=±.06H` 단기 화학 사례, 순수 Killing 비교만 `s=±.08H`와 1e15s. 실제 Einstein 제약, 물질 backreaction, 현재 CMB 사중극자 상한을 충족하는 우주론이 아니다.

## 2. 개별 birth cohort의 정확한 특징곡선

`P_i=a_i(t_b) E_b n_i(t_b)`를 보존하면 임의 고유시각의 에너지는

\[ E(t)=E_b\bigg[\sum_{i=1}^3 n_{b,i}^2\Big(\frac{a_i(t_b)}{a_i(t)}\Big)^2\bigg]^{1/2}. \]

이 표현에서 photon count의 reference-comoving inventory는 중력 redshift만으로 바뀌지 않으며, 광자 *에너지*의 차는 geometric radiation work다. 부피 `V=a_1a_2a_3`에서 가스 number densities `n_s ∝ 1/V`, 고정 조성 ideal monatomic thermal density `u_th∝V^(-5/3)`. 이력 변수에 올린 `W_geom`은 photon redshift와 gas expansion work를 별도로 적립한다. 이것은 photon birth/absorption이 아니다.

출생 이산화는 중간시각 `(t_n+t_{n+1})/2`에서 원본 `AxbiSource.at_redshift(z(tmid))`, 출생수 `j(tmid) Δt`, 각도·에너지 원본 cell 확률 가중치를 사용한다. 1차원 고유시각 retarded source-age 지원이며 native on-shell BASS 생성원 / 전영역 observer optical-depth의 검증과 구분한다.

## 3. 흡수는 photon을 정확히 한 소비자에게 소유시킨다

한 cohort의 frozen-gas midpoint opacity는 `κ_j=n_j σ_j[E(tmid)] c>=0`, `κ_tot=Σ_j κ_j`, 생존/흡수는

\[ N_{n+1}=N_ne^{-\kappa_{\rm tot}\Delta t},\qquad\Delta N_j=N_n\left(1-e^{-\kappa_{\rm tot}\Delta t}\right)\frac{\kappa_j}{\kappa_{\rm tot}}. \]

`j=(HI,HeI,HeII,DI)`. `κtot=0`이면 흡수=0. 각 채널의 `ΔB_j=χ_j ΔN_j`와 열전자 `ΔUth,j=(E−χ_j)ΔN_j`는 `ΔN_j E=ΔB_j+ΔUth,j`로 동일 사건에서 배분된다. `DAtomicProvider` threshold와 실제 D photo source bound check를 통과한 후에만 transaction commit; 실패 시 원본 state는 유지한다. Gas collision/CI/RR/CX/CE/FF/CMB는 기존 P2 source-native 구현에서 photons **OFF**로 한 번만 소유한다; `AtomicRhs XOR ThermalSubstep`를 중복 사용하지 않는다. 기하와 source injection을 포함한 총 comoving energy 교환은

\[\Delta E_{\mathrm{total,comoving}}=E_{\mathrm{birth,comoving}}+W_{\mathrm{photon,geom}}+W_{\mathrm{gas,expansion}}\]

으로 구조적으로 검산한다. Time-varying rates/gas/species를 정확히 적분한 것은 아니므로 전체 연산자 분할은 1차/조건부다.

## 4. `64-bin` 압축과 `384 owner-cell` positive 비교는 별개의 과학 주장

P2의 `MAX_PHOTON_BINS=64`를 그대로 두고, P3 연구자의 64bin representation은 original 48×8 owner cells를 8개 energy groups×8 angular bins에 number+energy moments preserving 방식으로 **반응 직전에** 축약한다. 이 평균값에는 nonlinear σ(E) 반응이 일반적으로 보존되지 않는다. 가령 `σ(E)∝E^-3`이고 `(1±x)E0`를 각각 1/2씩 섞으면 `⟨σ⟩/σ(E0)−1=6x²+15x⁴+...`; Wolfram 계산으로 확인했다. 따라서 number+energy를 보존해도 종별 포토이온화율을 보존하지 않는다.

수치: 3 energy segment ×8 angle 첫 absorption total grey mismatch 2.39%; 8 energy groups×8 angle aggregate 0.464%; 하지만 species threshold 민감도가 다르다. 세 threshold segment에 8 groups를 분할하는 56개 contiguous 정수배분의 scoped minimax `(2,2,4)` max species mismatch 0.603%; 이 수치는 다른 압축법에 대한 no-go 정리가 아니다.

이번 신규 `positive_age.rs`는 **384 original owner-cell cohort 각각** frozen-opacity를 평가해 P2 화학/에너지 적분기에 event inventories만 전달한다. 이 비교는 가스·광원·출생시각이 같을 때 압축 오차를 분리한다. 특정 8e10s의 N64 source-on FLRW 이력에 대해 64-bin 대 384-cell의 *누적* HI,HeI,HeII,DI 상대 사건차는 각각 `0.17772%, 0.44119%, 0.45241%, 0.16305%`, 생존자 photons 차는 `1.25484%`; 기체 온도차 `7.6564e-5 K`. 이것은 외부 PR171 H1/H2 native age/transport acceptance가 아니며, 그 0.5% 조건을 승격할 수 없다.

32 finished matched rows (`N=8/16/32/64 × FLRW/BI±/fesc=.25 × positive/grey`)에서 photon-number ledger max `1.9517013410e-15`와 step-total energy ledger max `6.9435384675e-16`를 확인했다. 이는 해당 owner-cell 모델의 산술 보존이며 rate/source physical uncertainty 혹은 total EoR 과학 정확도가 아니다.

시간 8→16→32→64에서 positive age 결과 자체도 계속 변한다. N128을 포함하던 exploratory run은 제한시간 내 **39/40 행 부분 종료**되었으므로 배제했다. 최종 scientific matrix는 complete 32 rows 뿐이다. 더 큰 N과 age, H/He source on time/a/angle/spectral refinement가 필요하다.

## 5. Source-only 정확한 Killing quadrupole

시간 1e15s의 opacity-free source births + exact original Bianchi Killing map은 N128,GL8에서 normalized observed energy P2: FLRW `-2.569e-17`, shear+ `-0.007051893`, shear− `+0.007114046`. 이는 sign-odd response가 존재함을 보여주지만 인플레이션·CMB 관측·Einstein backreaction의 과학 허가는 아니다. N8→128 birth timing refinement 및 GL8→16→32는 별도 CSV에 있다.

## 6. 아직 입증되지 않은 부분

`ISO-COUPLE` 전체: HOLD. Original `BI-SIGNED`, `FLRW-CONV`, `SA-01/02`, `HOLD_SOURCE_AGE_NATIVE_TIME`, `HEI_SPECTRAL`, observer-total CMB τ, material/tilted electron current, pre/post z20 end tails 모두 이전의 HOLD를 유지한다. 이번에 모든 BASS geometry time-series CSV를 가져온 것도 아니고 Bianchi shear와 H/He/D thermal feedback을 self-consistently Einstein iteration한 것도 아니다. 이 bounded 연구는 native owner 파일을 고치지 않는 **독립 source-bound scientific comparator**다. 다음 `ISO-COUPLE-P4`는 source+opacity retarded timing, 384-cohort per-owner adaptive/spectral comparison, 동일 광원 하의 source-time/age/energy/angle/time-step independent resolution와 physical BASS history intake다.
