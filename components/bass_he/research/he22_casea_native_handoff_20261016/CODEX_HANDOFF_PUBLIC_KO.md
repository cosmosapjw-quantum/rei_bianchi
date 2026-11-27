# BASS_HE HE22: NCP Codex 실행 handoff (공개용, 접속 정보 제외)

이 파일은 [HE21 PR67](https://github.com/cosmosapjw-quantum/BASS_HE/pull/67) HEAD `579ffbce28f988aadb51c377b15f348e4c0359af`의 후속 source-age→original Rust `igm_point_rhs` 구현을 실행하기 위한 공개 계약이다. NCP 서버 주소·키·사용자 로컬 저장 경로는 공개 문서에 넣지 않는다. 개인 접속 지침은 제공된 비공개 전체 archive의 `CODEX_HANDOFF_PROMPT_KO.md`를 따른다.

1. 기존 dirty 저장소와 active production job을 변경하지 말고 격리된 worktree/clone을 사용한다.
2. 원본 cold micro source는 `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`; 비교 참조 `bass_cr@e91ffe368c4e6db64c4b6c5962566302a33402b6`; 새 FLRW production `rei_bianchi@fe789b0b13b1883c5a74cbc907f72f6f963a5d66`는 별도 epoch.
3. `bash -n ncp/NCP_BOOTSTRAP_AND_TEST.sh`와 `sha256sum -c SHA256SUMS.txt`로 입력을 먼저 확인한다. NCP에 Rust 1.99+ 및 격리된 Python numpy/pytest를 준비한다.
4. `bash ncp/NCP_BOOTSTRAP_AND_TEST.sh`로 원본 `rei_microphysics`를 Git SHA에 묶어 빌드하고 실제 native RHS one-case pilot을 수행한다. 성공했을 때만 `HE22_RUN_MATRIX=1 HE22_MATRIX_WORKERS=8 bash ncp/NCP_BOOTSTRAP_AND_TEST.sh`로 12개 범위 제한 케이스를 실행한다.
5. photo-only HE21와 새로운 mock 극한 검증은 **24/24 local Python** 확인되었지만 원본 Rust native 물리 검증은 **NOT_RUN** 상태다. NCP에서 실패하면 FIRST_FAILURE 로그를 남기고 science와 runtime/auth를 구별한다.
6. 강제 merge/force push/관측 CMB 인정은 금지. GitHub에는 별도 draft PR, private 원본 결과는 Google Drive/Dropbox create-only 업로드 후 full remote readback SHA 통과를 명시적으로 기록한다.

필수 physics gates: 원래 MD14 blackbody source cell positive N/U; birth-time/angle 및 Killing energy 보존; photon fit cuts(13.60,24.59,54.42 eV)와 물리 binding(13.598434599702,24.587389011,54.41776 eV) 구별; photoevent converted into original `Gamma_s` and `heat_erg_per_absorber_s`; h=0 native micro과 외부 gas work의 단일 소유; CI/RR/DR, CMB 및 Case-A escaped energy의 수지; source count and gas/thermal positivity; independent timestep/frequency/angular convergence before astrophysical results.
