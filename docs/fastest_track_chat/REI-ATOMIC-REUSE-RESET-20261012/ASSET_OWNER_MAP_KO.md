# 원자물리·수송 자산의 소비 역할과 소유권

2026-10-12. 이 문서는 repo 이름이 아니라 **실제 물리 과정과 소비 범위**로 자산을 나눈다. 기본 원자물리의 재사용과 추가 고정밀 연구를 구별한다. 아래 core는 무조건적인 현재 admission이 아니라 선택한 scenario에서 실제 연결할 역할이다.

## 1. 통합 역할표

| 자산/과정 | 주 경로에서 쓸 부분 | 선택 확장/남은 범위 | 근거 상태 |
|---|---|---|---|
| atomic_provider / HE MICRO-0 | 선택된 H/He rate family·단면적·열 계수와 provenance | 새로운 source/domain에 대한 소비 연결, 정밀 rate 개선 | Git 함수/record 직접 확인; MICRO-0 복구는 사용자 감사 보고 |
| homogeneous_rates / CR photon stock | 종별 Γ·photon loss·binding·primary heat의 한 사건 장부 | wide propagated bound, hard-particle/secondary deposition | Git 소스 직접 확인; 182 panels/5824 points는 감사 보고 |
| coupled_primary / F08 composition | implicit stage, positivity·종/전하·에너지 장부, history composition | EoR rate/domain 주입과 time/source adapter | Git 호출 구조와 F08 campaign 원본 기록 확인; 재실행 없음 |
| Bianchi ray/packet | 기존 방향별 characteristic·양의 measure·remap | axisym 공급본/entry point의 필요한 차이, 실제 source-bound geometry | PR83 pin과 직전 source 범위; Dropbox axisym 동일성 미확인 |
| PR104 reduced | 실제 baseline 그림·partial τ·background/scalar source 참고 | full spectral source·종별/열 상태는 별도 | 기존 f66929c 범위 보존 |
| REC + BASS SYNC02/03 | 초기 history·clock·proper ne·τ/visibility API/저장 진단 | 새 EoR 입력과 observer tail, polarized sky는 별도 | SYNC03 Git 보고 원문 확인; full BASS build 주장 없음 |
| HE E13C8–C10 | 실제 지원 source/domain의 finite-path moment·감도/상계 | 2440-path 재정밀화는 목표 오차에 필요할 때만 | 감사가 보고한 고정 finite 문제; 물리/continuum 정확도 아님 |
| HH PHYS11 | 이름 붙은 반응의 electron/energy ledger와 λ,b 응답 | H− 또는 적합한 제거 폐쇄, native root/full-history | 33-group 결과는 감사 보고; 임의 IGM 외삽 금지 |
| RCT rate-only/synthetic | 해당 number-rate·알고리즘 진단 | physical escaping energy/moment와 RCT-ON 중요도 | 기존 PR112/113 비승격 범위 유지 |
| PHYS35 | 고정 source의 moment/shape root-gap 진단 | PHYS36은 observable 필요 시 선택 | 기존 제한된 결과와 소진 예산 보존 |

`bass_cr`에서 제공한 photoabsorption/heat 평가 도구를 사용하는 것과 hard-particle CR를 켜는 것은 다른 결정이다. HH/RCT/CR OFF는 선택한 baseline 설정이며 다른 repo의 독립 연구를 중지하는 지시가 아니다.

## 2. 소유권의 최소 계약

| 사건/항 | 한 번 처리할 위치 | 피할 중복/오해 |
|---|---|---|
| primary photon absorption | 선택한 primary stage 또는 대체 evaluator 한 경로 | primary sink에 homogeneous_photo_rates sink/heat를 추가하지 않음 |
| gas expansion work | 기존 primary의 thermal-work owner 또는 명시적으로 옮긴 새 owner | outer history에서 −2HT 항을 다시 더하지 않음 |
| photon redshift·각도/에너지 face flux | geometry/history owner | packet count/각도 Jacobian 중복 적용 금지 |
| 재결합 photons | explicit transport+Case A / Case-A escape ledger / Case-B OTS 중 선택 | sink·diffuse source·cooling/escape energy의 중복 금지 |
| effective MFP와 local opacity | 같은 absorber population에는 하나의 owner | 분리된 population이면 그 분해와 photon/energy 귀속을 명시 |
| spectral moments | 같은 photon measure의 σ 및 σ(E−χ) moments | 총 전이율을 미해결 differential spectrum으로 사용하거나 임의 평균 E로 heat 생성 금지 |
| HH H+ + H− | 명시 stoichiometry와 수정 전하 constraint | HII 변화만으로 free electron 증가를 단정하지 않음 |

