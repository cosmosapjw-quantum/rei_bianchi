# ENDPOINT14 원전 조사와 endpoint-zero 차수 확장 연결

조사일: 2026-10-28 (Asia/Seoul). 문헌 담당은 과학 계산, 후보 적합 판정, Wolfram 평가를 실행하지 않았다. 이번 검색과 원문 읽기는 다음 연구 단위의 근거 선택을 위한 것이다. 실제 scope/admission은 root 계약과 새 검증 결과가 결정한다.

## 재개 기준과 다음 문제

TANGENT13의 실제 결과 보고서, THEORY, source handoff를 읽었다. QUARTIC12의 RESEARCH_REPORT_KO.md, CONTRACT.md, INTERPRETATION_KO.md와 saved JSON의 이미 저장된 표시값을 읽었다. QUARTIC12에서 213/330 MeV free N16의 두 geometry 최소·최대와 258 MeV 최대는 이미 약 1e-14 폭으로 감싸져 있으며, TANGENT13이 남은 258 MeV 최소값 간격을 닫았다. 기존 최대값 캠페인을 다시 수행하는 것은 현 시점의 새 과학 의무가 아니다.

Root가 확정한 ENDPOINT14는 330 MeV, 같은 네 ERR-S 창과 endpoint-zero 조건을 유지하면서 even degree를 4에서 6으로 늘리는 조건부 비교다. 정의는

    z = mu^2,
    q(z) = (1-z) r(z),
    r(z) = a0 + a1 z + a2 z^2 >= 0 on [0,1].

기존 quartic endpoint-zero family는 r이 affine인 부분가족이다. 새 sextic family는 quadratic r을 허용한다. 실제 데이터 창에 들어가는 r의 구성적 증인을 찾으면 고정한 endpoint 조건에서 차수 제한이 feasibility에 미치는 영향을 분리한다. 새 family의 angular law를 실제 반응의 full multipole/polarization law로 채택하는 작업과는 구별한다.

## 실제 물리 원전 접근

### IAEA EXFOR M0475 — 현재 원자료 재사용

URL: https://nds.iaea.org/nrdc/exfor-master/entry/m/m0475.txt

이번 작업에서는 이미 보존된 공식 원문의 동일 파일 `work/BASS_HE/official_source/M0475.x4`를 실제 읽었다. 내용은 He-4(g,d)d, 즉 두 deuteron 채널이다. M0475002는 세 에너지의 12개 DCS와 통계오차, M0475003은 다른 에너지격자의 여섯 total cross sections를 담는다. 두 입자의 coincidence/TOF 검출과 liquid-He target은 기재되어 있다. 원문만으로 event/inclusive 적분 관례, 목표 medium의 전자·target-motion·response projection, 실제 photon history까지 확정하지 않는다. 물리적 상수·실험격자·ERR-S 창·full azimuth를 유지한다.

### Arends et al. (1976)

J. Arends et al., *Experimental investigation of the 4He(γ,d)d reaction*, Physics Letters B 62, 411–412. DOI https://doi.org/10.1016/0370-2693(76)90671-7

Publisher URL https://www.sciencedirect.com/science/article/abs/pii/0370269376906717 를 실제 fetch했다. 제목·저자·권호·쪽수·DOI와 접근 제한을 확인했으며 full text는 확보되지 않았다. CERN https://cds.cern.ch/record/790537 는 Hartmann의 같은 반응 thesis 제목·연도 metadata를 제공했지만 본문이나 normalization 식을 제공하지 않았다. 검색 공급자가 붙인 무관한 topic labels는 채택하지 않았다.

### Rice et al. (2000)

B. J. Rice et al., *Two-deuteron photodisintegration of 4He at Eγ=150–250 MeV*, Physical Review C 61, 064612. DOI https://doi.org/10.1103/PhysRevC.61.064612

Primary publisher abstract를 실제 읽었다: https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612 . 두 입자 coincidence, 여섯 각도와 150–190/190–250 MeV 두 energy bins, sin²θ 형태의 fit, allowed E2 s-/d-wave matrix elements에 의한 설명 가능성을 보고한다. 이 abstract는 같은 angular shape가 단일 multipole 해석을 고정하지 않는다는 비교 근거다. Full text가 접근 제한되어 정확한 multipole 식과 normalization을 이번 구현 입력으로 추출하지 않았다. 330 MeV의 새 측정값이나 endpoint-zero/degree6의 실험적 확정 근거로 사용하지 않는다.

### Silverman et al. (1984)

B. H. Silverman et al., *d+d→He4+γ cross section measurement at 376 MeV*, Physical Review C 29, 35. DOI https://doi.org/10.1103/PhysRevC.29.35

Primary abstract https://journals.aps.org/prc/abstract/10.1103/PhysRevC.29.35 를 실제 읽었다. Inverse reaction의 73°와 91° 측정 및 Arends와의 비교가 실려 있지만 full text는 제한되었다. 서로 다른 반응·격자·정규화의 값을 새 DCS 창으로 합치지 않았다.

## 수학 원전과 직접 적용

