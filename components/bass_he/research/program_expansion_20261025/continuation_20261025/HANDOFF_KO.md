# BASS_HE 후속 연구 인계 — HE-EXP-INTAKE-01

이 파일은 고정 인계 c456b05e0f1c53faa3ae36720826f43e57c06a91의 후속 기록이다. 과학 소스·원자료·검증의 불변 기준은 source S `965da72aa7a5e885e12956fafadfb8dc2519b81f`이며 중앙 관찰은 central C `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`에 게시·readback 검증되었다. 소스 ZIP의 Dropbox/Drive 성공 ACK와 후속 metadata size가 모두 확인되어 이 단위의 전달 상태는 `APPROVED_SCOPED_DELIVERED`다. 실제 게시·보존 근거와 확인 범위는 `delivery/PUBLICATION.json`, `delivery/BACKUP_ACK.json`을 따른다.

## 먼저 읽기

1. 현재 AGENTS.md, research/program-expansion-20261025의 실제 HEAD, HE101 owner research/he-ang-finitemass-cba-20261025의 실제 HEAD, 다른 owner PR과 WU/REC/CR 입력 변화.
2. RESULT.json, RESULTS_KO.md, DAG.json, LOOP_PROGRESS.json.
3. evidence/validation/RESOURCE_LEDGER.json, pair_source/reviews/INDEPENDENT_REVIEW_FINAL.json, exchange/PAIR_INDEPENDENT_REVIEW.md.
4. species/SPECIES_PROVIDER_REGISTRY.json, species/EXPLICIT_TRANSPORT_SOURCE_INVENTORY.json, sources/SOURCE_PROVENANCE.json.
5. pair_source/SELECTED_H_HE_SOURCE.json, pair_source/THEORY_KO.md, exchange/THEORY_KO.md.
6. evidence/inherited/HE101_RESOURCE_LEDGER.json 및 HE101_CLAIM_GATE.json; 소진 비용과 열린 C8을 그대로 보존한다.

## 재사용할 완료 결과

- WU32 supplied rows: atomic charge20+n1+electron pool2+synthetic extension9. 합성 확장을 실제 공급자로 승격하지 않는다.
- 실제 elemental scalar provider18(PI6/RR6/CI6), explicit transport27pairs/243Q expressions. Thermal-integral/DCS/joint-law 타입을 유지한다.
- H–He9Q행 및 기존Q11/Q22 일치. source Tstar50–50000K, 외삽0, 새fit평가0.
- 조건부 finite-mass moment map, Maxwell heat/linear drag 유도, thermal count/Cv/internal/binding/nonthermal ownership, common-bulk drift tensor 구현.
- 31 distinct methods에 대한 최종 scoped evidence. 실제36method-executions/5process outcomesPASS/PASS/PASS/FAIL/PASS. 원04FAIL은1ULP exact-equality oracle 문제이며05는해당1method만PASS. 원failure code/test bytes도04디렉터리에 보존.
- 검증 실행 구간 CPU0.282464889/wall0.280453644998488s, cap8/30, repairused1/verificationcontinuation1. 준비·모델·provider·IO는 별도이며 UNKNOWN_NOT_ZERO를 보존한다. 기존 allocation을 새 이름으로 초기화하지 않는다.
- Source compiler249-check, HE34/35, HE101 suite 재실행0. HE101C8PARTIAL_EXPORT/19of20/reserve0/actualPASS_FAIL_FAIL은 그대로다.

## 정확한 다음 작업

WU의 실제 isotope/state/mass 자료와 선택된 H–He source label의 대응을 결정하고, 선택 Tstar에서 실제 Qbar11 값과 calibrated source uncertainty를 공급한다. 준비된 pair_source/conditional_h_he_moments 인터페이스는 그 입력을 받는다. 물리적 평가에는 해당 source-validity 계약과 별도 명시 수치 allocation을 먼저 고정한다. 위 구현 검증의 남은 초를 physical campaign 예산으로 바꾸지 않는다.

