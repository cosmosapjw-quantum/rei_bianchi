# Endpoint metadata·중앙 DAG 독립 최종 검토

## 판정

**PASS_SCOPED_METADATA_AND_DAG** — reviewer `/root/rei_baseline_intake`.

이 addendum은 앞선 `FINAL_BASELINE_REVIEW.md/json`의 **PASS_SCOPED_SAVED_STATE_NORMALIZATION_AND_CALLBACK_BINDING**을 유지한다. 구현자 및 root framing 작성자와 다른 reviewer가 최종 시나리오·판정·보고서·다음 입력 계약·인계·재현 명령·DAG를 읽고 저장 자료만 비교했다. 과학 코드 수정, 공급자 import/callback, suite·적분·IVP 재실행은 하지 않았다.

## 메타데이터 항목의 종결

- **BASELINE-SCENARIO-01 CLOSED:** `SCENARIO.json`이 실행 전 동결한 모형을 요약한다. 원 donor SHA256, 실제 endpoint·온도·0인 종, r 및 n_ref0가 `ACTUAL_STATE_BINDING.json`과 일치한다. 고정된 것은 comoving bookkeeping number이며 물리 r 자체는 팽창한다. R≠0 manufactured control을 새 물리 시나리오로 승격하지 않았다.
- **META-DEPENDENCIES-01 CLOSED:** 새 child의 `source_field=dependencies`가 가리키는 `SCIENTIFIC_DECISION.json`에 정확한 세 dependency가 들어 있다. `REI-EXP-SCENARIO`, `REI-CHEM-LEDGER-01`, `REI-EXP-OPACITY-CONSUMER`가 contract·wrapper·decision 사이에서 일치한다.
- **META-REVIEW-COST-01 CLOSED:** supplier의 작은 산술 재구성 비용과 baseline reviewer의 저장 증거 비교 비용이 각 reviewer·source·계측 범위와 함께 분리되었다. 수작업·이미지·원격 작업의 미계측 overhead를 0으로 기록하지 않는다.
- **META-HE-CONDITIONAL-01 CLOSED:** energy-only heating/degradation을 선택할 때 필요한 energy distribution·stopping과 anisotropic transport/momentum을 선택할 때 필요한 angular source·outcome이 별도 조건이다. 이 미래 extension들은 이미 채택한 순간 endpoint 결과를 막는 선행 gate가 아니다.
- `REPRODUCE.md`는 실행 당시의 이름과 미래의 별도 승인된 unique attempt-name을 구별한다. 기존 execution receipt를 덮어쓰거나 새 실행을 자동 허용하지 않는다.

## 중앙 DAG의 실제 비교

원본 `rei_source/CENTRAL_DAG.json` SHA256은 `16443df7e62bea2ac9b6be733e7394cf6f7daffab9546dbceb9e2e2d48d9dced`이다. 비교 결과 기존 **87개 node의 contract·dependency·conditional prerequisite·budget·source fields**, **17개 integration edge**, 그리고 모든 non-node top-level 역사 자료가 구조적으로 정확히 같다. 기존 node에서 바뀐 것은 다음 세 wrapper의 `current_status`와 추가 `current_observation`뿐이다.

| 기존 wrapper | 현재 관측의 범위 |
|---|---|
| REI-EXP-SCENARIO | 동결된 GRID044 순간 endpoint 시나리오 |
| REI-EXP-EVENT-CONSUMER | endpoint PASS, 다른 channel OPEN |
| REI-EXP-OPACITY-CONSUMER | endpoint binding PASS, history OPEN |

88번째 child `REI-GRID044-ENDPOINT-BINDING-01`만 추가되었다. 세 dependency는 모두 기존 node에 연결된다. REI-L4와 V6 owner 원계약·상태를 포함하여 다른 기존 wrapper는 바뀌지 않았다. Top-level과 child의 `L4_ready=false`, `global_physical_completion=null`을 유지한다. 기존 budget의 reset·transfer 및 unused balance에 의한 새 실행 허가는 모두 false이다.

## 과학 판정과 범위의 보존

새 문서는 실제 저장 상태와 처방된 두 continuum의 순간 photo-only counterfactual임을 명시한다. 13 event owner와26 source contribution,21 material state와25 source output/25×23 J를 구분한다. Primary kinetic energy를 thermal heat로 바꾸지 않고, HE 물리 열화·새 BASS 흡수 four-force/stress·live geometry feedback·연속 VigilODE domain/error control을 OPEN으로 유지한다. Caller witness가 native FP 인증은 아니라는 제한도 일치한다.

