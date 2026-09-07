# REI G2b denominator reduction — main conversation handoff

STATUS: **G2B_DENOMINATOR_REDUCTION_PROVED / ENDPOINT_NUMERIC_VALUE_BLOCKED**
RETURN_TO: MAIN_CONVERSATION

PR #78의 실제 G2a 결과를 재사용했고 O01--O10, producer, canonical interval은
재실행하지 않았다.

이번 새 결과는 G2b의 남은 계산을 46,080-node 개별 neutral minimum 문제에서
**두 global weighted neutral shares의 단일 denominator 문제**로 줄인 것이다.

고정 totals에서

    X_HI  = sum_i (h_i/H_H)  * (1-x_HII,i)
    X_HeI = sum_i (he_i/H_He) * (1-x_HeII,i-x_HeIII,i)

이고

    D = q_H X_HI + q_He X_HeI.

따라서 stored Cartesian endpoint box에서 D의 exact lower는 모든 charged
fraction을 upper face에 두는 한 번의 affine evaluation이다:

    D_lo = q_H  sum_i (h_i/H_H)  (1-U_HII,i)
         + q_He sum_i (he_i/H_He)(1-U_HeII,i-U_HeIII,i).

nodewise minimum이나 generic interval optimizer가 필요하지 않다. `D_lo>0`이면
그 saved endpoint에 조건부인 G2b owner-current/JVP 경계를 즉시 계산할 수 있다.
`D_lo<=0`이면 independent HeII/HeIII box가 simplex correlation을 잃은 것일 수
있으므로 physical negativity로 해석하지 않는다.

부가적으로 저장 public 최대 width만 사용하면 midpoint denominator에 대한 box
폭 penalty는 보수적으로 `Delta_width < 1.0e-6 cMpc^-1`이다. 따라서 actual
saved midpoint에서 `D_mid>1e-6 cMpc^-1`만 확인해도 positivity가 성립한다.
이것은 충분조건이지 actual endpoint 값이 아니다. initial global state를 endpoint로
대체하지 않는다.

현재 대화에서는 GitHub JSON/text는 읽혔지만 NPZ binary 완전 reconstruction은
connector truncation, local container/Python ClientError, Wolfram MCP 404 때문에
막혔다. 그러므로 실제 D_lo와 conditional L은 **BLOCKED_BINARY_ARRAY_INTAKE**다.
수학적 denominator 구조가 UNKNOWN인 것은 아니다.

상세 증명과 execution boundary는 `PROOF_AND_EXECUTION_BOUNDARY.md`에 있다.
다음 로컬 계산은 전체 solver replay가 아니라 saved arrays 한 번을 읽어 equation (4)
한 개 scalar를 directed/exact arithmetic으로 평가하는 것으로 축소된다.
