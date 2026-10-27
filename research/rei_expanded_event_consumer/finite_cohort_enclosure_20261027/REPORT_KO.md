# REI finite-cohort 연구 결과

## 판정

이론 루프10/10을 완료했고 exact-rational 구현과20개 테스트를 작성·독립 정적 검토했다. 코딩 완료는5/10이며 C6/C8은 실행 보류, C7/C9/C10은 부분 완료다. 이번 과학 실행·테스트·CAS evaluator·기존 계산 replay는 모두0이다. Overall은 HOLD_RESOURCE_AND_ACTUAL_PROVIDER_BINDING_NO_GLOBAL_OR_L4_PROMOTION이다.

20개 단계는 각각 Git에 게시했고 양쪽 백업 ACK가 있다. R1–R6는 실제 ZIP이며 이후14개는 원문 체크포인트다. Source snapshot의97개 파일 전체는 복원 가능한 UTF-8 JSON으로 별도 전달했다. Whole-unit ZIP 생성은 자원 gate로 보류한다.

## 구성적 결과

선택한 cohort \(h_C\ge0\)의 누적 \(G(x)=\int_0^{\operatorname{clamp}(x,0,S)}h_C(s)\,ds\)로
\[
K_{A,B}(\tau)=G(B-\tau)-G(A-\tau),\qquad
D_{A,B}=\int K_{A,B}\,dF
\]
를 쓴다. 같은 response의 cumulative F를 모든 창이 공유한다. 이미 닫힌 \(l/u\)와 all-time cap 아래에서
\[
X=\{x:x_0=0,\ l_i\le x_i\le u_i,\ x_i\le x_{i+1}\},
\quad q_i^\mp=\min/\max_{[t_i,t_{i+1}]}K
\]
이면
\[
\inf_FD=\min_{x\in X}\sum_iq_i^-(x_{i+1}-x_i),\qquad
\sup_FD=\max_{x\in X}\sum_iq_i^+(x_{i+1}-x_i).
\]
증명은 finite measure의 cell mass를 분해하고 각 cell의 극점에 atom을 놓는 구성이다. 제외된 왼쪽 endpoint는 오른쪽에서 접근한다. Chain polytope의 vertex level은 \(V=\{0,l_i,u_i\}\)에 있으므로 prefix DP로 정확히 최적화한다. Nonnegative affine special case는 이전 정리로 환원된다.

여러 창을 결합할 때에는 kernel을 먼저 합친다. 같은 chain만으로는 cell 내부 최적 atom 위치를 공유하지 못하므로, 개별 sharp upper를 더하는 것은 일반적으로 sharp하지 않다. Box source \(h=1\) on[0,1], F(0)=0,F(2)=1에서 U01=U12=U02=1이므로 U01+U12=2>U02=1이다. 실제 고정 F의 관측량은 여전히 가법적이다. 일반 lower도 비달성 infimum일 수 있다.

이는 interval·monotonicity information set의 정리다. 전체 source의 shutoff나 실제 fixed physical response family의 sharpness를 새로 증명한 것은 아니다. 기존 convolution·p-box LP/vertices는 원전과 이전 source에서 재사용했다.

## 조사 범위와 달라진 근거

Owner-accessible51repos를 열거하고 직접 의존7repos의1399branch metadata를 terminal page까지 확인했다. REI282,CR187,Vigil218,HE107,BASS289,WU159,REC157이다. 최신 변화에 관련된 원문과 접근 가능한 백업 handoff를 읽었다. Dropbox REI292entries를 끝까지 조사했다. Drive folder direct read는100개 제한이 있어 exact known IDs로 보완했다. Personal context는 unavailable이므로 모든 대화·역사 파일·archive bytes를 읽었다고 주장하지 않는다.

- WU R6의 공개 final C9가 새로 완료됐다. 최신 확인0713cb7e, producer stored76/76·independent109/0mismatch를 재사용한다. Wolfram23zeros와 unresolved warnings를 함께 보존한다. Physical density/consumer는 null이다.
- CR1082776752d final C9는 PENDING이다. CR1098482ed83의 별도 final C9를 CR108로 옮기지 않는다. Source100K/response10000K mismatch와 recipient nb 미제공도 유지한다.
- BASS2036bf4a5d9에서 same-tube stocks·native opacity diagnostic·common volume·finite photon return이 확보됐다. QSS/non-Lyalpha energy owner와 physical radii는 남아 있다.
- BASS204의 Bianchi V Class B measure는 instantaneous scope다. Finite IVP를 실행한 근거로 사용하지 않는다.
- Vigil V8의 uniform-rounding 백업은 접근 가능하지만 Git UNKNOWN_NO_ACK이며 actual REI25 binding/native segment는 미제공이다.
- REC finite physical opacity/error radius, HE stopping/thermalization 및 미분 의무는 유지한다.

