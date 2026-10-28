# 선택 광자–동위원소·이온 결합 충돌 연구 루프

이번 단위는 고정된 13개 광이온화 반응에 대해 광자 16성분, 선택 핵종·이온 21성분, 에너지 장부 B/K/Xext를 연결하는 40상태 순간 RHS와 전체 국소 Jacobian을 구현했다. 기존 radiation-frozen target 미분에서 빠졌던 광자→이온 및 이온→광자 교차 미분을 포함했다. 기존 완료 계산은 재실행하지 않았다.

전체 목표에서의 위치는 원 WORK_THREAD의 **N3 → N4**, 중앙 87노드 DAG의 **REI-L1 부분 완료 / REI-EXP-OPACITY-CONSUMER**이다. 이 문서의 완료는 이 유한 연산자 단위에 한정한다. N6 HOLD, L4_ready=false, 전역 물리 완료율 null을 유지한다. 중앙 DAG나 다른 담당자의 노드를 직접 완료로 바꾸지 않는다.

## 구성과 물리적 의미

각 광자 packet j와 전자 이온화 edge e에 대해

\[
R_{ej}=c n_{\rm ref}\sigma_{a(e)}(E_j)y_{\ell(e)}N_j
\]

를 한 번 계산한다. 같은 사건률로 광자 제거, 낮은 전하상태 감소, 높은 전하상태 증가, 결합에너지 B 증가, 일차 전자에너지 K 증가를 조립한다. 외부 광원 에너지는 Xext에 기록한다. B는 이온 내부에너지의 중복 진단 변수이므로 총에너지에 한 번만 센다. K는 주입된 일차 전자에너지이며, 열화·이차 이온화·실제 gas heating은 아직 계산하지 않았다.

정규화된 모든 변수 z에 동일한 기준밀도 항을 적용한다.

\[
\Lambda=\frac{\dot n_{\rm ref}+3Hn_{\rm ref}}{n_{\rm ref}},\qquad
F=F_{\rm collision}+F_{\rm source}-\Lambda z,\qquad
J=J_{\rm collision}-\Lambda I-z\otimes\nabla\Lambda.
\]

현재 기준은 보존되는 comoving Href이므로 proper 밀도가 a^-3으로 감소해도 Lambda=0이다. 별도 affine-Lambda 검사는 변수 표현의 변환을 검증한다. nref 자체를 상태의 대수함수로 정의한 일반 모형은 추가 chain rule이 필요하며 이번 검증 대상에 포함하지 않는다.

| 축 | 이번에 명시·검증한 내용 | 물리적 해석 |
|---|---|---|
| 대칭성·게이지 | (-,+,+,+), 기존 normal observer, 고정 energy packet, 기준밀도 rescaling | 관측자와 표현을 고정한다. 기준 변경이 새 입자 생성원이 되지 않는다. |
| 불변량 | 동위원소·바리온 수, 전하 유도 전자수, B=epsilon·y, 광자/전자 사건수, 에너지 장부와 그 미분 | 하나의 사건을 모든 성분에 일관되게 배정한다. E_dot·N은 명시된 에너지 이동 일로 한 번 포함한다. |
| 실제 관측가능량으로 이어질 양 | 지정 normal observer에서의 흡수·이온화 사건률, 일차 전자 주입률, 광원 power | 이번 값은 선언된 유한 시험 상태의 국소 응답이다. 관측된 abundance나 보정된 우주 이력으로 해석하지 않는다. |

광원은 기존 실제 z=2 stellar/external IGM 식·정규화·원자 단면적을 재사용했다. 5–150 eV를 문턱과 LiI 식 전환점에서 나눈 GL2 16점 규칙이다. photon fixture는 N=1초×광원이며, y는 이전에 공개한 양의 synthetic API fixture이다. n=T=10^-20/Href는 수치 API 검사용 입력이지 우주 생성량 예측이 아니다. n/T=0 면도 별도로 검사했다. 새 연속 스펙트럼 수렴성이나 실제 z=2 target history를 주장하지 않는다.

## 실제 검증

