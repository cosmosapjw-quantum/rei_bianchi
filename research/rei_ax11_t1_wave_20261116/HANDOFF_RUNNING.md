```text
$physmath-research-loop
REI-AXBI-GOAL-20261014 / rei_bianchi AX11 T1 wave를 이어라.
CENTRAL_REVIEW_PIN=56dc609ea9b801c88d3364aed3eee140b3a20d46
PROJECT=cosmosapjw-quantum/rei_bianchi
BRANCH=research/rei-ax11-source-profile-20261116
PR=https://github.com/cosmosapjw-quantum/rei_bianchi/pull/377
이 파일을 포함한 exact public HEAD를 먼저 읽어라. 직전 public pin은
a5aea61c738f70af811f3871ca08501c6db3e0c7이며 새 stage가 뒤에 게시될 수 있다.

CENTRAL 원 workflow10/17, expansion28/88, AX08 baseline5/5 승인은 그대로다.
F05/F08/다른 source·clock·상태를 섞지 않는다. AX12와 full T2/grid는 시작하지 않는다.
Owner consumer=rei_bianchi scientific admission owner; 다음 node=AX11.
완료 baseline과 continuation002를 재실행하지 말라.

Native device=edd1b263-56a0-4391-8a2a-677dd00eabf5
ROOT=/home/cosmosapjw/research_backups/rei_ax11_t1_wave_20261116_v1
현재 full T1 controller session PID=481017. prepare/launch 재시작 금지.
ROOT/RUN_LEDGER.json과 cases/{ZERO,PLUS}/segment_NNN/progress.json을 확인하라.
segment000과001은 각case 누적500000accepted,1500057trials,10500405RHS로
exit10 정상 경계를 완료했다. 500000의 checkpoint SHA는 다음과 같다.
ZERO=5d9159a3326e963e6033cbe62023541a040d932faf12899ec3433dedbd0fc728
PLUS=737c0d9d5103a512738bf1b189fb2f5850f91e113ba803de244361a888dfc0c9
두case segment002가 exact checkpoint에서 이미 시작되었다.
여기서 T1 segment002는 원 AX08의 완료된 continuation002와 다른 run이다.
최초 native zbar4 endpoint는 아직 미확인이다. 카운터/비용을 0으로 초기화하지 말라.

Code/binary/config/preflight identities는
research/rei_ax11_t1_wave_20261116/{ALLOCATION.json,FULL_EXECUTION_BINDING.json,
SOURCE_BINDING.json,PREFLIGHT_VALIDATION.json}에 고정되어 있다.
Binary SHA=aad91a873fb475b56347f254a21882e974b09067183ddab0907d82bb05843404
Full-IC T1 source library는 이전 승인 candidate와 같다.
진전은 실제 endpoint와 paired error evidence로 세며 비용개선/게시를 node로 세지 않는다.

T0 기존1001점 두표와 original interp/field_at을 재사용한다.
BASELINE_REUSE.json, SAMPLING_GRID.json, SCIENCE_CONTRACT.md를 읽어라.
Consumer는 저장된nativefixture 32조합×1001점에서 원full-array 보간과 bit-equal했다.
동일저자 적대적검증이며 독립blind-referee라고 주장하지 않는다.

Native postprocessing source 3개와 ROOT/SAMPLING_GRID.json,
POSTPROCESS_PACKAGE_MANIFEST.json이 업로드되어 있고 아직 실행하지 않았다.
RUN_LEDGER가 T1_WAVE_FINISHED_WITH_RETAINED_OUTCOMES로 닫힌 후에만
python3 ROOT/harness/postprocess_executor.py ROOT
를 한 번 실행할 수 있다. 먼저 POSTPROCESS_STARTED.json 존재 여부를 확인하라.
이 launcher는 실제 남은 original18000CPU/summedwall 예산 안에서만
추출과 raw archive를 실행하며, 충분한 잔액이 없으면 실행을 거절한다.
원시자료는 삭제하지 않는다. Dropbox local copy와 provider verification을 구분하라.

ROOT/analysis_v1/{ZERO,PLUS}_sample_brackets.json.gz와 EXTRACTION_RECEIPT.json을
hash 검증해 가져온 뒤 harness/analyze_t1_response.py로 기존T0와 비교하라.
고정a·동일proper-time D01_state_ZERO, D01_state_PLUS, D01_pair를 모두 보존한다.
D01만으로 D12/수렴차수/전체오차상한/AX11완료를 주장하지 않는다.
실제 T1결과·비용·보존식·백업검증 후 같은작성자 적대적최종심사와 owner admission을 한다.
단계마다 backup/publication와10/17·28/88을 기록하고 마지막 exact HEAD handoff를 갱신하라.
```
