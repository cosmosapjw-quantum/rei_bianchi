# BASS_HE E13C10 — NCP local Codex 내부 인계문

사용자의 지속 지시: 짧은 이론·코딩·control·pilot는 ChatGPT 쪽에서 수행하고, 실제로 길고 무거우며 유용하게 병렬화되는 계산만 NCP64코어/128GB로 전달한다. 이번 E13C10은 해당 국소 작업을 완료했다.

## 현재 상태

- HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01: PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST.
- 5개 captured OFF 경로,12segments,170/170 raw nested 및 nonincrease, P60.
- 선택 가중 구간 폭 감소 P97.7836860203%,H98.0689999175%; full-population 개선율 아님.
- Source lock SHA256: dab62d573a17d5333aa09369c1865b873a2c55d77efc3a88aeef872beeef4bbb.
- 새 NCP work units: 빈 배열. NCP_ACTION=CLOSED_NO_NEW_HEAVY_TASK.
- E13C7 완료 heavy work, E13C8 full-finite, E13C9/E13C10 selected work는 닫힌 작업이다. 재실행하지 않는다.
- E13C10 full-population NOT_RUN; physical/continuum/production/receiver HOLD.

## 인수 절차

1. 외부 최종 handoff의 actual file ID/bytes/SHA로 승인된 backup에서 이 kit와 COMPLETE 또는 모든 조각을 가져온다. 추가 사용자 파일 첨부는 필요 없다. 기대 SHA는 final handoff의 고정값이어야 한다.
2. 동일 content identity로 완료된 복구가 현재 호스트에 있으면 그 receipt와 package state를 확인해 재사용한다. 이미 완료한 복구나 수치 검증을 반복할 필요가 없다.
3. 복구가 없으면 versioned restore_transfer_e13c10.py와 외부 transfer manifest를 사용해 fresh output에서 한 번만 --hydrate 한다. 조각 파일명의 .bin을 예상 이름으로 바꾸거나 이름만으로 연결하지 않는다. helper가 실제 bytes/SHA로 선택한다. 첫 실패를 보존하고 자동 재시도하지 않는다.
4. 새 package는 output/package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1, predecessor는 output/runtime/E13C9다. CURRENT_STATE.json 및 실제 독립 decision의 identity를 확인한다.
5. 현재 heavy queue가 비어 있으므로 MPI/budget/physics/full-first2/N512/native/gas/ODE/full-population 작업을 시작하지 않는다. 후보 코드를 수정하거나 과거 PENDING 상태를 승격하기 위해 원시 결과를 다시 쓰지 않는다.
6. 수신 측 작업을 수행했다면 새 receipt에 실제 호스트·Python·affinity·관측 가능한 quota/memory/provider 정보를 적는다. provider attestation이 없으면 NOT_ASSERTED로 둔다. 다운로드 bytes/SHA, 복구 입력과 output, invocation 수와 오류를 기록한다. 업로드하는 경우 승인된 기존 폴더에 additive로 저장하고 ACK와 이름·크기 readback을 구분해서 남긴다.

## 다음 연구와 새 heavy gate

다음 노드는 HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01, HERE_LOCAL, PROPOSED_NOT_RUN이다. 현재 선택 반폭에서 signed rectangle이 약98.83%를 차지한다. coupled prefix/kernel의 수학적 상계와 독립 짧은 통제부터 ChatGPT 쪽에서 진행한다.

실제로 필요한 full observable와 정확도 목표, 국소 채택 방법, 아직 계산하지 않은 독립 work list, 실제 비용·병렬효용 근거가 생기면 별도 고정 handoff를 만든다. source/input/P60 의미를 유지하고 path 안의 segment는 serial이다. rank×thread, BLAS/OpenMP 중첩 방지, NUMA/affinity/quota와20% RAM 여유는 측정으로 정한다. 현재 문서는 향후 계산 범위를 임의로 확장하라는 지시가 아니다.

완료 상태와 실제 invocation만 반환한다. 수치 계산을 하지 않았다면 physics NOT_RUN, invocation0이라고 명시한다. 복구 PASS를 물리 실행 PASS로 표시하지 않는다.

