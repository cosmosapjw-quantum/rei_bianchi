# FLRW06 실제96node 단계 반환 수신

Consumer8e8ea0c6의8개 새 반환 파일을 읽고 기존 native point 회귀와 새96node
primary_stage_step 증거를 수신했다. 단일 fixed-density/fixed-energy 단계이며
RCT stepper, expanding split-step 또는 F08 paired history 완료가 아니다.

실제 Dropbox archive 복구 SHA256:
`a73fb5b0aa76f6d94e0f5fac48be98002a1bf6fb77c6eae8a212b7af12fd6cad`.
2674608bytes/CRC/126payload manifest와 선택 입력21개 identity를 확인했다.
이는 sender outgoingR1 metadata보다 강한 **이번 incoming byte restore** 확인이다.
원 archive/binary는 ignored runs 캐시에 보존하며 Git에 재게시하지 않았다.

제공된 final_check.py는 saved receipts/outputs/sources를 검사하며 native나4D root를
실행하지 않는다. 출력만 새 경로에 atomic write+fsync/create-only로 보존하도록
SAVED_EVIDENCE_CHECK_ADAPTER.py와 OUTPUT_ADAPTER.diff를 준비해 실행했다.
원 FINAL_VERIFICATION.json은 바뀌지 않았다. 최초 시험의 잘못된 repo-root 경로는
TEST_PATH_FAILURE.log에 보존하고 .git 탐색으로 수정했다.

새 입력/출력 경계8시험 PASS: 원 receipt 보존, 비유한 JSON 거부, 누락 목적지 거부,
stage stdout/binary/source 변조와 실패한 reference 기록 거부.
Native0, reference root0, unchanged scientific suite0. Saved point comparator167개만
기존 고정 기준으로 확인했으며 stage1182개 비교는 hash-bound sender report로 수신했다.
1.307098350896367e-13 event relative 최대값을 새 수락 허용오차로 사용하지 않는다.
원 입력 및 사전 수락 기준은 inputs/archive/results/STAGE_INPUT.json과
STAGE_PREREGISTRATION.json에 원 byte로 보존했다.
독립 scientific review나 새 물리 상태의 검증 개수로 합산하지 않는다.

현재 stage12개 source blob를 대조했다. Coupled source는7c546910의09bb770a blob이고
baseline의 역사적 minimal lib와 최신 전체 crate identity는 구분한다.
기존 point stdout은 같고 binary는 다른 별도 실행이다. RCT local-RHS source도 그대로다.
입력/원본문서 pin은 INPUT_IDENTITY.json, 출력/수락 경계는 RETURN.json에 있다.

재검사에는 원 ZIP을 다음 위치에 복구해야 한다:
`runs/HE_FLRW06_INTAKE_20261004T205344Z/restored/rei_chat_flrw06_native_20261005/`.
원 archive의 hash/manifest를 먼저 확인하고, 원 research/final_check.py에
OUTPUT_ADAPTER.diff를 적용한 별도 final_check_preserving_receipt.py와 receipt_output.py를
research/에 둔다. 이 폴더의 `test_*.py`는 그 복구본에서 실패 입력만 검사한다.
실행: `python3 -B -W error -m unittest discover -s 이_폴더 -p 'test_*.py' -v`.
Saved checker 출력은 기존 파일을 덮어쓰지 않는 새 절대 경로를 인자로 지정한다.

다음은 owner의 RCT-STEP01 구현/native 반환 또는 FLRW07의2~4macrostep expanding
split-step 계약/반환이다. 후자는 먼저 추가F08 history 반환을 읽어 중복 campaign을
피해야 한다. Stage의 gas -2Hw는 이미 한 번 소유하므로 geometry에서 두 번 적용하지
않는다는 sender handoff를 보존한다. 여기서는 새 모델/solver를 만들지 않았다.

RCT OFF, source moments null, HE-F3 empty common-domain/F09 대기, physical HOLD,
Eq55 NOT_RUN, legacy PARKED_OPEN 유지. Consumer는 read-only이며 Git 동기화와
ChatGPT 직접 전달은 구분한다. 직접 스레드 전송은 수행·검증되지 않았다.
