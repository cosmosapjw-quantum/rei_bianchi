# BASS_HE R7: 런타임 closure 보존과 이식성 계약의 분리

## 1. 이번 노드의 결정

사용자가 제공한 재심사 결과를 범위 그대로 받아들인다. CODE_I02_CLOSED=true, full_certificate_fail_closed=true는 현재 허용 입력 도메인과 프로세스 내부 캐시를 포함한 bounded runtime admission의 판정이다. scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN은 별도로 유지한다. Critical 0, Important 0, Minor 2를 다시 Important로 올릴 근거를 만들지 않는다. 또한 outcome-blind=false라는 재심사 제한을 보존한다.

PR15 fresh HEAD는 b8b2fe47a367459f6faf6796eb2f251feacbbd7c이다. PR17은 R7 시작 시 7b276609e828078826ad1969a264c5604c332c3f였다. PR 설명문에는 오래된 HEAD와 테스트 수가 남아 있으므로 ref/파일 identity를 상태 기준으로 사용한다.

이번 재심사의 원시 RETURN_REPORT.json은 확인한 두 PR 연구 namespace에는 아직 없다. 스크린샷에서 읽은 24개 차단/4개 허용, 57+3 focused PASS는 사용자 제공 재심사 보고이지 이곳의 새 실행이 아니다. 원문 경로는 /tmp/BASS_HE_CODE_I02_INDEPENDENT_REREVIEW_20260929T024343Z이다. 원문 회수는 provenance 작업이며, 회수 실패를 이유로 동일 공격 행렬을 자동 재실행하지 않는다.

## 2. scientific_PROMOTE와 코드 closure는 다른 명제다

런타임 검증이 닫혔다고 전이확률의 해석이 확정되는 것은 아니다. 반대로 글로벌 scientific_PROMOTE가 HOLD라고 이미 닫힌 코드 검증을 false로 되돌려서도 안 된다.

현재 저장소 evidence/DR9B_EXPONENT_CHANNEL_AUDIT.json은 Eq.(52)와 Eq.(55)의 정규화 차이를 미해결로 보존하고, production default 변경을 NOT_AUTHORIZED로 적는다. 이는 기존 source/code normalization 이슈다. 이번 R7에서는 그 식을 새로 계산하거나 두 convention 중 하나를 실행 기본값으로 선택하지 않았다.

따라서 다음 노드는 RAW_REVIEW_CLOSEOUT_AND_SOURCE_NORMALIZATION_INVENTORY로 고정한다. 원문 재심사와 코드 identity를 연결하고, 그 다음 과학 작업의 정확한 승인 범위와 source authority를 정리한다. Minor 두 개가 과학적 HOLD의 충분한 이유라고 추정하지 않는다. L2/Krawczyk를 새 필수 선행조건으로 삽입하지도 않는다.

## 3. 이식성: 원본 증거와 목적지 실행 기록을 분리한다

현 validator의 exact hex equality를 isclose로 바꾸지 않는다. 현재 정책 아래서는 잘못된 입력을 허용하지 않도록 보수적으로 거부하며, 잠재 문제는 다른 지원 환경에서의 false rejection이다. 동일 호스트 OpenBLAS 1~4 thread의 동일 결과는 그 실험 범위의 증거일 뿐 cross-host 보장이 아니다.

선택한 후속 설계는 두 기록 방식이다. 원본 O_A는 바이트 단위로 고정하고, 다른 환경 mu_B에서 검증이 필요한 경우 명시적인 재검증 작업으로 새 기록 O_B를 만든다. O_B는 O_A의 parent SHA256, 입력 binding identity, 코드/정책 identity, 목적지 환경 정보와 현지 계산값을 기록한다. 원본의 passed/error를 복사하여 현지 authority로 사용하지 않는다.

형식적으로 x를 정확한 입력, P를 verifier-owned 정책, Q(x,P,mu_B)를 목적지에서의 실제 의미 검증 결과라 하면, 새 기록은 Q에서 구성하고 기존 엄격한 validator로 검사한다. allow_B => fresh_fold_B AND fresh_pair_B가 유지되어야 한다. 원본에서 error가 1 ULP 달랐다는 사실만으로 허용하거나, 아무 ValueError를 잡아 조용히 새 certificate로 대체하는 경로는 금지한다.

이 방식은 원본 기록의 변조와 다른 환경에서의 재계산을 구별한다. 그러나 새 기록은 원본과 byte-identical한 복원이 아니며, 재계산은 독립적인 물리 증명이 아니다. SHA256도 신뢰된 원본 해시와 대조하지 않는 한 생성 주체의 진위를 보증하지 않는다.

이것은 R7에서 선택한 설계 방향이지 구현 완료 선언이 아니다. 기존 PR15 source는 수정하지 않았다. wrapper나 새로운 admission path를 실제로 넣으면 그 변경분의 제한된 검토가 필요하며 기존 closure를 새 코드 전체로 상속하지 않는다.

## 4. normalized matching error의 조건부 enclosure

이전 R6는 거리 행렬 D에 대한 E(D)의 1-Lipschitz 성질을 정리했다. 이번에는 거리를 만드는 정규화 scale의 불확실성까지 포함한다.

