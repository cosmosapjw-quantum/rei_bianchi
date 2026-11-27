# BASS_HE A1b — 실제 채널과 exact P/Q 정식화

현재 판정은 `RESULT.json`과 `review/A1B_INDEPENDENT_REVIEW.json`이 소유한다. A1b는 `A1_PHYSICAL_CHANNEL_EMBEDDING_SPECIFIED`, parent A1은 prescribed classical nuclear trajectory의 단일전자 비상대론적 exact P⊕Q 범위에서 `FRAME_COMPLETE_CONNECTION_DERIVED`다. 6채널 근사의 수치 정확도나 실제 충돌 단면적을 인증한 결과는 아니다.

## 읽는 순서

1. `BASS_HE_POST_R10R_THEORY_CLOSURE_REPORT_KO.md`: 결과와 한계.
2. `A1B_CHANNEL_EMBEDDING_DERIVATION_KO.md`: 정규화 원자 함수, ETF, S/h/D, projector, 그리고 §9의 exact P/Q completion.
3. `review/A1B_INDEPENDENT_REVIEW_KO.md` 및 JSON: 초기 후보의 gap과 실제 보강 후 최종 판정, 검토한 파일 identity.
4. `VERIFICATION.json`, `evidence/`, `code/`: 한 번 수행한 새 검증의 입력·출력.
5. `NEXT_HANDOFF_KO.md`: 다음 단일 A2 실행 계약. C1은 A2를 기다린다.

`derivations/ASYMPTOTIC_GRAM_NOTE_KO.md`는 6채널 후보에 대한 범위가 제한된 선행 저자 노트다. 그 노트만으로 A1을 닫지 않는다는 문구는 맞으며, 최종 판정은 이후 추가한 본문 exact P/Q 정식화와 독립 검토가 소유한다. Private archive의 `provenance/A1B_PRE_PQ_DRAFT_KO.md`는 보강 전 이력이며 현재 결과가 아니다.

## 증거 및 재현 범위

새 Gram/projector unit tests 8개, P/Q fixture 1회(15 residual), Wolfram exact CAS 1회가 수행되었다. 실제 명령, 버전, tolerance와 실행 결과는 `CODE_IDENTITY.json`, `NUMERICAL_CONTRACT.json`, `VERIFICATION.json` 및 증거 로그에 있다. `code/README_KO.md`는 Gram/projector 코드의 실행법이며 별도 P/Q 확인 입력은 `code/check_pq_completion.py`다. 기존의 변경 없는 과학 검증은 재실행하지 않았다. 현재 코드와 기록은 물리 eigensolve나 collision propagation의 결과가 아니다.

`BASS_HE_COUPLING_DATABASE.csv`는 이번 유도의 symbolic/analytic 항목 5개다. 수치 단면적이나 benchmark 측정값을 생성한 것이 아니다. 기존 benchmark matrix와 uncertainty ledger는 바이트 그대로 이월했다. B1 source authority gap은 유지한다.

## 입력과 게시

새 namespace는 `research/shared_c64/20261001/A1B_CHANNEL_EMBEDDING_20261001T0238Z`, 같은 branch는 `research/shared-c64-crossrepo-20260928`이다. `PUBLIC_MANIFEST.json`의 파일만 새 namespace에 게시한다. 이 manifest 자체는 self-reference를 피하기 위해 payload 목록에서 제외하지만 함께 게시한다. Git 전송은 원래 UTF-8 바이트 및 줄바꿈을 보존한다.

전체 private archive는 `private_dependencies/BASS_HE_POST_DATABASE_A1_B1_20261001_v1.zip`에 이전 archive를 포함한다. 그 안의 v3 원전과 자료는 immutable dependency다. 원문 PDF·페이지 이미지는 공개 Git에 넣지 않는다. 이전 archive SHA256는 `40856c46050796054d2da66563149705880888db84a69dd062bb767639d0039e`, scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`다.

Publication commit/tree 및 provider backup ACK·크기·복구 여부는 별도의 receipt가 소유한다. 업로드 ACK와 원격 크기 확인을 raw archive restore 검증으로 부르지 않는다. Archive의 `MANIFEST.json`/`MANIFEST.sha256`와 외부 ZIP SHA256는 전송·무결성 확인용이며 과학적 정확도 인증이 아니다.

## 유지되는 gate

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.
