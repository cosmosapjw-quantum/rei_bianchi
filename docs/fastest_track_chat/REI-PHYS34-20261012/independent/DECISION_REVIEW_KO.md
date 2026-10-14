# PHYS34 독립 최종 결정 검토

**최종 판정: PROMOTE_SCOPED — 제한된 고정모델 명제 8개를 채택하고, 두 분지 gap 및 물리 승인 명제 2개는 HOLD로 유지한다. 치명적 결함 0건, 필수 수정 0건이다.**

검토자: `/root/decision_review`, `SOLE_INDEPENDENT_FINAL_DECISION_REVIEWER`. 모델은 상속한 GPT-6 Astra Pro다. 이번 하단 후보 작성자 `/root`, 이론 기여자 `/root/polynomial_theory`와 구별되는 별도 agent이며, PHYS34 후보 생성과 검증 설계에 참여하지 않았다. 검토는 비맹검이고 같은 모델·호스트·원자료 계보를 공유한다. 독립 물리 데이터 또는 별도 산술 backend 검증의 가산점은 0이다.

## 1. 판정 대상을 고정했다

판정 대상은 [최종 후보 동결](../evidence/FINAL_CANDIDATE_FREEZE.json)의 다음 identity다.

```text
SHA256 dec24ed482e659aecc451562141921849e41407dc475d6763ec4ac13ee35c3b6
payload 61 files / 3,917,681 bytes
frozen UTC 2026-10-12T00:33:17.461570+00:00
```

61개 파일의 실제 byte 수와 SHA256을 모두 대조했고 불일치가 없었다. 동결의 `files` 목록과 `sha256` 맵도 일치한다. 실행 전 고정한 33개 파일의 identity가 최종 후보에서도 유지된다. 독립 판정·닫힘·실제 출판 영수증은 이 후보에 덧붙이는 문서이며, 후보나 과거 원시 결과의 내용을 사후 변경하지 않는다.

이 판정이 채택하는 대상은 정확한 원 입력으로 정의된 source-real H I 응답 커널, 하단 분지, 지정한 두 프로파일, 폭 `0≤δ≤0.001 eV`, 전체 저장 하단 W의 반경 `0.25 eV²` tube다. 근 유일성은 이 tube 안의 명제다. source 시작 commit `06e65fa291685fcec0e012ee84d291b356922748` 및 scientific subtree `cb69b4736dd046e4675557577eb8e0ead037d1f3`의 연결 근거는 고정된 [SOURCE_MANIFEST](../SOURCE_MANIFEST.json)와 [연속성 감사](../evidence/CONTINUITY_AUDIT.json)다. 리뷰어가 원격 저장소를 새로 실행하거나 물리 검증한 것으로 표현하지 않는다.

## 2. 실행 근거를 직접 읽고 서로 대조했다

[첫 원시 인증서](../evidence/CERTIFICATE_FIRST.json)와 [복원 원시 인증서](../evidence/CERTIFICATE_REPLAY.json)는 각각 1,028,560 byte이며, 직접 byte 비교와 SHA256 비교가 모두 일치했다.

```text
9b576de7e6079b5a9a3352f6049f550fde13646dda8a1d36022febcf6e11ccf4
```

| 항목 | first | restored replay |
|---|---:|---:|
| raw 상태 | PASS_SCOPED | PASS_SCOPED |
| 통과 검사 | 25/25 | 25/25 |
| raw failure | null | null |
| Bernstein / prefactor box | 170 / 170 | 170 / 170 |
| ordinary-energy joint jet | 2 | 2 |
| 조립한 zero-width 잔차 | 1 | 1 |
| child main wall time | 0.941498452 s | 0.895135447 s |
| child main CPU time | 0.940994652 s | 0.892254564 s |
| child 보고 peak RSS | 16,896 KiB | 16,768 KiB |
| parent가 관측한 child returncode | 0 | 0 |
| timeout | false | false |
| 별도 stderr 크기 | 0 byte | 0 byte |
| 저장된 exec tool exit_code | 0 | 0 |

