# HE30 최적화 연구: 완료된 z=20→2 궤적을 재사용하는 BASS_HE 기여

작성일: 2026-10-21 UTC. 대상은 non-tilted LRS Bianchi I의 collisionless massive matter와 radiation을 분리한 고정 유한 격자다. 현재 구현·데이터에 대한 근거는 [analyze_saved.py](src/analyze_saved.py), [shared_runner.py](src/shared_runner.py), [ANALYSIS_SUMMARY.json](results/ANALYSIS_SUMMARY.json), [CATALOG.json](results/CATALOG.json), [D3_SOURCE_AUTHORITY.json](evidence/D3_SOURCE_AUTHORITY.json)에 있다. 단계별 DAG·게시·백업과 다음 실행 인계는 이 문서와 별도인 해당 영수증을 따른다.

## 1. 연구 결과와 실제 변경의 경계

이번 작업에서 오늘의 목표에 가장 직접적인 개선은 **이미 끝난 D3의 237개 궤적을 찾아 재사용하고, 그 원자료에서 독립 matter/radiation parameter sweep과 z=20→2 시간 진화 그림을 만드는 것**이다. 새 solver를 넣거나 기존 구간을 다시 계산하는 일은 필요하지 않았다. 신규 과학 IVP·tail 적분·benchmark는 모두 0회다. 저장 배열의 hash, 좌표, 접합, 분리 stress, 그림용 통계를 계산한 것은 실제 수행한 후처리이며, 이를 새 ODE 실행으로 집계하지 않는다. 원 D3의 237개 tail IVP는 이전 실행 실적으로 따로 남긴다. [결과 요약](results/ANALYSIS_SUMMARY.json), [원 실행 identity](evidence/D3_SOURCE_AUTHORITY.json).

| 구분 | 현재 상태 | 이번 결과와의 관계 |
|---|---|---|
| 완료 D3 원자료와 exact prefix/tail 재사용 | 구현·실제 처리 완료 | 237개를 새 적분 없이 소비한다. |
| NumPy 배열 단위 정규화·성분 분리·endpoint·guard 비교 | 구현·실제 처리 완료 | `237×153` 저장 epoch 배열을 처리한다. |
| compact observable archive와 case별 원본 SHA 연결 | 구현·생성 완료 | 재표시와 분석 입력을 가볍게 한다. |
| 공유 CPU/case lease와 동적 자원 admission | 구현·경량 검사 완료 | 향후 실제 pending 작업에 재사용할 실행기다. |
| canonical momentum의 고정 positive weights와 기존 `moment_batch` | 기존 vendor 구현 재사용 근거 확보 | 이번에는 저장된 moments를 읽으므로 새 moment 평가도 필요 없다. |
| `q²(1−μ²)`, `q²μ²`, 정규화 weights의 추가 준비와 fused reduction | 식과 변경 위치를 특정한 후속 후보 | D3 kernel에 새 패치를 적용하지 않았다. |
| PR198의 full40→reduced8 | 기존 다른 계열의 구현·검증 근거 확보 | D3 실행 방식으로 재분류하지 않는다. |
| ACCEL01의 exact binary64 C15 moment cache | 기존 warm C15 계열에서 구현·검증됨 | 설계와 조건을 재사용하며 현재 D3에 붙였다고 주장하지 않는다. |
| native H/He chemistry와 자기일관 electron feedback | 이번 모델에 없음 | 현재 `ne_source=None`; 후속 donor/adapter의 범위를 정한다. |

실제 처리량·저장 크기·차이값과, 식에서 유도한 연산량·메모리 추정은 아래에서 구분한다. wall-time 가속 배수, strong scaling, peak RSS 또는 NCP에서 새로 실행한 성능 결과는 제시하지 않는다.

## 2. 최신 저장소와 백업을 연결한 source authority

조사 시점의 접근 가능한 branch ref는 BASS_HE 87, rei_bianchi 255, bass 262, bass_cr 168, vigilode 185개로 총 957개다. 목록 pagination은 끝까지 읽었고, 각 저장소의 updated순 최근 PR과 과학 의존성이 있는 원문을 추가로 읽었다. 모든 branch의 모든 파일이나 비공개 대화 전체를 읽었다는 의미는 아니다. 조사 범위와 원문별 SHA는 [UPSTREAM_FINDINGS_KO.md](evidence/UPSTREAM_FINDINGS_KO.md), [UPSTREAM_SOURCE_MANIFEST.json](evidence/UPSTREAM_SOURCE_MANIFEST.json)에 연결되어 있다.

