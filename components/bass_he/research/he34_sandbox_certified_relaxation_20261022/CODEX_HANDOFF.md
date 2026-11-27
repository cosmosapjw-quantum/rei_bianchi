# Codex 실행자 인계 — HE34-SCR

## 먼저 고정할 연구 상태

Repo `cosmosapjw-quantum/BASS_HE`, branch `research/he34-sandbox-certified-relaxation-20261022`, [draft PR88](https://github.com/cosmosapjw-quantum/BASS_HE/pull/88), unit `research/he34_sandbox_certified_relaxation_20261022`. **workflow1.0.0 / approval0.2 유지.** 병렬 Lorentz unit/PR87과 경로를 섞지 않는다.

계산 코드와 실제 결과 S1 pin: `1a07166434a2a9ede1464bcdc465cba3088bb795`. 최종 science payload의 commit/tree, archive SHA256와 provider ID는 `delivery/S2_ACK.json`을 authoritative locator로 사용한다. 이 ACK는 archive 생성 후 Git에 추가되므로 해당 archive 자신의 내부에 들어갈 수 없다. 재개 시 Git의 최신 delivery/DAG 상태와 pin으로 고정한 archive를 함께 읽는다. 최신 metadata commit은 PR88 head다. branch head를 과학 dependency identity와 혼동하지 않는다.

| 재사용 대상 | identity |
|---|---|
| HE32 | `16a424b7290f484c57e97c8ed74f81e6d2043782` |
| HE33 complete source | `bb1259b21c7b83b0376a5f7fcbb0c6321918ec90` |
| 한 saved NPZ | `c97ffa6a793c092b6b559b32581a7996a82b85a8e725b0e5893be9ae1e7bf30a` |
| reduction source | `1b1c717c630aed08afe3a8e39a33395f74cd6684ea355ef126fbdfcb31c90e12` |
| neutral source | `40cf77034e077adb77ae145ec747de168d7674b55307dd7f722dada60e1e61d9` |
| collision subset | `699114aa23d13d38bd1d67fd74358fb52d06c25e8d3c87aa8d282de82dc26542` |
| plot source | `fc67ec6acdc07b86c57c07f1fff5fc79e02aa5ad20cb18ab7d2903af9d39fe0c` |

## 환경과 기본 재개 명령

현재 checkout 위치는 `/tmp/he32_resume_20261022/repos/BASS_HE`다. 이 복원 작업공간의 로컬 Git HEAD는 shell network 제약으로 HE32 pin에 남아 있으며, HE33/HE34 파일은 exact blob 복원 및 GitHub Git-data API로 게시한 snapshot이다. 현재 unit의 동일성은 로컬 HEAD 대신 receipt와 원격 tree로 판단한다. `evidence/LOCAL_WORKSPACE_STATUS.json`에 상태를 기록했다. 다른 환경에서는 현재 checkout의 root로 경로를 치환한다. Python3.12.14, NumPy2.3.5, SciPy1.17.0, Matplotlib3.10.8, Pillow12.3.0으로 실행했다. BLAS/OMP/MKL/NumExpr thread count는1이었다. CPU logical/affinity9, cgroup quota8 CPU, memory cap8 GiB 환경의 측정이며 독점 성능 환경은 아니다.

먼저 `README.md`, `RESULTS_KO.md`, `CONTRACT.json`, `DAG.json`, `RUN_RECORD.json`, `NEXT_DAG.json`, `delivery/S2_ACK.json`을 읽는다. 이후 기본 동작은 과학 재실행 없는 hash/receipt 검사다.

```bash
python research/he34_sandbox_certified_relaxation_20261022/verify_saved.py
```

완료된 현재 dependency에서는 `REUSED_COMPLETE_VERIFIED_PAYLOAD`와 `new_IVPs=0`, `new_renders=0`, `new_benchmarks=0`를 기대한다. 이 검사는 독립 과학 검증의 재실행이 아니며, 현재 code/input/output이 저장 증거와 일치하는지 확인한다.

`run_control.py`도 dependency-matched receipt가 있으면 새 계산 없이 `REUSED_COMPLETE_MECHANICAL_CONTROL`을 반환한다. 그러나 기본 재개에는 위 read-only verifier가 충분하다. `checks/check_transport.py`는 실제 검사·diagnostic·timing을 수행하므로 변경 없는 재개에서 호출하지 않는다. plot cache 재사용은 이미 실제 검증했으므로 다시 렌더할 이유가 없다.

## 새 코드 작업이 필요할 때의 계약

현재 mechanical API는 `src/certified_relaxation.py: solve_reduced(N_knots,S_knots,chi,r0=0,tol_ratio=1e-6,tol_logp=1e-6)`다. N은0부터 엄격히 증가하고 S는 부호 있는 선형 보간으로 정의된다. chi는 양의 상수, Q=j=0이다. `ReducedSolution.certified`는 연속계 상한 수용만 뜻한다. 수치 수용에는 `approximation_valid`, `quadrature_converged`, finite `quadrature_error_estimate+omitted_layer_tail_bound<=1e-9`도 필요하다.

현재 neutral API는 `prepare_neutral_transport(T_K,mass_H_kg,mass_He_kg)`의 `.viscosity(x,y)`와 `.viscosity_vectorized(x,y)`다. T=50–50000 K, 두 비음수 가중치 중 적어도 하나가 양수여야 한다. 실제 diagnostic은 공통 T=20000 K, H1=1*m_u/He4=4*m_u의 명시된 근사다. p/eta를 transient collision eigenvalue나 chemical number rate로 취급하지 않는다.

현재 수용은 prescribed chi=1000,10000 두 경우에 한정된다. chi=10,100은 고정1e-6 목표를 거절했다. source/interpolation/chi/Q/j가 달라지면 기존 증명의 dependency가 바뀐다. 특히 variable chi 또는 Q/J의 도입에는 새 residual 유도 또는 full solver reference가 선행해야 한다. 통과시키기 위해 tol을 사후 완화하지 않는다.

## 변경이 생긴 경우에만 쓰는 실행 명령

기존 결과를 다른 변경 기록 폴더로 먼저 복사하고, code/input identity와 재실행 이유를 남긴다. 다음 명령들은 실제 새 계산을 일으킬 수 있으므로 영향 범위가 생겼을 때만 사용한다.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python research/he34_sandbox_certified_relaxation_20261022/run_control.py --out /tmp/he34_scr_changed_control --rerun-reason 'describe the changed scientific dependency'
```

transport 연결이 바뀌었다면 복원된 NPZ와 HE32 unit을 명시한다.

```bash
python research/he34_sandbox_certified_relaxation_20261022/checks/check_transport.py --background /tmp/he32_resume_20261022/restored/research/he32_sandbox_primordial_20261021/results/cases/s07_m03_r03.npz --he32-unit research/he32_sandbox_primordial_20261021 --repeats 200
```

이 transport 명령은 기존 결과 경로를 사용하므로 반드시 이전 산출물과 receipt를 먼저 보존한다. performance만 확인하려고 반복하지 않는다. 새 model을 더하는 작업은 현재 단원의 파일을 덮어쓰지 말고 별도 unit/DAG로 진행한다.

## 비용, 중단·반환 형식

현재 완료된 mechanical worker는17.445 s/peak64344 KiB, transport worker는2.673 s, render는5.794 s였다. 측정값은 새 캠페인의 시간 보증이 아니다. 큰 sweep나 NCP 제출은 현재 필요 없다. 다음 B1/B2는 우선 small-source/table/adapter 검증으로 한정하고 실행 횟수와 자원 상한을 새 계약에 먼저 적는다.

수치 gate 실패, 입력 fit domain 이탈, cone/energy budget 실패가 나오면 해당 branch를 수용하지 말고 실패 receipt와 부분 산출물을 보존한다. 원인을 분석하고 영향을 받는 부분만 고친다. 완료된 HE32 394 trajectory, 기존 figure6쌍, unchanged prototype/HE33 suite를 반복하지 않는다.

반환에는 command/cwd/environment/source+input hashes, stdout/stderr, exit code, wall/peak memory, 실제 실행 횟수, raw metrics, 고정 수용기준 판정, 실패·수정 이력, output hashes를 포함한다. 각 단계의 진척·백업·게시 pin·다음 DAG를 함께 기록한다. 수학 유도, 수치 대조, 실제 실행, 저장 acknowledgement를 서로 다른 근거로 유지한다.

다음 실작업은 `NEXT_DAG.json`의 B1 transport pair/domain/moment inventory와 B2 SI/normalization/energy-owner adapter 계약을 병렬로 고정하는 것이다. 이 인계는 완료된 현재 계산을 다시 실행해 달라는 요청이 아니다.
