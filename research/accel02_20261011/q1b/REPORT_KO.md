# REI-ACCEL02 Q1B: 보존형 셀 표현과 장기 실행 준비 연구

**현재 결론은 `LOCAL_COMPONENTS_ONLY; FULL_HISTORY_HOLD`이다.** C08R1에서 기각된 Q1A의 후속으로, 고정 공변 운동량 셀마다 광자 수와 에너지를 독립적으로 저장하는 Q1B를 구현했다. 새 source/초기조건 분할은 저장된 기준과 약 $10^{-15}$ 수준에서 일치했다. 빈 셀과 새 source 진입의 수학적 경계를 명시했고, 독립 검토에서 발견한 좁은 지지구간의 거짓 성공을 수정했다. 완전한 상태·history prefix를 함께 복원하는 checkpoint 기능도 새 manufactured 문제에서 확인했다.

Q1B의 실제 재이온화 전구간 실행은 아직 시작하지 않았다. 새 native adapter는 로컬 Rust toolchain 부재를 기록한 뒤 별도 targeted GitHub CI에서 컴파일하고 여섯 개 protocol test를 통과했다. 실제 native opacity의 내부 셀 연결과 초기 UVB 진단도 완료했다. C1은 추가 local 오차 여유 기준을 넘고 C2는 통과했으며, 전구간 후보로의 승격은 보류했다. Source-entry solver와 production checkpoint 연결도 후속 gate이다.

이 보고서는 C09 증거, 좁은 지지구간 수정 후의 기록, 실제 native CI 결과를 종합한다. `C09A_STATUS.json`과 `INDEPENDENT_DECISION_INITIAL.json`은 수정 전 상태를 보존한 기록이며, 좁은 지지구간의 현재 근거는 `RECONSTRUCTION_REPAIR_EVIDENCE.json`과 `NARROW_SUPPORT_CORRECTED.json`이다. CI 이전의 `INDEPENDENT_DECISION_FINAL.json`은 R1을 제한된 범위에서 종결했지만 native 실행 부재는 당시 상태로 남겨 두었다. 후속 CI 증거의 독립 판정은 그 시간 순서를 보존하여 통합한다. C09A의 GitHub 게시와 Drive·Dropbox 이중백업은 실제 영수증으로 확인됐다. 실제 host model은 `UNKNOWN`이며, Astra 하네스 채택은 모델 자체의 확인을 뜻하지 않는다.

## 1. 이번 루프의 범위와 유지한 기준

기존 RUN002·EVENT003·Q0와 완료된 Q1A history를 반복하지 않았다. G2의 환경 중단을 완전한 history나 재개 가능한 solver 상태로 해석하지 않았다. 새 작업은 Q1B source/초기조건, 재구성의 국소 성질, native 입력 인터페이스, 완전한 checkpoint에 한정했다. 물리적 Q1B coupled ODE 호출은 0회이다. 새 checkpoint fixture의 소규모 manufactured 적분은 실제 재이온화 계산과 구분한다.

배경은 non-tilted axisymmetric Bianchi I이며, 새 source 검증에는 FLRW $r=0$을 사용했다. 고정 HM12 표와 보간법, UVB를 초기 광자장으로만 쓰는 계약, emissivity를 계속되는 광자 source로 쓰는 계약, 조건부 H/He 초기 기체 상태, Case-A와 기존 native 원자·열 물리를 유지했다. CR/RCT, secondary cascade, diffuse 재흡수 및 배경 backreaction을 추가하지 않았다. 이러한 별도 lane의 완료를 이번 결과로 선언하지 않는다.

| 검증 항목 | 유지한 전역 허용 기준 | 이번 실행 여부 |
|---|---:|---|
| 전체 평균 redshift 구간 | $15.9\rightarrow4$ | Q1B 미실행 |
| 동일 셀 시간 refinement, 9 history fields | $2\times10^{-6}$ | 미실행 |
| 에너지 잔차 / 초기 에너지 | $10^{-9}$ | 전역 미실행 |
| 광자 수 잔차 / 초기 수소 수밀도 | $10^{-9}$ | 전역 미실행 |
| geometry | $10^{-11}$ | 전체 history 미실행 |
| spectral refinement, 24 fields/moments | $10^{-3}$ | 미실행 |
| 상태 영역 | 유한값, 물리적 기체 영역, 비음수 광자; clipping 금지 | 국소 API에서만 검사 |

