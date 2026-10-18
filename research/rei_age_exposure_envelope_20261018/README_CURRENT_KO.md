# REI age-exposure resume closeout | 2026-10-18

이 파일이 이번 재개의 진입점이다. 이전 README/RESULT_STATUS/LOCAL_GIT_RECEIPT는 49-test archive 당시의 이력이며 현재 원격 게시 상태를 나타내지 않는다.

## 실제 현재 결과
- 원격 코드는 중단 중에도 `32cfbaad4806394b94edf450a3bf5d1d060330c8`까지 게시돼 있었다. 이를 읽고 바뀐 Python 4개 및 테스트 3개를 원격 Git blob과 일치시켜 복원했다. 기존 archive 49 tests, 복원된 remote 74 tests는 각각 새 실행에서 통과했다.
- 신규 `paired_response_bound.py`는 같은 source-age 분포라도 gas/opacity 반응이 다른 경우 필요한 response mismatch 항을 추가한다. 기존 74 + 신규 경계8 + NCP bootstrap1 = **83/83 PASS**. 24개 prescribed-opacity 비교도 모든 실제 이산 응답 차이가 조건부 경계 안에 있었다.
- `scripts/run_ncp.sh`는 고정 donor archive를 자동 취득한 뒤 `prepare_native.py --archive`로 전달하도록 고쳤다. 초기 shell regression exit28을 보존하고 같은 test의 exit0을 확인했다. 입력153개를 검증해 준비 결과156개를 생성했으며 compiler는 실행하지 않았다.
- 기존 native physics, threshold, source clock, chemistry tolerance, PR150/R9 checkpoint는 수정하지 않았다. 새로운 native/NCP 실행은 NOT_RUN이다.
- 이론 경계는 실제 함수의 sup/Lipschitz/threshold bound가 주어진 경우에만 유효하다. Native nonlinear opacity의 bound를 샘플 몇 개로 보증하지 않는다. binary64 outward interval certificate가 아니다.

## 재현
```bash
bash scripts/verify.sh
PYTHONPATH=src python3 src/run_paired_study.py --out results/PAIRED_RESPONSE_STUDY.json
```
Git에는 실행용 source/test/driver가 포함돼 있다. tests용 frozen original archive는 `scripts/fetch_donor.sh`가 인증된 rclone dbx/gdrv에서 직접 취득하고 SHA를 확인한다. 사용자가 별도로 다운로드할 필요는 없다. rclone 인증이 없으면 Codex가 기존 연결을 사용하거나 정확한 blocker를 기록한다.

NCP의 작업 전용 scratch에서만:
```bash
bash scripts/run_ncp.sh "$REI_REPO" "$NEW_SCRATCH" age64,time8,time16,time32,spectral128
```
이 명령은 원 native donor를 복원하고 컴파일한 다음 제한 실행한다. age64/spectral128 결과가 이미 존재하면 정확한 입력·실행기·출력 identity를 확인한 뒤 재사용한다.

## 입력과 물리 상태
Original native: `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`.
PR171 latest validated source lineage: `69b4e596ef679e17ccac7c1c1384c1c61cdfd47f`.
초기 49-test ZIP SHA256: `efb871b7507f627fb28ea05ce8f838e10e198b6b0fefe9db06d2007bcc480cfc`.
이번에 해당 Drive/Dropbox readback bytes와 모두 다시 일치시켰다.
BASS reactive backups `84805302...`와 `6f1a6151...`의 실제 code/DAG는 별도 one-way HHeD lane이다. 해당 기록을 PR171 age64 또는 HeI128의 새 정확도 PASS로 대체하지 않는다.

DAG: 복원/조건부 경계/경량 코드 검증 완료. Native age/time/HeI spectral 정확도 HOLD. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
Independent native subagent/reviewer: NOT_RUN_UNAVAILABLE. 수치·생성 코드 검증은 현재 샌드박스에서 직접 실행했다.