| 계열 | 조사 당시 branch/head | 이 작업에서 채택한 범위 |
|---|---|---|
| BASS_HE PR82 | `research/he29-rei-sigma-pi-pilot-20261021` / `048a73de4246f609b1bc14854ea5c48757cb82fd` | canonical mapping, Frobenius adapter, 공유 runner의 선행 구현. 기존 cold pilot은 z20→4다. |
| BASS PR176 / REI PR213 | `research/rei-sigma-pi-pilot-20261021` / BASS `26f4a89a54462c4e7c5705f281f187f33f45166a`, REI `d32cd99fa19c65aa1ca63dbc8aab8741834270e8` | 729-case/243-group warm 결과. 실제 구간 `a=.1999→.2`이며 장구간 D3와 합산하지 않는다. |
| BASS PR177 / REI PR214 | `research/rei-sigma-pi-acceleration-20261021` / BASS `4f19e6eaf50e8458d59d27ff47f03e9d8c8b22ca`, REI `98fcf3943fa54e089b0292d166c3a47becb5edb8` | exact C15 moment cache, 완료 registry, pending-only 배치 설계. |
| bass_cr C21M PR91 | `research/cr-c21m-independent-stress-20261021` / `b78a943e5d7ae341bbfe84f742a06a4ac36d0e43` | 독립 stress 27점, z20→4의 full-state 자료. D3 발견 전 검토한 donor다. |
| REI PR198 | `research/rei-lrs-v14-physical-birth-20261018` / `8bd35af5f11c7ea5945b656be1c013d1c1933498` | 기존 reduced8 source와 조건부 full/reduced 비교 근거. |
| REI PR199와 D3 백업 | `research/rei-age-exposure-envelope-20261018` / 관측 D0 게시 `8b71c13e23202edfce1ee67fb2da552fefb9a583` | D0는 계약·인벤토리 게시다. D3 실행 authority는 아래 archive와 실행 파일별 SHA로 잡는다. |

현재 D3의 핵심 identity는 다음과 같다.

- archive: `REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`, 31,904,176 bytes.
- archive SHA256: `7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498`.
- 물리 kernel: REI PR147 commit `3b85dedce84d37b3e165da00685a8a984950aafe`.
- `canonical_fv.py` SHA256: `91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5`.
- 실행 runner `components/unified_pilot.py`: 원 실행 `49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97`, 직렬화 보완 후 `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64`.
- compact `histories.npz` SHA256: `d4258bc58948b318df2b9d5ea7ceca6258eac62147aececc6ec10068987b6c6c`.

D3 결과 전체의 Git 게시 위치는 초기 archive 조사만으로 확인되지 않았다. 게시 직전 최신 상태를 다시 읽어 다른 세션의 REI source/results `3a525e3e16f1ba9393818a800327cc58597fd7b5`와 closure `744438f4512c7df1646aad0136ddc435b27200b0`를 확인했다. [그 시점의 실제 원문](evidence/UPSTREAM_FINAL_STATUS_OBSERVED.md)을 별도로 보존한다. D0 commit을 D3 실행 commit처럼 쓰지 않고, 원료 archive, kernel commit, 실제 실행 파일 SHA, 파생 compact SHA를 각각 보존한다. [정확한 초기 authority와 provider 정보](evidence/D3_SOURCE_AUTHORITY.json).

HE PR82의 완료40 보고와 현재 회수 가능한 raw27은 구별한다. 업로드되지 않은 missing13을 D3로 복구했다고 하지 않는다. D3는 별도로 완료된 데이터이며, 이번 목표에는 그 완전한 결과가 직접 적합하다. 기존 C21M27 continuation 계획도 새 과학 실행 전에 이 발견으로 대체했다. [백업 조사](evidence/BACKUP_CONTEXT_FINDINGS_KO.md), [대체된 계약](evidence/CONTRACT_SUPERSEDED_BEFORE_EXECUTION_KO.md).

## 3. 현재 데이터의 정확한 규모와 물리 좌표

D3는 평균 redshift `z̄=1/a−1`의 `20→4→2`를 다룬다. 초기 기준은 `a_ref=1/21`, 좌표는 `x=ln(a/a_ref)`, 최종은 `x=ln7`이다. 기존 prefix 121 epoch와 join을 포함한 tail 33 epoch를 접합점 한 개만 남겨 총 153 epoch로 저장했다. 평균 redshift는 방향별 관측 redshift와 구별하고, `elapsed_proper_s`는 z̄=20부터의 경과 시간으로 읽는다. [추출 코드](src/analyze_saved.py), [결과 요약](results/ANALYSIS_SUMMARY.json).

독립 joint grid는

\[
\Sigma_{F,i}\in\{0,0.0003,0.001,0.003,0.01,0.03,0.1\},
\]
\[
P_{m,i}\in\{-0.0003,-0.0001,0,0.0001,0.0003\},\qquad
P_{r,i}\in\{-0.001,-0.0003,0,0.0003,0.001\}
\]

의 `7×5×5=175`점이다. 기존 radiation baseline 91점과 겹치는 35점을 제외하면 nominal은 231점이며, 별도 refinement guard 6점을 더하면 237점이다. 각 nominal은 `40×153`, guard는 `56×153` full-state 배열을 원 archive에 보존한다. guard는 `ellmax=12, radial×angular=48×24, Gauss3`, nominal은 `ellmax=8,24×12,Gauss3`이다. 적분기는 기존 DOP853, `rtol=3e−11, atol=3e−13`이다. [source/config와 raw shape](evidence/D3_SOURCE_AUTHORITY.json), [case catalog](results/CATALOG.json).

직교 정규 성분에서 `D=diag(−1,−1,2)`, `σ=sD`, `π_X=p_XD`라 두면

\[
\Sigma_F=\frac{\sqrt6|s|}{H},\qquad
P_X=\frac{\kappa_t\sqrt6p_X}{H^2},\qquad
\Pi_X=|P_X|,\qquad \kappa_t=\frac{8\pi G}{c^2}.
\]

