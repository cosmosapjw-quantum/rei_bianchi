# R8–R10 이론 판정과 구현 인계

2026-10-24 UTC, /root. R6 및 R7의 실제 결과를 확인한 판정이다.

## R8 판정

**DERIVED_SCOPED.** 양의 bilinear DDCS 보간의 유한 window 모멘트, 축대칭
검출 전자 tensor/covariance, 선형 functional과 positive-denominator ratio의
box 극값 구성이 고정된 가정 아래 유도됐다.
원전 담당자와 별도 수학 검토를 맡은 /root/angular_source_search의 R6는
PASS이고 blocking finding은 0개다. 구현 작성자는 해당 검토를 수행하지 않았다.
R6은 THEORY/CONTRACT/source CSV의 정확한 identity를 기록했다.

Wolfram Language evaluator를 timeConstraint=10으로 한 번 실제 실행했다.
왼쪽/오른쪽 hat의 r=0,1,2 적분, sqrt(E) left-hat 적분, ratio derivative,
two-point variance identity의 잔차는 전부 0이었다.
코드·원출력·호출 시각은 evidence/wolfram/R7_RAW.json에 있다.
관측된 tool wall은 13.307 s다. 네트워크/도구 overhead를 kernel 실행 시간으로
바꾸지 않는다. 실제 remote CPU는 UNKNOWN_NOT_ZERO이며 local scientific
20 CPU s/60 wall s 예산과 분리한다. 사용 가능한 두 호출 중 한 번을 소비했다.

새 strong no-go를 주장하지 않는다. Node 보존 positive bump의 관찰은
보간 가정의 역할을 설명하며 문헌 대비 새 불가능성 성과가 아니다.
수치 출력 admission은 C6–C9가 끝날 때까지 보류한다.

## R9 식–데이터–코드 연결

| 입력/식 | 구현 위치의 계약 | 실제 검증 |
|---|---|---|
| Table IV 40 values, primary 32 | load_source, source JSON/CSV exact check | immutable CSV hash와 두 형식의 수치 일치 |
| A_i^(r), B_j^(q) | hat_integral_weights | closed-form constant/affine controls와 독립 cellwise GL16/32 |
| R_rq, J_r(E_j) | window_moments | dOmega=2pi dmu, 10^-23 SI factor, 단위·support |
| Tensor와 covariance | same window_moments result | trace, 축대칭, PSD, Cauchy-Schwarz |
| Linear box extrema | linear_box_extrema | signed coefficient endpoint witness |
| Ratio threshold scan | ratio_box_extrema | n<=6 모든 vertex oracle, signed b/ties/scale invariance |
| Linear-theta 대조 | theta_interpolation_control | radian의 sin(theta)dtheta, 같은 입력과 window |
| 결과 그림 | plot_results | data error와 deterministic box 범위 구분, root visual review |

Exact extrema의 수학적 결론은 **각각의 scalar linear 또는 linear-fractional
functional**에 적용된다. 서로 다른 ratio의 extremizer를 한 물리 상태로
합치지 않는다. Nonlinear covariance의 exact uncertainty extrema는 이 계약의
출력이 아니다. 이 확인 사항과 theta의 radian Jacobian은 기존 계약의 구현
검증에 포함하며 새로운 검토 단계를 추가하지 않는다.

## R10 이론 단위의 종료와 다음 실행

R1–R10의 이론 결과는 고정 조건부로 닫혔다. 전체 요청은 구현·수치 결과·독립
C9·게시·백업·중앙 반영을 남기고 계속 진행한다.
다음 명령은 unit cwd에서 Python -B code/run_bounded.py tests,
이어서 actual_analysis, plot이다. lower-tier coding agent가 CONTRACT의
누적 예산/실패 중단 규칙으로 순차 실행한다. 변경 없는 HE-X1/HE38/Hex는
다시 실행하지 않는다. 실패가 나면 실제 실패 입력과 원인을 root에 반환하고
관련된 수정 한 번만 승인받는다. 재실행은 남은 예산을 소비한다.

허용된 최종 claim은 measured-input **conditional finite-window moments**다.
HE-ANG 전체 source/frame/joint-event provider의 상태는
SOURCE_INPUT_PENDING이며 이번 이론 종료로 승격되지 않는다.

## 보존과 게시의 상태

각 R/C 단계는 LOOP_PROGRESS.json의 개별 행에 근거, DAG 선행 단계,
완성도, publication 및 Dropbox/Drive ACK를 기록한다. 닫힌 단계가 같은
검토 checkpoint를 공유하면 그 identity를 각 행에 연결한다.
과학 코드/결과는 C9 이후 expected SHA를 사용해 새 draft branch에 게시한다.
백업 ACK와 Git publication은 실제 도구 응답이 있을 때만 완료로 바뀐다.
