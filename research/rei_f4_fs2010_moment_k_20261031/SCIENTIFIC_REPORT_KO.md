# REI F4 | FS2010 original-table count+energy moment deposition enclosure and Ferrett laboratory/BASS native K calibration

**2026-10-31**. Immutable parent PR #305 HEAD `27b00a2e6bb0d96bcbdad8bc0520c8cc61c32126`; read-only sibling PR #304, active sibling PR #306, and preserved PR #302/#303. Original BASS21 source owner and PR287 source snapshot unchanged. Scope: **one auxiliary source-owned conditional physical calculation**, no new IVP, no native H/HeIII chemistry closure.

## Original data and identities
- User-supplied Furlanetto & Stoever 2010 `elec_interp.tar` SHA-256 `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101`. 14 × 258 primary energy deposition tables. For 14/14 tables, removing exactly one final LF produces the frozen 21cmFAST Git blob identity in commit `2a51aa316e216a1eb60650f9e7fbe35fe9e62040`; this is normalized TABLE CONTENT identity, not archive identity. Original log_xi_-4.0 HeII metadata inconsistency retained.
- User-supplied Ferrett et al. Phys. Rev. A **36**, 3172–3183 (1987), DOI `10.1103/PhysRevA.36.3172`, PDF SHA-256 `37b1b988798aee21b14d1d1cb018b8b1052da130e094c60f04ef1b347ea48711`. Table II direct R31 and Table III R32; Table IV absolute Mb inferred by external photoabsorption with ±20% common scale systematic beyond quoted point statistical errors. Private primary source raw bytes deliberately **NOT in public Git**.
- Immutable PR302 192 arrival energy/number moments SHA256 `155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df`; PR303 BASS193 H/He/HeIII 192 states SHA256 `dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09`.

## Constructive physics result
For absorber s, arrival j, electron energy band b, immutable source moments `N_jsb=∫dμ`, `M_jsb=∫E dμ` exist without assuming unknown intra-band spectrum. At fixed FS2010 one-x_i projected chemistry, its original bilinear table gives channel observable `G(E,x)=E f_channel(E,x)` for heat/ionization/excitation energy and `G(E,x)=n_channel(E,x)` for number yields. On each tabular energy segment, `G(E,x)=aE²+bE` for the energy channels and affine in E for the counts. Given E grid knots e_i, compute source number and first moment constrained 2-point LP extrema at pairs `e_i≤M/N≤e_k`; correct energy-channel interpolation using the exact quadratic chord identity
`G(E)-chord(G)(E)=a(E-e_i)(E-e_{i+1})`, bounded in magnitude by `|a|ΔE²/4`. For event-count channel the chord correction vanishes. Intersect the resulting enclosure with the valid prior marginal source-energy interval. The resulting bounds apply to FS tabulated model only and are source-number/energy consistent.

**Actual 87/192 within-x_i-grid source intervals (99.2164244283% original primary energy):**
- Heating energy [`6.671267524350548e-11`, `6.683272748656884e-11`] eV/baryon, prior PR305 [`6.654809992906246e-11`,`6.688386662957416e-11`], narrowing ×2.79684.
- Ionization energy [`3.880140007150628e-14`,`9.281309198949977e-14`] eV/baryon.
- Excitation energy [`8.61277345217821e-14`,`1.6300508929817864e-13`] eV/baryon.
- Ly-alpha photons [`6.204245283467859e-15`,`1.2099027584302217e-14`] / baryon, narrowing ×4.512.
- H I secondary [`2.8575587645902582e-15`,`6.680387756017807e-15`] / baryon; He I [`8.06891113747636e-19`,`1.3953295029694337e-16`]; He II [0,`2.891517874244315e-32`].
- 105/192 x_i-outside intervals retained unmodeled; `5.288541522292482e-13` eV/baryon source energy. Whole primary = `6.749242464433259e-11`, terminal-model = `8.581099847924098e-12` eV/baryon.
- FS2010 one-x_i chemistry **does not match actual BASS H/He/HeIII** at any saved endpoint pair (0/192); these are neither true gas heating nor observational constraints, nor an error enclosure on real species-mismatched cascade.

## New Ferrett source denominator evidence
Directly called the original frozen native BASS21 21-component photo-cross-section model at 13 published laboratory photon energies, including native Li6 K index 14 and Li7 K index 18. Cross-sections in m², convert 1 Mb=1e-22 m². On seven points 80–92.5 eV with direct Table II/III branching ratio support, `σ_lab(n2+n3)/σ_native(K)` deviates from 1 at most **3.514511% nominally**. Original three BASS measured-window photon energies E=[81.85233848280362,86.70882056440522,91.85344857617926] eV give piecewise-linear interpolated nominal α=[0.9942048873980895,0.9737628709745044,1.0147133763418674], with source-table statistical rectangle **and correlated ±20% common laboratory absolute scale** giving [0.7797056984453417,1.2165331820874024], [0.7702025795018245,1.181727021086074], [0.8018303018390539,1.2325666504619008]. All include unity.

**Critical counterexample**: native BASS Li K photo threshold = **75.64 eV** and `σ_native(K,75 eV)=0`, whereas Ferrett Table IV `σ_lab(n2,75eV)=1.99 Mb` because its 1s2s 3S binding threshold is **64.41eV**. This **refutes global operator equality** even though high-energy overlap numerically agrees. Lab n2+n3 also excludes some higher-n, valence and other channels; per-isotope equal native model cross sections are not independent isotope measurements. The Ferrett 1s2s singlet 2E1 source retains **zero admissible lower bound**; Langer 1S/3P and exact native K owner remain unresolved.

## Verification, claim gate and publication
- Same-author tests: original 22/22 moment tests plus 22/22 Ferrett/native comparison tests PASS; includes 240 randomized source-distribution counterexample attempts; source hashes and original TAR table metadata recorded.
- Wolfram symbolic chord identity independently evaluated. Deterministic CSV/PNG reconstruction and exact source SHA readback belong to the private full archive. All derived tables are source-conditioned, not observationally measured source yield.
- Distinct-author R6/C9 NOT_RUN; native subagent NOT_RUN; connected Chrome in this chat returned origin-context error (Browser not used).
- `WORKING_DAG=33/88; CENTRAL_DAG=28/88; F4_FAST_DAG=4/7; CANONICAL_DELTA=0; THIS_UNIT=1/1_SCOPED_AUXILIARY; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false; NEW_IVPS=0`.

**Next**: Original BASS21 isotope-complete K event owner/source replacement and REI 13→17 species mapping, coupled electronic/thermal proper-clock source F/J; independent H/He/HeIII electron cascade instead of one-x_i projection; Langer et al. PRA43 1652 channel data/covariance. No new FS2010 TAR is needed.
