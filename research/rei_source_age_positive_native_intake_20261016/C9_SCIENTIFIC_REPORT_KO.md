# SOURCE_AGE_NATIVE_POSITIVE_REFERENCE_INTAKE: C9 결과

## 범위와 판정

**`PASS_BOUNDED_POSITIVE_NATIVE_REFERENCE_IMPLEMENTATION`**, **`HOLD_SOURCE_AGE_SPECTRAL_AND_NATIVE_TIME_ACCURACY`**. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

이 결과는 원본 native commit `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`의 MD14/BB50k source, Grackle Case-A RHS, `PreparedAbsorption`, signed Bianchi-I geometry를 동일한 짧은 \(\Delta\ln a=0.002\) 구간에서 사용한다. PR #166의 음의 DOP853 내부 stage와 이 연구 첫 subnormal `AXBI_COVARIANT_MOMENT_FIT` 실패는 `evidence/`에 그대로 있다. PR #170의 manufactured Duhamel 결과를 이 source-matched 실행으로 대체하거나 production history로 확대하지 않는다.

## 새 식과 구현

- 광자 출생은 \(j=dN/d\ln a\), \(\dot N=Hj\), \(dt=d\ln a/H\)로 변환한다. 각 cohort는 실제 MD14 출생 시각·출생 방향·에너지 support를 보존한다. 미래 cohort와 물리적으로 비어 있는 lane은 정확한 zero invariant이다.
- occupied finite support \([l,h]\)에서 \(L=U-lN>0\), \(R=hN-U>0\)를 로그 좌표로 적분한다. Native quadrature에는 같은 shape의 \(\hat N=1,\hat U=U/N\)을 주고, log-loss에서 공통 진폭을 소거한다. 실제 photon event·work·ledger는 보존된 log amplitude로 되돌린다. Binary64 linear 출력 범위 아래의 양의 population도 로그 상태에 남는다. Native fit guard, threshold, binding energy, coefficient는 바꾸지 않았다.
- H logit, He softmax, thermal log-energy 좌표를 쓰고 원본 `igm_point_rhs`의 RR/CI/DR/CE/freefree/CMB를 photo input과 한 번만 결합한다. Photon sink는 `PreparedAbsorption`의 한 소유자에서만 나온다. Signed \(s/H\)와 magnitude \(\Sigma=\sqrt3|s|/H\)는 별도 기록하며 directional expansion work를 적분한다. Case-A escape는 bolometric energy ledger이고 미정 frequency/angular spectrum을 생성하지 않는다.
- 각 birth 사이 DOP853 trial은 active state와 14 ledger coordinate의 후보를 생성한다. domain reject는 같은 interval 시작 상태에서 작은 step으로 재시도하고, birth cursor는 성공한 interval 뒤에만 활성화한다. `positive_native.rs`, `positive_accessor.rs`, `matrix_owner.rs`, `positive_solver.py`가 이 source-native reference 및 공통 native 비교를 구현한다. Original production Rust 파일은 수정하지 않았다.

## 최초 실패와 수리

1. 원본 PR #166의 RHS trial #291은 첫 cohort의 occupied 광자 8개를 음수로 만들어 native guard를 실패시켰다. Raw `.npy`, JSON, traceback과 분류를 `evidence/pr166_first_failure/`에 보존했다.
2. 첫 로그-slack q0는 birth 2 부근에서 `AXBI_COVARIANT_MOMENT_FIT`으로 멈췄다. 실패 cell은 strict positive/support였지만 \(N=1.0256007242104761\times10^{-310}/H\)의 subnormal amplitude였다. 단위 진폭의 동일 shape는 native 128-node fit을 통과했다. \(e^{-100},e^{-400}\) 진폭 shift에서 log RHS 최대 상대차 `8.48e-14`, 종별 photo-event 최대 `2.64e-14`였다. Native 원본 guard를 유지하고 reference 쪽 진폭 표현만 정규화했다.
3. 정규화된 첫 q0는 끝점까지 왔지만 photon/energy normalized ledger `1.856e-5/1.520e-8`로 실패했다. 처음 scalar `atol=1e-10`이 작은 count/event ledger에 부적합했다. 독립 instantaneous owner 검산의 세 시점 photon gross residual은 `1.01e-15/1.66e-16/4.39e-16`이었다. Coordinate `atol=1e-11`, count/event `1e-16/H`, energy `1e-14 eV/H`, `rtol=2e-10`으로 **solver 오차 제어를 강화**했다. 고정 acceptance `1e-8` 및 native ledger `1e-10`은 그대로다. Tight 확인은 각각 10배 강하다. 모든 최초 실패 로그는 보존했다.

## 실제 실행과 residual

| 실행 | exit | RHS | wall | peak RSS | photon ledger normalized | energy ledger normalized |
|---|---:|---:|---:|---:|---:|---:|
| Ubuntu q0 | 0 | 2,784 | 24.12 s | 76,068 KiB | `6.59e-10` | `6.20e-13` |
| Ubuntu q0 tight | 0 | 3,384 | 27.74 s | 75,556 KiB | `8.48e-11` | `8.20e-14` |
| Ubuntu q−0.1 | 0 | 2,784 | 23.01 s | 76,356 KiB | `6.59e-10` | `6.17e-13` |
| Ubuntu q+0.1 | 0 | 2,784 | 25.23 s | 75,224 KiB | `6.59e-10` | `6.17e-13` |
| NCP q0 | 0 | 2,784 | 47.22 s | 78,732 KiB | `6.59e-10` | `6.20e-13` |
| NCP q0 tight | 0 | 3,384 | 56.79 s | 78,336 KiB | `8.48e-11` | `8.16e-14` |
| NCP age16 | 0 | 5,629 | 181.54 s | 91,984 KiB | `1.60e-9` | `1.45e-12` |

