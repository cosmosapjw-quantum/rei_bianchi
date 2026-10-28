# 기존 연구 스레드에 전달할 최종 인계문 — 2026-10-28

각 코드 블록을 해당 기존 스레드에 복사한다. 이 문서는 게시 전 template 문구를 정리한 현재 인계다. 새로운 스레드 개설이나 메시지 자동 전송은 수행하지 않았다.

중앙 H–Li 동기화: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/f7e4b73a6f7736166e85fa012cbd53bbb3b59f94/research/h_li_species_completeness_20261028
WU 식별 목록 정본: https://github.com/cosmosapjw-quantum/WU088_HH/tree/a3c6802c28be2207de210737940e1a847adf09c6/research/h_li_species_completeness_20261028

검토된 기존 8개 단원에 H–Li 식별/coverage 단원 1개를 추가했다. 정본 DAG는 28/88, 보조 결과는 9개이며 물리 완료율에 합산하지 않는다. 모든 과학 C9는 범위를 한정해 통과했다. 현재 source/backup 완료 영수증은 별도 FINAL_SYNC_ACK.json에 기록한다.

## WU088_HH

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/WU088_HH
이번 H–Li 전달 SHA: a3c6802c28be2207de210737940e1a847adf09c6
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/WU088_HH/pull/151
읽기: https://github.com/cosmosapjw-quantum/WU088_HH/tree/a3c6802c28be2207de210737940e1a847adf09c6/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 식별 목록과 microscopic provider의 정본 소유자.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: R16의 일반 비음수 유리수 cubic 결과를 재사용하고 이번 특수족은 독립 진단으로 취급한다. 다음은 실제 HD 반응 데이터와 명명된 consumer 결속이다. H−/D−/T−와 Li−, 준안정 He−는 각각의 동위원소·전자상태 근거 안에서 provider를 연결한다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## rei_bianchi

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/rei_bianchi
이번 H–Li 전달 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
이번 전달 branch: research/orchestration-sandbox-20261022
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222
읽기: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/f7e4b73a6f7736166e85fa012cbd53bbb3b59f94/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 선택 시나리오·상태 조립·에너지 원장·관측 응답.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: 기존 ON_refined 17-state pilot과 UVB Q=19.381736839571925, 조건부 p=0.003565238159436219를 재사용한다. 사전 고정 redshift tilt 식별성 또는 실제 두-cell 응답이 준비된 노드를 진행한다. 공유 사건 합성 예제를 실제 에너지→UVB 응답으로 승격하지 않는다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## bass_cr

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/bass_cr
이번 H–Li 전달 SHA: 7ee33930472ed40b84461e30daad08c2f92101ff
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/bass_cr/pull/117
읽기: https://github.com/cosmosapjw-quantum/bass_cr/tree/7ee33930472ed40b84461e30daad08c2f92101ff/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 외부 photon/baryon source, 흡수·cascade·stopping.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: 같은-bin high–low를 포함한 2d−C≤L+S를 재사용하고 실제 저장 atom table의 한 K에 정확 capacity를 결속한다. PR116 기존 전달을 보존한다. 추가 핵종의 생성·소멸은 실제 kernel과 isotope mapping이 있어야 하며 A에서 Q나 lifetime을 만들지 않는다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## rec_bianchi

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/rec_bianchi
이번 H–Li 전달 SHA: 6ab99170dc741e9132cba69ee4706d6a886d29f9
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/149
읽기: https://github.com/cosmosapjw-quantum/rec_bianchi/tree/6ab99170dc741e9132cba69ee4706d6a886d29f9/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 전자·분자 준위, 방출·흡수, 열역학 closure.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: HD δ=h(ν−cΔw)와 level2 인쇄정밀도 불가능 결과를 재사용한다. 원래 35Hz 7실패를 보존하며 CDMS/LAMDA provenance를 먼저 대조한다. PR148 ambient derivative와 JOINT-TANGENT 예약을 보존한다. 새 음이온·준안정종의 준위/전이를 isotope-qualified source로 연결한다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## BASS_HE

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/BASS_HE
이번 H–Li 전달 SHA: de6bcbd95d25f9686997ad7eadbd62ea4e917d59
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/103
읽기: https://github.com/cosmosapjw-quantum/BASS_HE/tree/de6bcbd95d25f9686997ad7eadbd62ea4e917d59/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 충돌·핵반응, 딸입자 birth와 비열적→열적 전달.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: ENDPOINT14와 15 birth-moment rows를 재사용한다. 실제 정규화 packet이 있을 때만 named nonthermal D pool을 결속한다. 두 딸입자의 공분산을 유지하고 birth kinetic energy를 자동 열화하지 않는다. 새 핵 공명과 전자 준안정 상태를 구분한다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## bass

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/bass
이번 H–Li 전달 SHA: 464aff9d95fe596e464e1788c8bebf10ebb2ed5f
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/bass/pull/233
읽기: https://github.com/cosmosapjw-quantum/bass/tree/464aff9d95fe596e464e1788c8bebf10ebb2ed5f/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 물질·복사 응력, geometry·clock·상태 조립.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: 검토된 chemical 6×23 geometry crossblock을 재사용하고 같은 실제 source의 tau RHS 행을 유도한다. PR231/232의 병렬 작업을 보존한다. 새 catalog 요청으로 기존 state array를 자동 확장하지 않으며 입자수·열용량·rest/internal energy 소유권을 유지한다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