근거 pin과 backup ID, 실제 확인 범위는 SOURCE_SURVEY.json과 SOURCE_DELTA_FINAL.json에 있다.

## 코드와 검증

cohort_bounds.py는8433bytes, test_cohort_bounds.py는8944bytes다. Exact Fraction 입력, nonnegative piecewise-affine partition, primitive/kernel extrema, combined-kernel DP, frozen limiting witness를 구현했다. Independent static review는 blocking finding0, requested repair0이다.

20개 tests는 box/nonadditivity, affine exact values, stationary point, 독립 tiny Cartesian-chain oracle, signed objectives, 경계·zero·invalid input, large integer, witness·deterministic tie를 다룬다. 실제 실행0이며 이전 affine16개도 미실행이다. 과거 causal3189/3189와264derivatives·528FD는 유효한 저장 결과로 재사용한다.

## 자원과 재개

Planning 누적15.077490885와 originalcap10을 보존한다. Presentation은 inherited43.787562494+이번 실측1.103205+새 tail0.10=44.990767494다. 마지막 helper 시작 비용0.124035가 예약0.11을 넘었고 전체unit actual+tail1.203205도 예약1.19를 넘었다. 해당 실패를 보존하고 local runtime을 중단했다. 원래 policycap10/30으로 복원했으며 Main595.225063/600, NO_MORE_IVPs와 foreign-owner budget을 보존한다. 미측정비용은 UNKNOWN_NOT_ZERO다.

다음 실행 제안은 planning absolutecap16과 신규0.80CPU 예약으로36개 최초 테스트, presentation absolutecap46과 신규0.80CPU 예약으로 ZIP1회다. 원래 baseline 대비50% 이상 인상이므로 명시적 별도 승인 전에는 실행하지 않는다. 이는 기존 게시·백업 권한을 다시 묻는 절차가 아니다.

## 단계별 기록


| 단계 | 실제 상태 | 게시 commit | 전달 | 원래 DAG |
|---|---|---|---|---|
| R1 | complete | `3aa0cd80fbc9` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R2 | complete | `e3d103718e61` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R3 | complete | `33006d906941` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R4 | complete | `03b0f9c13971` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R5 | complete | `611ff429448e` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R6 | complete | `c1b736238a45` | ZIP / 양쪽 ACK | 32/88 · 중앙27/88 |
| R7 | COMPLETE_ANALYTIC | `028ca1f8ed84` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| R8 | COMPLETE_SCOPED_ANALYTIC | `e61d4198535a` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| R9 | COMPLETE | `088782b4d267` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| R10 | COMPLETE_ANALYTIC_HANDOFF | `df110c72f6fa` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C1 | COMPLETE | `d7575dfe41d7` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C2 | COMPLETE_STATIC_MAPPING | `c65f6de50fe9` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C3 | COMPLETE_DESIGN | `39a613705ae8` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C4 | COMPLETE_PREPARATION_EXECUTION_GATE_PENDING | `2657606a3e7f` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C5 | COMPLETE_IMPLEMENTATION_STATIC_REVIEWED | `4f3f3678b5a2` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C6 | BLOCKED_NOT_RUN_BUDGET_HOLD | `e5a7f5292d5f` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C7 | PARTIAL_STATIC_AND_ANALYTIC_RUNTIME_PENDING | `36f1780e40eb` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C8 | BLOCKED_RUNTIME_EVIDENCE_NOT_RUN | `0e5fe7f25349` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C9 | PARTIAL_STATIC_PASS_NUMERICAL_PENDING | `2f5a0df10330` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |
| C10 | PARTIAL_HANDOFF_COMPLETE_EXECUTION_AND_ZIP_PENDING | `aef787c1e94f` | 원문 / 양쪽 ACK | 32/88 · 중앙27/88 |

원래88IDs/17edges와 기존 계약·status는 변경하지 않았다. L4_ready=false, global_physical_completion=null이다.
