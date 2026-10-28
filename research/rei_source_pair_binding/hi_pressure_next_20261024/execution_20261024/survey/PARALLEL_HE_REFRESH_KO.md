# 게시 중 추가된 HE PWBE 병렬 변경 — 한정 최신 조사

## 결론

**새 HE 결과는 압력 모멘트 또는 Bianchi stock의 현재 추상 범위를 무효화하지 않는다.** 두 소유 코드 경로의 수정이나 추가 과학 실행은 필요하지 않다. 중앙의 병렬 3파일을 보존하고, HE의 실제 새 모형 입력과 열린 의무를 최종 인계에 추가하면 된다.

다만 이전의 “joint amplitude/law가 없다”는 표현을 현재 HE 상태에 그대로 쓰면 부정확하다. 이제 **DERIVED_PWBE_MODEL_INPUT_AVAILABLE**이 실제로 존재한다. 그 의미는 명시적인 근사모형의 연속 pointwise joint TDCS와 조건부 방위각 법칙이며, 보정된 물리 공급자 승인과는 구분한다.

이 조사는 실제 이동 `9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9` → `cdba5c98819ea615c32c4d7cea2c613a737e9eb1` 및 거기서 지정한 source만 읽었다. 이전 1326-head snapshot과 코드·정적 검토 기록은 변경하지 않았다.

## 실제 중앙 변경

