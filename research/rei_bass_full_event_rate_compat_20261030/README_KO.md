# REI↔BASS FULL_EVENT_RATE_COMPAT | source-qualified static preflight · 2026-10-30

**Parent:** Draft PR266 HEAD `a3470c88b4bddb38a08623d37ff6aa61210e04ae` (unchanged), previous scoped 18/20.
**Current unit:** `REI_BASS_FULL_EVENT_RATE_COMPAT`; **new scoped 17/20**, central DAG **28/88**, working DAG **33/88**, physical delta **0**.
**Disposition:** `PARTIAL_STATIC_SOURCE_QUALIFICATION` / `FULL_EVENT_COMPAT=REFUSED_FOR_CURRENT_ACTIVE_SOURCE` / `F4=PARTIAL` / `L4_ready=false` / `PRODUCTION=HOLD`; no new IVP, no merge or force push. `R6/C9=NOT_RUN`.

This PR is a **documentation/index-only scoped checkpoint**. The complete reproducible Python exact-rational static source audit (33/33 PASS), model/network bytes, previous PR266 full ZIP, original numeric RED test history, source manifests and machine-readable gates are in the full ZIP:

* **Google Drive:** https://drive.google.com/file/d/1yIcUzAYsw7lc7hFoTog7ROcl5pYlzgwz/view
* **ChatGPT Library:** `/REI_BASS_FULL_EVENT_RATE_COMPAT_20261030/REI_BASS_FULL_EVENT_RATE_COMPAT_20261030_STATIC.zip`
* **Exact ZIP:** 606496 bytes, SHA256 `2c48efdb2a6862896898842d18bd4428bc03ed482b9c6a53b1ae4a15a0f9fb89`; Drive full raw readback SHA + byte compare **PASS**; original nested PR266 ZIP 571682 bytes unchanged.

**New BASS source:** donor commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`, original `research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/data/atomic_coefficients.json`; blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`. Source-manifest raw SHA256 `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc`; file was fetched and inspected via connected GitHub but **raw-byte local SHA readback / inclusion in full ZIP was not performed**. Existing owner `atomic_network.py`, `atomic_model.json` were restored and byte verified from the old parent ZIP.

**Static evidence (not native owner Python execution):**
* Independent source-table formula evaluator at `T=10000 K, n_b=100 m^-3, UV=1`: Li6/Li7 exact conditional photo/RR/DR/weak lift shows numerical F max `3.59e-43 s^-1`, J intertwining max `3.76e-37 s^-1`.
* REI original Rust `igm_rates.rs`, `igm_thermal.rs` have positive H I collisional ionization (Grackle `k1(10000K)=7.242752046045505e-16 cm^3/s`); BASS atomic21 excludes CI. Thus eventwise equality cannot hold with both `n_e,n_HI>0` unless the event models change. This is **not** a total-RHS no-go.
* REI H II RR `k2(10000K)=4.1700000000000014e-13 cm^3/s` versus BASS Verner–Ferland `alpha_HII(10000K)=4.1923227353086324e-13 cm^3/s`, difference `0.532467%` relative to BASS. This difference is independent of the historical H1/He4 isotope inventory mismatch.
* REI 13-species isotope bookkeeping excludes Li charge states and does not establish a 21-state REI full chemical RHS/J. REI photon/thermal terms, physical H,K,nHref/n_b, weak/nuclear/CR/injection/fast reservoir matching are not source-qualified.

**Clock condition** with `rho=n_Href/n_b`, `x=ln(a/a_ref)`, `dt/dx=1/H`, `Y=E rho u`:
`u_x=(P F_B(E rho u;x))/(H rho)-(rho_x/rho)u`.
The corresponding `J_u=H^-1 P J_B E-(rho_x/rho)I` requires `H,rho,E` to be state-independent and all feedback state variables to be included. **Neither equation is an admitted physical REI forward model.**

**Next source gate:** obtain genuinely common H1/D/T/He3/He4/Li6/Li7 isotope inventory, source-native atomic coefficients with byte readback, actual full REI chemical equations and per-event species stoichiometry including electron, photon and thermal pools, H/K/rho; then static same-state F and J tests only, no IVP. Real distinct-author R6/C9 only after another reviewer executes them. Preserve all PR265/266 historical failures and CI records.

See `CONTRACT.json`, `SOURCE_IDENTITY.json`, `results/RESULT.json`, `STAGE_LEDGER.json` for machine-readable evidence.
