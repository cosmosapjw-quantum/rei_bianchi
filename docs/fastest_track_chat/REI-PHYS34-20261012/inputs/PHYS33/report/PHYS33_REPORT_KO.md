# REI-PHYS33 — 고정 커널에서 유한 폭 상단 분지의 존재와 순서

연구일: 2026-10-12 KST / 2026-10-11 UTC. 최신 완료 PHYS32의 `PINNED_KERNEL_PACKET_SIGN_AND_ROOT_TUBE_ENCLOSURE` 인계를 수행했다. 이 보고서는 실제 수치 인증과 증명 연결을 기록한다. 최종 독립 판정과 전체 closeout 상태는 `../independent/DECISION_REVIEW.json`, `../state/FINAL_STATE.md`, `../state/CLOSEOUT.json`을 따른다.

## 1. 이번에 얻은 결론

**고정된 source-real 커널과 상속된 정확한 공통 높이 A에서, 0<δ≤0.001 eV 전체에 대해 지정한 ŵ±0.25 eV² tube 안에 두 상단 분지 근이 각각 존재하고 유일하며 \(W_p(\delta)<W_u(\delta)\)임을 인증했다.** 실제 분산 W를 사용했고, 같은 평균·같은 이차 모멘트를 갖는 균일 프로파일과 P4 프로파일을 비교했다. 특정 폭의 표본값이나 작은 폭의 형식적 계수 부호만으로 내린 결론이 아니다.

이번에 확인한 보수적 경계는

\[
\boxed{-8.8300\times10^{-3}\,\delta^4
\le W_p(\delta)-W_u(\delta)
\le-1.0760\times10^{-5}\,\delta^4<0}
\]

이다. 계수의 단위는 eV⁻²이고 δ는 eV 단위다. 특히 δ=0.001 eV에서는

\[
\boxed{-8.8300\times10^{-15}\le W_p-W_u
\le-1.0760\times10^{-17}\quad\mathrm{eV}^2.}
\]

이 구간은 양끝 사이에서 정확한 차이를 예측하는 값이 아니라, 부호까지 포함한 안전한 포함 구간이다. δ=0에서는 두 프로파일이 같은 근을 가지므로 엄격한 순서가 사라진다.

**Physical HOLD는 유지한다.** 이번 정리는 지정된 고정 커널에 관한 수학·구현 명제다. 원 J·원자 fit의 물리적 불확실성, 하단 분지, 두 분지의 gap 부호, 전체 coupled history를 인증하지 않았다. 보호 상태는 다음과 같다.

| 항목 | 유지 상태 |
|---|---|
| Physical admission | HOLD |
| 기존 실패 구간과 tick | [160,161] FAIL; tick160 |
| auxiliary escape | FAIL |
| HH / RCT / CR | OFF / OFF / OFF |
| precision atomic | PARKED |
| production source / default / runtime 변경 | 0 |

근거: `PHYSICS_CONTRACT.json`, `evidence/CERTIFICATE_FIRST.json`, `report/ROOT_TUBE_PROOF_KO.md` R33.1–19. 위 보호 상태의 직전 원본은 동봉한 PHYS32 `state/FINAL_STATE.md`와 `CLOSEOUT.json`이다.

## 2. PHYS32에서 무엇이 더 진행되었나

PHYS32는 같은 2차 모멘트 프로파일의 차이를 정확한 양의 Peano 평균으로 표현하고, 커널 4차 미분의 부호·기울기·근 tube가 확보되면 유한 폭의 근 순서를 얻는 구조를 정리했다. 이번에는 그 조건을 **실제 고정 입력의 한 분지와 닫힌 폭 구간에서 수치적으로 충족**했다.

| 의무 | PHYS33에서 확보한 근거 |
|---|---|
| 패킷과 기울기 적분 경로의 영역 | 전체 (δ,W) 직사각형의 exact 유리수 포함관계 |
| k″, k⁽⁴⁾ 부호 | 유리수 다항식 Bernstein 계수 + 바깥 반올림 외부 인자 |
| 같은 A의 두 근 존재 | 저장 중심의 실제 잔차, 균일 이동 상계, 양의 기울기 |
| 유일성 | 전체 tube에서 ∂WFα≥κ>0 |
| 엄격한 유한 폭 순서 | 정확한 Peano 항등식과 평균값 정리 |
| 재현성 | 복원 경로에서 같은 입력·코드로 재실행한 raw byte identity |