Wolfram의 서로 다른 기호 residual 75개가 정확히 0이었다. 첫 context 오류와 경고, 교정 후 실제 실행 결과를 함께 보존했다. SciSpace·Exa와 1차 문헌을 이용한 근거는 theory/SOURCES.json에 있다. 관련 기존 연구는 Reynolds et al., [arXiv:0901.1110](https://arxiv.org/abs/0901.1110)의 결합 복사·화학 수치계와 Abel et al., [astro-ph/9812151](https://arxiv.org/abs/astro-ph/9812151)의 보존형 복사전달이다. 이것이 이번 구현의 검증을 대신하지는 않는다.

| 검사 | 관측된 최댓값 / 결과 | 고정 기준 |
|---|---:|---:|
| 전체 검사 | 19/19 PASS | 모두 통과 |
| 각 active Jacobian entry complex-step | 6.567124650813327e-16 | 2e-12 |
| 구조적 zero entry | 0 | 0 |
| 행별 scale을 사용한 중심 유한차분 | 4.631090281577312e-13 | 2e-5 |
| affine Lambda 전체 Jacobian complex-step | 4.1312944324879133e-16 | 2e-12 |
| 독립 scalar 사건 조립의 미분 | 4.213027004381585e-16 | 3e-12 |
| 충돌 에너지 잔차 | 1.0795584324889047e-16 | 3e-12 |

희귀 Li6/Li7와 trace T를 각각 검사했고 작은 미분값을 max(1,|J|)로 가리지 않았다. source 진폭 미분은 photon state를 고정한 partial derivative이다. 단위 노출 fixture를 함께 미분하지 않았다. FD에서는 광원 주입을 끄고 광자는 유지하여 작은 충돌 반응을 확인했다. 전체 결합 Jacobian은 Metzler가 아니며, 고정된 광자장에서 target 전이 block의 성질과 구분했다.

실행은 1회, exit 0, CPU 0.200332초, wall 0.20596811699942918초였다. 1 CPU초/5 wall초/soft timer 0.8초, 1 worker/BLAS 1, 1 GiB 제한을 사용했다. 29개 source/input binding과 전후 bytes를 보존했다. 새 IVP와 이전 검증 suite 재실행은 0회다. 요청한 실행 모델은 gpt-6.1-sol/high, 검토는 별도 gpt-6-astra/high이며 실제 runtime model identity는 도구에서 노출되지 않아 UNEXPOSED로 기록했다.

독립 최종 판정은 **PASS_SCOPED**이다. review/ASTRA_FINAL_REVIEW.md 및 review/VALIDATION.json에서 실제 19개 검사, 29개 source binding, 36개 output hash와 저장 배열의 보존법칙을 독립 확인했다. 수정이나 재실행 없이 이 유한 연산자 범위가 승인됐다.

## 보존·남은 목표

- Source 누적: 8.201436/10 CPU초, 8.23558345200945/20 wall초. 남은 비용은 새 실행의 자동 승인이 아니다.
- Main: 595.225063/600 CPU초, NO_MORE_IVPs. N6 HOLD를 유지한다.
- Render: 15.533337507/16 CPU초. 이번에는 새 rendering을 하지 않고 이전 all-selected 21상태 HOLD plot과 opacity 결과를 보존한다.
- Packaging: 이전 4.978747874 CPU초/4.988865237003698 wall초에서 이어간다. 새 실제 비용은 delivery/*_PACKAGE_RECEIPT.json에 추가한다.
- 기존 owner PR221, ANGTHERM02 읽기 전용 예약, WU의 generic event compiler 소유권을 보존한다.

다음의 실질 의무는 WU가 제공한 event compiler의 독립 승인·import를 확인하고, 이번 선택 consumer를 선언된 물리 scenario와 실제 target/radiation 입력에 연결하는 것이다. 그 후 기존 provider의 beta daughter/stopping 및 n→p 공급, n/T 생성·소멸과 CR/중성미자/inverse-beta 채널을 L2/L3와 연결해야 한다. 해당 물리 입력·closure·남은 실행 예산이 갖춰지기 전까지 coupled history와 최종 all-selected-isotope/ion physical pilot plot은 열린 목표다. 이번 고정 전자 이온화 목록에 nuclear reaction이 없다는 사실을 n/T의 물리적 부재로 해석하지 않는다.

최종 과학 산출물은 승인된 별도 branch의 additive draft PR로 게시하고, recovery archive를 Drive와 Dropbox에 각각 저장한다. 이 문서와 archive는 자신의 이후 Git/저장 receipt보다 먼저 고정된다. 실제 commit·PR·provider ID·readback 결과는 이후 작성되는 delivery/FINAL_DELIVERY_RECEIPT.json을 확인한다. 이 순서는 자기 자신을 포함하기 위해 archive를 반복 재작성하지 않기 위한 것이다.
