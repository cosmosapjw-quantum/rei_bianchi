# R9 NCP 실행 안내

`REI_R9_NCP_HANDOFF_20261016.tar.gz`는 Unit2의 실제 전체 파일과 새 회수 도구·Codex 지시문을 포함한다. 계산 원본을 복원하기 위해 대화 기록을 다시 조립할 필요는 없다.

1. archive를 내려받아 **새 디렉터리**에 푼다. 이미 존재하는 `/root/REI_MICROPHYSICS_R9_20261015`를 덮어쓰지 않는다.
2. 로컬 Codex에 `CODEX_HANDOFF_KO.md` 전체를 전달하고 실제 실행을 요청한다. 기존 로컬 저장소와 SSH 접속 기록을 사용하도록 이미 지시되어 있다.
3. NCP에 패키지를 옮겼다면 기존 NCP 가상환경 Python으로 `handoff/recover_c10.py inspect`를 먼저 실행한다. 이어서 실제 분류에 맞게 `collect`한다. 구체적인 CLI는 `handoff/README_COMMANDS.md`와 `--help`에 있다.
4. 기존 결과를 회수·분류한 뒤에만 다음 계산 또는 제한된 수정 실행을 결정한다. 이미 제출된 FCI 계산을 첫 동작으로 재실행하지 않는다.

```bash
tar -xzf REI_R9_NCP_HANDOFF_20261016.tar.gz
cd REI_R9_NCP_HANDOFF_20261016
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="/root/REI_R9_C10_RECOVERY_${stamp}"
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python \
  handoff/recover_c10.py inspect \
  --root /root/REI_MICROPHYSICS_R9_20261015 --out "$out"
```

이 명령은 NCP의 현재 상태를 읽고 새 evidence 폴더에 기록한다. 기존 물리 입력·배열·프로세스를 수정하지 않는다. Python 환경이 없으면 lockfile을 이용한 환경 복구가 먼저 필요하다. SSH 포트·키·인증 정보는 패키지에 넣지 않았다.

현재 공개 상태: Unit2 commit `57e6e2d79c1a1ea4786d83b36c871abf581be738` 및 Drive·Dropbox 백업은 확인되었다. 이전 수거기는 게시 대기 제한으로 실패했으며, NCP 계산 자체의 최종 상태는 아직 확인되지 않았다. 이번 패키지의 로컬 fixture 검증은 NCP에서 이 회수 명령을 실행했다는 증거가 아니다.