`consumer.py`, 검사·bounded wrapper·렌더러·Rust 생성기 및 client, `ACTUAL_STATE_BINDING.json`, `results.json`, `RESOURCE_RECEIPT.json`, client contract와 직접 확인했던 PNG 등 **11개 과학 검토 대상의 byte count와 SHA256이 이전 독립 검토 시점과 모두 같다**. 새 문서의 physical source 값은 저장 results와 같고 science2.900492 CPU/2.940682361000654 wall, infrastructure14.682127000000001 CPU/14.797034617000463 wall 누적도 그대로다. 실패한 compiler probe를 제거하지 않았으며 역사적83·new83·NCP·GRID044/PR221 IVP를 재실행하지 않았다.

`NEXT_SELECTED_BINDING.md`와 `HANDOFF_KO.md`는 다음 H1 energy-resolved source 및 실제 stopping provider의 수신을 우선한다. 저장 Gamma/P/K에서 spectrum을 임의 생성하지 않으며, 선택하지 않은 전체 핵·분자 반응을 필수 AND gate로 추가하지 않는다. 다음 과학 단위의 예산은 아직 동결되지 않았고 이 검토가 새 실행을 승인하지 않는다.

## 최종 검토 파일 식별자

| 파일 | SHA256 |
|---|---|
| `SCENARIO.json` | `94af0c3a813ba2f7d6e14059d7720fb34d764d14d5972b1e87e60c11b8e60c92` |
| `SCIENTIFIC_DECISION.json` | `452dd8c25664f86adae65ab71c121eb99e19f68be342f8b0b6d97b64bfa6bd9f` |
| `REPORT_KO.md` | `1779f5979f9744e64d73f104220cc2e35a3b56312e8663be39dfd1f259c0ff6f` |
| `NEXT_SELECTED_BINDING.md` | `a993b59fba47d9c968b6e48bb7307878f2e215d7b25fd016a1050149ac9738bb` |
| `HANDOFF_KO.md` | `5dfbae64fdf97557fc39297fb2e0646b1edcf7cb9cc5948d2d27c184619e80bd` |
| `REPRODUCE.md` | `ce073934a199fcb0bd676620ab3b677eb26a311c6fb938e9fb09ab151bf72a80` |
| `DAG_DELTA.json` | `82310478ce1b80ed4936d6a889dc13f0f9f21d0b144d673f70ed451ab40b398f` |
| `DAG.json` | `125a3e71dd2cafc99bba299aed6fecd9ef9326b309031f09594d4de469b0091b` |
| `REI_GRID044_ENDPOINT_20261025.json` | `fb2c7ba7dac4a1177bf8fde2465ec7b87ceb8e0a2f16e6a2a239e2f479d53d91` |

구조 비교의 모든 항목과 보존된 과학 파일 식별자는 `METADATA_DAG_REVIEW.json`에 기록했다. 이 addendum을 원본 과학 검토와 함께 읽으면 초기 SCENARIO 누락은 해결된 metadata 항목이다. 과학적 수정·재실행 요청은 **0**이다.

## 게시·백업 단계와 구분

이미 승인된 additive expected-SHA publication 단계로 진행해도 된다. 이 문서 자체는 push·source ZIP·최종 Dropbox/Drive ACK의 완료 영수증이 아니다. Root가 각 노드 전 fresh AGENTS/HEAD/병렬 반환/backup을 확인하고 실제 delivery receipt를 별도로 기록해야 한다. Metadata·텍스트·hash 검사 overhead는 별도 계측하지 않았으며 0으로 산정하지 않는다.

## 파생 CURRENT_STATUS view 추가 확인

**PASS_SCOPED_CURRENT_STATUS_VIEW.** 게시 전 발견된 현재 상태 index의 정합성을 좁은 범위에서 추가 검토했다. 원본 `rei_source/CURRENT_STATUS.json`의87행 중84행은 데이터가 정확히 같고, 위 세 REI-EXP 행은 `current_status`와 `observation`만 바뀌었다. 기존 모든 `source_file`과 `json_pointer`는 보존되었다. 동일 schema의 endpoint child 한 행을 끝에 추가하여88행이 되었다.

88개의 ID·순서·status가 이미 검토한 현재 DAG와 전부 일치하고, 바뀐 세 행 및 child의 observation도 DAG의 current_observation과 같다. DAG 자체의 SHA256은 이전 검토와 동일하다. 새 과학 코드·suite·provider·IVP 검사는 수행하지 않았다.

- 원본 current view SHA256: `f41bf62a16af899cdf97ee81dd35b7862006ab38ae5b9107a7b74cc479dd74a2`
- 최종 `research/orchestration_expansion_20261025/status/CURRENT_STATUS.json` SHA256: `0f353b680a7e832f12d731c11bcbd7a7fd5c74ae83ffd4720fc2e6c959b95320`
- 저장 자료 비교9항목 모두 통과. 추가 과학 실행0, 예산 reset/transfer0.

이 확인은 전달 단계의 current-state index 모순을 해소하며 기존 endpoint scoped PASS와 L4/global gate를 바꾸지 않는다.
