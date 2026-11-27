# BASS_HE 후속 루프: 문헌 원전 조사 및 구성 후보

조사일: 2026-10-28 (Asia/Seoul). 담당 범위: R2 근거·재사용, R4 후속 구성 후보. 규약: 사용자 제공 physmath-research-loop 1.0.0. 이번 파일은 이론·문헌 근거이며 EXFOR11 재검증 또는 새 science 실행 기록이 아니다.

## 1. 즉시 쓸 수 있는 원전 식별

| ID | 원전 | 실제 접근 범위 | 이번 작업에서의 역할 |
|---|---|---|---|
| L1 | IAEA EXFOR M0475, https://nds.iaea.org/nrdc/exfor-master/entry/m/m0475.txt | entry 전체 텍스트, Exa fetch | reaction, experiment, tables, error labels |
| L2 | IAEA EXFOR JSON, https://nds.iaea.org/dataexplorer/api/exfor/entry/M0475 | entry JSON 전체, Exa fetch | L1의 구조화 확인 및 field 의미 |
| L3 | J. Arends et al., Experimental investigation of the 4He(γ,d)d reaction, Phys. Lett. B 62(4), 411–412 (21 June 1976), DOI https://doi.org/10.1016/0370-2693(76)90671-7 | publisher landing metadata만. 본문은 subscription 경계 | M0475의 원논문 identity; 동일입자 normalization은 본문 의무로 유지 |
| L4 | B. J. Rice et al., Two-deuteron photodisintegration of 4He at Eγ=150–250 MeV, Phys. Rev. C 61,064612 (18 May 2000), https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612 | APS 원전 abstract. 본문은 authorization required | 같은 반응의 multipole 해석 비유일성 |
| L5 | N. Otuka ed., LEXFOR, IAEA-NDS-208 Rev.2025/05, https://nds.iaea.org/nrdc/nrdc_doc/iaea-nds-0208-202505.pdf | Exa search excerpts 및 fetch 앞 32000자. 전체 PDF 독해는 미수행 | EXFOR quantity/CM heading 정의의 위치 확인 |
| L6 | O. Koshchii, P. E. Kuznietsov, Yu. A. Kasatkin, arXiv:1212.5419 (21 December 2012), https://arxiv.org/abs/1212.5419 | 원전 abstract, ar5iv 본문 검색 추출 | covariant amplitude 구성의 대안 참고. 본 과제 데이터의 실제 law로 채택하지 않음 |
| L7 | H. Hartmann, Experimentelle Untersuchung der Reaktion 4He(γ,d)d (1976), https://cds.cern.ch/record/790537 | CERN 서지 record metadata | 1976 실험 상세원전 추가 취득 후보. 본문 취득되지 않음 |

L1/L2가 명시하는 사실: 반응은 γ+4He→d+d. Bonn synchrotron, reaction-particle-tagged bremsstrahlung, cylindrical liquid-helium cell을 사용한다. 두 deuteron을 두 TOF scintillator arm으로 coincidence 측정하며 각 arm에서 질량·에너지·각을 측정해 kinematic overdetermination으로 background를 억제했다. M0475002는 Table1의 CM DCS12점, 단위 nb/sr, 에너지213/258/330 MeV, 각46/61/73/87도다. M0475003은 Table2의 total6점, 에너지201/225/253/285/320/359 MeV와 단위nb다. ERR-S는 statistical error label이다. 이것은 이미 완료된 EXFOR11 input identity와의 원전 연결이며 수치를 재계산하지 않았다.

L1/L2에는 event-normalized symmetric sphere lift인지, inclusive one-deuteron DCS인지 정하는 명시적 1/2 규약, detector efficiency/joint response 함수, liquid target momentum/spectral distribution이 없다. COINC 측정이라는 사실만으로 published DCS의 전역 counting convention을 정하지 않는다. 서로 다른 에너지격자의 DCS와 total을 비교해 κ=1 또는2를 결정하는 절차는 추가 interpolation/model을 필요로 한다.

