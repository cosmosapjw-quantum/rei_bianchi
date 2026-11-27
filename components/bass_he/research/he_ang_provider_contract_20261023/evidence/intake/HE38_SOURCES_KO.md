# HE38 후속 H1 유한질량 단원: 원전 및 모형 자격 심사

작성 범위는 source qualification이다. workflow1.0.0 / approval0.2를 유지한다. HE37 자료와 실행 근거를 재사용했으며, 이 작업에서 과학 모델·테스트·IVP·benchmark·과학 그림을 실행하지 않았다. 기존 CCC ZIP을 다시 다운로드하거나 원격 게시물을 수정하지 않았다.

## 판정

**\`admitted_explicit_physical_approximation\`: Le–Cambier 원래 Jacobi 좌표의 유한질량 운동학 + Eq85 상대에너지 단면적 + 명시적 균일 angular density.**

정확한 유한질량 보존식은 원전에 이미 있다. 다음 단원은 해당 운동학을 사용하여 HE37에서 생략했던 질량비 항과 종별 momentum/energy/STF를 유도할 수 있다. 원전이 제공하는 각도 모형은 경험적으로 교정된 실제 H1 각분포라는 자격을 갖지 않는다. 이번에 발견한 실제 DDCS 자료는 후속 검증 후보로 남긴다.

## 1. 기준 원전과 재사용 범위

Le, H. P. & Cambier, J.-L. (2016), *Modeling of Inelastic Collisions in a Multifluid Plasma: Ionization and Recombination*, Physics of Plasmas **23**, 063505, DOI [10.1063/1.4953050](https://doi.org/10.1063/1.4953050); [arXiv 1605.06545](https://arxiv.org/pdf/1605.06545).

이미 저장된 PDF와 텍스트를 다시 읽었다. 아래 page는 **PDF에 인쇄된 페이지 번호**이며, zero-based PDF index는 1을 뺀 값이다.

| 새로 확인한 부분 | 원전 위치 | 단원에서의 역할 |
|---|---|---|
| 질량가산 및 사건 보존식 | §II, Eq2, p4 | 유한질량 모형의 질량·momentum·energy 정의 |
| 초기/최종 Jacobi 좌표, 역변환 | §II, Eq3–4, p5 | 출력 입자 속도 구성 |
| 상대에너지와 공유 변수 | §II, Eq6–7, p5 | 상대에너지 E 및 Υ의 소유자 |
| 3차 미분 단면적, angular measure | §III.A, Eq11–12, p7 | 각도가 g1, g2의 방향임을 확인 |
| 질량비 근사와 isotropy | §III.E, p15 | heavy approximation과 angular assumption의 구별 |
| 바닥상태 H 반고전 단면적 | §VI.A, Eq85, p25 | 기존 HE37 law의 재사용 |
| 에너지 source 부호 | Eq39–41 p12; Eq42–48 pp13–14 | Eq48 국소 부호 불일치 후보 검토 |

재사용 PDF SHA256:
\`5ee591cde0cb90c03b5fc47a8ad439bae93bcc36bd05a4cbb4e1943fec93fc68\`

재사용 텍스트 SHA256:
\`34f495db1eefa34bdf1104117f8546b2a539ccc2b3f4ba303365d2c673cc18e5\`

원본 위치는 private manifest에 기록한다. 논문 PDF/전문을 공개 연구 산출물에 복제하지 않는다.

## 2. source에 맞는 정확한 운동학

이 절의 식은 원전 Eq2–7을 전자 충돌에 맞추어 다시 쓴 것이다. 전자 질량을 m, 양성자 질량을 p, 중성종의 **운동학적 질량**을 h=p+m, 사건 전체 질량을 M=p+2m으로 둔다.

\[
\mu=\frac{mh}{M},\qquad \mu_t=\frac{mp}{h},
\qquad
V=\frac{m v_{s0}+h v_{H0}}{M},\qquad
g_0=v_{s0}-v_{H0}.
\]

원전의 최종 Jacobi 좌표는 다음과 같다.

\[
g_1=v_{s1}-\frac{m v_{e2}+p v_{p2}}{h},
\qquad
g_2=v_{e2}-v_{p2}.
\]

따라서 출력 속도는

\[
v_{s1}=V+\frac hM g_1,\quad
v_{e2}=V-\frac mM g_1+\frac ph g_2,\quad
v_{p2}=V-\frac mM g_1-\frac mh g_2.
\]

여기서 s는 원전의 scattered-electron bookkeeping label이고 e는 ejected-electron label이다. 실제 전자 관측량은 두 전자를 합산한다. 선택적으로 labels를 교환하여 대칭화해도 사건 수를 2배로 바꾸지 않는다.

\[
E=\frac{\mu g_0^2}{2}
 =\frac{\mu g_1^2}{2}+\frac{\mu_tg_2^2}{2}+I,
\qquad
\Upsilon=E-\frac{\mu g_1^2}{2},
\qquad I\leq \Upsilon\leq E.
\]

**유한질량에서는 Υ−I가 ejected-electron–ion의 상대운동 에너지다.** lab에서 측정한 ejected-electron kinetic energy와 같다고 둘 수 없다. 같은 이유로 E−Υ는 scattered electron과 나머지 두 입자 COM 사이의 상대운동 에너지다.

h=p+m은 원전의 Newtonian mass-additivity convention이다. 실제 neutral rest mass의 binding-energy defect까지 정밀하게 반영한 값이라는 뜻이 아니다. ionization energy I는 별도 internal-energy owner로 한 번만 계산한다.

## 3. 채택하는 joint kernel

원전 Eq85에서 바닥상태 n=1에 대해 I=I_H=13.6 eV를 선택한다. source의 E는 Eq7 상대에너지다.

\[
\frac{d\sigma}{d\Upsilon}
 =\frac{4\pi a_0^2 I^2}{E\Upsilon^2},\qquad
\sigma(E)=4\pi a_0^2\frac{I(E-I)}{E^2},
\qquad E>I.
\]

\[
p(\Upsilon\mid E)=
\frac{IE}{(E-I)\Upsilon^2},\qquad
G(\Omega_1,\Omega_2)=\frac1{16\pi^2}.
\]

E≤I에서는 사건 단면적을 0으로 둔다. 마지막 G는 §III.E의 명시적 angular assumption을 **질량비를 근사하기 전 원래 좌표에 적용하는 채택 모형**이다. g1, g2의 방향은 이 joint density에서 서로 독립이고 균일하다. 출력 lab-electron directions를 서로 독립인 등방 분포로 두는 규칙이 아니다.

전자의 pair-relative coordinate 및 electron-pair–ion coordinate로 변환하는 것은 운동학상 가능하지만, 그 새 좌표에서 다시 uniform G와 같은 Υ law를 부여하면 다른 모형이 된다. 이번 source 일치는 원래 g1, g2 좌표를 유지한다.

현대 a0의 사용은 HE36/HE37에서 이미 문서화한 상수 refinement를 재사용한다. CCC total에 이 source의 energy partition을 곱하는 혼합 normalization은 채택하지 않는다. 이 논문은 density/momentum/energy의 multifluid source를 다루므로 새 Grad/STF 교환행렬을 이미 발표된 결과로 표시하지 않는다.

### 구현에 전달할 직접 유도 관계

다음 식은 위에서 채택한 kernel의 정규화 적분이며, 외부 angular calibration을 추가로 제공하지 않는다.

\[
\overline{\Upsilon}(E)
=\frac{IE}{E-I}\log(E/I).
\]

같은 온도와 bulk에서 원전 Table I의 COM/relative Maxwellian coupling coefficient γ는 0이 된다. 따라서 V와 g0의 Gaussian factorization을 정확히 사용할 수 있다. 원전은 Boltzmann constant를 생략하므로 SI 구현에서는 \(\theta=k_B T\)를 명시해야 한다. 서로 다른 온도 또는 상대 bulk drift까지의 확장은 별도 가정/유도가 필요하다.

## 4. 새 질량 상수

공식 [NIST SP959, CODATA2022 wallet table](https://physics.nist.gov/cuu/pdf/wallet_2022.pdf), May2024, 둘째 페이지를 직접 확인했다.

| 상수 | 구현에 고정할 값 | 표준불확도 | 처리 |
|---|---:|---:|---|
| mp | 1.67262192595×10⁻²⁷ kg | 5.2×10⁻³⁷ kg | 이번 유한질량 모형의 새 상수 |
| me | 9.1093837139×10⁻³¹ kg | 2.8×10⁻⁴⁰ kg | HE37 값 유지 |
| a0 | 5.29177210544×10⁻¹¹ m | 8.2×10⁻²¹ m | 기존 refinement 유지 |
| kB | 1.380649×10⁻²³ J K⁻¹ | SI 정의상 정확 | θ=kBT |
| 1 eV | 1.602176634×10⁻¹⁹ J | SI 정의상 정확 | energy conversion |

모형 내부에서 mass ratio는 고정한 mp,me로 계산하면 된다. CODATA의 별도 ratio 숫자를 함께 섞어 roundoff상의 다른 질량을 만들 필요가 없다. 표의 불확도를 모델 결과에 전파했다고 주장하지 않는다. I=13.6 eV는 source convention이며 정밀 분광 threshold로 교체하지 않았다.

## 5. Eq48의 국소 부호 불일치 후보

재사용 arXiv PDF p14 Eq48에는 kinetic-energy source 합을 \(+\Gamma I\)로 적은 항이 있다. 반면 p4 Eq2c는 incoming kinetic energy = outgoing kinetic energy +I이므로 outgoing-minus-incoming 합은 \(-I\)다.

또한 p12 Eq39는 incoming-minus-outgoing scattered-electron energy 앞에 음수를 둔다. Eq40–41은 scattered-electron energy change를 제공한다. p13 Eq43에는 target loss가 있고 p14 Eq47에는 product gains가 있다. 이 정의들을 유지하면 \(-\Gamma I\)가 사건 보존식과 일치한다.

현재 판정은 **해당 버전 Eq48의 국소 부호 불일치 후보**다. 다른 버전·정오표를 조사하여 논문 전체를 수정했다고 주장하지 않는다. 새 구현은 Eq48의 표시 부호를 복사하지 않고 Eq2c의 사건 보존식과 독립적인 종별 합으로 검증해야 한다. Root의 PDF 육안 확인과 독립 유도 검토를 요청했다.

## 6. 물리적 H1 angular provider 후보의 새 조사

SciSpace 검색과 Exa 검색 후 publisher/institutional primary records를 대조했다. 직접 link.aps.org 읽기 일부는 unavailable/403였지만 표준 APS abstract URL은 Exa fetch로 읽었다. 제한된 전문을 읽었다고 주장하지 않는다.

| 후보 | 실제 확인한 범위 | admission 결과 |
|---|---|---|
| Isaacs et al.2001, [DOI10.1103/PhysRevA.63.030704](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.63.030704) | APS abstract: ECS DDCS, incident17.6,25,30eV | 후속 numeric-table 후보; 이번 provider 미채택 |
| Colgan & Pindzola2006, [DOI10.1103/PhysRevA.74.012713](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.74.012713) | APS abstract/captions: TDCC DDCS/TDCS,15.6,17.6eV, 선택된 energy-sharing/angles | 후속 source 후보; 완전 domain/table 미채택 |
| Bray et al.2014, [DOI10.1103/PhysRevA.90.022710](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.90.022710) | APS abstract: 충분히 조밀한 pseudostate energies에서 ionization amplitude interpolation | 알고리즘 후보; 실행 가능한 calibrated amplitude dataset 미채택 |
| Childers et al.2003, [DOI10.1103/PhysRevA.68.030702](https://doi.org/10.1103/PhysRevA.68.030702), [기관 공개 원문](https://researchportal.murdoch.edu.au/view/pdfCoverPage?download=true&filePid=13136894710007891&instCode=61MUN_INST) | published version4쪽: 연구범위14.6–40eV, 이 논문의 제시값15.6,17.6,25,40eV; reportedangles10°–120°; H(n=2) excitation을 사용한 절대 normalization | 실제 differential 검증에 유용; full-angle inclusive energy-weighted P2 provider를 바로 구성할 수 없음 |

마지막 후보의 Eq1은 검출 전자 에너지/각도에 따른 DDCS normalization을 설명하고 Figures2–5는 선택된 값들을 제시한다. 이것이 full-angle/full-energy numerical table의 제공과 동일하지는 않다. 누락된 각도, exchange/inclusive normalization, energy sharing, incident-energy interpolation 및 불확실도 소유자를 닫기 전에는 calibrated \(D(E)\)를 등록하지 않는다.

**검색 결론은 현재 bounded intake에서 domain-complete numerical provider를 admission하지 못했다는 것이다.** 완전한 데이터가 어디에도 없다는 no-go가 아니다. 이후 표/소스코드를 확보하면 해당 실제 domain에서 다시 심사할 수 있다.

## 7. 완료와 남은 범위

이번 단원의 source route는 원전 g1,g2의 유한질량 kinematics와 그 좌표에 대한 명시적 isotropic model이다. 다음 coding loop는 이 조건에서 target motion, recoil, 종별 number/momentum/energy/STF를 구현할 수 있다.

아직 열린 것은 실제 H1 energy-weighted angular calibration, 다른 온도/상대 bulk/유한 비등방 분포의 validity, electron stress와 total baryon stress의 closure, 추가 atomic/nuclear processes, 그리고 coupled thermal/UV/population/metric IVP다. 정확한 질량 보존 구현은 이 나머지 범위의 완료를 뜻하지 않는다.

### 실행/재사용 기록

- 새로 실행한 과학 IVP, science diagnostic, 테스트, benchmark, science render: 모두 0.
- source 파일 읽기, SHA256 확인, 검색/primary-document qualification만 수행.
- 기존 Le–Cambier PDF/텍스트 및 기존 CCC archive evidence 재사용.
- 새 full-repository/full-conversation 조사 수행 또는 완료를 주장하지 않음.
- 상세 machine-readable 조건은 \`SOURCE_QUALIFICATION.json\`에 저장.

