# BR06 Recovery R1 C9 — bounded review closed

**판정: PASS_WITH_DECLARED_BOUNDED_SCOPE.** 최종 source manifest는 `f70901363e1901e71b6d2933dfa6080c9de9af8daa4e35178be77d1fcfab9402`이다. 삭제된 이전 수치 결과의 PASS를 계승하지 않았다. 검토 대상은 새 R1 wrapper와 byte-exact V2 path core에 대한 새 near-zero probe이다. 기록된 BR05 첫 단계, 동결 comoving 기체, one-way BASS ±shear 참조의 범위로 제한한다.

## 발견과 수정

R1 fixture loader가 384개 개별 유효 source row와 sequential template_id만 검사하면 source label을 중복시키면서 다른 label을 빠뜨릴 수 있었다. source-native 연구 입력의 정확한 원본 hash는 실제 실행을 보호했지만 malformed-source 거부에는 충분하지 않았다. 저자는 `spectral_index=id/8, angular_index=id%8`을 검사하는 작은 guard를 추가했다. 실제 중복 CSV를 사용하는 거부 테스트가 새 실행에서 통과했다. 이 변경은 유효 source의 수치 연산을 바꾸지 않는다. 13개 전후 비교는 measured wall_s를 제외하고 동일하며 source, geometry, birth, scalar moment 결과가 보존된다.

## 새 실행에 연결된 검산

- 새 BR06 테스트 16/16, strict Clippy, scoped rustfmt 로그를 읽었다.
- parent 전체 133개 파일(그중 Rust 117개)을 새로 hash 비교하여 원 archive와 모두 일치함을 확인했다. Root의 새 parent 테스트 233/233 및 strict Clippy receipt도 확인했다.
- 최종 rlib `0ce7e13c339be00db6f98d08c2ffca42beac0c96c3721f5eb72d1469a1f1ce6d`로 독립 C9 실행 파일을 컴파일하고 선언한 22개 thin-hazard 사례를 실제 실행했다.
- 독립 theory agent의 Decimal400 검산은 22/22를 통과했다. 20개 thin-route 사례는 HI absorption이 올바르게 반올림된다. τ=10^−7의 두 normal-route 사례는 최대 2 ULP 차이다.
- 최소 양의 subnormal opacity/event는 slab 1개와 4개 모두 보존된다. 이 격자에서는 기록된 underflow flag가 모두 false다. 이것을 모든 입력에서 underflow가 없다는 주장으로 확대하지 않는다.
- independent geometry work의 최대 상대오차는 3.91658895392577×10^−16, ledger-derived work는 3.12336275980153×10^−15다. 이는 E0=100 eV, 정확한 binary64 h=.05, T=1인 닫힌형 통제 문제의 결과다.

22개 격자는 잃어버린 이전 probe를 byte-identical하게 복원한 것이 아니다. 새로 선언한 11개 hazard와 1/4 slab의 조합으로 원 P1 메커니즘을 확인했다. CSV SHA-256은 `320063f05fc10cae8860f23fac3716862bbae185c64a21d7fbf9f561572fcdb8`이다.

## 물리 및 수치 소유권

새 fixture는 기존 MD14/BB50k source와 H/He/D opacity, 기록된 midpoint 기체 및 실제 donor geometry를 사용한다. 각 birth의 실제 시간·geometry·energy·spectral/angular label을 보존한다. Killing 상수와 마지막 방향, weights는 개별 CSV 행에 남는다. Reflection cache는 현재 diagonal geometry와 에너지에 의존하는 scalar absorption에서만 의미가 있고, 각 방향의 부호는 개별 행에서 복원된다. Scalar interval을 근거로 birth들을 임의의 하나의 age에 합치지 않는다.

Binding-energy owner와 Verner fit edge의 역할이 구분된다. 사건과 heat는 양의 적분 항으로 계산되고 chemical 및 geometry work ledger는 분리된다. W_ind는 생존확률×원 owner dE/dt의 적분이다. Ledger-defined work와 독립 work의 차이를 숨기거나 source energy로만 정규화하여 work 정확도라고 주장해서는 안 된다. 원 CX 및 four-corner source는 변경되지 않았다. 이 reference는 gas를 진화시키지 않으므로 그런 흐름을 실행·수렴시켰다는 의미도 아니다.

새 error wrapper는 CX work limit, reference work limit, representation limit, owner refusal, malformed input, 환경 실패를 구분한다. 미표현 subnormal과 실제 물리 부재를 혼동하지 않는다.

VigilODE adapter는 검토자가 작성했으므로 독립 theory agent가 수학적 identity, chronological source mapping, interval 폭 gate 및 Decimal110 containments를 검토했다. 이 C9 검토자는 그 결과를 읽고 wrapper 경계만 별도로 확인했다. 원 VigilODE 핵심 payload는 수정하지 않았고, gauss-quad 0.3.2 lock 및 원 package checksum이 보존된다.

## 남은 결과의 범위

현재 코드 검토의 blocking finding은 없다. Root/theory의 fresh full-source matrix가 실제 birth/path/spectral 오차와 ±shear 변화를 판정한다. Categorical birth-rule 비교에서 형식적인 수렴차수를 추론하지 않는다. 전체 진화하는 H/He/D 이력, 보편적 2차 정확도, EoR 초기조건, 두 방향 Einstein 피드백은 이 결과로 입증되지 않는다. 코드 C9 episode는 여기서 닫으며, 이후 필요한 작업은 새 그림의 구체적 해석 검토다.

전체 hash, 근거 경로, 소유권별 관찰과 제한은 `C9_RECOVERY_R1_FINAL_REVIEW.json`에 있다. 적용 정책은 physmath-research-loop 1.3.0의 bounded review, typed evidence identity 및 이번 세션의 명시적 연구·복구 권한이다.
