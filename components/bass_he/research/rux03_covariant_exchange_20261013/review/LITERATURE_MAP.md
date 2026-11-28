# HE covariant 04 — 일차 문헌 지도

**역할:** `/root/dropbox_checkpoint`, 문헌·소스 검토 후 독립 최종 검토자. 후보 유도나
수용기준을 작성하지 않았다. 공통 gas four-velocity와 현재 Case A 가정을 유지한다.
별도 all-Bianchi abundance-source/relative-species-tilt D2.3 과제는 이 조사 범위가 아니다.

Exa Search 스킬의 `searching.md`와 `patterns-papers.md`를 읽고 세 방향으로
각 5개 결과를 요청했다. **15개 검색 결과 슬롯에서 네 원논문을 선택하여 필요한 식과
주변 문맥을 읽었다.** 이는 15개 논문 전체를 읽었다는 뜻이 아니다. SciSpace는 두
질문을 사용했다. 첫 복합 질문은 범위 밖 atomic/QED 문헌으로 쏠려 제외했고, 좁힌
질문에서 2015 RAMSES-RT 원논문을 확인했다. 식의 근거는 검색 요약이 아니라 원문이다.

## 1. 채택하는 일차 근거

| ID | 원전 | 실제 읽은 위치 | 채택 범위 |
|---|---|---|---|
| L01 | Farris, Li, Liu & Shapiro (2008), [arXiv:0802.3210v1](https://arxiv.org/pdf/0802.3210), [PRD DOI](https://doi.org/10.1103/PhysRevD.78.024023) | PDF pp3–4, §II.B.1 식(19),(20),(30)과 (31)–(33)의 가정; 단위·metric 정의 | 일반 복사 four-force와 물질/복사 divergence 부호 |
| L02 | Barrow & Maartens (1999; preprint1998), [astro-ph/9808268v1](https://arxiv.org/pdf/astro-ph/9808268), [PRD DOI](https://doi.org/10.1103/PhysRevD.59.043502) | §II, PDF pp2–3, 식(1),(4),(5),(11),(12); 식(11)은 p3 | 정확한 1+3 radiation energy/momentum projection과 shear/acceleration 항 |
| L03 | Rosdahl & Teyssier (2015), [1411.6440v2](https://arxiv.org/pdf/1411.6440v2), [MNRAS DOI](https://doi.org/10.1093/MNRAS/STV567) | §2.3.3 PDF p5 식(26)–(28), Appendix A p24의 근사 범위 | H/He 흡수 momentum deposition와 1차 v/c 근사의 구별 |
| L04 | Rosdahl et al. (2013), [1304.7126v2](https://arxiv.org/pdf/1304.7126) | Appendix A PDF p37 식(A6)–(A10), p38 식(A15),(A16) | 등방적 recombination의 공간 flux moment와 ionization heating 구조 |

### L01 — four-force 일반식과 추가 closure를 구별

논문은 c=G=1과 −+++ convention을 사용한다. 물질이 받는 four-force를 G로 쓰면

\[
\nabla_\beta R^{\alpha\beta}=-G^\alpha,
\qquad
G^\alpha=\int(\chi_\nu I_\nu-\eta_\nu)N^\alpha\,d\nu\,d\Omega .
\]

이 일반 정의가 이번 연결의 직접 선례다. 뒤의 Kirchhoff·grey formula와 거의
등방적인 Eddington closure는 추가 가정이다. 특히 식(26)은 일반 anisotropic π를
포함하지 않으므로 Bianchi stress 전체식으로 가져오지 않는다. 현재 non-LTE Case A
방출을 Planck emissivity로 교체할 근거도 아니다. 등방 방출의 순공간 momentum이
기체 rest frame에서 0이라는 사실과 emission four-force가 0이라는 주장을 구별해야 한다.

### L02 — shear-work는 확립된 projection 항

원문의 비상호작용 radiation component는

\[
\dot\mu+\frac43\Theta\mu+D^a q_a
=-\sigma^{ab}\pi_{ab}-2A^a q_a
\]

를 만족한다. 식(12)는 공간 운동량에서 acceleration·pressure/stress gradient·shear·
vorticity도 남긴다. 해당 식들은 선형화 전의 정확한 식이다. 이번 H/He collision source의
추가는 후보의 공통 four-force에서 별도로 따라야 한다. Bianchi의 구체적 s와 Π 정의로
계수와 부호를 환원하는 일은 프로젝트 연결이며, 이 원전이 그 노드 정규화까지
검증한 것으로 쓰지 않는다. homogeneous/geodesic 단순화에는 해당 flux·acceleration
조건이 필요하다.

### L03 — 흡수 에너지와 운동량의 역할

식(27)은 energy flux F에 대해 H/He absorber의 contribution을

\[
\dot{\boldsymbol p}_\gamma
=\sum_i\frac{\boldsymbol F_i}{c}
\left(\kappa_i\rho+\sum_j\sigma_{ij}n_j\right)
\]

로 준다. 식(28)은 substep 흡수 momentum을 모으고 gas kinetic energy를 갱신한다.
Appendix A는 O(v/c)까지만 유지하며 제곱항을 생략한다고 명시한다.
이것은 완전한 atomic recoil 또는 모든 frame에서 정확한 미시적 rate 모델의 근거가 아니다.

**원문 사용 제한 LIT-S01:** HTML 식(97),(98)과 PDF text (A7),(A8)의 부호는 이웃 식의
v=0 absorption 및 총 에너지 설명과 그대로 대조할 때 문제가 있다. 특정 mixed-frame
식은 exact-covariant 근거에서 제외하고 명시된 근사 범위만 사용한다. PDF screenshot은
image block 없이 표시 문자열만 반환했으므로 시각 판독을 주장하지 않는다.

### L04 — 등방 방출과 photoheat

PDF 식(A6)–(A8)은 등방 recombination emission이 photon number에는 기여하고
공간 flux source에는 기여하지 않는다는 가정을 명시한다. 식(A15),(A16)의 heating은
흡수 photon energy에서 ionization energy를 뺀 양이며, 그룹 평균에서도 number/energy
cross section을 구별한다. HTML에서는 동일 식의 번호가 각각(54)–(56),(63),(64)이다.
그 논문의 transported recombination/OTS 선택을 현재 Case A escape로 바꾸어 인용하지
않는다. 읽은 식들은 현재 provider의 species별 recoil 분배나 captured kinetic moment의
원자료 보정을 제공하지 않는다.

## 2. 이번 후보를 검토할 때 구별할 사항

다음은 원전과 보존 가정의 적용 경계이며 새 후보 알고리즘이나 시험 설계가 아니다.

- Scalar heat, binding 변화, escape luminosity와 물질이 받는 총 four-force의 관계를
  같은 event 정의에서 읽어야 한다. Heat에 쓰는 excess energy를 photon 전체 momentum과
  혼동하면 안 된다.
- Emission isotropy의 frame과 source의 proper-volume/proper-time 정규화를 명시해야 한다.
  공통 gas velocity를 사용한다는 조건만으로 acceleration이나 radiation flux가 0이 되지는 않는다.
- 일반 1+3 identity와 정해진 Bianchi background의 특수화를 구별한다. π·q·A의 제거는
  정의 및 대칭 조건에 따라야 한다.
- 현재 warm Case A rate/moment는 보존된 현상론적 입력이다. 공변적인 tensor 표현이
  그 자체로 새로운 relativistic atomic recoil 계산이나 rate-domain 승인이 되지는 않는다.
- 일반 four-force, isotropic angular moment와 shear projection은 확립된 내용이다.
  새 성과의 범위는 보존된 H/He event/moment bookkeeping과 지정된 Bianchi convention을
  일관되게 연결하는 프로젝트 구성으로 평가한다. 전역 독창성 조사는 하지 않았다.

## 3. 남긴 근거와 재사용 범위

`SEARCH_EVIDENCE.json`에는 실제 Exa/SciSpace 질문, 결과 title/URL/ID와 선택·제외를
기록했다. `SOURCE_EVIDENCE.json`에는 읽은 페이지·식, PDF/HTML 번호 대응, source 제한과
web retrieval identity를 기록했다. 전문은 재배포하지 않는다.

직전 `PRIMARY_THEORY_03`의 사건·energy residual·BE product rule 판정은 보존 근거다.
이번 문헌 조사에서 그 기호 계산이나 native/ODE 결과를 재실행하지 않았다.
최종 후보와 Wolfram/xAct 원자료가 고정되면 별도의 독립 판정을 작성한다.
