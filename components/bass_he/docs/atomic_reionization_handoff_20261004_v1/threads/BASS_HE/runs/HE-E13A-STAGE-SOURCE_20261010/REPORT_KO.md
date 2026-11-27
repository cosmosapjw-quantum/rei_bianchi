# E13A: 저장된 E12 accepted-step 원소 수지와 native stage-input 인계

**판정**: `ACCEPTED_STEP_SOURCE_LEDGER_FINITE_PASS__NATIVE_FIRST2_STAGE_INPUT_CAPTURE_PASS__INDEPENDENT_STAGE_RHS_OPEN`.

## 1. 원 입력과 실제 source

입력은 봉인된 `BASS_HE_E12_NCP_RUNTIME_20261008T165053Z_4179815c983d.zip`, 6,298,776 bytes, SHA-256 `a7ee2893289119e10741afb9e4e80e701dbcd2c95e987cb41a11218eefe320e7`이다. 원 archive 652개 payload 해시와 전체 CRC를 검사했다. `shadow/research/transport_20261007/short-hhe-midpoint`의 `coupled.rs`, `material.rs`, `radiation.rs`, `diagnostics.rs`, 원 vendor `rei_microphysics`, `e11_native_telemetry.rs`를 변경하지 않았다. ChatGPT 분석 샌드박스에서 새로운 독립 Rust1.94.1 설치를 실제로 수행했으며 원 compiler archive hash를 확인하되 PGP signer 검증은 하지 않았다. 원본 실험의 source는 E10 shadow로 정본 owner 원격 채택이 아니다.

구성은 원과 동일한 저온 제조 FLRW, z12, T0=2000 K, 13.7..100 eV source, 초기 photon0, RCT OFF/KF96/GM25, ON의 연구용 mean35eV closure다. 현 문제와 무관한 핵천체·재이온화 물리변경이나 전체 3×384 새로운 계산을 하지 않았다.

## 2. 독립 산술조합: accepted-step balance

원 유한 CSV에 저장된 누적 계정의 binary64 값을 Python `Fraction.from_float(float(decimal_text))`로 정확히 승격하고 원 Rust의 `coupled::assemble_residual`이나 RHS 함수를 호출하지 않고 H/He의 종별 화학량론으로 네 accepted-step 수지를 재구성했다.

`Δ`는 *연속된 저장 누적값*의 차이, `A_i`는 photon absorption 사건수/H, `B_i`는 photon absorption erg/H, `C_i`는 CI events/H, `R_i`는 RR events/H, `D`는 HeII DR events/H, `J`는 H/He charge transfer(RCT) events/H, `f=nHe/nH`다.

- HII: `Δx − ΔA_H − (ΔC_H − ΔR_H + ΔJ)`.
- HeII: `Δy − [ΔA_HeI − ΔA_HeII + ΔC_HeI − ΔR_HeII − ΔD − ΔC_HeII + ΔR_HeIII + ΔJ] / f`.
- HeIII: `Δz − [ΔA_HeII + ΔC_HeII − ΔR_HeIII − ΔJ] / f`.
- Thermal: `Δw − [Σ_i(ΔB_i − χ_i ev_erg ΔA_i)] − Δ(nonphoto_thermal)`.

정본 source threshold는 `[13.598434599702,24.587389011,54.41776]` eV, `ev_erg=1.602176634e-12`, `Y_He=.24`, `f=Y/[4(1-Y)]`이다. 원 `TOL=[1e-14,1e-14,1e-14,1e-26]`의 새 허용치 변경이 없다. 열식의 `nonphoto_thermal`은 RCT 직접 열·기존 expansion work 등이 포함된 원 material owner의 proper-time 적분이지 임의의 새 cooling model이 아니다.

3 모드 ×384 step ×4성분 **4608개 잔차가 이 원 absolute TOL 안에 있다**. 최대 normalized component는 OFF `0.9417005422016922`, KF `0.7585216029399661`, GM `0.9947604228962691`로 GM의 step7 thermal이다. 이는 native norm의 최대 `0.9416965426`, `0.7585217312`, `0.9947619985`와 가깝지만 매 step 동일한 binary64 연산을 거치지 않으므로 완전 동일한 숫자는 아니다. 정본과의 최대 stepwise scalar norm 차이는 약 0.00159다. 누적계정의 두 큰 수를 빼는 반올림과 계산 순서 차이가 포함되므로 그 차이를 새로운 물리적 방법 오차로 해석하지 않는다.

