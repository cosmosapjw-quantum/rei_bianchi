# 2026-10-27 공급자 갱신 조사와 다음 결합 입력

## 결론

다음 계산의 직접 재사용 입력은 **REC124의 실제 RR/DR 열적 손실 계수와 Compton 모듈**, **CR의 canonical event·입자수·에너지 계약**, **HE의 thermal-pool count/EOS 투영**이다. 최신 REI PR236은 이미 native PW19 25-state 광전자 주입을 갖고 있다. 현재 선택 source는 PW19_z2.479_HeII_exclusive, He3II/He4II의 54.42 eV 문턱과 조건부 전자 반응률 동일성을 유지한다. 초기 요청의 H1 source 확장과 이 최신 native He II 선택을 혼합하지 않는다. H1 광전자 분포나 기존 GRID044 연속 스펙트럼을 다시 계산할 필요가 없다.

현재 관측한 HE/CR 공개 공급자에는 PW19의 약 0–49,945.58 eV와 현재 상태에 그대로 적용할 **유한시간 공동 입자수 편입률 J_N·열에너지 Q_th**가 없다. 이것은 공급 입력의 현재 범위 판정이다. 물리적 불가능성이나 연구 전체 중단을 주장하지 않는다. 명시적 조건부 ν 모형을 선택한다면 그 수학·수치 결합은 진행할 수 있지만, 실제 stopping supplier 채택과 구분해야 한다.

## 조사 범위와 현재성

| 저장소 | 전체 브랜치 수 | 페이지별 수 | 10월 25일 00:00 UTC 이후 갱신 PR 수 | 선택 최신 입력 HEAD |
|---|---:|---|---:|---|
| WU088_HH | 159 | 100 + 59 | 4 | 87933da5654bb2e4d93f7de4341df5e0fa0f8716 |
| rec_bianchi | 156 | 100 + 56 | 3 | 4a8e541030ee2cbd02e26ba671083b705d309d49 |
| bass_cr | 184 | 100 + 84 | 4 | b11b2e9255f2b10fb5582376412e045bd1e9151c |
| BASS_HE | 107 | 100 + 7 | 2 | ac6042a6b0610b09d0576538767ee0299389a5eb |
| bass | 277 | 100 + 100 + 77 | 4 | d7dcd731de1a0c59e5e65db5038c333f5abae0bd |
| vigilode | 215 | 100 + 100 + 15 | 3 | 72836e0290b66d33f4ca1771284b1c8070669a74 |

총 **1,098개 브랜치 metadata**를 마지막 짧은 페이지까지 읽었다. PR 목록은 updated 내림차순 첫 50개가 각 저장소 모두 cutoff 이전까지 내려가므로 이 기간의 갱신 PR 20개를 빠짐없이 포괄한다. 전체 브랜치의 모든 과거 구현 내용을 읽었다는 뜻은 아니다. 실제 source-body 검토와 metadata-only 검토를 SURVEY_COVERAGE.json에 PR별로 구분했다. GitHub 밖의 비공개 대화, 살아 있는 native dirty 작업공간, 미관측 실행은 조사했다고 주장하지 않는다.

2026-10-27 03:08:32 UTC에 위 6개 HEAD와 REC native thermal branch, VigilODE 성능/제어 2개 branch, 총 9개 ref를 다시 읽어 모두 같은 SHA임을 확인했다. 선택 WU/CR/HE의 root AGENTS 원문은 보존했다. REC/BASS/VigilODE 선택 commit에서는 root AGENTS.md 404와 root tree를 함께 확인했다. REC native 및 VigilODE 새 engineering branch의 정확한 root AGENTS 경로도 404였으며, 이를 다른 위치나 native 정책의 부재로 확대하지 않았다. URL 인코딩 실패와 정확한 경로 부재는 HEAD_FRESHNESS_CLOSURE.json, FETCH_GAPS.json에 남겼다.

## 1. REC: 바로 재사용할 실제 열적 계수

