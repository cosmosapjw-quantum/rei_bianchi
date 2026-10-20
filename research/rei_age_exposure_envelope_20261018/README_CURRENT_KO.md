# REI age-exposure/source-age 현재 상태 | 2026-10-20 정확 산술 최적화

같은 57,344 nodes와 birth clocks 8/16/32/64에서 warm kernel 중앙값을 **47.413 s → 3.532 s(2 task threads, 13.424배)**로 줄였다. 8 task threads에서는 **1.560 s**이며 2-thread baseline 대비 30.383배다. 모든 scientific binary64 값·interval endpoint·prefix 출력은 원 baseline과 동일하다. 새 native history나 age32 사례를 계산한 결과가 아니라 완료된 고정 모형의 산술·캐시·독립 검증 실행을 최적화한 결과다.

| 계산 경로 | Task threads | 3회 중앙값 (s) | Baseline 대비 | 검증 실행 |
|---|---:|---:|---:|---|
| 원 baseline | 2 | 47.413 | 1.000배 | 원 exact oracle 반복 |
| A: integer Taylor | 2 | 10.461 | 4.532배 | 원 exact oracle 반복 |
| B: cache preload | 2 | 6.619 | 7.164배 | 원 exact oracle 반복 |
| C: shared oracle | 2 | 3.532 | 13.424배 | 1회 exact oracle + 모든 prefix bit 비교 |
| C: shared oracle | 8 | 1.560 | 30.383배 | C와 동일, task threads 증가 |

현재 진입은 `RESEARCH_UPDATE_20261020_OPTIMIZATION_KO.md`, `optimization_20261020/README.md`, `optimization_20261020/THEORY_KO.md`, `optimization_20261020/results/BENCHMARK.json`, CURRENT5다. Source baseline HEAD는 `58dc257d1402daa3d0f64786279e13cd72bfb0c7`, task tree는 `1360944eb7e94743c1d5a668e7458f5b4f902d7a`다. 이전 CURRENT5 원문은 `optimization_20261020/baseline_current/`에 보존했다. 게시·백업은 `DELIVERY_RECEIPT_CURRENT.json`의 실제 응답을 따른다. v7 source는 `354823050e6da98e64dde40596be061ce22e71f2`에 게시했고 2,049개 Git blob/mode와 task tree `c583d426082fedc6ff67cce9644388e61573b492`를 확인했다. C8/C10 v7의 Drive/Dropbox 네 upload와 서로 다른 네 전체 readback이 완료되었다. Whole bytes/SHA/CRC/payload/source blob·mode/task tree/native153·B1/vendor 검증은 모두 PASS다. 실제 provider IDs·크기·SHA는 `DELIVERY_RECEIPT_CURRENT.json`과 `evidence/delivery_v7_20261020/`에 있다. 실제 source와 backup은 완료되었다. 이 배송 기록은 자신을 담은 Git commit에 binding하며 exact HEAD는 별도 post-commit v7 confirmation에 기록한다. Confirmation 자체의 upload/readback은 그 뒤의 별도 단계다.

표의 2/8은 global task-pool setting이며 모든 경로의 explicit affine-prefix validation은 별도 pools 1/2/4에서 수행한다.

## 구현·검증과 자원

Exact rational exp의 S18/S19를 같은 integer denominator recurrence로 계산하고 마지막 두 rationals만 normalize한다. Zero/752 guard·halving·directed conversion/squaring은 유지한다. B는 실제 unique miss 53,408개를 immutable rate에서 indexed Rayon map으로 계산하고 serial insert한다. C는 4,448 group exact recurrences/27,552 leaf inequalities를 한 번 확인한 뒤 64,000 all-prefix bit 비교로 thread 2/4 결과에 같은 부등식을 이전한다. 원 B repeated-oracle 경로도 유지한다.

142개 deterministic 일반 rational/경계 fixture, 4개 focused Rust tests, 실제 입력 53,628 exp endpoint parity를 확인했다. C9에서 요청 flag만으로 mode 실행을 인정하던 runner 결함을 실제 출력의 flag/counter로 교정했고 네 regression과 feature-free reference 요청의 예상 `MODE_NOT_ACTIVATED` 실패를 보존했다. 독립 C9는 PASS이며 C9-01 mode-activation finding을 교정·회귀 검증으로 닫았다. 실제 범위와 근거는 `optimization_20261020/reviews/c9/C9_RECEIPT.json`에 있다. 과거 83/85-suite·24-case·native 완료 campaign은 반복하지 않았다.

