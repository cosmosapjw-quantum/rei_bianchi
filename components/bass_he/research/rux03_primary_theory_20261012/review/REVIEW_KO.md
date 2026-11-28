# 독립 최종 검토 — HERE_RUX03_PRIMARY_THEORY_03

## 판정

**PROMOTE_SCOPED_THEORY.** 최종 v2의 R00은 기존 소스의 근거로, T01–T07은
명시된 가정 아래의 이론 구성으로 채택한다. 이론 단위의 과학적 완료를 막는 오류나
해결되지 않은 중대한 지적은 없다. 실제 공통 provider가 implicit point와
interval/root에서 소비된다는 구현·실행 근거는 다음
`HERE_RUX03_PRIMARY_PROVIDER_03`의 의무다.

검토자는 `/root/dropbox_checkpoint`다. 후보 유도·코드와 수용기준을 작성하지
않았고 후보 파일을 수정하지 않았다. 원전·보존 소스 조사, 식의 독립 대조,
witness 범위 지적과 기존 guard의 확인, 검토 기록과 byte 비교를 수행했다.
과학 evaluator·native test·ODE/history는 검토자가 추가 실행하지 않았다.

최종 대상은 `CANDIDATE_FREEZE_v2.json`이다.

- SHA-256: `ecb10af4f512a9b5798da26e4c72f7d3ececfb10e29aeea9a8f32af690a60a05`.
- 29개 파일의 byte 수와 SHA-256이 모두 일치한다.
- `REVIEWED_ARTIFACTS.json`은 과학·개정 파일 29개, freeze 1개, 선택 소스 13개,
  직전 독립 판정 1개의 44개 identity와 실제 읽기 범위를 기록한다.
- 수신 소스는 rei_bianchi PR114 `a5c958c414dea41216b445c05f58df837f05cacb`,
  tree `2e96362102caa69c814d477bae5d1c0177b502f9`다. 원격 head 관측은
  `CURRENT_SOURCE.json`의 2026-10-12 14:39:47 UTC 조사를 재사용했다.

## 정리별 판단

| 주장 | 판단 | 확인한 내용과 적용 조건 |
|---|---|---|
| R00 | 기존 근거 채택 | 소스에 source-free photon 소거, 양성 H/He proposal, conservative point, 네 변수 interval/Krawczyk가 이미 있다. 기존 알고리즘을 새 성과로 계상하지 않는다. |
| T01 | 조건부 이론 채택 | prescribed source는 numerator에 한 번 들어간다. reference/proper/per-H 변환, gas 미분, photon zero-set과 reduced Schur derivative가 맞다. |
| T02 | 조건부 이론 채택 | absorption 경쟁 Jacobian, 양의 column margin, 단일 node 역함수·응답 모드와 각 극한이 유리식에서 나온다. 엄격한 부호·역함수에는 hW>0가 필요하다. |
| T03 | 조건부 이론 채택 | 공통 사건이 full 및 reduced off-root identity를 준다. 일정 row transform과 정확한 가역 야코비안에서는 Newton increment가 같다. |
| T04 | 기존 guard를 포함해 채택 | 계수 factorization이 영 population·전자수에서 정의된다. C² chain rule과 moment 미분은 공통 point/interval 계약이다. v2가 zero-rate/zero-moment guard도 명시한다. |
| T05 | 조건부 이론 채택 | endpoint-energy 사건의 유한 product rule이 history work를 결정한다. 연속 endpoint work와의 차이 및 gas 미분이 맞고, O(h²)는 매끈한 단계에서의 결론이다. |
| T06 | 수정 해결 후 채택 | 상수 witness의 범위를 한 번 소비와 population/전자수 의존성으로 좁혔다. 별도 T² companion은 열 w/ww 및 chemical/mixed 미분을 판별한다. |
| T07 | 조건부 이론 채택 | 원래 w 잔차에 w=c_v dT를 대입하면 같은 map이다. 연속 T 방정식의 별도 BE에는 같은 species BE 조건에서 c_v ΔT Δd 차이가 생긴다. |

## 핵심 식의 독립 대조

### 사건 수지, residual row와 Newton

초기 R6에서 공유 유도의 식 (6), (11)–(17), (24)–(37)을 직접 대조했다.
CI·RR·DR·photoevent와 captured kinetic moment를 같은 단위로 합하면

\[
Q+\boldsymbol b_\chi^T G+Q_{esc}=\sum_{iq} E_q P_{iq}
\]

가 사건별로 상쇄된다. photon과 escape를 복원한 residual에는

\[
F_E=F_w+\boldsymbol b_\chi^T F_v
\]

가 root 밖에서도 성립한다. full residual에 남은 photon·escape row를 생략한 채
이 식을 적용하지 않는다는 조건도 적절하다. binding coefficient가 고정되어 row
transform은 일정하다. 가역 Jacobian의 정확한 Newton 증분이 같다는 결론은 맞다.
두 fixed-point proposal의 반복 경로, line search나 임의 residual norm까지 같다는
주장은 없다.

