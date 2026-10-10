# REI-PHYS21 독립 최종 판정

검토자: `/root/phys21_decision`. 별도의 최종 decision reviewer이며 후보 생성과 검증 설계에 참여하지 않았다. 부모의 작업 문맥을 전달받은 검토이므로 blind review를 주장하지 않는다. 아래 판정은 고정된 통합 보고서와 직접 읽은 원본 증거에 한정한다.

## 판정

**PROMOTE — 명시한 continuum 2차 커널·부호 진단·source-bound 인과적 기체 응답의 연구 보고와 다음 이론 루프로 승격한다. Physical admission은 HOLD다.**

대상은 `PHYS21_REPORT_KO.md`, 30,174 bytes, SHA256 `59fca954d998f9ffd5af2ed857ae15992f24c9779a77e9c7ba099d058990ab7a`다. 연구계약 SHA256은 `3d249e2915a4954268d6adee4c213a3d822d6ce31ab01466437723c1f836da42`다. 검토한 코드·기여문서·수치 결과의 해시는 동반 `DECISION_REVIEW.json`에 기록했다. 보고서가 변경되면 이 판정이 수정된 bytes에 자동 적용되지는 않는다.

현재 범위에서 승격을 막는 수학적·단위상·근거상 결함을 발견하지 못했다. 이 판정은 실제 evolving-gas의 finite-time 계수, native solver의 정확도, physical gate의 해소 또는 향후 publication의 성공을 인증하지 않는다.

## 1. 독립성과 검토 범위

Canonical GPT-6 Astra harness v4.0.0의 core, independent decision gate, phase gates와 stop rules를 읽었다. 후보 기여자인 `/root/phys21_tensor`, `/root/phys21_source_gas`와 owner로부터 분리된 새 검토자로서 다음을 직접 검토했다.

- 고정 연구계약, 통합 보고서 전체, 두 기여 문서 전체 및 기체 functional JSON.
- 세 diagnostic의 원본 결과 JSON, 실제 실행 receipt, 세 Python 검산 코드.
- Source binding 및 보존된 remote Git 응답. 기여 디렉터리에 materialize된 Rust source 7개의 SHA256/Git blob을 직접 재계산해 일치를 확인했다.
- `ft03_controlled.rs`의 CI/RR/two-DR 및 thermal/escape RHS, `coupled_primary.rs`의 온도 변환·zero-photon 호출·primary event/heat 주입, `ft03_rates.rs`의 관련 온도 의존 fit을 source와 수식 사이에서 대조했다.
- Local derivative의 최초 v1과 수정본 코드 차이, 양쪽 결과·실행 기록.

별도의 과학 계산 재실행은 하지 않았다. 이미 서로 구별되는 실제 검산이 있고 추가 실행으로 해결해야 할 구체적인 중대 위험을 발견하지 못했기 때문이다. 검토자가 한 byte identity 확인은 과학 재현이나 native 실행으로 세지 않는다. PHYS19/20의 닫힌 proof, gas IVP, native history도 실행하지 않았다. 문헌 검색은 반복하지 않았으며 새 결과를 기존 논문의 정리로 귀속하지 않는 보고서의 출처 구분을 확인했다.

## 2. 핵심 수학 판정

### 2.1 계수, 각도 평균, 인과적 memory

보고서 식 (4)–(8)은 physical birth 방향을 고정한 metric energy의 두 번째 로그 변분과 구면 Q2/Q4 contraction을 함께 사용한다. 여기서

\[
\langle\delta^2F\rangle=\frac2{15}(D^2+3D)F_0\,\operatorname{tr}A^2
\]

이며, 보고서가 출력하는 \([\epsilon^2]\) 계수는 이 둘째 미분의 절반이다. Product rule 식 (11)에 opacity memory를 넣으면 식 (12)의 전체 prefactor가 \(1/15\)가 되는 것이 일관된다. Endpoint–opacity covariance의 음의 부호, survival variance와 mean-opacity curvature의 구별도 맞다. \(A,M,V\)가 무차원이고 각 항이 endpoint weight \(L\)의 단위를 유지한다.

