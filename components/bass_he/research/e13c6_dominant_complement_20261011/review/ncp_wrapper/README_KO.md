# NCP wrapper의 과학 계산 없는 검증 기록

`NO_SCIENCE_VALIDATION.json`은 wrapper 구문, 실제 저장된 기준 numerical/analysis
object의 identity, 경로 이탈·바이트 변조·중복 JSON key·외부 lock SHA 변조·기존
출력 충돌·실패 ZIP의 manifest를 확인한 기록이다. 14개 확인이 모두 통과했고,
새 과학 work unit·coefficient evaluation·exact analysis 재실행은 전부 0이다.

`GUARD_CONTROLS/`의 실패 영수증과 ZIP은 의도적으로 잘못된 작은 fixture를 넣은
사전 실행 guard 대조군이다. 실제 과학 실패나 NCP 실행 결과로 세지 않는다.
이 fixture에서는 scientific source inventory를 통과하지 못하도록 만들었으며,
새 N512와 analysis를 한 번도 시작하지 않았다. 기존 출력 충돌은 최초 영수증의
SHA를 유지한 채 중단되는지도 확인했다.

`validate_wrapper_no_science.py`는 작성 시점의 검증 스크립트 원본이다. 원래
작업 폴더 배치를 전제로 작성되었다. 이 전달본의 NCP 실행 entrypoint는
`code/ncp_execute_once.py` 하나이며, 이 검증 스크립트나 대조군을 NCP에서
재실행하지 않는다. 실제 NCP reproduction은 인도 시점에 NOT_RUN이다.
