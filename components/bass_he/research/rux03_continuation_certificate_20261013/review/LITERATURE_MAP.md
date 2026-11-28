# THEORY06 — 독립 문헌 지도와 적용 조건

검토자: /root/dropbox_checkpoint. 기록: 2026-10-12 23:47:21 UTC.  
상태: **문헌 검토 완료; 후보 증명·실행의 최종 R6 판정은 대기 중.**

이번에 확인한 표준 도구는 **성분별 weighted contraction, parameter 구간 전체의 radii bound, Krawczyk 포함 인증**이다. THEORY06의 새 성과는 이 일반 원리를 다시 진술하는 데 있지 않다. 고정된 full H/He source와 물리적 box에서 실제 rate·Jacobian 상계를 얻고 양의 \(h\) 구간을 인증하는 연결이 현재 후보의 심사 대상이다. [고정 계약](../dossier/SCIENTIFIC_CONTRACT.md)의 초기 읽기 identity는 SHA256 **85b53f4c460fcb168a1b37f0f37775cf6496e615c20707d2cbef3f94a1a1ee24**, 4,290 B다.

## 1. 실제 읽은 원전

| 원전 | 직접 읽은 위치 | 현재 작업과의 관계 |
|---|---|---|
| [van den Berg–Lessard–Mischaikow, 2010](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf), *Global smooth solution curves using rigorous branch following*, Math. Comp. 79, 1565–1584; DOI 10.1090/S0025-5718-10-02325-2 | 저자 manuscript의 pp.5–10, 식 (13)–(20), Lemma 5·7, Definition 6, Proposition 8 및 연결 증명; fold에 대한 §1.2/§3 도입 | predictor tube 전체의 residual·derivative bound가 연속 parameter branch를 인증한다. 인접 조각은 동일 root를 포함한다는 연결 근거가 필요하다. |
| [Day–Lessard–Mischaikow, 2007](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf), *Validated continuation for equilibria of PDEs*, SIAM J. Numer. Anal. 45, 1398–1424; DOI 10.1137/050645968 | 저자 manuscript pp.3–6, 식 (2.1)–(2.6), Theorem 2.1와 증명 | 서로 다른 component 폭을 fixed weighted sup norm으로 정규화한다. 중심 defect와 box 전체 Lipschitz 상계가 self-map·contraction을 보장한다. |
| [Rump, 1995](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf), *Verified solution of large systems and global optimization problems*, J. Comput. Appl. Math. 60, 201–218; DOI 10.1016/0377-0427(94)00092-F | 저자 manuscript pp.2–6, interval 연산 및 §3 식 (3.1)–(3.9), Lemma 3.1·Theorem 3.2, parameter 확장 논의 | approximate inverse·residual·interval enclosure로 포함 인증을 만든다. 원 식 (3.6)의 centered enclosure 버전이 진술하는 존재·regularity와 full-box uniqueness 조건을 구분한다. |

