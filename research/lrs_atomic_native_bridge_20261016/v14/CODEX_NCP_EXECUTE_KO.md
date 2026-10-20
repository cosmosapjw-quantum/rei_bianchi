## 현재 전달 상태 — 실제 게시와 archive·sidecar 양쪽 전체 읽기 검증 완료

실제 stage1 commit은 **82364d3d2548a1e864468cb781336f825fc18c29**이며 원격 22파일의 전체 내용과 Git blob SHA가 모두 일치했다. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**와 과학 판정은 그대로다. 이 최종 metadata의 Git identity는 이를 담는 **ENCLOSING_COMMIT**이며, 아직 수행하지 않은 최종 ref 이동·원격 readback의 성공을 미리 주장하지 않는다.

고정 archive `REI_LRS_NCP_RETURN_RECOVERY_20261020.tar.xz`는 **1,816,608 bytes**, SHA256 `089a1ab2bf05f3368b77b5ec330bfb394b176e7f0b89ce7e32ce6eb2c71390be`다. 233파일의 manifest SHA256은 `6f438f505571d396c91ae1b13f2baabf41bc9497c64b71291539496a4ac9cebe`다. Drive `1XMokGRZfOeE284bvC0wJHuzD86rNMLRl`, Dropbox `id:BSpOijBcT10AAAAAAD_aEw`에서 전체 회수한 bytes·SHA256이 모두 일치했다.

별도 sidecar `REI_LRS_NCP_RETURN_RECOVERY_20261020_ACK.json`도 **4,735 bytes**, SHA256 `71ed1fbf1a5179d13199f321d6b01cf7591b4a9e116dc31342d02bc7b455a6c0`으로 Drive `1sMHEilLsvPF19lWhQ8gr1CgLzS8aB5TB`, Dropbox `id:BSpOijBcT10AAAAAAD_aFQ`의 전체 회수가 모두 일치했다. 모든 회수 process exit는0이다. Drive의 원천 HTTP 상태는 connector가 노출하지 않으며 raw fetch 성공 및 materialization HTTP200을 확인했다. Dropbox 직접 GET은 HTTP200이다.

archive 내부 PREPARED_NOT_PUBLISHED는 동결 당시 상태다. 실제 순서는 archive 동결 → Git 게시와 archive 양쪽 읽기 검증 병행 → sidecar 양쪽 읽기 검증 → 최종 metadata commit이다. archive·sidecar bytes와 과학/analysis/review 원문은 바꾸지 않았다. 이번 native 실행·build·Rust/native/numerical source 변경은0이며, 원래 C10 archive 필드는 역사 범위로 보존한다.

[최종 실제 ACK](vigilode_radau_20261019/continuation_20261020b/ncp_return_analysis_20261020/FINAL_PUBLICATION_ACK.json)에서 실제 게시·archive·sidecar 회수 receipt와 승인 범위를 확인한다. 다음 과학 작업은 실제 profile이 지목하는 optimizer 하나에 한정하며 완료된 native 실행을 강제 반복하지 않는다.

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

같은 19개 설정의 NCP 실행은 현재 미완료 작업이 아니다. 아래 실행 명령은 앞으로 사용자가 명시적으로 재현 실행을 선택할 때 참고한다. 최신 결과·source·백업부터 확인하고 실제로 빠진 작업만 수행한다.

---

## 아래 본문은 이전 실행 전 인계의 역사적 기록

아래의 NOT_RUN·NCP에 남은 작업 문장은 당시 상태이며 현재 실행 지시가 아니다.

# Codex: V14 최신 VigilODE Radau 실행 인계

현재의 실행 source는 `d87ba9ca25acb8a2a032154fa23057b45acd6207`이며 최종 branch HEAD와 구분한다. 먼저 [최신 완전한 실행 인계](vigilode_radau_20261019/CODEX_NCP_EXECUTE_KO.md), [연구 결과](vigilode_radau_20261019/RESEARCH_DELIVERY_KO.md), [source·backup·DAG receipt](vigilode_radau_20261019/stages/FINAL_DELIVERY.json)를 읽는다.

정상 Git 파일 `vigilode_radau_20261019/prepare_and_run.py`는 `--input-root`, `--output-root`, `--cargo`, `--all`을 받는다. 기존 checkout을 건드리지 않고 `git archive`로 source 입력을 추출하는 명령, VigilODE pin/복원 및 compile→7 Rust tests→19 native 설정과 사후 분석 명령이 완전한 인계에 있다.

샌드박스의 19개 실제 설정은 완료됐다. NCP에는 이 source의 실제 컴파일·표적시험·동일 설정 실행과 필요한 작은 호환 수정만 남는다. 새 NCP 실행은 NOT_RUN이며 현재 환경에는 지정 SSH key가 없다. 사용자에게 다운로드나 수동 SSH/SCP를 요구하지 않는다. 과거 84개 NCP 이력·제조76·Python57은 새로 세지 않는다.

---

## 아래는 직전 SSPRK2 실행 인계

# Codex: V14 최신 SSPRK2 실행 인계

이전84 native이력과projection62행은이미실행된근거다. 최신작업은 native SSPRK2 + common gas-midpoint + stable log1p clock의14표적시험/52transport행/16결합이력이다.

먼저 [완전한 최신실행인계](time_centered_ssprk2_20261019/CODEX_NCP_EXECUTE_KO.md), [현재연구결과](time_centered_ssprk2_20261019/RESEARCH_CONTINUATION_KO.md), [최종source·백업·DAGreceipt](stages/SSPRK2_FINAL_DELIVERY.json)를읽는다. 정상Git파일 run_ssprk2_native.py는 --input-root/--output-root/--cargo/--jobs/--mode를받는다. source를새run입력으로git archive하여기존checkout/dirty상태를보존하는정확한명령과source_publication_sha고정법이완전한인계에있다.

현재session에서새NCP실행은NOT_RUN(지정키없음,원격연결기월간한도)이다. NCP실행자는기존인증으로직접compile→14tests→transport52행→coupled16이력을수행하고sourceSHA/stdout/stderr/exit/raw와새백업을되돌린다. 사용자에게download/수동SSH/SCP/압축repair코드를요구하지않는다. source-on일반2차,HeIII endpoint차수,uniformstiff/CaseB/fullEoR/signedBianchi는실제추가근거없이승격하지않는다.

