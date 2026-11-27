# THEORY06 독립 최종 판정

**PROMOTE_SCOPED_THEORY — 명시한 이론 범위를 채택한다.**

단위: HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06  
경로: physmath-research-loop 1.0.0, THEORY  
독립 검토자: /root/dropbox_checkpoint  
판정 시각: 2026-10-13T00:28:41.259370+00:00

고정 후보는 [CANDIDATE_MANIFEST.json](../dossier/CANDIDATE_MANIFEST.json), SHA256 **7e3b571e4a27da5fd7c204e3a23309dc9f7c2ed6eb5b0369fe0bf2a1389af495**다. Manifest 자체는 9335 bytes이며, **48개 파일/426321 bytes 모두 실제 size·SHA256과 일치**했다. 확인 시각은 2026-10-13T00:22:42.012256+00:00이다. 전체 파일 identity는 이 manifest를 참조하며 중복 전사하지 않는다. 기계 판정은 [DECISION.json](DECISION.json)에 있다.

현재 고정 가정에서 미해결 material 수학 오류나 근거 불일치를 찾지 못했다. 검토자는 후보 proof·scientific code·수용기준을 작성하거나 변경하지 않았으며, 과학 계산을 실행하지 않았다.

## 1. 채택하는 정량 결과

고정 local Eulerian tetrad·체적, 공통 기체 속도, \((-+++)\), \(\Gamma=5/3\), \(D=10^{-3}\ \mathrm{cm^{-3}}\), \(f=2/25\)를 유지한다. 이전 상태는 \(\zeta_*=(1/2,1/50,1/50)\), \(T_*=50000\ \mathrm K\), \(\beta_*=(0,0,41/841)\)다. 각 단계의 \(\mu\in[10^9,1.5\times10^9]\ \mathrm{eV/H}\)는 고정되고 상계는 그 family에 균일하다. 23/35/70 eV의 지정된 여섯 방향 node는 각각 \(N_q^-/D=1/100\), 외부 공급 0이다.

Source decimal로 정의한 full FT03 CI3·RR3·DR2와 활성 Verner 광흡수, 원래 kinetic/binding escape를 유지한다. 선언한 affine unit cube에서

\[
0\le h\le H=500000000\ \mathrm s,\qquad
HB=\frac{2007609719349141}{2500000000000000}
=0.8030438877396564<1,
\]
\[
q=
\frac{702445907956526291951811059835445533}
{31250000000000000000000000000000000000}
=0.02247826905460884\ldots<1
\]

를 채택한다. 각 고정 이전 상태의 전체 \(h\) 구간에 cube 안의 유일한 해가 있고, 해는 \(h=0\)에서 시작하는 하나의 \(C^1\) 가지다. 이것은 **한 backward-Euler source 문제의 단계 매개변수 인증**이다. Cube 밖의 유일성, 최대 step, 실제 ODE 궤적 또는 시간 이산화 오차의 인증은 포함하지 않는다.

## 2. 주장별 판정

| Family | 판정 | 검토 근거와 한계 |
|---|---|---|
| C1 affine cube·primitive 역미분 | ADOPT_SCOPED | 상수 가역 행 변환이 원래 7개 finite 잔차를 보존한다. Cold remainder와 Hessian 상계가 전체 cube의 양의 cone/simplex/warm 포함을 미분보다 먼저 증명한다. Inverse differential, 밀도·온도·속도·Doppler chain과 scaling이 일관된다. |
| C2 실제 FT03/Verner 상계 | ADOPT_SCOPED | 고정 source 식·literal·두 DR target/energy와 RR kinetic derivative가 대응한다. 구간 monotonicity와 양의 factor, rational-power exact bracket 및 exponential Taylor-tail이 전 구간 상계를 지지한다. Native binary64 오차 인증은 후속 의무다. |
| C3 finite full source·미분 | ADOPT_SCOPED | \(D\gamma^{-2}e_H y k(T)\), 같은 endpoint의 opacity·Doppler·소거 분모 미분을 유지한다. 공유 사건을 투영한 \(-(\Gamma_*-1)B_{\rm esc}\) 상쇄, 에너지 단위와 lab-time 계수에 중복이 없다. |
| C4 실제 \(H\)·corrector 경계 | ADOPT_SCOPED | 실제 combined 입력이 C1과 C2 경계를 그대로 소비한다. 일곱 행 majorant와 양의 유리수 \(H\) 선택이 uniform self-map/contraction을 보장한다. State·inverse·parameter·photon·corrector 경계가 그 가정에서 따른다. |
| C5 tube·최대 endpoint | ADOPT_DERIVED_SPECIALIZATION | 고정 가역 \(A\), full-tube Jacobian의 \(Y+Zr<r\), weighted contraction 및 같은 root의 nesting을 요구한다. 교정된 finite nonextendible maximal-endpoint 귀결은 타당하다. 표준 정리의 적용이며 \(H\) 밖의 실제 tube pair는 미구성이다. |
| C6 tensor·coding 인계 | ADOPT_TENSOR_AND_HANDOFF_ONLY | 실제 xTensor contraction/canonicalization과 최종 구현 계약을 확인했다. Native consumer의 구현·검증 완료는 채택하지 않는다. |