쪽수는 실제 읽은 저자 PDF의 인쇄 쪽수다. 논문 전체나 numerical examples 전체를 읽었다고 주장하지 않는다. 세 번째 논문의 출판 정보는 [출판사](https://www.sciencedirect.com/science/article/pii/037704279400092F)와 [저자 소속기관 기록](https://tore.tuhh.de/entities/publication/973cf1c4-19ce-41ce-9c8d-4ed4a7b6622a)으로 확인했으며 파일명에서 연도를 추정하지 않았다.

## 2. 표준 정리의 적용 범위

Day의 정리는 \(T(u)=u-Jf(u)\), fixed 폭 \(w_i>0\)에서 중심 defect \(Y_i\)와 box 전체 변화의 component bound \(K_i\)를 사용한다. 조건은 \(Y_i+K_i<w_i\), \(\sup_i K_i/w_i<1\)이다. 유한 component/block majorant는 이 구조에 대응한다. **실제 범위 전체의 상계**가 필요한 이유와 variable scaling의 역할이 여기서 명시된다. 저자의 실험 timing과 interval-validated 결과도 원문에서 구분한다. [Day §2](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf)

branch-following 논문은 \(T_\nu=x-Af(\nu,x)\)에 대해 parameter 전 구간의 \(Y,Z\)와 음의 radii inequalities를 요구한다. 인증 구간의 일부 parameter 값만 검사한 결과로 tube 전체를 채우지 않는다. Proposition 8은 인접 enclosures의 nesting으로 같은 root를 연결한다. 단순한 두 box의 기하학적 교집합만으로 root의 동일성이 따라오는 것은 아니다. 읽은 PDF 텍스트의 Lemma 7 shifted-map 식에는 원점 중심 codomain에 필요한 predictor 차감 표기가 빠져 있다. 원 조판과 추출 중 어느 단계의 문제인지는 별도 확인하지 않았으므로 그 한 줄을 그대로 전사하지 않고 앞선 tube·fixed-point 정의로 좌표 변환을 확인한다. [Lemma 5·7, Proposition 8](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf)

Rump의 Theorem 3.2에서 사용하는 centered enclosure는 full-box Jacobian enclosure와 표기·범위가 다르다. 현재 후보가 채택할 **full-box Jacobian contraction**을 명시하면 uniqueness의 근거가 분명해진다. 전처리 역행렬의 역할, 입력·rounding·transcendental enclosure와 interval dependency도 실제 수치 인증의 일부다. [Rump §§2–3](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf)

## 3. 고정된 H/He 후보에서 확인할 연결

현재 계약은 하나의 실제 7변수 affine cube, \(\mu\) 범위, 여섯 photon node 및 full CI/RR/two-DR/photo model을 정한다. 다음 항목은 최종 후보를 심사할 적용 의무이며 아직 결과 판정은 아니다.

1. **물리적 domain:** cube 전체의 primitive, species, temperature 및 Doppler support가 먼저 입증되어야 그 domain에서 얻은 rate·derivative 상계를 사용할 수 있다. \(\mu\)의 허용 범위를 포함한 uniformity와 fixed scaling을 확인한다.
2. **실제 source 의존성:** primitive·density·electron·Doppler·photon elimination과 각 atomic moment의 변화를 포함한 transformed Jacobian 상계를 확인한다. node 중심이나 유한 표본의 최대값은 이 전체 box 상계를 대신하지 않는다.
3. **수치값의 근거:** exact inequality 또는 유효한 outward enclosure가 실제 양의 \(H\)와 contraction margin에 연결되는지 확인한다. 높은 표시 정밀도만으로 포함 인증을 대신하지 않는다.
4. **parameter와 시간 의미:** 고정 이전 상태에 대한 \(h\in[0,H]\)의 endpoint branch 인증, 여러 box를 잇는 continuation, 여러 물리적 time step의 누적 trajectory는 서로 다른 주장이다. 후보가 실제로 증명한 대상을 따라 채택한다.
5. **corrector와 연결:** approximate corrector의 수렴 기록과 실제 enclosure를 구별한다. 인접 인증은 포함관계 또는 공통 유일성 domain 안의 root라는 근거로 연결해야 한다.

이 목록은 저자 증명이나 수용기준을 새로 작성한 것이 아니다. 위 문헌의 조건을 현재 고정 계약과 대응한 독립 검토 범위다. 실제 full-rate 상계와 양의 interval은 root 및 해당 저자들의 후보·원 실행 근거를 받은 뒤 판정한다.

## 4. 물리 문헌 재사용과 검색 한계

THEORY05의 covariant source·gamma-law primitive·보존적 implicit radiation source에 대한 원전 읽기는 accepted PR33의 유지 근거로 재사용한다. 새 검색은 이를 되풀이하지 않았다. SciSpace에서 찾은 Dahmen–Gruber–Mula의 [adaptive radiative-transfer iteration](https://arxiv.org/abs/1810.07035)은 인접 분야의 후보지만, 이번 fetch는 abstract·index 자료만 반환했고 PDF open은 실패했다. 그 논문의 정리를 현재 moving H/He source에 적용하지 않는다.

kinetic positivity·Patankar 방법, chemical solver review, inexact Newton 강연과 acceleration 성능 연구도 검색에 나타났다. 이들은 서로 다른 discrete map 또는 다른 보장 범위를 갖기 때문에 고정된 backward-Euler source의 존재·유일성 근거로 전용하지 않았다. 제한된 검색을 문헌 전체의 부재나 신규성·불가능성 증거로 사용하지 않는다.

## 5. 실제 도구·읽기 회계와 보존

- Exa query **4회**, requested result slots **20개**, 반환 blocks **20개**, 서로 다른 URL **19개**.
- SciSpace query **1회**, paper entries **10개**.
- Exa fetch **4개 URL** 중 theorem 본문을 확보한 primary PDF **3개**, abstract/index만 확보한 항목 **1개**.
- 실제 식·정리 읽기 **3편**; 전체 논문 읽기 **0편**.
- 원 tool 입력·출력은 별도 local research cache에 그대로 보존했다. 공개 review에는 input·출력 locator·SHA256·read scope를 남기며 긴 원문 전체를 재배포하지 않는다.
- screenshot 요청은 image marker 텍스트만 반환했으므로 별도의 시각적 확인을 주장하지 않는다.

[SEARCH_EVIDENCE.json](SEARCH_EVIDENCE.json)은 실제 query·검색 결과·중복·선택 사유를, [SOURCE_EVIDENCE.json](SOURCE_EVIDENCE.json)은 theorem 읽기 위치·적용 조건·원 출력 identity를 기록한다. 최종 proof/evidence freeze 전에는 DECISION을 작성하지 않는다.

