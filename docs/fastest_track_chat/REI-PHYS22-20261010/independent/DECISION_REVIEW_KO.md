# PHYS22 최종 독립 판정

**판정: PROMOTE_SCOPED.** 실제 paired 초기조건에서의 국소 \(\epsilon^2\) 시간 계수, initial/birth 지연, He 간접 반응 및 온도의 입자수 변환을 연구 보고와 다음 한정된 물리 문제의 입력으로 승격한다. **Physical admission은 HOLD**다. 최종 고정 후보에 남은 필수 수정과 fatal finding은 없다.

## 1. 검토자와 고정 후보

검토자는 별도 agent /root/phys22_decision이다. 후보의 유도·코드 작성·검증 설계에 참여하지 않았다. Parent의 full-history 문맥을 상속한 **비맹검 검토**다. 문맥까지 독립적인 blind replication, 별도 native 구현 또는 독립 기체 IVP로 주장하지 않는다. 파일·식·원시 결과·실행 receipt와 관련 source 구간을 읽고 문서 전사 문제를 보고했다. 새 과학 검사나 닫힌 PHYS19/20/21 검산을 실행하지 않았다.

| 결속 대상 | SHA256 또는 identity |
|---|---|
| 최종 PHYS22_REPORT_KO.md, 26,662 bytes | a3d4ed48e753538eee763a3fe26931dfea6332132de15fc3a7b43b2b600797f6 |
| PHYSICS_CONTRACT.json | 1706650c98b6b30f12e57b2af670113fe8ec30770ae2f48909823c30936de4a6 |
| SOURCE_MANIFEST.json | ee8de581b01a630f0e12c5b9923d2d5a5cfb3bcc43c230ad19cabd07407ee8e5 |
| Input commit | 3dc42c64ab32075f0a59c96af3ddf7435d9b7f97 |
| Scientific source tree | cb69b4736dd046e4675557577eb8e0ead037d1f3 |
| Owner coefficient result | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |
| Radiation exact time-series result | fbea19efef78f823dafe1cae17eaa07ec59cdda8eee954b591bc7005fb85017e |
| Gas local result | 3b86f79b98bc393673f6415828818c33c80a9979049aca39494348d0d1ef735c |
| Cross-implementation comparison | 5075ec47f98998c42b347b43fbd59e720ce17f1910fa4a3a729745f42114025d |

Canonical Astra harness의 공통 core, model routing, phase gate, stop rule, independent decision gate를 적용했다. Harness ZIP identity는 dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7이다. 검토자가 remote tree를 다시 가져오지는 않았다. Owner의 immutable remote binding을 소비했고 local source 7개의 size/SHA256/Git blob identity가 SOURCE_MANIFEST와 일치함을 직접 확인했다. Source 내용은 actual IC, HI fit, local rates/RHS, primary 소유권 관련 구간을 읽었다. Byte identity와 과학적 타당성은 별개의 근거다.

## 2. 주장별 판정

| 주장 | 근거 상태 | 판정과 범위 |
|---|---|---|
| \(K_{L,2}=q[(\mathscr C L)u^2+k_3u^3]/15+o(u^3)\) | derived; exact-rational diagnostic check | PROMOTE. 초기 curvature, attenuation, covariance, mean-opacity의 계수와 차수가 맞는다. |
| Initial atom과 continuous birth의 시간 차수 및 \(1/3,1/12,1/4\) | derived; exact-rational diagnostic check | PROMOTE. Birth 시각의 \(\mathcal A\)와 cohort-age의 \(\mathcal T=\mathcal A-HD\)를 구분했다. |
| \(a_3=v_2/3,\ a_4=(A_0a_3+v_3)/4\) | derived; local coefficient checks | PROMOTE. Initial-photon endpoint abundance derivative가 \(A_0\)에 포함되며 gas-induced opacity memory는 더 늦게 들어간다. |
| 실제 HII/w/T \(t^3\), HeII/HeIII \(t^4\) 계수 및 부호 | derived; numerically checked | PROMOTE. 선언한 초기조건과 continuum 모델의 국소 계수다. Rigorous sign enclosure나 유한시간 부호 판정은 아니다. |
| HII/w/T의 full \(t^4\) 및 temperature-gradient drift | derived; numerically checked | PROMOTE. 필요한 \(D^3\), local baseline tangent, coupled matrix가 포함된다. 전체 \(t^4\)에 대한 두 독립 time integrator의 일치로 주장하지 않는다. |
| 온도 sign functional, 보고서 식 (19) | derived | PROMOTE. \(a_3\)와 온도 gradient의 정확한 선형 결합이며 별도 수치 실험으로 세지 않는다. |
| Count 및 leading primary-energy 일관성 | derived; exact/local checks | PROMOTE. 국소 time-jet와 primary 소유권 범위다. 전체 gas-history ledger의 실행 결과가 아니다. |
| Finite-time response/remainder, native arithmetic equivalence, physical admission | unresolved / outside admitted scope | HOLD 유지. 현재 검산이 이를 닫지 않는다. |