핵심 논증은 순환하지 않는다. 전체 cube의 \(10<w<11\), \(45000<T<55000\) 포함 뒤에 \(L_w=0.26\), \(L_T=1400\), \(L_\beta=3\times10^{-6}\), \(L_\gamma=2\times10^{-7}\), \(L_\delta=4\times10^{-6}\)를 사용한다. Fit cutoff와 binding energy가 구별되고 활성 cell이 고정된다.

Affine energy 행은 압력에 해당하는 \(dt=dw+(2/3)w\,d\gamma/\gamma\)를 유지한다. RR/DR binding의 단위 부분만 정확히 상쇄되며 \(\Gamma_*-1\)과 그 미분은 남는다. 정확 Picard 8회 update의 \(q^8HB/(1-q)=5.354461272651965\ldots\times10^{-14}\) 오차상계는 타당하지만 **실제 반복은 0회**다. Native 사후 잔차식에는 계산된 잔차의 엄밀한 오차 enclosure가 필요하다.

## 3. Actual input·raw·result 검토

| Batch | 실제 최종 수신 | 확인한 대응 |
|---|---:|---|
| Primitive | 17/17 groups | CALL_INPUT code = executed = canonical WL; raw를 decode한 객체 = normalized |
| FT03/Verner | 20/20 groups | CALL_INPUT code = canonical WL; raw 객체 = normalized; exact interval helper와 cap 비교를 읽음 |
| Combined source | 12/12 groups | CALL_INPUT code = executed = canonical WL; inline 여섯 cap field = 고정 rate result |
| xAct v2 | 8/8 groups, 17 zero residuals | CALL_INPUT = executed wrapper, embedded program = canonical v2; raw 객체 = normalized |

총 **57 named groups, 6 claim families**다. xAct 내부 residual 17개나 76 power/5 exponential 내부 witness를 추가 group·독립 정리로 세지 않는다. 과학 evaluator 시도 5회에는 xAct v1 실패 1회가 포함된다. Native build/test·chemical RHS·ODE/history·nonlinear-stage iteration은 모두 0이다.

실패와 capture 제한은 채택 근거에서 분리했다.

- xAct v1은 package load와 Hold[Throw[Null]]만 반환했다. 성공 group 수는 미관측이다. 입력의 fixed dummy-index helper를 v2에서 동치 projection scalar로 바꾸고 정의 residual을 추가했으며, 수학 가정을 완화하지 않았다.
- Rate의 실제 AssociateTo 인자 오류는 마지막 metadata append다. 20개 과학 결과는 완전하며 미수신 runtime/version/system은 null이다.
- xAct wrapper에도 같은 입력 형식 문제가 있으나 그 raw에는 해당 warning이 없다. Archive-hash guard 이후 tensor 결과와, 미수신 추가 hash/runtime을 정확히 구별한다.
- Combined raw의 유일한 ellipsis/key 경계를 문서화된 방식으로 복원했을 때 모든 실제 수신 field/value가 normalized와 일치했다. Exact \(H,HB,q\), 일곱 행 \(b,\ell_0,\ell_1,\ell_H\), 12개 판정과 summary는 수신됐다. 생략된 중복 exact scalar 네 개는 null이다.

