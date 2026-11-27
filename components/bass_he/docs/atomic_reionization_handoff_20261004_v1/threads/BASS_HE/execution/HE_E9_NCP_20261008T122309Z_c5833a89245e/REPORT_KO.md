# BASS_HE E9 NCP 실행 보고서 (2026-10-08 KST)

판정: 부분 완료. E6/E7/E8 cloud bytes 검증·복원, 원 owner 라이브러리 빌드, OFF N384 첫 두 accepted step의 3행/15필드 bit identity는 확인했다. 원 owner에는 KF/GM 선택 경로가 없어 3×384 전체 실행은 차단했다. 원 CLI 실행 또는 remote owner 채택을 주장하지 않는다.

## H0–H6

H0 완료: 최신 BASS_HE `5caf06ccb395f959b1d9e359ccd062b6927ad6f5` fetch, dirty 원 checkout 보존, 별도 worktree. 통합 ZIP 18,863,548 bytes, SHA256 `c5833a89245e74e4831e7a9ef4e653ce08f3fe1918c40ce281b53ff1ed2b5c31`. Dropbox actual download에서 SHA/CRC/전체 nested manifest를 검증하고 서로 다른 E6/E7/E8 namespace로 복원했다. Drive는 metadata만 확인했다. 복원 입력의 두 provider byte 검증을 모두 수행했다고 주장하지 않는다.

H1 완료: 발견된 Rust 1.94.1 compiler/std component와 공식 HTTPS checksum을 대조했고, Cargo 1.94.1도 official component SHA로 검증했다. PGP signer/key revocation 검증은 NOT_VERIFIED. `cargo build --offline --locked --release --lib` 원 owner build exit0. 별도 실행기 build exit0. 새 시계/관측 무변경 시험 3개 GREEN, 선행 clock-support RED exit101을 보존했다. 과거 E6/E7/E8 전수 과학 시험은 재실행하지 않았다.

H2 부분 완료: 원 receiver `39c39eab1cc2f1a215723680accc123e67ef13b6`의 라이브 linked library src 7파일 blob이 복원본과 같다. main.rs 차이는 config 상대경로뿐이며 원 main CLI를 실행하지 않았다. 별도 OFF-only 실행기는 E2의 사전 정의 N384 lattice `start + max_dln_a*(k/16)/24`와 원 `State::new`, `advance`, `output::row`를 호출한다. 512 panels/order4, active2440 nodes. 시작+두 step의 s/x/y/z/w 15개 f64 bits는 E7와 동일. original 41열 output을 그대로 쓰고 상태 sidecar를 별도로 작성했다. native 원 positivity/EOS/branch/budget/nonlinear gates 유지. 최대 nonlinear0.3600935098552125, number ratio1.4733107956201776e-5, energy ratio0.4904761552570339. 별도 Gamma 비교에서 positive6 fields는 bit-identical이 아니다. 원 solver density와 fixed-history endpoint 관측기라는 readout source 차이를 보존하며 E6 원 allowance `1e-22+1e-6*max(abs(a),abs(b))`로 첫 두 OFF step 최대 ratio 0.928386269462 (step1 HeI)를 기록했다. 이는 제한된 finite 비교이며 exact source identity/true error 인증은 아니다. 원 E8 full consumer는 3행을 385행으로 인정하지 않아 `OWNER_CLOCK_OR_ROW_COUNT`로 정상 거절. 원 owner KF/GM 경로가 없으므로 staged 모델을 이식하거나 대체 실행하지 않았다. 385×3 admission은 OPEN.

H3 NOT_RUN: optional first-moment 진단은 full source-bound owner admission/준비된 native diagnostic adapter가 없어 유보했다. Gamma나 35eV RCT closure로 heat를 만들지 않았다. 실제 atomic photon/heat/recoil은 null.

