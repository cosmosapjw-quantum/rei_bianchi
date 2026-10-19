# Codex/NCP 인계 | 2026-10-19 block-max 실행 후

## 기준

- Repo `cosmosapjw-quantum/rei_bianchi`, draft PR199, branch `research/rei-age-exposure-envelope-20261018`, 경로 `research/rei_age_exposure_envelope_20261018/`.
- 실제 HEAD는 PR과 `DELIVERY_RECEIPT_CURRENT.json`에서 확인한다. 이번 intake `18aae24…`, 결과 게시 `4b8e41f3c945612f686a34e11044b36925adf970`.
- native physics `35d9747a…`, 과학 코드 `db87456e…`.

## 이번 세션 실제 수행

1. NCP 직접 접속(`root@49.50.142.2`, 키 내용 미출력). 64 core idle, 125 GiB, disk 17 GiB free, rustc/cargo 1.99.0, gcc 13.3.0. system python3에는 NumPy가 없어 기존 venv `/root/REI_AGE_ENVELOPE_20261018T132700Z/venv`(Py3.12.3/NumPy2.3.5/SciPy1.17.0)를 PATH로 읽기 전용 재사용했다.
2. 기존 repo(LRS lane)는 blob:none partial clone이라 `git show`가 그 object store에 lazy fetch를 일으킨다. 그래서 task-owned blobless clone `/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/repo`를 `REI_REPO`로, `…/run`을 `NEW_SCRATCH`로 정했다. source는 `git archive 18aae24`로 export했다.
3. preflight targeted tests 24 PASS / 2 SKIP. `REI_TRANSPORT_THREADS=48`.
4. `bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age64-block-max` → exit0. 이어 `photon_ledger_diagnosis.py` exit0.
5. 결과·진단·독립 검토를 PR199에 fast-forward 게시하고 Drive/Dropbox에 새 이름으로 백업했으며 원격 전체 readback SHA를 확인했다.

## 다음 세션 규칙

- age64 block-max, RMS age64, spectral128, time8 교정은 반복하지 않는다.
- 현재 NCP READY 사례는 없다. `contracts/NEXT_DAG_CURRENT.json`의 후보는 먼저 로컬 구현, targeted test, 독립 검토를 거쳐 단일 명시 사례로만 실행한다.
- rtol/atol, RK 계수, 물리식, source schedule, photon/energy 1e-8 gate, 1800 s cap을 바꾸지 않는다. iso-cost RMS rtol 비교는 rtol 변경이므로 owner 결정이 필요하다.
- 결과 해석에서 block-max gate 통과를 RMS 희석 가설의 확인으로 쓰지 않는다. 18 관측 기록은 9 고유 상태다. source-jump는 MISSING_DATA다.
- NCP 작업은 task-owned 새 경로에서만 한다. owner checkout, LRS repo, PR150/R9, BASS HHeD, 기존 프로세스를 건드리지 않는다.

**PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.
