# Coupled source intake, 2026-10-27

The bounded provider refresh found no new producer science in the latest two PR records of each of the six external repositories. REI PR236 has advanced from the prior intake's `6c1604744fbc256a484513f7215dcb39660e6cff` to `413729993919d21895e2196cc65f0c1c007e8614`. Its native REC source callback and two scoped admissions are already part of the starting 32/88. This intake adds zero original-node admissions.

## Current source and owner identities

Exact top-two pins and URLs are in PROVIDER_DELTA.json. The unchanged external top heads are REC138 `4a8e541030ee2cbd02e26ba671083b705d309d49`, CR106 `b11b2e9255f2b10fb5582376412e045bd1e9151c`, HE102 `ac6042a6b0610b09d0576538767ee0299389a5eb`, BASS192 `d7dcd731de1a0c59e5e65db5038c333f5abae0bd`, VigilODE89 `72836e0290b66d33f4ca1771284b1c8070669a74`, and WU150 `87933da5654bb2e4d93f7de4341df5e0fa0f8716`.

Central [PR222](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222) remains `a5db4bac9dafadae29685bbea3cec7f43ab990b2`. Both PR metadata and direct git-ref agree. Its pinned CURRENT_STATUS.json has 88 original rows and blob `37b0687df054c9d82711eca3072b5981b8ea9db7`; REC-H6 is ACTUAL_INPUT_PENDING, REI-L2 retains physical beta daughter/stopping inputs, and CR stopping remains PARTIAL_OPEN. The earlier central 27/88 count is reused from the checked PR235 intake; it is separate from the unmerged working 32/88.

The direct ANGTHERM branch ref remains `8d10231b1f0f788164d5eadbe1bcee0b802cceca`. PR222's base_sha is a historical PR-base field, not the current owner-ref observation. HE101 remains `28a26f4db951ab9085180e2ecc5d600d981a1f71`, 19/20, C8 OPEN/PARTIAL_EXPORT, reserve0, with PASS/FAIL/FAIL retained. Published reservations do not establish a live local dirty-tree or lease census; those are UNOBSERVED. All producer files and unpublished work remain untouched.

## Immediate reusable coupling

The restored native REC119 source at `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7` and accepted REI236 source `881dbc0700e96366f97b559a2b86bc580a694a83` provide the actual 21-state callback, matched GRID044 z=2.479 snapshot, selected PW19 helium continuum and analytic JVP. They supply local source evaluation with distinct binding, primary-electron kinetic and prescribed-radiation partners. This is the correct existing consumer dependency for the next exact coupled-energy construction. It does not supply a PW19-evolved history or source-matched H6 temporal derivative.

REC124 `e6ecef7624e39bee66b39e09d99fe355f76e2eae` remains a reusable full63 gas Compton callback with exclusive actual-hot versus Planck-reference handling; its opposite-energy bookkeeping is distinct from a reciprocal spectral/Einstein solver. Existing CR106 scalar/ground-channel consumers can be reused within their original support and source conventions. Their unchanged records do not close a full cascade or finite-time assimilation.

## Particle-count term: primary-source support and precise mapping

