# BR04 Continuation Handoff

**기준일:** 2026-10-19 KST  
**프로젝트:** `cosmosapjw-quantum/rei_bianchi`  
**마지막 완료 단위:** `BASS-REACTIVE-04_TIME_AGE`  
**다음 bounded node:** `BR05_NATIVE_BIRTH_MONITOR_AND_R_PAIR`

## 1. 작업 방식

`physmath-research-loop`로 이론 유도, 실제 Rust 구현, 가벼운 sandbox 검증, 독립 수학·코드·그림 감사, 별도 add-only Draft PR 및 Drive·Dropbox 백업까지 수행한다. SciSpace·Exa·Wolfram을 필요에 맞게 사용한다. 외부 Codex, 사용자 local computing, NCP에 위탁하지 않는다.

기존 production, physical owner, source, 이전 branch·PR을 변경하거나 merge하지 않는다. S10 `budget_native.rs` 계보와 별도 PR #192의 `nested_budget.rs` 계보를 무검증 통합하지 않는다. 중단·환경 교체가 있으면 inventory와 hash·재현 검증으로 복구한다.

## 2. 정확한 Git checkpoint

| 항목 | 값 |
|---|---|
| Draft PR | https://github.com/cosmosapjw-quantum/rei_bianchi/pull/203 |
| Branch | `research/rei-bass-reactive04-time-age-20261019` |
| 최종 HEAD | `a8e550846745fc89e79e84ad32567e3fb556c175` |
| 과학 source commit | `1b5acc89cfbcfa7b42b87255e604f8f86c6a3a01` |
| 과학 source tree | `01f1dffe958f51fceb885f86857eff0bf776d6c1` |
| 부모 PR #202 HEAD | `8e60ecb627da46bb85861e2a4148a1b683d96fb0` |
| 검증된 PR 상태 | Draft, unmerged, 2 commits, 334 added files, 0 deletions |

재개 시 최신 HEAD와 diff를 다시 읽는다. 과학 source commit 뒤에는 원 과학 단위를 수정하지 않는 사후 publication receipt commit만 추가했다.

## 3. 필수 전체 복원 패키지

`REI_BASS_REACTIVE04_TIME_AGE_20261019_ae69c7c9_FULL.zip`

