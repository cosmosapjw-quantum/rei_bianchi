# HE-F2C 이후의 다음 작업

최신 root CURRENT_FASTEST_STATE.json을 우선한다. Codex508b6c366515b1d7b168285f20327138036cdefa에서 조건부 local RHS 수락은 완료했지만 HE_F2_global_completed=false다. 본 묶음의 같은 intake는 중복 확인이며 독립적인 완료/검토로 세지 않는다.

Supplier는 HE-F3_WAIT_REI_F09_RESULT를 유지한다. 실제 FT03[30000,110000]K와 GM25[200,10000]K가 겹치지 않아 OFF/KF96 alone은 paired source campaign 완료가 아니다. 같은 감사나 원자 suite를 반복하지 않는다.

Owner의 기존 다음 노드는 RCT-STEP01이다. actual combined_ft03_rhs를 stepper/residual에 연결해야 하며 Ft03Model.gas를 generic HHe wrapper에 넣어 RR/CI/DR를 지우지 않는다. source 선택·Ebar provenance·stage-domain·underflow·rollback 및 별도 RCT/escaped count를 유지한다. 두-half 사건은 각각 합한다.

상세 exact/BE 해와 온도 경계 reference는 DELIVERY_RECEIPT.json이 가리키는 전체 ZIP에 있다. 로컬 reference 명령은 다음 두 개다:

    python -B -W error -m unittest -v
    python -B -W error verify_reference.py

mpmath/sympy 버전은 evidence/DEPENDENCIES.json에 있다. 유한 고정밀 reference 결과를 native tolerance나 실제 source 정확도로 쓰지 않는다. BE 끝점이 온도범위 안이라는 사실만으로 exact path를 인증하지 않는다. cap을 넘으면 반응수를 clamp하지 않고 step 거절 또는 경계 재시작을 하며 사건 장부를 함께 유지한다.

HE-FLRW02B mixed photoionization native pending은 별개다. RCT116시험이나 본9시험으로 닫지 않는다. DEFAULT OFF, source moments null, physical HOLD, Eq55 NOT_RUN, HE-L1/L2/L3 PARKED_OPEN과 F04/과거 FAIL을 보존한다. 이 BASS_HE 스레드에서는 소비기를 수정하거나 native 실행하지 않는다.
