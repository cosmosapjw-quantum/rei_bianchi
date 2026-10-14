# PHYS30 별도 경로 재현 준비

상태: **PREPARED / NOT_RUN**. 이 문서는 실행 결과가 아니다. 현재 기여자는 재현 준비를 맡았으며, 후보 생성·과학 검증 설계·최종 승격 판정은 맡지 않는다.

PHYS30의 질문은 같은 중심 허용구간에서 고정 대칭 대역 프로파일의 일차 문턱계수 불변성과 이차 모멘트에 따른 이차계수 이동이다. 실제 `PHYSICS_CONTRACT.json`과 PHYS29의 `PHYS30_NEXT_HANDOFF_KO.md`를 읽고, 새 물리 커널·도함수·근 계산을 모두 0으로 유지하는 계약을 확인했다. replay는 저장된 PHYS29 값만 사용하는 새 프로그램의 단 한 번의 경로 재현이다.

`replay_once.py`는 실행되지 않은 준비 소스다. 먼저 root가 동결된 최초 main을 정확히 한 번 실행하고 실제 raw·실행 영수증을 읽어 성공을 확인해야 한다. 이후 root의 명시적인 GO와 파일 identity를 담은 `REPLAY_ADMISSION.json`을 제공받아야 한다. 이 JSON 자체가 실행 권한을 만들지는 않는다.

동결 manifest의 `files`는 PHYS30 루트 기준 경로·SHA256·bytes·mode를 제공한다. 프로그램이 읽는 manifest는 `contributions/numerics/PREEXECUTION_FROZEN.json`이며, archive와 복원본에서도 이 경로를 그대로 보존한다. 자기 자신을 제외한 정확한 runtime payload에 manifest 한 파일을 더하고, 기존에 없던 별도 절대 경로 아래 `runtime` 디렉터리로 복원한다. 결과·stdout·stderr는 형제 `run` 디렉터리에 남긴다. 출력 신규 절대경로 허용은 numerics와 root가 최초 실행 전에 정합화했으며, 이미 존재하는 출력이나 입력의 덮어쓰기는 허용하지 않는다.

실행 전에는 원본과 복원본의 안전한 exact member set, 일반 파일 유형, SHA256, bytes, mode 및 실제 bytes 동일성을 확인한다. 새 Python entrypoint만 `-B`와 30초 timeout으로 한 번 호출하고, actual command·UTC 시작/종료·wall time·exit·timeout·launch error·raw stdout/stderr·결과 identity를 기록한다. 최초 결과와 재현 결과의 raw bytes와 parsed JSON, 저장된 summary 및 counters를 비교한다. 이후 동결된 입력·코드·manifest의 identity와 복원 member set이 보존됐는지 확인한다. 이 과정은 추가 과학 검산을 설계하거나 물리 함수를 호출하지 않는다.

실패하면 처음 남은 결과·stdout·stderr·영수증을 유지한다. controller는 exclusive attempt lock을 쓰고 자동 재시도하지 않는다. 실행 후 실제 evidence는 `portability/raw`에도 byte identity가 같은 복사본으로 남겨 전체 전달 묶음에 포함할 수 있게 한다. 실행 성공 여부는 준비 문서가 아닌 실제 `REPLAY_RECEIPT.json`을 읽어 판단해야 한다.

재현의 범위는 같은 호스트·Python에서 분리된 경로로 입력을 복원한 구현 재현성이다. 독립적인 물리 자료나 새 물리 계산에 대한 검증 지분은 **0**이다. 과학적 승격 여부는 별도의 실제 NONBLIND 최종 판정자에게 남겨 두며, Physical HOLD 및 모든 보호 상태를 유지한다.

준비 소스는 정적 AST 확인만 허용된다. 이 준비 단계에서 candidate import/main, old program import/main, toy algebra, derivative, kernel, root, replay는 모두 **0**이다. 정확한 열람 경로와 정적 점검 identity는 `PREPARATION_READ_MANIFEST.json`과 `PREPARATION_STATIC_CHECK.json`에 기록한다.
