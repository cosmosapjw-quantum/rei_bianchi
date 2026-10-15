# PR 묶음과 선택 source

이 문서의 `D0`, `P0`, `P1`, `P2`, `PROVIDER`, `RECEIVER`, `OPTIONAL`은 **로컬 planned PR ID**다. GitHub PR 번호가 아니며 실제 생성 번호/URL은 publication return에 기록한다. 2026-10-14 관측 당시 실제 101개 open PR 전체의 number/title/url/head/base SHA/branch/draft/state/updated/mergeability는 [PR_INVENTORY.json](PR_INVENTORY.json)에 있다. 새 D0 draft PR가 생성되면 live open count가 102 이상으로 달라질 수 있다. snapshot을 영구 최신 목록이라고 하지 않는다.

| Planned ID | 소유와 범위 | Nodes | 조건·결과 |
|---|---|---|---|
| D0 | rei coordinator; additive execution docs, `.codex/agents`, support CLI/tests, saved-endpoint report, current-plan pointer | RUX01, RETAINED-REVIEW, REPORT-DRAFT; 전체 DAG/packet 준비 | base PR83 c07fc7e7. 사용자 승인된 commit/push + draft PR. solver/old contracts 변경 없음; 실제 remote SHA를 비교 |
| P0 | rei shared-runtime owner; exact E-P source/provider delta, scenario, adapters, first coupled FLRW interval | RUX00, SIBLING-INTAKE, SOURCE-INTEGRATION, RUX02–05, LOWT-PROVIDER, CC-PREP05 | point/provider/domain/time/source/owner 실제 연결; missing fields는 null과 한 supply task. warm guard를 확대하는 flag 변경으로 통과시키지 않음 |
| P1 | rei runtime/transport owners; selected geometry adapter, first BI interval and FLRW history | RUX06–08 | P0 first-interval gate. same source/IC/clock, zero-shear limit, checkpoint/새 output dir, 단계별 plot |
| P2 | rei paired/figure owner 및 unmodified pinned bass receiver 소비 | RUX09–11, CC-RECV, REPORT-DRAFT 갱신, SCIENCE-REVIEW, RUX16 | 데이터·observer-tail·error/independent review가 해당 claim에 충분할 때 scoped 결과. report는 HOLD에서도 제공 |
| PROVIDER | BASS_HE owner; 실제 필요한 low-T/thermal-domain supplier | LOWT-PROVIDER의 supplier 요구 | target/source/domain이 실제로 요청될 때 작은 공급 변경. rei 작업자가 sibling repo를 임의 수정하지 않음 |
| RECEIVER | bass owner; 기존 receiver에서 필요한 최소 schema/interface delta | CC-RECV, RUX10의 supplier 요구 | 실제 pinned receiver로 충분하면 새 PR 불필요. fixed-time τ/directional observed-redshift와 tail을 구분 |
| OPTIONAL | 각 HE/CR/HH/spatial owner 및 rei matched ON/OFF consumer | RUX12–15, 독립 control lanes | sensitivity/실제 claim이 요구할 때만 활성화. baseline OFF와 native full-history off-critical-path 보존 |

노드당 별도 PR를 의무화하지 않는다. 한 PR 안에서도 write owner를 분리하고 공유 Rust 파일은 단일 owner로 모은다. 2–4 writer는 서로 독립 path를 사용하며 coordinator만 checkout/stage/commit/push한다. same checkout과 owner dirty/untracked를 보존하고 자동 clone/worktree를 만들지 않는다. scientific admission, Git mergeability, draft publication을 별개로 기록한다. main/forward/타 owner branch 병합은 이 계획의 실행 작업이 아니다.

## 실제 선택 PR와 재사용

| Actual PR | 역할 | exact head | 통합 방식 |
|---|---|---|---|
| [rei 83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83) | active base/adopted v2/Rust core | c07fc7e765ce204bc3e84016cc6874612e535b86 | D0 기준. source가 이동하면 노드별 delta review 후 actual integration SHA 기록 |
| [rei 104](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/104) | retained reduced-history baseline | f66929c23ea3fa6e39dd4808e5b27d136c568a03 | saved results·scope reuse; whole merge 또는 재실행 아님 |
| [rei 110](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/110) | ACCEL02 native history/checkpoint 계보 | 17f8d0daa72e0f76a49cde01b110f650a6688c42 | completed evidence reuse. actual current NCP state는 별도 C0 확인 |
| [rei 114](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/114) | E-P warm conditional event receiving path | a5c958c414dea41216b445c05f58df837f05cacb | SOURCE-INTEGRATION이 정확히 필요한 code delta만 채택. full EoR provider admission 아님 |
| [rei 115](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/115) | OBSERVER15 R8 cubic selection | 39dce6702dcadbb516fc8e25e7ba5a6991f64c22 | R7-A same-target cubic + R9 return contract. 이름상 R5를 최신이라 하지 않음 |
| [rei 116](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/116) | separate microphysics R8 | 2df18a7238b3e52d0eb844fd45aa706dbf883ab3 | scope/contract reuse; heavy8 ready0을 전역 선행조건으로 올리지 않음 |
| [HE 47](https://github.com/cosmosapjw-quantum/BASS_HE/pull/47) | recovered warm state/ray supplier | dff95caa7fabb2a38acf73ba0946a1d88a125f3d | source-bound data reuse; absolute true-IVP column null |
| [CR 58](https://github.com/cosmosapjw-quantum/bass_cr/pull/58) | finite-rate constructive bound | 808d11c1869c6334572554edcb24370e35c69f44 | optional source-bound input; no microscopic tau calibration |
| [HH 64](https://github.com/cosmosapjw-quantum/WU088_HH/pull/64) | warm differential response | 6320b23cba96abf12b150eea439e458f86aa1d69 | matched-source sensitivity context; absolute baseline null |

한 branch가 runnable stack 전체를 포함하지 않는다. Git archive publication 문서와 실제 private payload를 분리하며 선택 source/source-config/observer identity를 actual return에 기록한다. 다른 95개 rei PR는 inventory/reference로 남기고 각각의 필요가 실제로 드러날 때만 좁게 읽는다. 모든 PR를 병합하거나 최신 제목만 따라가는 것을 실행 완료로 보지 않는다.

각 PR body는 문제/변경/실제 산출물/scope와 검증을 짧게 서술하고, unexecuted run에는 NOT_RUN 또는 null을 기록한다. final science PR에서도 native capability가 없었던 경우와 독립 검토 부재를 그대로 밝힌다. force push/타 branch mutation은 하지 않는다. push/readback/draft URL은 실제 관측값으로만 채운다.
