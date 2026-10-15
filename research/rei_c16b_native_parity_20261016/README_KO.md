# C16B 원본 native 점 비교

PR155 `f8f26710e3961609acf4d7e7930bc7b2a95bd39c` 연구 checkout과 PR150 `0e25846433170d0f420c4cda44a0bedbf02cd177` 원본 Rust를 비교한다. 기존 science source와 Cargo 의존성은 변경하지 않는다. 원본 `CovariantTransport::new/empty_state/add_delta/prepare`, `PreparedAbsorption::evaluate`, `AtomicProvider::reference`, `IgmGasState::from_temperature`, `igm_rates`, `igm_point_rhs`를 호출한다. `HHeModel::controlled_fixture`에서는 상수/EOS만 읽고 합성 반응 계수는 호출하지 않는다.

실행 시 필요한 형제 디렉터리는 `TASK/repo`, `TASK/native/rust/rei_microphysics`, `TASK/venv`이다. `TASK/repo`는 위 PR155와 PR150 object를 모두 가진 Git checkout이어야 한다. 배포 ZIP의 `evidence/benchmark/input/native_PR150_0e258464_build_inputs.tar.gz`를 `TASK/native` 아래에 풀면 `rust/`, `research/`, `docs/`가 생긴다. crate 밖의 9개 `include_str!` 입력도 이 archive에 들어 있다. 연구 폴더의 `c16b_native_parity.rs`를 `TASK/native/rust/rei_microphysics/examples/c16b_native_parity.rs`에 복사한다. Python 가상환경은 `python3 -m venv TASK/venv`로 만들 수 있으며 이 비교기는 표준 라이브러리만 사용한다. 기존 C16B `source_aware.py`와 `src/native_photo_contract.py`도 원래 위치에 필요하다.

```bash
bash TASK/repo/research/rei_c16b_native_parity_20261016/run_native.sh
```

스크립트는 모든 tracked native crate 파일을 정확한 PR150 Git blob과 비교하고 Rust example 두 사본의 바이트 동일성을 확인한다. 빌드에는 `CARGO_BUILD_JOBS=2`, 실행에는 `timeout 300s`, 가상 메모리 한도 8 GiB, Python 관련 thread 한도 1을 적용한다. 각 단계의 원문 명령, exit code, `/usr/bin/time -v`, 원본 JSONL, 비교별 결과를 `evidence/native/`에 보존한다. 출력의 `source_identity.json`은 immutable source, `checks.json`은 수치 판정이다.

48개 고정 사례는 fit threshold 3종의 바로 아래/동일/바로 위 binary64 값 × dt 0/1e9 s (18), 20/40/80 eV 비등량 스펙트럼 × b 0/+0.1/-0.1 × T 100/1e4/1e5 K × dt 0/1e9/1e16 s (27), He 없는 사례 dt 0/1e9 s (2), 빈 광자 제어 (1)이다. nH=0.01 cm^-3, Y=0.083 또는 0, native fractions=[0.31,0.23,0.17], N=[0.013,0.007,0.003] per H, reference mu=[0,0.37,-0.81], a=1, h=0이다. 100 K에서는 Tcmb=300 K, 나머지는 30 K이다. 서로 다른 delta는 서로 다른 ray에 배치한다. 원본 source 생성자의 스펙트럼 적분 격자는 입력 delta closure와 별도이며 광자를 주입하지 않는다.

Python은 기존 source-locked `source_aware.py`를 명시적으로 import하고 그 Verner opacity로 survivor N/(1+dt*c*kappa)를 독립 계산한다. Rust 출력 survivor를 Python 입력으로 사용하지 않는다. Python survivor를 기존 `native_photo_contract.photo_point`에 넣어 Gamma/Heat를 계산한다. 양의 survivor/사건/에너지와 Gamma/Heat는 성분별 상대오차 1e-12, 해석적 영은 exact zero, conservation/ledger/on-minus-off 항등식은 실제 gross operands 기준 128*eps를 적용한다. 모든 native RHS/rates field와 EOS, 실제 광자 에너지, threshold branch, 흡수 ledger를 출력한다.

범위는 고정 opacity의 유한 dt 흡수 및 native 점 photo/EOS/energy owner 대응이다. 큰 dt의 명시적 gas 갱신은 수행하지 않는다. 우주론적 history, 결합 적분기 수렴성, continuum 정확도, 물리 fit 정확도, 기존 합성 thermal bridge의 production 유효성은 이 실험에서 판정하지 않는다.

실측 기계 검증: 48 사례, 4,905 checks 모두 PASS, exact-zero 비교 417개. 모든 양수 비교의 최대 상대오차는 9.00603935062818e-16, cancellation의 최대 `abs(residual)/(128*eps*gross)`는 0.008526034075271402였다. 종별 Gamma 상대오차 최대(HI/HeI/HeII)는 1.67268e-16 / 7.73764e-16 / 1.67274e-16, Heat는 4.93856e-16 / 6.15019e-16 / 2.36455e-16이다. 상세 절대오차, 단위, raw residual, gross scale, 정규화 잔차는 `evidence/native/summary.json`과 `checks.json`에 있다. 대표 nonstiff 최대 노출은 0.45738167894861353이며 stiff는 4.573816789486135e6 이상이다.

원본 focused tests 37개도 PASS: `axbi_covariant_transport` 7, `axbi_transport_parallel` 6, `igm_foundation` 9, `igm_rates` 4, `igm_thermal` 11. 실행 command는 `focused_tests.time` 첫 줄과 `focused_tests.log`에 보존되어 있다. 마지막 example build/native/comparator/focused-test의 wall time은 각각 0.46/0.01/0.17/3.85초, 최대 RSS는 145920/2560/26624/171876 KiB, exit는 모두 0이다. 초기 library compile의 관측치는 9.97초, 329060 KiB였다. 이 결과의 과학적 admission은 부모의 독립 검토에 맡긴다.

첫 실패도 별도 보존했다. 최초 build exit101은 export의 crate 밖 원본 `include_str!` 9개 입력 누락으로, 동일 PR150 blob을 복구했다. 첫 native exit101은 harness source constructor의 n_mu=4가 원본 API가 허용하는 8/16/32에 속하지 않아 발생했다. 원본 테스트의 16 cells/segment, 8 mu 생성자로 수정한 후 실제 입력 ray 3개를 동일하게 명시했다. 첫 comparator HOLD는 `dt1000000000` 문자열이 dt=1e16 사례 ID에도 포함되는 coverage selector 문제였다. exact numeric dt_s==1e9로 고치고 보존 raw JSONL만 다시 비교했다. physics, frozen 사례, 허용오차, 원본 native source는 변경하지 않았다. 원문은 `build.first_failure.log`, `native.first_failure.stderr`, `first_failures.json`, `first_scientific_pass_summary.json`이다. 재비교 전후 raw JSONL SHA-256 동일성은 `raw_preservation.json`에서 확인했다.