### 계수·단위·regularity

\(F_2=[\epsilon^2]F=\tfrac12\partial_\epsilon^2F|_0\), \(q=2\varsigma^2\), \(a_n=[t^n]\eta\)가 보고서·코드·원시 JSON에서 일치한다. 시간 계수에 추가 factorial을 넣지 않았고 실제 표에는 물리 shear 제곱을 한 번 포함했다. 별도 normalized \(u_3,u_4\)의 단위는 state/s와 state/s²이며 실제 \(a_3,a_4\)는 state/s³와 state/s⁴다.

Leading curvature에는 \(C^2\)와 국소 baseline의 적절한 연속성이 충분하다. 일반 \(u^3\) radiation 및 full H/T \(t^4\)에는 \(D^3L\)가 필요하므로 보고서의 \(C^3\) 조건이 적절하다. He의 최초 \(t^4\)는 이미 얻은 \(C^2\) forcing과 smooth local gas derivative에서 나온다. 실제 초기점은 사용한 cutoff와 온도·fraction domain의 내부에 있다. 이 국소 사실을 유한시간 안전 구간 또는 remainder 상계로 확대하지 않았다.

### 복사·source·memory

Physical birth-angle 평균은 birth measure 자체에 일관되게 적용되어 불필요한 Jacobian이 없다. Continuous source의 leading factor는 cohort age를 적분한 \(1/3\)을 포함한다. Birth forcing의 다음 계수는 \(\mathcal A(\mathscr C L)/12+k_3/4\)의 **합**이다.

고정 baseline에 대한 radiation opacity history는 직접 forcing의 \(t^3\)에 이미 들어간다. 반면 \(\eta=O(t^3)\)가 gas abundance를 바꾸어 survival에 되먹임되는 Volterra 항은 RHS \(O(t^4)\), gas \(O(t^5)\)부터다. 보고서는 이 두 의미의 memory를 분리했다. Continuous-birth particular response 역시 동일 full baseline과 causal operator에서 forcing을 분해한 것으로 명시되어 있다. 이를 전체 해의 \(S\) 미분이나 모든 \(S\)-dependent higher coefficient로 바꾸지 않았다.

### 기체·온도·He

Nonphoto CI/RR/two-DR 식, per-H 열에너지, per-He fraction의 \(f\) 정규화, primary event/heat의 한 번 사용은 읽은 source와 일치한다. \(A_0=J_{\rm np,*}+N_0\mathsf B L_{y,*}\)의 endpoint derivative가 포함되어 H/w의 full \(t^4\)가 birth contribution만으로 대체되지 않는다.

\[
\theta_3=\frac{\mathcal A_T}{\Pi_*}a_{3,w}
-\frac{T_*}{\Pi_*}a_{3,x},
\qquad
\theta_4=(\nabla T)_*\cdot a_4+
\frac{d}{dt}(\nabla T)_*\cdot a_3
\]

의 입자수 항과 gradient drift는 실제 계산에 남아 있다. 보고서 식 (19)는 \(T_*/\mathcal A_T=w_*/\Pi_*\)와 \(\mathscr C\)의 선형성에서 나온다. 따라서 \(\mathscr C\)가 \(T,y\)를 고정한 에너지 미분이라는 조건하에서 정확하다.

HeIII의 양의 \(t^4\)는 직접 photo channel을 켠 결과가 아니다. \(G_{\rm HeIII}<0\)인 초기 순재결합 상태에서 음의 전자수 response가 주는 양의 항과 음의 온도 response가 주는 음의 항을 실제 수치로 비교한 결과다. 두 항과 합계, HeI 핵수 보존 관계가 맞는다.

## 3. 실제 증거의 범위