## 3. 기존 결과와 원본 위치

- F08 Git summary: `runs/rei_fastest_v1/paired/campaign_summary.json`, blob `c67b95d0643b54d2b17394aafbdbbec51d61f9a3`. status는 `PRESCRIBED_DISCRETE_PAIRED_HISTORY_INDEPENDENT_PASS`; 15 runs/248000 accepted trials/0–10^13 s. scientific_admission과 continuum/physical claim은 별도 원문 범위다.
- F08 CSV: `runs/rei_fastest_v1/paired/paired_history.csv`, blob `5a72b7d6cecee14bd72fea1ba7cd836616bd741b`. 이번에 본 파일은 header+15 endpoint 행이며 full time curve가 아니다. 저장 그림/소스별 actual history는 별도 자산이다.
- SYNC03: `docs/research_sync/REI-REC-BASS-SYNC03-20261007/README_KO.md`, blob `0137f0eedfbb1695b9a4c5b2346388033947c284`. finite endpoint-linear ne와 조건부 tail/observer 범위의 τ·visibility 기록을 재사용한다.
- 위 세 파일의 고정 commit은 `633e0bd26b40bf59e8dfe6b977edb6e6dacc144d`다. 원본 직접 읽기는 과거 계산을 새로 검증했다는 뜻이 아니다.
- PR104는 `f66929c23ea3fa6e39dd4808e5b27d136c568a03`의 `research/broad_history_20261010/REPORT_KO.md`와 RUN002 자료를 쓴다. Q/partial τ의 기존 적용 영역을 보존한다.
- MICRO-0/HE/CR/HH 및 physical-input archive의 외부 경로는 SOURCE_MAP의 upstream registry를 따른다. 이번에 archive 내부의 소비 admission을 재검증하지 않았다.

## 4. 선택할 입력과 다음 구현

N2의 당시 결손은 해당 입력 snapshot에 대한 판정이다. v2/P01/P02A/P03A/source-delta의 존재는 새로운 완비 판정이 아니다. 선택한 계보에서 필드별로 epoch/time map, 배경/밀도, gas/radiation IC, spectral source와 역할·단위, rates/thermal domain, closure/owners, 실제 callback을 연결한다. source-null을 zero로 바꾸지 않는다.

아래는 이번에 6개 Git 경로를 제한적으로 읽어 얻은 구체적인 엔진 연결 메모다. raw coefficient 평가·수치 구조·물리 소비의 자격을 구별한다.

---

# 기존 엔진 재사용 판정과 최소 연결 변경

## 결론

계획의 주력은 **이미 구현된 H/He–열–광자 결합 수치 골격에 물리적 EoR 입력과 선택된 rate/domain 경로를 연결하는 일**이다. 첫 chemistry–Bianchi 결합 엔진을 새로 만드는 작업으로 되돌리지 않는다. 기존 prescribed-xe/Liouville 경로는 독립 대조·진단으로 유지하되 endogenous history의 선행 완료조건으로 두지 않는다.

이는 “현재 파일에 새 source만 넣으면 physical EoR solver가 완성된다”는 뜻도 아니다. 실제 코드에는 FT03 rate 경로, 온도 창, 상수 H, 짧은 시간 구간과 좁은 광자 에너지 영역이 고정되어 있다. 재사용할 수치 구조와 새로 연결할 물리 입력을 구분해야 한다.

## 이번에 확인한 근거와 source 차이

기준 Git: PR #83의 `633e0bd26b40bf59e8dfe6b977edb6e6dacc144d`. 상위 작업이 직전 `6bf81d268e827942614669f2edd978e23b78b0d1`과 같은 `rust/rei_microphysics/src` tree `cb69b4736dd046e4675557577eb8e0ead037d1f3`임을 확인했다. 이번 bounded 읽기는 아래 6경로뿐이다.

