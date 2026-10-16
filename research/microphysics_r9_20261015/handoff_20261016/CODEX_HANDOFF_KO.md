# Codex handoff — R9 미시물리 NCP 회수와 다음 계산

아래 지시를 사용자의 기존 Ubuntu 작업 환경에서 실행하라. 실제 작업을 수행하고 결과를 반환하라. 계획만 작성하고 멈추지 말라. 이 문서는 2026-10-16 KST의 복구·인계 문서이며, 기존 물리 계산이 모두 완결되었다는 선언이 아니다.

## 작업 위치와 권한

- 기존 로컬 저장소: `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi`.
- 원래 연구 폴더: `research/microphysics_r9_20261015`.
- NCP 연구 루트: `/root/REI_MICROPHYSICS_R9_20261015`.
- 패키지: `REI_R9_NCP_HANDOFF_20261016.tar.gz`. `unit2/`에는 실제 코드·계약·입력·원시 결과·검토 기록·보고서가 포함되어 있다. `handoff/`에는 이번 회수 도구와 검증 기록이 있다.
- SSH는 로컬의 기존 설정을 사용하라. 필요하면 기존 저장소의 `research/axbi_goal_20261014/execution/NCP_ACCESS_RECOVERY_20261014.json`에서 확인된 연결 명령을 읽어 사용하라. 포트나 키 위치를 추측하지 말고, 개인키 내용이나 접근 기록 전체를 출력하거나 백업에 넣지 말라.
- 사용자는 이 연구의 코드 변경·NCP 실행·GitHub 게시·Drive와 Dropbox 이중백업을 승인했다. 통상적인 추가 확인을 반복하지 말라. 기존 작업을 삭제하거나 다른 연구 실행을 중단하는 권한은 이 인계에 포함되지 않는다.

먼저 기존 checkout의 `AGENTS.md`, HEAD, branch, remote, dirty/untracked 상태를 읽어라. 새 clone/worktree를 만들지 말고 관련 없는 파일과 현재 checkout branch를 보존하라. 해당 정책의 Astra 계약/과학 판단 → 낮은 tier 구현 분업을 지원되는 실제 모델과 도구로 적용하되, 실행하지 않은 모델·테스트의 이름이나 PASS를 만들어내지 말라.

## 먼저 읽을 자료와 고정 상태

1. `handoff/C10_HANDOFF_CONTRACT.md`와 `.json`.
2. `handoff/intake/LATEST_R9_INTAKE.md`와 `THREEE_COLLECTION_STATUS.json`.
3. `unit2/CONTRACT_MICROPHYSICS_V6_THREEE.json`, `unit2/code/microphysics_driver_v6.py`.
4. `unit2/review/FINAL_EXTENSION_REVIEW.md`, `unit2/results/CONVERGENCE_STATUS.json`.
5. `handoff/intake/PR150_LATEST_RESUME.json` — 다른 연구의 기존 NCP 자원 점유와 실행을 구분하기 위한 자료다.

현재 확인된 R9 게시 기준은 PR151의 commit `57e6e2d79c1a1ea4786d83b36c871abf581be738`이다. Unit2 archive/PDF/TeX의 Drive·Dropbox 백업은 완료되었다. Unit2 원본 archive의 SHA256은 `725cf8bf53d366b179d41708c4efc9477b29c6c6e0a748ac2d3585dbe33709a1`이며, 이번 대화 환경에서 실제 43,479,461바이트를 다시 내려받아 SHA256 및 Dropbox content hash를 검증했다.

수거기는 2026-10-15 15:24:03 UTC = 2026-10-16 00:24:03 KST에 Unit2 게시 대기 시간 초과로 종료되었다. Unit2 게시 자체는 15:48 UTC = 00:48 KST에 뒤늦게 완료되었다. 이는 수거 절차의 의존성 문제이며 FCI 실패 증거가 아니다. 실패한 수거기를 그대로 다시 실행하지 말라. 이번 `recover_c10.py`는 게시 완료를 기다리지 않고 NCP의 실제 파일과 프로세스를 직접 검사한다.

## 첫 번째 실행: 기존 NCP 결과 회수

대상은 다음 단 하나의 이미 제출된 계산이다.

```text
/root/REI_MICROPHYSICS_R9_20261015/runs/threeelectron_v6/quench_Li_Be_union_aug_TZ_occ_list_v6
```

