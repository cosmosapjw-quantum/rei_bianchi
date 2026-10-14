# PHYS28 다음 물리 연구 루프 — 작은 대역폭에서의 문턱 민감도

상태: **PROPOSED / NOT_RUN**. 이 문서는 PHYS27의 후속 한 질문이며 PHYS28 실행 증거가 아니다.

## 1. 다음에 답할 한 질문

**같은 실제 광자 분산 W를 기준으로 δ→0⁺에서 두 영점 W*,δ와 W0,δ의 일차 이동계수를 구하고, 대역 중심 지원구간의 축소와 균일 대역 평균화의 효과를 분리할 수 있는가? 그 국소식은 PHYS27의 δ=0.05 이동량을 어느 정도 설명하는가?**

명칭: PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY. 이 질문 이외의 신규 native solver, gas IVP, 폭·평균·J parameter campaign으로 확대하지 않는다. 두 이동계수가 0일 가능성도 사전 배제하지 않고 실제 유도에서 판정한다.

## 2. 실제 완료한 PHYS27에서 시작

PHYS27은 평균18, 광자 지원[13.61,24.58], 반폭δ0.05인 균일 대역혼합에서 전역 sharp interval, 유일 극값과 끝점, 같은 실제 W에서의 엄격 포함을 유도했다. 수치 지원 끝값 부호에 조건부로 두 영점과 전체 부호 지도를 정리했다.

- Wmin=δ²/3=1/1200; Wmax=(4.39−δ)(6.58−δ)+δ²/3=850231/30000 eV².
- W*,δ≈16.6294590240, W0,δ≈23.3008661823 eV².
- PHYS26 대비 +0.289514369390, −0.119352810041 eV².
- 첫 Decimal80 실행405/405 PASS, root2개×80회, kernel3923회. 새 경로 재현1회 결과 byte 동일. 재현의 독립 물리 credit0.
- 현재 새 code·J·first result identity는 아래와 같다. 전체 원리와 실제 승인 범위는 PHYS27 보고서·판정 파일에서 소비한다.

| 입력 | SHA256 |
|---|---|
| PHYS27 PHYSICS_CONTRACT.json | 46fe6fb98a78ca549f27ed78968850c14bdc12cdd3250892f28e239574005443 |
| PHYS27 새 numerical code | b2eeed5377f46ca1327672991ef9b9f9ebda93696e2c107df3f258a2d98cdd58 |
| PHYS27 FINITE_WIDTH_FIRST.json | 3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314 |
| PHYS22 J 원자료 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |

최종 원본 ZIP·승격·게시 commit identity는 **분리된 PHYS27_PUBLICATION_RECEIPT.json**에서 읽는다. 동봉한 `independent/DECISION_REVIEW.json`의 실제 decision 및 조건을 소비한다. 본 인수문 작성 시 그 최종 판정을 선제 주장하지 않는다. intake source subtree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이며 새 세션에서는 최신 actual head/source와 대조한다.

## 3. 해석적 작업의 계약

δ는 0≤δ<min(L,H), L=4.39, H=6.58에서의 국소 변수다. 광자 분산 W와 중심 분산 V=W−δ²/3를 엄격히 구별한다. fδ(c)=균일평균 k(c+s), α=a+δ, β=b−δ, ℓ=L−δ, h=H−δ를 모두 함께 미분한다.

PHYS27의 경계식과 exact-root 정의를 출발점으로 삼는다. PHYS26의 두 단순근과 양의 ∂W A0,±를 소비하여 implicit-function 조건과 단위부터 확인한다. fδ의 δ=0 우미분, 움직이는 지원 endpoint·이동 중심·확률의 항을 명시적으로 추적한다. 정확식의 미분과 수치 저장근에서 평가한 근사값을 구별한다. PHYS27에서 증명한 평균화 O(δ²)와 약한 극한은 재유도 캠페인 없이 소비해도 된다.

목표 산출물은 W*,δ=V*,0+c*δ+o(δ), W0,δ=W0,0+c0δ+o(δ)의 정당한 국소식과 c의 단위·부호·해석이다. 더 강한 remainder를 주장하려면 필요한 정칙성과 실제 상계를 따로 제시한다. δ=.05의 선형 예측 잔차를 기존 원값과 비교하는 것은 허용하지만 한 폭의 잔차를 수렴률 인증이나 유효 폭 전체의 단조성으로 승격하지 않는다. 다른 두 양의 폭의 분포족이 서로 포함된다고 가정하지 않는다.

## 4. 제한된 새 계산을 쓸 경우

실행 전에 새 계약·직렬화 입력·정밀도·대수 경로·허용오차를 동결한다. PHYS26/27의 저장된 원 근과 source-real constants 및 J를 그대로 사용한다.

- 새 과학 main 최대1회, **새 물리 근 탐색0회**.
- 이전 PHYS19–27 main/suite/root 재실행0회. 실제 읽은 순수 수식을 명시적으로 적응하는 것은 가능하며 old module main을 호출하지 않는다.
- 새 커널/도함수 평가 최대24개, 새 width root sweep0회. 필요 수치비교는 같은 고정 노드에서 다른 대수 표현으로 제한한다.
- PHYS24/25 k″·k‴ 부호 certificate campaign0회, native0회, gas IVP0회, dense LP0회.
- PHYS27 δ=.05 비교값은 원 JSON에서 읽고 재계산하지 않는다.
- 새 프로그램을 만들었다면 portable bundle의 별도 경로 replay1회만 허용하며 독립 물리 credit0으로 계수한다.
- 첫 실패를 보존한다. 사후 허용오차 완화나 root/width 추가로 원하는 부호를 만드는 실행을 하지 않는다. 새로운 필요가 드러나면 주장 범위를 줄이고 이유를 기록한다.

전역 곡률·모멘트 정리, 옛 스펙트럼 감사를 반복하지 않는다. 동결 입력의 값과 의미가 맞는지 선택적으로 확인하고 이번 미분 문제를 해결한다.

## 5. 종료 기준과 증거

정확 국소 미분식·가정·동일 물리 W의 처리, 첫 수치 결과가 있다면 원 stdout/stderr/exit와 모든 실제 횟수, 비례 상수와 실제 δ=.05 관측의 연결, 의미 있는 한계, distinct NONBLIND 최종 판정, 재현가능 묶음과 다음 한 질문을 남긴다. 생성자·수치 검증 설계자는 최종 승격을 판정하지 않는다. 하네스는 실제 채택 모델의 router로 읽고 템플릿 상태를 실행 근거로 쓰지 않는다.

## 6. 기존 권한과 보호 상태

사용자의 다음 물리 연구 루프 요청 및 기존 세션의 같은 branch additive docs 게시 권한을 유지한다. `cosmosapjw-quantum/rei_bianchi`, branch `forward/rust-reion-kernels-20260922`, PR83 draft를 사용하고 새 PHYS28 문서 prefix에만 추가한다. 최신 head를 읽고 expected-head nonforce CAS, 기존 경로·source subtree 보존과 선택 readback을 수행한다. merge, production source/default/runtime 변경, 타인에게 메시지 전송 권한은 포함하지 않는다. 게시 영수증은 hash cycle을 피하여 분리한다. 원격 ZIP 전체 복구를 다시 실행할 필요는 없다.

이 채팅은 fastest-track 이론·가벼운 수치 lane이다. BASS_HE/bass_cr/WU088_HH의 별도 atomic lane을 활성화하지 않는다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED**를 유지한다. 초기 ε²t⁴ 계수의 구조 연구와 실제 emitter·우주론 history admission을 분리한다.
