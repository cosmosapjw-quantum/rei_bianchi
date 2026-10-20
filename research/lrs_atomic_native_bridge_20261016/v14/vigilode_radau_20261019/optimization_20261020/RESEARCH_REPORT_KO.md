# 독립 LRS native 최적화 연구 — 2026-10-20

## 결론

현재 3-stage Radau IIA와 native photon–chemistry–thermal 식을 유지하면서, finite-difference Jacobian 안의 광자 cell 준비 결과를 재사용하는 `cell-cache` 경로를 구현했다. 같은 실행파일의 `legacy` 경로와 교차 측정한 세 N16 설정에서 native wall의 중앙값은 0.551→0.123 s, 1.793→0.362 s, 1.936→0.397 s였다. 각 설정의 paired speed ratio 중앙값은 각각 약 4.54, 4.89, 4.61이다. 이 결과는 명시한 유한 설정과 이 sandbox의 측정이다.

독립 이력 병렬화에는 pinned VigilODE가 이미 제공하는 `ParallelExecution::rayon`과 `map_ordered`를 실제로 재사용했다. 세 이력을 처리하는 교차 batch 측정의 중앙 wall은 worker 1/2/4에서 1.714/1.000/0.893 s였다. 입력 이력이 3개이므로 worker 4의 실효 동시성은 최대 3이다. 측정 중 시간 변동이 남아 있어 일반적인 병렬 확장 법칙으로 승격하지 않는다.

메모리 감소는 확인하지 않았다. 작은 C 부모 프로세스의 fork/exec/wait4로 측정한 4개 표본은 legacy 6400·6396 KiB, cache 6552·6456 KiB였다. 이번 최적화는 반복 준비 계산을 줄이며, 모든 node를 동일 순서로 합산하기 위한 cell cache와 임시 contiguous node buffer를 사용한다. 전체 node clone이나 RHS 출력 할당까지 제거한 구현은 아니다.

기존 19개 설정을 캐시 경로로 다시 실행했고, 독립 검토는 원본과 329,983개 값·구조 경로를 대조하여 차이 0을 확인했다. 이는 같은 19개 설정의 회귀 재현이며 새 19개 우주론 문제를 추가한 것이 아니다. 원래 76개 제조 수치문제, Python 57개, 기존 V14/SSPRK/NCP 이력은 다시 세지 않았다.

## 1. 새 실행 확인과 source 계보

연구 전에 GitHub PR198의 delivery HEAD `5cccbcfb28a2cec57997493160b49b79954fe8f3`와 지정 Drive/Dropbox 트리를 다시 확인했다. Drive는 V14 지정 폴더와 5개 하위 폴더, 총 28개 항목을 읽었고 Dropbox recursive는 43개 항목, `has_more=false`였다. 2026-10-20T05:29Z 이후 수정 항목이 없었으므로 새 native 실행으로 판정할 후보가 없었다. 이미 검증한 C10/C11 archive를 다시 실행으로 세거나 불변 archive를 재다운로드하지 않았다.

현재 baseline scientific source는 `d87ba9ca25acb8a2a032154fa23057b45acd6207`, VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다. 실제 baseline 복원은 native 152개 파일과 VigilODE 477개 파일을 검증했다. 이 회차의 변경은 연구 adapter, 그 additive native module/hook, runner와 연구 증거에 한정된다. 원본 native 152개 파일과 VigilODE 477개 파일의 bytes는 그대로다.

VigilODE PR73–76을 실제 조회했고 PR76의 successor 실행 run39361177464까지 읽었다. 그 실행 source는 `3bc8c937db1023356760c28db1cec04facee228d`, exit 0, audit 312 rows/30 pairs, 요약 26 matched/4 diagnostic이었다. 이는 다른 표준 강성계/few-mode 실험이다. 그 수치나 속도를 LRS의 성과로 옮겨 쓰지 않았다. 상세 source/API/receipt 조회는 `upstream/RETRIEVAL.json`에, 후보 비교는 `upstream/FINDINGS_KO.md`에 보존했다.