`s,H`는 s⁻¹, `p_X`는 J m⁻³이다. 따라서 Einstein convention `κ_E=8πG/c⁴`와는 `κ_t=c²κ_E`로 연결한다. vendor의 half-contraction norm에는 추가로 `Σ_F=√2 Σ_half`가 필요하다. 성분의 합은

\[
P_{\rm total}=P_m+P_r,\qquad
\Pi_{\rm total}=|P_m+P_r|,\qquad
\sigma:\pi_X=6sp_X
\]

로 처리한다. `Π_m+Π_r`를 total로 캐시하면 cancellation을 잃는다. 성분마다 magnitude와 signed amplitude를 함께 보관하는 것이 후처리와 향후 kernel 변경 모두의 계약이다. [물리 유도](evidence/PHYSICS_REUSE_KO.md), [독립 원자료 검토](evidence/INDEPENDENT_DATA_READBACK.json).

## 4. 연산·메모리·의존성의 병목을 어떻게 구분했는가

프로파일을 실행하지 않았으므로 어느 함수가 wall time의 몇 퍼센트인지 단정할 수 없다. 소스와 artifact에서 확인되는 비용 구조는 다음과 같다.

| 위치 | 소스에서 확인한 비용 | 오늘 제거하거나 줄인 일 | 현재 남는 의존성 |
|---|---|---|---|
| 독립 case의 RHS 반복 | adaptive solver가 moment·radiation·geometry를 반복 평가 | 동일 완료 IVP의 재실행을 없앴다. | 새 물리 입력에 대해서만 RHS가 필요하다. |
| canonical massive moments | packet 수에 비례하는 square root와 energy/pressure reductions | 저장된 D3 observables를 그대로 사용한다. | 미래 새 state의 moments에는 기존 kernel 또는 검증된 변경이 필요하다. |
| 자료 로딩과 provenance | NPZ decompression, 파일 hash, 원 prefix/tail 비교 | 원자료를 compact 분석물로 한 번 변환한다. | 처음 채택할 때 source/input/raw identity를 검토해야 한다. |
| 그림 반복 생성 | 같은 배열의 선택·축 변환·rendering | `--plot-saved`로 compact archive에서 재표시한다. | 그림 manifest가 compact SHA 및 실제 case IDs에 연결되어야 한다. |
| 실행 orchestration | 다른 세션의 CPU/RAM 점유, 중복 case, worker 초기화 | 동적 admission과 case/CPU leases를 사용한다. | 전역 중지 대신 현재 실제 여유를 관측한다. |
| 실패 회수 | 계산과 JSON 직렬화의 완료 시점이 다름 | full raw와 실패 receipt를 보존하여 과학 재실행 없이 회수한다. | 유실된 실행 metadata는 null로 남긴다. |

특히 D3의 100개 case는 raw/tail 저장 뒤 `np.bool_`의 JSON 직렬화 단계에서 실패했다. 완전한 raw를 회수한 후 필요한 검사를 했으며, `nfev`, 원 solver message, worker wall time/RSS는 남아 있지 않은 항목을 null로 보존했다. 나머지 137개 tail은 당시 보완된 runner에서 완료됐다. 이 구조는 계산 DAG의 실패와 결과 직렬화 실패를 분리해야 한다는 실제 근거다. 오늘 이 100개를 재계산하거나 유실된 성능 수치를 추정해 넣지 않았다. [B2 recovery와 실행 SHA](evidence/D3_SOURCE_AUTHORITY.json).

현재 의존성의 핵심은 `원본 authority 확인 → 원자료 hash/접합 확인 → 정규화·분리 stress 배열 → compact 자료/그림`이다. 기존 solver·prefix·tail은 완료된 입력 노드다. 모델 변경이 없는 renderer 수정 때문에 이 완료 노드를 다시 실행할 필요가 없다. 반대로 source·초기 분포·collision term이 달라지면 새 모델 identity가 필요하며, 파일 이름이 같다는 이유로 완료를 상속하지 않는다.

## 5. canonical immutable weights가 허용하는 최적화

