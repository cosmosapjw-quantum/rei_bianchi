# 현재 상태 — NCP 반환 완료, 2026-10-20T110800Z

상태 갱신: 2026-10-20T17:20:33Z. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**, VigilODE pin **8a8bd409b1d96c7b7421f496d229e119fd3d284e**의 실제 NCP 결과를 회수했다. metadata intake HEAD는 **90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec**이며 실행 source와 구분한다.

Locked release build exit 0 (345.147809 s), Rust 4 unit + 6 integration = **10 PASS**, 기존 **cell-cache 19설정(10 Radau + 9 SSPRK 대조) 모두 완료**다. 누적 RHS 시도 38,840, raw 내부 경과시간 합계 4.937230308 s다. `cell-borrowed` fixed Radau N2의 exit 0과 유한 물리값 일치가 반환됐다. 이 대화의 새 native 실행·build는 각각 **0**이며 저장된 반환 증거를 분석한다.

NCP binary SHA256은 **c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992**다. 이전 C10 sandbox binary `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`와 다른 실행 산출물이다. borrowed 개별 argv·inputs receipt·outcome receipt·binary hash는 archive에 없다. 동일 binary 연결은 delivery의 진술이며 독립 borrowed receipt로 복원되지 않는다. 명령을 추정하지 않으며 이 제한만으로 native 재실행을 의무화하지 않는다.

N2의 RHS 395·cell preparations 2,680·node visits 252,800은 같고 지정 상태/node clone은 cache 338/216,320 대 borrowed 0/0이다. raw wall은 cache 0.041180299 s, borrowed 0.061808789 s이며 stderr 마지막 0.091509 s는 측정 경계가 다르다. **speedup·memory reduction은 NOT_ESTABLISHED**, default legacy·성능 경로와 batch cell-cache는 유지한다. source-on 일반2차·uniform stiff·일반 양수성·Case B/full EoR/signed Bianchi·넓은 positive-CMB/비영 boundary·continuous global certificate는 HOLD, production은 NOT_ISSUED다.