측정은 순차 실행했고 build는 별도다. 누적 executable wall 253.924 s/600 s, 각 command 240 s 이하다. 공식 Rust/cargo 1.94.1 설치와 offline locked 22 dependencies가 실제 작동한다. 재첨부 installer는 192,287,020 bytes/SHA256 `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`이며 이미 설치한 동일 버전 공식 component runtime을 교체하지 않았다. C2 median CPU 6.581 s, C8 9.132 s로 8 threads는 이 표본에서 CPU를 약 38.8% 더 사용해 latency를 줄인다. 메모리 감소나 cold-build 전체 30배 speedup은 주장하지 않는다.

## 바로 쓰는 최적 경로

`optimization_20261020/run_optimized.py`가 preload/shared-oracle을 명시적으로 켜고 실제 mode activation과 원 numeric 출력을 확인한다. 기본 threads는 min(8, affinity, cgroup quota), `--threads 2`는 이 표본의 CPU economy, `--threads 8`은 낮은 latency 선택이다. 완료된 benchmark를 단순 재개 때문에 반복하지 않는다. 재현이 필요한 경우 README의 fresh scratch/offline build 명령을 사용한다.

## 새 intake와 기존 물리 상태

Parent의 REI BR06·LRS C11·RUN17/RUN18 및 VigilODE PR73/74/75 등의 실제 읽기에서 선택 source/CSV/receipt를 `optimization_20261020/intake/`로 보존했다. 이들과 2026-10-20 02:43:13Z cutoff의 upstream workflow 39360079278 failure에서 새 age32 완료 결과는 확인되지 않았다. Banded/JVP/residual-first 기법은 별도 ODE lane의 근거로 남기며 이 고정 exp model에 새 solver로 대입하지 않았다.

완료된 native age64 block-max는 exit0/19,756 RHS/case782.731 s, photon2.002711130429069e-10·energy1.929660553608937e-13로 원 1e-8 gate를 통과했다. Age64 source jumps는 MISSING_DATA다. Spectral64→128 HeI 누적 photoevent 차이 0.2660778682%는 finite-neighbor 결과다. Native age 수렴·time8/16/32 HOLD는 유지한다. 고정 모형 N64≈1.30931e-7/H와 nonlinear native endpoint≈1.29091e-9/H를 구분하며 nonlinear response bound는 NOT_ESTABLISHED다.

다음 native READY는 **단일 q0 age32 block-max/binary64, source8/n_mu8/transport16/time1, passive diagnostics ON, transport48, case/total cap1800 s**다. 원 B1 binary·computational base·runtime binding과 rtol/atol/RK/source schedule/photon-energy1e-8를 유지한다. 사용자 파일 이동 없이 실행하는 원 프롬프트와 모든 B1 identity는 `HANDOFF_CODEX_CURRENT_KO.md`에 그대로 있다.

## 현재 접근·배송 상태

현재 NCP 도구의 device list는 **DEVICE_LIST_SUCCEEDED**다. 이 턴 SSH 접근·명령은 **NCP_SSH_NOT_PROBED_THIS_TURN**, NCP 과학 실행은 NOT_RUN이다. 이전 월 사용량 중지 응답은 역사 receipt에 보존하며 현재 blocker로 상속하지 않는다.

PR199 draft/no merge/no force-push, owner checkout/PR150/R9/LRS/BASS HHeD와 원 B1 binary 보호를 유지한다. 기존 v6 source/C8/C10 및 네 provider full readback은 완료된 역사다. v7 final receipt/confirmation은 source-bound ZIP 뒤에 생성하며 self-hash loop를 만들지 않는다. **PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED**.

## Source CI 실제 상태

Source commit354823의 [run39366286534](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39366286534)와 [run39366281780](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39366281780)는 untouched top-level native `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check`에서 실패했고 workspace cargo test는 skipped였다. Scoped optimization C9/tests PASS와 구분하며 full-PR CI green을 주장하지 않는다. 실제 job IDs/URLs는 `evidence/delivery_v7_20261020/SOURCE_CI_READBACK.json`에 보존했다.