## 2. 실제 식에서 얻은 최적화

한 source-free chemical segment 안에서 geometry, scale factor, 수소·헬륨 밀도, CMB 온도, photon support 및 좌표 scale은 고정된다. 기체를 \(g=(x,y,z,W)\), 점유 photon cell의 좌표를 \(p_k\in\mathbb R^{d_k}\), \(d_k\in\{1,2\}\)로 둔다. 모든 입자수와 에너지는 total-H 기준이며

\[
Y=\frac{0.2454}{4(1-0.2454)},\qquad e=x+Y(y+2z).
\]

node의 number를 \(v_\ell\), reference energy를 \(q_\ell\), ray scale을 \(r_k\)라 하면 physical energy는 \(E_\ell=r_kq_\ell\)이다. 원본 native opacity/provider로 계산한 사건률은

\[
P_{\ell j}=c n_H\alpha_j\sigma_{\ell j}v_\ell,
\qquad \alpha=(1-x,Y(1-y-z),Yy).
\]

따라서 광자 RHS는

\[
\dot N_k=-\sum_{\ell\in k,j}P_{\ell j},\qquad
\frac{d}{dt}(U_k-\ell_kN_k)
=-\sum_{\ell\in k,j}(q_\ell-\ell_k)P_{\ell j}.
\]

cell k의 광자 출력은 자신의 moments와 공통 gas fractions에만 의존한다. thermal coordinate W와 다른 photon cell의 moments에는 의존하지 않는다. 기체 출력은 모든 cell의 photo-input을 합산한다. 실제 코드의 의존성은

\[
\dot g=F_0(g)+\sum_k H_k(g,p_k),\qquad
\dot p_k=G_k(g,p_k)
\]

이며 Jacobian은

\[
J=\begin{pmatrix}
A&B_1&B_2&\cdots\\
C_1&D_1&0&\cdots\\
C_2&0&D_2&\cdots\\
\vdots&\vdots&\vdots&\ddots
\end{pmatrix}.
\]

이는 물리 coupling을 버리는 근사가 아니다. 이미 source-free native 함수에 존재하는 변수 의존성이다. gas의 네 row는 모든 photon column과 연결되므로 전체 Jacobian을 단순 2-color FD만으로 복구할 수는 없다.

### 구현한 재사용 범위

`Context::jacobian`에서 base photon state의 `PreparedCell`을 한 번 만든다. gas 4개 좌표의 ±섭동에는 이 준비 결과를 재사용한다. photon 좌표의 ±섭동에는 해당 cell만 기존 `prepare_cell`로 다시 준비한다. 이후 모든 cell/node를 원래 순서로 이어서 기존 `native_rates`를 실행한다. photon compensated sum, species loop, 전역 사건/에너지 합산의 연산 순서를 유지한다.

평균 에너지가 바뀌면 exponential reconstruction의 beta, panel 수, steep node 위치, threshold 분할과 cross section이 바뀔 수 있다. 따라서 geometry만 같다는 이유로 모든 photon node를 고정하지 않았다. 다른 cell state 또는 support가 달라진 요청, shape 불일치, 잘못된 cell index는 명시적으로 거부한다. 캐시는 한 Jacobian 안에서만 살며 새 segment/geometry/birth/base state에서는 새로 만든다.

FD epsilon, central/one-sided 차분식, `PerturbationDomain`과 `Fatal` 구분, charge 순서, 즉시 fatal 중단과 실패한 후보의 상태 복원은 유지했다. 성공용으로 native rates, EOS, tolerance, GL2 시각 또는 solver를 바꾸지 않았다.

### 비용식과 실제 확인

점유 cell 수를 m, 좌표 차원을 \(d=4+\sum d_k\)라 하면 기존 준비 횟수는 \((1+2d)m\), 캐시는 \(m+2\sum d_k\)다. m=40, d=84인 실제 seeded state에서

