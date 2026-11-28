# BASS_HE — E13C3 뒤 다음 연구 루프 인계

## 지금부터 수행할 작업

`physmath-research-loop`를 읽고 현재 host가 명시한 모델에 맞는 하네스를 선택하라. 이번 완료 작업의 모델은 GPT-6 Astra Pro이고 연구/코딩 하네스는 v4.0.0이었다. 이 인계문은 다음 세션의 모델 선택을 강제하지 않는다. **다음 노드 `E13C4_LOCAL_REMAINDER_ENCLOSURE_ON_FIXED_GAS_PATH`를 시행하라.** 계획 제시로 끝내지 말고, 고정된 국소 범위의 실제 유도·구현·검증·독립 심사·보고서·인계·허용된 저장까지 완료하라.

## 현재 권위와 패키지

- Repository: `cosmosapjw-quantum/BASS_HE`.
- Branch: `research/shared-c64-crossrepo-20260928`; existing open draft PR #17.
- E13C3 intake HEAD: `7e82c807c372392b9f48c0ba3d77986e74d71aea`; 이것은 E13C3 게시 이후의 최신 HEAD라는 뜻이 아니다.
- 현재 과학 패키지: `BASS_HE_E13C3_EXPONENTIAL_CORRECTION_20261010_v1`.
- 게시 경로: `docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/runs/HE-E13C3-EXPONENTIAL-CORRECTION_20261010/`.
- 실제 E13C3 core/delivery commit, archive hash/bytes, 저장 object IDs는 이 패키지와 쌍을 이루는 별도 `BASS_HE_E13C3_DELIVERY_RECEIPT.json`에 있다. Receipt를 먼저 읽고 최신 branch HEAD를 한 번 대조하라. 최신 HEAD를 이 문서의 intake HEAD로 되돌리지 말라.
- 완전한 재현에는 full archive가 필요하다. Git projection은 큰 raw inputs와 node arrays를 생략한다. 부분 projection만 보고 입력이 없다고 새 photon/gas history를 만들지 말라.
- 원래 E13C2 archive: 7,275,484 bytes, SHA-256 `b8804561a86d8a171c478dbc0baf6313efb5b0c0e19fea9e1d0a095a9df661b5`.

## 완료한 과학 결과

E13C3는 fixed affine gas path에서 `r=delta_q-delta_Lambda*P_f`를 forcing으로 쓰고 `e1'+L_f*e1=r`를 계산했다. Frozen damping을 exact exponential로 유지하고 endpoint와 count/energy moments를 하나의 GL quadrature로 구했다. 경계에서 incoming defect를 reset하지 않았다. Captured binary64 midpoint 계수와 mathematical midpoint의 작은 차이도 delta coefficients에 포함했다.

동일 여섯 local controls의 독립 70자리 Decimal GL12/20과 주 구현 GL8/12가 일치했다. Local 최대 heat-defect 상대오차는 9.8204725e-9, **first2의 여섯 macro total-heat defect 최대 상대오차**는 1.6479380e-8이다. 사전 기준은 **저장된 signed total-heat defect의 1%**였으며 총 가열량의 1%가 아니다. Macro 종별 count defect 최대 상대오차는 3.3304869e-8이다.

OFF/KF/GM first2 총 14,652 segments; exported node rows는 14,640개다. GL12 coefficient samples는 175,824회이며 저장 E13C2 path RHS/segment 2,711,100회 대비 15.4194 비율이다. 이번 GL12 내부 시간은 1.220697 s. 통제된 wall-time speedup 주장은 없다.

Actual primary kernel checks 64 PASS; 새 exact algebra checks 317 PASS; local gate 104 PASS; final gate 136 PASS. 최종 독립 decision은 `INDEPENDENT_REVIEW.json`을 읽어 확인하라. Contributor 체크 수를 decision review로 대신하지 말라. 코드 as-run hash:

- Primary: `751a3899d2e78261be872c67a7730e3333234d4590c1a7ead1897e0ad51a5e69`.
- New Decimal: `b3d5830363911c892039547623ade74eaad0fc311808cf46eec11b6613650903`.
- New exact checker: `0e4f5e2824440fc0ef4f3b445d4e53edcef02c145105a2ca9d176940c04fa213`.

기존 E13C2 continuous reference는 읽기만 했으며 다시 계산하지 않았다. New native/gas/coupled Newton/old full3×384 run은 모두 0이다.

## 이어받을 식과 아직 열린 문제

`THEORY.md` §§2–6을 먼저 읽어라. `J(rate,width)=-expm1(-rate*width)/rate`, `J(0,width)=width`다. Kernels는 `W=exp(-L_f*(h-v))`, `K0=J(L_f,h-v)`, `KE=E(v)*J(L_f+1,h-v)`이다. Incoming moments `e_a*J(L_f,h)`, `E0*e_a*J(L_f+1,h)`를 빼지 말라.

