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

