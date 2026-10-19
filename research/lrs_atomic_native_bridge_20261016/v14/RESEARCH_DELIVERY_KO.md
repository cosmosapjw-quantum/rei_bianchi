# REI-LRS V14 최신 연구 전달 — 2026-10-19 VigilODE Radau 후속

## 최신 완료 범위

VigilODE의 정확한 source `8a8bd409b1d96c7b7421f496d229e119fd3d284e`에 있는 실제 Radau IIA3와 faer 0.24.4 LU를, 기존 native photon moment·chemistry·thermal 방정식에 opt-in으로 연결했다. 샌드박스 Rust 컴파일과 표적시험 **7개**, 실제 native **19개 고유 설정**이 통과했다. 19개 모두 exit 0이며 RHS 38,840회, native wall 9.146159986초다. 별도 실행기 회귀 4개는 process-only 검사이며 native 사례로 세지 않는다.

최종 실행 source는 **`d87ba9ca25acb8a2a032154fa23057b45acd6207`**다. 339개 게시 파일의 Git blob을 원본 바이트와 대조했다. 이 뒤의 branch HEAD는 source와 백업을 가리키는 전달 기록이다. 새 NCP 실행은 **NOT_RUN**이며 과거 V14의 NCP 84개 이력 완료와 구분한다.

현재 [연구보고서](vigilode_radau_20261019/RESEARCH_DELIVERY_KO.md), [이론 유도](vigilode_radau_20261019/THEORY.md), [source delta](vigilode_radau_20261019/SOURCE_DELTA.json), [root 판정](vigilode_radau_20261019/ROOT_SCIENTIFIC_ADMISSION.json), [실행 인계](vigilode_radau_20261019/CODEX_NCP_EXECUTE_KO.md), [최종 receipt와 DAG](vigilode_radau_20261019/stages/FINAL_DELIVERY.json)를 먼저 읽는다. 원래 `v14/SOURCE_DELTA.json`은 기존 복원 계약으로 유지한다.

고정 기하의 유한 refinement에서 주요 채널의 Radau 비율은 약 4.89–4.97이다. Source-on 전체 차수, 일반 nonlinear native 5차, uniform stiff 정확도·양수성, Case B/full EoR/signed Bianchi는 HOLD다. 원시 사건·gas·binding와 photon N/U 배열로 독립 재구성한 전체 누적 에너지 잔차는 최대 8.1864e-15 eV/H다. 이번 boundary N/U는 0이고 저장된 CMB stage는 모두 음수다.

최종 백업 `REI_LRS_V14_VIGILODE_C10_20261019T141050Z.tar.gz`은 **59621285 bytes**, SHA256 `7d709bcb82476fbfa11b8b68654319173740480686633b1e7d7e8b7f7e02812c`이다. Drive `1iubEGl2Cc7gLgm5l4s4M0U2LexsAqk_l`와 Dropbox `id:BSpOijBcT10AAAAAAD_Q6A` 양쪽 ACK 및 전체 readback hash가 일치했다. Drive 회수본의 1,299개 manifest hash와 manifest 자체까지 총 **1,300개 파일**을 검증했다. 상세 [remote ACK](vigilode_radau_20261019/stages/FINAL_REMOTE_ACK.json)를 참조한다. 이전 SSPRK2 Drive 미확인 기록은 역사적 상태로 보존한다.

---

## 아래는 직전 SSPRK2 및 projection 전달 기록

# REI-LRS V14 최신 연구 전달 — 2026-10-19 SSPRK2 후속

## 최신 완료 범위

닫힌 광자 모멘트의 실제 SSPRK(2,2)와 공통 gas-midpoint를 opt-in으로 구현했다. Sandbox Rust1.94.1의 실제14고유표적시험,52 transport진단행,16고유결합이력과 한 번의 실제 clock결함 수정·같은행렬재실행을 완료했다. SourceGL2의 관측가능한 w/T/photonN/photoheat는 이번 유한구간에서 약2차이며 HeIII endpoint는 수치분해능 때문에 HOLD다. 일반 source-on 전체2차/uniformstiff/CaseB/fullEoR/signedBianchi는 승격하지 않는다.

최신 [연구보고서](time_centered_ssprk2_20261019/RESEARCH_CONTINUATION_KO.md), [source delta](time_centered_ssprk2_20261019/SOURCE_DELTA_SSPRK2.json), [root 판정](time_centered_ssprk2_20261019/ROOT_SCIENTIFIC_ADMISSION.json), [독립 검토](time_centered_ssprk2_20261019/theory/INDEPENDENT_COUPLED_REVIEW.md), [NCP 실행 인계](time_centered_ssprk2_20261019/CODEX_NCP_EXECUTE_KO.md)를 읽는다. 실제 최종HEAD·게시commit·백업objectID·전체readback은 [SSPRK2 최종deliveryreceipt](stages/SSPRK2_FINAL_DELIVERY.json)에 있다.

원본 SOURCE_DELTA.json은 V14 원4파일 복원 identity로 보존했다. 새확장은 위 SOURCE_DELTA_SSPRK2.json을사용한다. 원native default/adaptive/checkpoint/MD14/Verner/Grackle/EOS 및기존physical_birth본문은그대로다. 원래 NCP84이력은 이미완료된근거이며 새16이력과합쳐새사례로세지않는다.

이번 새NCP실행은 NOT_RUN이다. 지정키가샌드박스에없고 원격연결기가월간한도로호출을중단했다. 정상Git파일로된복원기·실행기·14표적시험과코드수정은완료했으므로NCP에는실제compile/test/run과필요시작은호환수정만남는다. 사용자에게파일다운로드나수동SSH/SCP를요구하지않는다.

---

## 아래는 직전 projection 전달 기록

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

