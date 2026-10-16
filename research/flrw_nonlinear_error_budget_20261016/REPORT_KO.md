# 비선형 residual–adaptive norm 진단

고정된 4변수 chemical-stage residual/Jacobian을 binary64 scaled 선형계로 풀어 Newton 보정, condition estimate, backward error와 EOS 온도 투영을 계산하는 standard-library 모듈과 JSON CLI를 구현했다. 독립 C9 판정은 `PASS_SCOPED`이며 지적이나 추가 repair는 없다. 실제 accepted-stage residual/Jacobian telemetry가 없으므로 실제 source007 원인 분해는 `NOT_RUN_MISSING_RESIDUAL_AND_JACOBIAN_PACKET`이다.

검토된 코드 commit은 `e0d547521cd71047670d5c3967ca4289ea0db8b1`이다. AGENTS의 Astra 계약·수치 판정·독립 검토와 lower-tier 구현·경량 실행 분담을 적용했다. 이는 요청된 routing이며 실제 runtime 모델 식별을 관측했다는 뜻이 아니다.

입력 부호는 `J delta=-R`, 변수 순서는 HII, HeII, HeIII, w[eV/H]다. 현재 adapter는 driver blob `2a16fa8d898588d859eff2c7750a5f8496cadd0c`에 한정된다. 고정 native/adaptive scale을 사용하고 computed zero pivot만 singular로 분류한다. 유한한 큰 condition은 그대로 보고하며, corrected state의 물리 domain이 잘못되면 선형 진단은 남기고 exact EOS map은 null로 반환한다. 이는 nonlinear root error나 실제 trajectory 온도 오차의 인증서가 아니다.

C6의 6개 입력·metadata·원자적 저장·CLI 검사가 한 번에 통과했다. C7은 독립 작성 harness로 이미 완료된 exact oracle 결과를 읽어 7개 matrix case와 5개 adapter EOS case를 비교했다. 최대 절대 metric 차이 `1.4551915228366852e-11`은 condition=100000에서 약 `1.46e-16` 상대 차이이며, 고정된 fixture 비교 기준을 만족한다. Fraction solver와 scalar BE oracle은 재실행하지 않았다. BE cancellation 사례는 기존 R7 결과를 재사용한다.

C8의 작은 고정 검사에서는 condition `4398046511108`인 유한 near-singular 계와 power-of-two rescaling이 통과했다. oldw=10, currentw=0.001에서 thermal SR/Sy=10000, native residual norm=1e-13, scaled correction norm=1e-9를 확인하여 두 energy scale을 같다고 가정하지 않았다. 큰 benchmark는 수행하지 않았다.

실측 outer wall은 C6 `0.171708496 s`, C7 `0.054295429 s`, C8 `0.080472524 s`다. C7 child CPU는 `0.053937 s`, C8 child CPU는 `0.079877 s`다. 새 경량 검사 시간은 기존 NCP/PL 예산과 별도 기록이다. 기존 누적 `156.5376037069618/300 s`, 잔여 상한 `143.4623962930382 s`, 원래 deadline `1792122617.77407`은 바꾸지 않았다. 이번 단위의 NCP·native solver·production build·physical-history·PL replay는 모두 0이다.

공개 ZIP은 이 단위의 코드·계약·synthetic 증거·검토·인계 묶음이다. 전체 production 저장소나 private raw 이력을 대체하지 않는다. 실행 파일은 `nonlinear_budget.py` 하나이며 외부 Python 의존성이 없다. `ACTUAL_STAGE_PACKET_TEMPLATE.json`의 null telemetry는 의도적으로 typed HOLD를 낸다. 결과와 receipt는 fresh output에 atomic replacement, file fsync와 지원되는 directory fsync로 저장된다.

다음 구현은 `NEXT_NATIVE_OBSERVER_PLAN.json`에 따라 최신 canonical 상태와 SOURCE009의 현 소유자/완료 결과를 먼저 확인한다. 기존 승인은 유지된다. 적절한 새 source에 default-off accepted-stage R/J observer를 추가하고, 바뀐 producer blob과 unchanged-equation seam을 명시적으로 비교하여 다음 단위에서 adapter binding을 이전한다. 옛 blob으로 새 producer를 표시하지 않는다. 추가 RHS의 실패·fallback까지 세고 원래 cap/deadline을 유지한다. 계획의 6 packet/48 추가 평가 상한은 실제 실행된 case나 새 NCP 배정이 아니다. 실제 입력·owner 예산은 아직 계획상 null이며 최신 owner 기록으로 채운다.

미래의 실제 R/J packet은 owner 로컬 또는 허용된 private backup에 보존한다. 공개 선택이 이미 선언된 경우를 제외하면 raw telemetry를 공개 Git/ZIP에 넣지 않는다. 새 observer의 R1–R10/C1–C10에서는 유지된 이론·oracle·기존 SOURCE009 결과를 재사용하고 변경된 seam만 검증한다. 전체 수렴·Bianchi·D/isotope 판정은 기존 canonical DAG에 남는다.

C10 publisher는 root가 승인한 좁은 metadata append를 최신 canonical JSON 세 파일에 반영한다. 이 인계 연결은 production Rust 변경과 구별된다. 기존 실행 routing과 SOURCE009 소유권 필드는 보존하며, production Rust 변경은 0이다. 실제 publication과 backup 확인은 DELIVERY_LOG.json의 응답으로 별도 기록한다.
