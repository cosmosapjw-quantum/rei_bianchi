# REI 유한 비열적 압력 실행 전 최신 조사

## 판정

**준비된 유한 등방 압력 모멘트 fixture를 무효화하는 의존성 변경은 관측하지 않았다. 변경된 인접 연구 상태만 갱신하면 된다.** 이번 조사는 과학 admission이나 예산을 발행하지 않는다. 새 과학 child, CAS, 렌더, Git·cloud 변경, 원격 압축파일 다운로드는 모두 0이다. 읽기·저장 등 기계적 비용은 별도 미계측이며 0으로 간주하지 않는다.

고정 인계는 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`의 `research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md`다. root가 새로 확인한 AGENTS blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`를 전달받았다. 현재 세션의 사용자 승인 판단은 root에 있으며, 과거 영수증의 pressure `NOT_AUTHORIZED`를 현재 사용자 승인에 덮어쓰지 않는다.

## 실제 조사 범위

브랜치 metadata는 2026-10-24 08:34:42–08:34:51 UTC에 조회했다. REI 첫 페이지는 바로 앞 discovery call에서 받은 원응답을 재사용했으며 그 페이지의 별도 시각은 기록하지 않았다. 여러 API 읽기는 단일 시점의 원자적 snapshot이 아니다.

| 저장소 | 직전 05:15 snapshot | 이번 heads | 실제 빈 종료 페이지 |
|---|---:|---:|---|
| rei_bianchi | 265 | 266 | page 4 |
| bass_cr | 180 | 180 | page 3 |
| BASS_HE | 100 | 101 | page 3 |
| rec_bianchi | 150 | 151 | page 3 |
| WU088_HH | 152 | 152 | page 3 |
| bass | 271 | 271 | page 4 |
| vigilode | 205 | 205 | page 4 |
| 합계 | 1323 | **1326** | 7/7 |

24개 branch collection 읽기를 빈 페이지까지 수행했다. 기존 선택 PR 56개와 새 branch별 PR query 5개를 갱신해 서로 다른 PR 60개를 받았다. 초기 61요청은 직접 PR 53개와 branch-filtered query 8개다. 뒤에 움직인 REC PR133을 한 번 다시 읽었다. 변경 compare 3개, commit metadata 3개, 고정 SHA source text 18개 및 선택 PR 본문 3개를 읽었다. 세부 범위·SHA256·정확한 로컬 본문은 `github/SELECTED_READS_MANIFEST.json`에 있다.

이는 모든 branch head metadata의 조사다. 모든 branch의 모든 blob, 모든 역사적 PR, 모든 대화를 읽었다는 뜻은 아니다. 이번 Personal Context 호출은 실제로 `Personal context is unavailable for this conversation.` 오류를 반환했다. 이를 관련 대화의 부재로 해석하지 않았다.

## 중앙 HEAD와 압력 경로

