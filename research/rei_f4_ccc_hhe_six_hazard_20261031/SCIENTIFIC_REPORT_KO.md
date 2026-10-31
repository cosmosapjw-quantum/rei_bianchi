# REI F4 | 원본 CCC 6개 전자충돌 채널 × BASS193 원본 배경의 부분 충돌빈도

2026-10-31 | 연구 분류: **원본 source 기반, 제한된 물리 수치계산**. 단일 bounded 연구 단위. 부모 GitHub Draft PR #309 HEAD `701add5f6536d091350650f2b6649cded0c0de06`에서 새 독립 브랜치 생성, PR #306/#307/#308 읽기 전용. Signature (-,+,+,+). c, k_B, 전자 질량은 명시적 물리 상수. 새 초기값 문제(IVP), REI17 화학적 생산 계산, 분리된 CMB/온도 observable 없음.

## 1. 원전과 데이터 동일성 (R2/C2)

- 물리적 **원저자/1차 근원**: Curtin Convergent Close Coupling (CCC) [https://atom.curtin.edu.au/CCC-WWW/index.html](https://atom.curtin.edu.au/CCC-WWW/index.html). H I: Bray & Stelbovics, *Physical Review A* **46** 6995 (1992), DOI `10.1103/PhysRevA.46.6995`; He I: Fursa & Bray, *Physical Review A* **52** 1279 (1995), DOI `10.1103/PhysRevA.52.1279`. 실측치라는 이름보다 **CCC 수치 산란계산에 기반한 published theory / author-curated data**가 정확하다.
- 이번 실행에서 실제 바이트를 읽은 **고정 배포본**: [EXHALE](https://github.com/seoncafe/EXHALE/tree/7388232fac2c3cdadad613515006de008360f1ab/src/utils/electron_degradation_data), Git commit `7388232fac2c3cdadad613515006de008360f1ab`, `CCC_H` / `CCC_He`. README가 원저자 ZIP의 추출본임을 명시한다. 원본 Curtin ZIP과 EXHALE 저장본의 **archive byte identity는 검증하지 못했다**.
- 입력 채널 6개: H I `TICS.1S` 이온화, `2P.1S`, `2S.1S` excitation, He I `TICS.s1S` 이온화, `s2P.s1S` singlet excitation, `t2S.s1S` triplet excitation. 인출 Git blob SHA를 `inputs/ccc_adaptive_b64.json`에 명시. **H I σ 단위 a₀², He I σ 단위 cm²**. `a₀²=(5.29177210903×10⁻⁹ cm)²≈2.800285204×10⁻¹⁷ cm²`; 1e-22 cm² 단위로 수치 보존, 원본 60 eV 이하 1,660여 표본에서 0.5%×각 채널 peak σ 이하의 소스선형보간 차이인 적응적 reduced representation을 사용한다. 원본 full CCC data와 수치 동일하다거나 정밀도를 더 높게 주장하지 않는다.
- 원본 BASS193 입력 `inputs/PR302_ARRIVAL_192.csv` SHA256 `155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df` (192 first-flight 광전자 source); `inputs/PR303_SPECIES_192.csv` SHA256 `dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09` (BASS saved H/He ion화 비율); `inputs/PR302_THERMAL_192.csv` SHA256 `292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6` (정규화, proper intervals); `inputs/PR_BASS193_ELECTRON_FEEDBACK_193.csv` SHA256 `50a9a7a2728f08ac4534f0e92071cdd4fb3b7ddc9a3e9f8175458d398ad06b0f` (원본 BASS21 baryon number density/193 redshift). 모든 원본 저장 파일은 **원본 zip의 byte identity를 확인하고 변경하지 않았다**. 불변 parents와 연결된 snapshot을 로컬 입력으로만 복사.
- 관측적 측정값이 아니라 공개 원자충돌 계산 데이터/원본 BASS193 모델 계산이라는 의미에서 `literature-supported + derived + numerically-checked`; 비평형 및 우주론적 관측 검증 주장은 없음.

## 2. 유도: 화학 종별 충돌률과 모멘트 제약

원본 BASS193 192개 arrival cell j에서 총 수소 핵수 밀도를 `n_H,j = 10^-6 [n_b,j/m^-3] × [n_Href/n_b]_j` cm⁻³로 두고, 원래 저장된 화학 조성을 그대로 결합한다:

`n_HI = n_H (1-x_HII)`, `n_HeI = n_H y_He x_HeI`, `n_e^(HHe) = n_H [x_HII+y_He(x_HeII+2x_HeIII)]`.

`n_e^(HHe)`는 원본 21종 charge sum에서 다른 원소·이온 기여를 누락하므로 **전체 native BASS 전자밀도와 동등하다는 주장을 하지 않는다**. 여기서 계산한 선택된 비열적 electron-target 충돌에는 `n_HI`, `n_HeI`만 사용했고 자유전자-전자 감속은 별개 sibling PR #309의 과학적 소유 범위다.

광전자 운동에너지 E_e [eV]에 대해 입사 속도 `v(E_e)=sqrt(2 E_e (1.602176634×10^-12 erg/eV)/(9.1093837139×10^-28 g))` [cm s⁻¹]. CCC의 σ_a(E_e) [cm²]를 사용한 **부분적인 첫 비열적 inelastic collision hazard**

`ν_a(E_e,j) = n_target(a,j) σ_a(E_e) v(E_e)  [s^-1]`.

기존 2E1 쌍 광자 에너지 `E_pair=60.922559447552 eV`. 첫 흡수종 s의 threshold χ_s가 주어지면 kinetic support `0≤E_e≤E_pair-χ_s`. 원본 PR302의 서로소 5개 band b에는 실제 양의 광전자 측도 `dμ_{jsb}(E)`, 총수 `N_{jsb}=∫dμ` [events/b], 일차 에너지 `M_{jsb}=∫E dμ` [eV/b]가 저장돼 있다. 원래의 unknown within-band spectral shape를 **발명하지 않고**, `Ebar=M/N`과 각 energy band의 support만 고정한다.

CCC source 원본의 σ(E) 삽입점과 물리 threshold를 고정하고 구간 내 `g_a(E)=σ_a(E)v(E)`을 source knot 위에서 계산, 그 knot 사이를 **직선 보간한 하나의 명시적 수치모형**으로 정한다. 이 g 모델의 볼록하위껍질 `co(g)`와 오목상위껍질 `ca(g)`는 정해진 N,M을 가진 임의의 양의 측도에 대해 정확히

`N n_target co(g)(M/N) ≤ ∫ν_a(E,j)dμ(E) ≤ N n_target ca(g)(M/N)`

을 보장한다. 일차 모멘트가 고정된 양의 측도의 극점은 **두 개 이하의 E support point**를 갖는다는 표준 순간 문제로 충분하다. 평균에너지 collocation `N n_target g(M/N)`은 같은 정의의 piecewise linear g를 사용한다. 직접 `sigma_linear(E)*sqrt(E)`를 쓰면 정의가 다른 연산자라 hull을 근소하게 벗어나는 사례가 발견되어 코드와 검증을 함께 교정했다. 두 모형의 평균점 차이 최대값을 `RESULTS.json`에 보존하고, 그 차이를 물리 오차 상한으로 오해하지 않는다.

He I TICS 원본 데이터는 24.5 eV에서 zero이고 24.6 eV에서 positive인데, 원자 이온화 threshold 24.587389011 eV 아래로 잘못 직선보간하면 유효하지 않은 양의 σ가 나온다. 24.587389011 eV에서 `σ=0`을 보장하는 물리 threshold knot를 별도로 삽입하고 그 이상에서 24.6eV 원본값으로 연결했다. 단위/채널/threshold를 원본 owner별로 보존한다.

**중요:** 여섯 채널의 부분 합은 전체 CCC 들뜸·탄성 충돌 또는 전자-전자 Coulomb 감속을 포함하지 않는다. 이 연구는 실제 cascade Monte Carlo, 물리적 secondaries의 기댓값, full stopping rate, 기체 heating/evolved T, CMB 관측량을 계산한 것이 아니다.

## 3. 실제 원본 source 생성 과학 데이터

원본 192개의 arrival × 4종 first absorber × 5 kinetic bands × 6 CCC target channels = **23,040개의 신규 실제 source-conditioned 부분 충돌률 행**, 각 arrival마다 192개 집계 행. 전자 수 정확한 원래 합 `4.374110632809567×10^-12 /b`, 초기 kinetic energy `6.749242464433258×10^-11 eV/b`; 원본 BASS baryon number density 범위 `6.841278420868708..2346.5584983579656 m^-3`, 수소 핵수 `5.164853236972×10^-6..1.71849173756036×10^-3 cm^-3`.

원본 191개 양의 source arrival 구간의 6개 부분 채널 합 평균에너지 evaluation 순간률 범위 `7.382922506215308×10^-23..3.0019362100083545×10^-11 s^-1`. 대응 `1/ν_partial`은 `3.331183376468939×10^10..1.3544771723638583×10^22 s`; **whole physical stopping time 아님**. `ν_partial Δτ_original>1`인 저장 cell `85/191`. 

여섯 source-weighted 정지 snapshot rate `∑_j N_j ν_a(j)`에 대한 숫자는 
H I ion `1.3182680221571288×10^-24`, 1s→2p `2.0734084499988123×10^-24`, 1s→2s `3.533286261676332×10^-25`, He I ion `1.3222587731108516×10^-26`, singlet 2p `6.695523672627935×10^-27`, triplet 2s `3.176956867116043×10^-27` [per original baryon per second **summed over distinct snapshot values**]. 이 sum은 **시간 적분이나 충돌 사건 수가 아니라 source-weighted hazard의 숫자 진단량**이다. 물리적 진화량으로의 직접 해석 금지.

조건부 source Li II pure singlet의 하한은 여전히 0이고 Ferrett/BASS native K 분모는 범위 제한만 확인됐다. He II *target* CCC cross section은 이번 여섯 채널에 들어있지 않다. 원래 PR308 kinematic bound는 He II 재이온화 사건 수용량이 극소임을 보였으나 이것과 독립적인 허용오차/확률 계산은 하지 않았다.

## 4. 물리 blind-referee 적대적 검토

- **Theoretical:** 원본 CCC 연구자 컴퓨터 코드에서 추출한 충돌 데이터는 1차 권위의 대조 자료지만, 개인 배포본 원본 ZIP과 EXHALE mirror 간 byte identity는 미확인. EXHALE raw의 6개 Git SHA와 reduced data의 선언된 정확도를 분리한다. CCC helium 2026 numeric는 저자 README에서 unpublished results라고 밝히지만 현재 공개 다운로드 파일은 존재하므로 기다리는 자료를 blocker로 두지 않는다.
- **Theory vs implementation:** He I TICS 아래-threshold 보간에서 가짜 충돌이 발생할 수 있다는 반례를 발견하고 exact physical knot를 추가해 봉쇄. 또한 `σ_linear(E)√E`와 `linear(σ_k√E_k)` 혼용 시 예상 평균값이 convex/concave envelope를 벗어나는 수치 반례를 발견, 동일 모델 g로 교정. 원자들 각각 H/He first absorber의 최대 E 조건과 positive-event band N/M을 검사한다.
- **Missing collision channels:** H I 1s→2s와 →2p가 별도, He I singlet/triplet 별도이며 2p excitation을 곧바로 Lyα emission으로 처리하지 않는다. He II, additional n≥3, elastic, spin channels, electron-electron Coulomb은 이 수치 모델에 없다. 여섯 channel rate를 event probability로 주장하면 물리 오류이며 하지 않았다.
- **Time/coupling:** source 최초 광전자 충돌시간은 total survival clock이나 thermalized heating time이 아니라 6-ch instantaneous rate diagnostic. `νΔτ>1`의 숫자에 `1-exp(-νΔτ)`를 적용해 실제 probability라고 주장하지 않았다. 원래 total BASS electron bath를 HHe projection과 동일시하지 않는다. 원본 BASS193의 z와 proper-time, source N,M과 conserved sums는 byte-locked.
- **No-go status:** 부정적인 강한 no-go theorem은 제시하지 않았고, 공개한 것은 허용된 유효범위의 수치 모델·조건부 계산 결과다. Distinct-author review NOT_RUN; same-author adversarial tests only.

## 5. Validation, backup and DAG

실제 동일 실행환경에서 `python code/compute.py`, `python -m unittest discover -s tests -q` (24/24 PASS), `python code/plot_science.py` (2 PNG, 2 SVG), SHA manifest 확인 및 clean isolated ZIP replay를 수행한다. 첨부 소스 파일의 SHA 변조 negative test, random 2400 two-point mean-preserving measures의 hull bracket, 채널 threshold, native baryon scaling, 단위, 서로 다른 저장 배열 ID를 검사한다. Source raw binary bytes/copyright PDF and original protected Git parents not republished.

단일 bounded auxiliary work-unit, canonical promotion **0**. Working DAG **33/88**, central **28/88**, F4-fast **4/7**, F4 PARTIAL, L4_ready=false, production HOLD, no merge/force-push/new IVP/auto-next. 다음 작업은 He II cross section source-backed 추가, CCC H/He complete excitation/elastic Coulomb owner와 같이 물리적으로 완전한 first-collision survival/energy bookkeeping을 구성한 후 native REI17 full F/J·source replacement 연결. CCC source is public; user correspondence is NOT a blocker.