1차 ledger는 exact arithmetic/common quadrature에서 닫히지만 원래 모델 residual은 `delta_Lambda*e1`이다. Full species moments에는 `delta_lambda_i*e1`가 남는다. `delta_Lambda=0`이라도 종별 항이 0이라고 결론내리지 말라.

True/frozen opacity 비음수 아래에서 `D_L=integral(abs(delta_Lambda))`, `B_r=integral(abs(delta_q)+abs(delta_Lambda)*P_f)`라 두면 incoming uncertainty `eta_a`를 포함해

`sup(abs(e-e1_tilde)) <= eta_a + D_L*(abs(ea_tilde)+B_r)`.

Weighted endpoint/moment bounds에는 `H_h,H_0,H_E`, species bounds에는 `V_i,V_Ei`가 추가로 필요하다. 현재 E13C3 값은 quadrature estimate이고 rigorous enclosure가 아니다. Captured freezing에 대한 derivative bound에는 `h*abs(Lambda(m)-L_f)` 항도 남는다.

## E13C4의 최소 범위와 판정

1. E13C3의 `inputs/INPUT_MANIFEST.json` 34개 identity와 새 code/results를 read-only 기준으로 고정하라. 저장된 E13C2 local oracle과 E13C3 GL12 결과를 재실행 없이 읽어라.
2. 처음에는 같은 여섯 local IDs, captured `f0`, incoming correction 0만 사용하라: OFF/1/0/0; OFF/1/1162/0; OFF/1/1976/0; GM/2/1727/0; GM/2/2333/0; OFF/2/700/1.
3. Outward-rounded coefficient/integral enclosures 또는 residual-based validated bounds를 실제로 구성하라. Exponential, source law, cross-section domain, event branch, target density 및 arithmetic lift의 enclosure 근거를 명시하라. Unsupported 연산이 있으면 해당 지점을 `HOLD`로 분리하고 sampled 값을 상계로 승격하지 말라.
4. Photon, HI/HeI/HeII counts, energy와 heat 각각의 remainder upper bound를 기록하라. 총 opacity cancellation과 종별 residual, near-threshold heat cancellation을 구분하라. Reference 수치 불확실성과 candidate truncation bound를 구별하라.
5. Correctness gate는 interval/domain 포함성, outward rounding의 근거, 실제 양립 가능한 저장된 reference 차이의 포괄 여부다. Reference와 맞는 것만으로 rigorous proof를 대신하지 말라. Bound sharpness는 별도 진단으로 보고하고 결과를 본 뒤 기준을 완화하지 말라.
6. Near-zero number floor 1e-25, energy/heat floor 1e-24 eV를 기존 비교 표기의 기준으로 유지하되 physical tolerance로 쓰지 말라. Floor 아래 상대오차·sharpness 비율은 unresolved로 표시하라.
7. Local enclosure가 통과하고 incoming error 및 anchor terms를 엄밀하게 전파할 수 있을 때만 first2 확장을 고려하라. 반드시 필요하지 않으면 국소 결과로 종료하라. Nonzero outflow, 새 gas advance 또는 새 source는 이 노드의 범위가 아니다.
8. Implementation contributor와 별도 decision reviewer를 분리하라. 첫 실제 실패를 보존하고 수학/수치/구현/runtime/resource 중 원인을 분류한 뒤 최소 수정만 하라. 사용한 코드·입력 hash를 실행 전에 기록하라.

## 보호 상태와 사용자 권한

`baseline_RCT=OFF`; actual atomic photon/heat/recoil `null`; physical/production `HOLD`; HE-F2/F09 `OPEN`; receiver adoption `SEPARATE`; legacy Gamma alias `3.543295 FAIL`을 유지하라. 기존 gas algebraic TOL은 continuum accuracy budget이 아니다. Actual atomic RCT spectrum/moments와 late k7/k59 stock 입력은 별도 열린 노드다.

사용자가 이미 허용한 범위는 같은 BASS_HE 연구 branch의 additive non-force publication과 지정된 Drive/Dropbox create-only backup이다. 반복 승인을 요구하지 말라. Branch 업데이트 직전에 현재 HEAD를 확인하고 expected-SHA를 걸어 갱신하라. Concurrent 변화가 있으면 먼저 읽고 합쳐라. Merge, production defaults, 다른 사람에게 메시지 전송은 이 권한에 포함하지 않는다.

기존 backup 위치는 Drive parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/`다. 새 hash-bearing filename을 사용하며 기존 항목을 덮어쓰지 말라. Archive와 receipt는 분리해 순환 hash를 피하고, provider acknowledgement를 remote restore 검증과 혼동하지 말라.

## 완료 조건

새로 유도·실행한 것, 저장 결과만 검증한 것, 아직 계획인 것을 분리한 보고서; 원자료·producer identity·첫 실패; 별도 독립 decision; 다음 DAG와 인계문; 과학 payload manifest; 실제 허용된 publication과 backup receipt를 남겨라. 충분한 선택적 readback 뒤에는 옛 계산과 검사를 반복하지 말라. 최종 답변은 핵심 과학 결과와 물리적 한계, 다음 병목을 채팅에서도 자립적으로 설명하라.
