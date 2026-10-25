# REI GRID044 endpoint 결합 인계 — 2026-10-25

## 바로 읽을 것

1. 현재 `research/orchestration-sandbox-20261022`의 HEAD·AGENTS와 병렬 반환·백업 상태.
2. 이 디렉터리의 `SCENARIO.json`, `SCIENTIFIC_DECISION.json`, `REPORT_KO.md`.
3. `SOURCE_MANIFEST.json`, `RESOURCE_RECEIPT.json`, `evidence/FINAL_*REVIEW*` 및 최종 metadata review.
4. `delivery/FINAL_DELIVERY.json`의 실제 commit·ZIP·Dropbox/Drive ACK. 소스 archive와 그 생성 후의 전달 receipt는 별개 산출물이다.
5. 중앙 `research/orchestration_expansion_20261025/DAG.json`과 새 status 관측 `status/REI_GRID044_ENDPOINT_20261025.json`.

## 완료한 유한 단위

`REI-GRID044-ENDPOINT-BINDING-01`: **PASS_SCOPED_ENDPOINT_BINDING**. 원래 handoff는 commit `78f7ac5864d5817ceb79b48cb5e298cc30006510`에 고정되어 있다. 실제 GRID044 NPZ의 `atomic_abundance_per_Href[:, -1]`를 Li label로 재배열하여 z=2 저장 endpoint를 소비했다. n/T의 실제0을 유지했다.

Reference는 fixed-comoving bookkeeping number, r=n_ref0 a^-3이다. a_today=1, n_ref0=0.19078721280843758 m^-3, endpoint r=5.151254745827818 m^-3이다. r이 팽창으로 변하는 것과 실제 population을 따라 reference를 재정의하는 것은 구별한다. 일반 source와 tangent는 F=(S−xR)/r, dF=(dS−Rdx−xdR)/r−Fdr/r이며 consumer helper와 별도 controls로 확인했다.

13개의 single photo-event owner에 두 source의26기여를 결합했다. WU incidence, 저장 REC opacity/source-J, CR generic energy ledger, HE primary number/kinetic receiver, BASS prescribed geometry/signed stress stock, 원본 VigilODE D5 gateway의 actual21 client를 연결했다. CR의 다른 z/support에 해당하는 C23B spectra는 대입하지 않았다. 순간 counterfactual 연산자이며 기존 donor가 이 광원으로 진화했다는 뜻은 아니다.

Fast primary number source는 3.14906868137857e-18 m^-3 s^-1이다. Radiation loss / binding gain / primary kinetic gain은 [-8.35115562362068e-36,6.882360343067273e-36,1.4687952805534072e-36] J m^-3 s^-1이다. Thermal heat는 null이다.

Python32+Rust9 변경계약 검사가 통과했다. 구현자와 다른 두 reviewer가 소스·raw·저장 PNG를 확인했다. 잘못된 유한 J는 gateway가 허용하지만 독립 정확도 검사에서0.5오차로 검출했다. Source25/J25x23과 dynamical material21의 범위를 유지한다. Native FP witness, full physical domain, continuous trajectory/error control은 채택되지 않았다.

## 실행·비용 보존

- 새 science:2.900492 CPU s /2.940682361 wall s, cap30/120,512MiB,1worker.
- 새 infrastructure:14.682127 CPU s /14.797034617 wall s, cap60/180,1GiB. 최초 Rust linker 실패 비용과 raw를 포함한다.
- 별도 reviewer 산술/비교 비용은 SCIENTIFIC_DECISION과 review receipts에 scope별 기록. 계측되지 않은 전체 수작업·원격 overhead는0이 아니다.
- 새 integral,IVP,역사적suite replay,새83,NCP 모두0. 잔여 budget은 추가 실행 허가가 아니다.
- PR219 bootstrap, 기존83, GRID044 main/continuation, PR221 ANGTHERM01/02의 누적·미지·실패 비용과 범위를 보존한다. 새83 전구간을 재현하거나 NCP를 자동 시작하거나 예산을 초기화하지 않는다.

## 다음 최소 과학 입력

`NEXT_SELECTED_BINDING.md`의 H1 단일 primary-degradation 후보부터 이어간다. 같은 source/frame/reference의 energy-resolved source와 실제 유효범위가 맞는 HE stopping provider를 받아라. Gamma/P/K에서 spectrum을 임의로 정하지 마라. Angular law는 anisotropic transport/momentum을 선택할 때 요구한다. BASS 새 absorption four-force/stress 및 live Einstein feedback, 확장 VigilODE physical domain/Jacobian은 해당 선택 모델에서 이어 붙인다.

중앙 DAG는 기존87계약과17edge를 보존하고 이번88번째 자식만 추가한다. REI-L4와 V6 owner 상태를 대신 승격하지 않았다. `L4_ready=false`, `global_physical_completion=null`. 선택 H1 채널에 불필요한 모든 미래 핵·분자 반응을 AND gate로 걸지 않는다.

게시 중 중앙 HEAD에 HE 관측 commit `fc2c6044b5e9eb08e0e0486c17d1987c7099df9c`가 병렬 도착했다. 그 다섯 HE wrapper 관측을 보존한 상태에서 우리 세 REI 관측과88번째 child를 결합했다. HE source `965da72aa7a5e885e12956fafadfb8dc2519b81f`의 conditional exchange·ownership 구현 진행은 확인했으나 physical_provider_admitted=false, activation=false, HE101 C8=19/20·reserve0이다. 새 HE 입력을 받은 것으로 thermal heat를 채우지 마라. Evidence의 CONCURRENT_HE_STATUS, CONCURRENT_DAG_DELTA, CONCURRENT_MERGE_REVIEW를 함께 읽어라. 실제 최종 source/metadata HEAD는 delivery receipt가 정한다.

## 게시·백업 원칙

Owner는 게시·백업 및 필요한 자동 실행 권한을 명시 승인했다. 새 확인을 되묻지 말고 실제 권한 범위에서 작업하라. 각 노드 전에 fresh HEAD/AGENTS/parallel/backups를 확인하고, 새 변경은 독립 검토 후 expected-SHA·force=false로 기존 branch에 추가한다. 기존 draft PR222를 사용한다. Source ZIP은 정확한 과학 소스·입력·raw·review·DAG를 포함하며 전체 repo clone이나 compiler binary를 뜻하지 않는다. Dropbox와 Drive는 완료 ACK와 실제 size를 확인한 뒤에만 저장되었다고 기록한다.

입구에서 native 장치는 offline이었으므로 미게시 dirty/실행 상태는 UNOBSERVED이다. 다른 owner의 실행을 완료된 것으로 가정하거나 재시작하지 않는다. lower-tier spawn은 thread limit으로 거절되어 기존 compatible 완료 worker를 재사용했고, 이 routing 예외와 실제 실행자·독립 reviewer를 보존했다.
