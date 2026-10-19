# BASS-REACTIVE-02: 중단 복구와 백업 우선

2026-10-19 KST. 마지막 완료 산출물은 reactive01의 84805302... ZIP이다. 이 파일을 현재 샌드박스에서 재해시하고173payload를 검증한 뒤 Drive/Dropbox에 고유 이름으로 보존했다. Drive raw 재다운로드 해시는 일치했고 Dropbox는 upload completed까지 확인했다. GitHub에는 이 시점의 복원 계약과 보존 기록을 먼저 게시한다. 이 Git commit만으로 parent archive 전체가 보존됐다고 주장하지 않는다.

부모 PR194는 source-only intake를 담고 있으며 reactive01 결과와 구분한다. 예전 BASS-INTAKE-01 미컴파일 checkpoint로 되돌아가지 않는다. 기존179tests/13histories는 이 commit의 새 실행 결과가 아니다.

새 연구의 범위는 기존 one-way BASS/HHeD 연결을 보존한 더 긴 구간의 통제된 계산이다. 초기 조성/광원/원자율은 회귀 설정으로 고정하며 donor/time/inner-CX/spectral/birth-time 설정을 섞지 않는다. 실제 실행 결과가 확보된 뒤 이 directory에 코드·검증 근거를 추가한다. 상호 Einstein feedback, physical EoR IC, tilted/polarized transport 및 full EoR 수렴은 별도다.

복원: 두 cloud 중 하나에서 기록된 ZIP을 내려받고 `python restore_parent.py ARCHIVE.zip NEW_EMPTY_DEST`를 실행한다. 이전 source와 새 결과를 임의 덮어쓰지 않는다. 이번 연구는 샌드박스에서 실행하며 user-local/NCP/Codex를 사용하지 않는다.
