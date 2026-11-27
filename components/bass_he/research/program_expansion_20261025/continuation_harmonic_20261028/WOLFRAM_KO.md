# HARMONIC10 S07 — R7/C7 단일 Wolfram 검산과 해석

고정된 `scripts/VERIFY_SYMBOLIC.wl`을 evaluator 한 번, timeConstraint15s로 실행했다.
원 응답은 `evidence/wolfram/WOLFRAM_RAW.json`에 보존했다.
**잔차117개가 모두 literal0, Boolean14개가 모두 True로 반환됐다.**

동시에 원 응답에는 **N::meprec 2건**과 이를 알리는 General::messages가 있다.
독립 decimalπ의 두 부호 비교는130자리 정밀도를 요청했지만
`$MaxExtraPrecision=50` 한도에 도달했다. 해당 비교는 True를 반환했으나
실제로130자리 정확도가 확보됐다고 인증하지 않는다.
따라서 CAS 판정은 `QUALIFIED_CORROBORATION_WITH_PRECISION_WARNINGS`다.
경고를 삭제하거나 동일 계산을 다시 실행하지 않았다.

Exact Bernstein normalization/reflection, harmonic primitive, Machin identity,
polynomial examples, orientation/nonseparable/rotation/same-event identities의
117개 symbolic0과 정밀도 경고가 있는 numerical oracle 비교를 구분한다.
기본폭·52회 이분 등 rational inequality 결과도 원 항목별로 남는다.
Production certificate의 근거는 exact rational remainder와 직접 유도이며
CAS numeric130의 달성 여부를 전제로 삼지 않는다.

Wolfram이 실제 원격 CPU와 kernel wall을 제공하지 않았으므로 두 값은 null이다.
client tool latency는 별도 기록이며 CPU로 바꾸지 않는다.
Context lookup1과 evaluator1은 서로 다른 행위다.

비분리 독립식은 CAS에서 약
\(Y=0.040688719519895197\),
\(H_A=0.262362928177403248\),
\(Y/H_A=0.155085628150873903\)로 반환됐다.
Naive marginal과의 차이는 약0.008006679081951247이다.
이는 선언한 manufactured 법칙의 결과이며 actual DCS/flux 사건률이 아니다.

최초24PASS+1FAIL 및 targeted1PASS의 로컬 검증 기록을 변경하지 않는다.
저장값 plot과 같은 recorded pass의 결과 검토 뒤에만 새 reference를 채택한다.
현재 **local9/14 · central28/88**, 세 physical input open, L4=false, production=NOT_APPROVED.
