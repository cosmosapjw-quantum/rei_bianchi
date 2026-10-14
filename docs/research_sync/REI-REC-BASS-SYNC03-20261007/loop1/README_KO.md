# SYNC03 Loop 1 — 실제 F08 가시도 소비

실제 F08의 T0/T1/T2 × FLRW/BI 여섯 이력, 합계 **112,000 셀**을 exact BASS native 모듈로 소비했다. Decimal 70자리 독립 산술 **784,054 checks가 PASS**했다. 원본 REI 화학이나 BASS 생산 코드를 수정하지 않았다.

| 이력 | 셀 | 유한구간 τ(시작) |
|---|---:|---:|
| T0_FLRW | 8,000 | 1.85559546292785141e-05 |
| T0_BI | 8,000 | 1.85559580733599362e-05 |
| T1_FLRW | 16,000 | 1.85560583473609765e-05 |
| T1_BI | 16,000 | 1.85560617902065166e-05 |
| T2_FLRW | 32,000 | 1.85561102041427135e-05 |
| T2_BI | 32,000 | 1.85561136463692215e-05 |

최대 baseline τ 오차는 `1.148e-19`(상대 `8.702e-15`), 전자밀도→q 상대오차는 `2.050e-16`, cell probability 절대오차는 `1.090e-24`다. 공통 observer tail 0.1 진단도 통과했고 finite-interval probability 합 잔차는 `8.634e-16` 이하다.

이는 endpoint 선형보간 함수의 셀 적분과 cold-Thomson 모델에 대한 scoped 수신 검증이다. 원본 endpoint enclosure를 연속체 화학 이력의 bound로 바꾸지 않으며, finite-temperature tail·실제 우주 observer tail·fixed-redshift 방향별 관측량·full BASS build를 검증했다고 주장하지 않는다.

처음 두 실행은 손상된 기존 Rust runtime(LLVM truncation, std/core metadata 부재) 때문에 컴파일 전에/컴파일 진입 시 실패했다. 실패 로그를 보존하고 공식 보존 archive에서 복구된 동일 Rust 1.94.1 도구체인으로 새 executable을 빌드했다. 물리식·소스 모듈·수치 허용치는 바꾸지 않았다.

재현은 `SYNC03_RUSTC=<rustc> SYNC03_RUST_SYSROOT=<sysroot> python run_receiver.py`, 이어서 `python check_decimal.py`이다. exact 입력 hash는 intake manifest와 실행 시 대조하며 source modules는 Gitblob와 같은 bytes다.
