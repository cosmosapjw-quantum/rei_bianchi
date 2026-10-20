# RUN19 원격 소스와 재사용 범위 조사

이 문서는 2026-10-20 UTC에 실제 GitHub API로 읽은 원문에 근거한다. 실행은 선택적 원문 확보와 파일 identity 확인에 한정했다. 새 빌드, 테스트, native RHS 평가, IVP, 과거 M2 계산 및 Git ref 변경은 모두 0회다. 생산자 보고서의 PASS와 벤치마크는 `ARCHIVED_EVIDENCE_ONLY`다.

## 현재 계보와 기존 완료 작업

RUN19의 적절한 부모는 `research/rei-run18-vigilode-c0-repair-20261020`의 `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e`, tree `a529f6356722e6602774fbc7f4ddc6c63b878f33`이다. PR209는 해당 head의 open draft였다. RUN13 recovery branch는 `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`다. 조사 시점 250개 branch를 확인했고 후속 RUN19 branch는 없었다. 새 RUN19 작업을 부모가 시작한 이후의 ref 상태까지 이 inventory가 보증하지는 않는다.

RUN18의 다음 과학 노드는 original-owner interval RHS branch, invariant lift/scaling, gas-depth Jacobian 및 전 구간 residual/tube 결합이다. 온도표 최적화는 이 노드의 계산 도구를 개선하며 spectral continuum bound를 완결하지 않는다. 원래 45/26 DAG 경로와 해시는 보존한 `run18/DAG_CONTINUATION.json`에 있다. angular/birth continuum, whole domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE, Li/Be 및 nuclear T1–T8 의무는 계속 남는다.

별도 PR208 `b67884483be4be293805a5dd4c9319d6465322bc`는 BR06 frozen native birth reference를 이미 완료했다. 이는 고정 가스의 source-age 적분이며 새 비선형 gas history가 아니다. RUN18과 다른 owner 계보이므로 합쳐서 한 번의 과학 실행으로 취급하지 않는다.

## 이미 구현된 기능과 새로 연결할 부분

고정99 소스 `run13/recovered/code/rei_bass_coupled/owner_src/rate_table.rs`에는 immutable `IgmRateTable`, 15-channel `LogRateGrid`, SoA batch, 1–4 worker parallel batch, `PreparedIgmRates` 및 `Direct/Table` backend가 이미 있다. 기본 source와 evaluator는 그대로 유지해야 한다. `gas_reference_rhs.rs`와 `full_network.rs`에는 HHe 직접 rate 계산과 별도 D provider 호출이 남아 있어 동일 T의 prepared bundle을 실제 consumer에 연결하는 일이 유효한 새 작업이다.

원래 source는 Grackle 3.4.1의 고정 계수와 branch를 따른다. T-only 표에 저장 가능한 것은 계수이며 proper density, CMB, photo moment, expansion, thermal power assembly는 배경/상태 의존 caller에 남는다. CI/RR/DR 계수는 cm³/s이고 최종 gas RHS 밀도는 m⁻³다. metastable He I collisional-excitation 계수는 erg cm⁶/s이므로 다른 cooling 계수와 단위를 혼동하면 안 된다. 정확한 5500 K, 9284 K, floor/cap branch 및 구조적 zero를 유지한다.

C8/C9/C10 보고서는 이미 65,537-node 표를 검토했다. C8의 큰 speedup에는 worker 수가 혼합되었고 C9에서 동일 4-worker 기준 ordered 1.608×, random 1.371×로 정정했다. 약 9.11 MB 표와 build 비용, workload별 amortization을 포함해야 한다. 표의 sampled 값 오차와 도함수 오차는 별개이며 sampled derivative 결과를 analytic tube로 승격하지 않는다.

## PR150의 정확한 forwardport donor

PR150 `fd9a21c4d3886a495540b51d780a83b608e72ea2` 원문을 `upstream_selected/rei_flrw/` 아래 원래 상대경로로 보존했다.

