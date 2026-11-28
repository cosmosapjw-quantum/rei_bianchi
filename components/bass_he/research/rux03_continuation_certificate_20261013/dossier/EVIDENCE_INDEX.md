# THEORY06 근거 연결

과학 unit의 파일 identity는 CANDIDATE_MANIFEST와 최종 SCIENCE_MANIFEST에 고정한다. 실제 채택 상태는 review/DECISION.json이다. 다음 표는 주장·논증·actual checks를 연결한다. 검산 수가 전구간 증명을 대신하지 않는다.

| Claim family | 증명 | 실제 입력·원응답·결과 |
|---|---|---|
| C1 affine physical cube와 primitive 경계 | derivations/PRIMITIVE_DIFFERENTIAL_BOUNDS.md 및 .json | evidence/PRIMITIVE_DIFFERENTIAL_CALL_INPUT.json, PRIMITIVE_DIFFERENTIAL_RAW_RESULT.json, PRIMITIVE_DIFFERENTIAL_RESULT.json — 17 groups |
| C2 실제 FT03/Verner 경계 | source_map/SOURCE_FUNCTIONS.md, derivations/RATE_ENVELOPES.md | evidence/RATE_ENVELOPE_CALL_INPUT.json, RATE_ENVELOPE_WOLFRAM_RAW_RESULT.json, RATE_ENVELOPE_RESULT.json — 20 groups |
| C3 exact full source·photon derivative | derivations/FULL_SOURCE_CONTINUATION_CERTIFICATE.md S1–S25 | FULL_SOURCE_CERTIFICATE 입력·raw·result의 CS01–CS06; xAct의 3개 source-projection group |
| C4 실제 H·branch·corrector 경계 | derivations/EXPLICIT_H_CERTIFICATE.md; main proof S26–S31 | evidence/FULL_SOURCE_CERTIFICATE_CALL_INPUT.json, FULL_SOURCE_CERTIFICATE_RAW.json, FULL_SOURCE_CERTIFICATE_RESULT.json — 12 groups 전체의 결합 근거 |
| C5 tube와 maximum endpoint 대안 | main proof S32–S34 및 6절, EXPLICIT_H 6절 | 구성적 증명 및 독립 문헌·검토. H를 넘는 새로운 tube chain의 실제 수치 실행은 없음 |
| C6 tensor variations·coding 연결 | XACT_CONTINUATION_VARIATIONS_v2.wl, CODING_CONTRACT.md | evidence/XACT_CONTINUATION_CALL_INPUT_v2.json, XACT_CONTINUATION_RAW_v2.json, XACT_CONTINUATION_RESULT.json — 8 groups/17 residuals |

정확한 실행 내역과 실패 분류는 evidence/EXECUTION_RECORD.json 및 rate 개별 실행기록을 따른다. 초기 xAct v1은 완료되지 않은 실제 시도이며 input/raw를 보존했다. Metadata 미수신과 긴 JSON 생략은 과학 반례나 성공 재실행의 근거로 해석하지 않았다.

## 계승 근거

[부모 PR33](https://github.com/cosmosapjw-quantum/BASS_HE/pull/33)의 채택 THEORY05에서 global positive-gap primitive inverse, 일곱 finite source balance와 finite thermal diagnostic을 재사용한다. 부모의 accepted decision hash는 `c189d11f5a2c3f9c2e1e21ff5ad12d2451d254e6e751c3375cffc64a9aebfa8e`, science-manifest hash는 `b3d59e377a913a0b42dee91e767d73ad89d0969b64decd55aaf3183a7b342559`다. 관련 source head·tree·file hashes는 source_map/CURRENT_SOURCE.json에 고정했다.

## 문헌·검색

review/LITERATURE_MAP.md, SEARCH_EVIDENCE.json, SOURCE_EVIDENCE.json이 actual query와 읽은 정리·scope를 기록한다. Exa 4 query/20 requested slots/19 unique URLs, SciSpace 1 query/10 entries, 직접 읽은 primary theorem sections 3편을 구분한다. 긴 원문 PDF/검색 raw는 별도 local cache에 보존하며 science write set에 재배포하지 않는다. 과학 근거로 쓰지 않은 Wolfram contextual lookup의 두 긴 raw도 같은 원칙으로 제외하고, evidence/CONTEXT_LOOKUP_RECORD.json에 input/hash/scope를 남긴다.

## 파일의 역할

REPORT_KO는 사용자용 결과와 핵심 유도, CODING_CONTRACT는 실제 구현 입출력과 완료 근거, HANDOFF_KO 및 NEXT_DAG는 다음 작업을 정의한다. CLAIMS는 각 family의 domain·증거·남은 제한을 명시한다. CANDIDATE_MANIFEST는 독립 reviewer가 읽는 고정 저자 상태, SCIENCE_MANIFEST와 CLOSEOUT은 판정까지 포함한 종결 상태다. Git/backup/최종 파일 전달 receipt는 자기 참조를 피하도록 과학 manifest 밖에서 생성한다.
