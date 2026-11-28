## HE-EXP-INTAKE-01: 소스 입력과 조건부 교환 구현

전체 구성 대상을 종·전하·상태·전자 pool로 추적하면서 실제 공급자의 quantity와 적용 범위를 보존한다. 이 변경은 typed source intake, 유한질량 angular-moment/Maxwellian exchange, 열용량·입자수·단일 에너지 소유권 adapter를 추가한다.

- 소비자 32행: 원자 전하 상태20 + neutron1 + electron pool2 + 합성 확장 witness9. 합성 자료를 실제 물리 공급자로 승격하지 않는다.
- 실제 scalar provider18(PI6/RR6/CI6), 명시적 transport27pairs/243 thermal-Q expressions, H–He9Q행을 고정 원자료에서 추출했다. Thermal integral은 DCS나 joint law로 해석하지 않는다.
- H–He는 Tstar50–50000K의 소스 입력, zero-drift heat 및 linear-drift drag의 조건부 유도/구현까지 승인한다. isotope/state/mass, 실제 Q값·source uncertainty 결합은 열려 있다.
- Raw-to-central heat, thermal/fast particle-count, Cv, binding/internal/nuclear/nonthermal/radiation/escape의 단일 ownership을 구현했다. Common-T/u reduction 및 물리 공급자·production 승인은 보류 상태다.

### 검증과 실패 보존

31개 고유 메서드, 36회 메서드 실행, 실제 process outcomes **PASS/PASS/PASS/FAIL/PASS**. 독립 검토에서 유한 질량합 overflow 반례를 찾아 안정화했고, 수정 검증의 1ULP exact-equality FAIL을 원 코드·test·raw와 함께 보존했다. 독립 반올림 오차 경계에 근거한 oracle 수정 후 그 한 메서드만 PASS했다. 최종 전체 suite 재실행을 주장하지 않는다.

새 구현 검증의 측정 구간 CPU0.282464889s/wall0.280453644998488s; cap8/30s, child RLIMIT_AS256MiB, repair1/verificationcontinuation1. Child startup은 포함하고 parent startup/hash/prestart/postfinish/remote/model/IO는 제외한다. End-to-end cap 준수 주장은 없다. HE101 START·기존 과학 suite replay·새 physical campaign은0.

[최종 과학 독립 검토](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/pair_source/reviews/INDEPENDENT_REVIEW_FINAL.json) · [중앙 변경 독립 검토](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/delivery/central/INDEPENDENT_REVIEW.json)

### 실제 게시