L3 primary publisher 저자는 T.Hegerath로 표기한다. 일부 Exa DOI enrichment에는 A.Hegerath로 나타나므로 해당 자동 enrichment를 authoritative author spelling으로 대체하지 않는다.

L4 abstract는 두 energy bins(150–190,190–250 MeV)와6각 coincidence absolute cross sections를 보고한다. sin²θ distribution에 대해 strictly allowed E2 s/d-wave TMEs로도 설명할 수 있다고 한다. 따라서 이 abstract만으로 한 multipole 또는 polarization law를 현재213/258/330 MeV 데이터에 고정할 수 없다. 이 관찰은 모델 선택의 입력이며 새 no-go가 아니다.

## 2. 실제 검색 범위

Exa semantic search7회, requested results 합43: M0475 식별8, exact entry5, 원논문5, identical-particle convention8, EXFOR manual6, Rice full-text6, Bonn thesis5. Exa fetch4회10 URL 요청(중복 포함): servlet2, entry/master/API3, publisher/APS/CERN3, arXiv/manual2. servlet 두 URL은403, historical x4 mirror는 timeout, 나머지7 URL은 텍스트 반환. SciSpace 검색3회, 각각10 results. 관련 반응을 정확히 지정해도 인접한 deuteron breakup/다른 helium reactions가 주로 반환되어 SciSpace 결과는 scientific authority로 채택하지 않았다. 이는 검색 recall의 범위 제한이다.

전문 확보 시도는 접근 가능한 author/institutional record와 publisher 페이지로 제한했다. 구독 경계의 우회는 하지 않았다. 이번 자료로 원논문 전체 내용까지 확인했다고 주장하지 않는다. EXFOR 전체 corpus/관련 문헌 전체의 exhaustive review도 아니다. 사용자가 요구한 repo/branch/backups 조사는 다른 병렬 작업의 coverage와 합쳐야 한다.

## 3. 구성 후보: event → inclusive → detector response

다음은 L1의 실험구조를 수학적으로 연결하기 위한 직접 유도이다. 표기 자체가 새 과학 성과라는 주장은 없다.

### 3.1 동일입자의 event space

고정 CM energy에서 두 equal-mass deuteron 방향은 u와−u다. 물리 event의 방향공간은 Q=S²/{u∼−u}. Q의 확률측도ν를 sphere의 symmetric lift μ로 옮긴다: μ(S²)=1, μ(A)=μ(−A). 하나의 event orientation을 u로 표시하더라도 두 physical tracks는 p₊(u), p₋(u)=p₊(−u)다.

임의의 one-track observable g에 대해
E[N_g]=∫[g(p₊(u))+g(p₋(u))]dμ(u)=2∫g(p₊(u))dμ(u).
따라서 inclusive track measure의 total은2이고 event measure의 total은1이다. event cross section σ_e를 곱하면 total inclusive track cross section은2σ_e다.

관측된 even DCS를 f(u)=κσ_e w(u), ∫w dΩ=1, κ∈{1,2}로 연결할 수 있다. κ=1은 symmetric event lift, κ=2는 inclusive track convention이다. 정규화된 aperture ratio ∫_A f/∫f는 κ에 무관하다. 이것으로 기존 normalized aperture reference를 유지하면서 absolute event normalization 의무를 분리할 수 있다.

### 3.2 검출 observable

일반 aperture χ_A에 대해
N_A=χ_A(p₊)+χ_A(p₋),
U_A=1−[1−χ_A(p₊)][1−χ_A(p₋)],
C_A=χ_A(p₊)χ_A(p₋).
이는 각각 track count, event at-least-one, event two-track coincidence다. 서로 다른 observable이며 저장 형식에서 명시적 enum으로 구분해야 한다. 일반 forward CM hemisphere는 각 event에 track1개를 포함하므로 E[N_A]/2=1/2이고 E[U_A]=1이다. 이 예는 기존 EXFOR11의 HEMISPHERES라는 이름을 재해석하는 사례가 아니다; 기존 aperture definition은 그 원본대로 유지한다.

