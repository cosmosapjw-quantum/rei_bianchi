# REI Bianchi IGM | 원본 H/He 보존형 부모 변화와 비국소 광자 피드백

범위: 원본 26-event REI H/He ionization/OTS/thermal source, 46,080 original accepted-state nodes at tick160, one original microstep's positive MPRK predictor. Immutable PR345 HEAD 79ebc917cf4774f9fa96f885e518813018bec9af. Original archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b and accepted-state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01. Original main/production solver and source inputs READ_ONLY.

## Constructive physical calculation

Two candidate mass-conserving parent directions from original 46,080-node frozen *marginal* state box: H I → H II and He I → He II. At every original node the input alpha in [-1,1] moves only 20 percent of available H/He population slack, preserving H and He nuclei exactly. One original time and midpoint gas temperature are held fixed. The physical source within each candidate is recomputed using ORIGINAL 26-event event_box, with photon source denominators sharing the same three global HI, HeI, HeII moments. Original H 2x2/He 3x3 MPRK Krawczyk population certificates validated the parent and both signed endpoints in each mode.

Exact photo source derivative at fixed forcing: r_isg=J_g C_sg N_is/D_g and D_g=E_g+Σ_t C_tg S_t. Along a mass-conserving direction, dr/dalpha=(J_g C_sg/D_g)(dN_is/dalpha)−r_isg (Σ_t C_tg dS_t/dalpha)/D_g. Therefore local numerator and global competition are both present; earlier PR345's frozen-numerator partials alone are not the full physical parent response.

Actual predictor equation A(p,F(p),h) y = p, with all original 26-event fluxes F and original species Patankar denominators. Exact discrete implicit derivative is dy/dalpha=A^{-1}(dp/dalpha−(dA/dalpha)y). dA was constructed from directional derivatives of original event-box flux and original parent denominator, preserving H/He column sums. The selected finite-difference full source JVP was compared to the implicit derivative; the **global source component** independently agrees with PR345 formal three-moment Jacobian contracted against the actual dlog S.

## Numerically checked source response at 2026-11-01

Real original physical output 46,080 rows × 23 columns, gzip CSV SHA256 d5fb11cba87e9aad4f77a954213346fafb7c64e41430af06d00be94e9af911db. Pinned isolated runtime NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0. Nine targeted synthetic tests normal and nine optimized PASS. Independent stdlib CSV readback, 24 Decimal45 source witnesses, exact nuclear/charge decomposition and source hash PASS. A repeated source run after tightening machine-scaled parent/Krawczyk containment yielded identical CSV SHA256, BYTE_EXACT PASS.

Two modes, physical response per dimensionless alpha (actual amplitudes vary by node):

H I → H II: 46,080/46,080 source nodes have nonzero positive amplitudes. Max |dxe_total| = 7.755733399152083e-7 per H; median dxe_total=8.408668204016887e-10. Max |dxe_global_photon|=1.2350273078913867e-12; median dxe_global_photon=9.737028748713887e-15. Median |global|/max(|total|,1e-15)=1.1613607556598136e-5; p95=3.227393322727071e-4. Source independent formal-global JVP mismatch relative 2.148307730292117e-16. Population JVP vs source endpoint finite signal relative 7.770896675104967e-8, electron output max-signal normalized 1.589848103047175e-6.

He I → He II: 46,080/46,080 with nonzero amplitudes. Max |dxe_total|=4.6154236023786334e-7; median dxe_total=2.4242757083839707e-10. Max |dxe_global_photon|=1.5230543026893272e-11; median=1.0140115549956619e-13. Median |global|/max(|total|,1e-15)=4.0089437914821743e-4; p95=6.329194033423915e-3. Original PR345 global source mismatch 4.0299280071101257e-16. Population JVP vs source endpoint finite relative 1.1101712571478787e-7, electron max-signal normalized 8.771249668642246e-9.

Both directions' dxe_total and dxe_global are positive at all 46,080 nodes for the selected positive ionization transfers. This is a **conditional mode-response** sign, not a theorem over the entire uncertain physical parent set or over a cosmological history. The split into global and remaining terms is source-model based; the remaining term includes direct nucleus transfer, local photoionization numerator, ne-dependent collisional/recombination/OTS and Patankar denominator changes, not just one physical reaction process.

