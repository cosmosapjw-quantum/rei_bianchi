# R5: optical-depth birth-age quadrature in stiff H/He radiation

2026-10-16 KST. Independent research stacked on original [PR171](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/171) HEAD `c07ba9b839aa003a7b9afb3c6be9adce24761eeb`. Its original native MD14+Grackle executor is `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`; **unmodified**. This unit is **conditional prescribed-opacity math**, not a source-matched native solve.

Let `u=(ln a-ln a0)/Δln a∈[0,1]`, with per-u photon birth `j(u)≥0`, photon loss `κ(u)>0`, one fixed Killing momentum ray and `N'=j-κN`. Put `K(y)=∫_y^1 κ(u)du`, `τ=K(0)`, `z=K(y)`. The source solution is **exactly**:

```
N(1)=N(0)exp(-τ)+∫_0^τ exp(-z) [j(y(z))/κ(y(z))] dz.
```

For `0≤j/κ≤M`, the omitted `z>Z` contribution is bounded by `M exp(-Z)`. Split optical-depth quadrature at physical HeI photo-fit threshold crossings; `κ=0` intervals need a different clock. This is an integrating-factor change of variables, **not a new general no-go theorem**.

Manufactured positive case: `κ_H=120+20u`, `κ_HeI=180·1_(u<0.992)`, `κ_HeII=0`, `j=1e-4(1+0.6u)/H` where `/H` here means *per hydrogen nucleus*, **not Hubble**; `Δln a=.002`. Total `τ=308.56`, threshold `z_cut=1.11936`. Exact signed LRS energy:
`E(u)=24.59 exp(-Δu) sqrt((1-μ0²) exp(2qΔu)+μ0² exp(-4qΔu))/F(u_cut)` eV, with `q=s/H`, local direction dynamically changing; `Sigma=√3 |s|/H` is nonnegative. Note `j(u)` is **per normalized u**, not original native `dN/dln a`. HeI chemical binding is separately 24.587389011 eV.

Observed source-native **PR171 original comparison JSON** blob `f1408f759615e66d38021e688a63a3ad4812242c`: age16→32 survivor N relative `0.9013495136957606` vs integrated HeI photo-events `1.956139715976142e-5`; transport32→64 endpoint HeI Gamma `0.0008124834364653384` vs integrated HeI photo-events `0.007497350968307805`. This is **observable-specific sensitivity, not an error bound**.

Wolfram symbolic derivative of exact LRS energy and two hazard branches returned `{0,0,0}`. Scope: source/κ manufactured; no native Grackle, MD14, actual HeI spectral 64→128 or EoR history.

**R5 stage backup, complete CRC/manifest SHA readback**: [Drive](https://drive.google.com/file/d/1NfeICln0PDmGcyvjFZ4nQYZl4CqqFMNZ/view), 5,946 bytes, SHA256 `271a3471d71f9c14347136b8fffa353d9421ad9b4521b2a1a2beae163a23d0fb`. A second independently restored ChatGPT Library copy exists. This stage's standalone detailed derivation is in the R5 ZIP. **DAG R5=COMPLETE; next C5=positive optical cubature.**
