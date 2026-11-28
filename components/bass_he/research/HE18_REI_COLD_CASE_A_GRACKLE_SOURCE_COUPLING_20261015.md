# BASS_HE to rei_bianchi: cold Grackle Case-A H/He microphysics and photon-transport A/B

2026-10-15 KST. **This is a downstream cold AXBI research receipt, not a warm HE18 P01 FT03/HM12 source certificate.** Warm and cold source temperatures, He ratios, photon stocks, field units and rate conventions must remain separate.

Canonical executed and tested research implementation: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015/hhe_case_a_source_20261015

Source-tested research commit: `9e484874aa83f3d7631352271f869e8835ce27b6`. Original live cold owner remains `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`.

## Exact source and physics match

The original cold native `AxbiProvider::point` calls original Grackle 3.4.1 Case-A `igm_rates` and `igm_point_rhs` with source commit `af7939494ce65007887ada7b98d1813df6843346`. Seven tested Grackle rate/thermal/EOS function bodies match source bytes between the original frozen cold AXBI source epoch `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185` and separately compiled rlib full-source epoch `fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67`. **The full compiled source epochs are different**; only selected validated functions are identical.

Experiment gas initially T=8.098143045064857 K, YHe=.2454, LRS Bianchi I, normal-comoving electrons, proper time seconds, proper nH and nHe cm^-3, u in eV/H outside original native RHS and erg/H within `IgmPointRhs`. It evolves xHII,xHeII,xHeIII and gas thermal energy with photoionization, original native CI/RR/DR, collisional excitation, free-free and radiative/Compton thermal exchange, with explicit exact adiabatic half-maps. `IgmPointRhs` receives photo input zero so photon packet events are not double counted, and expansion h=0 because the adiabatic work is already done outside the micro RHS. Case-A recombination photon escape is tracked in a separate energy ledger, without claiming coupled OTS or emissivity after the initial packet.

At temperature ~8.098K, original source rates: alpha_HII = alpha_HeII = 3.96696030736e-11 cm3/s, alpha_HeIII=3.09279404430e-10 cm3/s, cold CI floor for each channel = 1e-20 cm3/s, DR=0 in the selected low-temperature source branch. Those are source code coefficients, not empirical claims of physical calibration at cosmological recombination or the warm HE18 model.

## Real local short-case numerical result

54 paired experimental cases / 108 actual native Rust transport lanes, q=-0.005,0,+0.005, original energy nodes 5/32/33, initial neutral eta=0 or 1e-5, outer steps 1/16/128, end mean zbar=19.998. Each source case initially injects only N_gamma=1e-6 per H into the original photon registry.

When initial eta=0, there is initially no HeII but recombination dynamically creates it. At q=0, E0=54.42eV, after 16 steps the projected lane has 0.6119734 false HeII photoionizations per initial photon and exact covariant lane has zero. At 128 steps the corresponding pair is 0.627702119356 versus zero, final delta xHeIII(projected - covariant)=-4.848315322214525e-5 and delta gas temperature=-0.009629655039089968 K. At 1 coarse step, neither arm initially photoionizes HeII and the gas states agree. This demonstrates a source interaction invisible in the earlier frozen-gas case.

**Counterintuitive event-ledger sign:** At q=0, eta=0, 128 steps, the projected lane gains 6.27702119356e-7 HeII photo events per H but increases native HeIII recombinations by 4.56944801142e-6 per H (CI differential ~8.14e-18), so final helium excess becomes negative. The exact balance delta(fHe xHeIII)=delta photo_HeII + delta CI_HeII - delta RR_HeIII closed to 4.86e-17 per H. This is a dynamic reaction feedback result for this source-scoped case, not a generic sign theorem.

Native micro Heun internal cap 1e10s vs independently compiled 5e9s produces delta xHeIII=-4.848315322214525e-5 vs -4.848344270624860e-5 at q0 eta0 outer 128, relative change 5.97e-6. No full original source global error bound or two-dimensional energy-grid/time convergence is claimed.

Full numerical ledger maximum residuals from original source-pinned outputs: photon+gas+binding+escape+CMB+expansion global energy ~1.7763568394e-14 eV/H; atomic binding ~1.4654943925e-14 eV/H; electron events ~1.1241008124e-15 per H; thermal energy ~6.9388939039e-18 eV/H. Serial and bounded two-worker physical CSV fields are identical. Total executable regressions including previous source lanes: 130 Python and 17 Rust = 147 PASS.

Original Grackle model domain and Case-A recombination-photon escape remain unchanged. Current status is `SOURCE_SCOPED_CASE_A_NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED`, while full coupled EoR/CMB optical depth/polarization and native global-error admission stay `HOLD`. The next task is continuous original emissivity and explicitly chosen recombination-photon routing with two-dimensional energy/time resolution studies, never a silent patch of the original live Rust driver.

Primary reference for H/He coupled reionization and the distinction between thermal and ionization timestep accuracy: Friedrich et al. (2012), MNRAS 421, 2232, Appendix G, https://academic.oup.com/mnras/article/421/3/2232/1077406 .