현재 종료·실패·실행 상태는 **UNKNOWN**이다. 과거 PID나 대화의 “실행 중”을 현재 상태로 사용하지 말라. 이 계산이 이전에 제출되었다는 사실만 확인되어 있으므로, 첫 동작으로 다시 실행하지 말라.

패키지를 NCP의 새 staging 폴더에 옮겨라. 기존 연구 루트 위에 전체 패키지를 덮어쓰지 말라. 예를 들어 패키지를 `/root/REI_R9_NCP_HANDOFF_20261016`에 풀었다면 NCP에서 다음을 실행한다.

```bash
cd /root/REI_R9_NCP_HANDOFF_20261016
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="/root/REI_R9_C10_RECOVERY_${stamp}"
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python \
  handoff/recover_c10.py inspect \
  --root /root/REI_MICROPHYSICS_R9_20261015 --out "$out"
```

`inspect`의 결과와 실제 반환 코드를 읽고 `README_COMMANDS.md`에 따라 `collect`를 실행하라. 도구의 `--help`가 최종 CLI 기준이다. 실제 프로세스·종료 receipt·입력·원시 배열을 확인하여 다음을 구분하라.

- **complete-success:** 동일 입력·소스의 안정된 receipt와 NPZ가 수치 기준을 통과한다. 데이터를 회수하고 독립 검토를 마친 뒤 해당 유한모형 결과로만 채택한다.
- **complete-fail:** 실제 실패 receipt 또는 부적합한 결과가 있다. 원래 실패·출력·로그를 보존하고 원인을 이론/수치/구현/실행환경으로 분류한다.
- **in-progress:** 실제로 일치하는 worker/supervisor가 실행 중이다. 중복 제출하거나 임의 종료하지 않는다. 현재 자원·경과 시간·출력 상태를 기록한다.
- **stale/missing/unknown:** 종료 자료가 없거나 접근이 불완전하다. 이미 수행한 계산의 부재를 곧바로 미실행으로 해석하지 않는다. 프로젝트 내 기존 위치·종료 로그·부분 출력을 한 번 조사하고 관측된 손실 또는 오류에 맞는 다음 조치를 정한다.

회수 도구는 기존 과학 파일을 수정하지 않는다. 완료된 NPZ 검산에는 NumPy가 필요하므로 기존 NCP 가상환경을 우선 사용하라. 환경이 실제로 유실되었다면 `unit2/ncp_results/requirements.lock`으로 새 가상환경을 만들고, 기존 성공 테스트는 소스·환경 관계가 유지되는 범위에서 재사용하라. 전체 계산을 재검증 명목으로 반복하지 말라.

## 수치·물리 채택 범위

이 계산은 점핵·고정핵·비상대론적 Coulomb Hamiltonian의 3전자 Li→Be⁺ sudden projection이다. Li/Be aug-cc-pVTZ AO union과 동일한 직교화 공간을 사용한다. 유한핵질량, recoil, 상대론/QED, 완전한 daughter bound/continuum 분포 및 electron capture는 포함되지 않는다.

- V6 source SHA256: `31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c`.
- 입력 파일 SHA256: `289520d8aed460cdee460f5497762b0c613f003bd6ba43bb505416d945995097`.
- 원래 예산: 12 threads, worker 1개, 24 GiB, 7200초. NCP는 명목 64코어/128GB이며 실제 가용 물리 메모리 관측값은 약 125 GiB였다.
- 부모·딸 각각 원래 Hamiltonian residual ≤ 1e-7 Eh, norm error ≤ 1e-10, orbital metric ≤ 1e-8, RDM trace error ≤ 1e-8, spin error ≤ 1e-6, 실제 수렴과 S²=3/4를 확인한다.
- `P_ground + ||complement||² = 1` 등의 저장 배열 항등식을 독립 검산한다. complement에는 bound excitation도 포함되므로 이를 ionization probability라고 부르지 않는다.
- driver `run` 프로세스의 exit 0만으로 worker 성공을 선언하지 않는다. 최종 receipt와 실제 NPZ가 필요하다.
- V6에는 Davidson iteration 재시작 checkpoint가 없다. 부분 NPZ를 iteration checkpoint라고 주장하지 않는다.

기존 결과 83건 중 77건은 유한모형 수치 기준을 통과했다. 그러나 Li core-valence ionization의 T→Q 차이 3.49970822e-4 Eh와 He/Li 확률 차이 2.72459345e-4는 각각 정한 1e-4 목표를 넘는다. Li projected-response TRK 1.11125914/1.65647443도 완전공간 값 3에 도달하지 않았다. 이를 이미 완료된 물리 정밀도로 승격하지 말라.