One targeted SciSpace question returned ten discovery records; abstracts did not establish the exact closure. One Exa search returned four results and two Exa fetches read the Hui–Gnedin primary paper through arXiv and ADS. [Hui and Gnedin, MNRAS 292, 27–42 (1997)](https://adsabs.harvard.edu/pdf/1997MNRAS.292...27H), section2.1, equation2 and its following prose explicitly distinguish expansion/compression, changing total gas particle count, and thermal heat input. The [arXiv source](https://arxiv.org/abs/astro-ph/9612232) identifies the same paper. OCR mangles parts of the displayed equation, so the following expression is an explicit algebraic mapping from the stated ideal-gas balances, rather than a verbatim OCR transcription.

For a common-temperature nonrelativistic monatomic thermal gas, set
`u_g=(3/2) k_B n_g T_g`, `p_g=k_B n_g T_g`,
`dot n_g+Theta n_g=S_N`, and
`dot u_g+Theta(u_g+p_g)=Q_g`.
The product rule gives
`dot T_g=-(2/3)Theta T_g + 2Q_g/(3k_B n_g) - T_g S_N/n_g`.
Thus a frozen-composition heat-capacity division alone omits the caloric particle-count term whenever S_N is nonzero. In a homogeneous FLRW element, Theta=3H. For a reference density with `dot n_ref+Theta n_ref=0` and `n_g=n_ref C_g`, this becomes
`dot T_g=-2HT_g + 2Q_g/(3k_B n_ref C_g) - T_g dot C_g/C_g`.

The application must define C_g as actual thermal translational particles: atoms/ions/molecules plus thermal electrons with each physical particle counted once. Molecular internal degrees of freedom require their own heat-capacity/internal-energy model. A primary electron stored in a nonthermal reservoir does not enter thermal C_g by assumption; its transfer must carry both number and kinetic energy into the bath. Conversely, if native REC assumes instantaneous thermal electron membership, adding a nonthermal reservoir requires an explicit partition/assimilation mapping. This is a conditional bookkeeping relation. The primary paper does not supply the missing physical stopping law.

## Fast photoelectron reservoir: primary context for the selected next component

A second targeted SciSpace query returned ten records and a second Exa search returned three. The primary full text [Furlanetto and Stoever2010, MNRAS404,1869–1878](https://academic.oup.com/mnras/article/404/4/1869/1083930), DOI10.1111/j.1365-2966.2010.16401.x, was fetched. Section2 follows primary and secondary electron cascades, with separate ionization, excitation and heat deposition. Section5 treats energy transfer from fast electrons to ambient electrons. Section6.1 explicitly assumes instantaneous deposition and identifies changing-background timescales as a limit. Its fixed-background cascade does not evolve the gas self-consistently. The residual below10.2eV is assigned to heat within that model; this is not a universal thermal cut or this project's assimilation law.

This source supports distinguishing fast-electron kinetic energy from thermal heat. The selected next component is the theory worker's independently derived pre-assimilation HeII source: nonthermal number zeta and energy w are explicit, chi_th=(1+q)Y-zeta, and dot zeta=q F_gamma cancels the source contribution to dot chi_th. With Q_th=0, the isolated photo source then gives dot log T=0. These algebraic identities are our conditional construction, not claims quoted from this paper. Existing REC124's all-thermal particle factor cannot be used unchanged when zeta>0. Physical stopping, cascade coefficients and finite-time assimilation remain inputs; this component leaves the original REC-COUPLED gate partial and produces no count increment.

Final literature coverage is two SciSpace searches/20 returned records, two Exa searches/seven results and three fulltext fetch calls. The first search concerns the gas-count equation; the second concerns fast-photoelectron energy ownership. No new numerical source table or source-matched evolved history was admitted.

## Preserve the neutron/tritium and inverse-beta source questions

Here nuclear `n/T` means neutron/tritium; it is distinct from gas density `n_g` and temperature `T_g`. Existing sources are not all absent:

- [DDEP_H3_TYPED_SOURCE.json](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3ab52a286a443622492403d89cd2bf80e58fb722/research/rei_expanded_event_consumer/coupled_followup_20261026/nuclear/DDEP_H3_TYPED_SOURCE.json), blob `acb8d60138d57d6769c1f4440c3ddbc9a82e09d5`, preserves the evaluated H3→He3 nuclear branch, molecular-tritium lifetime12.312(25)years, atomic-mass Q18.591(1)keV, tabulated endpoint18.564(3)keV, and electron kinetic mean5.68(1)keV. Its official BIPM table and LNHB evaluator-comment locators are retained. The [source interpretation](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3ab52a286a443622492403d89cd2bf80e58fb722/research/rei_expanded_event_consumer/coupled_followup_20261026/nuclear/SOURCE_RESULT.md), blob `61df444465e7c9e9d9c63189dbda6924d28a4e07`, explains property-specific regimes.
- This packet remains a qualified evaluated-property source, pending parent-state/consumer match. It does not provide a full electron–neutrino–recoil joint distribution, arbitrary ionization-state decay rate, source amplitude, deposition fraction or covariance. H3 data cannot furnish neutron coefficients.
- No newly qualified neutron, tritium full-event or inverse-beta source was found in the refreshed provider records. This unit did not perform a new neutron/inverse-beta literature search, so it does not claim literature-wide absence. Specify the reverse process, incident distributions, charge/nuclear states, thresholds, proper-time rate and energy partners before treating it as a usable inverse-beta source.
- Existing normalized beta algebra and moving-reservoir components remain useful conditional constructions. Neither an evaluated mean energy nor total Q supplies a heat deposition fraction. Preserve the unresolved daughter/recoil, nonthermal spectrum, collision-support and stopping-time obligations.

## Held sources and actual coverage

The prior HD finding was read and reused: original REC138 fixed bytes retain1pass/7fail at35Hz, maximum discrepancy1827572.5607572Hz; a complete precision-qualified same-fit successor deck is still absent from the checked evidence. No new HD lead appeared, so the same failed web search was not repeated. H5 continuous defect/stability/tube/curvature coverage0/313 and source-matched H6 history obligations remain exactly scoped.

Coverage is latest-two PR metadata for seven repositories, the named central/reservation records, prior intake and three PR235 intake/nuclear files. It is neither an exhaustive repository/branch/conversation survey nor a live worker inspection. A default-branch recent-commit query returned old commits and was not used to infer current producer freshness. One initially guessed source path returned404; the actual PR235 filename list supplied the corrected path. No claims are based on the404 beyond that path.

No scientific runtime, IVP, old-suite replay, producer edit or publication occurred. Entry planning debit11.551892911/original10 and main NO_MORE_IVPs were preserved; controller recovery/mechanical debits are separate updates. Metadata, source-search and model costs remain UNKNOWN_NOT_ZERO. Requested authority role was Astra; actual model identity was unexposed. Root AGENTS at the current REI pin, physmath common policy, theory loop, handoff contract and REI execution policy were read.

