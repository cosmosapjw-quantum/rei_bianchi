# 다음 실행 경계

BASS_HE root CURRENT_FASTEST_STATE와 actual supplier/consumer HEAD를 먼저 읽는다. 본 HE-F2D는 새 F07 S0 입력에 대한 조건부 직접 사건수 bound이며 새로운 RCT activation/stepper 승인 또는 HE-F3 완료가 아니다.

최신 수신 REI b553698a114fbff05640ab6ecb95d260410de492에서는 F04가 정적 영역에 한정해 완료됐고 다음 Codex task는 F05다. F04 원 certificate는 재감사하지 않는다. 실제 RCT-STEP01과 HE-FLRW02B mixed-native 반환은 별도다. 이 연구 단위를 F05/RCT-OFF baseline의 새 선행조건으로 추가하지 않는다.

새 실행 반환이 없으면 동일 source suite/수락/상한 검산을 반복하지 않는다. RCT-STEP01이 반환되면 source/model/closure/domain과 per-stage R/nH 장부를 대조한다. 정확 exponential density의 right endpoint에는 연속 exposure bound가 적용되지만 일반 구적/근사 density에는 actual quadrature bound 및 그 오차가 별도로 필요하다. 두-half 사건은 각 half의 정규화된 사건수를 합한다.

Ebar는 명시적 caller input이어야 한다. source photon/heat/recoil moments는 null이다. 작은 직접 J를 전체 ON/OFF 또는 anisotropy observable difference로 전용하지 않는다. 그 판단에는 실제 coupled response/error 계약 또는 사전등록된 결과가 필요하다. GM25는 현 S0/FT03 온도창 밖이므로 비교를 위해 guard를 낮추거나 clamp하지 않는다.

독립 reference 재현이 실제 필요한 경우 DELIVERY_RECEIPT가 지정한 전체 ZIP의 root에서 아래 두 명령을 쓴다. 코드환경은 Python3.13.5,mpmath1.3.0,sympy1.14.0이었다. 이 명령은 Rust/source-fit/S0 이력을 실행하지 않는다.

    python -B -W error -m unittest -v
    python -B -W error verify_exposure.py

반환은 repo/commit/tree/path/blob, 실제 command/exit/log, source/Ebar provenance, actual stage geometry/density/time weights, separate RCT/escape count, residual 및 NOT_RUN을 포함한다. source/model 계약이 바뀌지 않으면 legacy 원자 lane은 재개하지 않는다.
