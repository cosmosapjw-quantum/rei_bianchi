# RCT-STEP01 owner implementation

README_KO.md와 OWNER_PATCH_PLAN.json을 먼저 읽고 상세유도/결과는 DELIVERY_RECEIPT의 전체 ZIP에서 읽는다. current source/blob를 비교하되 동일 소스의 전체 과학검증은 반복하지 않는다. F08 owner와 파일 예약 전 실제 FT03/coupled source를 수정하지 않는다.

첫 구현은 기존 Picard 블록의 두 유효율 추가다. thermal/escape와 endpoint residual은 actual combined_ft03_rhs를 사용하고 final J=dt*R 하나로 species/energy/escaped count를 기록한다. 중간 iteration의 양쪽 cross-frozen counts는 accepted events가 아니다. baseline RR/CI/DR와 원래 수치 gates/floors를 유지한다.

OFF baseline delegation, half1+half2 events, full candidate 폐기, 실패시 state/escape/count의 transactional 보존을 검증한다. isolated exact/BE oracle은 기존 HE-F2C 전달물을 재사용한다. optional low-rank Newton은 denominator와 실제 linear residual을 검사하며 첫 patch의 필수조건이 아니다.

재현: python -B -W error verify_design.py (SymPy1.14.0). 이 명령은 새 설계의 수학만 검사하며 native consumer를 실행하지 않는다. 새 구현의 native 오차허용치는 별도 owner 계약을 따르고 기호검산 숫자를 물리오차 또는 interval 인증으로 쓰지 않는다.

mixed finite gate의 peer 반환은 수신 종료했다. root ACK_PENDING 표시만으로 또 같은2/274를 실행하지 않는다. 새로운 RCT stepper 반환만 HE-F2의 다음 연결을 판단한다. HE-F3 실제 F09, physical HOLD, RCT OFF, source moments null, Eq55 NOT_RUN, legacy PARKED_OPEN을 유지한다.
