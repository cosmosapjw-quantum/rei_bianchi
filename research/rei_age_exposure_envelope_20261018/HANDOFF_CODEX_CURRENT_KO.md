# Codex/NCP 현재 인계 | v9: age32 완료, 추가 native 실행 미발행

## 먼저 확인할 상태

기존 단일 `age32-block-max-diagnostics` 실행은 `93aca4cc483080b802fa85c9c44e43b9c85db5b7`에서 완료됐다. Native248.815719s/11786RHS/exit0, 원 photon·energy gate PASS다. 현재 분석은 `native_age32_analysis_20261020/results/attempt004/ANALYSIS.json`이며 native32/64의 N/U 상대차0.8248861211419689/0.7916059535400799는 원0.005 목표 FAIL이다.

**현재 NCP에 남은 필수 실행은 없다.** 완료 age32·age64·spectral128·v7 benchmark·v8 fixed-model 계산을 반복하지 않는다. Native age/time HOLD, nonlinear response bound NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED다. 다음 native 실행을 하려면 CURRENT DAG의 path exposure/source/reconstruction 연구 의무에서 새 workload를 구체화해야 한다.

## 자동 입력 복원

User에게 ZIP 이동·해제를 맡기지 않는다. 실제 최신 PR199 HEAD와 CURRENT5를 먼저 읽고, 기존 task-owned 저장 자료가 없을 때만 connector 또는 이미 설정된 rclone으로 새 task-owned 경로에 복원한다. Owner checkout, PR150/R9/LRS/BASS HHeD, 기존 실행과 파일을 변경하지 않는다.

C10은 source `729a12c5fdee8d05e77f26b396f0464c945351e1`의2,242 files snapshot이다. 실제 C10 provider IDs·SHA는 `DELIVERY_RECEIPT_CURRENT.json`을 따른다. 별도 post-commit `REI_AGE_ENVELOPE_DELIVERY_CONFIRMATION_20261020_v9.json` 자신의 IDs·SHA는 최종 사용자 인계 본문 또는 외부 배송 receipt를 따른다. Confirmation은 자신의 hash를 내부에 포함하지 않는다. C10 원 task snapshot에 confirmation의 정확한 UTF-8 delta를 자동 적용해 최종 tree를 확인한다. C10 루트의 `archive_only/RESTORATION_LAYOUT.md`이 원 native153/B1/deduplicated source161·vendor 복원 정보를 제공한다.

새 native32 입력은 C10의 `archive_only/native_age32/REI_AGE32_BLOCKMAX_DIAGNOSTICS_NCP_20261020T112800Z.tar.gz`에 들어 있다. C10을 사용하지 않을 때 이 파일을 직접 자동 다운로드해도 된다.

- Archive bytes1,181,985 / SHA256 `8c4579811faefbf3738c2dcd3c5105300a9aedec0b08c930bee032e094ef0cde`
- Drive folder `1phclg92jkhC5KgvnXhks8GbOFlya4qGe`, file `1VXPkeMv7-u3GTbVFRESX8poY6X-7qFTw`
- Dropbox `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`, file `id:BSpOijBcT10AAAAAAD_UEw`

새 빈 디렉터리에 archive를 해제한 뒤 `run_corrected/results/age32/attempt001/data`를 사용한다. 부모의 RECEIPT.json과 executed source도 함께 유지한다. ArchiveSHA,45raw hashes, 실행 source SHA `ab240948846a3a09e2bb60767af206e3865f6528a8673c90de177582569596f7`를 확인한다. Age64는 현재 task의 `evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data`를 재사용한다. 상세 경로는 `native_age32_analysis_20261020/RAW_INPUTS.json`에 있다.

## 저장 자료 분석을 다시 수행해야 할 구체적 이유가 생긴 경우

현재 결과를 읽기만 하는 데 재실행은 필요하지 않다. 환경 이식 또는 새 입력 확인이 실제로 필요할 때만 다음 entrypoint의 절대경로를 assistant가 정해 사용한다.

~~~bash
python <task>/native_age32_analysis_20261020/run_bounded.py \
  --data32 <자동복원한-native32>/run_corrected/results/age32/attempt001/data \
  --data64 <task>/evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data \
  --out <새-빈-attempt-directory> \
  --receipts <새-receipt-directory> \
  --postprocess-only
~~~

이 경로는 Python·NumPy·Matplotlib 저장 자료 분석이며 native solver/Grackle/Rust trajectory를 호출하지 않는다. 기존 결과를 덮어쓰지 않고120s aggregate cap과 command/exit/wall/stdout/stderr receipts를 유지한다. Native runtime 동일성은 Python3.12.3/NumPy2.3.5/SciPy1.17.0·B1 계약으로 별도 보존한다. Postprocess runtime과 native runtime을 혼동하지 않는다.

## 다음 native 작업에 반드시 남길 계약

원 physics `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, B1 binary SHA `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`, computational base SHA `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`를 유지한다. Native time8/16/32는 HOLD다. Source representation을 바꾸려면 이전 fixed-support 제약과 source-age 전달 문제를 수학·코드·작은 검증으로 먼저 닫고, NCP에는 필요한 컴파일·작은 환경 연결·명시된 실행만 남긴다.

모든 새 원격 변경은 그때 읽은 실제 HEAD를 부모로 잇고 expected-head fast-forward만 사용한다. PR199 draft/open, no merge/no force-push. 원 root CI cargo fmt 실패와 scoped analysis/R6/C9 PASS를 구분한다.

## V9 백업 확인

C10 Drive ID `1c6bCjR8oY3bhr337zqjVOi03lUbIclwD`, Dropbox ID `id:BSpOijBcT10AAAAAAD_aAA`, bytes25,147,021, SHA256 `5eef15a565636fa1e7c160aa30f3b2bb294dfa00364e504ee774f867c6ca4995`. C8/C10 네 전체 readback과 두 C10의 native/B1/vendor/raw checks가 PASS다. Source task tree `0cd25257f9e0fe4cfe1ce4ea6f34f2f65929fab7`. Final commit identity는 별도 confirmation에 있으며 자동 복원 후 exact tree를 확인한다. 현재 추가 native READY는 없다.