이 표의 근거는 [실행 합산 영수증](../evidence/EXECUTION_RECEIPT.json), `evidence/process/`의 first/replay stdout·stderr·process receipt·exec envelope와 `evidence/run_ledger/`의 6개 원시 ledger다. process receipt의 stdout/stderr byte 수와 SHA256을 실제 파일과 대조했다. 저장된 tool envelope의 출력 JSON은 해당 process receipt와 같고, stdout JSON은 finished ledger와 같다. wrapper command와 시작 marker의 freeze hash도 일치한다. 따라서 이번 PHYS34에서는 별도로 보존된 실제 종료·출력 기록까지 검토할 수 있다. 리뷰어가 당시 child를 직접 실행하거나 별도 호스트에서 관측한 것은 아니다.

[복원 영수증](../evidence/RESTORATION_RECEIPT.json)의 ZIP은 34개 member로, 사전 동결 33개 파일과 freeze 자체를 정확히 포함한다. 중복 member나 내용 차이가 없고, 별도 `phys34_restored` 경로의 33개 고정 파일 해시도 모두 맞았다. 두 raw가 같다는 것은 이 경로 복원과 같은 호스트 구현의 재현성 근거다.

main 시간, parent wait 시간, tool이 보고한 `wall_time_seconds`는 서로 다른 측정 필드로 보존되어 있다. 이들을 하나의 시계값으로 섞지 않았다. 첫 실행 1회와 복원 replay 1회는 cap 안에서 끝났고 예산은 **SPENT**다. 이 검토에서 과학 main, kernel 평가, root 탐색, quadrature, jet 계산, 일반 산술 검사 반복은 모두 **0회**다.

## 3. 입력과 실제 분산의 의미가 유지된다

원 PHYS29의 `second_order.jet_chain.lower_root.response_s-4`를 직접 읽어

\[
A_-=-3.2582515\times10^{-137}\ \mathrm{s}^{-4}\ne0
\]

가 계약·raw와 정확히 일치함을 확인했다. `constants.stored_PHYS26_root_strings.lower_root`의 전체 W 문자열도 정확히 같은 유리수로 보존되어 있다. PHYS22의 `J_nonphoto[2][0]`, `[2][3]` 문자열과 PHYS29의 J 복제 키가 일치한다. 이 입력들을 원자 물리의 오차 없는 측정값으로 승인한 것은 아니다.

원 binary64 리터럴의 값은 정확한 유리수로, 직렬화된 J와 W 및 선언한 기하·A는 정확한 십진 유리수로 해석한다. 후속 곱과 함수는 그 위의 정확한 실수 함수다. 원 rounded prefactor, native 산술 연산 순서, 상단 A, A=0 또는 새로 계산한 F₀를 대체 정의로 쓰지 않았다. proper seconds, 명시한 c, 기존 metric convention과 단위도 유지된다. 이 의미는 [계약](../PHYSICS_CONTRACT.json), [하단 유도](../contributions/theory/LOWER_BRANCH_DERIVATION_KO.md) 및 원 source 발췌에 고정되어 있다.

하단에서는

\[
r=R-\delta,\quad R=6.58\ \mathrm{eV},\quad
V=W-\delta^2/3,\quad e=b-\delta,\quad x=m-V/r,
\]
\[
p=V/(r^2+V),\qquad q=r^2/(r^2+V).
\]

이 두 중심의 평균은 m이고 중심 분산은 V다. 평균 0, 분산 1/3인 독립 프로파일 변위를 더하면 실제 분산은 정확히 W다. 두 프로파일의 이차 모멘트가 같으므로 같은 실제 W에서 중심과 확률도 같다. 이 연결이 빠지면 뒤의 응답 차이와 근 차이는 다른 물리량의 비교가 된다. 후보에는 해당 연결이 명시되어 있고 구현도 이를 그대로 사용한다.

전 tube의 exact feasibility 비교는 양의 확률과 지원 조건을 보장한다. 두 패킷과 같은 z에서 두 패킷을 잇는 모든 보간점이 J=[14.35,24.58] eV에 포함된다. 도함수 부호를 확인한 영역이 실제 기울기 적분 경로까지 덮는다.

## 4. 연속 영역 인증의 수학과 산술을 검토했다

`rational_kernel.py`의 exact Fraction 식을 정적으로 검토했다. 미분 numerator는

\[
T_{a,b}Q=[a+(a+b)\zeta]Q+\zeta(1+\zeta)Q'
\]

