# Codex/NCP 인계 | 단일 age32 reference READY

## 2026-10-20 현재 재개점: 최적화 완료, 새 native age32는 별도 READY

`optimization_20261020/`의 exact-arithmetic/cache/shared-oracle 최적화와 실제 측정을 재사용한다. Warm median baseline2 47.413 s, A2 10.461 s, B2 6.619 s, C2 3.532 s, C8(8 threads)1.560 s; scientific numeric bits는 동일하다. 원 입력·정확도·native B1은 바뀌지 않았다. 표준 최적 실행은 `optimization_20261020/run_optimized.py`이며 필요 없는 benchmark 재실행은 하지 않는다. 새 report/README/THEORY/BENCHMARK와 C9 receipt를 먼저 읽는다.

이번 baseline PR HEAD는 58dc257d1402daa3d0f64786279e13cd72bfb0c7/task1360944eb7e94743c1d5a668e7458f5b4f902d7a. v7 source는 354823050e6da98e64dde40596be061ce22e71f2/taskc583d426082fedc6ff67cce9644388e61573b492에 게시했고 실제 Git blob/mode를 확인했다. C8/C10의 Drive/Dropbox 네 upload와 네 whole-file readback은 PASS다. Source/native153/B1/vendor와 전체 payload를 확인했고 실제 provider IDs·SHA·receipt는 DELIVERY_RECEIPT_CURRENT.json과 evidence/delivery_v7_20261020/에 있다. 실제 source와 backup은 완료되었고 이 배송 기록의 identity는 자신을 담은 Git commit이다. Exact HEAD는 별도 post-commit v7 confirmation과 actual PR HEAD에서 확인한다. Confirmation 자체의 upload/readback은 별도 후속 단계다. CURRENT5 이전 원문은 optimization_20261020/baseline_current/에 보존했다.

현재 NCP는 DEVICE_LIST_SUCCEEDED; NCP_SSH_NOT_PROBED_THIS_TURN; NCP 과학 실행 NOT_RUN이다. 월 사용량 중지는 과거 receipt이며 현재 blocker가 아니다. 공식 Rust/cargo1.94.1 runtime과 22 locked vendor가 실제 작동한다. 재첨부192287020-byte installer SHA294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40는 추가 provenance이고 기존 공식 설치를 교체하지 않았다.

아래 age32 사용자 파일 처리 없는 복사 프롬프트, 원 binary/runtime identities, 원 gate와 cap은 유지한다. Native age32 READY와 native age/time HOLD는 최적화로 해제되지 않는다. PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.

## v6 인계의 유지된 과학·실행 본문


이번 intake HEAD는 `0ae749e9fdb179729c018706dbd59c4f61732b6a`다. 새 VigilODE 연구 source와 C8/C10 v6의 실제 배송 상태·commit·SHA는 `DELIVERY_RECEIPT_CURRENT.json`과 PR199 actual HEAD에서 확인한다. 기존 v5 배송 및 age64 결과는 보존한다. 이미 생긴 새 결과가 있으면 그대로 ingest한다.

## 이번 로컬 연구도 완료됐다

`vigilode_age_transport_20261019/`의 고정-opacity/native-derived 연구는 원래64 source/57,344 nodes, VigilODE affine original modules, exact-rational exp, locked22 dependencies, 4설정 및 독립 검산까지 완료했다. 전체 N32→64의 −0.815145%와 sensitive-node N의 약 −82.574593%를 구분한다. 이 모형은 원 nonlinear trajectory가 아니며 기존 native time HOLD를 해제하지 않는다. NCP에서 이 완료된 분석을 다시 돌릴 필요는 없다.

수정한 Rust 코드의 컴파일만 필요할 경우 새 task runtime에서 bundled inputs/offline dependency를 사용할 수 있다. 실제 재분석 명령은 새 subtree README에 있으며 필요 없이 실행하지 않는다. 다음 과학 실행은 아래 age32 native reference 한 사례다.

## 고정 기준과 완료 작업

