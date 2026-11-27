# BASS_HE 연구 루프 결과 — 2026-10-29

중단된 NONTHERMAL source를 복원하고 이론R1–R10 다음 코딩C1–C10을 수행했다. 새 조건부 과학 계산 두 노드는2/2다. 기존 HE scientific DAG14/18, 중앙28/88은 유지한다. source-only 결과이며 physical_activation=false, L4=false, production=HOLD다.

## 실제 새 결과

1. 정규화된 CM 측도 W의 약한 kinetic gain을 구성했다. 사건당2D, 총 에너지A+ε, 운동량εn/c를 보존한다. 실제 R_event는 null이다.
2. 선택한 even sextic law에서 x=(K-K0)/B의 bin별0·1·2차 모멘트를 정확 유리수로 계산했다. 비대칭4-bin partition에서도 전체 입자수2, reduced first moment0, pair kinetic306.1535218MeV/event를 보존한다. 같은 bin의 midpoint 대입 mutant는+1.05100768828307MeV/event 오차를 만들었다.
3. full selected law의 유한질량 stress trace에 기하급수 remainder 구간을 유도·구현하고 기존 m2-only Jensen/secant 경계와 교집합을 반환했다. 직접 두 딸입자 stress 적분 reference는588.1137615248901501446221509785273MeV/event다. N4 exact rational interval 폭은1.53869199865752e-16MeV/event. 기존 m2-only 폭6.64765685910e-4보다 좁은 것은 전체 선택 law의 추가 정보를 사용했기 때문이다. 실제 실험 law의 오차를 이 폭으로 해석하지 않는다.

## 최신 조사와 원전

BASS_HE·bass·bass_cr·rec_bianchi·WU088_HH·rei_bianchi의1,274 branches·944 open PRs 목록30페이지를 terminal까지 확인했다. 모든 branch history 본문을 읽었다는 주장은 하지 않는다. 중앙 pin4824eec8526185b6b866a5e7e0dabdc624b5543c의 DAG는88nodes이며 현행 scope-aware 집계28/88이다. 과거 FROZEN_STATUS의87과 구분했다.

원 source ZIP manifest15개 size/hash와 frozen15행 SHA256 1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264를 확인했다. 기존 suite/IVP/원15행 science를 재실행하지 않았다. backed source와 remote9044ef5 Stage01-only 게시 차이를 복구했다.

IAEA EXFOR M0475002는 실제330MeV CM46°,61°,73°,87° DA를 제공한다. WU source pin은 IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871이며 source-reference closure를 재사용했다. 네 점에서 full law, event/particle normalization 또는 photon history가 자동 결정되지는 않는다. Rice PRC61,064612(2000), DOI10.1103/PhysRevC.61.064612는150–250MeV 범위다. Arends et al. DOI10.1016/0370-2693(76)90671-7와의 source provenance를 유지한다. 확인 범위는 evidence의 HE/DEPENDENCY/BACKUP_SURVEY에 기록했다.

## 검증과 수정

- 새/영향받는13 test methods가 실제 exit0,13/13 PASS. 원28PASS는 historical reused evidence다.
- 별도 reviewer가 R6 독립 유도와 C9 최종 source4개를 검토했다. 원 exact API의 float/bool 방향 우회 및 float subclass 허용을 공통 strict helper/compatibility delegation으로 수정했다. source hashes가 테스트와 독립 검토에서 일치한다.
- N0 raw trace upper가 Jensen upper보다 넓다는 독립 finding을 보존하고 final intersection을 구현했다. exact positivity·partition·raw/nested bounds·mutation을 검사했다.
- Wolfram normalization/m2/remainder를 검산했다. 최초 radical mass-shell 표현의 미단순화/경고를 보존하고, γ²(1-β²)=1과 on-shell 조건으로 재표현한 검산은 {0,0,0}이었다.
- mpmath의 current-turn PACKAGE_MISSING을 보존한 뒤 stdlib Decimal16/32node,50/80digit Gauss-Legendre 직접 적분을 실행했다. 두 결과 차4.30061236092e-45; N0–6 구간과 일치. 이 적분 안정성 수치는 엄밀한 quadrature interval과 구별한다. trace truncation bound 자체는 해석적으로 증명된 유리수 경계다.
- 새 테스트/실패/reference 누적 CPU=0.112284/8s, wall=0.115408/30s. 새 plot CPU1.160435/10s, wall1.169084306/30s. 원 main595.225063/600s, reserve0, NO_MORE_IVPs를 보존했다.
- conditional_gain_trace.png를 직접 열어 비음성, midpoint mutation, trace 폭의 단조 감소와 라벨을 확인했다. 물리/수학 감사 다음 식–코드 감사를 순서대로 수행한 기록은 evidence/PLOT_AND_DUAL_AUDIT.md다.

## 게시·백업과 남은 의무

새 branch research/he-nonthermal-source-closure-20261029에 단계별 GitHub API tree/commit/expected-parent non-force ref ACK를 기록했다. CLI push는 인증입력 부재로 실패했으며 해당 실패를 보존했다. 로컬 commit과 API remote commit identity를 구별한다. 단계마다 create-only source ZIP을 기존 Drive/Dropbox parent에 보존했고 provider ACK/size/hash는 별도 delivery receipts로 확인한다. 최초 R6 missing-reference checkpoint는 실제 review 파일을 포함한 보정 checkpoint로 교정했다. Dropbox FETCH_FAILED는 실패/같은 파일 retry ACK를 구분한다.

남은 물리 의무는 (i) M0475002/3의 동일 D particle/event·full/half-sphere·beam/uncertainty 정규화, (ii) 실제 photon distribution/history와 target state/frame, (iii) named physical fast-D pool 및 stopping/deposition/Cv 결속이다. 다음 최소 노드는 (i)의 원 논문/공급자 convention 결속이다. 관련 실제 입력이 올 때에만 physical rate 및 pool source를 연결한다. H–Li registry requests와 조건부 REI/CR/WU 결과는 실제 He330MeV production admission으로 승격하지 않는다.
