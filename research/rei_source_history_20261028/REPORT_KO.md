# Source history와 transient QSS 검증

2026-10-28 UTC. 상태: PASS_SCOPED_QSS_HISTORY; solver READY_NOT_RUN; future-only wrapper/postprocessor STATICALLY_REVIEWED_NOT_RUN.

PR245의 illustrative external-source operator에 시간 이력을 명시하고 초기 fast/thermal n/T stock을0으로 두었을 때의 QSS 추적 오차를 평가하는 단위다. H1은 같은 저장 H로 elapsed proper time을 복원하고 constant per-Href injection·constant proper photon/CR flux를 구분한다. H2는 neutron/tritium 가족별 l1 수축을 이용하여 초기 불일치와 움직이는 고정점의 forcing-variation 항을 별도로 제한한다. QSS algebraic residual과 실제 trajectory lag는 서로 다른 양이다.

H1/H2는 실제 tests·diagnostic과 독립 검토에 따라 COMPLETE_SCOPED다. H3은 17 visible heavy states와 fast Bn/BT·Un/UT를 결합하는 prescribed-bath solver 준비다. Coupled IVP 세 case는 실행하지 않았다. 현재 원래 working33/88, central28/88, fast4/7, delta0을 유지한다. 이 모델은 astrophysical calibration, self-consistent photon/temperature feedback 또는 기존 전체 physical F4 완료를 뜻하지 않는다.

Source와 직접 유도는 `sources/SOURCE_HISTORY_SYNTHESIS.md`, 동결 조건은 `theory/FROZEN_CONTRACT.md`에 있다. 새 primary source는 Davydov et al., arXiv:2305.15595v3의 equilibrium tracking framework다. 실제 네트워크 특수형은 직접 유도했으며 optimization feedforward를 반응계에 넣지 않는다. 이전 여섯 논문은 PR245의 curated synthesis를 재사용한다. 게시·백업에는 논문 전문을 넣지 않는다.

의존성은 `delivery/DEPENDENCY_INVENTORY.json`에 기록한다. 기존 nominal NPZ/배경 archive는 원래 archive와 immutable hash를 참조하며 중복 업로드하지 않는다. 같은 saved H/nHref 및 photon/T/electron bath와 실제 `angular_model.py`/atomic provider를 사용하는 source 연결이다. 복원된 transitive source8개는 outputs/RESTORED_DEPENDENCIES.json의 실제 bytes/hash를 inventory에 기록했다. 다른 시나리오를 쓰는 `AtomicNetwork21.rhs`는 선택하지 않았다.

예산은 이전 charged planning19.204540885/presentation56.217331494와 승인 누적 ceiling30/65를 유지한다. 이번 fresh allocation은 tests4.5/diagnostic2.3/plot3.5CPU s reservation이다. 실제 debit·tail reserve·원래 정책 cap10/30 복귀는 아래 closeout과 BUDGET_CLOSEOUT.json에 기록한다. Main595.225063/600 NO_MORE_IVPs는 그대로이며 미측정 overhead는 UNKNOWN_NOT_ZERO다. PR244의 proposal20/60 및 과거 ledger는 새로운 실제 소비로 더하지 않는다.

## 미실행 pilot의 구체적 제안

Root가 최종 확인한 미실행 제안은 정확히 세 case다: OFF_base, ON_base, ON_refined. 각 case child≤30CPU s/wall≤120s, worker1,3GiB, 자동재시도0. Child 합≤90CPU s와 observer/tail≤10CPU s를 합한 새 main reservation≤100CPU s로, cumulative maximum695.225063이다. 이는 성능 측정이나 활성 실행 허가가 아니다. 같은201 saved epochs와 initial-relaxation dense samples를 사용하고 OFF/ON source control 및 ON base/refined 수렴을 비교한다.

