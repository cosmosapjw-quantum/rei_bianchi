# 작은 STF 성분 사용

`h1_ci_source`가 반환한 `J`는 직접식 `-nH*kappa2*pi_e`로 계산한 전자 STF source다. 아주 작은 STF는 등방 성분이 큰 `S`에서 뺄셈으로 재구성할 때 binary64에서 소실될 수 있다. 따라서 호출자는 반환된 `J`를 사용한다.

독립 review의 한 targeted control에서 pi_e=diag(1e-200,-1e-200,0)Pa에 대해 직접 J는 diag(-1.684966749100594,+1.684966749100594,0)e-210 Pa/s를 유지했고, donor projection은0이었다. 80digit Decimal 곱과의 상대차는2.220446049250313e-16이다. 해당 상태는 roundoff 위험을 판별하는 수치 control이며 물리적 유한 비등방성 검증이 아니다. code/data/receipt는 바뀌지 않았다.