이고, ordinary energy 미분마다 \(\zeta\) 지수가 2, \(1+\zeta\) 지수가 1 줄며 multiplier가 \((2B)^{-1}\) 추가된다. \(\mathscr D^2+3\mathscr D\)의 공통식에서 `6(1+ζ)` 항이 필요한 이유와 구현이 일치한다. 최종 차수는 8+n≤12로 선언한 cap 16 이하다. exact affine 변환과 Bernstein 계수 변환은 다항식 항등식이며, 비음수 basis의 합이 1이므로 최소·최대 계수는 cell 전체의 값 범위를 덮는다.

기존 JSON의 5개 차수별 32개 exact cell을 해석하여 순서, 양끝, gap 없는 연결을 확인했다. 각 order의 전역 range는 실제 cell enclosure 극값과 일치한다. order 2와 4의 모든 기록된 Bernstein 계수가 양수이고, 모든 외부 인자 하한도 양수다. 기록된 exact cell과 다시 Decimal로 넓힌 prefactor/표시 구간은 구별되어 있다. 다항식 경계는 exact cell의 경계이고, 외부 인자는 그 cell을 포함하는 조금 넓은 구간에서 감싼다.

`outward_decimal.py`는 기본 사칙연산에서 FLOOR와 CEILING 문맥을 구별하고, 유리수 입력을 먼저 outward로 감싼다. 음수 변환·절댓값은 정확한 Decimal copy 연산을 사용한다. ln·exp·sqrt는 문서화된 correctly rounded 근접 결과를 인접 표현값으로 한 번 더 확장한다. 양의 밑 실수 거듭제곱은 exp/log interval 합성으로 계산하며 `Decimal.power`의 근접값을 엄밀한 endpoint로 가정하지 않는다. 근거는 [Python Decimal 공식 문서](https://docs.python.org/3.12/library/decimal.html)와 [libmpdec 산술 문서](https://www.bytereef.org/mpdecimal/doc/libmpdec/arithmetic.html#square-root)다. 이 공식 문서의 의미는 선행 PHYS33 검토에서도 확인했으며 helper 두 파일은 동일한 바이트다.

이 감사는 Decimal/libmpdec의 문서화된 산술 의미를 전제로 한다. 라이브러리를 형식 검증하거나 별도 backend에서 확인한 것은 아니다. 이번 실행 기록의 runtime은 Python 3.12.14/libmpdec 4.0.0이다. PHYS33의 완료된 일반 helper 검사 6개는 원 raw·독립 decision·helper SHA256에 묶여 상속되며, 새 일반 검사 실행은 0회다. 이 리뷰어가 PHYS33의 최종 리뷰도 수행했다는 의존성을 숨기지 않는다.

새 하단 원시 경계를 바깥쪽으로 줄여 표시하면 다음과 같다.

| 양 | 보수적 경계 |
|---|---:|
| k″ | 1.14150×10⁻⁶⁶ ≤ k″ ≤ 4.49452×10⁻⁶⁵ s⁻⁴ eV⁻² |
| k⁽⁴⁾ | 1.28077×10⁻⁶⁷ ≤ k⁽⁴⁾ ≤ 8.10157×10⁻⁶⁶ s⁻⁴ eV⁻⁴ |
| 기울기 하한 κ | ≥5.70750×10⁻⁶⁷ s⁻⁴ eV⁻² |
| 기울기 상한 K | ≤2.24726×10⁻⁶⁵ s⁻⁴ eV⁻² |

실제 grid는 H I cutoff의 위, He I cutoff의 아래에 엄격하게 남는다. 가열 offset χ는 cutoff와 구별된다. [수치 요약](../report/NUMERICAL_SUMMARY.json)의 14개 표시값을 원 endpoint와 대조했고 모두 바깥 방향이 맞았다. 표의 짧은 상수를 다시 조합하여 원 margin이나 근 차이 계수를 재계산한 것은 아니다.

## 5. 잔차에서 존재로, 존재에서 엄격한 순서로 이어진다

하단에서 \(D=x-e<0\)지만

\[
F_{\alpha,W}=\frac{g(e)-g(x)+Dg'(x)}{D^2}
=\int_0^1t\int k''((1-t)e+tx+\delta z)\,d\alpha(z)dt
\]

다. D<0 때문에 추가 음의 부호가 붙지 않는다. 따라서 전체 tube에서 \(0<\kappa\le F_{\alpha,W}\le K\)이고 각 응답은 W에 대해 엄격히 증가한다.

저장 W를 exact root로 가정하지 않고 전체 문자열로부터 \(x_0=m-\widehat W/R\)를 재구성했다. 실제 잔차는

\[
F_0(\widehat W)-A_-
\in[-1.396128542248,-1.396128540852]\times10^{-142}\ \mathrm{s}^{-4}
\]

로 음수이며 0을 포함하지 않는다. 과거 `u_zero`는 수식 대조의 노드로만 쓰였고 이 exact x₀를 대신하지 않았다.

확률 단조성에는 별도의 조건 \(\widehat W>\mu_2Rd\)가 필요하다. 코드는 이를 exact 비교로 확인했다. 따라서 \(p_0\le p_\delta\le p_d\), \(q_\delta\le q_0\)이고, 중심 이동과 평균 0 프로파일의 평활화 나머지를 묶은 B가 전 폭에 공통이다. 원 90자리 경계에서

\[
B\le9.73485\times10^{-68}\ \mathrm{s}^{-4},\qquad
\kappa\eta-(B+\epsilon_r)\ge4.53392\times10^{-68}\ \mathrm{s}^{-4}>0.
\]

즉 tube 양 끝의 응답이 A를 사이에 둔다는 사실을 근 존재에 앞서 증명했다. 연속성과 엄격한 단조성으로 각 허용 폭·프로파일마다 tube 내부의 근이 하나씩 존재한다. 이 단계는 근 존재를 미리 가정하는 순환 논증이 아니다. 원 계산의 상한은

\[
|W_{-,\alpha}(\delta)-\widehat W|\le0.170563\ \mathrm{eV}^2<0.25\ \mathrm{eV}^2,
\]
\[
|W_{-,\alpha}(0)-\widehat W|\le2.44613\times10^{-76}\ \mathrm{eV}^2.
\]

B·ρ·ε/κ의 raw interval은 각각 계산한 경계값을 감싼다. 그 lower endpoint가 실제 미지의 근 이탈에 대한 양의 하한이라는 의미가 아니다.

프로파일 차이에 대해 \(Q(z)=(1-z^2)^4\), \(h_p-h_u=Q^{(4)}/768\), \(\int Q=256/315\)이고 끝점의 0–3차 경계항은 모두 0이다. 따라서 정확하게

\[
\int k(y+\delta z)(h_p-h_u)dz
=\frac{\delta^4}{945}\int k^{(4)}(y+\delta z)\,d\pi(z),
\qquad d\pi=\frac{315}{256}(1-z^2)^4dz.
\]

양의 확률측도와 k⁽⁴⁾의 양의 경계, 이미 존재한 두 근 사이의 양의 평균 기울기를 결합하면

\[
-\frac{M_4}{945\kappa}\delta^4
\le W_{-,p}-W_{-,u}
\le-\frac{m_4}{945K}\delta^4<0
\]

가 모든 0<δ≤0.001 eV에서 성립한다. 원 Csmall.lower와 Clarge.upper를 바깥쪽으로 단순화한 최종 표시가

\[
\boxed{-0.0150208\,\delta^4\le W_{-,p}-W_{-,u}
\le-0.00000603100\,\delta^4<0}
\]

다. 두 계수의 단위는 eV⁻²다. δ=0.001 eV에서는

\[
\boxed{-1.50208\times10^{-14}\le W_{-,p}-W_{-,u}
\le-6.03100\times10^{-18}\quad\mathrm{eV}^2.}
\]

δ=0에서는 두 응답이 같고 tube의 유일근도 같다. 양의 폭에서의 엄격한 순서는 유한 폭의 정확한 Peano 항등식에 근거한다. Taylor 선도항만으로 부호를 추정한 결과가 아니다. 상세한 원 조건과 식은 [근 tube 증명](../report/ROOT_TUBE_PROOF_KO.md)에서 확인할 수 있다.

## 6. 각 claim의 최종 disposition

| Claim | 최종 결정 | 검토 이유 |
|---|---|---|
| C34.1 | PROMOTE_SCOPED | exact lower A, 전체 W, 원 J와 source-real 해석이 일치한다. |
| C34.2 | PROMOTE_SCOPED | 실제 W와 중심 V를 구별하고 전체 tube의 확률·지원·보간 영역을 덮는다. |
| C34.3 | PROMOTE_SCOPED | J 전체에서 k″의 양의 하한이 exact Bernstein와 outward 인자로 감싸진다. |
| C34.4 | PROMOTE_SCOPED | 같은 연속 영역에서 k⁽⁴⁾의 양의 하한이 감싸진다. |
| C34.5 | PROMOTE_SCOPED | 저장값을 근으로 가정하지 않고 비영 잔차와 정확한 A의 근 거리 상한을 보존한다. |
| C34.6 | PROMOTE_SCOPED | B+ε<κη가 전 폭의 존재와 tube 안 유일성을 먼저 보장한다. |
| C34.7 | PROMOTE_SCOPED | exact Peano 표현과 양의 기울기로 양의 폭의 엄격한 quartic 근 순서를 얻는다. |
| C34.8 | PROMOTE_SCOPED | 실제 first/replay raw, 복원 archive, 종료·출력 기록과 소진 예산이 일치한다. |
| H34.1 | HOLD | 두 분지 이동 차이와 공통 A의 cross-branch 정리는 인증하지 않았다. |
| H34.2 | HOLD | J·원자 fit 불확실성, 전체 coupled history와 보호된 실패 상태를 해결하지 않았다. |

원 claim 문구와 각각의 상세 근거는 [기계 판독 결정](DECISION_REVIEW.json)에 보존한다. owner 요청의 disposition을 자동 복사한 것이 아니라 위 입력·수학·구현·실행 기록과 claim 범위를 실제로 대조한 결정이다.

## 7. 실패 보존과 판정의 한계

읽은 first/replay 과학 원시 결과에는 실패가 없으며 `failure=null`이다. 리뷰 과정의 첫 metadata 조회에서 리뷰어가 endpoint 필드를 `lo`로 잘못 가정해 `KeyError: 'lo'`와 exit_code 1을 얻었다. 실제 스키마는 `lower/upper`였다. 기존 JSON을 올바른 키로 다시 읽어 조회를 마쳤다. 이 오류는 후보 실행 실패가 아니며 후보 코드·결과를 고치거나 과학 실행을 추가하지 않았다. 해당 조회 오류와 범위를 이 문서와 JSON에 남긴다. 일반 파일 탐색 중 아직 없는 `phys34/claims` 경로를 지정한 read-only `rg` 경고도 있었고, 이후 실제 `evidence/CLAIM_LEDGER.json`을 읽었다.

`claim_ceiling.lower_branch=TARGET_NOT_YET_EVALUATED`는 immutable pre-run 계약 snapshot의 복사다. 실제 실행 결과는 raw의 status·checks·certificate에 있고, 현재 최종 disposition은 이 독립 결정에 있다. 서로 다른 시점의 라벨을 덮어써 과거 기록을 없애지 않았다. 기존 PHYS33의 process evidence 미보존 한계 역시 PHYS34의 새 캡처로 소급 해소한 것으로 쓰지 않는다.

같은 모델·host·입력·Decimal backend의 의존성은 남는다. 수식 표현 두 개가 맞고 복원 raw가 같다는 사실은 외부 원자 데이터의 독립 검증이 아니다. 매우 작은 수학적 근 오차나 프로파일 차이를 원자 fit 또는 관측 정밀도로 해석하지 않는다. 모든 분포의 전역 최적성, 더 넓은 폭·W 영역의 근 유일성도 채택 범위가 아니다.

보호 상태는 다음과 같다.

```text
Physical HOLD
[160,161] FAIL; tick160
auxiliary escape FAIL
HH/RCT/CR OFF
precision atomic PARKED
production source/default/runtime changes0
```

다음 [PHYS35 인계](../next/PHYS35_NEXT_HANDOFF_KO.md)의 joint branch comparison은 **PROPOSED / NOT_RUN / NOT_CERTIFIED**다. 서로 다른 A₋, A₊를 보존한 root separation과 새 공통 A의 문제를 구별해야 한다. 이번 판정은 새 과학 실행 슬롯이나 원격 변경 권한을 만들지 않는다. 출판은 현재 사용자 권위와 고정된 publication plan의 범위에서 root가 처리하고, 실제 반영 여부는 후속 detached receipt로 기록한다. 이 리뷰어는 후보·production·원격 상태를 수정하지 않았고 허용된 독립 판정 두 파일만 작성했다.
