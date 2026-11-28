# HE30 — 완료된 D3의 독립 성분 pilot 소비·그림·공유 자원 실행

## 현재 목표와 변경 근거

사용자의 2026-10-21 요청은 BASS_HE가 rei_bianchi non-tilted LRS Bianchi I의 물질/복사 응력 sweep와 z=20→2 preliminary 그림을 당일 완성하도록 기여하는 것이다. 관련 최신 branch/repo/백업을 조사한 결과, 새 IVP를 시작하기 전에 **D3 완료 237건**을 발견했다. 초기 C21M27 tail 계획은 `evidence/CONTRACT_SUPERSEDED_BEFORE_EXECUTION_KO.md`에 보존하며 **실행 전 대체**되었다. HE29 소유 원자료는 변경하지 않는다.

이번 실행 범위는 원본 해시·정규화·완료 상태의 확인, 독립 결과 심사, 벡터 배열 후처리와 parameter sweep/time evolution 그림, 공유 자원 runner 개선, 게시·백업·인계다. 새 ODE/IVP와 상세 성능 벤치마크는 0이며 과거 D3 실행 횟수와 구분한다.

## 입력 권위와 정확한 표본 집합

- BASS_HE 시작점: PR82 `048a73de4246f609b1bc14854ea5c48757cb82fd`.
- 원본 D3 archive: `REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`, 31,904,176 bytes.
- archive SHA256: `7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498`.
- 원래 kernel: rei_bianchi PR147 `3b85dedce84d37b3e165da00685a8a984950aafe`. Wrapper의 실제 실행 바이트는 `D3_SOURCE_AUTHORITY.json`의 SHA로 고정한다. D0 게시 commit은 D3 실행 commit이 아니다.
- joint grid: Σ_i={0,0.0003,0.001,0.003,0.01,0.03,0.1}; P_m,i={−0.0003,−0.0001,0,0.0001,0.0003}; P_r,i={−0.001,−0.0003,0,0.0003,0.001}. 7×5×5=175점.
- 기존 radiation baseline 91점과 중복35점을 제거하면 고유 nominal231점. refinement guard6점을 합하면237점이다.
- 초기 shear orientation은 s_i≥0. 성분 응력은 양·음의 방향을 독립적으로 변화시킨다.
- 각 사례의 z20→4 121점과 z4→2 33점을 경계에서 정확히 붙여153점. 기존40/56상태 전체 상태가 이어졌으며, D3를 reduced8 계산으로 표시하지 않는다.
- serialization 복구100건의 nfev/solver message/worker timing/RSS는 null을 유지한다. raw와 완료 끝점은 존재하며 복구 과정의 새 적분은 없었다.

## 물리·단위 계약

signature(−,+,+,+), a_perp=a exp(−b), a_parallel=a exp(2b), sigma_ab=diag(−s,−s,2s), pi_X,ab=diag(−p_X,−p_X,2p_X), p_X=(P_parallel−P_perp)/3 [J/m³]. H,s는 proper time에 대한 [s⁻¹].

Σ_F=√6|s|/H, signed S=√6s/H, signed P_X=(8πG/c²)√6p_X/H², Π_X=|P_X|. 에너지 단위 stress에 κ_E=8πG/c⁴를 쓸 때는 κ_E c²|pi_X|/H²이다. half-contraction norm과의 √2 변환을 유지한다. Π_total=|P_m+P_r|이며 Π_m+Π_r와 일반적으로 다르다.

물질 stress는 f_m=0.1 massive collisionless nonbaryonic 성분; 나머지 matter는 isotropic dust. 복사는 gamma+massless nu이며 동일 초기 angular shape를 쓴다. `ne_source=None`, native H/He chemistry·UV·baryonic stress·polarized collisions는 계산 범위에 없다. 평균 redshift는 z̄=1/a−1이며 directional observed redshift가 아니다. elapsed_proper_s는 z20부터 누적한 시간이며 cosmic age가 아니다.

## 수치·후처리·admission

원본 nominal은 ellmax8, radial24×angular12×Gauss3, binary64, DOP853 rtol3e−11/atol3e−13; guard는 ellmax12,48×24×Gauss3. aref=1/21, mass/Tref=30, source background와 canonical packet weights를 보존한다. 여섯 saved guard 비교만 재사용하며 전체 연속분포의 uniform error bound는 주장하지 않는다. Hamiltonian residual은 construction consistency이고 brightness는64개 angular sample에서의 값이다.

`analyze_saved.py`는 모델/solver를 import하지 않는다. source/raw/tail/prefix hash와 exact saved-state join을 확인하고, (case,epoch) 배열로 성분·합·norm을 계산한다. 출력 NPZ는 관측량 후처리용으로 full-state restart가 아니다. 원본 raw_y는 D3 archive가 권위다. 원본 CHECK의 PENDING은 수정하지 않고 별도 독립 심사 receipt를 붙인다.

## HPC 공유 정책

NCP 상한64CPU/128GiB, 실제 affinity/cgroup quota/MemAvailable와 사용량의 교집합에서 worker를 배분한다. 기본 reserve2CPU/16GiB, 작은 host에서는 축소한다. CPU55 고정 제외를 제거하고 one native thread, 전역 CPU lease·content identity lock, 완료 재사용, 원자적 저장과 실패 증거 보존을 사용한다. 다른 세션이 있다는 이유로 전체 작업을 중지하지 않는다. 이 catalog는 이미 완료돼 과학 pending=0이고 HPC를 재점유할 이유가 없다.

사용자가 상세 벤치마크를 제외했으므로 AGENTS의 일반 same-workload benchmark 선행 규칙은 이번 단위에서 적용하지 않는다. 성능 배율은 보고하지 않는다. 실제 자원 배분·회복·완료 재사용에 필요한 좁은 correctness 검사만 시행한다.

## 완료 조건

237개 원자료와 파생 catalog 일치, joint175와 baseline91/overlap35 정합, 네 그림의 시각 검토, 독립 scoped preliminary admission, runner pending0/worker_starts0, Git 게시 및 Drive/Dropbox 백업 ACK, 20단계 ledger/DAG와 두 handoff가 모두 기록되면 이 단위를 완료한다.