별도 Decimal110 산술로 각 모드 step1/7/16/59/384의 60개 성분을 재평가했다. 같은 binary64 입력의 대조에서 최대 normalized 차이 `1.6838e-99` 이하이며 이것은 **물리적으로 100자리 정확도**를 뜻하지 않는다. 부호·두 번 RCT 추가·χ 오류·thermal 누락·잘못된 He 질량비·clock·필드 누락에 대한 음성 제어가 작동한다.

## 3. 실제 Rust native E13A 2-step pilot

E12 원 `e11_native_telemetry.rs`와 격리된 새 `e13_stage_inputs.rs`를 만들었다. 새 runner는 읽기 전용으로 원 `coupled::evaluate`와 midpoint `material::rhs_selected`를 accepted state에서 재평가한다. **이 함수들은 정본 소스이고 서로 알고리즘적으로 독립적이지 않다.** 그에 비해 이전/다음/중점 상태, 실제 midpoint FLRW 배경·proper-time step, A/B photon owner, species/w RHS, residual, owner RCT direct moment를 49열 sidecar로 실제 출력한다.

로컬 Rust1.94.1에서 `RUSTFLAGS=-D warnings cargo build --offline --locked --release --example e13_stage_inputs` exit0. 원 E10 영향 5 Rust tests 통과. OFF/KF/GM 각 2step pilot를 Rust 소스 rustfmt 전후 각 1회 실행했고 모두 exit0이었다. 보고용 최종 세 모드에 **고유 6 accepted step과 witness 6행**이 있으며, 처음 형식화 전에도 별도로 6 accepted step이 실행됐다. 서로 같은 계산을 독립 실험으로 세지는 않는다. **원 E12 native41/RCT/STEPS/internal5/stage trace 총15개 파일의 헤더와 시작+2step prefix는 byte-identical**이며 임의 owner physics source 변경은 없다. 정확한 f64 stage 입력을 Python에서 별도 Fraction algebra로 재조합한 최대 normalized 차이는 4.454e-7로 선택 source 재평가의 float rounding 범위다.

E12 원 `OWNER_ACCEPTED_STAGES`의 `k=0` sentinel 9행(각 mode×3stage)을 보존하고, k>0의 실제 summary 3456행은 source f64 schema/finite/mask에 맞는다. Stage 2 count는2440또는2444인데, 이는 2440개/2444개의 독립 수치근을 인증했다는 뜻이 아니다.

## 4. 인증하지 않은 것과 후속 E13B

이번 성공은 **원 native 사건수·에너지 장부를 조건부 입력으로 사용한 종·열 균형의 독립 산술감사**이며, Grackle source 함수의 독립 수치 구현, photon characteristic의 별도 연산·구간수렴, full stage residual true-error/관측기 bias, 물리적 atomic fit 정확도를 뜻하지 않는다.

NCP/별도 수치 lane의 다음 노드는 독립적인 저온 Case A `igm_rates`/EOS 및 RCT coefficient evaluator를 실제 midpoint profile에 적용하는 E13B다. native A/B photon transaction을 조건부 입력으로 먼저 사용하고, photon source 자체까지 독립 보증할 때에는 각 grid node/stage spectrum/energy도 별도로 검증해야 한다. 현재 E13A는 독립 stage 인증을 OPEN으로 유지한다. 저장값만으로 `k=0` 생성원과 `k=7` 등의 내부 photon stage를 소급 복구할 수 있다고 추정하지 않는다.

원 NCP E12 1152step, E10 이전 테스트·원자 전수 suite를 이번 채팅에서 재실행하지 않았다. 새 root/서명독립 과학 심사는 없다. 기존 E7 endpoint/live Gamma 차이 최대 allowance ratio 3.543295 FAIL, 기본 RCT OFF, 실제 atomic photon/heat/recoil null, production·physical HOLD, HE-F2/F09 OPEN, full continuity true-error 부재를 보존한다.
