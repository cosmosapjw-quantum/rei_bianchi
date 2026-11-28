# Moving-gas THEORY05 — 현재 source와 재사용 경계

현재 [BASS_HE PR32](https://github.com/cosmosapjw-quantum/BASS_HE/pull/32)와 [rei_bianchi PR114](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/114)의 head는 직전 게시와 같다. **현재 production state에는 lab gas velocity·momentum primitive가 없다.** 이번 이론의 연결점은 이미 채택한 rest-frame 사건 four-force를, 속도가 바뀌는 고정 Eulerian 체적의 유한 source stage와 gas primitive recovery에 연결하는 것이다.

관측 시각은 2026-10-12 UTC / 2026-10-13 KST다. 조회 범위·정확한 파일 identity·실제 로컬 경로는 [CURRENT_SOURCE.json](CURRENT_SOURCE.json), 이전 과학 결과의 재사용 목록은 [VALID_REUSE_IDENTITY.json](VALID_REUSE_IDENTITY.json)에 기록했다. 이 source 조사는 새 native 실행이나 과학 계산을 포함하지 않는다.

## 1. 현재 정확한 기준

| 역할 | Head / tree | 현재 상태 |
|---|---|---|
| BASS_HE PR32 | `ca85cfc7353da190613f7fb37a6e0ffed9b51913` / `92945aa1d8f6d56cc1c05dc322100fb6c435e054` | open draft; 직전 covariant THEORY 게시와 동일 |
| rei_bianchi PR114 | `a5c958c414dea41216b445c05f58df837f05cacb` / `2e96362102caa69c814d477bae5d1c0177b502f9` | open draft; 직전 source-bound receiver와 동일 |

각 repo의 생성 시각순 최근 PR 10개에서 더 새로운 PR은 없었다. BASS의 `research/rux03-moving` 및 receiver의 `research/he-moving` ref-prefix 결과도 비어 있다. 이 bounded query에서 후속 moving-gas 구현이나 primary-provider 완료는 관측되지 않았다. 이름이 다른 모든 미게시 branch를 조사한 기록은 아니다.

PR32의 직전 검증된 diff는 covariant 단위 59개 파일 추가뿐이다. 따라서 root AGENTS의 기존 전체 읽기와 blob `8119a57e3c9f7b8c22a3532c9f88e430df1cebbf`를 재사용한다. 현재 receiver commit도 같으므로, root/rust/crate AGENTS의 이전 exact-ref NOT_FOUND 결과를 재사용한다. 새로 내려받아야 할 changed source는 없었다.

## 2. 실제 상태와 프레임

| 실제 구조 또는 변수 | 현재 의미 | moving stage에서 연결할 항목 |
|---|---|---|
| `ConditionalStage` | 시간, prescribed geometry, proper `nH,nHe`, fractions 3개, `w`, photon nodes | gas bulk velocity, Lorentz factor, conserved Eulerian `D`와 gas total energy/momentum |
| `ConditionalPhotonNode` | `energy_ev`, `mu`, reference photon count와 source | lab photon 방향과 gas-frame Doppler energy·density의 구별 |
| `AxisymCoupledState` | isotope proper densities, thermal energy, photon number/energy/pressure difference | lab gas momentum 및 conservative-to-primitive recovery |
| `PrimaryState` | fractions 3개, thermal `w`, scalar escape, 방향 없는 `energy_ev,per_h` packets | 유한 moving common stage의 새로운 변수 대응 |
| `AxisymLocalSources` | species/electron/photon counts와 scalar energy powers | absorption 및 escape의 공간 momentum source |

근거: [conditional structs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L85-L128), [coupled structs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_coupling.rs#L59-L96), [primary structs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/coupled_primary.rs#L13-L57).

현재 [physical CONTRACT](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/CONTRACT.json)은 prescribed Einstein dust+Lambda LRS Bianchi I 배경의 test gas/radiation, homogeneous primary-only Case A escape, one-temperature internal gas를 사용한다. 배경 provider의 시간은 comoving background의 proper elapsed seconds이며 `nH*a_rel^3`와 `nHe*a_rel^3`가 일정하다. gas가 그 프레임에 정지한 현재 경로에는 별도 lab/rest time 변환이 없다. [background.py](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/background.py#L1-L6), [density output](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/research/physical_provider_20261010/background.py#L113-L126)

Python `integrate`의 `tau=t/end`는 solver 변수의 무차원화다. gas proper time을 뜻하는 기호가 아니다. `dt`를 받는 primary/FT03 stage도 현재 같은 정지계에서 proper rate를 시간 적분한다. [source_bound_interval.py](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L197-L203), [FT03 endpoint](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_controlled.rs#L231-L274)

## 3. Fraction·열·시간 정규화

현재 소스의 변수 대응은 다음과 같다.

\[
x=\frac{n_{\rm HII}}{n_H},\quad
a=\frac{n_{\rm HeII}}{n_{\rm He}},\quad
b=\frac{n_{\rm HeIII}}{n_{\rm He}},\quad
f=\frac{n_{\rm He}}{n_H},\quad
n_e=n_H[x+f(a+2b)].
\]

CI/RR/DR/photo event는 proper \({\rm cm}^{-3}{\rm s}^{-1}\)이다. edge net rates를 \(J_0,J_1,J_2\)라 하면

\[
\dot x=J_0/n_H,\qquad
\dot a=(J_1-J_2)/n_{\rm He},\qquad
\dot b=J_2/n_{\rm He}.
\]

두 DR 항은 모두 HeII→HeI edge의 \(J_1\)에서 뺀다. finite primary event는 `dt*rate/nH`이므로 per-H event count와 helium fraction 분모 `nHe`를 구별해야 한다. [FT03 event/RHS](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_controlled.rs#L93-L177), [primary event normalization](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/coupled_primary.rs#L272-L292)

\[
u_{\rm th}=n_H\epsilon_{\rm eV}w,\qquad
T=\frac{2\epsilon_{\rm eV}w}
 {3k_B[1+f+x+f(a+2b)]},
\]

\[
B=\chi_0x+f\chi_1a+f(\chi_1+\chi_2)b.
\]

실제 primary의 scalar energy는 \(w+B+e_{\rm esc}+\sum_q e_qp_q\)다. `HHeModel::total_energy`도 thermal+binding+photons+escape를 더한다. 움직이는 gas의 총 lab energy나 bulk kinetic energy 항을 보유하지 않는다. THEORY04의 neutral reference mass를 포함한 \(\rho_g,p_g,T_g^{ab}\)는 채택된 constitutive 이론 대응으로 재사용한다. [native thermal/energy](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/hhe_events.rs#L133-L178), [primary scalar energy](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/coupled_primary.rs#L216-L221), [THEORY04 §5](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/derivations/COVARIANT_EVENT_EXCHANGE.md#L202-L286)

## 4. Photon·외부 source·escape의 소유권

현재의 \(V=a_{\rm rel}^3\), \(N_q=Vn_q\), \(e_q=qR_q\)와 source

\[
S_q=j_{\log}(e_q,z)\,w_q/R_q^3
\]

는 source-bound Python caller가 같은 시간·상태에서 준비한다. proper absorption event는 native에서 \(\mathcal R_{iq}=c\sigma_i(e_q)\ell_iN_q/V\)로 계산한다. 이 경로의 photon energy는 gas/background common frame의 에너지이고, Doppler transform이나 moving number-current 변환은 호출에 없다. [one-stage source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L156-L173), [actual opacity](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L335-L420)

`SourceBoundConditional::evaluate_detailed`가 FT03 provider를 선택한다. `ft03_rhs`에서 받은 CI/RR/DR와 captured kinetic powers, 같은 node에서 계산한 photo event는 하나의 owned `CaseAEventBundle`로 모인다. `into_ledger`가 이를 한 번 소비해 species·열·binding·photon·escape source를 만들고, 그 source를 실제 `axisym_coupled_derivative`에 전달한다. `EVENTS`는 그 호출의 결과 요약이다. [entry/provider](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L42-L56), [owned bundle](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L189-L294), [actual consumption](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L448-L466)

RR escape power는 \(\chi_iR_i^{\rm RR}+P_{i,\rm kin}^{\rm RR}\), 두 DR 항은 \(\chi_{\rm HeI}R_k^{\rm DR}+P_{k,\rm kin}^{\rm DR}\)를 더한다. primary photon birth는 외부 HM12 source가 소유하며 recombination을 diffuse photon birth로 되넣지 않는다. 기존 escape 출력은 energy counter이고 photon number 및 angular spectrum을 지정하지 않는다. gas-frame isotropic escape \(\mathcal L^a=(Q_{\rm esc}/c)u^a\)는 THEORY04의 명시적 closure로 재사용한다. [native escape ledger](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L258-L287), [THEORY04 escape closure](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/derivations/COVARIANT_EVENT_EXCHANGE.md#L105-L151)

escape·work·external source energy의 실제 적분 변수는 reference-volume scalar counters다. 현재 work `V*(H*rho_gamma+2*s*DeltaP+2*H*u_th)` 및 그 finite endpoint-energy 해석은 이미 확보된 내용이다. [native counters/work](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs#L478-L515), [counter observables](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/python/source_bound_interval.py#L175-L195)

## 5. 그대로 전달할 provider 정의역

FT03의 gas-frame 온도 정의역은 \(30{,}000\le T\le110{,}000\) K다. Verner는 finite \(0\le e\le50{,}000\) eV를 받으며 species fit cutoff 아래에서는 0을 반환한다. moving stage는 **Doppler 변환 뒤의 gas-frame energy**에 이 조건을 적용해야 한다. lab energy의 상한만으로 native fit의 유효범위를 승계할 수 없다. [FT03 guard](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_rates.rs#L24-L27), [Verner guard](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/atomic_provider.rs#L327-L353)

Fit cutoff `(13.60, 24.59, 54.42)` eV와 binding/heat threshold `(13.598434599702, 24.587389011, 54.41776)` eV를 계속 구별한다. 후자는 \(\chi\)이고 photoheat는 full gas-frame energy에서 \(\chi\)를 뺀다. 선택된 warm Case A provider와 optional CR/RCT/HH OFF 조건은 유지한다.

## 6. 재사용할 결과와 이번 열린 연결

THEORY04는 rest-frame four-force, neutral-reference gas constitutive law, covariant energy/momentum projections, weighted-force condition 및 paired finite work를 채택했다. §7의 observer projection은 **이미 구성한 four-force를 다른 observer로 투영**한 식이다. finite moving stage의 Doppler opacity·event·gas state를 동시에 해결하는 작업은 직전 [NEXT_DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/dossier/NEXT_DAG.json)와 [HANDOFF](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/dossier/HANDOFF_KO.md)가 지정한 새 구성 의무다.

재사용할 45개 THEORY04 check group과 47개 PRIMARY_THEORY03 group의 identity는 그대로 유지한다. 이번 source 조사에서 이를 다시 실행하지 않았다. fixed common-frame angular pairing의 가정을 일반 tilted lab 분포에 자동으로 적용하지 않는다.

새 연결은 고정 local Eulerian 체적에서 `D=gamma*nH` 보존, lab photon 에너지·방향·count, gas-frame event rates, total lab energy/momentum update, 물리적인 gas primitive recovery를 같은 stage에 배치하는 것이다. zero velocity, one beam 및 paired limit에서 기존 결과와의 대응을 구성한다. 이 source 문서는 그 수학적 존재성이나 완성을 판정하지 않는다.

`HERE_RUX03_PRIMARY_PROVIDER_03`는 여전히 첫 CODING 의무이며, `HERE_RUX03_COVARIANT_MOMENTS_04` 구현도 pending이다. 별도 all-Bianchi abundance-source/reference-current/class-B/relative-species-tilt D2.3 범위는 유지한다.