[현재 중앙 HEAD 9f410bf0](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9)는 직전 own closeout `c40d287874f72519103e68267e659fc022eba188`보다 3commit 앞선다. [실제 compare](https://github.com/cosmosapjw-quantum/rei_bianchi/compare/c40d287874f72519103e68267e659fc022eba188...9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9)는 다음 5파일뿐이다.

- `assembly/DAG.json`
- `assembly/HANDOFF_BASS_HE_KO.md`
- `assembly/HANDOFF_bass_cr_KO.md`
- `assembly/returns/BASS_HE_HEANG_TDCS54_ANCHORS_BACKUP_ACK_20261024.json`
- `assembly/returns/CR_N5_CE_KILLED_GENERATOR_FIRST_EVENT_20261024.json`

L1 consumer나 준비된 pressure 코드·fixture 경로의 변경은 0이다. 원 assembly DAG의 REI-L0…L5와 REC-HISTORY author plan 상태는 여전히 PROPOSED로 보존돼 있다. 이는 owner별 실제 완료 근거를 취소하는 값이 아니며, 별도 관측을 반영하지 않은 원 계획과 actual admission을 구분해야 한다.

## 새로 확인한 관련 연구

### CR PR102: 유한 chain의 첫 CE 사건

[bass_cr PR102](https://github.com/cosmosapjw-quantum/bass_cr/pull/102), documents `3acb6beca5de4f82fccff1673dbcac010c53cf24`, science `896800b4511f323ad3f0b5372b4912fb4770ea98`는 `PASS_SCOPED_NATIVE_KNOT_FINITE_CHAIN`이다. [실제 claim gate](https://github.com/cosmosapjw-quantum/bass_cr/blob/3acb6beca5de4f82fccff1673dbcac010c53cf24/research/cr_n5_ce_resolvent_20261024/CLAIM_GATE.json)는 고정 Maxwell EE chain에서 cutoff 첫 진입 전에 생기는 H1 1s→2s/2p 사건만 승인한다.

T=10000 K, thermal ne=0.14 cm⁻³, lnΛ=20, stationary ground-H1 n1s=0.9 cm⁻³, closed box에서 selected source 전자의 CE 확률은 1.4302747727e-5–1.4642413873e-5다. v3의 8 matrices/72 RHS/24 source rows와 독립 C9가 완료됐다. 첫 진입은 irreversible assimilation·Maxwellization이 아니고 internal excitation reward는 최종 bath heat가 아니다. full N4/N5는 PARTIAL/OPEN, N6/N7은 gate 뒤다.

v1 variable-shadow 실패와 exact raw 미복원, v2의 18개 probability-grid FAIL을 보존한다. 실제 누적은 22Q/21complete/189RHS, exact retained raw는 20complete/180RHS다. Known bounded worker lineage 24.830244114 CPU s는 부분합이며 global spend/remaining은 null이다. Canonical Library+Dropbox R3 PASS는 원 source의 보고이고, Drive는 UNKNOWN_NO_ACK/R3 NOT_RUN, terminal Drive는 NOT_ATTEMPTED다. 이번 조사에서 이를 재실행하거나 다시 다운로드하지 않았다.

### HE PR96: TDCS54의 두 sparse 좌표

[BASS_HE PR96](https://github.com/cosmosapjw-quantum/BASS_HE/pull/96), delivery `32f9227a9abef814bb009a87272c44be74941163`, science `60cacdb740fa4dadcdcbff43b7ffcb52566e077d`는 `PASS_SCOPED`다. [claim gate](https://github.com/cosmosapjw-quantum/BASS_HE/blob/32f9227a9abef814bb009a87272c44be74941163/research/he_ang_tdcs54_anchors_20261024/CLAIM_GATE.json)는 incident 54.4 eV, slow 5 eV의 위치가 지정된 두 reported TDCS 값과 정확한 nominal normalization/shape 진단을 승인한다. Full joint event law, event sigma, finite-mass recoil provider는 여전히 false이고 부모 HE-ANG은 SOURCE_INPUT_PENDING이다.

고정 D/E 파일의 B3 PENDING은 역사적 값이다. 이번에 읽은 실제 PR96 본문은 **FINAL_B3_ACK_COMPLETE, 유한 20/20 stage 완료**를 기록한다. B3는 82,877 bytes/21 members, SHA256 `cec1368a9cdab209266a799b59028d25168d8362875e4cf77536824cd069a051`, Drive `1wuatJqvHJuFoYDNiBJThsFikgR6GmeDk`, Dropbox `id:BSpOijBcT10AAAAAAD_9YA`다. 이는 PR의 실제 완료 영수증을 읽은 결과이며 이번 survey가 별도로 provider SHA를 검증한 것은 아니다.

측정 4child+runner CPU 1.887889 s/wall 1.9431963300012285 s, plot-only repair 1회, end-to-end CPU cap 미확립을 그대로 보존한다. HE94의 DDCS20 partial window와 C9-NB-01도 유지한다.

### REC PR133/REI PR225: 저장된 h2/h4 history의 discrepancy envelope

[rec_bianchi PR133](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/133)은 초기 head `a67044c411b4bef8d5762b4171c0c088fa34f161`에서 조회 중 `c5394eccf6ff45f134e396c549844af91988aeb7`로 이동했다. PR 재조회와 실제 git/ref 읽기로 후자를 확인했다. 한 commit/14파일 이동은 delivery·progress·report metadata이고 선택 과학 claim/source/result/review 파일은 바뀌지 않았다.

[현재 claim gate](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/c5394eccf6ff45f134e396c549844af91988aeb7/research/rec_history_refinement_envelope_20261024/CLAIM_GATES.json)는 `PASS_SCOPED_STORED_HISTORY_ENVELOPE`다. 314채널×759cell=238326 channel-cells, 714978 witnesses, Fraction350점/70cell, 26controls를 검증했다. 최대 저장 함수 차이는 1.6498272419025407e-15이며 outward upper는 1.649827241902541e-15다. 같은 채널 scale 대비 0.291986899…는 descriptive normalization으로, physical relative-error certificate가 아니다.

실제 physical reference uncertainty·endpoint uncertainty·curvature·absolute physical bound·convergence order는 null이고 원 target coverage는 0/313이다. H5 INPUT_DEPENDENT_UNCALIBRATED, REC-HISTORY PARTIAL, physical HOLD, production NOT_APPROVED, REI_activation=false를 유지한다. 유한 workflow는 D1에서 20/20 완료, 추가 Drive는 완료 ACK 없는 UNKNOWN이다. unit 측정 CPU 4.832465 s/wall 4.895043831013027 s, primary 재실행 0이다.

[REI PR225](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/225)의 observation `47abc82646d0f92b12d4843abb770be9b3593a37`은 별도 draft branch에 있다. 현재 중앙 9f410bf0의 REC-HISTORY node에 그 관측이 합쳐졌다고 주장하지 않는다.

## 그대로 유지할 범위

- C23E/PR100 `8e4e0636…`는 **conditional D43K** threshold-gated H-equality PI, shared H/D RR kinetic moment, WU79 CX의 instantaneous source 범위다. 독립 물리 isotope provider로 승격하지 않는다.
- HH의 두 head는 불변이다. PHYS85의 원 2회 호출/완전 출력 0/기존 잔여 0과 실패를 유지한다. PHYS86은 별도 actual projected reference 1017/1017와 finite moment 82/82를 완료했지만 physical finite-T nuclear rate·stopping·continuum Jüttner quadrature는 공급하지 않는다.
- BASS B3b는 canonical-rest f=0 finite transaction의 scoped PASS다. 일반 finite absorption owner/input은 열려 있다.
- VigilODE D3는 현재 head `d702012e…` 불변, 새 branch-specific PR query는 0건이다. 종전 prepared contract 및 native owner HOLD를 유지한다. 새 Dropbox `VIGILODE_NATIVE_RECONCILIATION_20261024T0516Z.zip`은 metadata만 확인했으므로 새 native admission을 추론하지 않는다.
- ANGTHERM02 `research/rei-coupled-isotope-contract-20261022@8d10231b1f0f788164d5eadbe1bcee0b802cceca`는 그대로 READ_ONLY다.

따라서 현재 pressure 작업은 주어진 유한 양의 측도에 대한 등방 모멘트 알고리즘과 fixture 범위를 유지한다. 주입률의 pressure moment를 저장된 비열적 입자 재고의 압력으로 바꾸거나 physical EOS·열화·L4를 승인할 근거는 새로 생기지 않았다.

## 지정 백업 폴더와 C 확인

Dropbox direct listing은 118→123개, has_more=false/cursor empty다. 최초 trailing slash 입력의 INVALID_PATH는 그대로 남기고 같은 폴더의 slash 없는 경로로 성공했다. Drive direct listing은 196→200개, top_k=1000이며 continuation token은 노출되지 않았다. 계정 전체나 하위 폴더의 완전성은 주장하지 않는다.

`REI_L1_ADMITTED_PRESSURE_PREP_C_20261024_05fdd1a843fa.zip`의 Drive `1DMgbS7M2BJqKYWHTQ1oLzgAwuAtB_Agd`, Dropbox `id:BSpOijBcT10AAAAAAD_9XQ`를 현재 metadata에서 확인했다. 둘 다 이름과 크기 **6,125,687 bytes**가 일치한다. 이미 있는 로컬 C를 실제 해시하여 SHA256 **05fdd1a843fa7ce3690e088092b3103b6f06e4aeb0bf3c62e56b76a897c19fa9**와 일치함을 확인했다.

두 provider의 최종 JSON 영수증도 읽었고 내용이 같다. Drive 영수증은 3429 bytes, SHA256 `ee1d2f2e1bf449a15809a00d0c240c7dab110c03fc795a73804e0f1bf4a39533`다. 원격 C 압축파일을 다시 다운로드하거나 원격 바이트 SHA를 독립 검증하지 않았다. 로컬 실제 해시·현재 원격 metadata·영수증의 해시 주장을 구분한다.

## 복구 가능한 근거

- `SURVEY_SUMMARY.json`: 범위, 상태, 제한, 변경 결과의 구조화된 종합.
- `all_heads/HEADS_COMPACT.json`, `all_heads/DELTA.json`, 각 repo raw pages: 실제 전수 head metadata와 차이.
- `github/PR_METADATA_RAW.json`, `CURRENT_PR_PINS.json`, `MOVING_HEAD_RECONCILIATION.json`: 선택 PR 및 움직인 REC head의 재확인.
- `github/SOURCE_FETCH_RESPONSES_RAW.json`, `SELECTED_READS_MANIFEST.json`, `reads/`: 실제 source 응답과 정확한 본문·SHA.
- `backups/`: 실제 direct listings, metadata, 최종 receipt 및 로컬 C identity.
- `ERRORS_AND_LIMITS.json`: 실제 접근·경로·로컬 스키마 처리 오류와 복구 범위.

Actual connector replies는 functions-store와 로컬 파일에 보존했다. 일부 backup raw에는 개인 metadata나 임시 signed URL이 있으므로 공개 Git에는 안전한 파생 요약·영수증을 사용한다.