최신성은 기억 요약이 아니라 저장소 원본으로 판정했다. 시작 기준 commit은 `e7cf037a07a8b238207cce45ac944497b0387253`, PHYS32는 완료·scoped promote 상태였고 후속 인계는 PHYS33이었다. PHYS32의 predecision `RESEARCH_STATE.md`보다 완료 후 `FINAL_STATE.md`와 `CLOSEOUT.json`을 우선했다. [PHYS32 인계 원본](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/e7cf037a07a8b238207cce45ac944497b0387253/docs/fastest_track_chat/REI-PHYS32-20261011/next/PHYS33_NEXT_HANDOFF_KO.md).

## 3. 고정 입력을 어떻게 해석했나

물리 에너지 범위는 a=13.61, b=24.58, 평균 m=18 eV이며 R=m−a=4.39 eV다. 상단 분지의 저장 분산 중심은 약 16.3399446545897073 eV²이고 전체 문자열은 증명 문서에 보존했다. 근 tube는 이 정확한 중심의 ±0.25 eV²다. 실제 분산을 W라 두고 두 패킷 중심의 이산 분산은 V=W−δ²/3으로 보정했다.

비교 프로파일은

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16},\quad -1\le z\le1.
\]

둘 다 정규화·양성·짝대칭을 만족하며 공통 이차 모멘트는 1/3이다. 4차 모멘트 차이는 8/315다. 따라서 보존된 분산에서 프로파일 모양만 바꾼 비교다.

공통 높이는 PHYS29의 정확한 키 `second_order.jet_chain.upper_root.response_s-4`에서 읽은

\[
A=-2.2748589\times10^{-137}\ \mathrm{s}^{-4}
\]

이다. 이는 0이 아니다. 더 긴 다른 저장 높이로 대체하지도 않았다. Jx, Jw는 PHYS22 `results.baseline_local.J_nonphoto[2][0]`, `[2][3]`의 문자열 그대로다. 해당 두 입력 JSON의 SHA256은 각각 다음과 같다.

| 입력 | SHA256 |
|---|---|
| PHYS29 SECOND_ORDER_FIRST | `40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f` |
| PHYS22 INITIAL_COEFFICIENTS | `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79` |

원 소스의 binary64 상수를 그 값 자체의 정확한 유리수로 해석한 다음 실수 곱을 취했다. J와 A는 직렬화된 정확한 십진 유리수다. 따라서 이 연구의 source-real convention은 원 소스 상수에 고정되어 있지만 native binary64 연산 순서 전체를 모사하지는 않는다. 물리 prefactor의 c는 cm/s로 유지했다. H I cutoff real64(13.60), He I cutoff real64(24.59), 에너지 오프셋 χ=real64(13.598434599702)는 서로 구별했다.

입력 해석의 상속 근거: 동봉 PHYS31 `INPUT_KEYS_AND_TWO_EXPRESSIONS_KO.md`, `KERNEL_REGULARITY_AND_PROFILES_KO.md`. 저장소 식의 확인에는 `atomic_provider.rs` 315–365 및 `coupled_primary.rs` 1–115 발췌를 사용했다. 발췌 파일을 소스 전체의 materialized copy로 표시하지 않았다.

## 4. 상쇄를 피하면서 전체 구간을 인증한 방법

고정 커널은

\[
k(E)=\mathcal P(D^2+3D)\phi(E),\quad D=E\partial_E,
\qquad \phi=\sigma_{HI}(E)[J_x+J_w(E-\chi)]
\]

이다. \(u=\sqrt{E/(E_0y_a)}\)로 치환하면 k의 0–4차 미분은 양의 거듭제곱 인자와 exact 유리수 다항식 Qn의 곱이 된다. Qn의 차수는 최대 8+n≤12다. 다항식 미분 재귀와 Bernstein 기저 변환은 `contributions/theory/DERIVATION_KO.md` T33.7–22에 직접 유도했다.

