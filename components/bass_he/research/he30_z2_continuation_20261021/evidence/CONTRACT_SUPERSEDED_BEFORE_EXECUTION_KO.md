# HE30: 저장된 독립 응력 pilot의 z=4→2 연속 계산

## 목표와 완료 조건

사용자의 2026-10-21 요청: BASS_HE가 rei_bianchi non-tilted LRS Bianchi I의 독립 matter/radiation stress parameter sweep와 z=20→2 시간 진화에 기여한다. 최신 관련 저장소·백업을 조사한 뒤 실제 실행 가능한 코드를 게시하고, 상세 성능 벤치마크는 수행하지 않는다.

이번 단위는 동일한 PR147 canonical collisionless model의 **C21M 27점**을 재사용하여 z=4→2 구간만 새로 계산한다. signed Frobenius 초기 grid는 S0={−0.012,0,+0.012}, Pm0=Pr0={−0.0002,0,+0.0002}. 중앙 원점은 원래의 부동소수점 잔차를 보존한다. 기존 z=20→4 전체40상태/101점은 변경하거나 재실행하지 않는다. 완료 조건은 원자료 identity 검사,27개 연속 적분, 전체 z=20→2 component histories/plots, 새 구간의 scoped science/implementation 검증, 게시·백업·실행 인계다.

## 권위와 재개점

- BASS_HE base: 048a73de4246f609b1bc14854ea5c48757cb82fd, PR82.
- C21M source/result: bass_cr b78a943e5d7ae341bbfe84f742a06a4ac36d0e43, PR91. 26개 original result와 C21L 중앙1개를 실제 raw 바이트로 import한다.
- 공통 원래 과학 코드: rei_bianchi 3b85dedce84d37b3e165da00685a8a984950aafe (PR147).
- Reduced8 구현: rei_bianchi 8bd35af5f11c7ea5945b656be1c013d1c1933498의 research/rei_bianchi_sigma_pi_pilot_20261021/pilot.py. 원본은 그대로 보존하고 continuation adapter에서 재사용한다.
- HE29의 raw27은 보존. 게시 중 유실된 original1+split12의 과거 완료 문구는 복원 증거가 아니며 이번 계산의 입력으로 쓰지 않는다. 조사한 백업에서 해당13개는 찾지 못했다.

## 물리·단위 계약

metric signature (−,+,+,+), a_perp=a exp(−b), a_parallel=a exp(2b), sigma_ab=diag(−s,−s,2s). 각 성분 pi_X,ab=diag(−p_X,−p_X,2p_X), p_X=(P_parallel−P_perp)/3 [J m^-3]. H와 s는 proper time [s^-1].

Sigma_F=sqrt(6)|s|/H; signed S=sqrt(6)s/H; signed P_X=(8 pi G/c^2)sqrt(6)p_X/H^2; Pi_X=|P_X|. kappa_E=8 pi G/c^4를 쓰면 Pi_X=kappa_E c^2 |pi_X|/H^2. Pi_total=|P_m+P_r|. 부모 half-contraction norm과의 변환은 sqrt(2)이며 magnitude만으로 상대부호를 제거하지 않는다.

matter stress는 fm=0.1의 massive collisionless nonbaryonic component. 나머지 pressureless matter는 isotropic dust. radiation은 동일 초기 angular shape의 gamma+massless nu. baryonic stress, UV/He chemistry, polarized collisions는 이 pilot의 계산 대상에 포함되지 않는다. 이 성분 구분을 그림·보고서에서 유지한다.

aref=1/21, Href, mass/Tref=30, immutable canonical packets와 source normalization을 보존한다. aend만1/3으로 확장한다. eta=ln(a/aref)를 z4에서0으로 재설정하지 않는다. elapsed proper time, b, s/Href, radiation moments는 저장된 끝 상태에서 이어간다.

## 수치와 자원

ellmax8, radial24×angular12×Gauss3, binary64, DOP853 rtol3e-11/atol3e-13을 유지한다. 기존 구간101점+새 구간65점(공통 경계1점 제거)=165점/case. photon=nu energy equality, odd parity, zero thermal feedback 조건을 입력에서 검사한 뒤 upstream Reduced8 RHS를 재사용한다. full40은 새 구간의 소수 paired correctness comparison에만 쓴다. 성능배율·연속분포 수렴 주장은 만들지 않는다.

NCP 상한64CPU/128GiB와 실제 affinity/cgroup quota/MemAvailable 중 작은 범위를 사용한다. case당 single native thread, 공유 CPU lease와 case identity lock, 완료 결과 재사용, 원자적 저장을 적용한다. 다른 세션 존재만으로 전체 작업을 중단하지 않는다. 자원 부족이면 그 시점에 신규 배분만 보류하고 기존 작업을 방해하지 않는다.

## 현재 정책 교정

AGENTS.md의 same-workload detailed benchmarking 선행 기본값은 이번 사용자 지시의 benchmark 제외를 적용한다. 정확도·closure 검증은 수행한다. 기존 runner의 고정 CPU55 제외는 실제 CPU topology와 configurable reserve로 대체하며 이전 증거를 보존한다. 단계별 작은 checkpoint와 Git/Drive/Dropbox acknowledgement를 기록한다. 새로운 strong no-go 주장은 없다.