실제 detector는 joint conditional response R(y|p₊,p₋,target,beam)를 가진다. 독립 detector 가정과 disjoint arm assignment가 검증되었을 때만 arm efficiency product를 쓸 수 있다. 일반 함수 R를 입력받는 positive pushforward가 더 직접적인 코드 계약이다. 0≤R≤1이면 event acceptance도[0,1]에 있고, R=1이면 event normalization이 보존된다.

### 3.3 Moving-target 조건부 이식

signature(-,+,+,+), four-momentum P=(Eα/c,pα), k=(Eγ/c,(Eγ/c)n), Q=P+k를 사용한다.
Eα=√(Mα²c⁴+c²|pα|²),
Eγ*=Eγ(Eα−c pα·n)/(Mα c²)=γαEγ(1−βα·n),
W²=−c²Q·Q=Mα²c⁴+2Mαc²Eγ*.
두 deuteron의 CM energy는W/2, momentum magnitude는q*=√(W²/4−m_d²c⁴)/c다. Q의 boost로 두 four-momenta를 lab에 옮긴 후 R에 전달한다. invariant threshold는W≥2m_dc²다.

주어진 normalized target distribution F(pα)와 photon density nγ(Eγ,n)에 대한 encounter integrand는
F(pα)nγ(Eγ,n)c(1−βα·n)σ_e(W)×∫R dμ_W.
여기서 flux factor와 energy projection이 각각 명시되어야 한다. 실제 F, nγ, μ_W, σ_e(W), R는 독립 입력이다. 특히 moving-target convolution은 고정213/258/330 MeV에서 벗어난 Eγ*를 요구하므로 데이터의 보간 또는 물리 law가 없는 상태에서 수치값을 발명하지 않는다.

### 3.4 후보 coding contract

- input: event/inclusive convention enum(unknown 허용), two-body masses/units, explicit angular law identity, target momentum, incoming photon momentum, joint response callback.
- output: ordered pair moments plus symmetric event observable; event acceptance and inclusive count separate; normalization coefficient/provenance retained.
- independent checks: four-momentum sum, daughter on-shell, exchange invariance, stationary target limit, full-response normalization, asymmetric aperture distinction, unknown convention propagation.
- stationary target and a named synthetic response can be exact reference checks. Synthetic F 또는 response는 실제 liquid-He reconstruction으로 표시하지 않는다.
- open physical input은 그대로 유지: experimental κ, actual medium/response, full angular+polarization law, incident flux/history, named birth/deposition/thermalization, global binding.
- population_rest_energy_witness sole owner를 바꾸거나 Gamma_thermal/Cv/thermal_deposition null을 채울 근거를 제공하지 않는다.

## 4. NG·watchdog 판정

새 strong no-go를 제안하지 않는다. NG1–NG7을 만족하는 새 배제정리라는 표현도 사용하지 않는다. 관측된 빈 finite cone 또는 문헌 접근 한계를 global impossibility로 해석하지 않는다.

watchdog: 동일입자 표기 → event와 track count를 혼동하면 rate가2배 달라질 수 있음 → explicit measure와 observable enum을 구현하는 최소 교정. Moving-target 표기 → fixed-energy input 밖의 law가 필요함 → required input identity와 미지 값을 보존. 두 항목은 실제 식·코드 연결을 제공하며, 실험값을 확보했다는 주장은 하지 않는다.

## 5. 기록 파일

같은 폴더의 exa_*.json, scispace_*.json, orig_fetch_0.json이 실제 tool response다. 결과의 scientific claim은 위에서 명시한 primary source 접근 범위와 직접 유도에 한정된다.