archive `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`: 47,372,583 bytes, SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`. 이전에 게시된 이 archive의 양쪽 full readback receipt와 이번 회수 증거를 구분한다. 저장소 CI 두 job의 cargo fmt 실패·cargo test skipped도 NCP 표적시험 PASS와 별개다.

다음 행동은 반환 결과를 사용하고, 실제 profile이 병목을 보일 때 후속 optimizer 하나만 선택하는 것이다. 완료된 build·19설정·N2 smoke를 강제로 반복하지 않는다. 이번의 승인 범위는 ADMIT_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT이며, 독립 판정 PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT와 함께 반환 분석 STATE와 review/에 기록했다.

[현재 반환 분석](vigilode_radau_20261019/continuation_20261020b/ncp_return_analysis_20261020/REPORT_KO.md), [현재 상태](vigilode_radau_20261019/continuation_20261020b/ncp_return_analysis_20261020/STATE.json), [다음 대화](vigilode_radau_20261019/continuation_20261020b/ncp_return_analysis_20261020/NEXT_THREAD_PROMPT_KO.md)를 먼저 읽는다.

---

## 아래는 2026-10-20 07:39 UTC C10 및 이전 시점의 보존 기록

아래 NOT_RUN과 명령은 당시 상태·인계의 역사 기록이다. 현재 작업 요구나 미완료 실행 목록이 아니다.

# 최신 상태 — 2026-10-20 borrowed-cell 연구 완료

현재 실행 source는 **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**다. 기존 native-rate 연산열을 공유하는 **cell-borrowed**를 명시적 실험 옵션으로 추가했다. 두 버전의 실제 build/test/기존19설정 회귀와 독립 raw 읽기에서 물리 값 차이0, 지정 cached 상태·node clone0을 확인했다. **속도 향상은 입증되지 않았으며 성능 목적에는 기존 cell-cache를 유지한다.** default는 legacy다. 원본152개 기존 바이트·hook·VigilODE477개·provider/FD/허용오차를 유지했다.

[현재 연구 보고](vigilode_radau_20261019/continuation_20261020b/RESEARCH_REPORT_KO.md), [최신 source·실행·백업·DAG receipt](vigilode_radau_20261019/continuation_20261020b/FINAL_DELIVERY.json), [Codex NCP 인계](vigilode_radau_20261019/continuation_20261020b/CODEX_NCP_EXECUTE_KO.md), [다음 대화 prompt](vigilode_radau_20261019/continuation_20261020b/NEXT_THREAD_PROMPT_KO.md)를 먼저 읽는다.

현재 source의 새 NCP 실행은 **NOT_RUN**이다. 과거 d87ba9ca의 NCP19설정 완료, 제조76/Python57/과거84 및 기존19설정과 구분하며 재집계하지 않는다. 넓은 source-on 차수·uniform stiff·CaseB/fullEoR/signed Bianchi·production은 기존 HOLD/NOT_ISSUED다.

---

## 아래는 보존한 이전 전달 기록

# 최신 상태 — 2026-10-20 native 캐시·Rayon 최적화 C10 완료

실행 코드 source commit은 `33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1`이다. `--native-eval cell-cache`로 Jacobian 안의 광자 cell 준비를 재사용하고, 독립 이력은 pinned VigilODE의 local Rayon pool로 병렬 실행한다. 원본 native 152개 파일과 VigilODE 477개 파일의 bytes 및 모든 물리식·허용오차를 유지했다. 같은 기존 19개 설정의 회귀, 독립 전체값 비교, Rust 표적 10개·Python 실행기 4개 및 실제 옵션 전달 smoke가 통과했다. 15개의 교차 측정쌍에서 finite numeric equality를 유지하면서 native 실행시간이 줄었다. 메모리 감소와 별도 SIMD 구현은 이번 성과에 포함하지 않는다.

[새 연구 보고](vigilode_radau_20261019/optimization_20261020/RESEARCH_REPORT_KO.md), [최종 source·실행·백업·DAG receipt](vigilode_radau_20261019/optimization_20261020/FINAL_DELIVERY.json), [완성된 Codex NCP 인계](vigilode_radau_20261019/optimization_20261020/CODEX_NCP_OPTIMIZATION_KO.md)를 먼저 읽는다. C10 archive와 ACK의 Drive/Dropbox 전체 파일 readback이 모두 통과했고, 회수 archive의 payload 5,462개 파일을 검증했다. 복원된 native 153개·adapter 7개·VigilODE 477개 파일은 컴파일한 최종 소스와 같았다.

이번 optimization의 NCP 실행은 **NOT_RUN**이다. 아래의 d87ba9ca source NCP 완료 및 이전 NOT_RUN 문장은 각 과거 단계의 기록이다. 일반 source-on 차수·uniform stiff·CaseB/fullEoR/signed Bianchi는 HOLD이며 production admission은 NOT_ISSUED다.

---

## 이전 전달 기록

# 현재 상태 — VigilODE NCP 완료 및 2026-10-20 복원 확인

2026-10-19 NCP에서 고정 source `d87ba9ca25acb8a2a032154fa23057b45acd6207`의 locked/offline release build, 표적시험 7개와 **샌드박스와 같은 19개 고유 설정**이 완료됐다. 모두 exit 0, 실패·중단 0, native RHS 38,840회, native wall 15.824811033초다. 두 host의 실행을 38개 고유 설정으로 합산하지 않는다. 실행 근거 commit은 `09bfe94bc270623b014bc6db78c59211152739aa`, C11 전달 commit은 `46a29285ad7095959bb0e5b5a10dab0fec97501f`다.

[실제 NCP 실행 receipt](vigilode_radau_20261019/ncp_20261019T171038Z/NCP_EXECUTION_RECEIPT.json), [NCP delivery/DAG](vigilode_radau_20261019/stages/NCP_DELIVERY_20261019.json), [2026-10-20 복원 보고](vigilode_radau_20261019/recovery_20261020/RECOVERY_REPORT_KO.md)를 먼저 읽는다. 이번 host에서는 native run 0·build 0이며 prepare-only 복원과 저장 결과 readback만 수행했다. 316,540개 raw 비시간 수치 leaf와 209개 endpoint, 435+323개 분석 leaf가 유한 f64이고 packed IEEE64로 일치했다. 기존 walker와 같은 시간 leaf 38개는 제외했다. 이는 같은 유한 설정의 결과 재현 확인이다.

일반 source-on 차수·HeIII endpoint 단일 차수·uniform stiff 정확도·일반 양수성·Case B·full EoR·signed Bianchi·positive CMB/비영 boundary는 HOLD이며 production admission은 NOT_ISSUED다.

---

## 아래 본문은 NCP 실행 전까지의 역사적 전달 기록

아래의 NCP NOT_RUN·남은 실행 지시는 해당 작성 시점의 상태다. 현재 완료 상태는 위 receipt와 복원 보고를 따른다.

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

