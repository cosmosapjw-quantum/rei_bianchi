# BASS_HE 다음 공변 이론 루프 — 현재 source와 열린 연결

관측일: 2026-10-13 KST / 2026-10-12 UTC. 이 문서는 현재 source 조사와 이론 착수 지점을 기록한다. 실제 파일 identity와 조회 범위는 [CURRENT_SOURCE.json](CURRENT_SOURCE.json), 초기 photon 배열의 정적 비교는 [STATIC_INPUT_PARITY.json](STATIC_INPUT_PARITY.json)에 있다.

## 1. 현재 head와 남은 의무

| 역할 | 현재 정확한 참조 | 상태 |
|---|---|---|
| 직전 이론 결과 | [BASS_HE PR31](https://github.com/cosmosapjw-quantum/BASS_HE/pull/31), `be96b0011772b47af4bd3c8e420f73153a745508`, tree `a6f219225a05c8ac73604d5219a82e128860ab04` | open draft; 직전 게시와 동일 |
| 실제 conditional receiver | [rei_bianchi PR114](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/114), `a5c958c414dea41216b445c05f58df837f05cacb`, tree `2e96362102caa69c814d477bae5d1c0177b502f9` | open draft; 직전 source와 동일 |

최근 갱신 PR을 BASS_HE 10개, rei_bianchi 15개만 조회했다. 그 범위의 최신 결과는 각각 PR31과 PR114였다. 두 repo의 `primary` 및 `covariant` branch 검색에서는 현재 BASS_HE 이론 branch 외의 해당 이름 branch가 없었다. **이 좁은 조회와 동일 receiver head에서 후속 primary-provider 구현은 관측되지 않았다.** 모든 미게시 작업의 부재를 조사한 것은 아니다.

직전 [NEXT_DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/be96b0011772b47af4bd3c8e420f73153a745508/research/rux03_primary_theory_20261012/dossier/NEXT_DAG.json), [HANDOFF](https://github.com/cosmosapjw-quantum/BASS_HE/blob/be96b0011772b47af4bd3c8e420f73153a745508/research/rux03_primary_theory_20261012/dossier/HANDOFF_KO.md), [DECISION](https://github.com/cosmosapjw-quantum/BASS_HE/blob/be96b0011772b47af4bd3c8e420f73153a745508/research/rux03_primary_theory_20261012/review/DECISION.json)의 실제 후속 의무는 여전히 `HERE_RUX03_PRIMARY_PROVIDER_03`이다. 공통 coefficient/event provider를 ordinary/conservative point, endpoint, interval/root 및 paired caller에 연결하고 실제 경로의 판별식을 실행하는 CODING 단위다.

현 사용자 요청의 공변 THEORY 확장은 이 의무를 보존한다. 기존 `RUX02 + RUX03 → RUX04 → RUX05` 의존성이나 owner 완료 상태를 바꾸지 않는다. 별도 all-Bianchi abundance-source D2.3 작업도 확장하지 않는다.

## 2. 기존 source가 이미 구현한 물리

현재 고정 [physical CONTRACT](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/CONTRACT.json)은 `-+++` signature, Einstein dust+Lambda LRS Bianchi I background 위의 test gas/radiation, homogeneous primary-only Case A escape를 명시한다. 초기 HM12 radiation은 isotropic이며 이후 anisotropic redshift를 받는다. source는 HM12 emissivity를 실제 stage energy와 volume-redshift에서 평가한다. 현재 사건은 warm FT03 CI/RR/두 DR 및 primary photoabsorption이고 CR/RCT/HH는 off다. 30000–110000 K provider 영역을 재사용한다.

기체의 closure는 charge-neutral/no-positron/all-electrons-thermal, one-temperature, nonrelativistic이다. [`AxisymCoupledState`와 `AxisymLocalSources`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs#L60-L96)에 proper species density, thermal energy, photon number/energy, `DeltaP = P_parallel - P_perpendicular`와 local scalar powers가 있다. **gas velocity/momentum, photon flux, momentum source, escape angular moment는 이 자료형에 없다.**

[`AxisymmetricPoint::snapshot`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/bianchi_i.rs#L79-L133)은

\[
a_\perp=a e^{-b},\quad a_\parallel=a e^{2b},\qquad
H_\perp=H-s,\quad H_\parallel=H+2s
\]

를 구현한다. [`CharacteristicRay::derivative`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/bianchi_i.rs#L341-L364)는 `dot E = -E sum_i H_i n_i^2`와 방향 변화식을 사용한다. source의 axisymmetric moment는

\[
\rho_\gamma=\sum_q n_q E_q,\qquad
\Delta P=\sum_q\tfrac12(3\mu_q^2-1)n_qE_q
\]

다. 이는 [현재 conditional node loop](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L368-L405)에서 계산된다.

[`axisym_coupled_derivative`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs#L233-L256)는 이미

\[
\dot u=-5Hu+Q_{th},\qquad
\dot\rho_\gamma=-4H\rho_\gamma-2s\Delta P+Q_\gamma
\]

를 소비한다. local ledger는 [`validate_sources`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs#L132-L178)에서

\[
Q_\gamma+Q_{th}+Q_{int}+Q_{esc}-Q_{ext}=0
\]

와 baryon/charge source 일치를 검사한다. `Q_int`는 thermal에서 제외한 binding/excitation/rest-energy 변화다. Case A RR/DR의 captured kinetic power는 사건률과 별개 모멘트로 공급된다.

[`axisym_conditional.rs`의 실제 work 출력](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L478-L506)은

\[
\dot W_{ref}=V\left(H\rho_\gamma+2s\Delta P+2Hu\right),\qquad V=a^3
\]

다. 따라서 `2s DeltaP` 자체를 이번의 새 결과로 삼지 않는다. 이 항을 공변 `sigma:pi` 투영과 정확히 연결하고, 같은 local source의 공간 투영을 명시하는 것이 열린 연결이다.

단위 경계도 이미 명확하다. conditional event와 photon 자료는 proper cgs 및 reference-volume cgs를 쓰고, AXI derivative에는 density를 `×10^6`, energy/power를 `×0.1` 하여 SI로 전달한다. `w`는 eV/H다. 이 변환은 [actual consumer](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L422-L464)에 있다.

## 3. 현재 photon의 μ 반전 대칭: 입력 성질과 API 조건의 구별

### 고정된 실제 초기 입력

선택된 `extended_dataset.npz`는 SHA256 `3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`, 188,284 bytes다. 이번 조사에서는 이 파일의 `q_eV`, `mu0`, `weights`, `initial_state`만 읽었다.

- **726 energy nodes × 4 angular nodes = 2,904 photon nodes**.
- **1,452개 opposite-μ pair**가 있고 짝이 없는 node나 μ=0 node는 없다.
- 모든 pair의 q, angular-energy weight, 초기 photon count가 각각 **bitwise 동일**하다.
- 뒤의 history state는 읽거나 재실행하지 않았다. 이는 초기 입력의 정적 비교 기록이다.

생성자의 [`quadrature`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/run_interval.py#L57-L69)는 `leggauss(nmu)`와 `wm/2`를 사용한다. 이 source는 selected commit에서 가져온 base64 bytes와 retained local bytes가 정확히 같았다. [`hm12_data.py`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/hm12_data.py#L168-L190)는 angle-integrated photon density/emissivity를 E,z의 함수로 반환한다. 따라서 angular quadrature의 `dmu/2`는 이미 angle-integrated 수량을 axisymmetric ring에 배분한다.

### 현재 source와 transport의 대칭 구조

production의 [`characteristics`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L107-L110)는

\[
R(\mu_0)=a^{-1}\sqrt{(1-\mu_0^2)e^{2b}+\mu_0^2e^{-4b}},
\quad E=qR,\quad \mu=\frac{\mu_0e^{-2b}}{aR}
\]

다. 같은 q에서 R,E는 μ0 반전에 대해 even이고 μ는 odd다. [`stage`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L157-L164)의

\[
S_{q,ref}=s_{log}(E_q,z)\,w_q/R_q^3
\]

도 동일 weight의 pair에서 even이다. 이는 이론적으로 source 대칭을 보이는 직접적인 식이며, 이번 조사에서 table provider를 다시 실행한 결과가 아니다.

흡수율은 같은 stage의 `c sigma_s(E) n_s n_q`이고 μ의 부호를 사용하지 않는다. 따라서 동일 pair가 같은 gas state를 공유할 때 formal node RHS는 반전에 대칭이다. 이 구조는 pair equality가 보존되는 invariant subspace와 그 위의 axial first-moment 소거를 구성할 근거다. 초기 이후에도 isotropic하다는 뜻은 아니다. anisotropic even 분포는 `DeltaP != 0`를 가질 수 있다.

### API는 반전 대칭을 강제하지 않는다

[`ConditionalPhotonNode`와 `ConditionalStage`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L84-L107)는 각 node에 독립 count/source를 받는다. [node validation](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L372-L399)은 finite, `|mu|<=1`, positive E, nonnegative count/source만 검사한다. opposite-μ pair나 동일 count를 요구하지 않는다. production loader도 [shape와 초기 UVB 일치](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L125-L143)를 확인하지만 mutable state에 반전 대칭 projection을 가하지 않는다.

따라서 **선택된 초기 입력과 source가 지지하는 even subspace**와 **일반 API의 허용 입력**을 구별해야 한다. 일반 unequal pair에는 radiation axial flux와 absorption momentum이 남을 수 있다. 현재 scalar ledger의 통과만으로 그 입력의 gas momentum 방정식까지 닫혔다고 주장할 수 없다. 실제 ODE 출력의 bitwise parity나 장기 momentum certificate는 이번 조사 범위가 아니다.

## 4. Case A escape의 정확한 위치

source 문서 자체가 [recombination은 escaped ENERGY만 기록하고 photon count는 unspecified](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L1-L7)라고 명시한다. `escape * V`는 derivative output으로 나가며, Python의 [energy ledger](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L177-L193)에 reference-volume 누적 counter로 들어간다. 이는 local escape-radiation density, spectrum, stress tensor를 진화시키는 상태가 아니다.

따라서 이번 root가 제안한 `G_gas = A - L`, comoving-isotropic Case A emission `L = (Q_esc/c) u`는 **공변 구성에서 명시할 closure**다. 현재 source가 제공한 scalar Qesc를 쓰되 angular emission 정보가 이미 구현되어 있다고 서술하지 않는다. primary absorption의 energy/direction 자료는 실제 node에 있고, 원시 events가 이를 소비한다. 공간 absorption projection을 정의하려면 이 node 정보를 사용하면 된다. escape isotropy가 필요한 곳에는 그 가정을 표시한다.

## 5. 직전 이론에서 이어받을 결과와 이번에 닫을 연결

직전 PR31에서 R00은 기존 알고리즘 재사용, T01–T07은 조건부 이론 채택이다. 특히 shared event cancellation과 `F_E=F_w+b_chi·F_v`, source normalization/ownership, endpoint-energy BE의 `-sum DeltaE N_in` work를 재사용한다. 47개 Wolfram group은 그 루프의 세 실행이며, 이번 source 조사에서 새로 실행하지 않았다.

현재 [`PrimaryPacket/PrimaryState/PrimaryStage`](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/coupled_primary.rs#L14-L37)도 energy/count, scalar escape, mean H만 가진다. photon direction이나 gas momentum을 implicit stage에 추가한 구현은 없다. 현재 primary-provider 코딩 의무는 이 사실과 독립적으로 남아 있다.

이번의 가장 직접적인 이론 단위는 다음 연결이다.

1. 기존 local Case A 사건·binding·thermal power를 지정된 u와 projection tensor의 gas energy equation에 대응한다.
2. 같은 photon absorption의 공간 four-force를 구성하고, comoving-isotropic escape 및 even photon subspace가 zero net momentum에 주는 정확한 조건을 명시한다.
3. `sigma:pi`의 LRS 표현과 기존 `2s DeltaP`를 맞추고, 연속 source ledger와 직전 finite-step work의 역할을 연결한다.
4. prescribed background, isotropic nonrelativistic gas, source angular symmetry가 제거하는 항을 명시한다. 실제 bulk-velocity/radiation-flux evolution 또는 all-Bianchi abundance-source 모델을 구현한 것으로 승격하지 않는다.

## 6. source/정책 provenance

관련 crate source 8파일은 기존 clean-build receipt의 SHA256과 일치한다. 추가로 current frozen physical CONTRACT, HM12 loader, dataset을 해당 production hash에 맞추었고, quadrature generator는 exact current Git bytes와 비교했다. 수정된 receiver source가 없어 새 archive나 source tree를 받아 복구하지 않았다.

선택된 BASS_HE base의 [AGENTS.md](https://github.com/cosmosapjw-quantum/BASS_HE/blob/be96b0011772b47af4bd3c8e420f73153a745508/AGENTS.md)를 전부 읽었다. source/derivation/evidence 분리, explicit approximations, independent review, 동일 dependency의 근거 재사용 규칙을 적용한다. receiver의 exact ref에서 `AGENTS.md`, `rust/AGENTS.md`, `rust/rei_microphysics/AGENTS.md`는 모두 없었다.

이 조사에서 remote mutation, native build/test, RHS call, ODE/history 실행은 0이다. 현재 source 및 기존 결과를 좁게 읽고, 초기 photon 배열을 정적으로 비교했으며, 이 source map만 작성했다.
