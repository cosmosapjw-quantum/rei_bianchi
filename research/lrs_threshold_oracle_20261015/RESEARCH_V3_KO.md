# rei_bianchi: LRS Verner photon–H/He dynamic chemistry reference, 2026-10-16

연구 범위: 기존 독립 PR #152(`bbbd18b5c16eff70bc32ba4296360dceb9060ec4`)에서 분기하는 새로운 연구 단위. 원본 v3/rux DAG, PR #150 FLRW production, PR #151 microphysics, PR #149 Case-A source를 수정하거나 대체하지 않는다.

## 출처와 검증 지위

- Source literature: Verner et al. (1996), ApJ 465, 487, DOI: 10.1086/177435. PR #152에 원본 185행 donor 고정.
- Comparison literature: Pawlik & Schaye, arXiv:1008.1071 (multifrequency H/He RT), Friedrich et al., arXiv:1201.0602 (He/X-ray extension of photon-conserving C2-Ray).
- 이번 실행: ChatGPT 실행 컨테이너 Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2. **사용자 Ubuntu 및 64-vCPU NCP에서는 이번 구현을 실행하지 못했다.** Desktop Commander 월간 사용 한도 도달로 원격 명령이 차단됨. NCP 연결과 rustc 1.99.0은 제한 전 읽기 작업으로 확인했다.
- 실제 테스트: 신규 21개 pytest PASS, 독립 Radau continuous RHS 기준해 비교, step-refinement, strong absorption positivity, isotope stage conservation, ray parity/FLRW isotropy.

## 변수·가정·단위

`(-,+,+,+)`, `ds²=-c²dt²+a²e^{-2b}(dx²+dy²)+a²e^{4b}dz²`, `X=ln(a/a₀)`, `b=(s/H)X`이고 signed `s/H` 일정. `Σ=√3|s|/H`; orientation `sgn(s)` 별도. `E_r(X)=E_{r0}e^{-X}√[(1-μ₀²)e^{2b}+μ₀²e^{-4b}]` (eV).

모든 입자수와 광자수는 초기 comoving 부피당 n★로 정규화한다. 원자종 스톡 `M_HI`, `M_HII`, `M_HeI`, `M_HeII`, `M_HeIII`; photon ray 스톡 `N_r`. `n★`는 정규화 기준 proper 초기 number density(m⁻³). `H₀`(s⁻¹). Verner `σ_i(E)`는 Mb, `1 Mb=10⁻²²m²`. 입력 `rate_per_mb = (c n★/H₀) × 10⁻²²m²` (무차원/Mb).

실제 작동 hazard:

`λ_{ri}(X) = rate_per_mb · exp(-3X) · σ_i[E_r(X)]/[H(X)/H₀]`,

`A'_{ri}=λ_{ri} N_r M_{target(i)}`,

`N'_r=-Σ_i A'_{ri}`,

`M'_HI=-Σ_r A'_{r,HI}`, `M'_HII=+Σ_r A'_{r,HI}`,

`M'_HeI=-Σ_r A'_{r,HeI}`,

`M'_HeII=+Σ_r A'_{r,HeI}-Σ_r A'_{r,HeII}`,

`M'_HeIII=+Σ_r A'_{r,HeII}`.

자유전자 스톡은 독립 ODE가 아니라 `M_e=M_HII+M_HeII+2M_HeIII`. 재결합/재방출, collisional ionization, Thomson, source emission, gas temperature ODE, hydrodynamics 및 metric Einstein backreaction은 없다. 초기 광자만 진화하는 **조건부** 검증 문제다.

## 정확한 개별 반응과 전체 합성

고정된 local rate `κ`에서 `dN/dX=dM/dX=-κNM`은 `D=|N₀-M₀|`, `B₀=min(N₀,M₀)`로 풀 수 있다:

`B(t)=B₀D exp(-Dκt)/[D+B₀(1-exp(-Dκt))]`,

`D=0`에서는 `B=B₀/(1+B₀κt)`. `A=B₀-B(t)`는 `0≤A≤min(N₀,M₀)`. Wolfram Language로 미분방정식 잔차 0 및 positivity 검산.

