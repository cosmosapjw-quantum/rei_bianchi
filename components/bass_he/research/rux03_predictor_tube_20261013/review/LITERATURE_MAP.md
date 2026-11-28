# THEORY07 독립 문헌 검토

검토자: /root/dropbox_checkpoint  
상태: 문헌의 추가 확인 완료, 현재 후보의 최종 판정 대기  
단위: HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07

## 이번에 확인한 범위

THEORY06의 세 원전과 정량 인증 결과는 읽은 범위 그대로 재사용한다. 이번 추가 확인은 parameter-dependent fixed point의 미분과 Newton 변환의 의미에 한정했다. 실제 Exa 검색 3회(15개 결과 URL), SciSpace 검색 1회(10개 반환 항목, 동일 논문 중복 1쌍)를 수행했다. 새 원전 2편의 필요한 절·식을 읽었으며 논문 전체를 읽었다고 주장하지 않는다. 후보 증명·코드·수용기준 작성과 과학 실행은 수행하지 않았다.

## 추가 원전

| 원전 | 실제 읽은 범위 | 이번 연결과 제한 |
|---|---|---|
| Helge Glöckner, *Finite order differentiability properties, fixed points and implicit functions over valued fields*, arXiv math/0511218v2, 2007-04-27 | [저자 원문](https://arxiv.org/pdf/math/0511218), printed pp. 34–38: Definition 4.4, Proposition 4.5와 증명, Remark 4.6 식 (42), Theorem 4.7의 진술과 증명 시작 | 균일한 contraction과 존재·정의역 가정 아래 parameter 미분을 준다. 상태 미분의 resolvent와 parameter 미분이 함께 들어간다. 정량 H 및 H/He rate 상계는 별도 의무다. |
| P. Deuflhard · G. Heindl, *Affine Invariant Convergence Theorems for Newton’s Method and Extensions to Related Methods*, SIAM JNA 16(1), 1–10, 1979 | [공식 서지](https://epubs.siam.org/doi/10.1137/0716001), [원 논문 OCR 재현](https://paperzz.com/doc/8502921/f--x-), §1 printed pp. 1–3: 식 (1.1)–(1.4), 예 (1.5)–(1.6′), 식 (1.7) | 가역 residual left-transform의 Newton 동치와 norm별 수렴상계의 차이, approximate Jacobian의 대응 조건을 확인했다. 일반 state/reanchor 변환 전체를 이 읽기에서 검증했다고 간주하지 않는다. |

Glöckner의 Proposition 4.5는 각 parameter에서 고정점이 존재한다는 조건을 포함한다. 실제 self-map과 contraction 인증이 이 전제를 충족해야 한다. 제안된 \(D_\xi X=F_X^{-1}\)는 같은 고정 chart에서 \(\xi\)가 additive하게 들어가고 \(G\)가 \(\xi\)와 독립이라는 조건을 확인한 뒤 적용한다. old photon 입력이나 anchor까지 변하면 해당 미분도 포함해야 한다.

Deuflhard–Heindl의 공식 PDF 클릭은 도구 오류로 실패했다. 서지는 공식 페이지와 저자 목록에서 대조했고 실제 식은 원 논문의 OCR 재현에서 읽었다. 일부 §2 반경 식은 손상되어 사용하지 않는다. 2018년 *The Grand Four*는 abstract와 index·강연 안내만 확인했으며 정리의 근거로 채택하지 않는다. 같은 주제의 generic web 검색이 반환한 무관한 결과도 사용하지 않았다.

## 재사용하는 THEORY06 원전

| 원전 | 이전 실제 읽기 | 이번에 유지할 조건 |
|---|---|---|
| van den Berg · Lessard · Mischaikow (2010), [Global smooth solution curves using rigorous branch following](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf) | §2 printed pp. 5–10, 식 (13)–(20), Definition 6, Lemmas 5·7, Proposition 8 및 접합 증명 | parameter 구간 전체의 predictor-tube 경계와 같은 근의 연결. 단순한 기하학적 상자 교차만으로 접합하지 않는다. |
| Day · Lessard · Mischaikow (2007), [Validated continuation for equilibria of PDEs](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf) | printed pp. 3–6, 식 (2.1)–(2.6), Theorem 2.1과 증명 | 고정 가중 norm, center defect와 전체 상자의 derivative bound를 구분한다. |
| Rump (1995), [Verified solution of large systems and global optimization problems](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf) | printed pp. 2–6, §2 및 §3 식 (3.1)–(3.9), Lemma 3.1, Theorem 3.2 | rounding과 interval 포함 관계를 유지한다. 읽은 centered-slope 정리의 존재·정칙성에 전체 상자 유일성을 무조건 추가하지 않는다. |

이전 source evidence의 읽기 한계도 유지한다. branch-following 원문의 shifted-map 표현은 추출 텍스트에서 predictor subtraction이 누락된 것으로 관측했지만 인쇄 원문의 시각 확인은 완료하지 못했다. 이번에 해당 논문들을 다시 fetch하거나 이전 심사를 재개하지 않았다.

## 후보에 대한 독립 검토 초점

아래는 현재 후보의 판정이 아니라 문헌의 적용 전제다.

- 모든 허용 \(h,\xi\)에서 물리적 cube 포함, full-box Jacobian 경계, self-map과 contraction이 성립해야 한다.
- 접합점의 인증된 근이 동일하다는 포함·유일성 논증을 확인한다.
- affine reanchor의 old-state, 잔차, approximate inverse, norm과 radius를 일관되게 옮겨야 한다. 정확한 Newton의 좌표 동치가 interval 폭이나 기존 \(Y,Z\) 수치를 그대로 보존하지는 않는다.
- 더 큰 \(h\), 두 slab 및 old-state family의 정량 여유는 저자 후보의 새로운 검산 대상이다. 표준 contraction 정리 자체를 새 정리로 취급하지 않는다.
- \(h\)-parameter의 implicit root family와 다단계 물리 시간 진화·시간 오차 인증의 범위를 구분한다.

## 부모 문서의 표시 정오

Frozen THEORY06 EXPLICIT_H_CERTIFICATE.md에서 open-brace + LF + m인 단위 조각 다섯 곳만 확인했다. Photon 23·35·70 eV 행 세 곳과 \(L_T=1400\ \mathrm K\), \(L_w=0.26\ \mathrm{eV/H}\) 두 곳이다. 실제 CR 문자는 0개이며 파일 SHA와 과학 입력은 변하지 않았다. 이전의 CR0 관측은 맞지만 literal 표기가 전부 복구됐다는 서술은 이 LF 잔여를 포착하지 못했다. 새 인용에서 단위를 바르게 표시하고 frozen 부모 파일은 수정하지 않는다.

입력·반환 결과·읽기 범위·SHA·미사용 검색은 SEARCH_EVIDENCE.json과 SOURCE_EVIDENCE.json에 기록했다. Full-text 응답은 별도 cache에 보존하며 공개 dossier에 논문 전체를 재배포하지 않는다.