현재 vendor는 collisionless Bianchi I의 공간 translation Killing momentum을 사용한다. 분포의 positive cell populations는 시간에 따라 움직이는 상태가 아니라 초기 canonical quadrature의 상수다. 물리 momentum만 metric과 함께 redshift된다. massless Bianchi I의 distribution·stress 대응은 Dash–Jaiswal의 원전에서 확인했고, massive extension과 유한 quadrature 보존식은 이번 물리 노트에서 mass shell로 직접 유도했다. [Dash–Jaiswal, PRD 97, 104005](https://arxiv.org/abs/1711.07130), [자체 유도·Wolfram 근거](evidence/PHYSICS_REUSE_KO.md), [수치 항등식 receipt](evidence/CANONICAL_MOMENT_CHECKS.json).

`r=e^{−x}`, 고정 quadrature node `q_j, μ_j`, 질량 `m`, 고정 비음수 packet weight `w_j`, 초기 energy normalization `N`에 대해

\[
p_{\perp,j}^2=q_j^2(1-\mu_j^2)e^{-2x+2b},\qquad
p_{\parallel,j}^2=q_j^2\mu_j^2e^{-2x-4b},\qquad
E_j=\sqrt{m^2+p_{\perp,j}^2+p_{\parallel,j}^2}.
\]

따라서

\[
\rho=\frac{e^{-3x}}{N}\sum_jw_jE_j,\quad
P_\perp=\frac{e^{-3x}}{N}\sum_j\frac{w_jp_{\perp,j}^2}{2E_j},\quad
P_\parallel=\frac{e^{-3x}}{N}\sum_j\frac{w_jp_{\parallel,j}^2}{E_j}.
\]

현재 `CanonicalMomentumFV`는 `_q`, `_mu2`, `_numbers`, `_cell_numbers`를 read-only로 두고 number sum과 reference normalization을 준비한다. 기존 scalar `moments`에서는 각 호출에 `(r*q)^2`와 angular factors를 다시 조합한다. 식을 보존하는 다음 변경 위치는

\[
A_j=q_j^2(1-\mu_j^2),\qquad B_j=q_j^2\mu_j^2,\qquad W_j=w_j/N
\]

를 case 준비 시 계산하고, RHS에서 두 axis factor `exp(−2x+2b)`, `exp(−2x−4b)` 및 volume factor `exp(−3x)`만 곱하는 것이다. `min(cell_numbers)`와 number sum도 고정 값으로 재사용할 수 있다. Legendre energy/number matrices와 photon Thomson diagonal 역시 해당 truncation·operator가 같으면 준비 단계에 둘 수 있다. **이 추가 패치는 현재 D3 vendor에 적용되지 않았다.** 이번 실행 경로는 이미 저장된 moments를 읽는다.

초기 angular weight는 `1+A_m P₂(μ)`이며 양성성 domain은 `−1≤A_m≤2`다. `A_m`, mass, quadrature order, radial/angular nodes, normalization, 단위 또는 source가 바뀌면 준비된 weights도 다른 객체여야 한다. case 사이에 geometry 배열을 공유하더라도 amplitude-dependent weights를 이전 case 것으로 남겨 두어서는 안 된다. 불변 배열이라는 가정은 값뿐 아니라 dtype·shape·strides·소유 수명에 적용한다.

이 변환의 연산량은 여전히 packet당 `O(1)`, moment당 `O(N_packet)`이다. 줄이는 것은 고정 항의 반복 생성, 배열 temporary와 동일점 재평가다. reduction 순서를 바꾸는 fused native loop나 SIMD는 같은 식이라도 부동소수점 합산 결과가 달라질 수 있다. 따라서 실제 도입 시 원 finite quadrature, number/energy/work 항등식과 출력 정규화에 대한 변경 부분만 확인한다. 전체 완료 sweep을 다시 실행할 필요는 없다. 이번 연구에서는 그런 새 kernel 실행이나 가속 배수를 측정하지 않았다.

## 6. 배열 일괄 처리와 메모리 상한

현재 `analyze_saved.extract`는 case별 파일 I/O와 identity 검사를 수행한 뒤 동일 epoch grid의 관측량을 `np.stack`한다. 이후 `Σ_F`, SI stress의 `P_m/P_r`, signed 합, cross term과 오차 reductions는 `(case,epoch)` 배열 연산으로 처리한다. `plot`은 exact grid lookup으로 실제 175점과 대표 저장 궤적을 선택한다. sweep 표면 보간을 만들지 않고, 시간선은 저장 epoch를 연결한다. [현재 구현](src/analyze_saved.py), [그림 provenance](plots/FIGURE_MANIFEST.json).

저장된 분석물의 작성 시점 크기는 다음과 같다. 파일 크기는 실제 bytes이고, 수식으로 적은 payload는 배열 shape에서 계산한 값이다.

| 항목 | 값 | 해석 |
|---|---:|---|
| 저장 case×epoch | `237×153=36,261` | 모든 case에 동일 time grid를 사용한다. |
| float64 관측량 배열 | 21개 | 원 20 fields와 추가 `S_signed`다. |
| 관측량 숫자 payload | `237×153×21×8=6,091,848` bytes | Python 객체·압축·plot 메모리를 포함하지 않는다. |
| compact `histories.npz` | 4,688,444 bytes | 실제 압축 파일이다. |
| NPZ 내부 NPY 전체 | 6,159,392 bytes, 25 members | axis arrays·case IDs·NPY headers도 포함한다. |
| `CATALOG.json` | 280,805 bytes | 원 input/result/raw/prefix/tail SHA와 물리 축을 잇는다. |
| `endpoints.csv` | 154,659 bytes | 실제 endpoint table이다. |
| `selected_histories.csv` | 318,943 bytes | 대표 시간 그림의 모든 저장 점을 담는다. |

compact file은 관측량 archive다. 원 full `raw_y`의 40/56상태를 담지 않으므로 restart checkpoint로 쓰지 않는다. 미래 실제 continuation에는 D3 원 archive의 full state와 정확한 source/config가 필요하다. 31,904,176-byte D3 archive에는 prefix/tail·source·receipts 등 더 넓은 내용이 들어 있으므로 두 파일 크기의 비를 알고리즘 가속률이나 동등한 데이터의 압축률이라고 부르지 않는다. [compact scope](results/ANALYSIS_SUMMARY.json).

새 moment diagnostics가 필요한 미래 작업에는 vendor의 기존 `moment_batch(eta,b,chunk=32)`를 재사용할 수 있다. nominal의 packet 수는 `24×12×3²=2,592`다. 현재 237×153 epoch를 모든 packet과 한 번에 broadcast하면 float64 tensor 하나가 산술적으로 `751,908,096` bytes다. 반면 한 case의 chunk32 tensor는 `663,552` bytes다. 여러 temporary와 guard quadrature를 포함하면 실제 메모리는 더 크므로, case×time×packet 전체 tensor를 한 번에 만드는 방식은 피하고 chunk의 수명을 제한한다. 이 값들은 shape에서 산출한 메모리 예산이며 peak RSS 측정치가 아니다.

현재 compact 후처리는 packet tensor 자체를 만들지 않는다. 수 MiB의 관측량 분석을 64개 process로 무조건 복제할 이유가 없다. 64코어 병렬화의 주 적용 단위는 새로 필요한 독립 IVP 또는 충분히 큰 독립 분석 묶음이고, 공유 자원 runner는 그런 pending 작업에만 자원을 할당한다.

## 7. full40→reduced8의 유효 조건과 D3의 실제 실행 방식

REI PR198의 기존 `pilot.py`에는 `Reduced`가 이미 구현되어 있다. source는 `research/rei_bianchi_sigma_pi_pilot_20261021/pilot.py`, Git blob `0c90eabbb07ee80ba9ba32f855cb698b98b9680b`이며, 독립 matter 초기화는 `matter_radiation_20261021/component_pilot.py`, blob `66a6501cff0e367cfe2263f2d25c24f1ec85f55c`다. 기존 검토 source/results commit은 `b140170ce0c58159368b6b81be49ac35ca764851`다. [선행 조사와 source manifest](evidence/UPSTREAM_FINDINGS_KO.md).

L=8에서 8상태는 `(H_ref Δt,b,s/H_ref,E0,E2,E4,E6,E8)`이다. 축소가 성립하려면 적어도 다음 조건이 함께 필요하다.

1. reflection-even LRS이며 odd multipoles가 초기와 evolution에서 0이다.
2. photon과 massless neutrino의 정규화 energy hierarchy가 같은 초기값과 같은 collisionless operator를 가진다.
3. number hierarchy가 energy/geometry에 역으로 결합하지 않고 thermal slot이 비활성이다.
4. canonical massive weights와 background lock, truncation·closure·initial mapping이 같은 모델이다.
5. 사용자가 필요로 하는 관측량을 보존하거나 별도 algebra로 재구성할 수 있다.

이 조건에서 even energy vector는 `E′=b′ME`이고 고정 M에 대해 `E=exp[(b−b_i)M]E_i`라는 관계가 성립한다. 그러나 기존 `Reduced.rhs` 구현은 이 vector를 ODE state로 적분한다. 현재 HE30이 새 matrix-exponential solver나 3상태 적분기를 도입한 것은 아니다. 기존 full/reduced 비교 6건의 maxabs `2.173e−11` 등은 그 원 source·조건의 검증 근거로 재사용한다. 이를 새로운 operator·collision term의 검증으로 확대하지 않는다.

**현재 D3 nominal 231개는 full40, guard 6개는 full56으로 실행되었다.** 이번 후처리는 해당 full raw의 정확한 접합을 확인한 뒤 관측량만 추출한다. 보관된 reduced8 source는 선행 구현 참고이며 현재 결과를 생성한 solver로 적지 않는다. 향후 `n_e≠0`로 photon만 Thomson collision을 받으면 gamma/nu의 동일 hierarchy 조건부터 깨질 수 있으므로, 기존 8상태를 그대로 채택할 수 있는지 다시 유도해야 한다. [raw shape와 실행 authority](evidence/D3_SOURCE_AUTHORITY.json).

## 8. C15 exact moment cache에서 재사용할 설계와 금지할 근사

ACCEL01의 `cached_context.PreparedContext`는 warm C15 owner `80825585f9fe31d2ee0d5af545ada3fa1f52be72`의 원 `massive_source_3moments`를 miss 때 그대로 호출한다. 고정 model의 mass, quadrature geometry, weights와 normalization 아래에서 moment 세 개는 `(x,b)`에만 의존한다. key는 `struct.pack('>dd',x,b)`이고, finite/domain 검사 뒤 lookup한다. 기본 LRU 128 entries이며 정확히 같은 입력 bytes에서 원래 반환된 immutable float를 재사용한다. [ACCEL01 보고서](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/98fcf3943fa54e089b0292d166c3a47becb5edb8/research/rei_sigma_pi_acceleration_20261021/REPORT_KO.md).

이 설계가 주는 재사용 조건은 명확하다. `round(x,n)`, `round(b,n)`, coarse epoch label 또는 total stress 하나로 key를 만드는 방식은 이 exact cache가 아니다. 서로 다른 geometry state가 같은 key로 합쳐지면 adaptive error estimate와 signed cancellation에 새 근사가 들어간다. 이 작업에서는 rounded key를 적용하지 않는다. photon state, gas temperature, H, 전체 RHS 또는 predictor-corrector proxy를 `(x,b)`만으로 캐시하지도 않는다. source/grid/weights가 변하면 새 model/cache를 만들어야 한다.

원 요청 수를 R, 실제 miss 수를 U, packet 수를 N이라 두면 원 moment 구적 부분의 작업량은 `O(RN)`에서 `O(UN)`으로 바뀌고 lookup/binding 비용이 더해진다. U=R인 workload에는 구적 절감이 없으며 overhead만 생길 수 있다. 기존 ACCEL01의 동일점 hit와 byte-equality 검사는 해당 구현에서 확인한 사실이고, D3에서의 hit율이나 wall-time 향상은 측정하지 않았다. source owner가 다른 canonical FV에 적용하려면 의존성·domain·불변 수명부터 맞춰야 한다.

기존 검증을 재사용할 때는 같은 입력·source·floating-point 환경에 대한 반환값 동등성만 상속한다. 다른 플랫폼 사이의 bitwise 동등성이나 연속 Vlasov 해의 오차를 뜻하지 않는다. kernel cache와 완료 case registry도 목적이 다르다. 앞의 것은 한 model 내부의 동일 moment 호출을 줄이고, 뒤의 것은 완성된 과학 작업을 다시 실행하지 않도록 한다. 오늘의 직접 효과는 후자와 saved-data consumer에서 발생했다.

## 9. NCP 64CPU/128GiB를 함께 쓰는 실제 admission 식

[shared_runner.py](src/shared_runner.py)는 HE29가 보관한 `c21k_scheduler.resource_snapshot`, `acquire_cpu`, thread 환경과 `bass_resources._cpu_counters`를 재사용한다. CPU55 고정 제외는 제거했고 reserve를 명시적 옵션으로 바꿨다. 최대64는 권한 상한이며, 실제 폭은 affinity/cpuset·cgroup ancestor quota·측정된 CPU 여유·메모리와 pending 수에 의해 결정된다. 다른 세션이 있다는 사실만으로 전체 작업을 HOLD하지 않는다.

현재 구현을 수식으로 쓰면, affinity CPU 수 A, cgroup quota Q, active 자기 worker 수 N, pending 수 P에 대해

\[
C=\min(64,A,\lfloor Q\rfloor),\qquad
r_C=\min(r_{C,req},\max(0,C-1)),
\]

이다. quota 제한이 없으면 해당 항은 A로 둔다. 각 CPU busy fraction을 u_i라 하면 `I=Σ_i(1−u_i)`이고, finite quota ancestor에서 사용량을 샘플링한 headroom의 최솟값을 J로 둔다. memory는

\[
M=\min(128\,\mathrm{GiB},M_{limit}),\quad
r_M=\min(r_{M,req},M/8),\quad
V=\min(M,M_{available})
\]

로 제한한다. 현재 기본 worker당 admission 예산 B=1 GiB에 대해 새 worker 수는

\[
W_{new}=\min\left\{
P,\ (W_{max}-N)_+,\ (C-r_C-N)_+,\
\lfloor I-r_C\rfloor_+,\
\lfloor J-r_C\rfloor_+,\
\left\lfloor\frac{(V-r_M)_+}{B}\right\rfloor
\right\}.
\]

J를 관측하는 finite quota가 없으면 그 항은 C다. 코드는 floor 경계의 부동소수점 잡음을 위한 작은 여유를 둔다. 실제 CPU를 선택할 때는 관측 idle 순으로 시도하고 이미 잠긴 CPU는 건너뛴다. 수식으로 admission이 가능해도 cooperative CPU lease를 얻지 못하면 그 slot은 실행하지 않는다.

현재 `M_available`에는 이미 실행 중인 worker의 resident memory와 다른 작업의 사용량이 반영되어 있다. 여기에서 `N×B`를 다시 빼면 같은 메모리를 두 번 차감한다. 수정된 실행기는 active 수를 concurrency 상한에 한 번 반영하고, RAM slot은 관측 가용량에서 reserve만 뺀다. B=1 GiB는 실제 peak RSS 측정치나 OS의 강제 메모리 제한이 아니라 admission 가정이다. 새 종류의 큰 작업에 적용할 때는 적절한 예산을 제공해야 한다.

무부하 64CPU/128GiB라는 가상 snapshot에서 기본 reserveCPU2/RAM16GiB는 최대62개 새 worker를 허용한다. 이는 경량 capacity 검사의 입력/출력이며 NCP 현재 사용량 관측이 아니다. 예를 들어 8GiB host에서는 RAM reserve를 최대1GiB로 조정한다. 실제 pending이 0이면 다른 조건과 무관하게 W_new=0이다. 완료237을 다시 pending으로 만들면서 CPU 사용률을 높이는 것은 이 구현의 목적이 아니다. [경량 검사 기록](evidence/RUNNER_CHECK.json).

각 child는 CPU 한 개에 pin하고 OMP/OpenBLAS/MKL/BLIS/NumExpr/VecLib/Rayon thread를 1로 제한한다. shared directory `/tmp/cosmosapjw_hpc64_cpu_leases`의 `cpu_N.lock`과 `rei_job_<identity>.lock`은 협력 runner 사이에서 같은 CPU·같은 case의 중복을 막는다. 미참여 프로세스를 강제 예약하거나 종료하는 기능은 없으며, 그 사용량은 관측 headroom에 반영한다. child가 lease FD를 상속하므로 parent의 비정상 종료만으로 같은 실행 중 case의 lock이 즉시 풀리는 문제도 줄인다.

worker 완료 후 자원을 다시 읽고 준비된 다른 case를 채운다. malformed/mismatched receipt나 partial output은 보존하고 자동 덮어쓰기·재시도를 하지 않는다. 시간 예산은 최대3600초이며 timeout 정리는 자신이 생성한 직접 child에 한정한다. 실패 receipt와 원자적 JSON/fsync는 출력 손실이 과학 중복 계산으로 이어지는 위험을 줄인다. 이 실행기는 신규 physical worker의 자손 process까지 관리하는 범용 batch scheduler를 주장하지 않는다.

## 10. 현재 결과 검토에서 재사용할 정확한 지표

다음 표는 저장된 237개 배열을 소비한 [ANALYSIS_SUMMARY.json](results/ANALYSIS_SUMMARY.json)의 값이다. source/input/raw SHA와 prefix/tail의 exact array identity는 모두 통과했다. 수치가 작다는 사실과 검토 범위는 함께 읽어야 한다.

| 검토 항목 | 현재 값 | 주장 가능한 범위 |
|---|---:|---|
| 시작·접합·끝 redshift | `20.0`, `4.0`, `2.000000000000001` | 저장된 평균 scale-factor epoch |
| Frobenius shear 재구성 최대 차이 | `4.163336342344337e−17` | SI shear와 stored norm의 일관성 |
| SI→P_m / SI→P_r 최대 차이 | `0` / `3.2526065174565133e−19` | 분리 stress의 단위·정규화 일관성 |
| 현재 배열의 signed sum / magnitude / cross residual | 각각 `0` | 같은 저장 관측량 사이의 algebraic identity |
| gamma/nu N0 최대 오차 | `0` | 저장 epoch의 number monopole |
| 최소 sampled brightness | `0.5424751213728825` | 저장 epoch의 지정 angular reconstruction samples |
| Hamiltonian construction residual | `2.220446049250313e−16` | 같은 algebra로 재구성한 H의 consistency |
| joint-grid signed shear reversal | `22/175` | `|S|>1e−12`인 저장 표본에서 부호 전환 |

Hamiltonian 항목은 H를 같은 식에서 구성하므로 독립 constraint propagation 인증이 아니다. sampled brightness의 양수성은 시간·각도 연속체 전체의 positivity proof가 아니다. signed shear reversal 수는 threshold와 저장 시간 샘플에 의존하며 추가 root-finding을 수행하지 않았다.

6개 matching nominal/guard의 z2 endpoint 최대 차이는 `|ΔΣ_F|=3.5701298281608576e−13`, `|ΔP_m|=1.0678464744937922e−14`, `|ΔP_r|=1.6561865811073884e−16`, `|Δb|=7.122080702970379e−14`, `|ΔH/H|=3.468336728928989e−13`이다. 같은 6쌍의 전체 저장 history 최대 차이는 각각 `2.25151184114346e−11`, `1.1521239149346607e−13`, `2.4590410003383356e−14`, `3.274023413490923e−12`, `3.772537837676282e−13`이다. endpoint와 전체 history의 수치를 혼동하지 않는다. 이 비교는 이미 존재하는 guard 자료의 재분석이며 새 convergence campaign이 아니다. 전체 grid·연속 parameter 공간의 균일 오차 한계도 아니다.

nominal z2 endpoint에서 `Σ_F` 범위는 `[2.0760631305256127e−20, 0.005311432097083972]`, signed `P_m`은 `[−8.851425947637313e−6,5.8150423727203424e−6]`, signed `P_r`은 `[−2.0812599293428715e−4,1.3252705923966326e−4]`다. 서로 다른 희석과 geometry feedback 때문에 초기 `P_m+P_r=0`이 계속 유지될 필요가 없고, 따라서 부호를 지우는 cache나 `Π_m+Π_r` 합산은 이 pilot의 과학적 관측량을 손상시킨다. 실제 선택 궤적은 [selected_histories.csv](results/selected_histories.csv)에서 그대로 추적한다.

## 11. H/He가 기여할 실제 연결점과 외부 코드의 조건

현재 massive matter는 비바리온 collisionless 성분이며 초기 전체 matter의 fraction0.1, `m/T_ref=30`이다. 나머지 dust와 구별한다. `ne_source=None`이므로 이 pilot은 native H/He 재이온화, photoheating, electron density의 자기일관 feedback을 실행하지 않았다. BASS_HE의 다음 직접 기여는 새 baseline 재적분이 아니라 명시적인 H/He donor를 photon opacity에 연결할 계약이다. [물리 계약](evidence/PHYSICS_REUSE_KO.md), [source/config 검토](evidence/INDEPENDENT_DATA_READBACK.json).

proper number density를 쓰면

\[
n_e=n_Hx_{\rm HII}+n_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII}),\qquad
\Gamma_T=c\sigma_Tn_e.
\]