E∈[13.61,22] 전체를 포함하는 sqrt-domain을 32개 exact rational cell로 나누었다. 각 cell의 Bernstein 계수 최소·최대는 그 cell의 모든 점에서 다항식을 덮는다. 외부 인자는 90자리 Decimal 구간 연산으로 바깥 반올림했다. ln·exp·sqrt의 올바르게 반올림된 값에 인접 representable 값을 붙였고 거듭제곱은 exp(α ln x)로 계산했다. 이 경계는 Python Decimal/libmpdec의 산술 의미를 신뢰한다. [Python 3.12 Decimal 공식 문서](https://docs.python.org/3.12/library/decimal.html).

Bernstein 계수 경계의 exact cell과 Decimal 표시용 `z_interval`의 차이는 증명 R33.5에 명시했다. 실제 grid가 cutoff를 넘지 않는 포함관계도 exact 비교했다. 부호 증명에 조밀한 점 샘플, root iteration, 유한 폭 수치 적분을 쓰지 않았다.

| 인증량 | 보수적으로 표시한 결과 | 역할 |
|---|---|---|
| k″ 범위 | [2.8173987399×10⁻⁶⁶, 6.0442193357×10⁻⁶⁵] s⁻⁴ eV⁻² | 양의 W 기울기 |
| k⁽⁴⁾ 범위 | [3.0731179233×10⁻⁶⁷, 1.1754655667×10⁻⁶⁵] s⁻⁴ eV⁻⁴ | 두 프로파일 응답의 엄격한 차이 |
| Bdisp | <1.8002089619×10⁻⁶⁷ s⁻⁴ | 0≤δ≤0.001에서 중심·가중치·프로파일 이동 |
| κη−(Bdisp+εr) | >1.7215394631×10⁻⁶⁷ s⁻⁴ | tube 양 끝이 A의 반대편임을 보장 |
| 모든 폭의 근과 저장 중심 사이 거리 | <0.127793 eV² | ±0.25 tube 내부의 더 작은 위치 경계 |
| 영폭의 정확한 A 근과 저장 중심 사이 거리 | <7.005×10⁻⁷⁷ eV² | 저장 중심을 정확한 근으로 가정하지 않음 |

마지막 행의 극히 작은 값은 고정된 수학적 입력에서 얻은 잔차 기반 거리다. 원자물리적 정확도를 나타내지 않는다. 저장 중심의 잔차는 실제로 약 −9.86683597×10⁻¹⁴³ s⁻⁴의 음의 구간이며, 코드가 이를 0으로 만들지 않았다. 표의 모든 간략 수치는 원시 경계를 더 바깥으로 반올림했다.

## 5. 왜 두 근의 순서를 얻는가

첫째, 전체 tube의 W 기울기는

\[
\partial_WF_\alpha(\delta,W)=
\int_0^1t\int k''((1-t)e_\delta+t x_{\delta,W}+\delta z)
d\alpha(z)dt
\]

로 표현된다. k″>0이므로 κ=m2/2≤∂WFα≤M2/2=K다. 저장 중심의 잔차와 폭 변화의 균일 상계가 κη보다 작으므로 tube 양 끝은 공통 A를 사이에 둔다. 중간값 정리와 단조성으로 두 프로파일 모두 각 폭에서 정확히 한 근을 갖는다.

둘째, PHYS32가 유도한 정확한 Peano 항등식은

\[
f_p(y)-f_u(y)=\frac{\delta^4}{945}
\mathbb E_{\pi_4}[k^{(4)}(y+\delta Z)],
\quad \pi_4(z)=\frac{315}{256}(1-z^2)^4
\]

이다. π4는 양의 확률밀도이고 두 패킷 가중치의 합은 1이므로, 인증한 m4와 M4가 응답 차이를 바로 덮는다. 같은 A에서 p 프로파일이 더 큰 응답을 가지므로 증가함수의 근은 더 작은 W로 이동한다. 평균값 정리와 κ,K를 결합하면 첫 절의 정량 부등식이 나온다. 이 945 정규화의 직접 증명은 `ROOT_TUBE_PROOF_KO.md` R33.15–17과 상속한 Peano 문서에 있으며 일반 Rodrigues 배경은 [DLMF 18.5(ii)](https://dlmf.nist.gov/18.5#ii)를 참조한다.

이 논증은 두 아주 가까운 수치 근을 구해서 빼는 계산에 의존하지 않는다. 그 대신 양의 적분의 하한을 바로 차이에 전달한다.

## 6. 실제 실행과 재현성

계약과 프로토콜, 입력 2개, 새 코드 3개, 대수 증명 1개를 최초 main 이전에 동결했다. `evidence/PREEXECUTION_FREEZE.json`에는 실제 8개 파일 SHA256이 있다. 첫 실행 후 같은 동결 입력을 별도 경로에 복원하고 replay 1회를 실행했다. 이 문서 작성 과정에서 과학 계산을 더 실행하지 않았다.

| 항목 | 첫 실행 | 복원 재실행 |
|---|---:|---:|
| 검사 | 29/29 PASS_SCOPED | 29/29 PASS_SCOPED |
| wall time | 0.970251 s | 0.916250 s |
| CPU time | 0.967342 s | 0.915743 s |
| peak RSS | 14,464 KiB | 14,464 KiB |
| Bernstein box | 172 | 172 |
| 초월 prefactor box | 170 | 170 |
| 별도 ordinary-energy joint jet | 2 | 2 |
| 영폭 잔차 조립 | 1 | 1 |

각 main에서 물리 영역의 32 cell×5 미분 차수=160 enclosure가 있고, 잔차·교차 대조·일반 대수 검사가 나머지 카운터를 이룬다. 두 보존 지점에서 k,k′,k″,k⁽⁴⁾를 별도 ordinary-energy Taylor 표현과 교차 대조했다. 두 수식 경계의 overlap은 구현 대조 근거다. 전체 구간의 정당성은 앞 절의 Bernstein 및 interval 포함 증명에 있다.

두 raw JSON은 각각 959,245 byte이고 **바이트 단위로 동일**하다. 공통 SHA256:

```text
98b23330410982d6c09a31f1e8b6e431396a9fdfe71b61acf080de2d9183d6aa
```

각 실행의 실제 기록은 `evidence/run_ledger/`, 합산·복원 기록은 `EXECUTION_RECEIPT.json`과 `RESTORE_INPUT_RECEIPT.json`에 있다. 누적 main=2, Bernstein=344, prefactor=340, joint jets=4, 잔차 조립=2다. **first1/1 + replay1/1은 모두 사용했다.** PHYS33 예산은 SPENT이며 추가 실행 예산으로 재해석하지 않는다. PHYS32 및 다른 캠페인의 기존 예산도 재설정하지 않았다.

새 root search, 유한 폭 quadrature, 과거 과학 프로그램 import·main·suite, native, gas IVP, NCP는 모두 0회다. 같은 호스트에서의 replay는 경로 복원·재현성 검증이며 별도 물리 데이터나 독립 플랫폼 검증으로 세지 않는다. 실행 환경은 Python 3.12.14 / libmpdec 4.0.0이다.

## 7. 독립성·출처·후속 연구

대수·Fraction 후보 작성은 `/root/polynomial_theory`, 실제 interval 코드·실행·root tube 연결은 `/root`가 맡았다. `/root/continuity_audit`는 read-only 연속성 및 원본 audit을 수행했다. 최종 decision reviewer `/root/decision_review`는 후보 생성과 검증 설계에 참여하지 않은 별도 에이전트이며, 새 과학 실행 없이 동결된 결과·코드·증명·원시 입력·기록을 검토한다. 같은 모델·호스트·출처를 공유하는 NONBLIND 검토라는 한계를 명시한다. owner self-review를 독립 판정으로 표시하지 않는다.

다음 작은 연구 단위는 **하단 분지에 대한 별도 고정 커널 패킷·기울기·근 tube 인증**이다. PHYS33의 상단 분지 결과를 상속하고, 하단 분지의 정확한 A·저장 중심·기하·에너지 구간을 원본에서 새로 확인하여 실행 전 계약을 만들어야 한다. 두 분지의 프로파일 이동이 각각 음수여도 그 차이인 gap 이동의 부호는 자동으로 정해지지 않는다. gap 명제는 이후 별도 공통 경계가 필요하다. 후속 인계는 `../next/PHYS34_NEXT_HANDOFF_KO.md`에 보존한다.

외부 반영은 기존 PR #83의 같은 branch에 새 `docs/fastest_track_chat/REI-PHYS33-20261012/` 경로만 추가하는 범위다. 실제 반영 여부와 commit은 `../publication/PUBLICATION_RECEIPT.json`의 원격 확인 결과를 따른다. 기존 source·경로, PR 본문·draft·unmerged 상태를 유지한다. PR 링크: [rei_bianchi #83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83).