Spectral 비교는 129개 epoch와 65개 부분집합에서 각각 그 집합의 fine-history 진폭으로 정규화한다. 기준 진폭이 정확히 0이면 절대 차이도 정확히 0이어야 한다. 전역 ledger는 필요한 saved epochs와 기록한 segment endpoints를 포함한다. 이번 $10^{-12}$ source engineering gate, $10^{-7}$ reconstruction 국소 수치 기준, checkpoint fixture의 오차 기준은 각각 별개이며 위 전역 기준을 대체하지 않는다.

## 2. 저장량과 공통 광자–기체 연산자

고정 $q$ 셀과 초기 각도에서 $E=R_c(t)q$, $\dot R_c=-\lambda_c R_c$라 쓰고,

\[
N_c=\int F_c\,d\ln q,\qquad
Q_c=\int qF_c\,d\ln q,\qquad U_c=R_cQ_c
\]

를 정의했다. 실제 저장 변수는 $N_c,U_c$이다. 이 선택은 광자 수를 시간에 따라 변하는 대표 에너지로 나누어 복원하는 경로를 없애고, 광자 수 및 에너지 ledger를 저장 상태의 선형 합으로 만든다. 물리적 팽창 일은 그대로 남는다. 양의 power-law로 셀 내부 스펙트럼을 복원하는 것은 명시적인 **수치 closure 변경**이며, 실제 연속 스펙트럼과 동일하다고 가정하지 않는다.

고유 부피/기준 부피 비를 $V=a_{\rm rel}^3$라 하고,

\[
K_{0\alpha c}=c\int\sigma_\alpha(R_cq)F_c\,d\ln q,
\qquad K_{E\alpha c}=c\int R_cq\,\sigma_\alpha(R_cq)F_c\,d\ln q
\]

를 같은 quadrature에서 얻으면,

\[
\dot N_c=S_{Nc}-\sum_\alpha n_\alpha K_{0\alpha c},\qquad
\dot U_c=S_{Uc}-\sum_\alpha n_\alpha K_{E\alpha c}-\lambda_cU_c,
\]

\[
\Gamma_\alpha=V^{-1}\sum_cK_{0\alpha c},\qquad
\mathcal H_\alpha={\epsilon_{\rm eV}\over V}
\sum_c(K_{E\alpha c}-\chi_\alpha K_{0\alpha c}).
\]

광자 에너지 손실, 화학적 결합 에너지 증가, 열 증가가 동일한 $K_0,K_E$를 사용하므로 대수적으로 짝을 이룬다. 흡수체 밀도로 나누지 않으므로 $n_\alpha=0$에서도 per-absorber rate를 정의할 수 있다. 이 유도는 native 구현 및 전역 오차 통과의 대체물이 아니다. 화학적 χ와 cross-section turn-on 값 $13.60,24.59,54.42$ eV는 기존의 서로 다른 상수로 유지한다.

비등방 계산에서는 각도별 $R_c,\lambda_c$를 합 안에 유지해야 한다. 유한 각도 quadrature의 $\sum w_cR_c^{-3}=V$가 일반적으로 자동 성립하지 않으며, 이번 FLRW source 검사로 이를 인증하지 않았다. 현재 지지구간 상한 $\min(q_R,50000/R_c)$은 각 방향의 단조 redshift 범위에서만 허용한다. 방향별 blueshift가 생기는 확장에는 과거에 도달한 지지구간과 provider 에너지 범위의 새 계약이 필요하다.

## 3. Source와 초기조건: 완료된 구현·검증

C1은 10 eV부터 $q_{\max}=168999.99999999997$ eV까지의 64개 log 기본 구간에 초기 UVB의 서로 다른 양측 값을 갖는 19개 중복 에너지, 세 cross-section threshold, 50000 eV를 합쳐 **87개 에너지 셀**로 고정했다. C2는 각 C1 셀을 log 좌표에서 한 번 이등분한 **174개 에너지 셀**이다. 두 경우 모두 Gauss 각도 2개를 사용하므로 전체 셀 수는 174와 348이다. 초기 경계와 각도 배열은 `GRID_C1.json`, `GRID_C2.json`에 고정했다.