\[
6760\longrightarrow200
\]

을 Rust 실행으로 확인했다. RHS 시도 수 169회는 양쪽에서 같았다. 빈 photon state는 d=4, 9회 시도, 준비 0회이고 delta cell은 d=5, 11회 시도, 준비 11→3회였다.

33.8배는 한 Jacobian의 준비 작업 수 비율이다. 전체 이력에는 Jacobian 이외의 RHS와 stage replay가 있으므로 같은 비율이 되지 않는다. 실제 fixed N16 전체 이력은 준비 119680→14720회, 약 8.13배 감소였으며 node 방문 1914880회와 charged RHS 2992회는 그대로였다.

## 3. 실제 profiling과 같은 정확도의 시간 측정

Host: AMD EPYC 9V74, 사용 가능 CPU 0–8, cgroup quota 8 CPU, RAM 8 GiB, swap 없음. Rust 1.94.1/cargo 1.94.1, locked/offline/release이며 빌드는 jobs 2였다. 개별 성능 측정은 CPU 0에 고정하고 native transport 1 thread, 동일 geometry/source/resolution/initial state, Radau Newton scaled atol 1e-13·rtol 0을 유지했다.

같은 candidate binary에서 `legacy`와 `cell-cache`를 선택했다. 두 경로 모두 context의 불변 ray-scale cache를 포함하므로 아래 수치는 주로 Jacobian-local cell 준비 재사용의 효과다. 별도로 변경하지 않은 original-source binary의 N16 출력 3개를 생성하여 두 경로의 물리 결과를 비교했다.

각 설정·variant를 warm-up한 뒤 5쌍을 AB/BA 교대로 측정했다. 아래 중앙값은 native JSON의 내부 wall이며 process wall은 별도로 보존했다. profile flag는 측정 시 꺼져 있었다.

| 설정 | legacy 중앙 native s | cache 중앙 native s | paired ratio 중앙값 | 모든 paired ratio 범위 |
|---|---:|---:|---:|---:|
| fixed, Radau N16 | 0.550993 | 0.122657 | 4.5382 | 4.2224–4.6442 |
| GL2 birth, Radau N16 | 1.792522 | 0.361862 | 4.8865 | 4.5708–5.2739 |
| seeded disabled, Radau N16 | 1.936270 | 0.397404 | 4.6051 | 4.2750–5.7487 |

중앙값의 비와 paired ratio의 중앙값은 다른 통계다. 원시 5쌍 모두, 각 범위/IQR, source/binary SHA, 실제 argv, stdout/stderr와 종료코드를 남겼다. process-wall 중앙값은 각각 0.666076→0.214912, 2.073549→0.666494, 2.272976→0.720854 s이며 native wall과 혼합하지 않는다.

profile-on fixed N16 한 쌍은 측정 원인을 확인하는 별도 관찰이다.

| 관찰 | legacy | cell-cache |
|---|---:|---:|
| charged RHS attempts | 2992 | 2992 |
| node visits | 1914880 | 1914880 |
| occupied cell preparations | 119680 | 14720 |
| preparation s | 0.495075 | 0.078447 |
| native node rates s | 0.015549 | 0.016176 |
| gas provider s | 0.007003 | 0.007128 |
| inclusive Jacobian s | 0.474229 | 0.051619 |

Preparation/rates/provider는 실제 기록된 평가 구간의 배타 시간이며 Jacobian 시간은 그중 일부와 겹친다. 이 열을 모두 더해 총 wall로 만들지 않는다. admissibility와 일부 context/solver/report 비용은 이 세 구간 밖이다. profile의 fine-grained clock은 profile-off 시 실행하지 않는다. 작업 카운터는 profile-off에도 남는다.

## 4. 병렬화, 벡터화와 경량화의 선택