현재 extension HEAD 4a8e541에는 native thermal 파일이 없다. 최신 REI가 이미 pin한 별도 native branch research/rec-compton-coupled-20261022의 **e6ecef7624e39bee66b39e09d99fe355f76e2eae**에서 다음 10개 파일을 정확히 복구했다.

- rec_thermal_moments_20261022/code/thermal_system.py
- 같은 code/thermal_sources.py, recombination_moments.py
- provenance/MAO_SOURCE_LOCK.json
- data/mao2017_calc.dat, mao2017_pars.dat, mao2017_selected.json
- 해당 FROZEN_CONTRACT.md
- rec_thermal_omitted_budget_20261022/code/compton_budget.py
- 해당 FROZEN_CONTRACT.md

로컬 기준은 rec_bianchi/files/e6ecef7624e3/research/이다. 모든 Git blob identity를 확인했고 Mao 원자료 2개와 selected JSON의 SHA256도 원래 source lock과 일치한다. 계수를 평가하거나 module import, constructor, 옛 quadrature를 실행하지 않았다. 전체 63-state host 의존성의 완전 복구·실행을 주장하는 패킷은 아니다.

**ThermalSources.coefficients(T)**와 logT 미분은 현재 상태에 필요한 직접 재사용 지점이다. 공유 계수 domain은 100–10⁶ K이며 현재 약 14,919.86 K를 포함한다. RR 기본 mao2017은 부모 α에 Mao 평균 에너지 factor를 곱하는 hybrid다. Mao Eq.7의 자연로그, T_eV, recombined-electron 인덱싱, DR signed fitted resonance 성분과 nonnegative total loss를 보존한다.

기존 ThermalSources.evaluate는 prompt primary thermalization과 η=(1+q)Y를 가정한다. finite ξ 상태에는 그대로 호출하면 안 된다. 현재 REI의 n_e,th=n_b(qY−ξ), χ_th=(1+q)Y−ξ를 RR/DR/thermal Compton의 동일한 thermal pool에 적용하고 모든 state·clock·기준밀도 미분을 연결해야 한다. compton_budget.py의 실제 dilute-spectrum 순간량과 Planck-reference 순간량도 구분한다. 하나의 복사 에너지 밀도만으로 다른 spectral moment를 만들어 넣지 않는다.

근거: [REC native frozen contract](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e6ecef7624e39bee66b39e09d99fe355f76e2eae/research/rec_thermal_moments_20261022/FROZEN_CONTRACT.md), [thermal_sources.py](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e6ecef7624e39bee66b39e09d99fe355f76e2eae/research/rec_thermal_moments_20261022/code/thermal_sources.py).

최신 REC138의 HD/H5 확장은 별도 유효범위를 유지한다. HD는 9 levels·8 lines·50/100/200 K literal table parser이며 line-frequency source discrepancy/uncertainty 미결을 포함한다. H5는 313 queries와 626 endpoints의 입력 결속이며 physical error-bound coverage는 0이다. 이 결과를 새 stopping rate나 실제 양의 오차 반경으로 해석하지 않는다.

## 2. CR와 HE: 실제 가능한 조합과 적용 범위

CR의 최신 contracts.py에는 이미 canonical EventBook, matching-pool CaloricDerivative, source support·frame·proper/comoving/reference conversion 검사가 있다. boundary_flux는 특정 cutoff에서 Q=E_c J_N을 요구하는 계약이다. 일반 분포 전체의 finite-time relaxation에 임의로 대입할 수 없다. first-entry와 irreversible assimilation을 구분한다.

직접 읽은 CR104/105의 기존 실제 계산은 T=10,000 K, thermal n_e=0.14 cm⁻³=1.4×10⁵ m⁻³, prescribed lnΛ=20, stationary isotropic common-T baths, 초기 0<W<10 eV, 상단 Rθ=34.47/68.94 eV의 저장 finite chains다. 원 MTCS support는 H1 0.01–1000 eV, He4 0.1361–1360.6 eV이며 외삽을 허용하지 않는다. 현재 PW19 약 49.95 keV·n_b≈10.6693 m⁻³·14,919.86 K로 무검증 전용할 수 없다. H1/He4 ground spontaneous RR도 zero-recoil stationary-heavy-target component이며 total all-level RR와 이중 합산하지 않는다. RR retained photon은 thermal heat가 아니다.

