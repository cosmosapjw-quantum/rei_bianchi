# HE-E11 scoped research + NCP heavy handoff

이 패키지는 원 NCP E10(3×384 accepted steps)와 E7(컷오프를 인지하는 endpoint observer)의 저장된 같은 가스 경로를 대조한 **새 read-only exact f64 분석**, 그리고 NCP에서 컴파일해야 할 추가 native 내부장부 telemetry Rust example을 포함한다. 새로운 물리 source / heat / recoil을 구현한 것이 아니다.

- `bash run_checks.sh /absolute/NEW_DIR`는 **Python 분석만** 새 디렉터리에서 재현한다. 원 native 3×384, E7 5,199 observer campaign, E8 source campaign을 실행하지 않는다.
- `canonical/analysis/RESULTS.json`은 1,155 mode-epoch 및 770 paired photoelectron 분석, 25 N24 anchors exact reader equality, sign flip24→25, source/cancellation 증거다.
- `canonical/budget/BUDGET_RESULT.json`은 E10 원 scalar photon-energy column으로 E7 BH+BY+BZ 합만 측정 반올림 수준에 근접하는 것을 보여준다. 종별 B 또는 nonphoto micro terms를 infer할 수 없다.
- `doc/e11_native_telemetry.rs`는 **CHATTIME_NOT_COMPILED**. E10의 원 source를 수정하지 않는 독립 native example을 제안한다. NCP가 pinned Rust1.94.1로 컴파일 및 first2 native 시험을 새로 해야 한다. Python `e11.verify_telemetry`의 성공은 synthetic consumer tests에만 해당한다.
- `NCP_LOCAL_CODEX_HANDOFF_KO.md`는 cloud-first 원본 회수, exact source/pins, affected compilation, first2 witness, 조건부 full telemetry, owner-review/claim limits, create-only backup 및 return 형식을 담는다.

원 실행 source는 E10 sealed runtime cloud ZIP, 본 패키지에는 필요한 read-only 데이터와 candidate example만 있다. 원 PDFs·compiler binaries 없음. 모든 역사적 FAIL/source identification이 별개이며, baseline RCT OFF, atomic photon/heat/recoil NULL, physical HOLD, HE-F2/F09 global OPEN.