## 실패가 확인되면 실제 다음 작업으로 진행

관측된 실패 원인을 한 번 분석하고, 현재 목표에 필요한 최소의 구성적 수정 또는 유실 결과 재구성을 선택하라. 사용자의 이어가기 승인은 이 범위의 실제 작업을 포함한다. 계약이 해결되지 않은 오류를 숨기거나 허용 오차를 완화하는 근거는 아니다.

변경 시 새 source/contract/attempt identity와 새 출력 폴더를 사용하고 원래 실행을 보존하라. 기존 단계의 실패와 같은 소스·입력을 근거 없이 반복 제출하지 말라. 특히 직접 `case` 모드만 실행하면 wall supervisor를 잃으므로, 새 실행이 정당화되면 계약 문서의 `run` supervisor template을 사용하라. 가벼운 진단과 최소 변경 테스트 뒤, 실제 여유 CPU/RAM을 확인하여 한 번의 제한된 NCP 실행으로 넘어가라. 추가 감사가 실행을 무한히 지연하게 만들지 말라.

독립 PR150의 owner 실행은 다른 작업이다. 기준 commit은 `fe789b0b13b1883c5a74cbc907f72f6f963a5d66`, full005의 고정 종료시각은 `2026-10-16T02:50:17.774070Z`이다. 이 인계를 이유로 그 실행·watcher·epoch를 재시작하거나 중단하거나 바꾸지 말라. 다른 연구가 사용하는 자원을 확인하여 중첩 병렬화와 메모리 초과를 피하라.

## 다음 8개 물리 과제의 연결

이번 회수 결과와 `C10_HANDOFF_CONTRACT.md`의 readiness 표를 근거로 다음 계산을 선택하라. 이미 구현된 유한모형·조건부 bridge와 앞으로 구현할 물리 계산을 구분하라.

1. Li bound: core/valence 기저 오차와 필요한 질량·상대론 보정.
2. Li continuum: outgoing Coulomb/exchange channel과 에너지 정규화된 단면적.
3. 저온 분자 반응률: 장거리 potential·channel coupling·핵 운동 및 radiative association.
4. Daughter: 이번 3e 결과 회수 후 excited/continuum 분해. Be7 electron capture는 전자 소멸/contact 연산자로 별도 구현.
5. 핵 정밀도: 실제 likelihood/covariance 및 이론 truncation 불확실성.
6. Charge cascade: 재결합 주입 분포, 2s two-photon, collision/charge-changing channel.
7. BBN→17: Be7 변환·전하 이력·공통 electron/EOS 연결.
8. Transport: 채택된 provider를 owner solver에 결합하고 실제 우주론적 이력을 수렴시킨다.

회수 결과가 없는 상태에서 8개를 모두 완료했다고 표시하지 말라. 회수 후에는 의존성이 충족되는 한 개의 구체적 다음 계산을 정하고 실제 구현·실행 또는 명확한 물리적 미해결 조건을 반환하라.

## 반환·백업·게시

실제 명령, 환경, source/input identity, 프로세스 관측, 종료 코드, receipt/NPZ, 측정된 수치 기준, 자원/시간, 실패 원인과 남은 의존성을 반환하라. 결과의 과학적 채택과 실행 종료와 백업 성공을 각각 보고하라.

새 결과를 immutable Unit3 회수 archive로 만들고 로컬의 기존 rclone `dbx`, `gdrv` 설정을 재사용하여 백업하라. Dropbox 폴더는 `/BASS_DERIVATION_DOSSIERS_20260912/`, Drive 폴더 ID는 `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`이다. 실제 object ID·크기·checksum 확인 뒤 성공을 기록하라. 한쪽이 막혀도 완료된 결과와 다른 쪽 백업을 먼저 보존하고, 원시 결과 회수를 다른 게시 작업의 완료에 다시 종속시키지 말라.

GitHub는 `cosmosapjw-quantum/rei_bianchi` PR151의 현재 head를 다시 읽고 task-owned source·compact receipt·review·delivery만 fast-forward로 추가하라. 현재 branch와 무관한 파일을 stage하거나 force push하지 말라. raw NPZ와 큰 archive는 백업 링크로 연결한다. 자동 merge 또는 production activation은 수행하지 않는다.

최종 답변에는 새로 관측한 NCP 상태, 실제 수행한 계산/검증, 다음 DAG 항목, 백업·게시 링크와 남은 blocker를 간결하게 제시하라.
