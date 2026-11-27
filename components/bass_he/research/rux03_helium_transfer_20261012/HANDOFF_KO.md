# 다음 최소 작업: HERE_RUX03_EVENT_BRIDGE_02

이번 패킷은 BASS_HE의 RUX00 입력·원자 owner 정리와 RUX03 재결합 사건/광자 응답 유도·screening 결과다. 시작할 때 review/DECISION.json의 실제 scope를 읽고 SOURCE_AUTHORITY_LOCK.json의 실행 입력과 source를 사용한다.

## 바로 사용할 입력

선택은 physical_provider_20261010의 warm HM12 extended, 10–50000 eV, 2904 nodes, 17 epochs, 초기 50000 K, elapsed 0–1e11 s다. screening/inputs/extended_dataset.npz와 extended.json을 함께 쓴다. base의 10–200 eV/1984 nodes 및 다른 He III 초기값을 섞지 않는다. 실제 thermal 경로는 FT03 Case A escape다. PHYSICAL_INPUT_ADMISSION.json, ATOM_OWNER_MATRIX.json, RATE_DOMAIN_MAP.json이 단위와 source의 계약이다.

## 다음 실행자가 수행할 한 작업

rei_bianchi owner의 선택된 RHS에서 기존 warm Case A escape의 사건 bundle을 실제로 한 번 소비하도록 연결한다. 광이온화 event counts, H/He 종 변화, 자유전자 source, RR/DR kinetic cooling, binding energy와 escape energy를 같은 clock/volume 단위에서 조합한다. 유도식은 theory/HE_RECOMBINATION_TRANSFER_KO.md를 그대로 사용하고 raw Grackle rate를 actual FT03 callback으로 오인하지 않는다.

새 native interval을 수행한다면 먼저 선택된 source·clean build·실행 binary를 같은 immutable identity로 묶고 stage evaluation 전 확인한다. 기존 P01의 warm 물리 입력 유무와 이 source/build binding은 서로 다른 문제다. 작업의 결과는 실제 callback 주입 기록 및 영향을 받는 사건·에너지 장부 검증이다. source review 또는 raw coefficient replay만으로 owner RUX03을 닫지 않는다.

이번 frozen response는 밀도와 local E를 고정한 6개 에너지 probe다. 54.42 eV의 문턱 이동을 포함하는 Bianchi 이력 또는 실제 방출 spectrum으로 취급하지 않는다. 실제 source를 넣는 경우 emission time/direction을 포함하는 joint measure 또는 확인된 조건부 kernel을 쓴다.

## 계승과 실행 예산

B1의 PROMOTE_SCOPED_PYTHON, PR113의 저장 RCT exposure, P03A finite-grid cap은 그대로 재사용한다. 이번 ratio와 uniform-birth 응답만 새 계산이다. completed 11-history campaign, B1 refinement, PR113 36-call campaign, P03A를 새 이름으로 다시 실행하지 않는다. P02A 5000 K coefficient parity가 cold history의 승격은 아니다.

RCT의 직접 전자 source는 0이지만 photon mean energy/heat/spectrum은 scalar rate에서 얻을 수 없다. diffuse source가 실제 필요한 관측량을 정한 후 eta_j(E) 또는 검증된 response moment를 공급한다. 기존 세 폐쇄 구분은 receiver plan에 이미 존재한다. RUX02/RUX03의 독립 작업과 receiver preview는 전체 history 완료를 기다리지 않아도 된다.

현재 새 NCP work unit은 0개다. 먼저 클라우드의 작은 affected calculation으로 비용을 측정한다. 실제로 무거운 일만 기존 승인 범위의 NCP 경로에 넘긴다. E13C11은 관측량 필요가 생길 때만 재개한다.