정확한 실행 제안은 `execution/IVP_PROPOSAL.md`의 ordered `bounded_case_runner.py` 세 명령과 bounded postprocessor다. Owner override receipt는 실제 예외 허가 후에만 root가 작성한다. Acceptance는 동결 계약의 positivity, isotope-scaled base/refined≤1e-5, augmented baryon/charge ledger≤1e-8 및 event balance를 그대로 따른다. 허가 전 이 명령은 실행하지 않는다.

추가 허가가 필요한 이유는 예산 ceiling과 실행 종류의 제한이 다르기 때문이다. PR245 정확 HEAD의 historical `research/rei_expanded_event_consumer/lumina_resume_20261026/BUDGET_POLICY.json`에는 `"main_status": "NO_MORE_IVPs"`가 있다. AGENTS.md는 임시 증액 정책에 대해 “This does not change scientific claim gates, reserved producer ownership, the existing NO_MORE_IVPs instruction, or the heavy-execution location policy.”라고 명시한다. 새 총 reservation100은 원래600 대비50% 미만이지만 NO_MORE_IVPs 예외는 별도로 필요하다. 최초 지시의 발행자·사용자 원문을 확인했다는 주장은 하지 않는다.

최초 tests 할당은 게시된 amendment01에서 child4CPU s/reserve4.5로 변경했다. 진단2.3과 plot3.5 reservation은 유지한다. Provider 의존성8개는 coder가 원래 archive에서 복원했고 `outputs/RESTORED_DEPENDENCIES.json`의 실제 hash 기록을 inventory에 반영했다. Source-history 결과와 tests receipt는 독립 검토에서 PASS_SCOPED로 판정됐다. Pilot의 제안 main temporary cap은700이며 새 reservation100과 cumulative maximum695.225063을 구별한다. 세부 grid·명령은 `execution/IVP_PROPOSAL.md`를 따른다.

## 실제 결과와 예산 closeout

Targeted tests7/7 PASS, diagnostic/plot 각1회 완료, IVP0회다. Neutron/tritium 두 가족 모두201개 saved epochs 중200개가1% criterion을 만족한다. 최초 시점은 두 가족 모두 relative bound1이며 index0만 미인증이다. 이후 전체 saved epochs 인증은 index1, elapsed80325473529033.45s부터다. 이것은 analytic envelope의 FP64 saved-epoch 판정이고 whole-interval certificate나 실제 evolved trajectory 측정이 아니다. Interval certification은NOT_RUN이다. 같은 H의 GL8/16 총 elapsed difference1.6422314193213868e-16, 최대 interval difference4.727601132088829e-15, elapsed endpoint9.742841241346858e16s를 얻었다. Old-bath H/nHref 상대 mismatch는 각각0이다. 독립 검토는 PASS_SCOPED_QSS_HISTORY와 solver READY_NOT_RUN을 기록했고 future-only wrapper/postprocessor도 STATICALLY_REVIEWED_NOT_RUN으로 최종 판정했다.

새 observed child+partial wrapper는 planning1.114921/presentation1.195392CPU s다. 기존 charge와 새 tail reserve 각0.5를 보존한 closeout은 planning20.819461885/presentation57.912723494CPU s이며 원래 policy caps10/30으로 복귀했다. Main595.225063/600 NO_MORE_IVPs와 unknown overhead UNKNOWN_NOT_ZERO를 유지한다. 미래 postprocess는 presentation child≤3/reservation3.5를 기존65 ceiling 내 별도 기록하는 제안이며 아직 실행하지 않았다. 원래33/88·중앙28/88·fast4/7·delta0은 변하지 않는다.

최종 제안의 실행 위치는 현재 cloud bounded pilot 환경이다. 요청할 예외는 이 호스트에서 위 세 case에 한정한 NO_MORE_IVPs 및 기존 heavy-execution-location 정책의 좁은 예외이며, 아직 허가되지 않았다. 기존 위치 정책 전체를 변경하거나 다른 실행을 승인한 것으로 해석하지 않는다.