54.37903440052643 eV와 54.42 eV는 별도 경계로 유지했다. 전자는 UVB의 불연속 위치이며 emissivity에도 중복 행이 있지만 그 두 ordinate는 같다. 서로 가까운 숫자라는 이유로 이를 cross-section threshold와 합치지 않았다.

현재 물리 에너지에서 셀과 source band의 교집합  

\[
E_l=\max(R_cq_L,10),\quad E_h=\min(R_cq_R,50000)
\]

에 대해

\[
S_{Nc}=w_cR_c^{-3}\int_{E_l}^{E_h}s_{\log}\,d\ln E,
\qquad
S_{Uc}=w_cR_c^{-3}\int_{E_l}^{E_h}E s_{\log}\,d\ln E
\]

를 구현했다. $S_Q=S_U/R$이며 $E_h\le E_l$이면 두 source는 정확히 0이다. 10 eV 아래로 redshift된 기존 광자를 지우는 연산은 없다. 초기 UVB도 $R=1$에서 N과 U를 각각 적분했다.

| 고정 grid | source 최대 정규화 차이 | 초기 UVB 최대 정규화 차이 | 국소 기준 |
|---|---:|---:|---:|
| C1: 87 × 2 | $1.4459741734\times10^{-15}$ | $5.8365698482\times10^{-16}$ | $10^{-12}$, PASS |
| C2: 174 × 2 | $1.6475334512\times10^{-15}$ | $2.7892453094\times10^{-15}$ | $10^{-12}$, PASS |

Full band 및 H I/He I/He II threshold-selected band의 number·energy를 proper/reference 단위로 검사했고, 129/65 epoch 집합을 각각 평가했다. 계산 시간은 4.035초였다. 저장된 Q0 기준값을 읽어 새 셀들의 합과 비교했으며 Q0 기준을 다시 생성하지 않았다. 여섯 개 새 테스트는 상수·log-linear 함수의 해석 적분, 불연속, 빈/부분 진입, R·단위 인자, 잘못된 입력 거부, nested grid를 다룬다. 최초 기능 부재 RED와 실제 GREEN 로그를 보존했다.

`SOURCE_IC_CELL_CHECK.json`과 `SOURCE_C1.npz`, `SOURCE_C2.npz`가 실제 근거이다. 새 적분은 고정 HM12 데이터, redshift 보간, analytic exponential weights를 기존 기준과 공유한다. 따라서 이 결과는 **선택된 보간법의 새 셀 분할 검증**이다. 독립 물리 데이터 검증이나 실제 continuum 정확도를 뜻하지 않으며, threshold-selected source 수치가 opacity·photoheating 적분을 대신하지 않는다. 독립 검토는 source/IC 및 고정 grid 구성에 한해 국소 사용을 승인했다.

## 4. 빈 셀·진입·재구성에서 드러난 실제 blocker

양의 power-law 복원에서 내부 평균 $m=U/(RN)$는 $q_L<m<b$를 만족해야 한다. 내부에서는 $dm/dp=\operatorname{Cov}(q,\ln q)>0$이므로 유일한 지수 p가 존재한다. 고정 시간의 kernel $g(q)$에 대해서는

\[
D_g={\operatorname{Cov}(g,\ln q)\over\operatorname{Cov}(q,\ln q)},\quad
\partial_N[N\langle g\rangle]=\langle g\rangle-mD_g,\quad
\partial_U[N\langle g\rangle]=D_g/R
\]

를 사용한다. 그러나 빈 원점에는 일반적인 Fréchet Jacobian이 존재하지 않는다. $q\in[1,2],R=1,g=q^2$에서 방향 $(1,1)$, $(1,2)$의 미분값은 1,4인데, 그 합 방향 $(2,3)$에서는 $14/3\ne5$이다. 따라서 `EMPTY`는 정확한 0 rate와 `NO_JAC_AT_EMPTY`를 반환해야 하며, 0 Jacobian이나 가짜 photon seed를 만들어 일반 BDF에 넘길 수 없다. 허용된 방향의 미분과 일반적인 행렬 Jacobian을 구분해야 한다.

새 상단 source 진입 시 매끄러운 비영 source와 양의 팽창률을 가정하면 $N\sim\tau^2$, $Q-q_LN\sim\tau^3$이며 축적된 광자의 평균은 지지구간의 약 1/3 위치에 들어온다. 순간 source의 약 1/2 위치와 다르다. 이 유도는 임의 seed가 부적절함을 보여 주지만, 실제 startup 구현을 검증한 것은 아니다. 다음 시도할 알고리즘은 8절과 SOURCE_ENTRY_NEXT.md에 별도로 제안했다. 연속 방정식의 realizability 보존도 BDF predictor·Newton trial의 영역 보존을 보장하지 않는다.

