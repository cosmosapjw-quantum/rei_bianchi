# 사용자 지정 19반응 목표망과 현재 provider 범위

제공 그림의 오른쪽 반응식 목록을 기준으로 19개 ID를 그대로 보존했다. 왼쪽 그림의 일부 번호/화살표는 오른쪽 식과 대응하지 않으므로 코드 반응 방향의 근거로 사용하지 않는다. 그림 원본과 SHA-256은 `TARGET_NETWORK_19.json`에 기록되어 있다.

| ID | 오른쪽 목록의 반응 | 현재 선택 계보의 범위 |
|---|---|---|
| 1 | H I + γ ↔ H II + e⁻ | 기존 H/He 전자계수·photo owner; 전체 목표망 미완료 |
| 2 | He I + γ ↔ He II + e⁻ | 기존 H/He 전자계수·photo owner; 전체 목표망 미완료 |
| 3 | He II + γ ↔ He III + e⁻ | 기존 H/He 전자계수·photo owner; 전체 목표망 미완료 |
| 4 | ⁴He + γ ↔ ³He + n | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 5 | ⁴He + γ ↔ T + p | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 6 | ⁴He + γ ↔ D + D | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 7 | ³He + γ ↔ D + p | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 8 | D + γ ↔ p + n | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 9 | T → ³He + e⁻ + ν̄ₑ | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 10 | n → p + e⁻ + ν̄ₑ | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 11 | ⁷Li + γ ↔ ⁴He + T | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 12 | p(n,γ)D | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 13 | D(p,γ)³He | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 14 | D(D,p)T | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 15 | D(D,n)³He | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 16 | T(D,n)⁴He | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 17 | ³He(D,p)⁴He | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 18 | ³He(n,p)T | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |
| 19 | T(α,γ)⁷Li; α ≡ ⁴He | 선택한 native 계보 결합 미완료; metals에서 구현하지 않음 |

## 전자와 핵의 장부

전자 광이온화는 핵종·핵전하를 유지하면서 이온전하와 자유전자 수를 각각 하나 늘린다. 역방향 재결합은 자유전자를 하나 소비한다. 반면 β⁻ 반응은 핵전하를 하나 늘리고 전자·반중성미자를 방출한다. 이 둘을 같은 electronic rate 또는 binding-energy 항으로 처리할 수 없다.

핵반응의 원자 껍질과 생성물 이온전하는 별도 projection 문제다. 특히 n→p+e⁻+ν̄ₑ의 p를 곧바로 중성 H I로 배치하지 않는다. 핵 결합/정지질량 변화, 방출 입자, photon ledger, 열에 실제 남은 에너지도 원자 재결합계수만으로 채울 수 없다.

목록 7↔13, 8↔12, 11↔19에는 정·역방향의 물리적 중첩이 있다. 이는 19개의 사용자 목표를 줄이는 이유가 아니다. 계수의 상세평형 관계를 사용하려면 해당 핵 source, 통계 인자, 분포와 온도 전제를 따로 검증한다.

## 이번 선택형 Li/Be 코드의 의미

Li6/Li7 source는 이미 존재한 PR150의 전자 CI/RR/DR 구현을 고정99 grid로 호환 이식한다. Be의 세 계수는 VF1996 total-RR이며, Be III→Be II, Be IV→Be III, Be V→Be IV의 number contribution만 계산한다. 두 경우 isotope label은 `ElementalElectronicEquality`이고 isotope-specific 실험 계수라는 주장을 하지 않는다.

이 전자 과정들은 목록 11의 ⁷Li 광핵 분해나 19의 T+α 핵 포획을 구현하지 않는다. Be7 label도 전자계수 호출만 허용하며 electron capture·decay·daughter 모델을 가정하지 않는다. 모든 미구현 핵반응과 기존 T1–T8, 전체 EoR/배경 feedback/연속 수렴 의무는 그대로 남는다. 이번 작업에서 full BBN 적분은 실행하지 않았다.