named state n_i, local state l_j, 중심 z_c의 성분 k에 대해 현재 계산은

    s_k = max(1, |z_c,k|, |l_0,k|, |l_1,k|),
    d_ij = ||(n_i-l_j)/s||_2

를 사용한다. 여기서 1은 저장소의 dimensionless legacy spectral-coordinate convention에 속한다. 이 규칙을 SI 물리량에 그대로 적용하는 일반식을 주장하지 않는다.

성분 크기 a_ijk=|n_i,k-l_j,k|에 대해 a^-<=a<=a^+, 양의 scale에 대해 0<s^-<=s<=s^+라는 유효한 enclosure가 주어졌다고 가정하면

    L_ij = sum_k (a^-_ijk / s^+_k)^2,
    U_ij = sum_k (a^+_ijk / s^-_k)^2

이고 L_ij<=d_ij^2<=U_ij이다. 실제 근과 중심에 대한 오차 반경이 각각 eta_n, eta_l, eta_c이면 삼각부등식으로 a^- = max(0, |n_hat-l_hat|-eta_n-eta_l), a^+ = |n_hat-l_hat|+eta_n+eta_l를 얻는다. modulus와 max의 Lipschitz 성질로 scale 반경은 sigma_k=max(eta_c,k,eta_l0,k,eta_l1,k)로 둘 수 있고 s^-_k=max(1,s_hat_k-sigma_k), s^+_k=s_hat_k+sigma_k다.

2x2 bottleneck matching의 제곱은

    E^2 = min(max(d00^2,d11^2), max(d01^2,d10^2)).

min/max의 성분별 단조성으로

    E_L^2 = min(max(L00,L11), max(L01,L10)),
    E_U^2 = min(max(U00,U11), max(U01,U10))

가 된다. 현재 코드의 <= 정책을 보존하면 conditional pass는 E_U^2<=tau^2, conditional reject는 E_L^2>tau^2이고 나머지는 unresolved다. equality를 임의로 strict inequality로 바꾸지 않는다.

유효한 root/scale enclosure가 선행하지 않으면 이 식은 실제 spectral certificate가 아니다. 존재·유일성·서로 다른 두 근·ordinal membership도 이 min/max 계산만으로 증명되지 않는다. 이론식은 conditional이고 실제 BASS_HE interval root solver는 이번 노드에서 실행하지 않았다.

## 5. 실제 검산

Fresh WolframLanguageEvaluator는 정규화된 제곱 항의 enclosure와 min/max 단조성을 실수 전칭식으로 확인했고 모두 True를 반환했다. 경계의 <=와 >도 {True,False}로 확인했다. 이는 R6의 도구 내부 오류를 덮어쓴 것이 아니라 R7의 별도 성공 결과다.

Python Fraction으로 1,000개 유리수 표본과 16,000개 거리 박스 꼭짓점을 검사하여 enclosure 위반 0을 확인했다. 경계 6개, 잘못된 계약 5개 거부, zero-width limit과 잘못된 denominator 방향의 negative control도 통과했다. 실제 정책은 decimal 5e-6의 이상적 유리수가 아니라 binary64 0x1.4f8b588e368f1p-18로 해석하여 그 정확한 Fraction을 사용했다.

연구 검산 스크립트는 BASS_HE를 import하지 않으며 spectral solve=0, geometry action=0, Eq55=NOT_RUN이다. 기존 focused/full suite는 재실행하지 않았다.

## 6. 정책 SSOT 처리

지금 상수와 함수 default의 수치는 일치한다. 중복 literal은 Minor maintenance finding으로 보존한다. 향후 정리는 같은 두 값을 하나의 변경 불가능한 정책 선언에서 전달하도록 하되 tolerance를 완화하거나 runtime global mutation을 지원하는 별도 기능으로 확대하지 않는다.

Python 함수 default는 함수 정의 시 평가된다. 따라서 literal을 constant 이름으로 바꾸는 것만으로 runtime global 변경을 따라가는 동적 정책이 되지는 않는다. 현재 요구는 동적 정책이 아니라 producer와 verifier의 코드상 단일 선언이다. 정리 후에는 그 영향 범위의 테스트만 필요하고 새 데이터/물리식 변경이 없는데 56-action replay나 worker sweep를 반복하지 않는다.

## 7. 문헌 근거와 한계

SciSpace로 발견한 Revol-Theveny의 IEEE TC/arXiv:1312.3300 및 Becker et al. arXiv:1707.02115v2의 저자 초록을 원문 레코드에서 확인했다. 전자는 재현성과 interval inclusion을 구별하고, 후자는 roundoff bound의 검증된 certificate checker를 다룬다. 어느 논문도 이번 두-record 설계나 BASS_HE에 대한 구체적인 오차를 증명해주지 않는다. 그 연결은 여기서 명시한 설계 제안이다. 참고 URL과 버전은 LITERATURE_NOTES.md에 보존했다.

## 8. 종료 조건

이 노드는 CODE-I02 closure의 범위를 보존하고, 이식성 설계 방향과 조건부 수학적 enclosure를 산출했으므로 닫는다. 다음 Codex는 또 하나의 전체 hostile rereview를 시작하는 대신 원문 재심사를 게시하고 과학적 source-normalization inventory를 반환한다. Eq55 실행 승인과 모든 물리적 승격 상태는 현재 false/HOLD를 유지한다.
