# REI-LRS V14 현재 연구 전달 — 2026-10-19

## 현재 결론

**V14 native 컴파일·표적시험·smoke·84개 full 이력은 2026-10-18 NCP에서 실제 완료됐다.** 이번 재개에서 Drive와 Dropbox의 전체 archive, stdout, 종료코드, source hash 및 원시 CSV를 확인했으며 기존 campaign을 다시 실행하지 않았다. 실행 code anchor는 `f6046418d15e2f44418dfbc04ca67999f389a7df`, 재개 때 HEAD는 `55d267d00e8dd9b04005af5d8551e948251c0777`이다.

실제 GL2 온도 refinement는 Xend=1e-5 / 1e-4에서 p≈1.059 / 0.947였다. 이번 원시 사건·열 채널 분해에서 photoheat와 종별 광흡수 배분이 leading 온도 차이를 운반함을 확인했다. 기존 source-off 제어는 photon population이 0인 gas-only 이력이었다.

새 이론 유도와 실제 native transport 진단은 고정 기체·기하에서 spectrum을 N/U로 매번 재구성하는 map의 O(h²) 국소 결함과 약 1차 반복 적분을 확인했다. 새 고유 행렬은 48 pair +14 frozen-history=62행이며 coupled 우주론 이력이 아니다. 재현 runner를 fresh sibling layout에서 한 번 확인했고 최초 62행/13,312 cell rows와 완전히 같은 CSV bytes를 얻었다. 보존 잔차가 작아도 이 시간 오차는 남는다.

전체 유도, 가정, native source 대응, 결과 및 한계는 [RESEARCH_CONTINUATION_KO.md](projection_diagnostic_20261019/RESEARCH_CONTINUATION_KO.md)에 있다. [독립 검토](projection_diagnostic_20261019/INDEPENDENT_PROJECTION_REVIEW.md)는 PASS_SCOPED다. 원래 coupled T 오차 중 이번 기작의 인과적 기여율은 미분리이며 full source-on 2차는 HOLD다.

## 실제 실행 범위

| 항목 | 상태 |
|---|---|
| 2026-10-18 NCP | Rust1.99.0, offline locked release, 36 distinct targeted tests가 smoke/full에서 각각 PASS |
| Smoke | exit0, 28 histories/336 rows |
| Full | exit0, 84 histories/7056 rows, 7 modes×6 N×2 Xend |
| 2026-10-19 sandbox native 진단 | Rust1.94.1, compile0/run0, 첫 native 실행0.094112117s |
| 새 runner 재현 | fresh restore/build/run/analyzer 모두0; 같은 두 CSV SHA256 일치 |
| 이번 새 NCP 실행 | NOT_EXECUTED — Desktop Commander 실제 probe가 월 사용량 한도 SERVICE_ERROR |
| 기존 Python57/제조76 | 과거 결과 재사용, 이번에 재실행·새 연구 집계하지 않음 |

기존 네 V14 native output, MD14 source, Verner/Grackle/EOS, default/adaptive/checkpoint는 그대로다. 새 native 파일은 추가 진단 example 하나다. 현재 분석기와 재현 runner를 정상 GitHub 파일로 제공한다.

## 이번에 정정한 실제 결함

두 기존 요약 JSON에서 species-event residual의 전체 최댓값이 `0`으로 잘못 집계돼 있었다. 기존 독립 분석의 두 interval 값 중 최대인 `4.84017834763862e-14/H`로 정정하고 이전0과 근거를 보존했다. Native 사건 회계의 변경은 아니다. 새 analyzer의 환경 상태는 CSV로 추정하지 않도록 고쳤다.

`ef94f08df149b57959b868646b397a2bff2b268b`는 full run 종료12:41:16 뒤인12:45:53에 생성된 **실행 증거 게시 commit**이다. 이를 실제 실행 순간의 checkout SHA로 부르지 않는다. 원본 필드는 보존하고 역할을 부연했으며, native byte identity는 code anchor+네 output SHA로 확인한다.

## 판정·다음 작업

원시 P/C/R/D 사건, binding/heat/cooling/escape/signed CMB/work를 구분한다. 모든 양은 total-H 기준이며 e=x+Y(y+2z), Y=.2454/[4(1-.2454)]다. 기존 CSV에 없는 surviving photon energy와 boundary photon number의 전체 독립 회계를 새로 주장하지 않는다.

Full source-on p2, uniform stiff, Case B, full EoR, signed Bianchi는 HOLD다. 다음 연구 대상은 closure R(M)를 유지한 source-free photon–gas update의 시간 중심 stage 설계다. 기존 84이력을 반복하거나 birth quadrature만 추가하는 것으로 이번 projection 결함을 해결했다고 하지 않는다. 이 알고리즘 선택은 NCP의 작은 호환 수정으로 넘기지 않는다.

[실행 인계](CODEX_NCP_EXECUTE_KO.md), [다음 연구 인계](NEXT_CHAT_HANDOFF_KO.md), [이번 DAG](stages/PROJECTION_DIAGNOSTIC_20261019.json)를 따른다. 사용자가 파일을 내려받거나 수동 SSH/SCP를 할 필요는 없다.

## 과거 기록

기존 57 Python 제조 CSV 시험, 8 FAIL 반례와 독립 여섯 회계 수정, 76 제조 수치 문제는 [실행 준비 시점 기록](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/2676c31df1bf18ec0c7d60108846f1e9c8ca853c/research/lrs_atomic_native_bridge_20261016/v14/RESEARCH_DELIVERY_KO.md)에 보존돼 있다. 그 시점의 native NOT_RUN과 독립 agent NOT_RUN은 현재 완료 상태가 아니다. 기존 실행 원본과 초기 실패는 [NCP execution directory](executions/REI_LRS_V14_20261018T124115Z/)에 그대로 남아 있다.
