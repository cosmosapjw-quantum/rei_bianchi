# Codex/NCP 인계 | 2026-10-19 진단 checkpoint

`physmath-research-loop`를 적용하고 GitHub와 최신 백업을 먼저 실제로 읽는다. 사용자가 파일 다운로드·압축 해제·SSH 준비를 수동 수행하도록 요구하지 않는다.

Repo `cosmosapjw-quantum/rei_bianchi`, draft PR199, branch `research/rei-age-exposure-envelope-20261018`, 연구 경로 `research/rei_age_exposure_envelope_20261018/`, original native `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`.

1. 실제 PR HEAD 및 다섯 CURRENT 진입 파일을 읽고 receipt 뒤의 새 결과가 있으면 먼저 재사용한다. 이번 intake HEAD는 `0c6b0466b10a47788f6415a8538e9d3e7a268163`이다. 이전 문서의83 tests/NOT_RUN 또는 전체5사례 실행 명령을 현재 상태로 사용하지 않는다.
2. spectral128은 이미 완료됐다. age64 RMS/binary64 replay도 완료된 실패이고 photon ratio `1.0081783527976493e-8 > 1e-8`를 보존한다. native time8/16/32 기존 실패는 MOMENT_FIT이다. 같은 입력·코드 캠페인을 반복하지 않는다.
3. 새 로컬 time8 진단은 153-input manifest 일치, Rust1.94.1 빌드, 6.436 s exit1이다. 정확 셀 원본 재생에서 n≈1.187e-309, count5η>3η, energy89η≤116η를 확인했다. 이 셀의 저장 양자화 교정 연구는 별도 opt-in 경로에서만 검토 중이다. 최신 DAG에 READY가 되기 전 time16/32를 실행하지 않는다.
4. reference 새 `--error-norm block-max`는 같은 RK stage에서 기존 RMS보다 느슨하지 않은 오차검사다. 기본값은 rms다. 새 age64에는 binary64와 명시적 block-max를 사용하고 기존 rtol/atol 및 모든 gate를 유지한다. 이것이 기존 RMS 재실행과 다른 과학적 목적이다.
5. 실제 NCP 연결·CPU/RAM/디스크/Rust와 활성 작업을 먼저 읽기 전용 조사한다. 기존 Ubuntu 연결 안내는 `ssh -i /home/cosmosapjw/.ssh/ncp_key -p 22 root@49.50.142.2`이며 키 내용을 출력하지 않는다. 현재 도구 가능 여부를 다시 확인한다. owner checkout의 dirty/untracked와 PR150/R9 및 BASS HHeD lane을 덮어쓰거나 종료하지 않는다.
6. branch source/test/runner의 실행 준비는 이 연구 경로 안에서 끝낸다. 기존 repo의 immutable native Git object 또는 SHA 검증된 donor archive를 자동 취득한다. 사용자 수동 파일 전달은 필요하지 않다. 컴파일·작은 연결 수정은 raw failure와 변경을 남긴다.
7. 단일 case 실행 후 endpoint, source clock, 각 종의 누적 photo/RR/CI, Gamma/heat, T, source-age W1를 분리하여 비교한다. DR aggregate0은 종별 성공으로 표시하지 않는다. source-birth paired snapshot이 없으면 MISSING을 유지한다. 실행 exit0/보존 PASS와 정확도 수렴을 구별한다.
8. 의미 있는 변경/실행 결과를 PR199의 현재 실제 parent 위에 fast-forward 게시하고, Dropbox `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`와 Drive `rei_bianchi_research_backups`에 새 이름으로 백업한다. provider upload 응답, 로컬 ZIP SHA/CRC, 전체 readback SHA를 서로 구별한다. 새 증거 없이 동일 replay를 반복하지 않는다.

이 checkpoint 이후의 완성된 한 번 실행 명령은 최신 `contracts/NEXT_DAG_CURRENT.json`의 READY 항목에 따른다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`를 유지한다.
