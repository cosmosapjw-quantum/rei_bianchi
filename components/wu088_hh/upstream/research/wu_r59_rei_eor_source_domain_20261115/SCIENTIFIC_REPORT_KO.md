# WU R59 | CORE REI-EXP-SCENARIO original source and geometry admissibility

Date 2026-11-15. Immutable WU parent PR198 HEAD abb4036b8a5cc5fa0df760db09a5ef0bfdd29fb2. REI source owner last reviewed PR373 is Draft/HOLD. Original first-interval source-owner accepted H/He tick160/131072. Canonical WU 34/49, REI central 28/88, working 33/88 non-additive, Physical Fast 4/7. All canonical deltas zero.

The original WU CURRENT_MISSION_DAG.json and research/rei_igm_process_audit_20261101/NEXT_CONSUMER_UNIT.json direct CORE_NOW to REI-EXP-SCENARIO / RUX02–RUX05 and matched BI–FLRW radiation, chemistry, energy and observables, with HD19 optional. This research unit implements quantitative source eligibility and original cell-level Thomson material, not another isotope coefficient atlas.

## Original immutable physics inputs

Original REI F05 26-event source 184320 rows, four accepted material endpoints 0,64,128,160, augmented native 27-field H/He/thermal RHS SHA256 d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e. Original F05 17 time-node source photon forcing SHA256 9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268. Original initial H/He material with normalized 46080 spatial cell weights SHA256 7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d. Original continuous F08 S0 4 model branches ×160 BASS photon+HHe native Rust steps SHA256 75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843, owned by BASS PR328, with an independent BI and FLRW source pair and not original F05 26-event owner.

The F05 original photon source labels begin z=6.0, midpoint z=5.95, and end z=5.9 over proper source duration 638562959250984.8 seconds. Conditional FLRW mean source H calculated directly from source clock:
H_source=log[(1+6.0)/(1+5.9)]/Delta_t=2.2532997324143277e-17 s^-1.
This matches in scale a model-dependent flat Planck 2018 LambdaCDM comparator with H0=67.4 km s^-1 Mpc^-1, Omega_m=0.315, OmegaLambda=0.685, ignoring radiation. This is an internal clock sanity check, not an observational fit or unique expansion model. Reference: Planck 2018 VI, DOI 10.1051/0004-6361/201833910.

Original F08 S0 prescribed BI H_i=(1.01,0.99,1.00)e-14 s^-1 and FLRW H_i=(1,1,1)e-14 s^-1. F08 mean H is 443.7935999435534 times the F05 source-redshift mean. The four F08 native branches have 640 genuine time steps (160 in each), initial x_HII about 0.900 and last x_HII about 0.9088, proper t=0 to 1e11 s. F08 native source does not specify a common absolute z epoch with F05, so matching its toy scale factors to F05 would be unjustified. This specific source/clock mismatch is NOT a universal no-go for an anisotropic EoR universe.

F05 actually accepted H/He source states cover only tick0→160 of 131072: source time t160/tfull=160/131072. In all four original accepted epochs, 0/46080 original cells have x_HII below 0.99. Tick160 original HII fraction spans [0.9927557354136588,0.9999970270709362], median 0.9999437241659213. The original H-nucleus-weighted neutral fraction at tick160 is 0.00012307048141179292. F05 thus provides near-complete-ionization / late-reionization boundary FLRW material and photons, not an already computed neutral-to-ionized first EoR history. Its fourth native photon group has exactly zero counts and absorptions in all 17 forcing nodes. Original Gamma_HI PCHIP rate exposure from t0 to native tick160 is 0.1835490038029455 per initially neutral H atom, not the actual evolved HI absorption-event count.

## New physical scalar data (not observer sky tau)

Take original 46k per-cell accepted N_e(t_j) and original W_node comoving physical volume V_i=W_i Mpc_cm^3/(1+5.95)^3, for j=0,64,128,160. Declare piecewise-affine interpolation n_e(t) between accepted endpoints and calculate exact integrated source proxy
T_i = c sigma_T sum_j (t_{j+1}-t_j)[n_e(t_j)+n_e(t_{j+1})]/2,
c=2.99792458e10 cm/s, sigma_T=6.6524587321e-25 cm^2.
Original real 46080-cell source value min 6.1233270030073306e-9, median 1.2111200609760683e-6, p95 1.5737651300346214e-4, max 2.7367690641870164e-4. These are source rest-frame Thomson collision hazards, not observer geodesic line-of-sight tau(z), polarization or CMB visibility. Accepted original H/He source data and original F05 source clock are real; the between-knot interpolation is the explicitly introduced approximation. No source-owner new MPRK/SDIRK integration or Bianchi photon transport performed.

## Source-consumer science verdict and next dependency

F05 source-qualified FLRW late-EoR boundary: YES for source radiation, original 26-event H/He chemistry, thermal and source proper clock; full accepted 131072-tick neutral-to-ionized history: NOT DONE. F08 S0 self-consistent native BI vs FLRW model pair: YES within its own clock and photon prescription; same physical EoR epoch and clock as F05: NOT QUALIFIED. Puchwein et al. 2019 UVB literature has an EoR photo-rate and heating model around z~6, but the published spatially homogeneous UVB does not by itself define the F05/F08 original coupled source, Bianchi tetrad, escape, initial data and photon observer. Reference Puchwein et al. MNRAS 485 47–68 DOI 10.1093/mnras/stz222.

The minimum blocking science input is one REI source-owner versioned Bianchi I matter-photon-thermal history with the F05 or a new explicitly accepted EoR photon spectrum, same proper clock and absolute cosmological epoch as its FLRW control, and a certified observer normalization. This is a scoped source-support finding, not a strong no-go. WU can contribute original atomic molecular sources only when a real named scenario requires them.

## Verification

Independent same-author readback of all 184320 original REI HHe rows, all 46080 new source-cell Thomson records and 640 original BASS S0 rows; native 17 photon time nodes and original source SHA all verified. Original HHe charge NE=NHII+NHeII+2NHeIII max source relative residual 0. New 46k Thomson hazard independent recomputation maximum relative difference 3.1295204061858164e-16; original gamma source PCHIP direct integral versus independent numerical quadrature relative difference 1.5121616048337008e-16. Normal Python 14/14 and optimized Python -O 14/14 tests PASS. Wolfram analytic affine-integral and Hubble clock derivative identities yield {0,0,0}. Distinct-author referee and native subagent NOT_RUN.

Claim status: DERIVED+NUMERICALLY_CHECKED+IMPLEMENTATION_VERIFIED_SOURCE_SCOPED; original EoR BI–FLRW observable, REI-L4, and official tick161 admission remain HOLD. Preservation: source-free GitHub Draft PR and a small incremental ZIP referencing already verified original parent backups. NO_MAIN_MERGE, NO_FORCE_PUSH, NO_PRODUCTION, AUTO_NEXT_NODE=false. Original source, main, history, owner tolerances and acceptance status are untouched.
