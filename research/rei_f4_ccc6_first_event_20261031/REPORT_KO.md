# REI F4 Physical Fast | original BASS193 × public CCC six-channel first inelastic event, 2026-10-31

## 판정 (2026-10-31)

**신규 실제 물리 계산 완료, canonical F4 미완료.** 원본 193개 BASS21 상태, PR302/303의 192개 Li II 2E1 도달 구간 및 3,840개 전자 소스-band에서, PR311의 공개 원저자 CCC 계보에 귀속된 **6개 부분 충돌 채널**과 PR309의 원래 전체 전자 bath Coulomb 손실을 조합해 처음 선택된 비탄성 사건의 확률·종별·에너지 요구량을 계산했다. NIST Kim (1992) PR310은 **대체 원자 이온화 모델**로 비교만 했고, CCC에 더하지 않았다.

PR311 immutable HEAD `63052797e382b438ef375e8389f539118a7e2a0c` / 부모 PR309 `701add5f6536d091350650f2b6649cded0c0de06` / read-only PR310 HEAD `6a9343f49da8287616c338de5f853bb1a0b44b5d`. 새 우주론 IVP, 생산 F/J 변화, H/K 변경, source double counting, PR merge·force push 없음. Signature (-,+,+,+), c와 ħ 보존.

## Authority, owner, provenance

물리적 primary reference: I. Bray & A. T. Stelbovics, “Convergent close-coupling calculations of electron-hydrogen scattering”, Phys. Rev. A **46**, 6995–7011 (1992), DOI `10.1103/PhysRevA.46.6995`; D. V. Fursa & I. Bray, “Calculation of electron-helium scattering”, Phys. Rev. A **52**, 1279–1297 (1995), DOI `10.1103/PhysRevA.52.1279`. 수치 공개 1차 제공자: Curtin CCC DB `https://atom.curtin.edu.au/CCC-WWW/index.html`, 2026 H I/He I 갱신. 이번 **byte owner**는 공개 EXHALE 배포 고정 Git commit `7388232fac2c3cdadad613515006de008360f1ab`에서 PR311이 source-locked한 6개 Git blob이며, 실제 입력은 원래 PR311 source-inclusive ZIP의 `inputs/ccc_adaptive_b64.json`이다. 이 data는 최대 peak σ의 0.5% 기준으로 저차원 적응 재표본화한 **근사 소스**이므로 원저자 ZIP과 byte-exact 또는 무오차 연산자 동등성은 주장하지 않는다.

여섯 채널: H I total impact ionization (`HI_ion`), H I 1s→2p, H I 1s→2s, He I total impact ionization (`HeI_ion`), He I 1s²→1s2p ¹P (`HeI_2p`), He I 1s²→1s2s ³S (`HeI_t2s`). 각 ionization threshold와 He I 24.587389011 eV source interpolation knot는 PR311 소스 owner로 고정. H I CCC tabulated σ는 a₀² 원단위를 cgs cm²로 변환, He I는 이미 cm². Source PR311 ZIP SHA256 `4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52`, 1,234,543 bytes, Google Drive ID `14DhyHe8kHlM_jagiVD9if3KEXG2zjgEz`. Original BASS Coulomb plasma CSV SHA256 `66c60518c1fe60482aa31472f0437104f52176b6b7fef3a807318dabf3efb463`. Published alternative PR310 source-band CSV SHA256 `20a1aad4e5b3fa6766139384f5cbd8e231b26789a1a77fbe84c6f1620a43162f` (plot only).

## 유도 (source conditional, 새 cosmic IVP 없음)

원래 저장 상태의 21종 전체 전하합 `n_e=n_b q^T Y`를 사용한다. 즉 PR311의 H/He-only `n_e^(HHe)`를 이번 Coulomb RHS에 대체하여 쓰지 않는다. 같은 저장 구간의 target species는 PR311의 original `n_HI=n_H(1-x_HII)`, `n_HeI=n_H y_He x_HeI`. PR311과는 달리 **first inelastic probability**를 계산한다.

`E` [eV]의 직접 전자–전자 Coulomb 연속 손실은 FS2010 Eq.(5),(12)에 따라

`b_ee(E)=-dE_eV/dt=4π(α ħ c)² n_e lnΛ/[m_e v(E) (1.602176634×10^-12 erg/eV)] >0`,

`v(E)=sqrt(2 E(1.602176634×10^-12 erg/eV)/m_e)` [cm/s],
`lnΛ=ln[4E_eV/(7.40×10^-11 (n_e/cm^-3) eV)]`.

`E>=13.7 eV`, `lnΛ>1`, 고정 화학·온도·배경만 인정. CCC channel a의 hazard per eV

`h_a(E)=n_target(a) σ_a(E) v(E)/b_ee(E)`, `[h]=eV^-1`

를 정의한다. 첫 selected 충돌이 발생하지 않을 확률은 `S(E0)=exp[-∫_13.7^E0 Σ_a h_a(E)dE]`이고, **처음** 발생한 selected channel의 확률은

`P_a(E0)=∫_13.7^E0 h_a(E) exp[-∫_E^E0 Σ_b h_b(E')dE'] dE`.

여섯 채널만 있는 **지정된 부분 모형**에서는 `S+Σ P_a=1`. 비음의 구간 hazard `Δ_a`에 대해 구간별 정확한 생존 분할 규칙

`P_a(E_{i+1})=exp(-ΣΔ)P_a(E_i)+[Δ_a/(ΣΔ)](1-exp(-ΣΔ))`,

`S(E_{i+1})=exp(-ΣΔ)S(E_i)`를 사용했다. 영 hazard 극한은 0으로 처리한다. 기준 소스 모형의 독립 transport limit을 확인하려고 이전 naive global trapezoid를 재사용하지 않았다.