Jiawang Nie and James W. Demmel, *Shape Optimization of Transfer Functions*, author manuscript:
https://mathweb.ucsd.edu/~njw/PUBLICPAPERS/TrnShapOptCoef.pdf

이번에 저자 PDF 텍스트 §2 Theorem 2.2와 2.3을 실제 읽었다. 유한 구간의 비음수 다항식은 차수에 맞는 square와 endpoint factor를 사용하여 표현할 수 있고, 계수 cone 및 dual cone은 해당 semidefinite matrices로 표현된다. 여기서는 r이 quadratic이므로 r의 양 끝과 interval 내부 stationary minimum만 확인하는 직접 algebra가 가장 간단하다. q=(1-z)r의 interval positivity는 (1-z)>0인 [0,1)에서 나눈 뒤 r의 연속성을 사용하여 z=1까지 확장하면 동치다. 이 적용은 알려진 positivity 사실을 새 데이터 조건과 degree6 family에 구체화하는 것이다.

후보에 따라 새 μ6 aperture moment가 필요하다. 기존 geometry endpoint enclosure가 그대로라면 새 primitive ∫μ6 dμ=μ7/7을 그 저장된 경계에 평가하는 변경분만 계산할 수 있다. 이전 geometry/trigonometry campaign의 재실행은 이 문헌 조사로 요구되지 않는다.

### 저장된 moment에서 새 차수로 연결하는 geometry 의무

실제로 읽은 구현 경로는 다음과 같다.

- `continuation_exfor_20261028/src/exfor_aperture.py::geometries`: HEMISPHERES/CAPS는 full azimuth, A=[ν0,1], B=[−1,−ν0], ν0=0 또는 1/2다.
- `continuation_azimuth_20261028/src/azimuth.py::azimuth_pair_response`: coincidence는 Aplus∩Bminus와 Bplus∩Aminus의 합집합이며 두 입자는 같은 사건의 μ 및 −μ로 연결된다.
- `continuation_kinematic_20261028/src/kinematic.py::PhysicalAngularMap`: K<0인 경우 [-1,1]에서 단조증가 branch를 사용한다.
- `continuation_quartic_20261028/src/quartic_aperture.py::integrate_monomials,moments`: 각 inner/outer interval에 짝 monomial의 primitive를 정확히 적분한다.

330 MeV가 단조 topology임을 root의 새 계약/검증에서 확인한다고 하자. F^{-1}(ν0)=α, F^{-1}(−ν0)=β이면 coincidence set은 C=[−1,−t]∪[t,1], t=max(α,−β)≥0다. Full azimuth strips에서 같은 polar set을 사용하고 azimuth weights 합계가 1이므로, saved k0 lower/upper가 주는 threshold enclosure는

    t_hi = 1 − k0_lower/2,
    t_lo = 1 − k0_upper/2.

따라서 새 μ6 moment는 [2(1−t_hi^7)/7, 2(1−t_lo^7)/7]로 감쌀 수 있다. 이미 저장된 k1(μ²), k2(μ⁴)가 같은 threshold 식과 정확히 맞는지는 새 reader의 의미 있는 일관성 검사다. 이 보조정리와 단조 topology 확인 없이 일반 geometry의 k0만으로 고차 moment를 복원할 수는 없다. 이 문헌 작업에서는 위 식을 유도·전달했으며 수치 평가를 실행하지 않았다.

## 주장과 물리 상태의 경계

새 과학 결과의 핵심은 실제 전구간 양성 polynomial, nominal-angle window enclosure, endpoint-zero identity, 같은 detector union에 대한 새 witness aperture 값이다. 가능한 결과는 고정 degree4의 EMPTY와 degree6의 NONEMPTY가 양립함을 구체적 polynomial로 보이는 것이다. EXFOR11의 n8 endpoint-zero EMPTY는 충분조건인 global Bernstein coefficient cone에 대한 결과여서 이를 일반 degree8 positivity family의 공집합으로 바꾸지 않는다.

세 physical input 묶음은 이번 원전 접근에서 닫히지 않았다. root와 다른 survey가 새로운 실제 payload를 확인하면 그 입력을 우선한다. 본 조사는 문헌 전체의 부재 또는 novelty를 증명하지 않는다. 새 논문 수준의 일반 정리나 strong no-go 채택도 하지 않았다.

## 실제 검색 수와 교정 이력

- Exa search 6회, 요청 결과 수 합계 32. Exa fetch 2회, URL 요청 6개(그중 Nie/Demmel author PDF와 물리 publisher 원문/abstract 실제 읽기).
- SciSpace search 3회, 각 10개 결과. 검색 반환에는 관련 없는 다른 반응이 다수 포함되어 검색결과 수를 채택 근거 수로 세지 않는다.
- 첫 물리 Exa/SciSpace 질의가 proton-triton 채널로 잘못 구성되었다. 즉시 공식 M0475를 읽고 dd 채널로 교정했다. 최초 질의 raw를 보존했으며 이 잘못된 채널의 자료를 과학 입력으로 채택한 수는 0이다.
- 공개 게시에는 이 요약과 인용·접근 범위만 넣는다. 공급자가 반환한 긴 논문 텍스트와 원시 검색 JSON은 조사 원본으로 별도 보존한다.