H4 부분 완료: 새 adapter 3시험과 output collision exit2, 원 raw 41열 CSV/상태 prefix 검사. 측정용 독립 OFF prefix 두 개도 같은 CSV SHA/bytes다. unique science2 steps + benchmark4 steps를 구분한다. 첫 단일 측정 wall10.36s/CPU0.28s/peakRSS2560KiB, 병렬 개별 raw time 약0.31s/peakRSS2560KiB. fsync latency와 shared PROCESS.json.tmp 기록기 race가 있어 speedup은 주장하지 않는다. 두 번째 supervisor wait exit UNKNOWN; `/usr/bin/time` raw exit0와 READY는 별도로 보존. live child 없음 확인 후 재실행하지 않았고 future process metadata를 tag별 namespace로 분리했다. active cap4096 유지; endpoint PathCache를 호출하지 않아 32768 cache-key cap은 이번 native owner density lane에 적용된 실행검사가 아니다. true error는 인증하지 않는다.

H5 읽기 전용 inventory: C2H1은 implementation 완료·molecular pilot 미실행, 별도 review/authorization 필요. HH local ON06G total256/time3.2e11s 및 next source를 읽었다. XTHREAD01 최신 cloud object는 새로 회수하지 않았으므로 해당 freshness는 미확인. CR R12 return과 후속 local R13/R15 evidence가 존재하나 current local branch 이름 remote 조회는404. REI live forward/rust-reion-kernels commit40ea171d6be12275f9ee8b4f50f68b9dad59ed0a는 BRIDGE15 conditional IEEE ledger scope와 BRIDGE16 next를 포함한다. BRIDGE12/13 또는 타 owner science는 dispatch하지 않았다.

H6: 이 보고서/RETURN/source lock/실패/검토 및 원 raw runtime을 immutable private archive로 봉인한 뒤 두 provider create-only ACK·size readback을 기록한다. 공개 Git은 작은 adapter/계약/요약/영수증만 ordinary non-force push. 사후 receipt는 봉인 ZIP 외부에 저장한다. R1 UPLOAD_VERIFIED와 actual remote restore를 구별한다.

## 물리 및 과학 주장 한계

본 실행의 manufactured low-T HHe wiring domain은 관측 EoR 또는 calibrated cosmology가 아니다. OFF를 유지했고 어떤 RHS/opacity/CI/RR/DR/RCT provider, tolerance, source/cutoff, ledger도 바꾸지 않았다. N384 clock 지원은 전달된 exact lattice의 실행 경계 adapter이며 계산 solver 재설계가 아니다. Python sealed source/decomposition PASS는 재사용 evidence이고 새 owner 채택 증거가 아니다. 본 새 결과는 OFF finite prefix/state identity와 native original guard 범위뿐이다. baseline RCT OFF, physical HOLD, HE-F2/F09 OPEN, continuous true-error 미인증, actual atomic first moment null.

## 실패·복구·다음 작업

원 Git fetch의 권한/서버중단, RED, row-count 거절, collision 거절, owner CLI config-path 차이, 병렬 supervisor race를 성공으로 바꾸지 않았다. native debug State 체크포인트는 원 density/장부 상태를 보존하지만 restart codec가 없으므로 NONRESUMABLE이다. 새로운 full history를 허용하려면 연구 thread가 원 owner opt-in KF/GM code+계약과 OFF regression/시계/gates를 source lock으로 전달해야 한다. 임의 owner mutation, staged substitution, 25→385 보간, full F09는 금지. 실행 command/hash는 RETURN_HANDOFF_KO.md와 SOURCE_AND_TOOLCHAIN_LOCK.json 참조.

H6 최종 전달: Git preseal commit `4af25af78369337a328192e9ad4db45f2899fccb`, 두 provider ACK/name/parent/path/38,139,729 bytes readback 일치. Archive SHA256 `1ddd8a347d5640ad15e027005c2d29e5b2ba92bf42be04ca0f95dfdd6da2984a`. Drive object `1TzbtsbD-PrZC7KCoSZr9f3n-6lpw7pw6`, Dropbox `id:BSpOijBcT10AAAAAAD3fpg`. 두 runtime backup은 R1 UPLOAD_VERIFIED이며 재다운로드 RESTORE_VERIFIED는 NOT_RUN. immutable ZIP 안의 H6 상태는 seal 당시 snapshot, 사후 완료와 영수증은 외부 RETURN/DELIVERY_RECEIPT에 있다.
