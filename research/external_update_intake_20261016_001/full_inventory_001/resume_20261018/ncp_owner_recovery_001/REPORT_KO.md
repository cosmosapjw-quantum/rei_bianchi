# NCP 복구 후 실제 재접속·기존 실행 확인

2026-10-18 KST. 소유자의 “NCP 복구 완료, 재시도” 요청으로 기존 SSH 경로에 접속했다. 접속 exit0,1.4893s. 현재64CPU, 전체메모리약125.78GiB, 가용124.35GiB, 디스크가용18,035,466,240bytes를 확인했다. 조회 당시 uptime150.27s인 새 부팅이며, 현재 전체 process 목록에서 REI solver/watcher/codex process는 관찰되지 않았다. 과거 PID나 RUNNING 파일을 live handle로 사용하지 않는다.

## 회수한 실제 종료 증거

- FLRW source005 Q512/Q1024 두 case는 모두 exit0,zbar4,a=.2까지 완료된 terminal receipt와 checkpoint가 있다. source identity `1a2268e3da98ed47159cb738762a1a3d3d17bdcb6806e611cbd2bc3c0c6eaff7`, binary `4aa337414a275c66068a900b8349a4114ddc1b1eebad1d904b61cbbd3da84fd4`를 보존한다. 완료된 figure/report/검토를 재사용하며 다시 적분하거나 그리지 않았다. 전체 수렴 승인은 기존 HOLD다.
- R9 원 실행은70newH, campaign action interval[156,230] 후 NumPy API 오류로 실패했다. 원 checkpoint128은 현재 파일797,968,906bytes로 남아 있다. 이것을 새로 읽어 계산·복사·hash하지 않았다.
- 별도 `diagnostic_repair001`은 RUNNING이 아니다. 실제552byte receipt는 `status=deferred`, `supervisor_exit_code=-9`, `reason=wall_limit`, wall1647.067036553s다. 종료 시각은 **2026-10-16 13:48:55 KST**, 원 allocation deadline13:48:54.971486KST와 대응한다. residual 결과가 완료됐다고 주장하지 않는다.
- diagnostic receipt의 `checkpoint_exists=false`는 별도 diagnostic output에 관한 필드이며, 부모checkpoint128 파일이 없어졌다는 뜻으로 쓰지 않는다. 원 internal gates PASS와 spectral refinement HOLD를 그대로 유지한다.

## 실제 조치와 다음 상태

서버 접근 blocker는 해소됐다. R9 현재 상태를 UNKNOWN/RUNNING에서 `TERMINAL_DEFERRED_ORIGINAL_WALL_LIMIT`로 갱신했다. 만료된 deadline을 초기화하거나 동일 진단을 다시 실행하지 않았다. 이번 실행의 새 Hamiltonian action/물리 solver/후처리/빌드/test는 모두0이다.

기존 allocation의 재실행을 현재 READY로 간주하지 않는다. R9 residual을 다시 계산하려면 기존 checkpoint·source와 원 비용을 유지한 별도 명시적 예산/반환 계약이 필요하다. RUN10에서 승인된 단일 수정은 이미6testsPASS로 완료됐고, 추가 native 통합의 coding-worker 가용성은 여전히 해소되지 않았다. NCP 복구를 모델 사용량 한도 복구라고 해석하지 않는다.

`python -m json.tool research/external_update_intake_20261016_001/full_inventory_001/resume_20261018/NEXT_READY.json`

현재 checkpoint `PAUSED_RESUMABLE`, `GOAL_DONE=false`. 실제 SSH argv/cwd/exit/wall와 remote resource/process/terminal 원문은 `OBSERVATION.json`이 가리키는 저장소 밖 owner-private 경로에 보존했다. 이번 공개 산출물에는 원 비공개 NPZ/CSV payload나 executable을 넣지 않는다.