별도 `src/bin/lrs_batch.rs`가 현재 pin의 `rodas5p_integrators::ParallelExecution`을 사용한다. 로컬 Rayon pool의 입력은 고유 CPU와 순서가 정해진 이력 목록을 가진 worker slot이다. 각 slot은 자신의 child를 순차 실행하며, slot 간 DriverState/Budget/output은 독립이다. pool 결과는 입력 순서로 수집한다. 각 이력 안의 stage, GL2 birth, 사건 합산도 기존 순서를 유지한다. native child는 taskset으로 CPU를 고정하고 timeout으로 실행 시간을 제한한다. child의 nonzero 종료는 결과 자료로 보존한 뒤 전체 batch를 실패로 판정한다.

최초 width별 연속 측정에서는 worker 1의 시간 변동이 커서 width 1/4 중앙값 비가 3 job 상한을 넘었다. 해당 자료는 진단 결과로 보존했다. 같은 바이너리로 한 번 추가한 교차 측정에서는 width 순서를 [1,2,4], [4,1,2], [2,4,1]로 배치했다. 9 batch가 11.1554 s 안에 끝났고, 27 child 모두 exit 0이었다. 큰 raw JSON의 비교는 전체 시간 측정이 끝난 뒤 수행했다.

| worker slots | 세 whole-batch wall s | 중앙값 s | worker 1 중앙값 대비 관측비 |
|---|---|---:|---:|
| 1 | 1.533921,1.714462,1.919065 | 1.714462 | 1 |
| 2 | 0.999520,1.000239,1.120961 | 1.000239 | 1.7141 |
| 4 | 0.786588,0.892772,0.953085 | 0.892772 | 1.9204 |

이는 3개의 독립 이력을 처리하는 처리량 실험이다. 한 이력의 시간 가속과 구분하며, 4 slots 중 최대 3개만 사용한다. 시간이 전반적으로 증가하는 drift도 남아 있다. 위 관측 범위 밖의 core 수/resolution/host에서는 다시 측정해야 한다.

기존 faer 0.24.4는 dense LU와 SIMD가 구현된 패키지이며, 공식 low-level API는 caller 소유 MemStack/scratch 재사용을 지원한다. 현재 VigilODE manifest는 faer의 rayon feature를 켜지 않는다. 이번에는 비용 비중이 확인된 native 준비 반복을 줄이고 기존 Rayon pool을 사용했다. 별도 SIMD crate, fast-math, global reduction 재결합, threaded LU, 새 RODAS5P solver는 도입하지 않았으며 구현 완료 항목에 포함하지 않는다.

실제로 줄어든 것은 재구성/cross-section 준비 횟수와 실행 시간이다. photon node를 다시 연속 buffer로 복사하는 할당은 남아 있다. memory 표본은 약 6.25 MiB 대 6.30–6.40 MiB로, 감소 주장의 근거가 없다. 향후 할당 감소를 시도한다면 immutable node iterator와 caller-owned rate scratch가 명확한 후보지만, 실제 남은 비용 비중과 실패 후 초기화의 동등성을 확인해야 한다.

## 5. 외부 코드·문헌을 적용한 범위

| 자료 | 확인한 기능 | 이번 회차 적용 |
|---|---|---|
| pinned VigilODE Radau | 기존 modified Newton/frozen J/residual-first | 그대로 유지; 이미 있던 기능을 새 성과로 세지 않음 |
| pinned VigilODE ParallelExecution + Rayon 1.12.0 | local ThreadPoolBuilder, ordered map, explicit width | 독립 이력 batch에 실제 사용/컴파일/실행 |
| faer 0.24.4 | dense LU, low-level scratch/in-place API, feature 조건 | 기존 LU 사용; workspace 추가 변경은 후속 후보 |
| native prepare_cell/cell_quadrature/AtomicProvider | state-dependent positive reconstruction과 cross-section | 캐시 miss 때 원본 함수를 직접 재사용 |
| van der Houwen–Sommeijer, CWI/ZAMM 1996 | RK stage/block-Jacobian 반복의 구조와 비용 | Schur 후속 설계와 조건을 검토; 새 solver 구현으로 세지 않음 |

