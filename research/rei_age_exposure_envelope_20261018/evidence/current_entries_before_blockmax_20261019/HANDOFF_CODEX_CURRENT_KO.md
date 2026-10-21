# Codex/NCP 인계 | 2026-10-19 최종

## 목표와 실제 현재 기준

`physmath-research-loop`를 사용하여 GitHub와 최신 백업부터 실제로 읽는다. 사용자에게 다운로드·압축 해제·SSH·수동 Git 준비를 요구하지 않는다.

- Repo: `cosmosapjw-quantum/rei_bianchi`
- Draft PR: `199`
- Branch: `research/rei-age-exposure-envelope-20261018`
- 연구 경로: `research/rei_age_exposure_envelope_20261018/`
- Original native physics: `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`
- 이 세션 intake HEAD: `0c6b0466b10a47788f6415a8538e9d3e7a268163`
- C8 게시: `e729adaf2a16064e95f6f5efc7e469f708b58559`
- 최종 source/delivery HEAD는 실제 PR와 `DELIVERY_RECEIPT_CURRENT.json`에서 확인한다.

README_CURRENT_KO.md, HANDOFF_CODEX_CURRENT_KO.md, HANDOFF_NEW_CHAT_KO.md, contracts/NEXT_DAG_CURRENT.json, DELIVERY_RECEIPT_CURRENT.json 및 RESEARCH_UPDATE_20261019_KO.md를 먼저 읽는다. 새 결과가 있으면 코드·입력·실행기·출력 identity로 재사용한다.

## 이미 수행된 작업

spectral128은 완료됐고 He I transport64→128 누적 photo 차이는0.2660778682%다. 기존 RMS age64도 endpoint까지 실행한 뒤 photon1.0081783527976493e-8 >1e-8로 실패했다. 같은 RMS나 spectral128 캠페인을 반복하지 않는다.

기존 native time8/16/32는 MOMENT_FIT로 실패했다. 이번 로컬 time8 failure-only 진단으로 subnormal count 저장 오류를 확인했고, opt-in count 교정으로 첫 셀은 통과했으나 뒤의 energy-only 셀2η>η에서 다시 실패했다. **현재 time8-subnormal-count 재실행과 time16/32 확장은 READY가 아니다.** script에 진단 재현용 mode가 존재한다는 이유로 실행하지 않는다. 다음 native 단계에는 먼저 count/energy 동시 저장 표현의 타당성 연구가 필요하다.

새 고유26 targeted tests PASS, 두 task-native 컴파일과 실제 로컬 진단 실행, 독립 검토를 완료했다. 기존85 PASS/1optional skip은 이력이다. 환경 초기화 후 코드와 native153/age64raw70은 exact hash로 복구했으나 D의 두 번째 셀 전체로그는 미복구다. SCRATCH_RESET_RECOVERY_20261019.json에 범위가 있다. 이 기록을 NCP 실행 결과나 원본로그로 바꾸어 쓰지 않는다.

## 유일한 다음 실행 READY: q0 age64 block-max

새 가설은 성분 수가 증가할 때 global RMS에서 ledger 오차가 희석되는 효과다. 동일 stage/scale에서 block-max≥기존 RMS를 유도·검증했다. `rtol/atol`, 물리식, source schedule, RK coefficients, 고정 photon1e-8 gate는 그대로다. 이 변경을 검사하는 **새 단일 사례**만 실행한다.