조건부 유도:
Tstar=(mbTa+maTb)/(ma+mb), mu=mamb/(ma+mb),
gbar=sqrt(8kBTstar/(pi mu)),
G=4kB na nb mu/(ma+mb) gbar Qbar11,
Qa=G(Tb−Ta), Qb=−Qa,
K=(4/3)na nb mu gbar Qbar11.
열식은zero drift, K는small-drift1차다. Finite-drift O(U²) heating은 별도 same-event 분배를 필요로 한다.

다음 source가 scalar rate/thermal integral만 제공하면 full differential law나 recoil cross moment를 채우지 않는다. Mass number A를 kg mass로 사용하지 않는다. REC-HD parser는 REC owner가 제공하며 p/o-H2, exact50/100/200K와 미확정 vibrational state를 유지한다. WU nuclear/weak daughter payload와 CR stopping은 선택한 채널에서만 조건부 의존한다.

열 count는 thermal pool의 Gamma_th다. Nonthermal birth를 즉시thermal count/heat로 더하지 않는다. Population-derived binding/internal/rest energy의 derivative witness와 별도 evolved RHS를 중복 소유하지 않는다. Common-T/u reduction은 실제 시간척도·관측량 오차가 필요하다.

## 게시와 보존

검증된 확장 경로만 additive 갱신하고 expected SHA/force=false를 사용한다. HE101 owner나 다른 owner branch를 수정하지 않는다. 소스 ZIP은 이 작업의 재현 가능한 소스·입력·검증 패키지이며 전체 저장소 Git history archive는 아니다. 두 provider 성공 응답·ID·size를 확인한 뒤에만 이중 백업으로 표시한다. 원 source PDF는 공개 재배포하지 않는다.

physical_provider_admitted=false, global_physical_completion=null, L4_ready=false, production=NOT_APPROVED, activation=false를 유지한다.


## 실제 전달 영수증과 상태 해석