독립 검토는 최초 reconstruction 구현이 매우 좁은 지지구간에서 잘못된 성공을 반환하는 R1을 발견했다. 임의 분포에도 정확한 항등식

\[
\int {q-a\over b-a}F\,d\ln q={Q-aN\over b-a}
\]

을 검사했을 때, $a=50000$, 상대 폭 $10^{-12}$, 평균 위치 1/3인 사례에서 정확한 $K_0=1/3$ 대신 0.3345574493을 반환하고도 성공으로 판정했다. 이는 단순 quadrature 차수 증가로 숨길 문제가 아니다. 절대 q 기준 오차와 큰 Jacobian에 지배된 공통 척도가 셀 내부 좌표의 손실을 놓쳤다.

수정은 $(m-a)/(b-a)$에 대한 역변환, `log1p`/`expm1`을 이용한 지지구간 상대 좌표, 각 moment/Jacobian 성분의 분리된 오차 척도, 상수 kernel covariance의 정확한 처리에 집중했다. 수정 후 일곱 개 국소 테스트가 통과했다. 독립 affine 검사에서 상대 폭 $10^{-4},10^{-6}$의 오차는 각각 $2.0\times10^{-15},4.39\times10^{-12}$였다. $10^{-8}$부터 $10^{-14}$까지의 더 좁은 사례는 현재 binary64 q-kernel API가 수치를 분해할 수 없다고 **명시적으로 거부**한다. 이를 미세 source 진입 해결로 해석하지 않는다.

원 실패 코드와 RED, 중간 수정 실패, 최종 GREEN, 독립 반례를 모두 남겼다. 수정 후 코드의 유효 영역 밖에서 성공을 허위 보고하는 문제는 차단했지만, 실제 source-entry, native threshold 양측 trace, 빈 셀 방향미분 API, 전체 N/U–gas Jacobian, 비실현가능 trial의 solver 처리는 아직 미완료다. 현재 64/128 임시 quadrature 비교는 자체 진단이며 일반적인 엄밀 오차 상계도 closure 오차 추정도 아니다.

## 5. Native 연결과 checkpoint의 현재 도달점

새 별도 crate의 `CELL_RHS_V1`은 $N,U,S_N,S_U,K_0,K_E$를 받아 기존 gas/axisymmetric owner를 호출하도록 작성했다. 흡수체가 없거나 빈 photon 셀인 경우를 처리하고, 공통 moment를 광자 손실·기체 rate·열·counter에 연결한다. 실제 cross section 적분이나 새 Jacobian을 이 ABI가 자동으로 제공하지는 않는다.

로컬 최초 기록 `NATIVE_VALIDATION.json`은 `IMPLEMENTED_BUILD_BLOCKED_NO_TOOLCHAIN`이다. Rust compiler 부재와 공식 toolchain 다운로드의 연결 실패는 실행 환경 문제로 기록했으며 물리 실패로 분류하지 않았다. 이후 [GitHub CI run 38100360778](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/38100360778)은 commit `8bc4357dfcd3cbaa9ffc838cdd05134255373226`을 실제로 build했고, 여섯 개 targeted protocol test가 0.018초에 통과했다. 로그·compiler 기록·commit·binary hash는 `evidence/NATIVE_CI_C09A/`에 있다. 내려받은 새 바이너리의 SHA256은 `e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f`로 확인됐다. 이전 실행 환경 실패를 삭제하거나 처음부터 성공한 것처럼 바꾸지 않는다.

검사 범위는 광자·화학·열 pairing, 빈 셀, volume rescaling, source와 비등방 work, signed CMB, 흡수체/He 부재, 잘못된 moment 입력 거부이다. 원 gas provider와 새 bridge가 공유하는 부분은 명시한 그대로이며, 이 통과가 Grackle 원자 물리나 셀 closure의 독립 재검증을 뜻하지 않는다. 새 바이너리가 존재한다는 사실만으로 실제 photon opacity와 source-entry solver가 완성되는 것도 아니다.

