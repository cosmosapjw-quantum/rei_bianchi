# ACCEL02 중단 복구 독립 검토

현재 Git HEAD `304afc3592ae60242e3bb72efc56d806519b4a60`와 실제 복원 파일을 읽었다. 기존 N1, 128-grid 시간·보존 검증, BASS N4의 범위 한정 판정은 보존한다. 완료 RUN002나 기존 시간검증을 재실행할 이유는 없다.

C06 ZIP SHA `c76771b2ce05ff13d9baea2e812f0635a8ba218dc25be27e55fc16127986f560`과 native 실행파일 SHA `3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac`은 서로 다른 객체의 identity다. 둘을 혼용하지 않는다. 원 EVENT002의 driver/base-driver/RESULT/IDENTITY는 저장된 독립 판정의 hash와 모두 일치한다. 이는 기존 증거 연결의 확인이며 과학 계산의 재검산이 아니다.

게시 전에 소실된 원 EVENT003 원자료, local-only ce40 commit, 최종 spectral 판정은 현재 증거에서 제외한다. 대화 요약의 숫자로 원자료를 대체하지 않는다. 정확히 누락된 256×2, r=0, rtol=1e-11 전체 z15.9→4 계산만 `EVENT_COUPLED003_RECOVERED`라는 새 식별자로 수행하는 것은 복구 범위에 적합하다.

현재 게시된 event driver는 원 EVENT002 대비 accepted gas 및 유한성 검사, endpoint와 common-epoch를 결합한 ledger 판정만 추가했다. 물리 RHS/source/closure를 바꾸지 않았다. 이 변경으로 원 EVENT002의 모든 accepted gas state가 사후 검증되었다고 주장할 수는 없다. 해당 항목은 원래대로 NOT_EXPLICITLY_MEASURED다.

후속 판정은 새 RESULT·IDENTITY·저장 history를 실제 읽고 수행한다. 에너지 initial-scale 1e-9, number/nH 1e-9, time field 2e-6, spectral field 1e-3은 유지한다. 유한 spectral grid의 시간 검증과 continuum 또는 비등방 신호 검증을 구분한다. CR/RCT, secondary cascade, source band 확장, 실제 anisotropic CMB와의 결합은 별도 미완료 범위다.

본 reviewer는 구현·test oracle을 편집하지 않았고 과학 ODE 또는 기존 테스트를 실행하지 않았다.