photon Schur 비교는 photon equation을 만족하도록 재구성한 상태에서 한다.
분모를 이전 gas 값에 고정한 반복 단계는 조건부 선형 풀이이며, endpoint gas의
변화를 모두 미분한 Schur Jacobian과 구별된다. 이 구분은 공유 유도에 명시되어 있다.

실수 대수에서 R^E=R L^-1로 행 변환을 상쇄하는 사실과, 구간 entry를 독립적으로
평가해 생기는 dependency widening은 다르다. 후보는 기존 thermal residual을
canonical interval field로 유지한다. 이전 root certificate를 새 map에 이름만으로
옮기지 않는다. thermal proposal의 warm-domain budget도 특정 candidate의
필요충분조건이며, 전체 box 자기 사상이나 전역 수렴으로 쓰지 않는다.

### 계수·모멘트와 경계

primitive는 n_H m(v)e(v)c(T)로 factorize된다. affine population과 전자수의 곱,
T=τw/d의 1·2차 미분을 적용한 식이 정확하다. population=0에서 rate를 population으로
나누지 않는다. 전체 세 상태 He 생성자의 비대각 비음수성과 column sum=0는 기존
양성 resolvent를 설명한다. 계수를 고정한 chemistry 단계의 성질이며 전체 비선형
gas/thermal map의 전역 해 존재를 새로 보장하지 않는다.

현재 RR moment를 α에서 구성하면

\[
\kappa''=k_B\left(5\alpha'+\frac{11}{2}T\alpha''+T^2\alpha'''\right)
\]

