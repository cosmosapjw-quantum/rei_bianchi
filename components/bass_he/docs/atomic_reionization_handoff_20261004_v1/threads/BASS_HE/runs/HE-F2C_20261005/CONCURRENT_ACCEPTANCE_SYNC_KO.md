# 동시 수락과 게시 충돌 조정

이 부록과 기존 root 상태가 초기 완료 표현보다 우선한다. 원 입력faea0580e5751ffaf23012f91649c34e48fbb7cb 뒤에 Codex508b6c366515b1d7b168285f20327138036cdefa가 동일 제한 수락을 먼저 게시했다. canonical root blob은0bf26c443371239ee2099634db23ddfbfb028097, canonical acceptance blob은e4073407d2625fd480fc85eb3c215f9770d93584다.

상태는 LOCAL_RHS_BINDING_ACCEPTED_WAIT_STEPPER_AND_F09, actual_RCT_binding_accepted=true, HE_F2_global_completed=false다. HE-F3 WAIT_REI_F09_RESULT와 mixed HE-FLRW02B SEPARATE_PENDING을 유지한다. 수락 대조는 서로 일치하는 중복 작업이며 독립 과학검증이나 두 번째 milestone으로 세지 않는다.

첫 expected_sha 갱신은 argument binding 실패, 이어 force=false 갱신은422 Not a fast forward로 거절됐다. 두 실패에서 ref는 변경되지 않았다. 생성됐지만 branch에 게시되지 않은 commit1d2738e79d4e295615e106a55fd6bac031859384를 현재 결과로 쓰지 않는다. 최신 parent 위에 additive 자료만 올리고 root/TASKS/CODEX_START/execution을 모두 보존한다.

새 결과는 isolated RCT exact/BE extent, 온도-domain crossing과 endpoint/path 반례다. 새로운 native/physical/stepper 승인이나 다른 스레드의 전체 결과 재검증은 아니다. 미게시 root 제안은 ZIP의 evidence/UNPUBLISHED_PROPOSED_CURRENT_FASTEST_STATE.json에 historical proposal로만 남긴다.