1. 현재 연결 도구와 실제 NCP 접근을 다시 확인한다. 이전 세션의 blocker를 상속하지 않는다. 기존 Ubuntu SSH 안내는 `ssh -i /home/cosmosapjw/.ssh/ncp_key -p 22 root@49.50.142.2`이며 키 내용을 출력하지 않는다.
2. NCP의 hostname, CPU/RAM/disk, compiler/Python/NumPy/SciPy, 활성 작업과 기존 연구 결과를 읽기 전용 조사한다. owner checkout, dirty/untracked, PR150/R9, 별도 BASS HHeD lane을 수정하거나 종료하지 않는다.
3. 실제 최신 PR source를 task-owned snapshot에 자동 준비한다. 기존 repo의 immutable Git objects를 읽고 별도 새 scratch에 export하는 방식이면 owner checkout을 전환할 필요가 없다. 기존 인증과 GitHub/백업 연결을 사용하며 파일 처리 전부를 Codex가 수행한다.
4. `REI_REPO`는 immutable native Git object를 읽을 수 있는 실제 repo로, `NEW_SCRATCH`는 충돌 없는 새 작업 경로로 Codex가 결정한다. 번들에 frozen `contracts/NATIVE_INPUTS.json`이 들어 있으므로 원래 donor ZIP을 수동 구할 필요가 없다. script는 `prepare_native.py --repo --fetch-missing`으로153개SHA를 검증한다.
5. 기존 작업에 사용할 CPU를 침범하지 않는 범위에서 `REI_TRANSPORT_THREADS`를 명시한다(실행기는1..48로 제한하며 identity에 기록). idle 자원이48개 이상이면 이전 binary64/48 비교와 같은48을 사용할 수 있다. BLAS 관련 thread는 script가1로 고정한다.

연구 source 경로에서 실행할 명령은 다음 하나다. 아래 변수의 값을 사용자에게 묻거나 직접 채우게 하지 말고 Codex가 위 조사에서 정한다.

```bash
bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age64-block-max
```

이 명령은 source preparation, native compile, binary64 RPC, explicit block-max age64 단일 실행, FOLLOWUP_RESULT.json을 생성한다. case/total cap은 기존1800초다. mode는 native moment-rounding none이므로 count 교정과 섞이지 않는다. 컴파일·작은 연결 수정만 필요하면 raw failure와 최소 변경을 보존하고 바로 진행한다. cap이나 수치 tolerance를 자동 완화하지 않는다.

## 실행 후 해야 할 일

- command, source/prepared/binary hash, runtime와 threads, case status/exit, RHS/wall/RSS, 실패 trial, 원래 species/charge/photon/energy gate를 기록한다. endpoint 도달이나 exit0을 참해 정확도 PASS로 표시하지 않는다.
- 다음 명령을 실제 attempt data 경로에 대해 실행한다. 경로는 Codex가 결과 tree에서 선택한다.

```bash
PYTHONPATH=src python3 src/photon_ledger_diagnosis.py --data "$CASE_DATA" --out "$NEW_SCRATCH/PHOTON_LEDGER_DIAGNOSIS.json"
```

- gate가 통과하면 source·clock·owner identity가 맞는 기존 age32 reference와 `src/compare_results.py LEFT RIGHT --out RESULT`로 비교한다. 동일 source가 입증되지 않으면 age 수렴성은 HOLD로 둔다.
- N/U, T, species별 누적 photo/RR/CI, Gamma/heat, source-age W1와 common pre/post 관측을 구분한다. DR은 aggregate scalar로 보고한다. 분모0, species 누락, 실제 birth jump side 누락을 성공으로 처리하지 않는다.
- 새 결과가 gate를 실패하면 그 정확한 결과를 게시하고 추가 동일 실행을 중단한다. NCP에서 본격적인 이론 재설계나 허용치 완화를 시작하지 않는다.
- 의미 있는 결과는 PR199의 실제 parent 위에 fast-forward 게시한다. force push, merge, owner checkout 변경은 하지 않는다.
- Dropbox `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`, Drive `rei_bianchi_research_backups`에 새 파일명으로 백업한다. 로컬 SHA/CRC/payload, provider 완료 응답, 원격 전체 readback을 각자 실제 수행 범위로 기록한다. 가능한 경로가 바뀌었으면 실제로 시험하되 동일 실패 경로를 반복하지 않는다.

최종 보고는 실제 HEAD, 실행 표, 정확도 HOLD/유한차이 판정, 두 백업 결과와 다음 DAG를 제시한다. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**를 유지한다.