정확한 API/manifest는 [faer 0.24.4 memory allocation](https://docs.rs/faer/0.24.4/faer/linalg/index.html), [faer manifest](https://docs.rs/crate/faer/0.24.4/source/Cargo.toml), [Rayon 1.12.0 manifest](https://docs.rs/crate/rayon/1.12.0/source/Cargo.toml), [pinned ParallelExecution](https://github.com/cosmosapjw-quantum/vigilode/blob/8a8bd409b1d96c7b7421f496d229e119fd3d284e/crates/rodas5p-integrators/src/parallel.rs), [CWI 원문 서지](https://ir.cwi.nl/pub/1390)에 있다. Exa와 SciSpace를 실제로 사용해 조회했으며, 최종 출판 연도 1996은 CWI 원문으로 확인했다. SciSpace 검색의 1995 표기를 그대로 채택하지 않았다. MIT/Apache license와 현재 pin의 MSRV 1.94.1 범위에서 사용했으며, 새 의존성 추가는 없다.

## 6. 유도는 마쳤지만 구현하지 않은 후속 경로

현재 bordered J에 대해 3-stage Radau의 252×252 frozen-J 행렬을 cell 우선으로 재배열하면 gas 블록은 12×12, cell 블록은 최대 6×6이 된다. local 블록을 \(M_{kk}\)라 할 때 가역 조건하에서

\[
S=M_{gg}-\sum_kM_{gk}M_{kk}^{-1}M_{kg},\qquad
b_S=b_g-\sum_kM_{gk}M_{kk}^{-1}b_k,
\]
\[
S\delta g=b_S,\qquad
\delta p_k=M_{kk}^{-1}(b_k-M_{kg}\delta g).
\]

이는 같은 선형계의 block elimination이다. 전체 행렬이 가역이라고 모든 local 블록이 가역인 것은 아니므로 dense fallback과 backward residual 검사가 필요하다. 아직 구현하거나 시간 성능을 검증하지 않았다.

고정 node topology의 exponential family에서는

\[
\frac{d\langle a(q)\rangle}{d\mu}
=\frac{\operatorname{Cov}(a(q),q)}{\operatorname{Var}(q)}
\]

로 analytic moment derivative를 쓸 수 있다. endpoint 분산 0, panels 변화, steep moving node와 \(\sigma(E)\) 미분은 별도 처리가 필요하다. Wolfram이 검산한 것은 이 전제하의 대수 항등식이며, 전 범위 native analytic Jacobian이 완성됐다는 증거가 아니다.

## 7. 검증과 실패 보존

- 변경하지 않은 baseline release build는 exit 0, candidate release build도 exit 0이었다. 최종 case binary SHA256은 `24f9d38e56d3380e830478b8afe7760b2f44fff7ab60167ed14aa668ae7f4ac0`이다.
- Rust 표적 시험 10개 PASS: 기존 7개와 신규 cache 회귀 3개. 신규 시험은 실제 seeded/empty/delta의 전체 Jacobian, threshold/steep 재구성, stale cache 거부와 실패 시 상태 복원을 다룬다.
- 첫 threshold fixture가 실제 native energy bin을 벗어나 exit 101로 실패했다. 원시 실패를 보존하고 fixture를 실제 HeI threshold를 포함한 bin으로 고친 뒤 통과했다. solver나 허용오차를 고쳐서 통과시킨 것이 아니다.
- 기존 19개 설정의 cache 회귀, paired 측정 30개 출력, 최초 batch 36개 child, 교차 batch 27개 child, 메모리 표본과 옵션 전달 smoke의 각 raw/exit를 보존했다. 반복 실행은 고유 물리 설정 수를 늘리지 않는다.
- Python 실행기 회귀 4개 PASS. `prepare_and_run.py --all --native-eval cell-cache`의 전달 경로는 실제 fixed Radau N2/profile smoke로 확인했다.
- 초기 batch 호출의 인자 누락과 `/usr/bin/time` 부재로 인한 실패를 보존했다. RSS 측정은 optional로 처리했다. 초기 Python fork 메모리 쌍은 pre-exec parent RSS 오염 가능성으로 판정에서 제외하고 C helper 표본을 별도로 남겼다.
- 독립 Astra 에이전트는 코드를 구현하지 않고 diff와 raw를 검토했다. 값의 일치는 finite numeric exact equality이며, signed-zero의 비트 동일성 검사가 아니다.

비교는 P/C/R/D, photo-binding/photo-heat, CE/RR/DR/FF/CMB/escape, work와 photon/state 출력을 포함했다. 저장되지 않은 물리 정보를 추가로 독립 회수했다고 말하지 않는다. 모든 원본 physics field가 같으므로 기존 유한 setting의 stage/endpoint/ledger 결함도 보존되며, 시간 정확도가 새로 증명된 것은 아니다.

## 8. 전달과 다음 실행

현재 사용 가능한 경로는 명시적 `--native-eval cell-cache`다. 기존 CLI/default와 public Budget::new는 legacy다. NCP에서는 정상 Git 파일을 회수하고 정상 prepare/compile/test/run을 수행하면 된다. `CODEX_NCP_OPTIMIZATION_KO.md`와 `FINAL_DELIVERY.json`이 이번 회차의 최신 인계이다. 이전 source의 NCP 19개 설정 완료와 이번 optimization의 NCP 실행을 구분한다.

이 sandbox에는 사용자가 지정한 `/home/cosmosapjw/.ssh/ncp_key`가 없으며, 사용 가능한 NCP/SSH 실행 connector도 없었다. 이번 최적화의 NCP 실행은 NOT_RUN이다. 사용자의 다운로드나 수동 SSH/SCP를 요구하지 않고 Codex용으로 복사 가능한 명령을 제공한다.

C1–C4 checkpoint는 commit `d07c326658a41ece2722271c3f4e1cf62972f145`로 게시했고, 15개 Git 파일의 원문을 readback했다. Drive/Dropbox 전체 파일 GET은 둘 다 HTTP 200, 93202 bytes, SHA256 `ec610f486be6c99c367d8be0ae9b500fa9e884c90d946d6ef1704d9ccdb1514b`로 일치했다. 코드·실행 증거의 source commit은 `33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1`이며 41개 파일의 정확한 Git 원문 readback이 통과했다. 최종 C10 archive는 53,269,577 bytes, SHA256 `623797d7a8b83b078f10ffaad780c7b2c223247e8b5593110c8d5f52286991b0`이다. Drive `1TV56tJoJXkK4XyFTXTrnTgCtfDDOTJzT`와 Dropbox `id:BSpOijBcT10AAAAAAD_SPg`에서 전체 GET/exit 0/동일 SHA를 확인했다. Drive 회수본의 payload 5,462개 파일과 330,173,104 bytes도 내부 manifest와 모두 일치했다. 정상 prepare-only 복원은 exit 0이며 native 153개·adapter 7개·VigilODE 477개 파일이 컴파일한 최종 소스와 같았다. 보존 확인서도 양쪽 전체 readback이 통과했다. 최종 ID·receipt·DAG는 `FINAL_DELIVERY.json`과 `FINAL_BACKUP_ACK.json`에 기록했다.

일반 source-on 전체 차수, uniform stiff 정확도, 일반 양수성, CaseB, fullEoR, signed Bianchi, positive CMB/nonzero boundary, continuous/global certificate는 HOLD다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`이며, 이번 승인은 유한 native 동등성과 명시한 비용 관측 범위에 한정된다.