- Source S: `965da72aa7a5e885e12956fafadfb8dc2519b81f`, tree `ea66060e77b9a6fea4b7de9ccae046a200bb3ffd`. BASS_HE `research/program-expansion-20261025`에서 expected parent `c456b05e0f1c53faa3ae36720826f43e57c06a91`, force=false로 게시되고 HEAD readback 및 87개 Git blob 일치가 확인되었다.
- Central C: `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`, tree `f803d76227190767a4771a5fa927c7f61d4291d2`. `research/orchestration-sandbox-20261022`에서 expected `78f7ac5864d5817ceb79b48cb5e298cc30006510`, force=false로 게시되고 HEAD readback 및 변경 14개 Git blob 일치가 확인되었다. 바뀐 것은 5개 HE-owned wrapper의 상태·관찰 및 그 대응 뷰다.
- Source ZIP: `BASS_HE_HE_EXP_INTAKE01_SOURCE_20261025_965da72a.zip`, **1013057 bytes**, SHA256 `0405ee8803dfaa72a6a54a8bc005376c79c15e5eecf95f23a50582ec0fc49ef9`. S의 87개 소스 파일과 archive context 2개, 총 89개 member를 보존한다. 전체 저장소 또는 전체 Git history의 archive는 아니다.
- Dropbox: ID `id:BSpOijBcT10AAAAAAEAbGA`, rev `65eaa1ee52f820af03d47`, path `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_HE_EXP_INTAKE01_SOURCE_20261025_965da72a.zip`. 업로드 성공 ACK와 후속 metadata의 1013057 bytes를 확인했다.
- Drive: ID `1yANHEfXKlBQqMX5PbLvty_Fdm_C1_kgf`, parent `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, URL https://drive.google.com/file/d/1yANHEfXKlBQqMX5PbLvty_Fdm_C1_kgf/view?usp=drivesdk. 업로드 성공 ACK와 후속 metadata의 1013057 bytes를 확인했다.

SHA256는 로컬 archive 무결성 영수증의 식별자다. 두 provider의 전체 ZIP 재다운로드 또는 provider가 반환한 원격 cryptographic checksum 검증을 주장하지 않는다. 전체 원 영수증은 `delivery/SOURCE_ARCHIVE_RECEIPT.json`, 87개 원격 source blob 확인은 `delivery/SOURCE_REMOTE_VERIFICATION.json`, 최신 관찰 입력은 `delivery/PREFLIGHT.json`, 중앙 독립 검토는 `delivery/central/INDEPENDENT_REVIEW.json`에 보존한다.

소스 ZIP은 **S 시점의 역사적 snapshot**이다. 그 안의 RESULT `APPROVED_SCOPED_DELIVERY_IN_PROGRESS` 및 R10/C10 `in_progress`는 당시 상태로 보존되어 있다. 현재 상태는 이 파일과 RESULT/LOOP_PROGRESS 및 `delivery/` metadata overlay로 읽는다. 과학 소스·측정·실패 원문을 이 상태 변경 때문에 다시 쓰거나 재실행하지 않는다.

이 overlay를 게시할 후속 metadata-tail D의 실제 commit SHA, D ZIP identity와 두 provider ACK는 실제 생성·확인 후 **BASS_HE PR102 외부 영수증**에 기록한다. 자기 commit 안에 자신의 미래 SHA를 넣지 않는다. 이 기록 시점에는 D SHA/ZIP/ACK를 예측하거나 D tail backup이 완료되었다고 주장하지 않는다.

## 다음 연구 thread에 전달할 정확한 지시

1. 현재 AGENTS, 실제 expansion/HE101 owner HEAD와 열린 owner PR을 다시 읽고 `delivery/PREFLIGHT.json`의 관찰값과 비교한다. 과학 근거는 source S `965da72aa7a5e885e12956fafadfb8dc2519b81f`, 중앙 관찰 근거는 C `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`로 유지한다. source ZIP의 과거 in_progress를 현재 상태로 덮어 읽지 말고 최종 delivery metadata overlay를 적용한다.
2. PR102의 외부 영수증에서 root가 실제 기록한 D commit, D ZIP bytes/SHA256 및 provider ACK를 확인한다. 영수증이 아직 없으면 미확인으로 남기고 미래 SHA나 tail backup 완료를 만들지 않는다.
3. 다음 과학 작업은 H–He source label과 실제 isotope/state/mass의 대응, 선택 Tstar의 실제 Qbar11 값, calibrated source uncertainty를 고정하는 것이다. 이것들은 여전히 physical binding pending이다. 현재 조건부 구현의 검증을 물리 공급자 승인으로 승격하지 않는다.
4. 물리 평가 전 source-validity 계약과 별도의 명시 수치 allocation을 고정한다. Physical allocation은 아직 UNALLOCATED다. 기존 8 CPU/30 wall cap과 사용된 repair1/verification continuation1을 새 이름으로 초기화하거나 남은 시간을 physical campaign 예산으로 돌리지 않는다. 변경되지 않은 과거 suite·HE101·compiler를 재실행하지 않는다.
5. HE101 owner `28a26f4db951ab9085180e2ecc5d600d981a1f71`의 C8 `PARTIAL_EXPORT`, 19/20, repair reserve0, 실제 PASS/FAIL/FAIL 및 누적 ledger를 유지한다. 이 source-intake 단위의 R10/C10 완료는 HE101 C8 완료를 뜻하지 않는다. WU/REC/CR 소유권과 입력 타입, thermal/nonthermal count 및 에너지 소유권 경계도 유지한다.
6. `physical_provider_admitted=false`, `production=NOT_APPROVED`, `activation=false`, `global_physical_completion=null`, `L4_ready=false`를 유지한다. 새로운 물리 주장·수치 실행은 해당 frozen contract와 독립 authority 판단을 따로 받아 진행한다.
