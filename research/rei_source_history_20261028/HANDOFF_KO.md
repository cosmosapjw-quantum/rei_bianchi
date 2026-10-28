# 다음 대화 인계: source-history/QSS

상태: source-history/QSS는 PASS_SCOPED_QSS_HISTORY. Tests·diagnostic·plot 각각1회 완료. Coupled IVP는0회; future-only runner/postprocessor STATICALLY_REVIEWED_NOT_RUN.

기준 PR245 HEAD `cc17c2481f3f1057062efe0cbfb505114a0e8cfc`. 새 branch `research/rei-source-history-20261028`; 실행 전 checkpoint HEAD `f1972409489de724f8ab67b47ed77addb9a651da`, 두 파일 exact UTF8 readback 완료. 최종 publication/dual backup의 실제 HEAD·PR·provider ACK는 별도 DELIVERY_RECEIPT.json을 따른다.

H1: constant external histories + saved H/nHref 동일 clock 연결. H2: zero initial five stocks의 가족별 initial/variation QSS error bound. H3: full17 prescribed-bath solver READY_NOT_RUN; future packet STATICALLY_REVIEWED_NOT_RUN. H4: OFF_base/ON_base/ON_refined coupled IVPs NOT_RUN, NO_MORE_IVPs 예외 허가 대기. H1/H2는 COMPLETE_SCOPED이며 H3 준비는 READY_NOT_RUN, future-only packet은 STATICALLY_REVIEWED_NOT_RUN이다. 원래33/88, 중앙28/88, fast4/7, delta0 유지.

실제 코드/입력/복원 source 목록은 `delivery/DEPENDENCY_INVENTORY.json`, 과학 계약은 `theory/FROZEN_CONTRACT.md`, curated primary literature는 `sources/SOURCE_HISTORY_SYNTHESIS.md`다. 원래 NPZ archive를 중복 업로드하거나 donor IVP를 재실행하지 않는다. 논문 전문은 게시·백업에서 제외한다.

계속 유지할 budget: inherited planning19.204540885/presentation56.217331494; approved continuing ceilings30/65; fresh tests4.5/diagnostic2.3/plot3.5 reservations. 실제 debit과 원래 policy10/30 복귀는 아래 closeout에 반영했다. 누적 debit/reserve와 UNKNOWN_NOT_ZERO를 보존한다. Main595.225063/600 NO_MORE_IVPs. PR244는 별도 owner의 PROPOSED_NOT_APPROVED_NOT_RUN이며 그 stale ledger를 최신 실제 debit으로 합산하지 않는다.

다음 IVP 허가 요청은 generic budget 요청이 아니다. 구체적 세 case, 각 child≤30CPU s/wall120s, 총 new main reservation≤100CPU s, main cumulative maximum695.225063, worker1/3GiB/자동재시도0 제안을 root가 최종 확인했다. `REPORT_KO.md`의 기존 NO_MORE_IVPs/AGENTS 정확 인용을 유지한다. 예산 승인만으로 기존 실행 제한이 사라졌다고 주장하지 않는다.

최초 tests 할당은 게시된 amendment01에서 child4CPU s/reserve4.5로 변경했다. 진단2.3과 plot3.5 reservation은 유지한다. Provider 의존성8개는 coder가 원래 archive에서 복원했고 `outputs/RESTORED_DEPENDENCIES.json`의 실제 hash 기록을 inventory에 반영했다. Source-history 결과와 tests receipt는 독립 검토에서 PASS_SCOPED로 판정됐다. Pilot의 제안 main temporary cap은700이며 새 reservation100과 cumulative maximum695.225063을 구별한다. 세부 grid·명령은 `execution/IVP_PROPOSAL.md`를 따른다.

## 실제 결과와 예산 closeout

Targeted tests7/7 PASS, diagnostic/plot 각1회 완료, IVP0회다. Neutron/tritium 두 가족 모두201개 saved epochs 중200개가1% criterion을 만족한다. 최초 시점은 두 가족 모두 relative bound1이며 index0만 미인증이다. 이후 전체 saved epochs 인증은 index1, elapsed80325473529033.45s부터다. 이것은 analytic envelope의 FP64 saved-epoch 판정이고 whole-interval certificate나 실제 evolved trajectory 측정이 아니다. Interval certification은NOT_RUN이다. 같은 H의 GL8/16 총 elapsed difference1.6422314193213868e-16, 최대 interval difference4.727601132088829e-15, elapsed endpoint9.742841241346858e16s를 얻었다. Old-bath H/nHref 상대 mismatch는 각각0이다. 독립 검토는 PASS_SCOPED_QSS_HISTORY와 solver READY_NOT_RUN을 기록했고 future-only wrapper/postprocessor도 STATICALLY_REVIEWED_NOT_RUN으로 최종 판정했다.

새 observed child+partial wrapper는 planning1.114921/presentation1.195392CPU s다. 기존 charge와 새 tail reserve 각0.5를 보존한 closeout은 planning20.819461885/presentation57.912723494CPU s이며 원래 policy caps10/30으로 복귀했다. Main595.225063/600 NO_MORE_IVPs와 unknown overhead UNKNOWN_NOT_ZERO를 유지한다. 미래 postprocess는 presentation child≤3/reservation3.5를 기존65 ceiling 내 별도 기록하는 제안이며 아직 실행하지 않았다. 원래33/88·중앙28/88·fast4/7·delta0은 변하지 않는다.

최종 제안의 실행 위치는 현재 cloud bounded pilot 환경이다. 요청할 예외는 이 호스트에서 위 세 case에 한정한 NO_MORE_IVPs 및 기존 heavy-execution-location 정책의 좁은 예외이며, 아직 허가되지 않았다. 기존 위치 정책 전체를 변경하거나 다른 실행을 승인한 것으로 해석하지 않는다.
