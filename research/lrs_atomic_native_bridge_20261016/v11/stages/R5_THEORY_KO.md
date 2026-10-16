# REI LRS V11 R5: photon-off CI/CE/free-free/CMB 시간 배치

## 정확한 출발점과 보호 범위

- Parent: `rei_bianchi` Draft PR172, head `c91ba18a38b744a1e64ff40423f02a35f2999605`.
- Native owner는 PR150 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`로 고정한다. 최신 PR150은 병렬 진행 중이므로 변경하지 않는다.
- 실제 owner의 `rust/rei_microphysics/src/igm_rates.rs` SHA256 `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`, `igm_thermal.rs` SHA256 `30515d96270ec73a37829ba298513a42112991168479d3cb40f33b67fd469ab2`, `igm_state.rs` SHA256 `1651b00a517d67aaa71b38d3c69af6413570adfc38b591a3ed25284f039e0ae0`.
- Source-free means photon count/source=0, NOT CI/CE/CMB=0. Signed Bianchi/stellar source/Case B/EoR 결과 아님.
- `X=ln(a/a0)`, FLRW `a=a0 exp(X)`, proper `n_H(X)=n_H0/a³`, `dX=H dt`, 모든 stock과 energy per *total H nuclei*. Signature `(-,+,+,+)`.
- HII/HeII/HeIII native fractions `(x,y,z)`, total He/H number ratio `Y`, electron abundance `e=x+Y(y+2z)`.
- Thermal storage `W=3 k_B T (1+Y+e)/(2 eV_erg)` eV/total H; chemical binding B in eV/H.

## Owner microphysics and ledger

Exact original owner Grackle3.4.1 commit `af7939494ce65007887ada7b98d1813df6843346` Case-A rates:
`CI=[n_e(1-x)k1, n_e Y(1-y-z)k3, n_e Y y k5]`,
`RR=[n_e x k2, n_e Y y k4_RR, n_e Y z k6]`, `DR=n_e Y y k4_DR` in s^-1 per H; divide each by H to convert to X rates.
`CE_HI=n_e n_HI c_CE_HI / n_H`, `CE_HeI=n_e² n_HeII c_CE_HeI / n_H` (metastable HeI), `CE_HeII=n_e n_HeII c_CE_HeII/n_H`, `free-free=n_e (n_HII+n_HeII+4 n_HeIII)c_ff/n_H`, in erg/H/s; divide by H*EV_ERG to get eV/H/X. CMB signed gas input from original Planck blackbody `4σ_T a_rad k_B /(m_e c)*n_e Tcmb^4(Tcmb-T)` in cgs energy volume/time; divide by n_H H EV_ERG. Recombination ionization binding and CI thermal are **single-owned**; CE/ff radiation escape is separate; CMB reservoir signed.

Discrete internal energy equation with micro process rates evaluated at one of old/mid/end states:
`ΔW_micro=−Σ χ_i ΔCI_i − Σ ΔQ_RRDR − Σ ΔQ_CE − ΔQ_FF + ΔE_CMB`.
`ΔB=Σ χ_i (ΔCI_i−ΔRR_i−ΔDR_i)` with proper HeII DR binding.
`ΔE_escape=Σ χ_i(ΔRR_i+ΔDR_i)+Σ ΔQ_RRDR+Σ ΔQ_CE+ΔQ_FF`.
Exact adiabatic half maps satisfy gas work `ΔW_gas=W_before−W_after` for each half. Then exact per-step ledger identity:
`W_init+B_init=W_final+B_final+W_gas+E_escape−E_CMB`.
This identity holds for any consistent choice of micro clock phases, including inaccurate BE. It **does not certify temporal order**.

## R5 general clock decomposition

For a smooth local source-free autonomous microphysical system `q'=F(q)=Σ_j F_j(q)` at the *same fixed midpoint FLRW geometry*, write a mixed-clock update
`q_+=q+h Σ_j F_j((1-θ_j)q+θ_j q_+)`, where θ_j=1 for endpoint BE and θ_j=1/2 for state-midpoint.
Expanding around q gives

`q_num−q_exact = h² Σ_j (θ_j−1/2) D F_j(q)·F(q) + O(h³)`.

Wolfram Language checks this identity symbolically in a two-channel model; for full vector fields `DF_j` is a Jacobian matrix. Exact gas geometry splitting removes the linear adiabatic equation from the microthermal solver, but commutators give O(h³) local errors only for smooth prescribed background. One wrongly timed remaining term generically leaves global O(h), even with RR midpoint. Cancellation is possible, so estimate signed state errors against independent continuous Radau, not only conservation and self-differences.

## Falsifiable hypotheses / controls

- BE all: first order, source-off baseline PR172. This output is compared to the independently reported native V10 `N=128,T=14988.7611352303 K`, not treated as the native executable.
- State midpoint all rates: formal O(h²) global for nonstiff smooth solutions and converged nonlinear root, no uniform stiff positivity theorem.
- Midpoint CI, midpoint CE, midpoint FF, midpoint CMB **one at a time** isolate process-specific leading signed errors.
- Midpoint CE+FF+CMB but endpoint chemistry, and conversely chemistry-mid + thermal-end, should generally retain O(h).
- Four-channel RR/DR cooling separately counted; Grackle CI floor, CE cap, HeI metastable n_e², actual TCMB(a) and total-H proper density required.

## Literature and scope

- Grackle 3.4.1 original `src/clib/rate_functions.c` at frozen commit, original C literal reference checked against 96-row all-temperature table.
- Anninos et al., *Cosmological Hydrodynamics with Multi-Species Chemistry and Nonequilibrium Ionization and Cooling*, 1997, astro-ph/9608041: non-equilibrium chemistry/thermal source and BDF stability; not a second-order proof for this owner.
- Norman et al., *Fully Coupled Simulation of Cosmic Reionization I*, ApJS 216:16 (2015): radiation-thermochemistry splitting accuracy contextual reference; transport differs from this oracle.

**Claim ceiling:** derived local error decomposition and conditional source-free microphysical parity only; PR150 source-on original 2nd-order and isolated native Rust thermal clock sweeps NOT_RUN; all actual source-age/Case B/full EoR/signed Bianchi remain HOLD.