| 원래 경로 | 재사용 기능 | 제한 |
|---|---|---|
| `research/axbi_goal_20261014/performance/temperature_rate_table_001/src/lib.rs` | source-bound T-only 표 저장/읽기 | mutable `Cell` counters 및 AoS API는 고정99 immutable SoA API와 다르다. 그대로 대체할 수 없다. |
| `rust/rei_microphysics/src/axbi_parallel.rs` | persistent ordered worker pool | 입력/결과 순서를 유지하지만 scheduler가 floating-point reduction 정확도를 대신 보증하지 않는다. |
| `rust/rei_microphysics/src/lithium_rates.rs` | Li6/Li7의 CI/RR/DR, 12-channel 표, 별도 number state | full-chain 공통 T는 약 58,022 K–10⁷ K. 10,000 K에서는 채널별 cold-valid RR만 별도 인정할 수 있다. |
| `rust/rei_microphysics/src/isotope_state.rs` | 기존 13-state registry | Li 8개 별도 좌표와 registry를 조용히 합치지 않는다. |

Li source는 Voronov CI와 Badnell RR/DR 원본 3개 행 파일을 사용한다. 세 파일과 Li/parallel 테스트 원문도 함께 저장했다. `ElementalElectronicEquality` 정책만 제공하며 isotope-specific coefficient가 아니다. Li8/Li9은 decay/daughter closure 미완료다. 이를 RUN19에서 이식하면 기존 구현의 compatibility forwardport이지 최초 물리 모델 구현이 아니다.

기존 serializer의 `rates.bin` 9,109,725 bytes는 Git tree metadata와 생산자 기록만 읽었고 다운로드하지 않았다. 이 inventory는 선택적 원문 집합으로, donor crate 전체 복원이나 production 성능을 인증하지 않는다. 초기 compile failure와 이후 성공 receipt도 모두 원문으로 보존했다.

PR151 `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`의 R9 unit8에는 Li/Be 6개 ground channel의 total RR 및 conditional photo/Milne Python source가 이미 있다. VF1996를 native로 가져오는 새 작업은 이 선행 코드와 formula lineage를 밝혀야 한다. Be I, thermal moments, abundance, nuclear closure를 임의로 채우면 안 된다.

## 연관 저장소의 실용적 재사용

| 저장소 / 조회된 연구 head | 적용 가능한 부분 | 현재 범위 |
|---|---|---|
| BASS_HE `329f838399f24d3952f780d469ad657d8630c4e2` | case-level 병렬화와 내부 BLAS thread 1 제한, 소유 subprocess의 bounded timeout | HE29 reference 0/4. REI HHeD owner 대체 없음. |
| bass_cr `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5` | persistent native line protocol | 별도 HHe 23-field protocol/owner. RUN13 protocol과 다르다. |
| WU088_HH `efd1520dfc0643220f729307583ff0bc04b059e9` | analytical JVP와 matrix-free workspace 예 | 특정 HH partial wave 범위. REI용 thermal k(T)는 확립되지 않았다. |
| rec_bianchi `368d87ad5de90dde74226ed109c3ba29d9607c84` | history serialization cost 분리와 이미 완료한 prefix 재사용 | R3O bounded/grid lane. 저장 속도를 solver speedup으로 해석하지 않는다. |
| VigilODE `6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a` | persistent parallel coupled stage, supplied-JVP small projection | autonomous identity-mass, supplied JVP 전제. full adaptive controller/dense output 제공 아님. |

VigilODE의 재사용된 `directed.rs` Git blob `89e2b3122b08db1849e4e56cc94f1f58c473b735`는 최신 선택 tree에서도 동일하다. 새로운 coupled-stage API는 원래 DOP853이나 비자율 REI RHS에 대한 자동 정확도 인증이 아니다.

## 보존된 근거

`SOURCE_PROVENANCE.json`에는 원문 44개의 repository, commit, path, Git mode/blob, 새로 계산한 byte count와 SHA-256이 있다. 44개 합계 256,388 bytes가 원격 Git blob과 일치했다. `remote/REI_CURRENT_REFS.json`과 `remote/RELATED_CURRENT_REFS.json`은 실제 API 응답에서 필요한 ref/PR/tree만 추린 기록이다. 이번 결과의 지위는 source inventory 및 byte identity 확인이며 물리적 호환성은 해당 RUN19 구현/검증의 별도 책임이다.