Checkpoint는 임시 파일 묶음이 아닌 완전한 immutable generation으로 설계했다. 상태, 저장 epoch prefix, counters, scales, extrema/ledger metadata, source/grid/control identity를 함께 저장하고 manifest를 확인한다. 여덟 개 targeted test와 새 manufactured 실험에서 segment 경계의 fresh BDF 재시작을 검사했다. 복원 배열·metadata는 동일했고, 분할 재시작과 중단 없는 실행의 차이는 0, 해석해와의 최대 절대 차이는 $9.309\times10^{-12}$였다.

이 결과의 범위는 **generic checkpoint와 새 manufactured segment 복원**이다. BDF 내부 상태의 bitwise 복원을 주장하지 않으며, 실제 Q1B provider/driver와의 연결도 아직 없다. 실제 실행 중에만 알 수 있는 accepted-step extrema와 ledger events를 수집하는 production hook, authoritative input identity, 원격 durable upload의 확인이 별도로 필요하다. 자기 manifest의 일관성과 원본의 진위, upload 확인과 실제 restore 검증은 구분한다.

## 6. 다음 실행 DAG와 과학 결과로의 연결

| 순서/병렬 lane | 다음 구체 작업 | 종료 조건 |
|---|---|---|
| A: native 실행·연결 | 완료된 build와 6 protocol test 증거를 독립 판정하고 실제 moment caller를 연결 | 실행·identity 증거 채택; caller 연결은 별도 확인 |
| B: 실제 opacity | 고정 native σ에 대한 threshold-split $K_0,K_E$, endpoint 내부 trace; 64/128 임시 quadrature와 C1/C2 closure 오차 분리 | 실제 kernel 국소 기준 통과; manufactured kernel로 대체 금지 |
| C: source 진입/solver | 좁은 신규 지지구간을 정확히 다루는 좌표·startup 선택, 영역 밖 nonlinear trial 처리, 내부·경계 N/U–gas Jacobian | 영역 보존·짝지은 counters·오차 차수·stiff 동작의 실제 증거 |
| D: production checkpoint | 선택된 실제 driver의 accepted-state/prefix/ledger hook과 identity를 generic generation에 연결 | 새 실제 경로의 중단/복원 비교 통과; stale/torn 상태 거부 |
| E: 통합 국소 결정 | A–D의 실제 근거 및 source/IC 결과를 독립 검토 | 명시적 local GO; 파일 존재나 이론식만으로 통과 금지 |
| F: 전체 history | 고정 C1/C2 후보와 미리 정한 동일 grid 시간 비교를 $z=15.9\to4$에서 실행 | 기존 모든 전역 허용 기준 평가 |
| G: 과학 비교 | 채택된 FLRW 기반 위에 Bianchi 비교쌍과 실제 BASS receiver 연결 | 새 history 및 receiver 자체의 증거로 판단 |

Native caller 연결과 B는 solver 설계와 병렬 진행할 수 있고, D의 공통 계약 부분도 먼저 준비할 수 있다. C의 경계 처리 결정은 전체 Jacobian과 production 연결을 실질적으로 좌우하므로 의존성을 명확히 유지한다. 양의 source 추가와 implicit absorption을 결합하는 시간 알고리즘은 별도 후속 설계 후보이며, 아직 채택된 생산 solver나 검증 결과가 아니다. 국소 gate가 모두 끝나면 전구간으로 진행하고, 근거 없이 좁은 redshift 반복 검증이나 point-grid 증식을 다시 시작하지 않는다. 반대로 source 합이 정확하다는 이유만으로 미완성 entry solver를 장기 실행에 넣지 않는다.

이번 결과는 source quadrature 오류를 제거할 수 있는 구체적 구현과 장기 실행의 복구 기반을 제공했다. 아직 새로운 채택 가능한 scientific plot은 없다. 과거 Q1A의 실패 그림은 계속 수치 진단이며, 이번 source/IC의 작은 오차가 진화된 $x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},T,\Gamma$의 정확도를 예측하지 않는다. BASS의 기존 reduced N4 채택 범위는 그대로 유지하고, 새로운 native history/receiver는 `HOLD`이다. 전체 실행 시점과 wall time은 아직 통과하지 않은 solver/native 단계의 실제 성능 없이 확정하지 않는다.

## 7. 재개에 필요한 최소 파일