## vigilode

```text
$physmath-research-loop를 사용해 이 기존 스레드의 연구를 계속하라.
repo: cosmosapjw-quantum/vigilode
이번 H–Li 전달 SHA: e46704cbc5a1356bd8fd199de09ad26b046acfd4
이번 전달 branch: research/orchestration-blockers-20261028
기존 검토 단원 PR: https://github.com/cosmosapjw-quantum/vigilode/pull/99
읽기: https://github.com/cosmosapjw-quantum/vigilode/tree/e46704cbc5a1356bd8fd199de09ad26b046acfd4/research/h_li_species_completeness_20261028
WU 정본 SHA: a3c6802c28be2207de210737940e1a847adf09c6
중앙 통합 SHA: f7e4b73a6f7736166e85fa012cbd53bbb3b59f94
먼저 AGENTS.md, 실제 최신 HEAD·로컬 변경·병렬 PR·최근 결과를 확인하라. 위 SHA는 고정 인계 기준이며 이후 변경을 덮어쓰지 않는다. 이미 완료된 계산과 검토는 재사용한다.
담당 역할: 수치 오차·metric·capsule·solution enclosure.
H–Li 기록은 NUBASE2020의 26 ground catalog entries와 5 핵 들뜬 상태다. 초기7 이외19개를 추가했으며 미확정/추정 3Li를 확정종으로 취급하지 않는다. 102 formal charge requests, 26 negative requests, 5 qualified anion reference groups, 6 전자준위 예제, 10 분자 후보는 서로 다른 범위다. 이 수를 실제 활성 species나 검증된 rate coverage로 세지 않는다.
기존 20 H–Li atomic charge slots + neutron=21, REI ON_refined17, VigilODE6/30/33을 구분한다. 기존 ElementalElectronicEquality 조건부 provider 근거는 유지하고 새 isotope/state-qualified missing layer와 혼동하지 않는다.
다음 최소 작업: uniform rate-box Γρ²와 별도 δJρ를 재사용한다. 이미 accepted된 native capsule 하나와 실제 u33/query rounding을 결속한다. PR96/97/98의 owner 작업을 보존한다. 6 chemical/reduced30/full33과 새 102 formal requests를 구분하고 서로 다른 weights를 합치지 않는다.
NEXT_NODE_CONTRACTS/PR_PLAN/CLAIM_GATES와 이 저장소 CONSUMER_CONTRACT/REPO_ROLE_PROJECTION을 적용한다. 필요한 source·단위·유효범위·isotope/level·clock·energy owner와 새 누적 예산을 동결한 뒤 준비된 단위만 실행한다. 이전 소모·예약·UNKNOWN 예산은 초기화하거나 이월하지 않는다.
H–Li 검증 첫 실패는 Li7:i8/Li8:i8 원문 끝 공백을 strip한 validator 문제였다. 한 줄만 수정해 16검사가 통과했으며 두 시도와 원문 해시는 보존됐다. 재실행하지 않는다. 미공급 rate/lifetime/Q는 null, 범위 밖 CI/CX는 임의 0·외삽 금지다.
원자/분자 반응의 isotope 보존과 핵반응의 baryon·charge 보존을 구분하고, 물질/복사 응력과 photon·thermal·nonthermal·rest/binding energy 소유권을 유지한다. He2/diproton과 post-2020 coverage는 추가 source gap이며 부재 주장으로 바꾸지 않는다.
이론 R1–R10 → lower-tier 구현 C1–C10 → 다른 검토자의 심사 → expected-SHA/force=false 게시와 source ZIP 이중 백업을 수행하라. fresh83/NCP/대형 IVP·기존 캠페인을 자동 실행하지 않는다. 물리 gate, production/L4, actual whole-domain solution enclosure는 근거가 생길 때만 승격한다.
```

