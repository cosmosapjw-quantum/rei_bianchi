# A2 원전 근거: united-atom 및 separated-atom 점근 구조

범위: A1b의 완료된 frame/ETF 정식화를 반복하지 않고, A2의 작은 R 상태 섭동과 큰 R 국소화에 필요한 근거만 조사했다. 기존 v3 source archive의 P06/P23/P24를 선택해서 읽고 실제 PDF 바이트를 catalog와 대조했다. 새 원전 GK1961은 저널 서버에서 확보했다. 계산·eigensolve·benchmark 추출은 실행하지 않았다. 원문 파일/페이지 이미지는 공개 게시 대상이 아니다.

## 근거와 허용되는 사용

| 원전 | 읽은 위치 | 이번 작업에서 뒷받침하는 내용 | 뒷받침하지 않는 내용 |
|---|---|---|---|
| **GK1961** S. S. Gershtein and V. D. Krivchenkov, *Electron terms in the field of two different Coulomb centers*, Sov. Phys. JETP **13**, 1044–1051 (1961) | PDF pp.3–5,7–8; journal pp.1046–1048,1050–1051; Eqs.(16)–(46), Appendix (A.1)–(A.14) | charge-center UA, degenerate spherical zeroth-order states, R² energy shift; unequal charges의 resonant separated-atom sector 국소화 | 특정 R10R Ly 계수, 전체 Hilbert 공간의 analytic family, Ly/weighted-Sobolev remainder bound |
| **P23** T. P. Grozdanov and E. A. Solov'ev, PRA **42**, 2703 (1990), [DOI](https://doi.org/10.1103/PhysRevA.42.2703) | PDF pp.5–8; journal pp.2707–2710, §IV A–D; p.2708·2710 시각 확인 | UA·SA label의 구별; branch-point/geometry에 따른 점근 영역 제한; symmetric와 asymmetric localization의 차이 | 제시된 branch-point 추정치를 BASS_HE의 엄밀 uniform radius로 사용; 분자상태 remainder의 operator norm bound |
| **P06** A. A. Gusev, E. A. Solov'ev and S. I. Vinitsky, CPC **286**, 108662 (2023), [DOI](https://doi.org/10.1016/j.cpc.2023.108662) | PDF p.5, Eqs.(17)–(18), 전후 설명; 시각 확인 | UA spherical label에서 SA center/parabolic label로의 구분; opposite-center의 exponential damping을 명시하고 GK1961을 ref.[31]로 인용 | energy sorting만으로 sector identity 선택; 정량적인 exact-molecular error certificate |
| **P24** A. K. Belyaev, A. Dalgarno and R. McCarroll, JCP **116**, 5395 (2002), [DOI](https://doi.org/10.1063/1.1457443) | PDF pp.4–5; journal pp.5397–5398, Eqs.(8)–(17); 시각 확인 | origin lever로 bare rotational matrix element가 R에 비례할 수 있음; origin change에 따라 다른 coupled-equation 항도 변하며 전체 해는 일치 | bare nonzero를 독립 전이율로 더하기; 바뀐 origin의 coupling만 교체하고 equation의 나머지를 유지하기 |

GK1961의 [공식 저널 PDF](https://www.jetp.ras.ru/cgi-bin/dn/e_013_05_1044.pdf)는 실제 확보·열람했다. PDF pp.5,7을 그림으로 확인하여 OCR 수식에 의존하지 않았다. 그 밖의 source identity와 읽은 위치는 JSON manifest에 있다.

## 작은 R: 원전이 주는 것과 남겨 두는 것

GK1961 p.1048은 charge-center에 놓인 전하 Z₁+Z₂의 원자를 기준으로 하고, degenerate cluster의 zeroth-order eigenvectors를 spherical Coulomb states로 택한다. 같은 N의 l↔l+2 radial integral이 영이라는 항등식을 근거로 든다. Eq.(45)는 전자 에너지의 R² 항이다. 원전은 atomic units를 쓰며, **이 식은 Ly 전이행렬원소에 대한 식이 아니다.**

원전의 R² energy 결과는 source-supported지만, 여기서 exact state expansion이 Lᵧ-graph norm에서 정해진 차수로 성립한다고 추론하면 안 된다. 특히 ground-state odd-parity mixing을 얻기 위해 외부 multipole potential을 r=0까지 무조건 적용하는 것은 이 원전이 제공한 정당화가 아니다. energy expansion, weak matrix-element expansion, state expansion, angular-momentum matrix-element expansion의 remainder는 각각 구분해야 한다. A2가 독자적으로 도출한 contact/inner-region 항과 범위는 `derived`로 분류한다.

보충 원전 **BHL2008**: D. I. Bondar, M. Hnatič and V. Yu. Lazur, *Symbolic computations for the two-Coulomb-centers problem in the space of arbitrary dimension*, Physics of Particles and Nuclei Letters **5**, 255 (2008), [DOI](https://doi.org/10.1134/S1547477108030242). [JINR 공개 원문](https://www1.jinr.ru/Pepan_letters/panl_3_2008/24_bond.pdf)의 PDF pp.4–6, Eqs.(14)–(18)을 읽었다. 안쪽 radial solution과 큰 ξ solution을 matching하고, 증가 지수해의 계수를 제거하여 spectral condition을 구성한다. 이것은 separated equations를 이용한 matching 경로의 근거다. **이 짧은 논문에서 R10R g,b의 remainder bound 또는 해당 Ly leading coefficient를 확인하지 못했다.** 로그항의 정확한 시작 차수도 이 원전으로 인증하지 않는다.

추가 후보 Abramov–Slavyanov, J. Phys. B **11**, 2229 (1978), DOI `10.1088/0022-3700/11/13/007`; Bondar–Hnatič–Lazur, J. Phys. A **40**, 1791 (2007), DOI `10.1088/1751-8113/40/8/008`; Nickel, J. Phys. A **44**, 395301 (2011), DOI `10.1088/1751-8113/44/39/395301`는 fulltext authority로 채택하지 않았다. 공개 검색 결과는 작은-R 로그항을 언급하지만, 이번에 원문을 확보하지 못했으므로 exact coefficient·차수·norm theorem의 근거로 쓰지 않는다. 반복 접근은 중단했다.

## 큰 R: atomic energy degeneracy와 sector localization은 양립한다

GK1961 Appendix는 Z₁/n=Z₂/n′로 isolated atomic energies가 같을 때도 Z₁≠Z₂이면 1/R diagonal energy difference가 exponentially small cross-center mixing보다 크다고 설명한다. 따라서 각 asymptotic state는 한 핵으로 국소화된다. 반대로 동핵의 symmetric/antisymmetric states는 두 중심 조합으로 남는다. 이는 H(1s)와 He⁺(n=2)의 공통 한계 에너지만 보고 두 sector를 혼합하거나 label을 버려서는 안 된다는 직접 근거다. 원전의 분석은 asymptotic atomic-combination 방식이며 exact projector의 norm bound를 명시한 정리는 아니다.

그러므로 A2에서 다음 두 주장을 분리한다.

1. `literature-supported`: 중심별 sector 구분, 1/R diagonal separation, intercenter mixing의 exponential suppression.
2. `derived` 또는 `unresolved`: BASS_HE의 특정 g,b와 atomic comparison states의 오차를 unbounded Lᵧ에 넣어도 작은 항이 되는지, 그 power 및 상수. 단순 L² convergence만으로 ⟨g,Lᵧb⟩의 remainder order는 따라오지 않는다.

P24 Eqs.(9),(17)은 origin displacement에 energy gap×atomic dipole을 곱한 rotational term의 선형 R 구조를 보여 준다. 이 사실과 큰-R ETF-completed generator의 감쇠는 모순이 아니다. 서로 다른 객체이며, completed generator에서는 translation·basis connection을 함께 처리해야 한다. 이번 문헌 검토는 A1b의 exact P⊕Q memory를 없앨 근거를 제공하지 않는다.

## 판정

**SOURCE_BOUND_SUPPORT_WITH_REMAINDER_GAP.** 확보한 1차원전은 UA charge-center convention, degeneracy 처리 및 SA sector localization을 뒷받침한다. exact R10R 작은-R Ly coefficient와 두 극한의 uniform state/weighted-derivative remainder를 문헌만으로 freeze할 수는 없다. A2 본문의 직접 유도와 독립 검토가 그 공백을 닫았는지에 따라 최종 gate를 정해야 한다.

이번 접근 실패는 일부 추가 문헌의 web fetch failure다. 기존 자료 훼손, 수식 반례, scientific gate failure로 분류하지 않는다. 기존 source 재다운로드·전체 데이터베이스 재구축·A1b 시험 재실행은 없었다.
