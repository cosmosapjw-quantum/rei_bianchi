# BASS_HE → rei_bianchi: Dynamic photo-only H/He and thermal energy A/B, 2026-10-15

This is a **downstream cold AXBI source-scoped photoionization-only experiment**, not a certification or numerical reuse of the warm HE18 FT03/HM12 16-cell source. The cold native atomic threshold, helium number ratio, temperature, photo source and clock differ from warm HE18; no warm numbers or rates have been silently inserted.

Canonical original-code-using implementation:
https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/dynamic_hhe_ab_20261015

Verified isolated research commit: `d35ae44057bde6319b6eda5f5c651b3ebbcfd742`. Original live owner remained `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`.

## HII, HeII, HeIII and thermal-energy source equations

Use per-H photon stocks and proper number densities, with helium number ratio `fHe=0.2454/(4*(1-0.2454))`. Let `x=xHII`, `y=xHeII`, `z=xHeIII`. Original midpoint absorption rates `lambda_j=c*n_neutral,j*sigma_j(E)` use the same Verner `AtomicProvider` and `HHeModel::controlled_fixture` threshold energies as original separately linked Rust reference. Exact frozen midpoint photoevent count is `dN_j=N_before[-expm1(-lambda dt)]lambda_j/lambda`. Gas changes are

    ΔxHII=dNHI
    ΔxHeII=(dNHeI-dNHeII)/fHe
    ΔxHeIII=dNHeII/fHe
    Δ(ne/nH)=dNHI+dNHeI+dNHeII.

All `dN` above are photons per H. Gas thermal internal energy in eV/H receives `Q=sum_j (E-chi_j)dNj`, gas work receives adiabatic cooling `u_new=u_old (a_old/a_new)^2` for each geometric half-step, and temperature is derived from `u=(3/2)kBT(1+fHe+ne/nH)`. Charge/nuclei and binding-photoheat/redshift/boundary photon-energy ledgers are checked. This is **photoionization, photoheating and adiabatic cooling only**: no recombination, collisional ionization, emission after the initial photon or temperature-dependent rates. No full EoR solution or calibrated observational claim.

## Actual native experiment

For q=-0.005,0,+0.005; neutral eta=0,1e-5,1e-4; initial photon energies at native indices 5,32,33; time subdivisions 1,16,128 from zbar20→19.8; injected photon `1e-6/H`: 81 paired conditions, 162 transport lanes. `PROJECTED` uses native two-neighbor `Driver::geometry_map` and canonical source-grid Verner `sigma(E_i)`; `COVARIANT` transports the exact Killing momentum and uses original reference `absorb_frozen_gas` at identical midpoint, gas and proper dt. Both update their own evolving gas fractions and internal energy.

**Primary numerical result:** At q=0, eta=1e-5, initial 54.42-eV HeII-threshold photon, 128 steps, projected HeII absorption/initial photon = 0.002465757338921187; covariant HeII absorption = 0. Final difference xHeIII(Projected)-xHeIII(Covariant) = `3.0328614397667764e-8`. Temperature difference is `-1.0459413308794296e-6 K`. At eta=1e-4 the corresponding HeIII difference is `2.8944642516126606e-7` and delta T = `-1.215268004211012e-4 K`. With eta=0 the two dynamical gas outcomes coincide and gas temperature follows exact adiabatic expansion. At energy index 33 above threshold both lanes produce physical HeII absorption. The ghost effect persists in these three source-step levels, but no global error convergence or causal attribution to full production EoR is claimed.

Independent exact Wolfram gas-event conservation: hydrogen and helium nuclei sum constraints vanish identically, and the electron abundance per H increases by the sum of absorbed HI/HeI/HeII photon counts per H. Original freeflight angular/geometric source epoch and 12 atomic/transport original Rust function bodies are hash-bound; **full** original frozen native solver and separately compiled rlib source epochs differ and are NOT identified as byte-identical.

Ubuntu verification: 115 Python regression tests + 12 Rust tests = 127 PASS across parent/transport/frozen/dynamic lanes. The final rustfmt binary SHA256 is `0cfc6308a68fd5a0ef7a0dff9b28ea71a52fa58db3e0296e54ebbba5a7fde39e`. All 162 serial vs 2-worker scientific output strings agree identically, except timing diagnostics. Wall time 15.11 s serial, 14.61 s two worker, 14.37 s final formatted binary two worker; speedup modest ~1.05x source-scoped, **not** the production Rust solver.

Two backup tarballs created under archives/ and Dropbox/BASS_DERIVATION_DOSSIERS_20260912/HE18_REI_TRANSFER_20261015, SHA identical at the two mounted locations:

- `HE18_DYNAMIC_HHE_CODE_d35ae440_20261015.tar.gz`, SHA256 `8ffa93a121882971866375cc2c2d95fdb376dc2373f6616b5fdeaec56cecf193`.
- `HE18_DYNAMIC_HHE_RAW_d35ae440_20261015.tar.gz`, SHA256 `1c289ca34841ae782cb1c14fdfb40c98139ea1440c8fb5b50d7c04fc9f12de43`.

Next scientific coding stage `HHE_AB6_RECOMBINATION_THERMAL`: source- and unit-matched H/He collisional/recombination/thermal cooling plus physical continuous photon injection under complete photon, nuclei, threshold and heating/cooling ledgers. Only then initiate 2D time/energy-grid convergence to support source-calibrated EoR global error or CMB tau claims.

Primary references: Friedrich et al. (2012), MNRAS 421:2232, https://academic.oup.com/mnras/article/421/3/2232/1077406 ; Norman et al. (2015), ApJS 216:16, https://doi.org/10.1088/0067-0049/216/1/16.