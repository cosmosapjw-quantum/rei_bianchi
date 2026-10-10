# Fresh bass_cr intake — 2026-10-10

The major change is **two parallel causal-electron lines plus new tail/source components**, not a completed CR/IGM history. PR25's title/body is stale: its current head contains PHYS02B_DELAY, PHYS02C source/NIST table/kernel, PHYS04A/B and PHYS05, beyond the advertised xi=.1 knot. All four relevant PRs remain open drafts; main remains `77237751bdd2aed5934bf7fc3bc626d631a09058`.

## Exact live pins

| PR / branch | Head | Scientific identity |
|---|---|---|
| [24](https://github.com/cosmosapjw-quantum/bass_cr/pull/24) physical provider | `e41e18873af438ef989ff44f505fe2665118fdec` | `0522fac6dcaf1874974e2a59979aef88408a81e6` |
| [25](https://github.com/cosmosapjw-quantum/bass_cr/pull/25) phys03-fs10-xi01 | `b157c7873851a9cc0f455786b607ad9fcfbaa168` | current tree `ae8438680c15e15b70acf1e6993dbf713d521bc1` |
| [26](https://github.com/cosmosapjw-quantum/bass_cr/pull/26) phys02a-causal-subthreshold | `58c8e1cda5c8f8ca8b83269cb89899ea40ab91fe` | `a6717cddf830b8195bc629b37d824009e1fc15c5` |
| [27](https://github.com/cosmosapjw-quantum/bass_cr/pull/27) phys02b-causal-cascade | `b5b0f2244311a6e46692da55e75db6d04d3ef305` | `929abd7ff981f08ed965e302532af9daac06316f` |
| r17b2b-homotopy-certification | `12ea71a20f9e0902cf808814babf312c0d5ee6fc` | photon/CR_OFF, no sharpening |

GitHub connector metadata and direct read-only Git refs agree. PR25/PR27 merge-base is PHYS01 final `e41e188...`; neither includes the other's causal implementation.

## What is genuinely new

**PR25 lineage:** source remains normalized over10keV–1PeV; production neutral collision band is still1–4MeV. Latest committed components:

| Unit / commit | Result and precise ceiling |
|---|---|
| PHYS03 `efeefb8022d1e568eca3476a3901afe35d0e2ec9` | Exact FS10 xi=.1 knot at100K; no interpolation/history. |
| PHYS04A `c55cd78bade16d95bf140456c6036b406c9356ea` |4–10MeV neutral-ionization tail: loss6.8577852e-43 J/m³/s. Secondary kinetic energy unallocated;3.9721% exceeds FS10 table maximum. Instantaneous diagnostic, solver intervals0. |
| PHYS04B `3189026c312318bfee4cac70ea3be45cc9cbfcae` |1–10MeV Coulomb plasma transfer4.1953126e-43 J/m³/s. Explicitly **not heat/deposition**; fixed collisionless population, no feedback. |
| PHYS02B_DELAY `6445f9a3b7aec08cd3d966e86bf58841bb498f22` |10–1000eV DarkHistory-old-rate impulse cascade; characteristic repair PASS_SCOPED.≤10eV remains inert number/kinetic reservoir. |
| PHYS05 `b65d51abebe5bd307b3e434632d2cfb8c05ee270` |Actual direct10–1000eV source convolution Q=tA to1e10s, PASS_SCOPED. Birth quadrature first failure preserved and panel repair accepted.99% remains active:98.9063% active,0.38716% heat,0.39346% cutoff of selected injected energy. |
| PHYS02C_SOURCE `c471d455d0516385c94d6418c2b3bf583a0e717f` |>1keV direct source through exact~8.7keV endpoints now calculated;24.46189% of direct electron kinetic source lies above1keV. This is source energy, not deposition. |
| NIST_TABLE `19a1cf0f5fe377f4760c805c39ab2ce9bd71ff49` |Two source-pinned H/He singlet excitation channels1–3keV; not oldHeI23s replacement. |
| NIST_KERNEL `b157c7873851a9cc0f455786b607ad9fcfbaa168` |Two-channel excitation-only event graph,25impulse/time rows PASS_SCOPED. Crossing residual number/energy retained; **P02B_INTERFACE HOLD**. |

PHYS05 source/kernel SHA checks pass in this checkout. Source code confirms cohort-specific grids are observed before aggregation; cutoff is explicitly not passed to PHYS02A. NIST source code retains integer-meV event counts/energies and absorbs crossings below1keV. These are real implemented components, not only plans. Existing receipts were inspected; no old scientific suite was rerun.

**PR26→27 lineage:** PR26 supplies directly born0.1–10eV Coulomb stopping. PR27 extends to0.1–900eV HI/HeI BEQ/BED+CCC hybrid causal branching. PR27's selected source contains73.55293% of direct kinetic energy; at316.88yr,98.29509% stays active and1.32307% has reached cumulative bath heat. Heat rate3.44099538e-44 J/m³/s is3.41089% of its **same-operator** instantaneous terminal proxy. This is not a universal suppression factor. Review is PROMOTE_SCOPED, not atomic physical-accuracy certification.

Do not combine the percentages or kernels across these lines: domains, atomic channels and operators differ. PR27 still records He total-Q .8841 versus sharing-Q .9130416667 and CCC effective threshold versus spectroscopy discrepancies. Its stated PHYS02C-ATOMIC-CONSISTENCY is **not** completed by PR25's differently scoped NIST table/kernel.

## Critical path and blockers

For an actual CR-on broad-redshift history, the remaining required work is:

1. **Select a canonical atomic/cascade model and source/domain contract.** Compare the two causal lineages on matched conditions if selection needs evidence. Avoid treating one as an automatic upgrade of the other.
2. **Close spectral and temporal interfaces.** Low cutoff counts/energy cannot be dumped into heat. High-energy crossing moments do not specify a daughter spectrum. Connect low response,10–1000eV response and high-energy response with no energy overlap or double counting.
3. **Complete or bound omitted response domains.** The >1keV source is already known; only two excitation channels to3keV are implemented in the new high-energy kernel. Full source reaches~8.7keV. Model omissions and atomic uncertainties remain outside numerical tolerances.
4. **Evolving-state transport and receiver coupling.** All new causal results use a100K,xi=.01 fixed bath and short local ramp. No broad-z gas/source history, feedback, cosmological electron transport or production receiver has been admitted. One extra FS10 composition knot does not solve this.
5. **Proton coverage/feedback or explicit residual bounds.** Full-spectrum normalization does not provide full-spectrum losses. The4–10MeV neutral and1–10MeV Coulomb diagnostics still have no full deposition/feedback evolution. A narrower partial claim can be useful if residual energy is explicit and bounded.

Optional or scope-conditional items must not block an independent CR-free baseline: native original-atomic G02/b_grid/all_bound completion, R17B2B high-order source sharpening, arbitrary FS10-knot interpolation unless that is the chosen model, and broad repeated audits. Preserve their original gates. A receiver that actually relies on those features does inherit their gates.

R17B2B closes whole-eta tube and finite nonlinearity remainder but leaves actualJ3/regularK4 unbounded. Its candidate~±9.9974e-17 is wider than safe source fallback2.125035e-18, so **NO_CERTIFIED_SOURCE_SHARPENING** and zero replacements are correct. This is13.7eV photon source work with CR_OFF_FASTEST and provides no cosmic-ray completion.

## Fastest honest acceleration

If the independently audited reionization baseline has adequate cosmology/source/thermal/atomic inputs, deliver its broad-redshift **CR-off** result now while CR extension proceeds in parallel. Keep CR completion as a separate unmet requirement. Use the current fixed-state finite-band causal results as a useful labelled response study immediately; do not promote them by extrapolating the317yr ramp or multiplying a full history by one lag factor.

The next CR work should be a bounded interface/model choice, reusing existing endpoint source and reviewed kernels. New computation should discriminate the atomic choice, resolve crossing spectra and conservation, then validate evolving-state coupling and a paired CR-off/CR-on receiver result. Repeating entire suites or rediscovering pinned NIST data adds no missing physics. The latest project policy routes scientific decisions/review to Astra and closed-contract implementation to a lower tier; no current model identity is inferred from historical receipts.

## Evidence and limitations

Read-only GitHub metadata plus actual cloned source/reports/receipts;8 source-manifest file checks passed. No source changes, remote mutations or scientific runs were performed. Status reflects exact pins above, not a fresh independent physical validation. Full source URLs/hashes, unit commits and machine-readable blockers are in `cr.json`.

Key source files:

- [research/cr_phys05_source_convolution_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys05_source_convolution_20261010/REPORT_KO.md)
- [research/cr_phys05_source_convolution_20261010/convolution.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys05_source_convolution_20261010/convolution.py)
- [research/cr_phys05_source_convolution_20261010/evidence/INDEPENDENT_REVIEW.json](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys05_source_convolution_20261010/evidence/INDEPENDENT_REVIEW.json)
- [research/cr_phys02b_delay_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02b_delay_20261010/REPORT_KO.md)
- [research/cr_phys02b_delay_20261010/causal_generator.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02b_delay_20261010/causal_generator.py)
- [research/cr_phys02c_source_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02c_source_20261010/REPORT_KO.md)
- [research/cr_phys02c_nist_table_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02c_nist_table_20261010/REPORT_KO.md)
- [research/cr_phys02c_nist_kernel_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02c_nist_kernel_20261010/REPORT_KO.md)
- [research/cr_phys02c_nist_kernel_20261010/excitation_kernel.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02c_nist_kernel_20261010/excitation_kernel.py)
- [research/cr_phys02c_nist_kernel_20261010/DAG.json](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys02c_nist_kernel_20261010/DAG.json)
- [research/cr_phys04a_tail_20261010/README.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys04a_tail_20261010/README.md)
- [research/cr_phys04b_coulomb_20261010/README_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys04b_coulomb_20261010/README_KO.md)
- [research/cr_phys03_composition_20261010/REPORT_KO.md](https://github.com/cosmosapjw-quantum/bass_cr/blob/b157c7873851a9cc0f455786b607ad9fcfbaa168/research/cr_phys03_composition_20261010/REPORT_KO.md)
- [PR27 handoff](https://github.com/cosmosapjw-quantum/bass_cr/blob/b5b0f2244311a6e46692da55e75db6d04d3ef305/research/cr_phys02b_20261010/START_CODEX_HANDOFF_KO.md)
- [R17B2B claim gate](https://github.com/cosmosapjw-quantum/bass_cr/blob/12ea71a20f9e0902cf808814babf312c0d5ee6fc/research/cr_r17b2b_20261010/CLAIM_GATE.json)