- Repo cosmosapjw-quantum/rei_bianchi, draft PR199, branch research/rei-age-exposure-envelope-20261018.
- 경로 research/rei_age_exposure_envelope_20261018/. 먼저 실제 PR HEAD와 DELIVERY_RECEIPT_CURRENT.json을 읽고 선택 HEAD를 기록한다.
- 원 native physics35d9747a0bbedcafdb568467ce7c1e7a25f965b6.
- B1 binary SHA89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4.
- 원 computational solver SHA78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620.
- 원 prepared identity SHAe376b58ee3ef2b14cda70bc8d966d686db52aabc0a832cab0b8cc0ea8a430bfd.
- 기존 NCP runtime Python3.12.3/NumPy2.3.5/SciPy1.17.0, transport48, BLAS1, rustc/cargo1.99.0.
- 원 age64 결과는 COMPLETE이며 반복하지 않는다. 이번 age32 코드·진단·비교는 로컬 구현, 독립 검토, 실제 tiny native off/on 대조까지 완료했다. native time8/16/32는 별도 HOLD다.

## 사용자 파일 처리 없이 실행할 복사 가능한 지시

아래 지시 전체를 Codex에 복사한다. 이것은 실행을 위임하는 프롬프트이며 이 대화에서 NCP 실행했다는 뜻이 아니다.

~~~text
physmath-research-loop와 repo AGENTS를 읽고 REI age32 후속 실행을 수행해.
먼저 PR199와 최신 Drive/Dropbox를 실제로 읽어 이후 age32 결과가 이미 생겼으면 그것을 ingest하고 같은 실행을 반복하지 마.
Repo cosmosapjw-quantum/rei_bianchi, branch research/rei-age-exposure-envelope-20261018,
task research/rei_age_exposure_envelope_20261018/.
README_CURRENT_KO.md, HANDOFF_CODEX_CURRENT_KO.md, HANDOFF_NEW_CHAT_KO.md,
contracts/NEXT_DAG_CURRENT.json, DELIVERY_RECEIPT_CURRENT.json을 먼저 읽어.
RESEARCH_UPDATE_20261019_VIGILODE_KO.md와 완료된 고정 모형 결과도 읽어.
VigilODE 연구는 native age32 결과가 아니다. 그4설정 분석/원 native age64/spectral128은 완료되어 반복하지 마.

NCP 연결은 실제 사용 가능한 경로로 확인해. 기존 접속 대상 root@49.50.142.2.
키/토큰 내용은 출력하지 마. owner checkout, PR150/R9, LRS repo, BASS HHeD,
기존 프로세스·기존 결과를 변경하지 마.
새 task-owned /root/REI_AGE32_REFERENCE_<UTC>를 만들고 다음 task-owned repo를 사용해:
  /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/repo
이 repo가 없으면 새 task 아래에서만 clone해.
실제 확인한 PR HEAD를 fetch한 뒤 git archive로 새 task/code에 task 경로를 export해.
standalone archive ancestry를 force-push하지 마.

기존 venv /root/REI_AGE_ENVELOPE_20261018T132700Z/venv를 읽기 전용 재사용해.
Python3.12.3, NumPy2.3.5, SciPy1.17.0인지 실제 확인하고
transport48, OMP/OPENBLAS/MKL1을 설정해.
비교 기준:
  BASE_RUN=/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/run
  prepared=$BASE_RUN/native
  age64=$BASE_RUN/results/age64/attempt001
이 기준의 원 BUILD_RECEIPT, PREPARED_IDENTITY, binary, age64 RECEIPT와 outputs를 검증해.

기준 파일이 사라졌으면 사용자에게 ZIP 이동·해제를 맡기지 말고 자동 복원해:
  파일 REI_AGE64_BLOCKMAX_NCP_20261019T084150Z.zip
  SHA256 d1a1166de0426c660d6edda4e66df50c87bc7a93267d3b78ea07d0e85e3a2178
  Drive folder rei_bianchi_research_backups
  Drive file id 1xHJ0mUeQL-REI3v5NvP07NToqqKDNFFn
  Dropbox /bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/
  Dropbox file id id:BSpOijBcT10AAAAAAD_QgQ