| 경로 | 이번 source 확인 | 재사용·제한 |
| --- | --- | --- |
| [atomic_provider.rs][AP] | `AtomicProvider::{record,raw_coefficient,cross_section}`, `RawRecord`, `RecombinationCase` | Grackle 고정 reference와 Verner ground-state fit이 구현되어 있다. 소스·단위·밀도 prefactor·반응별 종 변화 정보를 재사용한다. |
| [homogeneous_rates.rs][HR] | `homogeneous_opacity`, `homogeneous_photo_rates`, `OpacityOwners` | HI/HeI/HeII의 Γ·사건·heat·binding·광자 손실 장부가 있다. proper gas 밀도와 bin-integrated comoving 광자를 명시적으로 변환하며 effective MFP는 제외한다. |
| [coupled_primary.rs][CP] | `PrimaryState/Stage/Events`, `primary_stage_step_conservative`, `primary_stage_root` | packet 에너지를 stage 동안 고정한 gas–primary photon implicit 단계와 사건·에너지 장부가 실제 구현되어 있다. `lib.rs`에서 public module이다. |
| [paired_runtime.rs][PR] | `PairedState`, `paired_trial`, enclosing `endpoint` | 기하 전파→source 주입→각도 합산→실제 primary stage 호출→각 방향에 생존비율 반영→장부 누적이 이미 있다. |
| [lib.rs][LIB] | 원자·광자 public exports 및 `pub mod coupled_primary` 확인 | 현재 `paired_runtime` module/export는 없다. 이것은 이 crate의 공개 구성에 대한 사실이며 별도 실행 경로·과거 엔진 부재의 증거가 아니다. |
| `src/axisym_radiation.rs` | 이 pin의 이 경로에 404 | `GIT_PATH_NOT_LOCATED`로 제한한다. `axisym_coupling.rs`는 이번 직접 읽기 대상이 아니다. |

성공한 5파일의 blob은 순서대로 `62211d8910cd332fffa8f94c6989cae77128916e`, `d5aedfd37485b33c82a4cf0ee1d854099a517842`, `b95dbea540d9ca4347f05d3aef76164e668e2d5f`, `70eed18b07b6dd4297d8ef8da6d7e1be8e44456e`, `b74d04636d6918dfb20e81506123b3256fc15d94`이다.

**Dropbox 관측본은 별도 층위다.** 사용자 첨부 감사는 `/bianchi/rei_bianchi/rust/rei_microphysics/src/`에서 두 axisym 파일과 공개 API를 관측했다고 보고한다. 이번에는 그 Dropbox bytes나 빌드 entry point를 다시 읽지 않았으므로 Git pin과 같다고도, 존재하지 않는다고도 판정하지 않는다. 후속 구현에서 실제 사용할 **한 실행 경로**의 source/entry point만 연결하면 된다. 모든 branch·백업의 전수 대조를 새 선행조건으로 만들지 않는다.

**F08 실행 성과는 보존한다.** 첨부가 인용했고 상위 작업이 Git 원본도 확인한 [campaign_summary.json][F08]은 15 histories, 248,000 accepted trials, prescribed `10^13 s` 구간의 기록이며 이전 PR83 snapshot에도 이 범위의 실행 성과가 보고되어 있다. 이번 source 읽기는 실제 결합 호출 구조를 확인한 것이고, 그 캠페인의 실행·오차를 재검증한 것이 아니다. CSV endpoint 차이를 재산술하지 않았다. Git export 차이로 이 기존 실행 근거를 무효화하지 않는다.

## 재사용할 골격과 새로 연결할 물리 경로

### 1. 기존 엔진 소유권을 유지한다

`coupled_primary`는 stage의 H/He 반응·광자 흡수·binding/heat·escape·가스 팽창 work를 소유한다. 실제 RHS에 `-2 H_mean w`가 있고 `PrimaryEvents::thermal_work_ev_per_h`가 있다. 바깥 history는 배경·proper 밀도·광원·방향별 redshift·spectral face flux와 광자 redshift work를 소유한다.[CP][PR]

따라서 axisym 결합에 가스 팽창 냉각을 다시 넣거나, primary의 흡수에 `homogeneous_photo_rates`의 sink/heat를 추가하여 같은 사건을 두 번 세면 안 된다. homogeneous 장부는 선택한 경로의 adapter 또는 대조 평가로 사용한다. 물리 source·escaped recombination photons·Case A/B·local opacity/effective MFP의 owner도 이 호출 경계에 붙인다. scalar rate를 고른 사실만으로 미확인 differential emission spectrum까지 승인하지 않는다.

### 2. FT03 고정 rate/domain을 EoR 입력과 연결할 adapter가 필요하다

현재 `PrimaryStage` 입력은 `n_h_cm3, f_he, h_mean_per_s`뿐이다. 내부에서 `Ft03Model::controlled()`, `ft03_rhs`, `ft03_coefficients(T)`를 호출하고 단면적에는 `AtomicProvider::reference()`를 직접 사용한다. 즉 raw 원자 공급자에 새 값을 마련하는 것만으로 실제 primary 실행 경로의 rate가 바뀌지 않는다.[CP]