원래 photon first absorber `s`와 에너지 band `b`의 입사 전자 측도 `dμ_{jsb}(E)`에 대해 원래 source가 저장한 수 `N=∫dμ`와 운동에너지 `M=∫E dμ`만 사용한다. `g(E)=P_a(E)`를 계산 그리드에서 선형 보간한 **지정된 수치 모델**의 convex minorant `co(g)`와 concave majorant `ca(g)`를 이용하면

`N co(g)(M/N) ≤ ∫ g(E) dμ(E) ≤ N ca(g)(M/N)`.

이는 해당 **piecewise-linear 확률 kernel**과 source N/M/support의 정확한 moment enclosure다. CCC 저차원 소스 자체의 물리 오차 상한은 아니다. 서로 다른 채널의 상한이 동시에 달성된다고 주장하지 않는다. 직접 H I excitation은 10.204 eV부터 가능하지만 Coulomb 식의 낮은 유효한계 13.7eV 아래는 **이번 selected first-event 계산에서 0으로 정의**했고 따라서 물리적 전부의 사건을 세지 않는다.

## 실제 출력 및 핵심 수치

193개 원래 배경 epoch × 7개 단일 초기 에너지 = **1,351 mono-response rows**; 192×4×5 = **3,840 first absorber × band physical rows**; 원본 source집계 192 rows; 10 epoch의 reference energy grid subset. 모든 숫자는 original baryon 당이며 원래 conditional Li II singlet 최대 source는 positive observation lower bound가 아니다.

- 원래 첫 광전자: `4.374110632809567e-12` /b; kinetic `6.749242464433258e-11 eV/b`.
- 선택된 여섯 CCC의 first inelastic event source-bound (within model): `[5.398784246664346e-15, 6.5003519092767815e-15]` /b; mean-energy collocation `5.409791742394313e-15` /b = 전체 original first electrons의 `0.001236775243364`.
- mean collocation **ionization**: H I `1.844220992809806e-15`, He I `8.640071116799827e-18`, 합 `1.8528576222770252e-15` /b.
- mean collocation **excitation**: H I 2p `3.035889123143908e-15`, H I 2s `5.057272527830821e-16`, He I singlet2p `6.95107998347056e-18`, triplet2s `8.368798370907945e-18`, 합 `3.556934120117288e-15` /b. 비열적 excitation은 Lyα counting이나 실제 온도 증가와 다름.
- 첫 선택된 사건마다 최소 필요 excitation/ionization threshold energy의 조건부 총량 `[6.163728374290739e-14,7.520211010996073e-14] eV/b`, mean `6.175615391028366e-14 eV/b` (원래 첫 kinetic energy의 `0.000915008672984`). 실제 가열률, 기체 총내부에너지 변화 또는 광자 재복사는 NOT_CLAIMED.
- 원래 BASS 21종 전체 electron density와 PR311 HHe-only free electron projection 최대 상대 차이 `3.8715560800525075e-05`; 혼동 없이 고정.
- 55eV mono-selected first-event probability (original BASS epoch 0 z20) ≈1; epoch60 z10.432 = 0.2350675697; epoch80 z8.3346 = 0.0005174920; epoch192 z2 = `6.173331335013188e-08`.
- 비교: PR310 NIST Kim ion-only `[6.424375422539788e-16,8.982351933188815e-15]` is a DISTINCT model and He II target is included there. NIST Kim and CCC first-event counts MUST NOT be added.

## 물리적 허용범위, 반례, 필요한 공개 원전

이 계산은 CC(6) 부분 채널에 한정되고 Coulomb energy loss 이외의 에너지 손실, He II target ionization, 추가 H/He excited n>=3, elastic, transfer below13.7 eV 및 secondary source는 누락된다. 따라서 `first six-event probability`는 실제 physical first inelastic process rate, full cascade, temperature increment, optical depth 또는 CMB source를 의미하지 않는다. 원래 BASS 배경은 고정된 193-state snapshot이고 그 사이에 갱신되지 않는다. **핵심 missing 물리는 채널 확장+에너지 재분배**, 허가받지 않은 cosmological IVP 추가나 원자 Li 교신 답변이 아니다.

공개 자료 기준: Curtin CCC 공식 `https://atom.curtin.edu.au/CCC-WWW/index.html`에서 He II `e-HeII_XSEC_LS.zip`, H/He complete author ZIP을 직접 받아 현재 reduced six-channel witness와 대조할 수 있다. 이번에는 원래 PR311의 source-locked EXHALE 표본을 정확히 재사용했고 원본 저자 ZIP과 byte-equality를 추가 주장하지 않는다. 통합 fully native REI17 isotope complete F/J는 여전히 권위 있는 owner 및 matched H,K, clock/thermal source를 필요로 하므로 별도 DAG.

## 실행 및 보존 판정

- `python code/run.py 2100`; `python -m unittest discover -s tests -q`; `python code/plot_science.py`; `python code/verify_outputs.py`; `python code/verify_manifest.py`.
- 32 same-author targeted source/physics tests PASS; 1,200→2,100 source total event estimate relative change `1.03e-6`, model numeric grid uncertainty not physical atom or BASS error.
- Source manifest/published Git and remote backup confirmations are separate from local science validation; exact final receipts in `evidence/`.
- Full physical outputs and PNG/SVG 5+5 generated; exact identity of immutable source ZIP preserved in private master. Native subagent unavailable, distinct-author R6/C9 NOT_RUN.
- **Working 33/88, Central 28/88, Physical Fast 4/7, canonical_delta=0, F4 PARTIAL, L4 false, Production HOLD, no new IVP, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false**.