기존 donor의 `cm−3` 단위에는 `c_cgs σ_T,cm2`를 곱해 s⁻¹로 변환한다. 이 rate는 photon collision operator에만 들어간다. massless neutrino나 비바리온 massive stress를 electron chemistry로 대체하지 않는다. donor는 적어도 epoch 정의·지원 redshift 구간·proper/comoving density·H/He abundance·photoionization/rate source·보간 방식·파일 SHA를 가져야 한다. 고정 donor는 one-way coupling이며 fully coupled thermochemistry를 완료했다는 의미가 아니다.

고정 T와 radiation rates, frozen n_e에서 3종 helium의 rate matrix는 비음수 off-diagonal과 column sum0을 가져 matrix exponential로 nuclei conservation과 positivity를 보존할 수 있다. 하지만 n_e와 T를 동시에 진화시키면 freeze/splitting error가 별도 생기며 full H/He OTS photon coupling도 유지해야 한다. 이 식과 Jacobian의 Wolfram 검산을 재사용하되 이번 HE30에 새 chemistry stepper를 넣지는 않았다. Friedrich et al.의 H/He 비평형·coupled OTS 논문은 이런 coupling을 정하는 원전이다. [Friedrich et al., MNRAS 421, 2232](https://arxiv.org/abs/1201.0602), [symbolic receipt](evidence/TOOL_EVIDENCE.json).

외부 문헌과 코드는 다음 범위로 채택했다.

| 원전·코드 | 재사용하는 내용 | 현재 도입 상태와 조건 |
|---|---|---|
| [Dash–Jaiswal 2018](https://arxiv.org/abs/1711.07130) | Bianchi I의 collisionless momentum·stress 구조 | 현재 canonical 모델의 물리 근거를 대조했다. 논문의 convention과 massive 자체 유도를 구별한다. |
| [Friedrich et al. 2012](https://arxiv.org/abs/1201.0602) | H/He rate coupling, OTS, ion fraction과 thermal accuracy의 구별 | 후속 donor/chemistry 계약에 반영한다. 논문 자체가 anisotropic stress closure를 제공하는 것은 아니다. |
| [Grackle initialize_rates.c](https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/src/clib/initialize_rates.c) | 고정 temperature-grid rate의 초기화와 계수 준비 패턴 | 구조를 참고했으며 기존 locked rates를 교체하거나 외부 함수 source를 복사하지 않았다. |
| [Grackle 공식 설정](https://grackle.readthedocs.io/en/latest/Parameters.html) | six-species H/He와 UVB/rate configuration | UVB 지원 epoch와 가정이 새 donor 범위에 맞는지 먼저 명시한다. z20에 범위 밖 fallback을 암묵 적용하지 않는다. |
| [HYREC-2](https://arxiv.org/abs/2007.14114) | effective rates와 RT correction을 미리 준비하는 설계 | primordial recombination calibration을 z20→2 재이온화 prescription으로 전용하지 않는다. source 복사 없음. |

Grackle pinned commit `6d57fe2c3eb07c34dadb0b0e568cdc12f975146d`의 공식 [LICENSE](https://github.com/grackle-project/grackle/blob/6d57fe2c3eb07c34dadb0b0e568cdc12f975146d/LICENSE)는 Enzo Public License의 NCSA/BSD 조건이다. 향후 source 재배포에는 저작권·조건·disclaimer 보존, binary 배포에는 문서 동봉, 무단 endorsement 금지 조건을 적용해야 한다. 공식 license 원문을 확인했다. 현재는 외부 Grackle source를 복사하지 않았고 준비 패턴을 연구에 사용했다.

현재 REI vendor의 LICENSE는 MIT이며 원 저작권과 permission notice를 유지한다. HYREC-2는 조사 당시 GitHub license metadata가 null이었으므로 오픈 열람 가능성만으로 재배포 허가를 추정하지 않았고 코드도 복사하지 않았다. 수학적 방법과 외부 source bytes의 도입은 별개의 판단이다. [외부 source·license ledger](evidence/SOURCE_LEDGER.json), [REI vendor license SHA](evidence/D3_SOURCE_AUTHORITY.json).

## 12. 다음 변경에 사용할 우선순위

오늘 목표의 실제 기여는 완료237의 재사용, 독립 stress 좌표와 시간 진화의 가시화, provenance가 유지되는 compact 분석물, 공유 자원 실행기의 보완으로 완료된다. 그 다음 수정은 새 물리 질문에 필요한 범위에서 정한다.

| 우선순위 | 구체적인 후속 단위 | 재사용할 근거 | 변경 후 필요한 최소 확인 |
|---|---|---|---|
| 1 | 승인된 H/He `n_e(a)` donor adapter | 현재 frozen opacity interface, H/He 단위·rate source 계약 | 단위·epoch 지원범위·gamma-only coupling·새 source identity |
| 2 | canonical moment 준비 객체와 temporary 축소 | 기존 positive weights, packet energy/number 항등식, `moment_batch` | 바뀐 배열 수명·finite quadrature·reduction 차이만 확인 |
| 3 | 새 pending case에서 exact moment 재사용 | ACCEL01의 binary64 key·binding·bounded LRU | 실제 함수의 입력 의존성과 immutable state 보장 |
| 4 | 새 모델에 맞는 state 축소 | PR198의 even collisionless invariant subspace | gamma/nu 동일성·number/thermal feedback 조건을 다시 확인 |

새 full native H/He 결합이나 collision operator가 들어가면 reduced8의 전제, cache key의 충분성, 원 conserved weights의 의미도 함께 검토한다. 반면 현재 저장 배열에서 색상·범례·case 선택을 바꾸는 작업은 `--plot-saved`로 완료하며 solver 검증을 다시 시작하지 않는다. 이번 R/C 작업은 새로운 계산량을 만드는 대신 기존 유효 증거를 연결하고 필요한 후처리를 완성했다. 과학 결과의 범위는 고정 유한 격자의 scoped preliminary pilot이며, 상세 benchmark와 성능 배수 주장은 남기지 않았다.