- 크기: **18,943,104 bytes**
- SHA-256: **`ae69c7c912cb918112b96b471a5494a3dea6cc24e265d6a3604af6bed5c103da`**
- ZIP entries: **399**
- 검증된 payload hashes: **398**
- Drive: https://drive.google.com/file/d/1oh_aSpB0Ab-2ewdQJ1UGH3iFFSdO1izN/view
- Dropbox: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_REACTIVE04_TIME_AGE_20261019_ae69c7c9_FULL.zip`
- Dropbox content hash: `7caa310cdae159a3c0d8195cf903e6ec1096eb10f0d0c24df492d379a89a7702`

두 cloud 모두 원시 GET, 별도 폴더 추출, 전체 ZIP SHA 및 payload 398개 검증을 완료했다. Drive의 별도 provider checksum은 노출되지 않았으며 raw SHA 검증은 완료했다. ZIP에는 전체 crate, donor/source, 보존 native 이력, 실제 birth-node CSV, 독립 검산, 실패·복구 기록, source patch와 증분 Git bundle이 들어 있다.

### 명시적인 복구 예외 1개

게시 도중 실행 환경이 교체됐다. 원격 Git에서 326개 파일과 125개 입력 계약을 복구했다. 과학 CSV 7개와 독립 기준 CSV 3개는 원본 bytes/hash와 일치했다. Native 분석 JSON도 보존된 역사 provenance를 명시적으로 재구성하여 원래 SHA와 일치했다.

`evidence/theory/DECIMAL_ACTUAL_NODE_VERIFICATION.json`의 이전 `created_utc`와 정확한 Python 문자열은 복구하지 못했다. 원래 기대 hash는 다음과 같다.

`de8cf30c9da5fb088e0ab20dbba736ce95392cf137afdb3369d339bb2b26e0d5`

전체 ZIP에는 실제 새 실행의 provenance를 가진 검산 JSON을 넣었다. 새 SHA는 다음과 같다.

`5df888e3076e6545483bc8dedaeb5e101efc5934b1bb2210136e5af561f01867`

과학·기준 CSV와 보존된 검산 요약은 새 실행과 일치한다. **이 JSON 한 개의 원본 metadata 바이트가 복구됐다고 주장하지 않는다.** `ARCHIVE_README_KO.md`, `ARCHIVE_SOURCE_IDENTITY.json`, `RECOVERY/DECIMAL_PROVENANCE_REPLACEMENT.json`이 원 계약과 현재 archive identity의 관계를 설명한다.

## 4. BR04에서 실제로 완료한 연구

새 opt-in Rust API `compare_nodes`와 `compare_fitted`는 방출·생존 질량과 조건부 연령 분포의 오차를 분리한다. CDFsup, 1차 Wasserstein 거리 W1, 평균 및 두 번째 연령 moment를 내보내며, zero source·underflow·표현 불가능한 node 배치를 구분한다. 실제 native transport나 controller를 변경하지 않았다.

부모 입력 118개에는 crate 105개가 포함된다. 이 파일들과 원 physical owner 12개, source identity, CX half-flow, S10 four-corner controller는 모두 불변이다. BASS는 여전히 one-way background다.

### 동결 참조

상수 opacity의 생존 연령은 `dμ = j exp(-κA) dA`다. 각 measure의 질량을 따로 기록하고 정규화한 분포의 CDF/W1을 계산했다. 겹치지 않는 같은-label panel은 비정규화 거리의 합/최대값으로 합성하고 전체 질량으로 정규화한다. 겹치는 source label의 합성은 label-weight TV를 포함한 **상계**이며, 정확한 unlabelled mixture 거리가 아니다.

| tau=93, 한 time panel | r=1 | r=4 | r=16 |
|---|---:|---:|---:|
| Survivor CDFsup | 0.2152354382 | 0.0671209749 | 0.0177192053 |
| W1(A/T) | 0.002009860423 | 0.0006178404901 | 0.0001669431599 |

원 source 384 labels, Nt=32에서 정확한 생존수는 `1.00111686436201655e-8` reference-comoving m^-3다. AP r=1→8의 mixture W1 상계는 `3.5196749383e-4 → 5.6983450103e-5`다. GL2/GL4 count bias는 `−74.50568024% / −16.28240889%`를 재현했다. 이 참조를 진화 기체의 절대오차로 해석하지 않는다.

### 새 native 계산: 정확히 두 사례

`ap_n16_r4`, `ap_n64_r4`만 새로 실행했다. 합계 **80 macrosteps, 203.6714초**이며 원 BR03 driver를 사용했다. 공통 설정은 `SIGNED_MINUS`, `grid=121`, `t0=0`, `duration=8e12`, `split=false`, `frozen=false`, `birth_gl=2`, `opacity=4`, `cx_rtol=1e-12`, `cx_atol=1e-14`, `birth_mode=fitted`, `refinement=4`다. 정확한 argv와 binary/CSV SHA는 각 native receipt에 있다.

부모 native 이력 7개를 해시 검증하여 재사용했다. 기존 Nt32r4와 새 Nt16r4/Nt64r4의 형식적 시간 차분 차수는 count 1.0054, mean age 0.4956, second age moment 0.1350, q2 0.0592, DI 0.6565, temperature 1.8187이다. Nt32→64/r2→4 rectangle에서 mixed/time signed ratio는 mean age −4.1268, q2 −6.5203이다. 안정된 점근 joint-error 모델이나 보편적 2차 정확도는 승인하지 않았다.

### 검증 범위

- 최종 소스에서 Rust 1.94.1 **224/224**, strict all-target Clippy, scoped rustfmt를 실제 실행했다.
- 원래 fresh restore는 신규 15개 tests와 두 studies를 다시 실행했다. 전체 224 및 Clippy 실행과 구분한다.
- 환경 교체 후 새 `light` 재현도 Rust 15개·Python 7개, 과학 CSV 7개·기준 CSV 3개, 저장된 native 분석 9개 일치를 확인했다. 새 native simulation은 0개다.
- Decimal90은 scalar 84 cases, 실제 16,370 nodes, 2,016 field comparisons를 검증했다. Source 실제-node 검산은 **12/288 rules, 5,888 nodes, 264 fields**의 명시적 표본이며, 별도로 전체 4,608 label identities와 12 mixture rows를 확인했다.
- PHYS-MATH-CODE audit는 PASS_SCOPED다. 그림 21개 검사와 21개 변조 탐지를 완료했다. 디지털 그림은 PASS이며 90/182 mm 인쇄 조판은 미승인이다.
- Subnormal quantile, zero-label CLI, fresh input-path 오류는 수정 기록을 보존했다. Tau1e300 `NoForwardProgress`는 representation limit다. 부모의 0-row `Cx(WorkLimit)`는 work-budget exhaustion이며, 새 native 두 사례는 완료했다.

## 5. 다음 bounded node

**`BR05_NATIVE_BIRTH_MONITOR_AND_R_PAIR`**

1. 실제 retained native cohort의 물리적·광학적 birth-panel 폭과 동결 참조 certificate를 읽기 전용으로 내보내는 monitor를 유도·구현한다. Birth time/geometry, Killing constants, energy, direction, age 및 source labels를 유지한다.
2. 작은 native 비교를 선택한다면 Nt16r8 한 사례를 보충하고 기존 Nt32r8을 재사용하여 r4→8 rectangle을 닫는다. 실제 비용을 기록한다. Nt128r4는 별도 비용을 산정한 후 다른 bounded unit으로 처리한다.
3. 동결 연산자의 birth-error 추정과 비선형 gas/opacity response를 구분한다. CX half-flow 및 four-corner timestep owner를 바꾸지 않는다.
4. Variable opacity, blueshift threshold entry, 전체 age–energy–angle joint convergence, 분광·각도 독립 수렴 및 gas-response stability는 남은 의무로 유지한다.

현재 상태는 `BR04_JOINT_TIME_AGE_CONVERGENCE=PARTIAL`, `LONGSPAN_SOLUTION=NOT_ADMITTED`, `ISO-COUPLE-P4=PARTIAL`이다. `SA-01/02`, `FLRW-CONV`, `BI-SIGNED`, `FULL_EOR`는 HOLD이며 two-way Einstein feedback은 미구현이다.

Metric (-,+,+,+), V=a³, signed s/H와 비음수 Sigma의 구분, 원 MD14/BB50k·Verner H/He·H-equality D 계약을 유지한다. H binding 13.598434599702 eV, 제조 D threshold 13.602134599702 eV, Verner H fitting edge 13.60 eV를 혼동하지 않는다. 기존 10⁴ K/20 K control 상태를 full-EoR 초기조건으로 승격하지 않는다.

## 6. 재현 명령

다음 파일부터 읽는다: `contracts/DAG_PROGRESS.json`, `docs/REPORT_KO.md`, `docs/AGE_CERTIFICATE_THEORY.md`, `evidence/SCIENCE_RESULTS.json`, `evidence/VERIFICATION.json`, `ARCHIVE_SOURCE_IDENTITY.json`, `RECOVERY` 기록.

압축 해제 디렉터리에서 Rust/Cargo 1.94.1, Python 3.12를 사용한다.

```bash
bash RUN_STAGE.sh verify
bash RUN_STAGE.sh light
```

전체 tests와 Clippy가 필요한 경우 해당 component가 설치된 환경에서 다음을 실행한다.

```bash
bash RUN_STAGE.sh test
```

출력과 build cache override는 패키지 밖의 새 경로로 지정한다. 전체 crate는 부모 Git checkout 없이 재현할 수 있지만, source patch 및 증분 bundle은 부모 commit `8e60ecb627da46bb85861e2a4148a1b683d96fb0`이 필요하다.