가용 connector 또는 기존 rclone gdrv:/dbx:로 새 task에 다운로드하고 SHA/CRC/payload를 확인한 뒤 해제해.
예: rclone copyto --immutable gdrv:rei_bianchi_research_backups/REI_AGE64_BLOCKMAX_NCP_20261019T084150Z.zip <새 task의 zip>
Drive 경로가 실패하면 기존 dbx:/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/ 경로를 사용해.
BASE_RUN을 복원된 REI_AGE64_BLOCKMAX_NCP_20261019T084150Z/run으로 지정해.
현재 reference_base.py가 compactB1의 동일 prepared source를 복원하고 원 binary binding을 검증한다.
원본 build receipt를 새 binary에 맞춰 꾸며 변경하지 마.

새 코드 src를 PYTHONPATH에 넣고 기존 gate와 runtime/binary가 맞는지 preflight해.
전체 old test suite와 완료 캠페인을 반복하지 마.
필요한 컴파일·작은 환경 연결 수정만 하고 다음 명시적 한 사례만 실행해:
  export REI_PREPARED_BASE="$BASE_RUN/native"
  export REI_TRANSPORT_THREADS=48
  bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age32-block-max-diagnostics
q0 age32/n_mu8/source8/transport16/time1, binary64, block-max, diagnostics ON,
원래 rtol/atol·RK·source schedule·photon/energy1e-8, case/total cap1800s 유지.
기준 binary SHA89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4,
computational base SHA78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620
및 비교 runtime이 맞지 않으면 실행 전 해당 mismatch를 HOLD로 남겨.
age64, spectral128, native time8/16/32, iso-cost RMS 재실행은 하지 마.

성공하면 source_jump_diagnosis.py --data <새 age32 attempt/data> --out <새 결과 JSON>,
photon_ledger_diagnosis.py로 저장 ledger 진단을 만들고,
compare_age_references.py --age32 <새 attempt> --age64 "$BASE_RUN/results/age64/attempt001" --out <비교 JSON>을 실행해.
binding-block telemetry를 실제 accepted/discarded/rejected 범위에 맞게 분석해.
source-jump32/32 coverage, nonbirth/gas/ledger 좌표 bits, 정확 저장 잔차를 보고하고 새 gate를 만들지 마.
기존 age64 source jumps는 MISSING_DATA로 둬.
비교기는 source/runtime/output hash를 검증한다. finite32→64 차이를 continuum 인증으로 쓰지 마.
실패·cap·identity mismatch 시 raw source/config/stdout/stderr/receipts를 보존하고 자동 재시도하지 마.

모든 실제 결과와 실행된 코드 SHA·runtime·binary·solver hash·exit·wall·RHS를 저장해.
변경이 필요했다면 작은 수정과 검증 근거를 포함해 PR199 branch에 expected-head fast-forward push해.
새 결과 ZIP을 Drive와 Dropbox에 새 이름으로 올리고 실제 전체 readback SHA/CRC/payload를 확인해.
CURRENT5, DAG, delivery receipt를 갱신하고 매 단계 게시/백업/DAG를 표시해.
PR은 draft 유지, no merge/no force-push.
PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.
~~~

## 해석 제한

단일 age32 결과가 기존 age64와 비교 가능해지는 것이 이번 목표다. age resolution의 finite-neighbor 차이, 출생 jump 저장 잔차, binding blocks를 분리해 보고한다. observer 추가 자체는 기존 age64를 다시 실행할 사유가 아니다. block-max의 성공만으로 RMS 희석 가설을 판정하지 않는다.

현재 wrapper의 원본 time8-subnormal-count 모드는 과거 진단용이다. native count/energy representation이 HOLD인 상태에서 이 모드를 새 캠페인으로 실행하지 않는다.

## v6 최종 배송 확인

완료된 source snapshot은 `50bc41f6b6aea05f67c03ab3ad23bb118d574622`이며 C8/C10 v6의 양 provider 네 전체 readback이 완료되었다. 다음 시작에서는 별도 final confirmation과 PR199 actual HEAD를 먼저 읽고, 이미 완료된 고정 모형 계산·export를 반복하지 않는다. Immutable ZIP에는 생성 시점의 pending CURRENT가 남고, 이 최종 receipt가 이를 대체한다. Source CI의 기존 task 밖 formatting 실패와 skipped tests는 `SOURCE_CI_READBACK.json` 참조.
