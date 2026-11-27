# HE-E10: 원 owner KF/GM 선택형 native shadow 후보

이번 새 연구는 NCP E9의 실제 blocker인 `KF/GM native owner path absence`를 겨냥한다. E9 OFF prefix의 이미 완료된 두 step을 science 재실행 의무로 다시 만들지 않는다.

**판정:** `PINNED_OWNER_NATIVE_KF_GM_FIRST2_BIT_PARITY_PASS__FULL384_AND_REMOTE_OWNER_OPEN`.

- 수정된 세 owner 파일은 지난 RCT03D에서 source-bound로 검증한 **동일 Git blob**이며 새로운 원자식이 아니다. 초기 original remote SHA는 `39c39eab1cc2f1a215723680accc123e67ef13b6`.
- 다른 dependency는 E9 안의 E6 `rei_microphysics` 42 source/Cargo files와 42/42 byte 동일하다. 원격 owner 자체에 원 vendor 디렉터리가 있다고 가정하지 않는다.
- 고정 E9 N384 lattice와 E7 three-mode fixture에서 OFF/KF/GM 각각 첫 2 step의 state5+RCT4 field를 대조: 81 f64 bit checks PASS. E7 10-column sidecar 전체 90 값 string exact. 원 E9 OFF 41-column CSV 3행 byte identical.
- Rust 1.94.1 `cargo test --offline --locked --test e10_native_mode`: 새 5개 테스트 PASS. 원 owner 컴파일 RED의 `E0599 State::with_rct`를 먼저 확인했다. strict `RUSTFLAGS=-D warnings` release example build PASS, 5개 invalid/unapproved/collision 입력 거절 시험 exit2.
- **전체 source, self-contained matching vendor, signed-old owner patch, selected runner, fixtures, RED/GREEN logs and run_checks.sh**는 아래 sealed ZIP 한 개에 있다. Git은 요약·input identity·계약만 담는다. owner/physics 원격 branch를 변경하지 않는다.

## Cloud-first 실행 입력

- **Archive:** `BASS_HE_E10_OWNER_NATIVE_KF_GM_SHADOW_20261009_v1.zip`
- **Bytes:** 193927
- **SHA256:** `f9217156bb5e56c32784bf2d31dc029b66f3455eb8861e1f8e844d11443292c3`
- Drive ID: `1oebECHgdRuJ-_oPv40IlzSyPWr6l8sBn`.
- Dropbox ID: `id:BSpOijBcT10AAAAAAD3iGg`.
- Dropbox path: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E10_OWNER_NATIVE_KF_GM_SHADOW_20261009_sha_f9217156bb5e.zip`.
- Input source root inside ZIP: `HE_E10_OWNER_KF_GM_SHADOW_20261009_v1/research/transport_20261007/short-hhe-midpoint`.
- Restore: new directory unzip and `sha256sum --check SHA256SUMS`; then `bash run_checks.sh /absolute/NEW/smoke` with Rust1.94.1.
- No Rust toolchain/binary or original source PDFs in ZIP.

**Limitations:** Same-conditioned short local 2-step identity is not full-384 science validation, receiver remote adoption, or true continuous error. NCP E9 native gamma vs E7 endpoint gamma remains a distinct readout identity; 0.928386 finite prefix ratio is not a cross-source equality guarantee. Default OFF; physical HOLD; HE-F2/F09 global OPEN; real atomic moments null.