성공한 과학을 metadata·serialization 때문에 재실행하지 않았다. 위 제한은 현재 core certificate의 근거를 제거하지 않는다.

## 4. 지적 해결과 최종 coding 범위

독립 지적은 해결됐다. “finite endpoint”를 “finite nonextendible (maximal) endpoint”로 한정했고 extension proof는 유지했다. C1/explicit-certificate의 CR literal과 Rump 절 표기를 복구했다. xAct intended metadata·실제 반환·warning의 차이는 최종 실행 기록에 정확히 반영됐다. S14의 derivative norm 및 direct \(L_\delta\) 설명도 확인했다.

[최종 CODING_CONTRACT](../dossier/CODING_CONTRACT.md)의 SHA256은 **61fe0dd8b3b1fc14822f6c0676ae30d42ec521598eff2969527621c40ddf022e**다. 전체를 읽고 다음 의무를 확인했다.

- 다른 고정 chart로 옮겨도 \(F_{\rm new}=X_{\rm new}-X_{{\rm old,new}}-hG_{{\rm new},h}\)에 변환된 이전 상태를 남긴다. \(h\)-dependent chart는 별도 미분을 요구한다.
- 실제 \(s_m=a_*10^{-6}\)와 majorant의 하한 1000을 구별한다.
- Proper density, per-H/per-He, node weight와 방향을 정확히 소비한다. 횡방향 속도 API는 실제 ray 또는 명시적 방위각 적분을 유지한다.
- Gross 사건·kinetic/binding/escape·photon 장부와 JVP가 동일 endpoint를 공유한다.
- Baseline 표현·primitive·provider·사건 합·변환·분모의 실제 오차를 residual/update budget에 포함한다.
- 미래 tube는 full-domain enclosure와 strict inequalities, 공통 root 포함을 실제로 제시한다.

이들은 후속 구현 완료 조건이다. 문서에 적힌 native 판별 검사를 이번에 실행했다고 판정하지 않는다.

## 5. 원전, 독립성과 남은 의무

표준 도구는 [Day–Lessard–Mischaikow 2007, Theorem 2.1](https://www.math.mcgill.ca/jplessard/papers/validated_continuation.pdf), [van den Berg–Lessard–Mischaikow 2010, Lemmas 5/7·Proposition 8](https://www.math.mcgill.ca/jplessard/papers/branch_following.pdf), [Rump 1995, §3](https://www.tuhh.de/ti3/paper/rump/Ru95b.pdf)에 귀속한다. Rump의 해당 centered-slope 존재·regularity 결론을 자동적인 full-box uniqueness로 확대하지 않았다.

검토자는 Exa 4 query·SciSpace 1 query를 실제 사용해 3편의 필요한 theorem sections를 읽고 문헌 기록을 작성했다. 검색 수와 원전 읽기 범위, 전체 논문 읽기를 구별한다. 후보 proof/code/수용기준 저자 역할이나 과학 계산 실행에는 참여하지 않았다. JSON decode·byte/SHA 비교·manifest·판정문 저장은 metadata 처리이며, 닫힌 THEORY05 과학을 재실행하지 않았다.

기존 PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04, MOVING_GAS_STAGE_05와 새 CONTINUATION_CERTIFICATE_ADAPTER_06는 coding pending이다. THEORY07은 명시적 full-rate tube pair, 실제 strict inequalities, same-root 연결 및 old-state family/reanchoring을 구성해야 한다. RUX02 + global RUX03 → RUX04 → RUX05와 별도 all-Bianchi/abundance-source/reference-current/class-B/relative-species-tilt D2.3 의무를 보존한다. Native 검증, \(H\) 이후 tube·fold 통과, 전체 cosmological evolution 및 전역 신규성은 채택 범위에 없다. 새 strong no-go 주장·채택도 없다.

판정의 쓰기 대상은 DECISION.md와 DECISION.json 두 파일뿐이다. 임시 파일 write/flush/fsync 후 각 경로에 atomic replace하고 review directory를 fsync한다. 저자 후보는 변경하지 않는다. 후속 SCIENCE_MANIFEST·CLOSEOUT·publication·backup·delivery의 실제 완료는 root의 별도 영수증에 기록한다.
