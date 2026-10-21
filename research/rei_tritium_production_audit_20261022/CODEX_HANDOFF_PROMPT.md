# Copyable continuation prompt

```text
cosmosapjw-quantum/rei_bianchi의 research/rei-isotope-quotient-pilot-20261022 (Draft PR219)에서 이어가라.
AGENTS.md와 research/rei_tritium_production_audit_20261022/의 HANDOFF.json, NEXT_DAG.json, NUCLEAR_NETWORK_CONTRACT.json, NUCLEAR_PROVIDER_INVENTORY.md, review/NUCLEAR_NETWORK_DECISION.json, delivery/FINAL_DELIVERY_ACK.json을 먼저 읽어라.
공개 repo/백업에서 필요한 파일을 직접 취득하라. 사용자에게 업로드나 수동 다운로드를 요구하지 말라.
기존 T=0은 초기조건과 literal-zero lift 때문에 생긴 구조적 결과였다. 18개 반응군의 조건부 계산은 PASS_SCOPED이며, authoritative T/n은 NUCLEAR_NETWORK_HISTORIES.npz의 log_T_n이다. 누적 생성·소멸의 차이를 잔존량으로 대체하지 말라.
완료된 DD·18반응군 계산, 기존 83개 배경 IVP와 28개 검산을 재사용하고 변경 의존성만 검증하라. 실패한 사다리꼴 결과와 수정 이력도 보존하라. 과거 NCP 예산·deadline을 초기화하지 말라.
다음 목표는 isotope-native ionic solver에 핵반응 딸핵·전자·에너지 투영을 실제 연결하는 것이다. 고속 중성자/triton 감속, 광자·중성미자 에너지 분배, Li6 부분 단면적 및 저온 공급자 근거를 병렬로 확보하라. 기존 all-bare/즉시 열평형 민감도와 물리적으로 결합된 production 결과를 구별하라.
physmath-research-loop로 해당 단위의 이론→코딩을 수행하라. 가능하면 Astra/high가 계약·독립 판정을, Sol/high가 구현·bounded 실행·게시를 담당하되 실제 사용 가능한 모델과 관측한 실행 정체성을 기록하라.
production 개발과 통제된 실행은 이미 승인됐다. 기존 단일 에너지 소유권과 허용오차를 유지하고, 미완료를 완료로 승격하지 말라. 각 완료 단위의 DAG·검토·push·이중 백업을 갱신하고 다음 실행 가능한 의존성으로 이어가라.
```