Birth와 endpoint가 같을 때, shear history가 0일 때, 자유 광자 에너지일 때의 극한을 확인했다. 고정 principal axes, trace-free deformation, \(\epsilon\)-independent mean expansion/source, threshold-separated \(C^2\) 응답은 결과에 필요한 조건이다. 보고서는 이를 Einstein-backreacted 전체 2차 계수로 승격하지 않는다.

### 2.2 Source Jacobian과 좌표 표현

Physical-birth 적분에 \(J_b\)를 다시 곱하지 않는 정의와 fixed-q 표현의 \(J_b\) 한 번 사용이 일치한다. 식 (14)의 평균은 \((4/3-20/15)\operatorname{tr}(CX)=0\), \((30/15-2)L_0\operatorname{tr}C^2=0\)으로 사라진다. Birth 좌표의 에너지 변분만으로 충분하다고 주장하지 않고 first-order kernel–Jacobian covariance와 second-order Jacobian까지 포함했다.

### 2.3 부호와 Jensen 부등식

Determinant-one map에 대한 \(\langle R^{-3}\rangle=1\)은 연속 구면 항등식이다. 고정 baseline gas와 동일한 inverse-cube law가 모든 ray의 전 경로에 적용되면 \(\langle\Theta\rangle=\Theta_0\), 따라서 convexity로 \(\langle P\rangle\ge P_0\)가 된다. 보고서는 이를 cumulative absorption 확률의 부등식으로 사용하며, endpoint 사건률의 부호 정리로 바꾸지 않는다.

식 (17)–(19)의 power-law 계수와 부호 예시는 일반 커널에서 일관되게 나온다. 특히 \(c_A=3\tau(\tau-4)/10\), \(c_Q=3\tau^2/10-2\tau/5-8/15\) 및 \(c_Q\)의 양의 영점 \(2(1+\sqrt5)/3\)는 맞다. 작은 \(|\epsilon|<\ln2\)에서 heat threshold를 피하므로 반례의 부호 변화는 threshold cusp를 필요로 하지 않는다. 이 진단은 고정 gas, H=0의 운동학 모델로 명확하게 제한된다. 실제 FT03의 evolving gas 온도 부호를 이 반례에서 추론하지 않았다.

### 2.4 Source-bound gas response

Per-H photon measure, He nucleus당 fraction, per-absorber \(\Gamma\)와 per-H event \(A=\ell\Gamma\)의 구분은 소스와 일치한다. Photon count에 \(-3HN\)을 추가하거나 primary 사건을 두 번 주입하지 않았다.

PHYS20의 가정 아래 scalar \(y_1=0\)을 입력으로 소비하면 선두 quadratic gas coefficient에 작용하는 것은 local Jacobian과 radiation functional의 선형 Fréchet derivative다. 보고서 식 (29)의 endpoint abundance 항과 과거 opacity memory 항, 식 (30)의 \(\lambda_y\), 식 (31)의 injection matrix, 식 (33)–(34)의 Volterra 적분 순서가 일치한다. Gas Hessian의 \(D_y^2F[y_1,y_1]\) 항은 이 조건에서 0이다.

