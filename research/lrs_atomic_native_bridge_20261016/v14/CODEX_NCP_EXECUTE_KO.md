# Codex: V14 최신 SSPRK2 실행 인계

이전84 native이력과projection62행은이미실행된근거다. 최신작업은 native SSPRK2 + common gas-midpoint + stable log1p clock의14표적시험/52transport행/16결합이력이다.

먼저 [완전한 최신실행인계](time_centered_ssprk2_20261019/CODEX_NCP_EXECUTE_KO.md), [현재연구결과](time_centered_ssprk2_20261019/RESEARCH_CONTINUATION_KO.md), [최종source·백업·DAGreceipt](stages/SSPRK2_FINAL_DELIVERY.json)를읽는다. 정상Git파일 run_ssprk2_native.py는 --input-root/--output-root/--cargo/--jobs/--mode를받는다. source를새run입력으로git archive하여기존checkout/dirty상태를보존하는정확한명령과source_publication_sha고정법이완전한인계에있다.

현재session에서새NCP실행은NOT_RUN(지정키없음,원격연결기월간한도)이다. NCP실행자는기존인증으로직접compile→14tests→transport52행→coupled16이력을수행하고sourceSHA/stdout/stderr/exit/raw와새백업을되돌린다. 사용자에게download/수동SSH/SCP/압축repair코드를요구하지않는다. source-on일반2차,HeIII endpoint차수,uniformstiff/CaseB/fullEoR/signedBianchi는실제추가근거없이승격하지않는다.

