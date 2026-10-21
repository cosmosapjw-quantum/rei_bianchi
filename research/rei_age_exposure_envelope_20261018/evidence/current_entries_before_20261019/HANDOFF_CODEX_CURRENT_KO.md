# Codex/NCP: 검증된 age-exposure 코드 실행

physmath-research-loop를 사용하라. 사용자에게 다운로드·압축해제·SSH·수동 Git 준비를 요구하지 않는다.

Repo: cosmosapjw-quantum/rei_bianchi
Branch: research/rei-age-exposure-envelope-20261018
연구 경로: research/rei_age_exposure_envelope_20261018/
원 physics SHA: 35d9747a0bbedcafdb568467ce7c1e7a25f965b6
재개 당시 remote: 32cfbaad4806394b94edf450a3bf5d1d060330c8
신규 조건부 경계 science commit: a3b8c6100c12da2bbb7bb4b009f9a01057863632
실제 최신 HEAD와 README_CURRENT_KO.md, contracts/NEXT_DAG_CURRENT.json, DELIVERY_RECEIPT_CURRENT.json을 먼저 읽는다.

GitHub에 source/test/driver가 있으므로 이전 sandbox 경로나 standalone bundle에 의존하지 않는다. 기존 checkout과 frozen task identity를 보존하고 dirty/untracked 파일을 덮어쓰지 않는다. 최신 backup에 이미 해당 age64/time/spectral 실행결과가 있으면 먼저 읽고 일치하는 작업을 중복 실행하지 않는다.

1. 연구 경로에서 `bash scripts/verify.sh`. 현재 기대치는 83 tests이다. 스크립트가 frozen donor ZIP을 인증된 rclone으로 직접 취득한다. 그 ZIP SHA는 535a4fce4b52660bc3025fdab8e4159cd9a41173f9c1cf1fa0dc524a099de83a. 별도 사용자 파일 전달이 필요 없다.
2. NCP 연결은 Ubuntu에서 `ssh -i /home/cosmosapjw/.ssh/ncp_key -p 22 root@49.50.142.2`. 키 내용을 출력하지 않는다. CPU/RAM/디스크/Rust 및 활성 PR150/R9/BASS 작업을 조사한다. 기존 작업을 종료하지 않는다.
3. NCP에 연구 source와 원본 donor를 전달하거나 기존 repo/인증에서 직접 취득한다. 충돌 없는 scratch를 지정하고 연구 경로에서 `bash scripts/run_ncp.sh "$REI_REPO" "$NEW_SCRATCH" age64,time8,time16,time32,spectral128`을 실행한다. 컴파일에서 작은 연결 수정이 필요하면 raw failure와 변경을 보존한다. 물리식/허용오차를 바꾸지 않는다.
4. age64는 q=0, age64/angular8/source8/transport16. time8/16/32는 age32 고정, 공통 birth levels [8,16,32,64]의 각 구간 시간 subdivision factor만 변경한다. spectral128은 q=+0.1, age8/angular8/source8 고정. 기존 matched age32와 transport64 reference를 먼저 재사용한다. 이전 [8,16,32] 공통격자와 동일하다고 부르지 않는다.
5. `src/compare_results.py`로 survivor N/U, 세 종별 누적 photo/RR/CI/DR, 순간 Gamma/heat, 온도, age W1와 pre/post 관측을 분리한다. missing species, missing clock side, zero denominator를 성공으로 처리하지 않는다. paired_response_bound에는 두 지지집합 전체의 물리적 response supremum이 필요하며 원 native solver의 certificate가 아니다.
6. 실패 trial과 first negative/subnormal logs, 기존 0.5% HeI 누적 event 목표를 유지한다. 실행 exit0/보존 PASS와 참해 수렴을 구분한다. 실제 age/time/spectral 정확도는 실행 전 모두 HOLD다.
7. 단계마다 code/raw results/DAG를 commit/push하고 Dropbox `dbx:bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/` 및 Drive `gdrv:rei_bianchi_research_backups/`에 백업한다. 각 파일 전체 readback SHA/CRC와 fresh replay를 구분해 기록한다.

최종 보고: HEAD/PR/source SHA, 각 사례 command/exit, state/species residual, reference floor, RHS/wall/RSS, 두 클라우드 readback SHA, 다음 READY. Full production admission은 NOT_ISSUED를 유지한다.
