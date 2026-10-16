# NCP 직접 재개 안내

이 v2 패키지는 기존 source005 코드·설정과 `d3bbd732be3851fa8eff4f201e49e9e2e130bb6f`까지의 최신 검토 기록을 복구하고, NCP 로컬 파일시스템에서 쓸 운영 도구를 추가한다. 원격 도구의 월 한도 차단을 우회하는 접속 기능은 없다. 사용자가 NCP에 연 터미널 또는 Codex에서 아래 명령을 실행한다.

이 패키징 환경에서는 NCP를 직접 관측하지 않았다. 다른 작업 스레드가 게시한 2026-10-16 03:36:44 KST(10-15 18:36:44 UTC) 관측에서 Q512는 z=12.7627, Q1024는 z=13.0120이고 둘 다 실행 중이었다. 자체 계산의 평균 사용량은 약3.43코어였으며 64코어 활용은 미완료다. watcher는 03:37:02 KST에 대기 중이었다. 이후 상태는 NCP에서 새로 읽는다.

## 실행 위치와 준비

기존 rei_bianchi checkout이 있으면 변경 사항을 보존한 채 게시 커밋을 가져온다. 별도 Git clone/worktree를 만들 필요는 없다. checkout이 없는 NCP에서는 게시된 GitHub ZIP/tar.gz를 새 작업 디렉터리에 풀어도 된다. 이 디렉터리는 현재 계산 중인 `/root/REI_FLRW_COVARIANT_20261015_005`와 분리한다. 이후 명령은 `AGENTS.md`와 `research/`가 있는 패키지 루트에서 실행한다.

`ncp_resume.py`와 `backup_ncp.py`는 Python 표준 라이브러리만 사용한다. 물리 그림을 만드는 기존 renderer에는 NumPy와 Matplotlib이 필요하다. 설치 여부를 먼저 확인하고 누락을 기록한다. 현재 패키지에서는 의존성이나 Rust toolchain을 자동 설치하지 않는다.

```bash
python3 --version
python3 -c 'import numpy, matplotlib; print(numpy.__version__, matplotlib.__version__)'
rustup toolchain list
```

실행 중인 source005는 Rust 1.94.1 빌드다. 기본 Rust 1.99.0 설치 여부와 별개로 그 binary를 덮어쓰지 않는다. 최초 복구본은 source005였지만 현재 패키지 Rust 소스는 게시된 opt-in source006이다. source006 identity는 `abf4ad86…09ba55`, 실행 중 source005 identity는 `1a2268e3…6eaff7`로 다르다. 기존 stage005를 이 패키지로 덮어쓰거나 재빌드하지 않는다. 이번 패키징 환경에는 Rust/cargo가 없어 새 빌드를 수행하지 않았다.

## 1. 실제 상태와 checkpoint 보존

```bash
python3 research/ncp_direct_resume_20261016/ncp_resume.py status \
  --output /root/NCP_RESUME_STATUS_20261016_001.json
python3 research/ncp_direct_resume_20261016/backup_ncp.py compact \
  --code-root "$PWD" \
  --output /root/REI_NCP_COMPACT_20261016_001.tar.gz
```

출력 경로는 새 경로여야 한다. 이미 존재하면 해당 receipt를 먼저 읽고 다음 번호를 사용한다. 상태 도구는 과거 PID 대신 실제 command line을 대조한다. 단일 시점 CPU 누적값/RSS를 기록하며 이를 평균 코어 사용량으로 부르지 않는다. compact 백업은 현재 checkpoint·설정·controller 기록·진단 caller 기록을 보존하며 전체 history 백업으로 표시하지 않는다. 백업 도구의 `missing` 목록과 `code_dependencies`를 확인한다.

원래 science hard stop은 **2026-10-16 11:45:17.774 KST**, campaign 종료는 **11:50:17.774 KST**다. 종료 시각과 누적 counter를 초기화하거나 `full_control.py`를 다시 실행하지 않는다. 상태가 실패/부분/불명확하면 그 상태를 기록한다.

## 2. 완료된 진단 재사용과 다음 병렬화

다른 승인된 작업 스레드가 `c3360857`에서 개행 수정·pinned Rust 1.94.1 빌드·진단을 완료했고 `37ea9e60`에 게시/백업 확인을 남겼다. **남은 build/run allowance는 각각 0이다. `repair-profile`은 재실행을 거부한다.**

`../flrw_covariant_transport_20261015/resume_20261016_001/`의 실제 caller 전후 코드, 측정 JSON, 독립 검토와 백업 영수증을 재사용한다. 진단은 0.439393초/70 RHS였고 prepare 8→16 worker의 측정 비율은 1.458328이다. 단일 terminal fixture이며 전체 이력 속도 향상이나 성분별 production 시간 비율을 뜻하지 않는다. 원 fixture/checkpoint는 NCP 및 해당 private raw backup에 있고 공개 ZIP에는 포함하지 않는다.

