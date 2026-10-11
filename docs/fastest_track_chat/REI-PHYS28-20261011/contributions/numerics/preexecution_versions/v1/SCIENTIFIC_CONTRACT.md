# PHYS28 수치 구현의 scientific contract

상태: 첫 실행 전 고정할 연구 계약의 수치 구현. 이 문서는 검증 성공이나 최종 승격 판정이 아니다.

## 목적과 권한

실제 광자 분산 $W$를 고정한 균일 대역 반폭 δ의 우미분에서 두 임계근의 일차 이동계수 $c_*=-B_+/S_+$, $c_0=-B_-/S_-$를 계산한다. 기존 PHYS26 두 저장근과 PHYS27 δ=.05 저장근을 그대로 소비한다. 루트 프로젝트의 `PHYSICS_CONTRACT.json` SHA256 `d9c50cb43d60bf466eb92e91e8e62791fcf84680025c34fc0c42c899ed16fde2`가 과학 계약이며 이 문서는 이를 변경하지 않는다. 사용자의 다음 루프 요청과 실제 읽은 PHYS28 인수문이 제한 계산의 권한이다.

## 정의와 계산 경로

| 양 | 정의 | 계산·검산 |
|---|---|---|
| 물리 분산 | $W=V+δ^2/3$ | 우미분에서 $V′(0)=0$; 순간 질량·평균·분산 미분 보존 확인 |
| 중심·끝점 | $a_δ=a+δ,b_δ=b-δ,v_δ=m+V/(L-δ),u_δ=m-V/(H-δ)$ | 끝점·이동 중심·확률 미분항을 각각 산출 |
| 커널 | $k=F(D^2+3D)\{σ(E)[J_x+J_w(E-χ)]\}$, $F=qN_0κ/180$ | 읽은 PHYS27 degree-three log Taylor Jet와 별도 scalar log-derivative 표현을 명시적으로 적응; 정규화 한 번 |
| 커널 도함수 | $k′=F(D^3+3D^2)\{σ[J_x+J_w(E-χ)]\}/E$ | 각 경로에서 같은 고정4노드만 공동 평가 |
| 폭 기울기 | $B_±=(∂_δ A_{δ,±})(W,0^+)$ | 일반 저장근에서 compact 식과 세 개 이동항 합을 대조; 정확 영점 가정의 간략식 사용 안 함 |
| 분산 기울기 | (S_±=(∂_W A_{0,±})$W$) | secant/tangent 식과 quotient 미분 표현 대조 |
| 계수·잔차 | $c_±=-B_±/S_±$, 실제 이동-$.05c_±$ | 양 대수 경로 대조, 기존 저장값과 선형 예측의 차이를 직접 기록 |

## Convention·고정 입력

metric $(-,+,+,+)$, proper seconds, 에너지 eV, $w$ eV/H. 초기 HeIII ε²t⁴ 계수이며 $[ε^2]$는 둘째 ε 도함수의 절반이다. $k$는 s⁻⁴, $B$는 s⁻⁴/eV, $S$는 s⁻⁴/eV², $c$는 eV다. $a=13.61,m=18,b=24.58,L=4.39,H=6.58$. 원 source binary64 literal의 exact-real 해석을 Decimal 산술로 계산하며 native f64 산술의 재현이 아니다. J는 PHYS22의 직렬화된 전체 decimal 문자열을 사용한다. J·atomic·gas 불확실성을 둘러싸지 않는다.

## 필요한 검증과 적용 제외

Decimal80, 고정4노드, Jet·별도 scalar 두 표현의 σ,k,k' 비교, 이동항 합·분산 기울기 식·고정 W의 moment 미분·기존 저장근의 유한 잔차를 확인한다. 모든 norm·scale·허용오차와 원문 hash는 실행 전에 `PROTOCOL.json` 및 `PREEXECUTION_FROZEN.json`으로 고정한다. 물리 근 탐색과 quadrature가 없으므로 root iteration, 격자·시간간격 수렴 검사 및 width sweep은 해당하지 않는다. 연속체 부호 정리는 별도 이론 산출물이며 이 유한점 비교로 증명하지 않는다. JVP finite-difference campaign은 하지 않으며 양 analytic 표현을 사용한다. 샘플·likelihood·seed가 없는 결정론적 계산이다.

새 과학 main 최대1회, 새 물리 근 탐색0회, 계획한 joint kernel/derivative8회(경로당4회), hard ceiling24회. k와 k' 출력수를 따로 센다. 별도 실행자의 새 경로 replay1회만 허용하며 독립 물리 credit0이다. PHYS19–27 old main/suite/roots0, 새 k''/k''' certificate0, native0, gas IVP0, dense LP0, 새 width root sweep0, production 변경0.

## 독립성·실패·주장 한계

담당자는 parent의 이론식·기존 결과·검증 설계를 읽은 NONBLIND 생성자다. 최종 판정자 역할을 하지 않는다. 두 경로는 같은 원래 HI fit, source-real 상수, J, Decimal 초월함수와 정규화를 공유하며 독립 물리 데이터가 아니다. 별도 decision reviewer와 portability 검증은 owner가 통합한다.

첫 stdout/stderr, exit, UTC와 wall, 실제 호출수 및 실패를 보존한다. 실패를 THEORY_OR_MATH / NUMERICAL / IMPLEMENTATION / RUNTIME_ENVIRONMENT / EVIDENCE_AUTHORITY 등으로 구분하며 조용한 fallback·clipping·허용오차 완화·숨은 재실행을 하지 않는다. 많은 저장 자릿수는 재현 자료이며 수치 계수는 최대 약12유효숫자로 보고한다. 계수는 저장된 근 근사치에서 평가한 수치값이고 interval enclosure가 아니다. .05의 잔차는 단일 폭 진단이며 수렴률 인증·유효 폭 범위·양의 폭 사이 전역 단조성을 주장하지 않는다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 보존한다.
