# BASS_HE → REI IGM | 원본 accepted 0→160의 He II Lyα 시간 적분 방출 입력

2026-11-02 KST | Original 26-event physical source native | SOURCE-CONDITIONAL DRAFT/HOLD | 원래 REI canonical Δ0.

## 연구 질문과 SSOT
BASS_HE PR #150(immutable parent HEAD f2d26ef196b50e69c1793cc4c29e96a248fe6c0b)은 accepted tick160의 원본 H/He/OTS 에너지 장부를 실제 계산했으나, 시간 적분된 광자 방출입력은 산출하지 않았다. REC #195(HEAD 0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235)는 REI PR #363의 원래 26-event accepted 상태를 0→64→128→160까지 복원했고, 기존 원본 kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644 및 source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b의 identity를 확인했다. 본 연구는 REI PR #355 exact HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00의 원래 물리 계산을 변경하지 않고, 그 accepted 세 시간 구간에서 HeIII-cascade → HeII Lyα 광자 원본 소스만 시간 적분한다. 이는 REC #195의 상태 재생, BASS #326의 F08 Rust 결합, BASS_HE #150의 정적 OTS 장부, BASS_CR #160의 *조건부 H Case-B Lyα*와 다른 소스 채널이다.

실제 사설 원본 상태들의 SHA256: tick64 aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425, tick128 bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6, tick160 74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6. REC195 source-inclusive ZIP SHA256 ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657. 원래 accepted state 0과 위 3개 endpoint는 독립적인 4개 우주가 아니라 하나의 실험 궤적이다.

## 실제 물리 계산: 정의와 데이터
원본 signature (-,+,+,+), gas proper time s, HeII Lyα photon Eα=(3/4)χHeII=40.81332 eV, εeV=1.602176634e-12 erg/eV. 원래 F05 유효 OTS 원자 이벤트:

r3cas=NHeIII ne max(αB,HeIII − min(αn2,HeIII,αB,HeIII),0),
Qescape,j=r3cas,j(1−v(T_j))(1−f_j) Eα εeV [erg/s],
Ndotescape,j=Qescape,j/(Eα εeV) [photons/s].

특히 original interval_discrete_map.event_box는 f_j ∈ [0.1,1.0]이고, f_j=1이면 유효 국소 탈출량이 0이다. 따라서 정확한 SOURCE interval lower bound는 0이고 upper만 유한하다. v(T)와 f의 원본 구간을 임의로 고정하지 않았다. 미해결 OTS 에너지 잔여량을 Lyα 광자로 환산하는 잘못된 closure도 금지했다.

Alexander–SDIRK2 native gamma=1−1/√2를 사용해 each accepted source half-step h에 대해 Iα = h[(1−gamma)Qescape,gamma + gamma Qescape,final]로 원본 이벤트 박스를 적분했다. 실제 accepted state는 원래 full/half1/half2 3개 native map에서 마지막 twohalf endpoint의 REIADP1 source interval SHA/arrays를 통해 확인했다. 각 구간 source times는 원래 t_tick = (tick/131072)*forcing.duration_seconds(0), 임의 연대나 인위적 cosmological geodesic clock이 아니다.

| 원본 accepted 구간 | 두 half-step Lyα 국소 탈출 에너지 상한 (erg) | HeII Lyα 광자수 상한 | 소스 시간 평균 에너지율 상한 (erg/s) |
|---|---:|---:|---:|
| tick0→64 | 7.844171553869001e48 | 1.1995953266017161e59 | 2.5157837781833317e37 |
| tick64→128 | 7.838038692322915e48 | 1.1986574388975963e59 | 2.5138168459858994e37 |
| tick128→160 | 3.917646536984917e48 | 5.991187781616674e58 | 2.5129362708905776e37 |
| **0→160 합계** | **1.9599856783176835e49** | **2.99737154366098e59** | source-time specific |

원래 동일한 5.523438018661131e66 H 원자 핵 inventory에 대한 누적 native SOURCE escaped HeII Lyα 광자수 상한은 5.4266410404792337e-8 photons/H. f의 실제 history가 없으므로 이는 upper only이며 양의 lower bound가 아니다. HeII Lyα 40.81332 eV는 HI·HeI ground-state thresholds 위, HeII ionization threshold 아래다. 따라서 이 한 선의 광자는 H I·He I 후속 photoionization에 기여할 수 있지만, HeII 이온화를 직접 일으키지는 않는다.

