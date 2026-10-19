# REI BASS-REACTIVE-03 게시 완료·Continuation Handoff

기준일: 2026-10-19 KST. 이 문서는 검증된 과학 소스와 클라우드 게시 영수증을 연결한다.

## 완료 상태

- BASS-REACTIVE-03_POSITIVE_BIRTH = COMPLETE_VERIFIED_SCOPED
- LONGSPAN_SOLUTION = NOT_ADMITTED_FULL_CONVERGENCE_INCOMPLETE
- ISO-COUPLE-P4 = PARTIAL
- SA-01/02, FLRW-CONV, BI-SIGNED, FULL_EOR = HOLD
- TWO_WAY_EINSTEIN_FEEDBACK = NOT_IMPLEMENTED

## 정확한 출발 identity

새 Draft PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/202

새 연구 branch: research/rei-bass-reactive03-positive-birth-20261019

과학 source commit: aa916fd9b30b8c280d193a8e5469af996a04d450

과학 tree: 4eea625089fec600c91869e6624cdd309ceb2f43

부모 PR #201 HEAD: 5a2ae6313ad8ea7b5fdc9b0b2a58009778764b6e

과학 소스는 research/dossier_ssot_sandbox_20261016/bass_reactive03_positive_birth_20261019 아래에 동결했다. 이 별도 게시 디렉터리의 commit은 과학 소스 commit 뒤에 온다. 다음 작업에서 PR의 최신 HEAD와 diff를 실제로 읽고, 위 과학 commit과 게시 commit을 혼동하지 않는다.

원 receiver 97개 파일, physical owner 12개 및 donor owner를 변경하지 않았고, 새 Rust 파일 8개를 추가했다. 새 검증 entry point는 ap/Cargo.toml이다. 기존 branch와 production을 수정하거나 PR을 병합하지 않았다.

## 필수 전체 아카이브

파일: REI_BASS_REACTIVE03_POSITIVE_BIRTH_20261019_4de47e86_FULL.zip

SHA-256: 4de47e86bcb9779a87d1974bf95c6b34ba68936a71486eae6c94475efd9f061f

크기: 7739067 bytes. ZIP entry 386개, outer payload hash 385개, scientific inner payload hash 377개.

Drive: https://drive.google.com/file/d/1bUIZON6cWxO7u7LAxRSc4N8NwjJh0wmE/view

Dropbox: /bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_REACTIVE03_POSITIVE_BIRTH_20261019_4de47e86_FULL.zip

Dropbox content hash: 50334d37b7af6640a5ae6b0fba1ecf99860e382c17db83c05136b0b0ab293abb

두 provider 모두 upload ACK/완료 및 크기를 확인했다. Dropbox provider hash가 로컬 block-hash와 일치한다. 두 provider에서 각각 원시 ZIP을 실제 재다운로드해 전체 SHA-256 일치, 압축 CRC, 두 manifest의 모든 payload 해시 및 실제 압축 해제를 확인했다. 원시 readback 결과는 이 디렉터리의 두 JSON이다.

ZIP 내부 publication/에는 실제 적용 검산한 binary-safe patch와 git bundle이 있다. Patch는 부모 HEAD에서 source tree를 정확히 복원한다. Bundle은 부모 commit을 prerequisite로 가지며 검증 PASS다. ZIP의 전체 crate 실행에는 부모 Git checkout이 필요 없다. Compiler 바이너리는 ZIP에 포함하지 않았다.

## 검증된 정량 결과