근거: [CR104 원 계약](https://github.com/cosmosapjw-quantum/bass_cr/blob/257007cc708d0db403ec2ff0c741e4a10b6207ab/research/cr_n5_neutral_elastic_20261025/FROZEN_CONTRACT.md), [CR105 원 계약](https://github.com/cosmosapjw-quantum/bass_cr/blob/b1aed87852d4f8994494c2ae41a913afd390eccd/research/cr_n5_rr_milne_20261025/FROZEN_CONTRACT.md).

HE102는 32 species records, 18 scalar PI/RR/CI providers, 27 transport pairs·243 Q expressions를 조사했다. 27쌍의 분류는 thermal collision integrals/auxiliary fits다. 선택 H–He의 정확한 공급자는 Mutation++ 58678c0e038eb2f078fed3b45640741fdaf167dc, data/transport/collisions.xml, blob d86bf74e05e6bcac9db67cfc03055621ebed2f8c이다. 50–50,000 K 두 Maxwellian의 zero-drift/linear-drift 조건부 map이다. differential cross section, joint event law, physical provider admission은 모두 false다. H–He 열적 map을 PW19 빠른 전자의 stopping law로 바꾸지 않는다.

그와 별도로 최신 **exchange_closure.py**는 다음 결합에 바로 쓸 수 있는 algebra를 이미 갖고 있다. temperature_rhs는 thermal pool의 Γ_s만 받아 C_V·Tdot=Q−Θp−shear−div(q)−Σ ε_sΓ_s를 계산한다. PopulationSourceReceipt는 fast birth와 thermal source를 분리하고, EnergyTransfer는 canonical owner와 두 반대 부호 leg를 검증한다. population-derived binding energy는 독립 RHS가 아닌 derivative witness로 돌려준다. 실제 물리 ν나 J_N,Q_th를 생성하는 함수는 아니다.

근거: [HE selected source](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/pair_source/SELECTED_H_HE_SOURCE.json), [HE caloric/ownership module](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/exchange/exchange_closure.py).

HE101 owner HEAD 28a26f4d...의 직접 CLAIM_GATE.json은 아직 19/20, C8 PARTIAL_EXPORT, reserve=0, physical event cross section/recoil false다. 부모가 별도 개인 문맥의 20/20 export 진술을 알려 왔으나, 이 조사에서는 그 대화나 더 새 owner archive를 관측하지 않았다. 따라서 Git의 19/20 관측과 외부 진술을 혼합하지 않는다. export 수와 physical admission도 별도다.

## 3. WU, BASS, VigilODE의 새 결과

WU150의 R1/R2는 actual source registry와 target19 integer projection을 넓혔다. R1의 102 variants·125 columns·92 identities와 R2의 새 26 variants·24 columns를 재사용할 수 있다. 28 listed directions 중 27은 primary reference가 있다. 새 rate/Q/energy/consumer admission은 모두 false이며 He4(γ,dd)의 수치 원자료 의존성은 남는다. source availability를 실제 계수/energy로 승격하지 않는다. 기존 compiler와 249 checks, PHYS91 zero budgets를 보존한다. [WU R2 admission](https://github.com/cosmosapjw-quantum/WU088_HH/blob/87933da5654bb2e4d93f7de4341df5e0fa0f8716/research/provider_registry_network19_20261025/SCIENTIFIC_ADMISSION.json).

BASS192 B3g는 실제 **저장된** 512 births/514 endpoints를 연결했다. 원 과학 사례는 B3c S2의 manufactured cold non-tilted recoil-free detached f_plus=0 Bianchi-I다. 이것을 GRID044/PW19 continuum source라고 부를 수 없다. binding.py, geometry.py, transport.py, readiness.py와 계약을 복구했다. 새 실제 cell→incoming-face source, finite spectrum/angular/time measure, frame/proper clock/volume, interpolation bounds와 atomic internal/recoil owner가 필요한 B3h는 별도다. cQ rate와 T,π stock을 구분하고 이미 적용한 endpoint stress kick을 재가산하지 않는다. [B3g admission](https://github.com/cosmosapjw-quantum/bass/blob/d7dcd731de1a0c59e5e65db5038c333f5abae0bd/research/bass_b3g_actual_cohort_binding_20261025/ADMISSION.json).

VigilODE의 전체 215 branch metadata에는 named V6 branch가 없었다. 부모가 복구한 실제 V6 ZIP의 SHA256은 8779aef897595e2d4cbbe2e46ff18bae9f4521e8a66066379b864947c216d555이며 1,223,513 bytes다. 이 조사는 12개 핵심 파일을 byte-identical하게 복사했다. 과학 판정은 **ADMIT_RECOVERY_ACTUAL_POINT_BINDING_ONLY**다. BASS cc602e20...의 s04_m04_r04 row80, 실제 point checks 13/13, protocol repairs 10/10, independent saved arithmetic 14/14·20 FD rows 범위다. 이 결과가 현재 REI PW19 25-state derivative를 검증한 것은 아니다.

V6는 ProvidedOnly, partial_x UNSUPPLIED, native norm evaluations 0, actual native integration OPEN, V7 full restore NOT_RUN, V8 certificate false다. 기존 budget은 119 RHS/7 J/3 actual pairs, wall 38.853874599994015 s, closed=true다. 원 36 FD rows/manifest serialization 전체는 미복구이며 그 상태를 보존한다. publication은 BLOCKED_EXTERNAL_NO_ACK로 Git consumer commit/PR/central return은 null이다. source archive 복구와 게시 성공은 다르다.

별도 native engineering branch도 관측했다. 0d3c7c51...의 switcher economy는 deterministic work와 direct-path bit identity의 개선을 보고하며 wall-time drift 때문에 시간표는 diagnostic/unreliable이다. 9b062e81...의 joint-controller는 opt-in이며 production HOLD다. 이 둘은 V6/V8 physical domain gate의 완료 근거가 아니다. [switcher 분석](https://github.com/cosmosapjw-quantum/vigilode/blob/0d3c7c510c5039b46ff81c9c23e04bc102114ab0/research/adapter_switcher_economy_20261026/ANALYSIS_KO.md).

## 다음 동결 계약의 준비 상태

1. 최신 REI의 native 25-state primary source를 그대로 parent로 두고, ξ·thermal n_e·thermal particle count의 미분과 REC RR/DR/Compton 열적 계수를 연결한다.
2. 각 편입 사건에서 fast number loss, thermal number gain, fast kinetic loss, thermal energy gain을 한 canonical transfer로 묶는다. 기준밀도가 변하면 해당 quotient 항과 Jacobian을 함께 유도한다.
3. 공급된 실제 물리 stopping law가 없는 동안 선택하는 finite ν는 명시적 조건부 모형으로 유지한다. 기존 CR low-energy chain나 H–He Maxwell map으로 물리 출처를 대체하지 않는다.
4. 바뀐 모델의 실제 client derivative/domain 검증은 새 scoped node로 수행한다. V6의 이미 닫힌 예산과 기존 IVP를 재사용 실행하지 않는다. 전체망·V7/V8·L4는 별도 gate로 둔다.

실제 소스 48개/516,251 bytes와 V6 복구 subset 12개/123,980 bytes를 보존했다. source ID, Git blob, SHA256, 원 URL은 SOURCE_FETCHES.jsonl, SOURCE_INDEX.json, vigilode/RECOVERED_V6_SOURCE_MANIFEST.json에 있다. 준비된 native REC subset은 THERMAL_NATIVE_DEPENDENCY_MANIFEST.json으로 분리했다.

새 과학 실행·suite·source quadrature·IVP·새83·NCP dispatch는 모두 0이다. source body를 읽고 해시를 확인했으며 과학 모듈을 import하지 않았다. metadata/recovery/review CPU·wall은 계측하지 않았으므로 null이며 0으로 꾸미지 않는다. 기존 남은 예산, 과거 unknown 비용, 실패 및 delivery gate는 초기화하지 않았다.