Original full-step 0→160 Lyα escape-energy UPPER 총합 1.9598504836947276e49 erg와 twohalf upper 1.9599856783176835e49 erg는 다르다. 두 값을 독립적으로 빼서 연속시간 적분 오차 상한이라고 주장하지 않는다. 이 수치는 원래 SDIRK source-site를 서로 다른 원본 계산단계로 평가한 numerical scope diagnostic이다.

## 본래 원본 물리 및 실행 검증
- 46,080개 원래 material cells × 3 accepted intervals = 138,240 새 original-source Lyα line-injection physics rows, deterministic CSV.gz, byte SHA256 13e05ff26adfb8eec5c2e0d0d028a1106f190771c642c2bb4306db79d9a80daf.
- Source JSON SHA256 545f363740a8533f643d1f26b9dd6fd0c30d42078800fc6dce0d3c604156a993.
- Same-author independent standard-library all-row photon-energy audit SHA256 197a4a603f27af881da6c615187523c60c162aa88fd943669a1d8e292068a9f3, 138240/138240 verified, max photon-number × Eα to erg relative discrepancy 1.976481654589712e-16.
- 원본 accepted tick64/128/160 population 및 log-temperature arrays source original identity exact 4/4 per state, original 3×(full/half1/half2) = 9 maps all original step.certified=True. 3/3 x 원본 14 ledgers include zero and zero table events. Local gate 최대 1.60637217206272e-4 < 원래 변경 불가 2e-4, public width 최대 1.720930111712704e-4 < 원래 변경 불가 2e-3.
- Original pinned NumPy2.3.5/pandas2.2.3/SciPy1.17.0 opt Python cold replay produced derived CSV.gz and JSON byte-identically, without source or tolerance changes; due old optional compiled system libraries NumPy1 extension ABI stderr diagnostic was separately captured, exit=0. Source-free normal Python 3/3 and -O 3/3 unittests PASS, tampered hash negative test fails closed, native original source 9-map cold readback and independent audit PASS.
- 본문에 도출한 HeII Lyα photon-number/energy identity는 Wolfram symbolic algebra에서 0 잔차로 확인했다. 수치 시뮬레이터 통과만으로 일반 물리적 인과적 transport 성공을 주장하지 않았다.
- GitHub Actions source-free published receipt workflow는 오직 derived data의 개수, hash, 단위, 원본 상태 서술과 public scope를 확인한다. private 원본 ZIP, original 9 native map을 원격 CI가 다시 돌리지는 않는다.

## 적대적 감사 / drift watchdog
가장 심각한 과학적 오해는 f=0.1 단일점의 Lyα 탈출 광자수를 원래 26-event accepted source의 예측으로 확대하는 것이다. 원본 f ∈ [0.1,1]은 모든 accepted interval 내에서도 남아 있으며, 탈출 lower=0이다. 또한 누적 source photon-count는 *local OTS approximation에서 빠져나온 수량*, 실제 cell-to-cell null ray로 수송되거나 관측자에게 도달한 광자수가 아니다. Source elapsed-time quadrature는 새로운 V2 approved original photon-transfer owner, full F05 [160,161] admission, Einstein-consistent Bianchi geometry, emitted angular distribution, E/B CMB spectrum을 전혀 입증하지 못한다.

이번 한 단위의 실질적 기여는 원본 accepted history의 H/He HeII Lyα local-escape SOURCE를 실제 proper-time source sites로 계산하고 138k physical data와 exact source/number identity를 보존한 데 있다. 후속 BASS_HE source-only atlas는 STOP한다. 중앙 REI는 동일 source/clock에서 \(J_\nu(t,x,n)\) spectral-angular emission + absorption and OTS transport와 geometry를 구현하거나, original 14-ledger V2 [160,161] official source admission을 해결해야 한다. Blind different-author referee와 native subagents는 NOT_RUN; 동일 작성자 독립 계산과 본 적대적 감사만 수행했다.

REI central 28/88_REPORTED, working 33/88_REPORTED, physical fast 4/7_REPORTED, BASS_HE physical 14/18_REPORTED, canonical delta 0, production HOLD, no merge / no force push / no original source tolerance change / official tick161 not accepted.

원전 방법론: Mellema et al. 2006 C2-Ray doi:10.1016/j.newast.2005.09.004, Friedrich et al. 2012 helium-coupled OTS doi:10.1111/j.1365-2966.2012.20449.x. REI/REC original source is actual numerical physics authority, published methods do not replace that identity.