구현: 모든 ray×channel에 대해 (1) 정확한 spectral threshold crossing 분리, (2) 배경·Verner 단면적을 timestep midpoint에서 평가, (3) 개별 positive reaction exact map을 순방향 half-step과 역방향 half-step으로 합성(대칭 Strang), (4) 전후 half drift 에너지는 정확한 특성곡선으로 평가. 각 reaction마다 `E_threshold A`를 binding, `(E_mid-E_threshold) A`를 electron excess heating ledger에 적립.

중요한 발견: ray를 무차별적으로 순차 적용하면 FLRW에서 `Π/U~10⁻⁸`의 **가짜 angular stress**가 생길 수 있다. 동일 초기 E₀이며 동일 동역학 characteristic(FLRW에서는 모든 μ, Bianchi에서는 ±μ)인 ray들을 group으로 합산하고, 같은 생존비율을 각 ray에 적용하면 이 spuriosity가 제거된다. 이 집단화는 동일 absorption rate를 공유하는 ray들의 수학적 정확한 합산이다. 별도 reflection/isotropy 테스트를 추가했다.

## 보존법칙 및 검산과 의미

`H_total=M_HI+M_HII=const`, `He_total=M_HeI+M_HeII+M_HeIII=const`.

광자수/자유전자: `Σ_r N_r(X)+M_e(X)=Σ_r N_r(0)+M_e(0)`.

binding storage `B=Σ_{ionized events}E_threshold ΔA`, excess electron kinetic `Q=Σ(E_mid-E_threshold)ΔA`.

energy: `Σ_r N_r(0)E_r(0)=Σ_r N_r(X)E_r(X)+B+Q+W`,
where `W` is source-free geometric redshift/shear work computed as **exact discrete split drift**. 따라서 에너지 잔차가 machine precision임은 scheme의 회계 구조를 뜻할 뿐, 연속체 해 수렴의 증명은 아니다. 이를 독립적인 SciPy Radau direct continuous RHS, exact event partition, 다양한 `ΔX_max`에서 비교했다.

## 수치 시험 원시 설정 및 판정

초기 gas `(HI,HII,HeI,HeII,HeIII)=(0.37,0.03,0.085,0.012,0.003)` (`n★` units). 초기 photon spectrum `(E0[eV],N0)=(110,0.12),(72,0.08),(43,0.06)` 각각 GL8 μ-quadrature weight/2. `X_end=0.65`, prescribed `H/H0=1`, rate_per_mb=2, `s/H∈{-0.04,0,+0.04}`.

`ΔX_max=0.005` 기준 독립 Radau 결과와의 최대 state/binding/heat/work 절대차 (서로 다른 단위의 출력 함께 비교하므로 **원시 수렴 진단 값**): 
- `s/H=-0.04`: `3.91965e-6`;
- `s/H=0`: `4.13072e-6`;
- `s/H=+0.04`: `3.94854e-6`.

최종 electron/cosmological angular quadrupole `M_e, Π/U`:
- `s/H=-0.04`: `0.075176194`, `+0.043021788`;
- `s/H=0`: `0.075175622`, `~0` (≤2e−14 tested);
- `s/H=+0.04`: `0.075176115`, `−0.041437005`.

최대 number-electron residual ~1e-16, 최대 energy ledger residual ~1e-14 eV/n★ in this benchmark. 

## 재현 및 이후 연결

`python -m pytest -q tests/test_dynamic_chemistry.py`

`python run_dynamic_benchmark.py`

`evidence/dynamic_chemistry_radau_convergence.json` contains full raw 3×5 convergence rows, invariant residuals, source inputs and numerical statuses.

PR #150 native adapter의 연결 전 필요한 확인: 실제 native transport moment/angle representation, gas state units and normalization, source term and recombination signs, Verner donor identity, discrete coupling direction, temperature-energy bookkeeping, radiation `Π_ab` mapping, conservation and convergence tests. 본 PR 자체가 production integration을 구현하거나 실제 EoR 신호를 추정하지는 않는다.

**Claim gate**: analytic pair flow `derived + Wolfram-checked`; discrete implementation `sandbox-test-verified`, direct Radau error/convergence `numerically checked`; original Ubuntu/NCP integrated execution `NOT_RUN`; publication as astrophysical EoR result `HOLD`.