가 필요하다. 후보는 α''' 의존성을 남겼고, 독립적인 C² moment를 공급하는 경우와
현재 analytic moment를 Jet으로 평가하는 경우를 구별한다. f64 moment를 Jet 상수로
감싸는 구현은 이 계약을 충족하지 않는다. point 경계에서 primitive가 정의된다는
사실도 현재 strictly interior interval/root domain을 확장한 것으로 쓰지 않는다.

### photon allocation·단위·geometry

최종 photon 문서의 erg 에너지 E와 eV callback 인자 e는 E=ε_eV e로 구별된다.
`source_bound_interval.py`의 characteristics·stage를 읽어 provider에는 eV가
들어가고 source에는 weight/R³가 들어가는 대응을 확인했다. `axisym_coupling.rs`의
thermal dilution 및 photon shear work도 연속 수지와 일치한다. 두 파일의 SHA-256은
photon 문서에 적힌 값과 같다.

allocation A=hW λ_vec/D의 Jacobian은 유한 공급에서 채널 사이 경쟁과 총흡수의
증가를 분리한다. 역함수는 독립 opacity의 한 node 문제에 해당한다. 실제 여러
node는 같은 세 분율을 공유한다는 consistency 조건을 문서가 보존한다. source가
있는 큰 h, 고정 h에서 큰 opacity, transparent 경계의 조건도 구별되어 있다.

유한 history 에너지에서

\[
\Delta(EN)=E^+\Delta N+\Delta E\,N^-
\]

이므로 W_γ,geom=−ΣΔE N^-가 endpoint-energy BE microphysics와 정확히 닫힌다.
N^-는 birth 전 history의 incoming reference photon이다. source를 primary 입력에
미리 합산해도 history work의 N^-와 그 입력을 구별하도록 구현 계약이 정한다.
ΔE<0인 redshift에서는 work가 양수다. 기존 continuous RHS/DOP853에 BE 전용
correction을 추가한 결과로 주장하지 않는다.

## 지적과 최소 수정의 해결

### R6-F01 — 상수 witness의 판별 범위

`R6_REVIEW_INITIAL.json`은 최초 공유 문서 SHA
`def8a428123e477ae2325d35899713ce3bef6a38a68b0e0d4c329e4a79f5b499`와 지적을
보존한다. 상수 ρ,η이면 δκ의 온도 의존성이 없으므로 이 witness만으로 kinetic
coefficient의 T 미분 누락을 검출할 수 없다. 식 자체의 오류는 없었으며 최소 수정은
설명 범위를 한 번 소비와 population/전자수 미분으로 좁히는 것이었다.

최종 §6과 CLAIMS T06은 범위를 정확히 좁혔다. 저자는 별도로
ρ(T)=ρ_star(T/T_star)² 및 δκ=ε_eV ηρ(T)를 구성했다. 검토자가 companion을 설계하거나
실행하지 않았다. 고정 분율에서 T∝w이므로

\[
\partial_w\delta F_w=2h\eta r_\delta/w,
\qquad
\partial_{ww}\delta F_w=2h\eta r_\delta/w^2
\]

이며 양의 내부 상태에서 두 값은 양수다. 직접 primitive perturbation,
conservative row·escape 변화, chemical gradient/Hessian과 mixed derivative도
추가 스크립트와 일치한다. 실제 9-group 출력까지 확인하여 **해결됨**으로 판정한다.
이는 manufactured primitive pair의 판별 기대값이며 새로운 atomic fit의 승인이 아니다.

### R6-F02 — 기존 event-bundle guard의 전달

저자가 최종 소스 대조에서 zero-event/zero-kinetic-power guard의 명시를 제안했고,
검토자가 실제 `CaseAEventBundle::into_ledger`의 RR·DR 조건을 확인했다. 일반적인
비음수 C² 계수만으로는 α=0, κ>0 같은 pair가 배제되지 않는다. 현재 FT03와 양의
witness는 이미 guard를 만족하므로 현재 식의 오류는 아니다.

최소 v2는 SHARED §4와 CODING 계약에 α=0⇒κ=0, δ=0⇒ζ=0를 명시한다. 두 문장
교체를 역으로 적용하면 각각 v1의 SHA-256이 정확히 복원된다. 나머지 변화는 index의
hash 갱신과 diff/수정 기록 2개 추가다. REPORT·CLAIMS·과학 식·세 Wolfram input과
raw/summary는 바뀌지 않았다. 기존 guard의 전달 조건으로 **해결됨**을 확인하며,
새로운 과학 계산은 필요하지 않다.

## 실제 근거와 계산 범위

| 기록 | 확인 | 역할 |
|---|---|---|
| shared provider Wolfram | 19개 group literal True, raw decoded JSON과 summary 모든 필드 일치 | 사건·잔차·미분·T 좌표 대수 보강 |
| photon Wolfram | 19개 named group True, raw association과 summary 이름·값 일치 | photon 수지·allocation·변환·product rule 보강 |
| temperature companion Wolfram | 9개 group literal True, raw decoded JSON과 summary 모든 필드 일치 | 새 perturbation과 1·2차 미분 보강 |
| 최초 SymPy 시도 | import 실패, algebraic check 미도달 | 환경 의존성 기록; 성공 계산으로 계상하지 않음 |

세 성공 실행의 19+19+9=47은 expression group 수다. 겹치는 항등식도 포함하므로
새 정리나 native test 47개를 뜻하지 않는다. 기호 유리식 검산이 부호·domain·smoothness·
source ownership의 증명을 대신하지 않는다. 이 조건들은 유도와 소스를 별도로 읽어
판단했다.

직전 EVENT_BRIDGE_02의 176 native tests, primitive 비교와 단일 production interval은
변경 없는 conditional path에만 재사용한다. 이전 독립 decision SHA는
`4df64a70f77ccf698ca31a1e7e4f95a5704a1ee70e5450162649c2bb4953d153`이다.
이번 신규 native build·test·ODE/history는 모두 0이다.

원전과 읽은 페이지·식은 `LITERATURE_MAP.md`에 보존했다. C2-Ray/Friedrich의
계수 고정과 반복, Rosdahl의 photon update, Reynolds의 Schur 대수와 lagging,
Blanes–Iserles–Macnamara의 양성 BE resolvent는 기존 구조의 근거다. Friedrich의
OTS와 현재 Case A escape를 혼합하지 않았다. 원전 전체 읽기나 전역 독창성 조사로
확대하지 않았다.

## 후속 의무

`CODING_CONTRACT_KO.md`의 callsite 묶음은 실제 소스와 맞는다. 다음 코딩 단위는
한 계수·사건 선택이 ordinary point, conservative point, raw/endpoint, interval/root와
paired caller에 전달되도록 해야 한다. root centre의 ordinary point와 paired caller의
conservative point·root 연결을 유지하며, 새 field의 실제 한 번 소비·미분 witness와
기존 root gate를 평가해야 한다.

이어서 RUX02 physical input과 RUX03 rate-domain/provider closure를 결합한 RUX04
scenario lock, 그 뒤 RUX05로 진행한다. 이 판정은 owner node 상태를 변경하지 않는다.
새 Case B/OTS·CR/RCT/HH, 전역 수렴·물리 closure·continuum certification은 이번
완료 범위에 들어 있지 않다. 별도 science rerun·source snapshot·수용 오차 변경을
요구하지 않는다.

## 판정 identity

- `DECISION.json`: `620ee3490cdac5fadb36b087b5cfb17def8890e27d898b6ec53cf87fd8c7f3a2`.
- `REVIEWED_ARTIFACTS.json`: `027f36973197eda8e85b59cd439974c3e80354c2e8456fe70ab20686d3cb993e`.

판정은 위 v2 freeze에 적용된다. 게시·전달 metadata는 추가할 수 있으며, 고정
과학 파일이 바뀌면 이 identity의 판정과 구별해야 한다.