[두 중앙 commit의 compare](https://github.com/cosmosapjw-quantum/rei_bianchi/compare/9f410bf0f4b5d14d1e6b7c17cd2e23a916f241c9...cdba5c98819ea615c32c4d7cea2c613a737e9eb1)는 ahead 1commit, 아래 3파일이다.

| 파일 | 변경 |
|---|---|
| assembly/DAG.json | HE-ANG 아래 두 필드 추가 |
| assembly/HANDOFF_BASS_HE_KO.md | 기존 본문 앞에 10줄 추가 |
| assembly/returns/BASS_HE_HEANG_PWBE_SPIN_AZIMUTH_20261024.json | 새 실제 return |

두 DAG의 JSON을 기계적으로 대조한 의미 차이는 다음 두 추가뿐이다.

- `/nodes/19/observed_completion/next/model_available`
- `/nodes/19/observed_completion/pwbe_spin_azimuth_subunit`

다른 39개 node, 기존 HE-ANG 필드와 나머지 top-level 값은 모두 동일하다. Handoff 이전 본문도 그대로 보존됐다. Pressure·stock 소유 경로 변경은 0이다. AGENTS 동일성은 root의 새 실제 관측을 전달받았고 중복 조회하지 않았다.

## Source identity와 현재 판정

[현재 PR97](https://github.com/cosmosapjw-quantum/BASS_HE/pull/97)을 2026-10-24 **09:12:21 UTC**에 읽었다.

| 항목 | 관측값 |
|---|---|
| Unit | HE-ANG-PWBE-SPIN-AZIMUTH |
| Branch | research/he-ang-pwbe-spin-azimuth-20261024 |
| 실제 Science S / PR head | db91cbd3ac0f4db7908cd69c1f40e961f81051f9 |
| Science tree | d04f1bfb97d9c3a61835b3d0709825453f9b3a3f |
| 실제 Central C | cdba5c98819ea615c32c4d7cea2c613a737e9eb1 |
| PR | open / draft / unmerged |
| R6 | PASS |
| R7 | Source가 기록한 실제 한 evaluator, 10 Boolean TRUE와 exact oracles |
| C9 / root | **PASS_SCOPED_SCIENCE_PRESENTATION_OPEN** |
| 부모 HE-ANG | **SOURCE_INPUT_PENDING** |
| Physical provider | **false** |
| 현재 유한 stage | **17 complete / C8 partial / R10·C10 pending** |
| 20/20 또는 전체 물리 완료율 | 미승인 / null |

[CLAIM_GATE](https://github.com/cosmosapjw-quantum/BASS_HE/blob/db91cbd3ac0f4db7908cd69c1f40e961f81051f9/research/he_ang_pwbe_spin_azimuth_20261024/CLAIM_GATE.json), [ROOT_ADMISSION](https://github.com/cosmosapjw-quantum/BASS_HE/blob/db91cbd3ac0f4db7908cd69c1f40e961f81051f9/research/he_ang_pwbe_spin_azimuth_20261024/reviews/ROOT_ADMISSION.json), [RESULTS](https://github.com/cosmosapjw-quantum/BASS_HE/blob/db91cbd3ac0f4db7908cd69c1f40e961f81051f9/research/he_ang_pwbe_spin_azimuth_20261024/RESULTS_KO.md), C9와 실제 저장 analysis를 읽었다. 읽은 theory·contract·AZIMUTH_ANALYSIS의 실제 SHA256은 C9가 고정한 세 SHA와 모두 일치한다.

고정 claim/result 파일의 `ACTUAL_S_NOT_YET_PUBLISHED` 및 frozen contract의 실행 전 문구는 작성 시점의 기록이다. 현재 S와 C가 실제 존재한다는 관측을 publication 축에서 적용한다. 반대로 “나중 delivery가 끝나면 19 complete”는 목표일 뿐 현재 완료로 승격하지 않는다.

## 새로 얻은 과학적 기여와 물리 범위

새 입력은 **H(1s) 전자충돌 이온화**의 nonrelativistic, infinite fixed proton, plane-wave first-Born exchange 모형이다. Weigold FIAS-R-39 June1978 Eqs19–20의 direct amplitude와 outgoing-electron exact swap을 사용하며, 독립 unpolarized spin trace를 다음과 같이 결속한다.

`1/4 |D+X|² + 3/4 |D−X|² = |D|² + |X|² − Re(DX*)`

원전 printed Eq21의 −2DX는 원문으로 보존하면서 unpolarized law로 채택하지 않았다. Buică Born–Ochkur exchange와 동일시하지 않는다. Buică erratum body 미확보도 유지하며, 이 독립 trace의 필수 전제로 쓰지 않는다.

입력과 출력의 domain·measure·count는 고정돼 있다.

- Binding 1/2 Hartree는 해당 수학모형의 exact 값이다.
- `dE_B dΩ_A dΩ_B`, `dΩ=dμ dφ`, beam +z, relative azimuth를 사용한다.
- Pointwise TDCS에는 추가 2 또는 4를 곱하지 않는다.
- 향후 event integral은 ordered sector factor 1 또는 full labeled sector factor 1/2다. **그 전체 energy/solid-angle event integral은 이번에 수행하지 않았다.**
- Positive normalization domain에서 closed relative-azimuth conditional law, cosine moment와 두 전자 방향의 조건부 상관을 제공한다. Zero normalization의 conditional law는 undefined로 구분한다.

이 결과로 새 analytic joint model은 생겼다. **Plane-wave model의 실제 정확도·calibration, finite-mass recoil, required support·uncertainty와 consumer admission은 여전히 OPEN**이다. 기존 DDCS20/TDCS54의 부분 관측을 전체 물리 공급자로 승격하지 않았고 empirical table fit도 하지 않았다. 기존 sparse 자료와 이번 derived model은 별개의 scoped 근거다.

## 실제 검증·실패·자원

[저장 결과와 C9](https://github.com/cosmosapjw-quantum/BASS_HE/blob/db91cbd3ac0f4db7908cd69c1f40e961f81051f9/research/he_ang_pwbe_spin_azimuth_20261024/reviews/C9_REPORT.json)는 초기 14 methods의 **12 PASS / 2 FAIL**을 보존한다. 두 assertion이 frozen comparison allowance와 충돌한 false-FAIL로 판정돼, 기존 tolerance helper를 적용한 해당 두 methods만 targeted PASS했다. Core/source/theory/contract/analysis와 tolerance는 변경하지 않았고 전체 14-method replay도 하지 않았다.

G1–G6의 독립 Cartesian source-amplitude periodic quadrature는 N=64/256/1024/2048을 사용했다. 저장된 최종 비교의 최대값은 Kbar 상대오차 **7.15623529622744e-15**, conditional cosine 절대오차 **3.3306690738754696e-16**, normalization error **6.772360450213455e-15**다. Frozen 1e-10 기준의 유한 사례 검증이며 global/physical error certificate는 아니다. 이번 refresh는 저장 행을 읽었고 kernel이나 quadrature를 실행하지 않았다.

| 실제 attempt | 상태 | 측정 CPU s | 측정 wall s |
|---|---|---:|---:|
| 초기 tests | FAIL | 0.093884 | 0.11865653000040766 |
| 두 assertion의 한정 repair | PASS | 0.089662 | 0.12036444200020924 |
| azimuth analysis | PASS | 0.172483 | 0.2182225649994507 |
| 첫 plot draw | FAIL | 1.610416 | 1.6219177279999712 |
| 누적 | 실패 비용 포함 | **1.966445** | **2.079161265000039** |

새 allocation은 CPU/wall 8/30이며 reserve 1회 사용·잔여 0이다. 추가 child는 승인되지 않았다. End-to-end CPU cap은 미확립이고 host·remote 전체 CPU는 UNKNOWN_NOT_ZERO다. 이전 budget·실패·unknown의 reset/transfer는 없다.

Plot은 Mathtext bracing으로 실패했다. 표시 문자열 3개만 정적으로 고쳤고 재렌더링하지 않았다. **C8-PLOT-01 = STATIC_CORRECTED_NOT_RERENDERED_OPEN**, C8 PARTIAL이며 figure/render/visual PASS를 주장할 수 없다. 이 표시 문제는 현재 REI pressure·stock scope의 blocker로 이전하지 않는다.

## 백업과 실제 전달 경계

[Science S의 B1 receipt](https://github.com/cosmosapjw-quantum/BASS_HE/blob/db91cbd3ac0f4db7908cd69c1f40e961f81051f9/research/he_ang_pwbe_spin_azimuth_20261024/delivery/B1_BACKUP_ACK.json)는 실제 dual upload ACK와 별도 metadata readback을 기록한다.

| 항목 | 값 |
|---|---|
| Archive | HEANG_PWBE_SPIN_AZIMUTH_B1_PREEXECUTION_20261024.tar.gz |
| Size / members | 210830 bytes / 37 |
| SHA256 of local uploaded bytes | 4a3f1c5c2e9e7941d113c6217befcf51167eb0f0cb48c58bc0ab87d3652e8b49 |
| Drive | 1mkc6jKqa2trgI_5gjm1UV3DABSGTmrmu |
| Dropbox | id:BSpOijBcT10AAAAAAD_9Zg |
| Independent remote SHA256 | false |

이는 고정 source의 실제 receipt를 읽은 결과다. 이번 refresh가 두 provider를 다시 조회하거나 archive를 다운로드한 것은 아니다.

관측한 새 central return과 현재 PR97에서 **exact S/C의 B2, 후속 D/E 및 B3는 PENDING_ACTUAL**이다. 실제 S/C가 게시된 사실만으로 이 백업들을 완료 처리하지 않는다. 이전 HE96의 B3 COMPLETE는 그대로 유지하며 이번 HE97의 pending과 섞지 않는다.

## Pressure 및 stock에 대한 판단

Pressure의 유한 양의 측도 모멘트 경계는 이 새 전자충돌 모형을 전제로 하지 않는다. 현재 HI photoionization summary consumer와 source process도 다르므로 자동 교체하거나 결속하지 않는다.

Bianchi stock의 조건부 에너지 경계는 이미 unrestricted angular positive measures를 허용한다. 새 조건부 각도 모형이 그 수학적 경계를 무효화하지 않으며, 필요한 실제 cohort의 N,U,L,M·초기 stock·주입 이력·외부 배경 ratios를 공급한 것도 아니다. 따라서 pinned stock static verdict는 그 범위에서 유지한다. 물리 EOS·열화·Einstein closure·L4를 새로 승인하지 않는다.

Root는 병렬 중앙 3파일을 보존하고 다음 문장 수준의 상태를 최종 인계에 추가할 수 있다.

> HE-ANG-PWBE-SPIN-AZIMUTH의 Science S=db91cbd3…와 Central C=cdba5c9…를 수신했다. Derived continuous PWBE joint model/conditional azimuth input은 실제로 이용 가능하며 C9/root PASS_SCOPED_SCIENCE_PRESENTATION_OPEN이다. Parent HE-ANG SOURCE_INPUT_PENDING, physical_provider=false, calibrated accuracy/recoil/consumer obligations OPEN을 유지한다. 현재17complete/C8partial/R10·C10pending이며 plot static correction은 rerender하지 않았다. B1 dual ACK, 새 B2/D/E/B3 pending actual이다. 이 변경은 현재 추상 pressure/stock scope와 코드에 영향을 주지 않는다.

## 근거와 수행 범위

새 source 9파일, central text 4개, compare 1개, PR 1개로 **15회의 한정 GitHub 읽기**를 수행했다. Tool error는 0이다. 일곱 저장소 재조사, backup inventory 재조사, private context/PDF/archive 다운로드, 과학 실행, CAS, render, Git/cloud 변경은 모두 0이다. 읽기·비교의 기계적 I/O 비용은 미계측이며 0으로 쓰지 않는다.

실제 raw 응답과 정확한 text, C9 pin 대조, DAG semantic delta, handoff diff는 `survey/parallel_he_refresh_20261024/`에 보존했다. `READ_MANIFEST.json`은 어떤 필드를 실제로 읽었는지 구별한다. 약200KB의 저장 analysis는 전체 raw를 보존했지만 pointwise grid 전부를 검사했다고 주장하지 않는다. 기존 snapshot 문서와 코드는 수정하지 않았다.