`RUN_CONTRACT.json`, `GRID_C1.json`, `GRID_C2.json`, `theory/THEORY_CONTRACT.md`, `theory/EMPTY_CELL_DECISION.json`이 고정 정의와 경계를 제공한다. 실제 source 증거는 `evidence/SOURCE_IC_CELL_CHECK.json` 및 `SOURCE_C1.npz`, `SOURCE_C2.npz`; reconstruction의 현재 증거는 `evidence/RECONSTRUCTION_REPAIR_EVIDENCE.json` 및 `review/NARROW_SUPPORT_CORRECTED.json`; checkpoint는 `evidence/CHECKPOINT_VALIDATION.json` 및 `CHECKPOINT_MANUFACTURED.json`; native는 최초 `evidence/NATIVE_VALIDATION.json`과 후속 `evidence/NATIVE_CI_C09A/` 및 CI receipt를 함께 읽는다. 최초 실패 증거는 보존하며 현재 결정을 판정할 때 수정 후 구현 identity와 혼합하지 않는다. `C09A_REMOTE_RECEIPT.json`은 게시 commit/tree와 두 백업 provider의 실제 성공 응답을 보존하며, 이 백업 판정은 `UPLOAD_VERIFIED_NOT_RESTORE_VERIFIED`이다.

후속 작업의 첫 행동은 **완료된 증거를 읽고 source-entry solver 및 C2/C3의 새 고정 후보 gate를 병렬로 진행하는 것**이다. 완료된 source reference나 이전 history를 다시 계산하는 것이 재개의 선행 조건은 아니다.

## 8. 최종 추가 결과: 실제 native opacity와 다음 후보

`opacity_native.py`는 고정 N1 binary의 SIGMA를 직접 호출한다. 세 새 binding 검사가 통과했고, C1/C2의 522개 초기 셀 모두 결과를 반환했다. 실제 UVB 분포를 직접 적분하는 별도 opacity 기준의 32/64차 차이는 최대 $1.016\times10^{-14}$였다. 이 기준은 power-law 복원과 독립이지만 동일한 물리 데이터·단면적 및 Gauss 계열을 사용한다.

| 초기 시각 비교 | 최대 상대 차이 | 사전 local $10^{-4}$ 기준 |
|---|---:|---|
| C1 / 직접 UVB opacity | 0.00033628985 | FAIL |
| C2 / 직접 UVB opacity | 6.336521e-05 | PASS, IC 한정 |
| C1 / C2 | 0.00031569048 | FAIL |

이 최초 실패를 보존했다. 전체 history의 $10^{-3}$ 기준보다 작은 초기 차이라는 이유로 별도 local 기준을 완화하지 않는다. 다음 고정 후보는 C2(174개 energy cells)를 기준으로 C3(348개)를 한 번 이분할하는 계획이다. C3는 아직 만들거나 계산하지 않았으며, 다음 루프에서 새 C3만 저장된 opacity 기준·C2 및 Q0 source 값에 대조한다. C1/C2나 기존 history를 다시 실행할 필요는 없다.

동시에 `theory/SOURCE_ENTRY_NEXT.md`의 실제 source 누적→양의 implicit absorption→native gas 네 변수 해법을 구현한다. 이는 새 first-order 시간 알고리즘 제안이다. Grey scalar recurrence의 약 1차 수렴만 확인했으며 production 구현·전체 수렴·실제 복구는 주장하지 않는다. 특히 combined native work에서 photon redshift work를 이중 계산하지 않도록 소유권을 분리해야 한다.

Native의 추가 독립 판정은 `review/INDEPENDENT_NATIVE_CI_ADDENDUM.json`에서 국소 bridge만 승격했다. 기존 repository verify는 Q1B 이전부터 cargo fmt 단계에서 실패했고 이번에도 같으므로 repository 전체 CI 성공으로 표현하지 않는다. 새 targeted native CI와 이 상태는 구분한다. 현재 실행 순서는 `NEXT_DAG.json`과 `RESUME_PROMPT_KO.md`를 따른다.

실제 opacity 추가 독립 판정은 `review/INDEPENDENT_OPACITY_IC_ADDENDUM.json`이다. Native moment 계산 대상 468개와 정확한 dormant 셀 54개로 총 522개이며, 실제 binding/진단만 채택하고 C1/C2 local headroom 실패와 전구간 HOLD를 유지했다.