온도는 \(T=2e_{\rm V}w/(3k_B\Pi)\)이므로 식 (35)의 입자수 항이 필요하다. 이 항과 He의 \(T,n_e\) 매개 간접 반응을 보존했다. Source thermal row의 \(-2Hw\), RR kinetic derivative의 \(g'\), two-DR 소유권도 일치한다. Volterra equation의 존재·유일성은 보고서가 선언한 smooth, bounded, finite-interval baseline 조건 아래의 formal 결과다. 해당 response를 실제로 풀었다는 주장은 없다.

## 3. 수치 근거 판정

| 근거 | 직접 확인한 결과 | 지지 범위 |
|---|---|---|
| Owner HI kernel | 39/39 PASS, 실제 exit 0, 결과 SHA `ed41b97cfd65ffeb4e21efb6fab672488cc0a9495f28f439e08f0840ee2f0a5b` | 두 cohort의 고정 initial neutral-fraction 커널, retained density dilution, 해당 finite differences/구적 변화 |
| Tensor contribution | 44/44 PASS, 실제 exit 0, 결과 SHA `a90666a1e280ad736f73e0b5b84b7f372e9c43cf3ff7ea569a36e2dfdcde889f` | Exact Fraction coefficient, Q2/Q4 contraction, fixed-q covariance, 별도의 finite-amplitude 진단 |
| Local gas derivative | 60/60 PASS, 실제 exit 0, 결과 SHA `e15b464cbb88f5522531b021c42988158fc901e98ece7c49801d69e01802aa57` | 세 smooth fixture의 manual Python nonphoto Jacobian과 temperature gradient |

검사 수는 각 프로그램의 판별 항목 수다. 여러 개의 독립된 물리 정리 수나 통계적 유의도인 것처럼 합산하지 않는다. Report의 최대 오차와 허용오차는 실제 결과에 부합한다. HI 상대 계수의 survival 양수, absorption/heat 음수, surviving energy 양수라는 표도 원본 결과와 일치한다.

Decimal과 exact-rational 비교, angular/time resolution 변경은 stated scope의 numerical agreement를 제공한다. Rigorous enclosure, native finite-grid 검증, full source integration 또는 gas trajectory 검산으로 읽을 수 없다. 현재 보고서는 이러한 상한을 유지한다.

Local gas v1의 DR constant 계산을 source와 같은 연산 순서로 바꾼 수정은 source transcription 정렬이다. 실제 v1과 수정본은 모두 PASS이고 결과 JSON은 bytes까지 동일하다. Step \(10^{-24}\), tolerance \(2\times10^{-12}\)가 그대로이며 초기 코드·결과·receipt가 보존되어 있다. 최초 실패 또는 물리 오류라는 잘못된 서사가 없다.

## 4. Claim별 최종 판정

| Claim | 판정 | 근거 상태와 상한 |
|---|---|---|
| C21-KERNEL: 일반 continuum quadratic scalar kernel | PROMOTE | derived; declared diagnostics에서 numerically checked |
| C21-COORDINATE: physical-birth와 fixed-q+\(J_b\)의 2차 일치 | PROMOTE | derived; exact contraction 및 finite-amplitude 진단 |
| C21-SIGN: inverse-cube cumulative inequality와 endpoint absorption/heat 부호 반례 | PROMOTE | derived; 반례의 stated diagnostic 수치 검산. 일반 opacity/gas 부호 정리 아님 |
| C21-HI: 실제 HI fit의 frozen-neutral cohort 계수 | PROMOTE | source-bound diagnostic에서 numerically checked. Evolving gas 계수 아님 |
| C21-GAS: FT03 linear causal response와 temperature mapping | PROMOTE | source supports; derived. Local derivative만 numerically checked |
| C21-FINITE-GAS: 실제 finite-time \(x,T,\Gamma,\tau\) 계수와 부호 | HOLD | unresolved; required baseline evaluator/enclosure와 response solution이 없음 |
| Native discretization / physical admission | HOLD | 이번 근거의 대상 밖이며 기존 실패/gate 상태를 해소하지 않음 |

PHYS19의 상계와 terminal interval은 필요한 baseline trajectory를 유일하게 정하지 않는다. 이는 finite-time 숫자의 gap이며, 완성된 새 functional 전체를 무효화하는 blocker가 아니다. 제한된 archive 검색 결과를 archive 부재의 증명으로 바꾸지 않은 것도 타당하다.

## 5. 유지 조건과 종료

`physical=HOLD`, `[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지한다. Source/default/runtime returns 변경은 이 판정의 범위 밖이다. 검토 중 수정이 필요한 fatal issue는 0개이고, 같은 결과에 대한 추가 전체 과학 재검산은 요구하지 않는다.

다음 `REI-PHYS22_INITIAL_TIME_COUPLED_SHEAR_RESPONSE`는 PHYS21 kernel 및 local gas operator를 이용하는 bounded 초기시간 연구로 적절하다. Report의 \(O(\varsigma^2t^2)\) forcing, \(O(\varsigma^2t^3)\) gas response와 continuous-birth 지연 차수는 **검증할 출발 가설**로 남아 있으며 이번 승격이 그 계수나 차수를 이미 인증하지 않는다.

이 독립 decision gate는 여기서 닫는다. Owner는 승인된 보고·재현 포장·추가 경로 publication을 완료할 수 있다. 향후 archive restore, Git readback 및 저장 성공은 각각 실제 실행 후 별도 receipt로 기록해야 하며 본 수학 판정이 이를 대신하지 않는다.
