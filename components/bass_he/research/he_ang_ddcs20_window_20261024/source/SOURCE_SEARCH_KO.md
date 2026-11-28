# HE-ANG 다음 입력: 공개 differential 자료 조사

조사일: 2026-10-24 Asia/Seoul. 역할: 별도 원전 조사. 새 과학 수치 실행, solver build, catalogue 재실행, 게시, 업로드는 0회다.

## 선택할 수 있는 실제 원자료

J. G. Childers, K. E. James Jr., I. Bray, M. Baertschy, M. A. Khakoo, **Low-energy electron scattering from atomic hydrogen. I. Ionization**, Physical Review A **69**, 022709 (2004), DOI [10.1103/PhysRevA.69.022709](https://doi.org/10.1103/PhysRevA.69.022709).

- 저자기관 공개본: https://researchportal.murdoch.edu.au/view/pdfCoverPage?download=true&filePid=13137015150007891&instCode=61MUN_INST
- 실제 PDF: `Childers2004_readonly.pdf`, 306700 bytes, SHA256 `efcb2f849162b31425f2e609c6d563171b6bba1068b8eefd4dc1465f54213941`.
- PDF 11쪽에는 기관 cover가 포함된다. 인쇄 쪽번호 022709-4와 022709-5는 PDF page 5와 6이다.
- `pdftotext -layout` exit 0. 두 쪽을 PNG로 렌더링해 실제로 읽었다. Fontconfig cache 경고가 있었으나 두 렌더링은 exit 0이고 표의 숫자가 보인다.
- PDF와 원문 추출 전체 및 원문 스크린샷은 읽기 자료다. 공개 Git 재배포에는 넣지 않는다. 공개 산출물에는 서지정보·해시·재현 가능한 수치 사실과 자체 유도를 사용한다.

이 논문은 H(1s)의 electron-impact ionization에 대한 **절대 doubly differential cross section**을 실제 숫자 표로 제공한다. 관측량은 한 검출 전자의 잔여 운동에너지 E1과 입사 방향에 대한 각도 θ에 대한 D(E0,E1,θ)=d²σ/(dΩ dE1)다. 상대 전자의 각도는 적분돼 있어 joint angular/event 상관은 이 자료만으로 정해지지 않는다.

| Table | E0 [eV] | E1 [eV] | 각도 행·지원 | 수치 DDCS 셀 수 |
|---|---:|---|---|---:|
| I | 14.6 | 0.9 | 11개 관측행; 20–127°; 60°,90° 중복 측정 | 11 |
| II | 15.6 | 1.0,1.2,1.4,1.6,1.8 | 8행, 15–120° | 40 |
| III | 17.6 | 2.0,2.75,3.25,3.75 | 11행, 12.5–125° | 44 |
| IV | 20 | 2,3,4,5,6 | 8행, 15–120° | 40 |
| V | 25 | 3,4,5,6,7,8,9,10,11 | 11행, 12–110° | 99 |
| VI | 40 | 2,3,5,7,10,13,15,17,20,23,26 | 본측정 7행 10–110°; 추가 측정 10°,15°는 처음 5개 E1만 | 87 |

따라서 원문 표에서 손으로 센 예상 합계는 321개 숫자셀이다. 이 수는 후속 실제 전사/파서에서 독립 확인해야 한다. 모든 표의 native 단위는 10^-19 cm²/(sr eV)다. abstract의 12–127° 요약과 달리 Table VI에는 10° 데이터가 실제 존재한다. 지원 범위는 표별로 관리한다.

Table III에서 시각적으로 읽은 예:

- θ=12.5°: E1=(2.0,2.75,3.25,3.75)eV에 D=(18.2,27.7,34.6,41.8), quoted uncertainty 17.0%.
- θ=90°: D=(2.10,2.29,2.39,2.57), quoted uncertainty 18.4%.
- θ=125°: D=(4.24,4.34,4.47,4.70), quoted uncertainty 16.4%.

## 원전 정규화와 오차의 실제 의미

Eq.(1)의 계산식은 다음이다.

\[
D(E_0,E_1,\theta)=\frac{N_{\rm cont}(E_1)}{N_{n=2}\,\Delta E}
\frac{d\sigma_{{\rm exc},n=2}(E_0,\theta)}{d\Omega}
\frac{\overline T(E_1(n=2))}{T(E_1({\rm cont}))}.
\]

ΔE≈0.04 eV/channel이다. H n=2 excitation DCS의 CCC 값을 절대 스케일 표준으로 사용했다. 논문은 그 표준의 정확도를 sub-10%라고 설명하지만 **표의 error bars에는 CCC 기준 DCS 오차를 포함하지 않았다고 명시**한다. 표의 one-standard-deviation 값에는 통계, background subtraction, analyzer transmission, continuum polynomial fitting 오차가 포함된다.

Continuum은 energy loss의 4차 이하 polynomial로 fitting했다. 따라서 같은 θ에서 서로 다른 E1의 셀을 독립 관측으로 가정할 근거가 없다. 전체 covariance가 제공되지 않았다. CCC 보정 DCS 자체가 θ에 의존하므로 모든 정규화 오차가 단일 공통 스케일로 상쇄된다고도 가정하지 않는다.

Table IV의 E1=2 eV, Table V의 E1=3 eV에는 overall uncertainty가 다른 에너지보다 약 5% larger라는 footnote가 있다. ratio인지 percentage point인지 원전 문구만으로 결정하지 않는다. Table I의 별표는 장비 수정 후 측정, Table VI의 별표는 후속 검증 측정이다. 별표 행을 조용히 평균하거나 본측정을 덮어쓰지 않는다.

이 실험 자료는 실제 H를 측정한 것이며 finite-nucleus 이론 coefficient를 제공하는 것은 아니다. 입사/검출 laboratory convention 및 실험 support를 유지한다. fixed-nucleus 모델을 비교하려면 recoil·threshold·frame 근사 의무를 별도 관리한다.

## 이번 공개 조사에서 다른 후보의 상태

1. **CCC 공식 DB:** https://atom.curtin.edu.au/CCC-WWW/ . H I n_i≤9 전체 state cross sections가 August/2026 자료로 설명된다. 링크된 e-H_XSEC_LS.zip은 HEAD 응답에서 7010887B, Last-Modified 2026-10-12였다. archive 자체는 다운로드하지 않았다. 기존 CCC total과 다른 각분포 source로 채택하지 않는다.
2. 공식 H I electron-impact 디렉터리 https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/ 를 목록 끝까지 읽었다. 1133792B SHA256 `038e67e5bad5417b13dd47617103f09c4de5cccaa6ed012704db8d5ab8f64b33`, HTML 끝 확인, href 5286개. 링크 이름 중 dcs/ddcs/tdcs/amp/ion 패턴으로 식별되는 파일은 없었다. 이것은 이름 기반 조사 범위이며 하위 디렉터리나 모든 source의 부재를 뜻하지 않는다. e-H/, orig_data/, prev/, n10/ 하위 목록은 이번에 읽지 않았다.
3. **Bray 1999 원문:** https://arxiv.org/html/physics/9906008v3 . equal-energy sharing에서 CCC spin amplitude의 coherent/exchange combination과 finite-basis normalization을 다룬다. Eq.(27) partial amplitude 및 Eq.(26) 양측의 관계가 있다. 이번 검색에서 즉시 사용 가능한 raw joint amplitude 파일 링크는 확인하지 못했다. Figures만을 숫자 payload로 취급하지 않았다.
4. **Bray et al. 2014:** https://doi.org/10.1103/PhysRevA.90.022710 . 저자·abstract·출판일을 공식 APS에서 확인. dense pseudostate amplitude interpolation이 주제다. 본문은 subscription wall이며 이번에 원문/수치 supplement를 읽었다고 주장하지 않는다.
5. proton-impact H, molecular H2, laser-assisted H, excited H(2s/3s) 자료는 목표인 field-free e+H(1s) 채널과 달라 채택하지 않았다.

## 도구와 검색 범위

SciSpace `search_papers`를 full natural-language question으로 1회 수행하여 10개 후보를 받았다. 제목/abstract로 선별 후 CCC 공식 사이트, arXiv 저자 원고, APS 원전, Murdoch 저자기관 공개본을 직접 확인했다. 웹 검색은 CCC/TDCS/DDCS/ECS/raw/supplement 범위의 두 검색 엔진을 사용했다. 검색·접근 실패와 실제 다운로드를 구분했다. 기본 shell network 요청은 EPERM이었으며, read-only escalation 후 공식 목록과 공개 논문은 성공했다. APS 2004 DOI 직접 fetch는403, 기관 stable URL을 통한 PDF 읽기는 성공했다. signed redirect URL은 산출물에 기록하지 않는다.

## 다음 구성 후보

우선순위가 높은 실행 가능한 단위는 **측정된 DDCS 표의 admission과 측정 각영역의 제한된 모멘트 계산**이다. 예를 들어 E0=17.6eV의 Table III는 같은 11개 각도에서 4개의 E1을 제공하고 별표·저에너지 추가오차 footnote가 없어 첫 입력으로 단순하다. 전 표 321개 값을 보존하되 처음 수치 판별은 이 단위에서 고정할 수 있다.

빔 축의 방위각 대칭을 명시하고 μ=cosθ에 대한 비음수 piecewise-linear 보간을 새 근사로 고정하면 측정 영역의 함수형

\[
M_\ell(E_0,E_1;\mu_a,\mu_b)=2\pi\int_{\mu_a}^{\mu_b}P_\ell(\mu)D(E_0,E_1,\mu)\,d\mu
\]

을 다항 적분으로 계산할 수 있다. 보간·영역·통계 covariance 미지·미측정 영역은 각기 별도 의무다. 측정 1σ를 결정론적 신뢰구간으로 바꾸지 않고 sensitivity envelope로 표현할 수 있다. 이 함수형에서 전체 angular distribution, event correlation, recoil moments를 추론하지 않는다. 이것은 새 실제 입력을 활용하는 제안이며, root의 R1–R5 계약 및 독립 유도 후 구현해야 한다.