Original primary photoheat source directional max amplitudes: 3.6522456614816727e-32 erg/H/s per alpha (H direction), 5.809421896401587e-31 erg/H/s per alpha (He direction). Fixed-T thermal and chemical binding-energy responses are saved per node. These instantaneous source perturbation rates are NOT cumulative heating.

## Blind-referee style same-author adversarial findings

A1 (critical scope): Being within all original componentwise accepted boxes and preserving nuclear sums does NOT prove the sampled directions belong to the full cross-site/source-correlated *dynamically reachable* original accepted parent set. The word reachable must NOT be used to promote these two modes.
A2 (numerical): Earlier naive subtraction of two nearly identical MPRK matrices produced an unstable nuclear-JVP relative-residual test; corrected by differentiating flux and parent denominators separately and using physically normalized residual. The original 2e-4/2e-3 science gates were not changed.
A3 (implementation): First source run found an unbound EV symbol in output-only chemical binding conversion; corrected to EV_ERG without changing any owner. Independent auditor's per-node relative error was uninformative at tiny responses, so both pointwise and max-signal normalized errors are retained.
A4 (false novelty): PR333/335 performed similar physical point modes; this work's distinct value is the original **local-vs-nonlocal photon-source contribution decomposition** inside the actual positive MPRK predictor with all original 26-event source fluxes, not another point-atlas pass.
A5 (physical): Group-four photon current is subnormal; no physical HeII global photo absence theorem follows from numerical zero under this frozen forcing. Thermal SDIRK coupling and table branches are not solved in this one-step fixed-T predictor.
A6 (verification): Independent author referee and native subagent NOT_RUN. The output CSV may be internally reproducible while the original whole-X nonlinear difference-map certification remains NOT_COMPUTED. Full source-to-Bianchi 1+3/LoS observables also remain outstanding.

## DAG and claim gate

REI canonical CENTRAL=28/88_REPORTED, Working=33/88_REPORTED, Physical Fast=4/7_REPORTED, canonical increment 0. Original first canonical interval accepted only 160/131072 ticks; frozen next [160,161] local logT error bound 2.1245050576368385e-4 > unchanged gate 2e-4, width 2e-3. Production HOLD, no main merge, force push, source swap, IVP restart, or tolerance reset.

Next executable science: use real local and global 26-event source directional decomposition to assemble the full MPRK corrector and SDIRK thermal implicit-root derivative with common forcing and source, then construct true all-X common-parent full-minus-two-half Jacobian with rigorous nonlinear and table-event remainder. Only after actual full-X PASS should tick161 or central DAG be admitted. Otherwise direct B2D Bianchi geometry/observables within REI can continue independently.

Publishing and durability: independent Git Draft PR #346 preliminary checkpoint published, full source outputs to GitHub Actions pending scientific CI. Full data binary backup and remote provider readback must be verified before dual-backup claim.

## 실제 CI·이중백업 검증 및 최종 범위

GitHub Actions 41286491472 SUCCESS, repository verify 41286491492 SUCCESS, 9/9 normal+9/9 optimized tests, 46,080 rows and 23 scientific columns exact. Original source archive SHA matched; CI CSV SHA256 d5fb11cba87e9aad4f77a954213346fafb7c64e41430af06d00be94e9af911db unchanged from isolated pinned local replay. GitHub Actions archive #13075935680 9,701,923 bytes SHA256 079dd3f194ebbe9967f9978f5b37617a150d9f9b2df7b4629f018189c2182917. Google Drive file 15Lox3cMpbPz4FOQQKjK_gL3Ji0v_Zpv6 raw redownload size/SHA256/ZIP CRC exact MATCH; this certifies binary two-provider backup for THIS science output ZIP only.

Important additional adversarial boundary: the original event_box supplies independent interval-enclosed reaction fluxes; its selected midpoint flux vector is NOT proven to be one jointly physically realized reaction history. The complete numerically recomputed predictor response is source-conditional. Both nuclei-conserving parent curves are componentwise admissible, but their dynamical reachability in the correlated original parent set remains UNPROVED. The original whole-X D_h gate is unchanged and still FAIL. No new accepted canonical REI node.
