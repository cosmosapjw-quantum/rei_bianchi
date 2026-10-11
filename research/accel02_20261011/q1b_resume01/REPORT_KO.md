# 직접 복구와 다음 실행 연결

사용자의 직접 수정·재개 승인에 따라 이미 Astra가 허용한 serialization
addendum을 실행했다. 원인은 `numpy.bool_`의 JSON 직렬화와, 그 수정 검사를
막던 실행 의미 없는 마지막 LF 차이였다. LF를 다시 편집하지 않고 승인된
정확한 byte 관계로 검사했다. Python/NumPy 참·거짓 네 경우와 native selective
attempt2가 exit0이다. 첫 실패 및 이전 계약·비용은 변경하지 않았다.

실행기 관측은 `PASS_SELECTIVE_RECONSTRUCTION_OPACITY_SCOPED`이며 독립 판정은
별도 후속 기록에 남긴다. HI K0/K1/H 직접 기준 상대 차이는 각각
5.7675563e-5 / 2.6495142e-5 / 4.7594587e-5이다. 9개 지표 중 parent L1
최대는 8.5086800e-5이고 기준은 1e-4 그대로다. 추가 child wall은
4.233267896초, 알려진 추가 CPU는 3.633063초다. 미측정 overhead는 0이 아니다.

신규 agent 생성의 `agent thread limit reached`는 관측됐으나 scheduler 내부
원인은 입증되지 않았다. interrupt를 삭제 또는 slot 회수로 설명하지 않는다.
완료된 독립 Astra reviewer와 planner를 `followup_task`로 재사용했고 planner의
실제 source 복구 메시지를 확인했다. 이 복구 방식을 global/local AGENTS와
사용자가 요청한 memory 보완 note에 기록했다. 기본 Astra 계획/리뷰와 하위
tier 구현 분담은 유지하며, 이번 controller 구현만 명시적 사용자 예외다.

최신 PR110 C09B에서 이미 작성·검증한 `CELL_RHS_V1`을 발견했다. 새 native
adapter 중복 작성은 중단했다. 정확한 commit/tree의 source를 복구했고,
binary는 기존 로컬 Dropbox ZIP에서 해당 파일 하나만 복구해 SHA를 확인했다.
이는 새 build나 production interval이 아니다. C09B의 C1/C2와 이번 선택적
C02/E02는 구분하며, 어떤 결과도 다른 격자의 실패를 덮어쓰지 않는다.

CR PR34의 saved-grid 수리는 component 범위이며 새 pulse 실행 완료가 아니다.
HE/HH/REC 및 BASS의 최신 head도 읽었다. 이 lane의 CR/RCT/HH OFF 또는 기존
conditional IC를 몰래 교체하지 않는다. 다음은 최신 bridge를 재사용하는
caller binding 계약이다. source-entry solver, 실제 checkpoint 연결, 전구간
시간·스펙트럼·ledger 및 Bianchi/BASS admission은 계속 별도 gate다.

## 이어 실행한 current-stage 연결

위 계획 이후 `q1b_selective_native_bind03`을 실제 구현·실행했고 독립 reviewer가
`PASS_SELECTIVE_CURRENT_STAGE_NATIVE_BINDING_AND_INTERIOR_PHOTON_JVP_SCOPED`를
승인했다. C02 176 angle-cell 중 158은 interior, 18은 zero-width empty이다.
118개 검사를 통과했고 5개 셀×2개 방향×3개 epsilon 및 Richardson 비교를
수행했다. JVP 최대 scaled 오차는 2.0577958421e-8로 1e-7 기준 안이다.
같은 closure의 셀별 L1 차이는 4.589974756e-15이다.

새 연결은 실제 `CELL_RHS_V1`을 69회 호출했다. SIGMA는 606 messages와
58176 energies, native process는 2개였다. 추가 wall3.512445672초,
CPU3.324143초이며 build/장기 history/기존 suite 재실행은 0이다.
누적 native5, SIGMA632, energies156624, 계측 wall47.440636295초,
알려진 CPU46.169729초를 보존한다. 미측정 비용을 0으로 두지 않는다.

승인은 fixed-gas·fixed-geometry의 strict-interior 광자 방향에 한정한다.
진단 residual 출력12·13의 미분, gas/geometry/time Jacobian, evolving Bianchi
stage는 검사 대상이 아니다. E02는 schema/identity만 연결했다. 독립 검토자는
native나 테스트를 다시 실행하지 않고 저장된 값·차분과 실제 코드를 검산했다.
다음 전이는 `SOURCE_ENTRY_POSITIVE_STEP_V1`의 별도 최소 실행 계약이다.
