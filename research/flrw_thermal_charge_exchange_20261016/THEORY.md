# Isolated thermal charge exchange

## R1 — Research question and scope

Construct the isolated fixed-proper-volume evolution of D0 + H+ ↔ D+ + H0 with the existing Savin2002 rate coefficients evaluated at the evolving common temperature. A single signed extent must own density changes, binding-energy change and thermal-energy change. Completion requires a concrete bounded scalar algorithm, an independently checkable temperature-dependent manufactured solution, and new small verification fixtures.

This unit starts from canonical commit `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`. The existing exact frozen-coefficient map in `deuterium_charge_exchange.rs`, blob `dd0a8c9b96ef3e53b8eef0fd08961045779f20b7`, is reused. The existing isotope-native point RHS and frozen wrapper in `deuterium_atomic.rs`, blob `8477162430af02585a32d18092454e1f7bb52f60`, are also reused as source-level evidence. Evolving temperature inside the kinetic flow is the new contribution.

The actual completed SOURCE011 three-stage diagnostic supersedes the historical missing-packet plan. Its tiny sampled Newton corrections do not supply whole-history error or cause attribution. PR166 owns its positive signed-MD14 reference and source-age convergence diagnosis. This unit is independent of those active supplier tasks and writes only its new directory.

The intended physical scope is isolated CX in fixed proper volume, with ideal monatomic common-temperature EOS and conserved particle count. Expansion, photoionization, recombination, electron ionization, source transport and full isotope evolution remain separate. Neither native production files nor existing rates, domains or defaults are changed.

The theory author performs source intake and mathematical construction. The assigned coding agent performs only the frozen bounded implementation and tests. A separate reviewer decides scoped mathematical/numerical acceptance. Actual stage artifacts are captured before advancing. No numerical computation or scientific code was executed for R1.

## R2 — Source and completed-evidence reuse

The pinned existing module defines forward CX as D0 + H+ → D+ + H0, explicit proper SI densities and thermal energy density, and opposite thermal/binding ledger increments. It labels its map exact only for frozen coefficients and fixed proper volume. The D atomic point evaluator includes the same signed CX event and thermal temperature derivative, while its finite-step wrapper calls the frozen map. These source contracts support the new thermal-feedback scope without replay of old tests.

Savin (2002), ApJ566,599–603, DOI10.1086/324218, Eq.(6), Table2 supplies the retained fitted rates. In cm³/s:
```
kf(T)=2.00e-10*T^0.402*exp(-37.1/T)-3.31e-17*T^1.48
kr(T)=2.06e-10*T^0.396*exp(-33.0/T)+2.03e-9*T^(-0.332)
```
Multiply by10^-6 for m³/s. Preserve the inclusive domain2.7≤T≤200000 K. The fit exponents37.1 K and33.0 K are not the binding-energy defect. The independently supplied defect remains a named input. The retained conditional example is DeltaChi=0.0037 eV, with the precision/provenance stated by the earlier isotope-provider theory.

The retained physical constants are kB=1.380649e-23 J/K and eV=1.602176634e-19 J. Model fit deviations and numerical integration error are distinct. The prior isotope-provider source review and existing Savin tests are reusable evidence; new verification targets thermal-feedback integration and changed seams. Root separately acquired the primary Savin paper and will attach its receipt; this author's direct reads are the pinned repository sources.

Source locators and object identities are preserved in `evidence/PINNED_SOURCES.json` and the completed intake. No scientific computation was executed for R2.