| 실행 경로 | 보관된 실제 결과 | 독립성·제한 |
|---|---|---|
| Radiation contributor | 52/52, exit 0 | 6개 normalized analytic fixture의 새 time/source jet. PHYS21 kernel 구현을 import하지 않았다. |
| Gas contributor | 11/11, exit 0 | 고정 inherited local-gas 함수와 한 새 physical direction의 complex-step. Full old suite를 실행하지 않았다. |
| Owner Decimal80 | 21/21, exit 0 | 별도 source 식 전사, 새 \(D^3\), baseline tangent, temperature chain rule와 대수 관계. |
| 두 경로의 계수 비교 | 16/16 PASS; owner 보고서에 exit 0 기록 | 최대 상대차 \(7.71105352001234\times10^{-15}\), 허용오차 \(5\times10^{-12}\). Leading/birth 및 local coupled 항의 비교다. |

위 숫자는 check rows 또는 성분 비교의 개수다. 물리 법칙의 독립 개수로 합산하지 않는다. Decimal 경로의 \(T_*=50000\) 정확한 실수 정규화와 binary64 initial-w의 역변환 \(49999.99999999999\) K는 작은 차이가 있지만 동일 arithmetic identity는 아니다. 보고서는 이 차이를 명시했다.

검토자는 프로그램들을 재실행하지 않았다. 이미 수행된 새 검산의 원시 결과와 receipt, 코드의 관련 계산 구조를 검토했다. Portable replay, ZIP 검증, remote publication은 owner의 이후 closeout 근거이며 이 판정에서 완료로 선행 주장하지 않는다.

## 4. 발견 사항과 해소

한 번의 집중 검토에서 다음 문서 전사 문제를 보고하고 해당 수정만 확인했다.

1. Radiation RT10의 두 birth \(t^4\) 항 사이에 +가 빠져 있었다. 코드에는 처음부터 올바른 합이 구현되어 있었고 exact 결과도 그 합을 검산했다. 원문 v1과 correction receipt를 보존했다.
2. Radiation RT20/21의 form-feed 및 LaTeX, RT23의 brace 표기를 고쳤다. RT20의 추가 제어문자는 동일한 한정된 정규화 과정에서 기여자가 찾았다.
3. Gas note의 복합 단위 전체에 지수가 걸리던 7곳을 명시적인 eV H⁻¹ s⁻ⁿ, K s⁻ⁿ 등으로 고쳤다.
4. 첫 고정 통합 보고서 §7의 \(\mathrm{eV\,s}^{-1}\)을 \(\mathrm{eV\,s^{-1}}\)로 고쳤다. 원본 SHA는 a5521b69166bf52e18db54697c1ebb84c28966c68b2b9255898a35906c5b6547이고 evidence/PHYS22_REPORT_KO_v1.md에 보존되었다. 최종 판정은 수정된 보고서 SHA에 결속한다.

이들은 **문서 수식·단위 전사 수정**이다. 과학 코드, 수치 결과, 최초 실행의 성공 여부, 허용오차를 바꾸지 않았다. 과학 실패나 재실행을 새로 만들어 기록하지 않는다. 관련 기록은 두 contribution의 DOCUMENT_CORRECTION.json과 evidence/REPORT_DOCUMENT_CORRECTION.json에 있다.

수정된 radiation note SHA는 cd3ff830cceb4d654ca24fbd97f6a1fb83010cfc60acacd67153621bcda93c17, gas note SHA는 2dbdf17cede8a12f6a3375cdece56c896fc0283c22de02018e1586c7090e8b3c이다. **미해소 필수 수정 0, fatal issue 0**이다.

검토 파일을 처음 쓰려던 functions.exec 호출 한 번은 JavaScript 문자열 quoting의 SyntaxError로 평가 전에 실패했다. 파일 mutation이나 과학 프로그램 실행은 발생하지 않았다. 이를 검토 문서 작성의 tooling 오류로 분류하고 수정된 문자열로 작성했다. 과학 실패와 구분한다.

## 5. 승격 한계와 종료

Fixed-mean-expansion의 source-inspected continuum 모델에서 실제 초기 기체의 국소 scalar response를 구했다는 범위에서 유효하다. 임의의 유한시간 endpoint, 온도 crossover, 관측 가능성, native stage의 미분 가능성 또는 bitwise equivalence는 지지하지 않는다. Positive \(t^4\) temperature coefficient만으로 negative \(t^3\)에 대한 유한시간 부호 반전을 선언하지 않은 점은 적절하다.

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 새 gas IVP, native history, protected source/default/runtime returns 변경은 이 판정이 승인하지 않는다.

보고서와 다음 한정된 PHYS23 문제의 입력으로 **PROMOTE_SCOPED**한다. 과학적 필수 위험과 독립 decision gate는 위 범위에서 해소되었으므로 추가 전면 감사나 과거 검산 재실행은 필요하지 않다.