NCP `s1a0e5abed09`: 64 logical CPU, 125 GiB RAM, Rust/Cargo 1.99.0. 실행 전 R9와 BASS_HE 프로세스가 활동 중이어서 작업 전용 scratch에서 serial로만 실행했다. 병렬 speedup은 **`NOT_MEASURED`**. 원본 PR150/R9 실행·checkpoint는 건드리지 않았다.

Postformat coordinate/scaling/zero/원본 실패 replay와 targeted Rust build는 각각 exit 0이다. Birth moment recovery 최대 `2.78e-15`. q0 일반/tight survivor N/U 상대차는 `9.37e-13/7.61e-13`, gas fraction 절대차 최대 `8.29e-14`, thermal \(w\) 차 `2.20e-13 eV/H`. 가장 촘촘한 새 reference 중 worst photon ledger는 `5.98e-13/H` (`4.10e-9` gross-normalized), energy `9.40e-12 eV/H`. Charge residual은 q0 `9.45e-16/H`, tight `1.50e-16/H`였다.

NCP age16과 Ubuntu age16의 상대 차이 최대: photon N `1.35e-14`, U `1.09e-14`, HI/HeI/HeII Gamma `2.02e-14`, heat `1.82e-14`, photo events `2.01e-14`, RR `1.40e-14`, CI `1.38e-14`; DR은 둘 다 정확히 0. 종별 실제 값은 `evidence/NCP_LOCAL_PARITY.json`과 양쪽 `endpoint.json`에 있다.

## 분리한 refinement 축

`run_refinement_matrix.py`는 q0 age 8/16/32, q+0.1 angular 8/16/32, transport spectral cell 16/32/64, source-energy subdivisions 8/16을 각각 한 축씩 변경했다. 모든 native 비교는 같은 `common_mesh(a0,a1,[8,16,32],time_factor=1)`을 사용하며 mesh SHA-256은 `957a7d68562701534dfca3e224d222aa29400b1a8d95305baaf24d22e0a56bc2`이다. Continuous reference는 해당 실제 birth event에서 재시작하고 공통 관측 시점의 pre/post birth를 구별한다. 새 reference 7건은 모두 exit 0, 합계 31,269 RHS 및 720.58 s, peak RSS 최대 90,228 KiB였다. Matched native 비교 9건도 exit 0이고 공통 관측 18/18을 각각 보존했다. 두 원본 reference baseline은 정확한 완료 입력을 재사용했다.

| 축 | 가장 촘촘한 비교 | 결과 |
|---|---:|---|
| Birth age 16→32 | survivor N `90.13%`, U `88.20%`, Gamma 최대 `94.42%`, age second moment 포함 최대 `2.835386` | `HOLD` |
| Proper time native 1/2/4/8 | level8 survivor N 상대오차 `10.63`, HeII fraction 절대오차 `1.42e-6` | `HOLD`; gas도 안정화되지 않음 |
| Angular 16→32 | 최대 선택 관측량 `6.30e-10` | 독립 reference floor 수준, `REFERENCE_FLOOR_LIMITED` |
| Transport spectral 32→64 | HeI 누적 photo-event `0.749735%` | 목표 `0.5%` 초과, `HOLD` |
| Source quadrature 8→16 | 최대 `1.254e-8` | 두 수준 sensitivity만 측정 |

Source subdivisions는 출생 spectrum 적분 분할이고 transport spectral cell 분할과 다르다. Pressure/quadrupole 차이는 \(\Pi\approx0\)가 아니라 실제 radiation energy로 정규화했다. Birth-age 분할의 작게 보이는 *emitted-stock-normalized* photon 차이로 큰 survivor-relative 차이를 덮지 않았다. Common-mesh native와 matched continuous reference 사이의 Gamma 상대차는 최대 약 `5.09e3`이며, 이 native mesh에서 정확도 PASS를 발행할 수 없다.

## 독립 검토와 남은 경계

독립 C9 검토는 새 material code defect를 찾지 못했고 `PASS_BOUNDED_POSITIVE_NATIVE_REFERENCE_IMPLEMENTATION` 및 `HOLD_SOURCE_AGE_SPECTRAL_AND_NATIVE_TIME_ACCURACY`를 판정했다. 원본 8개 native source body는 task-local accessor suffix 이외 byte-identical임을 확인했다. 별도 production full-history, EoR 관측예측, age continuum, angular convergence order, Case-A escape spectrum은 **검증하지 않았다**. 모든 원시 명령·exit·벽시간·ledger·종별 rate·age histogram은 `evidence/matrix/`와 `evidence/ncp_*`에 있다.

다음 READY는 `SOURCE_AGE_SURVIVOR_AND_NATIVE_TIME_LOCAL_REFINEMENT`: 동일 source·clock을 고정하고 마지막 출생 이후 stiff absorption 경계층에서 age 32→64 및 더 촘촘한 native time mesh를 각각 제한 실행한다. Transport HeI event 32→64 불일치를 별도 축으로 추적한다. Full production admission은 계속 `NOT_ISSUED`이다.
