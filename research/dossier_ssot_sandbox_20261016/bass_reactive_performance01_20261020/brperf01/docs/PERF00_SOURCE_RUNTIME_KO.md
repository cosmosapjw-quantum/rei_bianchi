# PERF00: 소스와 실행 환경 기준선

2026-10-20 사용자의 성능 최적화 및 추가 원자 데이터 이식 지시에 따른 별도 연구 단위다. BR06 과학 판정은 기존 identity가 유지되는 범위에서 재사용한다. 이 단계는 성능 향상이나 새 반응 이력의 검증을 주장하지 않는다.

## 확인한 소스

- REI Draft PR #208 HEAD: `54948439be7039c9b2b1f9580bee69bebeb80129`. 기존 branch와 production을 변경하지 않는다.
- BR06 과학 commit: `0c71466c0a9b4fb357f9b168dbbe4cae74e1f8dd`.
- BR06 전체 복원 ZIP SHA-256: `3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135`.
- VigilODE 현재 HEAD: `8d0c79184e09efb5bdadc24a6315c60a71a44264`.
- 기존 BR06 VigilODE kernel pin: `a21d573980f66fe02891bd216153443b5352f921`. 최신 GMRES 연구와의 무검증 병합은 하지 않는다.

## 기존 구현을 기준선으로 인정

기존 PR150 owner 계보의 `rate_table.rs`는 이미 15개 T-only 계수, 기본 65,537개 logT 노드, SoA 배치, 최대 4개 std worker 및 exact-temperature prepared bundle을 제공한다. 이번 연구는 이를 새 기능으로 세지 않는다. 실제 비용 후보는 중복 좌표 계산, 초기화 중 반복 source 평가, 배치마다의 할당과 worker 생성, 크기가 큰 loglinear 계수표이다.

BR06 광자 경로는 이미 정확한 reflection orbit 및 geometry cache를 쓴다. 아직 각 경로의 Gauss rule 구성, inverse-optical-depth 평가마다의 임시 Vec, 동결 기체의 EOS·밀도·threshold 확인과 동일 birth-ray 구성을 반복한다. 새 경로는 양수 source 적분의 구적 차수·산술순서·Killing 경로·출생 metadata를 유지하면서 이 비용을 분리한다.

## 실행 환경

제공된 Rust 1.94.1 archive는 192,287,020 bytes이며 SHA-256 `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`가 공식 HTTPS checksum과 일치한다. detached OpenPGP 검증은 수행하지 않았다. Rust/Cargo/rustfmt/Clippy 및 offline smoke는 실제 실행했다.

CPU cgroup quota는 8 cores, process affinity 9 slots, 메모리 limit 8 GiB다. 99개 Cargo registry package의 4,944개 payload SHA와 원 BR06 lockfile checksum을 확인했다. 별도 prefix와 Cargo home을 사용한다. 과학 benchmark는 다른 컴파일/benchmark와 겹치지 않게 실행한다.

## 다음 작업과 판정 조건

1. 양수 rate 보간, 분기 부근 direct fallback, immutable table 저장/복원, T를 공유하는 원 H/He/D RHS의 재사용을 실제 비교한다. coefficient 오차와 native ledger/반응 차이를 따로 측정한다.
2. 동일 BR06 광자 입력에 대해 serial 원본, reuse serial, ordered persistent workers를 비교한다. correctness fingerprint와 실제 작업수를 timing과 함께 보존한다.
3. 원저자 데이터와 domain이 확보된 추가 이온 PI/CI 및 가능한 RR를 additive catalog로 이식한다. 미구현 DR/CX/CE·열/전자/원소 반응망을 완료로 표시하지 않는다.
4. 단계별 GitHub Draft·Drive·Dropbox 상태는 ACK, provider hash, raw restore 여부를 구분한다. 과학 노드 BR07과 longspan admission 상태는 성능 실험만으로 승격하지 않는다.