`d3bbd732`에서 **별도 source006 opt-in Jacobian 4개 열 병렬화도 완료**됐다. 집중 테스트7개, pinned build, 단일 진단이 통과했고 전체72 stage/504 RHS의 상태·장부·control이 비트 단위로 일치했다. 고정 입력의 화학 단계 wall 비율은1.324002였다. 전체 속도·64코어 활용·전구간 수렴 근거는 아니다. **source006의 남은 test/build/run allowance도 모두0이며 기존 결과를 재사용한다.**

이 ZIP에는 source006 구현·contract·R/C loop 기록·결과·독립 검토가 포함된다. flag 기본값은 false이고 source005에 배포/재시작하지 않았다. 다음 실행은 기존 full005 결과를 검토한 뒤 변경 의존성과 실제 필요한 refinement에 대해 별도 유한 contract를 정하는 단위다. 과거 profile이나 source006 검증을 재실행하지 않는다. 추가 isotope-provider 이론 연구는 기존 실행과 병렬로 진행할 수 있다.

## 3. 실제 전구간 완료 후 그림·보고서

```bash
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py check
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py render \
  --output /root/REI_FLRW_FULL005_DIRECT_POSTPROCESS_20261016_001
```

`check`가 실제 두 case의 완료·고정 binding을 확인한 뒤에만 render가 진행된다. 기존 owner watcher가 이미 결과를 만들었다면 그 결과를 먼저 재사용한다. 이 도구는 별도 watcher나 solver를 시작하지 않는다.

bind와 render는 합계 300초, AS8 GiB로 제한된다. 기존 절대 후처리 마감은 **2026-10-16 12:50:17.774 KST**이며 자동 연장하지 않는다. 마감이 지난 경우 이 wrapper는 명시적 상태를 남긴다. 새로운 후처리 예산은 과거 campaign의 재설정과 구분해 별도 결정해야 한다.

그림은 z=20에서 시작한 경과 proper time와 실제 저장된 Tgas를 사용한다. Tgas 축의 곡선은 시간 순서를 유지한다. H/He만 포함하며 D history를 만들어내지 않는다. pair 비교는 독립 과학 검토 전까지 진단 결과다. 생성 ZIP에는 코드·설정·검토 의존성이 들어가지만 큰 원자료는 외부 경로/해시로 연결되므로 전체 원자료를 포함한 archive라고 부르지 않는다.

## 4. 종료된 원자료 전체 보존

case별 terminal이 기록되고 해당 scientific process가 끝난 뒤 각각 실행한다. 실패 terminal도 실패 상태 그대로 보존할 수 있다.

```bash
python3 research/ncp_direct_resume_20261016/backup_ncp.py full \
  --case FLRW_FULL_Q512_001 --code-root "$PWD" \
  --output /root/REI_FULL_Q512_RAW_20261016_001.tar.gz
python3 research/ncp_direct_resume_20261016/backup_ncp.py full \
  --case FLRW_FULL_Q1024_001 --code-root "$PWD" \
  --output /root/REI_FULL_Q1024_RAW_20261016_001.tar.gz
```

기본 백업 제한은 archive당 1800초·16 GiB, disk free floor 8 GiB다. 제한/중단/파일 변경 오류가 나면 `.partial`과 실패 receipt를 보존한다. `ARCHIVE_CREATED`는 파일 보존 결과이며 과학적 완료 판정이 아니다. 사용 중인 승인된 Dropbox/Drive 또는 별도 저장소로 archive와 receipt를 옮기고 실제 업로드 결과를 기록한다. 새 원자료는 이 대화에서 업로드됐다고 가정하지 않는다.

## 후속 연구

완료된 profile 및 source006 측정과 실제 전구간 검토가 다음 실행 배분의 입력이다. 병렬 pool이나 메모리를 인위적으로 채우지 말고, 측정된 병목에서 유효 계산량/초를 개선한다. q=0 전용 `inactive_hi_split`을 signed Bianchi에 그대로 적용하지 않는다. D/추가 핵종은 실제 donor·photo/recombination·thermal provider와 단일 에너지 소유권을 확보한 뒤 cosmological chemistry에 연결한다.

구현은 gpt-6.1-sol/high, 이론 판단과 독립 과학 검토는 gpt-6-astra/high를 권장한다. 이 단위는 운영 구현·변경 의존성 검증·handoff이며 새로운 물리 이론 루프 완료를 주장하지 않는다.

최초 v1 ZIP은 profile 완료 전 안내를 담은 역사본이다. 실행에는 `REI_NCP_DIRECT_RESUME_20261016_v2.zip`을 사용한다. 공개 ZIP은 source/config/tool 묶음이고 현재 NCP의 전체 raw history 백업이 아니다.