- 소스 S: [965da72aa7a5e885e12956fafadfb8dc2519b81f](https://github.com/cosmosapjw-quantum/BASS_HE/commit/965da72aa7a5e885e12956fafadfb8dc2519b81f); task snapshot87파일 Git blob 일치.
- 중앙 C: [fc2c6044b5e9eb08e0e0486c17d1987c7099df9c](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/fc2c6044b5e9eb08e0e0486c17d1987c7099df9c); 변경14파일 Git blob 일치. 87노드 중 HE5개의 상태 관찰만 갱신하고 다른82노드·원계약·예산·토폴로지를 유지했다.
- 전달 D: [ac6042a6b0610b09d0576538767ee0299389a5eb](https://github.com/cosmosapjw-quantum/BASS_HE/commit/ac6042a6b0610b09d0576538767ee0299389a5eb); metadata15파일 Git blob 일치.
- 세 게시 모두 expected SHA + force=false, 성공 응답과 실제 HEAD readback을 확인했다. 이 PR은 draft 유지.
- [최종 인계](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/HANDOFF_KO.md) · [결과](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/RESULTS_KO.md) · [R1–R10/C1–C10](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ac6042a6b0610b09d0576538767ee0299389a5eb/research/program_expansion_20261025/continuation_20261025/LOOP_PROGRESS.json)

### 실제 백업

- **SOURCE** `BASS_HE_HE_EXP_INTAKE01_SOURCE_20261025_965da72a.zip` — **1013057 bytes**, 89 members.
  - SHA256: `0405ee8803dfaa72a6a54a8bc005376c79c15e5eecf95f23a50582ec0fc49ef9`
  - Dropbox: `id:BSpOijBcT10AAAAAAEAbGA`, rev `65eaa1ee52f820af03d47`, completed ACK + size 1013057.
  - [Drive SOURCE ZIP](https://drive.google.com/file/d/1yANHEfXKlBQqMX5PbLvty_Fdm_C1_kgf/view?usp=drivesdk), ID `1yANHEfXKlBQqMX5PbLvty_Fdm_C1_kgf`, success ACK + size 1013057.
- **DELIVERY** `BASS_HE_HE_EXP_INTAKE01_DELIVERY_20261025_ac6042a6.zip` — **1792855 bytes**, 33 members.
  - SHA256: `166467272a14a25ba35f4d743fbc3856b78c5d6ac557d5e15b969cd463c233fb`
  - Dropbox: `id:BSpOijBcT10AAAAAAEAc0A`, rev `65eaa6349c4e90af03d47`, completed ACK + size 1792855.
  - [Drive DELIVERY ZIP](https://drive.google.com/file/d/1IodRD1I_sxb1Jld0VAolZMC1suLok4YW/view?usp=drivesdk), ID `1IodRD1I_sxb1Jld0VAolZMC1suLok4YW`, success ACK + size 1792855.

**SOURCE와 DELIVERY 모두 Dropbox/Drive 실제 성공 ACK 및 후속 metadata size 확인 완료.**

소스 ZIP은 S 시점의87개 소스 파일+archive context2개다. 전달 ZIP은 D의15개 HE metadata와 C의14개 중앙 변경 파일, 실제 게시 영수증과 복원 안내다. SOURCE ZIP의 역사적 in_progress 상태는 D overlay의 최종 전달 상태와 구분한다. 두 ZIP은 함께 이 연구 단위를 복원하며 전체 저장소/Git history archive를 뜻하지 않는다.

ZIP의 SHA256/CRC/member 검증은 로컬에서 수행했다. 각 provider에 대해서는 실제 업로드 성공 ACK와 후속 metadata size를 확인했다. 전체 원격 ZIP 재다운로드나 provider-returned cryptographic checksum 검증을 주장하지 않는다. D 안의 미래 D SHA/ZIP/ACK null은 자기 참조 방지를 위한 작성 당시 기록이며 이 실제 외부 영수증으로 결속한다.

### 보호 상태와 다음 물리 입력

HE101 owner28a26f4db951ab9085180e2ecc5d600d981a1f71, C8 PARTIAL_EXPORT,19/20,reserve0, 기존 PASS/FAIL/FAIL과 누적 비용은 그대로다. 이번 R10/C10 완료는 HE101 C8 완료가 아니다.

physical_provider_admitted=false, global_physical_completion=null, L4_ready=false, production=NOT_APPROVED, activation=false. 다음 단위는 선택된 H–He의 isotope/state/mass 대응과 실제 Qbar11 값·교정된 source uncertainty를 source-validity 계약 및 별도 수치 allocation으로 고정하는 것이다. 완료된 scoped 근거와 기존 예산 이력은 재사용한다.


### 병렬 중앙 작업의 후속 관찰

중앙 후속 [ad9c0e29453fcb6d66637413b51bf42f08688cf1](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/ad9c0e29453fcb6d66637413b51bf42f08688cf1)은 C를 직접 parent로 갖고 REI-GRID044-ENDPOINT-BINDING-01을 추가했다. 해당 commit의 CURRENT_STATUS88행에서 이 단위의 HE5개 관찰과 HE101-EXPORT가 C와 동일하고, HE 관측 원문 blob도 동일함을 확인했다. 본 DELIVERY ZIP의 중앙 부분은 고정 C14파일 snapshot이다. 이후 연구는 최신 중앙 HEAD/AGENTS/병렬 작업을 확인하며 이 후속 진척을 보존한다.

<details><summary>이전 확장 계획 게시 기록</summary>

기존의 제한된 역할을 전체 구성 대상 핵종·동위원소·이온과 인접 source/emission/absorption 연구로 확장하고, 이 저장소가 소유할 과정과 소비자 인터페이스를 명시합니다.

다음 과업: 대상 종 전체의 미분 충돌·유한질량 열화와 에너지운동량 교환 계약을 진행하고 소진한 HE101 예산은 보존한다.

고정 중앙 계약: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/641a725ada4be27473069c2c35005a94c2ab0248/research/orchestration_expansion_20261025

검증: 독립 검토된 87-node DAG, 기존40계약/17연결/31반환 보존, source-pointer 일치 및 순환 없음. 이 PR은 검토된 연구 계획·역할·인계 문서의 추가입니다. 새 과학 실행은 이 저장소에서 수행하지 않았습니다.

전체 물리 완료율은 null, L4는 false. 새 예산 미배정과 과거 소진/불명 예산을 그대로 보존합니다. 기존 owner 브랜치를 수정하지 않는 별도 draft이며, merge와 force push는 수행하지 않습니다.

</details>


