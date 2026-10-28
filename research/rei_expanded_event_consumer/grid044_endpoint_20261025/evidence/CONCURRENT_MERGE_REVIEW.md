# HE 동시 게시 관측의 독립 병합 검토

## 판정과 범위

**PASS_SCOPED_CONCURRENT_HE_OBSERVATION_MERGE** — reviewer `/root/rei_baseline_intake`.

최초 ref-update에 GraphQL UNKNOWN이 반환된 뒤 root의 fresh readback에서 중앙 HEAD `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`가 관측되었다. 이는 HE source `965da72aa7a5e885e12956fafadfb8dc2519b81f`의 별도 관측 게시다. 준비했던 endpoint commit이 HEAD가 되었다고 간주하지 않는다. 이번 검토는 저장된 incoming delta·HE status·current view와 우리 병합 전/후의 DAG·current view만 비교한다. 이전 과학 검토를 재실행하지 않으며 과학 suite·provider import/callback·IVP 호출은0이다.

## 두 작업 계보의 보존

병합 전 우리 DAG와 CURRENT_STATUS snapshot의 SHA256은 앞선 독립 `METADATA_DAG_REVIEW`에서 검토한 정확한 hash와 같다. 이 snapshot을 기준으로 다음을 확인했다.

- 변경된 DAG node는 HE-EXCHANGE, HE-RESERVOIR, HE-CLOSURE, HE-EXP-PAIR, HE-EXP-CLOSURE의 **다섯 개뿐**이다. 각 변경은 incoming의 `current_status`와 `status_observation`을 정확히 보존한다.
- 우리 세 REI wrapper와 endpoint child는 **데이터가 정확히 같다**. 다른83개 pre-merge node도 그대로다.
- 원래87개의 contract·dependency·budget·source fields,17 integration edge와 모든 non-node top-level 역사 자료가 보존되었다.
- incoming87행 current view 중 우리 세 REI 관측 외 **84행은 정확히 동일**하다. 우리 세 행과 child도 pre-merge와 정확히 같고, 최종88개 ID·순서·status가 merged DAG와 일치한다.
- incoming HE observation의 값은 저장 owner-status의 각 해당 JSON object와 정확히 같다. 새 관측의 source pointer를 다른 근거나 현재 endpoint 채택으로 바꾸지 않았다.

## 과학적 gate와 비용

HE의 `physical_provider_admitted=false`, `activation=false`, production `NOT_APPROVED`, allocation `UNALLOCATED`를 그대로 유지한다. HE101 C8는19/20, reserve0이며 HE101 START를 수행하지 않았다는 owner 기록도 보존한다. 새로운 conditional finite-mass/ownership 구현 관측은 현재 endpoint의 물리적 degradation·thermal heating 채택이 아니다. Owner의 기존 검증 횟수·실패·비용은 해당 owner 계보에 속하며 endpoint의41개 검사나 예산에 합산하지 않는다.

Merged DAG, endpoint child, HE source intake의 `L4_ready=false`, `global_physical_completion=null`은 유지된다. 새 실행 허가나 기존 예산 reset/transfer는 발생하지 않았다. REPORT_KO/HANDOFF_KO에 추가된 동시 반환 설명도 이 범위와 일치한다.

## 게시 기준과 전달 경계

새 publication parent는 `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`, tree는 `f803d76227190767a4771a5fa927c7f61d4291d2`로 정확히 기록했다. 이 리뷰는 local merged 자료의 정합성 판정이며 retry의 HEAD 도달 또는 백업 완료 영수증이 아니다. Root는 이 fresh base tree를 사용하여 다른14개 HE owner 파일을 보존하고, 실제 expected-SHA ref 갱신·source ZIP·dual ACK를 별도로 확인해야 한다. 이미 승인된 publication workflow 범위에서 진행하면 되며 추가 과학 실행은 필요 없다.

## 비교 증거

저장 자료 비교 **21항목 모두 통과**했다. 아래 식별자와 세부 boolean 비교는 `CONCURRENT_MERGE_REVIEW.json`에 보존했다. 이 additive review는 이전 review의 당시 hash·판정을 덮어쓰지 않는다.

| 파일 역할 | SHA256 |
|---|---|
| original_DAG | `16443df7e62bea2ac9b6be733e7394cf6f7daffab9546dbceb9e2e2d48d9dced` |
| pre_merge_DAG | `125a3e71dd2cafc99bba299aed6fecd9ef9326b309031f09594d4de469b0091b` |
| pre_merge_status | `0f353b680a7e832f12d731c11bcbd7a7fd5c74ae83ffd4720fc2e6c959b95320` |
| incoming_delta | `9419e77d623c5887d3565dcbe803b991e7a2cb722c9f67aeaa792bab4794781e` |
| incoming_status | `5507082e718ce2b7796b7c8625a0317cfe2dee49c247e2b53981a219e6e3d6c8` |
| incoming_HE_status | `9dc21834a2a6074dc1739979a8e98add975b07f3188f7ea626c2dcae601cada6` |
| merged_DAG | `0565402991c3597946279330594a914e638f483dde48813dd8d15ea00c77c3c3` |
| merged_status | `d1664a8dea7481eadd044fb670ab6fa37e201380f88d21d95aaaffefce639f93` |
| unit_DAG_delta | `f3cb09afc244e73056a87792d68ab7517d727d3815aa1950a1be96f8ab179d4f` |
| report | `ecd14a9b5d7cef4399343d5087b5db46901cd759868d61c63a3fce944b69fd65` |
| handoff | `bed00b3768bb7b6872a961ae6bea95766a53804fe057598aaeee049f0852855e` |

Metadata·hash·텍스트 비교 비용은 별도 계측하지 않았고0으로 주장하지 않는다. 과학 실행0, 과학 코드 변경0, 예산 reset/transfer0이다.
