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

