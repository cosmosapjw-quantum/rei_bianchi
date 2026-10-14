---
name: physmath-research-loop
description: 사용자가 "연구 루프", "연구루프", "수학·물리 연구루프", "코딩 연구루프"를 실행하거나 이어 달라고 할 때, 현재 채택 모델에 따라 GPT-5.6 또는 GPT-6 Astra용 물리·수학 연구/코딩 하네스를 선택해 읽고 적용한다. 단순히 연구 루프라는 표현을 인용하거나 설명하는 요청에는 실행하지 않는다.
---

# 연구 루프: 모델에 맞는 하네스

사용자의 2026-09-08 명시적 선호다. "연구 루프" 실행 요청에는 채택 모델에 맞는 canonical 하네스를 우선 적용하라. 이 스킬은 작업 지침의 자동 선택 경로이며 ChatGPT 저장된 메모리 항목이 아니다.

## 선택과 로드

1. 현재 요청의 명시적 하네스 버전 선택을 먼저 적용하라. 없으면 현재 실행 모델을 호스트가 제공한 신뢰 가능한 metadata로 확인하라. metadata가 없으면 사용자가 현재 채택했다고 명시한 모델을 사용하고 그 근거를 기록하라. 단순한 과거 대화, 말투, 사용 가능 모델 목록은 현재 모델 증거가 아니다.
2. `references/MODEL_ROUTER.json`에서 GPT-5.6 계열은 gpt56 v3.1.0, GPT-6 Astra는 gpt6-astra v4.0.0으로 매핑하라. 필요하면 `scripts/resolve_model.py --registry <skill_root>/references/MODEL_ROUTER.json --model '<확인된 모델>' --task research|coding|both`를 사용하라. 명시적 버전 선택에는 `--harness`를 쓴다. 이 스크립트는 선택만 하며 모델 변경·메모리 쓰기·파일 취득·실행을 하지 않는다.
3. 모델이 불명확하고 버전 선택이 실제 다음 작업을 바꿀 때 한 번만 짧게 질문하라. 확인 가능한 입력은 다시 묻지 말고, 버전과 무관하게 가능한 읽기·계산은 계속하라. 알려지지 않은 모델을 6 또는 5.6으로 추측하지 말라.
4. 이론·문헌·수학·물리 연구에는 research, 코드 구현·수치 알고리즘·테스트에는 coding을 선택하라. 두 루프를 요청하면 연구 계약과 검증 결과를 코딩 계약으로 전달하라. 현재 명시된 scope와 claim ceiling을 보존하라.
5. ChatGPT Library에서 registry의 stable library_file_id로 파일을 해소하고 Library 스킬의 절차로 ZIP을 가져와라. ID가 없거나 삭제된 경우에만 registry의 고유 파일명으로 검색하라. 이미 제공된 첨부 바이트가 일치하면 재다운로드하지 말라. `START_HERE.md`, 해당 핵심 instructions, 현재 state, 필요한 phase만 읽어라. 실제로 읽기 전에는 "로드/적용 완료"라고 말하지 말라.
6. Library 접근이 없으면 사용자가 준 ZIP 또는 기존 프로젝트에서 정확한 버전의 파일을 사용하라. 모두 없으면 `HARNESS_UNAVAILABLE`을 명시하고 필요한 해당 ZIP 한 개만 요청하라. 파일명이나 과거 기억만으로 하네스 본문을 복원하지 말라.

## 실행 중 유지할 규칙

사용자의 현재 요청과 유효한 승인을 우선하라. 모델/하네스 전환은 완료된 연구를 다시 시작할 이유가 아니다. source identity, assumptions, definitions, closure, tolerances, existing failures, acceptance criterion, 남은 실행 예산을 보존하라. 리뷰 횟수 제한으로 생산적인 in-scope edit → test → diagnose → edit를 중단하지 말라. 새 과학적 의미·범위·미승인 외부 행동이 필요할 때만 그 경계를 설명하라.

다중 agent 작업이면 각 실행자의 확인된 모델로 그 작업에 맞는 하네스를 선택하라. 원본·과학 계약·claim ceiling은 공유하라. 도구 접근과 실제 모델 선택 권한은 호스트에 따르며 이 스킬이 생성하지 않는다.

GPT-5.6 원본은 변경하지 않았다. 구버전 안의 일반적 phase STOP이나 승인 문구가 사용자에게 이미 승인받은 bounded work를 반복 승인받으라는 의미가 되지 않도록 현재 명시적 지시를 적용하라. 연구·코딩 검증 기준 자체를 낮추지 말라.

자동 선택은 이 스킬이 활성화되고 호스트가 skill discovery를 지원할 때 작동한다. 모든 ChatGPT 대화의 기억 등록이나 모든 모델의 trigger 실행을 보장하지 말라. 소스·지침 확인, 실제 실행, 모델 간 성능 향상은 별도 근거 상태로 보고하라.

## REI 대화의 실행 장소 정책 (2026-10-11)

rei_bianchi 지속 통합 대화에서 사용자가 지정한 실행 분담을 적용할 때 `references/REI_EXECUTION_POLICY.md`와 `references/REI_EXECUTION_POLICY.json`을 읽어라. 독립 연구·코드 작성·가벼운 검증은 assistant의 클라우드 컴퓨터에서 직접 하고, 별도 연구/코딩 작업 스레드는 반복 blocker 해소에만 쓰며, 사용자 컴퓨터의 local Codex는 무거운 실행에만 사용하라. 기존 읽기 전용 VS Code 관찰은 유지하라. 이 정책을 다른 연구 대화에 자동 확대하거나 canonical 과학 하네스의 정확도·모델·예산·승인 규칙을 바꾸지 말라. 호스트 제약으로 직접 실행이 불가능하면 명시하고 사용자 컴퓨터로 임의 대체하지 말라.