- 원 source 384개 cohort의 동결 exact survivor = 1.00111686436201655e-8 reference-comoving m^-3.
- 16개 동결 Nt × birth refinement 사례에서 새 규칙의 최대 survivor 상대차 = 2.220446049250313e-16. 부모 Nt32 GL2/GL4의 −74.50568% / −16.28241% 편향을 이 동결 문제에서 해소했다.
- 실제 source-native 진화: T=8e12 s, 완료 12개 이력·496 macrostep. 계획한 추가 1개 CX 엄격 허용오차 사례는 첫 단계 Cx(WorkLimit), exit2, 결과0행이었다.
- r2, Nt16/32/64/128 생존수 = 1.0038697846883761e-8 / 1.0038242638797143e-8 / 1.0038015923032240e-8 / 1.0037907507400008e-8.
- 형식적 생존수 차수 = 1.00564, 1.06431. 평균 survivor age의 연속 시간 차분 절댓값은 0.941e6, 2.443e6, 4.240e6 s로 커진다. 에너지 가중 q2의 시간 차분도 안정적으로 수축하지 않는다.
- Nt32 r4→8에서 count 상대 변화 약 −1.70e-9, mean-age 상대 변화 −6.6487e-5. 전체 age distribution은 유한 cohort 근사이며 정확하지 않다.
- 단일 분광 비교에서 count +0.0290177%, DI 사건수 −0.0309449%. 전체 분광 수렴 증거가 아니다.
- 독립 native photon/total-energy/species-sum 최대 상대 잔차 = 9.700747050909076e-15 / 1.041528045063209e-15 / 5.183970680370968e-16. 별도 source-energy 분모의 Decimal80 잔차 = 2.185641671044374e-10. 두 에너지 정규화를 혼용하지 않는다.

## 실제 검증과 실패 분류

Rust 1.94.1에서 현재 full tests 209/209, strict Clippy, 추가 파일 scoped rustfmt PASS. Decimal90 65개 scalar 사례, Wolfram, 독립 source/native 검산을 보존했다. Fresh source/empty target에서 209/209와 Clippy를 재실행했고 4개 frozen CSV SHA, 5개 완료 native 이력의160행·8,000과학 셀 exact parity를 확인했다. CX0행도 별도로 재현했다.

OFF는 부모 GL2/GL4와 과학 셀2,368개 exact text parity이며 관측용 read-only cache hit가2개 추가된 운영 차이는 기록했다. 원 CX half-flow와 four-corner timestep 제어기를 변경하지 않았다.

Cx(WorkLimit)는 내부 계산예산 소진이며 물리적 해 부재나 수렴 실패가 아니다. 초기 sample CSV/receipt 불일치와 orphan stream의 원인은 UNRESOLVED로 보존하고 최종 정량 결과에서 제외했다. 이전 실패와 수정 후 실제 재실행 증거를 분리한다. 전체 population vector는 native CSV에 모두 내보내지 않으므로 CSV 양수 audit의 범위를 과장하지 않는다.

## 다음 bounded unit

1. BR04_JOINT_TIME_AGE_CONVERGENCE (NEXT): 물리적·광학적 age 오차 목표를 고정한 Nt × r 교차 계열에서 count, mean, second moment, 에너지 가중 q2와 CDF의 수축을 검증한다.
2. BR04_VARIABLE_OPACITY_THRESHOLD (PENDING): 시간가변 opacity, 이후 blueshift에 의한 문턱 진입과 노드 배치 오차를 분리한다.
3. BR04_BIRTH_ERROR_MONITOR (PENDING, 1번 의존): 원 CX 및 four-corner 제어기의 소유권을 유지하며 opt-in age-distribution error monitor를 연구한다.

상수 방출률과 opacity에 대한 exact/AP 정리를 시간가변 전체 반응계의 보편적 정확성으로 확장해 주장하지 않는다. 원 MD14/BB50k, H/He/D native rates, threshold·binding 구분, 회귀 초기조건과 one-way BASS의 물리적 범위를 유지한다.

## 복원

ZIP 자체 SHA와 ARCHIVE_MANIFEST.sha256를 먼저 검증한 후 README_RESTORE.md를 따른다. 실제 Rust/Cargo1.94.1을 확인하고 새로운 출력·target 디렉터리에서 실행한다. 예: REI_RUN_OUTPUT=/absolute/new-run bash RUN_STAGE.sh all ap_n32_r2

다음 스레드는 $physmath-research-loop로 위 미완료 DAG부터 실제 연구·개발·독립 검증을 수행한다. 기존 PASS를 새 코드에 계승하지 않는다.
