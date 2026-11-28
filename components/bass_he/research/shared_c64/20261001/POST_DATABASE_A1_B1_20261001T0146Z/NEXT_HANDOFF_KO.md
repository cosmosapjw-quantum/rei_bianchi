# 다음 단일 연구 node: A1b

ROLE=BASS_HE_A1B_ASYMPTOTIC_CHANNEL_EMBEDDING_AND_ETF_CHOICE

기존 publication branch `research/shared-c64-crossrepo-20260928`에서 이어간다. Scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`이며 publication identity는 외부 delivery receipt에서 확인한다. 이 패키지는 첫 A1/B1 bounded loop다. 전체 연구 프로그램은 미완료다.

먼저 `A1/FRAME_ETF_DERIVATION_KO.md`, `review/A1_INDEPENDENT_REVIEW.json`, `A1/CLAIM_LEDGER.json`, `B1/SOURCE_RECOVERY_ERRATA.json`, `B1/RESULT.json`, `BASS_HE_RESEARCH_DAG.json`을 읽는다. Input source archive v3의 SHA256은 `0f9dc51cc013aa0b91e7f3ff560bbca5afd1ee1551b67c8bb33278c445b1cd84`다. Minami2008 PDF8/printedp7 AppendixTableA3의 exact5keV/u 자료를 복구했다. v3의 P04 table 미발견 주장은 B1 errata로 정정되며 별도 standalone 원자료 유무와 구별한다.

현재 판정은 `FRAME_CONNECTION_GAP_IDENTIFIED`. 일반 transport와 covariance 유도는 독립 검토됐지만 finite-R physical ETF completion은 아니다. 이미 확인한 항등식과 변하지 않은 R10R/기존 scientific suites를 다시 실행하지 않는다.

이번 한 질문은 다음이다. “H(1s) incoming과 He⁺(1s,n=2) outgoing localized subspaces를 어떤 명시적 finite-R basis/ETF embedding으로 연결하고, 그 안에서 S,h,D와 boundary projectors를 중복 없이 정의할 것인가?”

1. 같은 physical asymptotic channel을 표현하는 후보를 좁혀라: source-defined AOCC orbital ETFs와 MO/subspace continuation, 필요한 경우 quantum Jacobi/HSCC 경로. 단순히 asymptotic plane-wave phase만 정했다고 finite-R MO choice가 유일하다고 주장하지 말라.
2. R10R의 g,b 및 incoming σ를 localized asymptotic subspace에 연결하라. 무한 핵질량 근사의 H1s–He⁺n2 degeneracy, m-doublet와 state-projector tracking을 명시하라. Nuclear reduced-mass corrections를 넣는다면 Hamiltonian 변경으로 기록하라.
3. 최소 한 candidate에 대해 χ, phase, derivative-at-fixed-coordinate convention과 S,h,D를 명시하라. Channel-dependent spatial ETF가 finite span을 바꾸면 단순 gauge로 분류하지 말라.
4. S의 비특이성 조건, omitted-space residual, asymptotic incoming/outgoing projectors를 정하라. Bare Q12 probability에서 coherent phase를 역추정하지 말라.
5. Source-oriented CPC ω와 현재 active θdot의 관계가 검증되지 않으면 별도 unresolved 항목으로 유지하라. 물리 amplitude를 만들기 위해 부호를 benchmark에 맞추지 말라.
6. 필요한 최소 operator/CAS 또는 작은 matrix check만 수행하고 독립 검토를 받아라. Output: 명시적 embedding contract 또는 좁혀진 physical formulation gap. A1을 닫기 전 electronic/collision solver와 A2/C1 이후 계산을 시작하지 않는다.

STOP: `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED` 또는 `FRAME_CONNECTION_GAP_IDENTIFIED` 또는 `SOURCE_AUTHORITY_BLOCKED`. 첫 label도 구현·채널수렴·cross-section 정확도를 자동 인증하지 않는다.

Gate: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

게시/보존은 같은 branch의 새로운 research namespace, non-force, append-only로 한다. 원문 PDF와 PDF page images는 private backup에만 보존한다. 각 major node 종료 시 기존 Drive·Dropbox 폴더에 create-only 백업하며, ACK·content identity·실제 restore를 구분한다.