최소 변경은 기존 implicit step·사건 장부를 유지하면서 **선택된 rate/thermal provider와 validation domain을 stage에 전달하는 adapter/injection 지점**을 추가하는 것이다. 확보된 EoR rate family 또는 기존 physical receiver의 경로 하나를 source 고정하여 연결한다. 구체 provider 선택은 physical-input intake에 의존하며 새 원자 계산은 요구하지 않는다.

root/interval 경로를 함께 사용할 때에는 point RHS와 같은 provider/domain을 연결한다. point 계수만 바꾼 뒤 기존 FT03의 수치 상계를 새 rate의 증거로 재라벨하지 않는다.

- `coupled_primary::valid`는 현재 30,000–110,000 K, paired guard는 35,000–60,000 K이다. 물리 이력의 온도 영역을 먼저 확인하고 그 영역을 지원하는 rate와 열 closure를 연결한다. guard 숫자만 넓히지 않는다.
- `AtomicProvider::record`의 `consumer_admission=false`, `physical_support_resolved=false`와 100–10^9 K reference guard는 **이 legacy raw 공급자가 physical consumer로 자동 승인되지 않았음**을 뜻한다. Grackle 계수 자체가 무효라는 판정이 아니다. API의 넓은 계산 가능 영역과 선택한 물리 모델의 지원 영역을 구분한다.[AP]

### 3. fixture 상수는 scenario와 시간 계약으로 옮긴다

`paired_runtime`의 `SOURCE=5e-15`, `BIRTH=13.7 eV`, 초기 `T=50,000 K`, `nH(t)=10^-4 exp[-ΣH_i t]`, 상수 directional H, `t≤10^13 s`, 10–20 eV 노드와 미구현 upper guard는 S0 전용 구성이다.[PR] 이것들을 새 runtime 전체로 복제하지 말고 아래 입력 경계만 분리한다.

- 선택한 physical epoch, `a_i(t),H_i(t)`, proper `nH,nHe`, IC와 `t↔ln aV/zV` 매핑.
- spectral emissivity·escape/clumping·경계 광자 inventory와 source의 단위/시간·각도 convention.
- 해당 스펙트럼의 HI/HeI/HeII support, 에너지 경계 유출입, source/opacity/rate domain과 callback.

기존 `igm_background`의 `ln(a)/z` adapter는 앞선 소스 확인에서 proper-time 역변환을 제공하지 않았으므로 ln(a)를 seconds로 넘기지 않는다. time map은 한 owner가 관리한다. 광자 per-H, comoving cMpc⁻³, proper cm⁻³를 자동 혼용하지 않고 하나의 변환 지점을 둔다.[HR][CP][PR]

13.7 eV 단일 source·20 eV 상한의 F08은 He 광이온화를 시험하지 않는다. 그렇다고 spectral 상한만 넓혀 physical source가 마련되었다고 하지 않는다. 선택한 광원 history와 He를 포함하는 주장 범위를 함께 고정한다.

### 4. 다음 실제 구현 단위를 작게 유지한다

후속 순서는 **이미 보존된 성과 사용 + 한 physical scenario 선택 → rate/domain·time/source adapter → 기존 stage로 첫 FLRW coupled interval → 같은 입력의 Bianchi interval → 선택된 다중 epoch history**다. 이번 문서는 이 순서를 계획할 뿐 실행하지 않는다. 기존 F08/SYNC02/SYNC03 또는 완료된 원자 정밀 계산의 재실행을 첫 interval의 의무로 두지 않는다.

비교에는 동일한 `H(t)`·밀도·광원·IC·epoch의 isotropic-transport 대조군을 두어 배경 변화와 방향별 수송을 구분한다. F08의 유한 구간 성과를 physical EoR, continuum sign, 관측 가능한 anisotropy 또는 homogeneous `xHII=Q_V`로 승격하지 않는다. HE/CR/HH 정밀 확장은 관측량 민감도가 필요성을 보여줄 때 소비하며 기본 H/He 결합을 막지 않는다.

## 조회·행동 범위

첨부 `REI_ATOMIC_REUSE_PLAN_20261012(5).md`, `Pasted text(20261012-072016).txt`, 직전 로컬 원천정보와 위 Git 6경로만으로 판단했다. 과학 실행·scientific import·test·원격 mutation·archive 전수 다운로드는 0회다. 과거 시험의 PASS는 보존된 보고 범위이고 이번 재검증 결과가 아니다.

[AP]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/atomic_provider.rs
[HR]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/homogeneous_rates.rs
[CP]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/coupled_primary.rs
[PR]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/paired_runtime.rs
[LIB]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/lib.rs
[F08]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/runs/rei_fastest_v1/paired/campaign_summary.json
