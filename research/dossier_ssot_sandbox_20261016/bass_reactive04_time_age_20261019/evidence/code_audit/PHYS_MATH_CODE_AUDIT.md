# BR04 independent PHYS–MATH–CODE audit

**PASS_SCOPED**. Finalized at `2026-10-19T06:11:10.952412+00:00` after the parent confirmed the physics/math contract. The formal C9 start was `2026-10-19 05:58:41 UTC`. Earlier source reading and the subnormal-quantile observation were preliminary C2 inspection, not a prior C9 approval.

## Frozen contract and code

The accepted mathematical contract is `docs/AGE_CERTIFICATE_THEORY.md`, SHA-256 `3b6e022e7c1460fce82c20f2adff290695a0f5144d3067fe7a3a614da889d992`. Its bytes remained unchanged through this review. Seven new code/manifest files were checked at their final hashes, and all 118 inherited input files remained byte-identical. The source-study example has the reviewed input-contract correction; all other new sources retain the initial frozen hashes.

| File | Final SHA-256 |
|---|---|
| br04/Cargo.toml | `82ad4312044af0ec472da36434be17e0b826e331499307b22d3c64749005ac22` |
| br04/Cargo.lock | `726aaa9383bb3660afd92631d85ca9b010d8cdc39d80e804d49236656347d2d9` |
| crate/br04_lib.rs | `b23a8f1dda15e059f262b406577bb819b97cf6591b3f0fae3d50eb1f523ab730` |
| crate/birth_age_certificate.rs | `8091268f51545559ba1036beb1bce2891e51dbec8324c9391251a001fba770ae` |
| crate/tests/birth_age_certificate.rs | `8ef26047f0bb4be2d0b9d22319f88e6fed01f705239ff42e02c3118badec7957` |
| crate/examples/birth_age_study.rs | `aefe8d7b25f363d6437fdd6ba40932bd687a2d1862774c7dd953f5b6b969790b` |
| crate/examples/birth_age_source_study.rs | `e2da81aae1e57ea73a657ece1a7ce6d4029ba3cc71781447d3e612ec758a63ac` |

## Equation-to-code findings

- **Measure and units:** tau=kappa*T, age x in [0,1], born in caller count convention; emitted tau=0 and survivor tau references separated. Physical W1=T*reported W1.
- **CDF supremum and W1 formulas:** Both sides of all CDF jumps are checked. Positive plateau integrals equal the theory section3 expressions; each interval is split at the continuous quantile.
- **Stable limiting arithmetic:** phi uses expm1; psi/chi Taylor coefficients match their positive integrals; large-tau scaled formulas avoid tau squared. Subnormal quantile uses the factored removable limit.
- **Mass versus normalized shape:** Direct/log mass fields and normalized shape are separate. A zero source or empty quadrature has shape=None. A positive underflowed mass can retain a mathematical conditional shape with an explicit absolute_mass_underflow flag.
- **Physical population and ownership:** No AgeHistory/state/cohort mutation, absorption, thermal, chemical or work update is introduced. Sorting acts on an owned copy for diagnostics. Parent118 bytes, including original 105 crate files, remain identical.
- **Time and label composition:** Global age mapping (elapsed_cells+x_local)/Nt and emitted weight w_local/Nt represent the stated constant-source reference. Cache reuse is restricted to identical scalar tau within a fixed family/refinement; source row identities remain distinct.
- **Mixture upper bound semantics:** Source summary computes sum p_exact*d_label + half L1 difference in normalized label masses. W1 diameter is one and the CDF bound uses the same TV bound. It does not compute the exact unlabelled mixture distance.
- **Bound versus floating evaluation:** Theorems hold in real arithmetic. API/docs identify outputs as binary64 evaluations without directed intervals; tests use floating tolerances. No executable returned bound is presented as an outward-rounded enclosure.
- **Input rejection and failure classification:** Invalid/nonfinite/negative masses and ages are rejected. Fixed-source CLI now requires strictly positive label masses. Original fitted NoForwardProgress is retained as a representational limit; no physical no-solution inference or CX-flow change occurs.
- **Independent execution at final hashes:** Reviewer executed 15 final diagnostic tests and a before/after synthetic zero-label CLI probe. Root post-review full 224 tests/Clippy/fmt and source 384-output byte parity are separately evidenced.

The W1 identity is independently checked algebraically at the implementation boundary: for v≤b the plateau integral reduces to exp(-tau*u)*(v-u)*[phi(tau*(v-u))−exp(-tau*(b-u))]/[1−exp(-tau)]; for u≥b it reduces to exp(-tau*b)*(v-u)*[1−exp(-tau*(u-b))*phi(tau*(v-u))]/[1−exp(-tau)]. These equal the positive psi/chi or scaled-psi/chi branches. Their uniform limit is the area under the absolute linear-CDF discrepancy. Both sides of each atom jump suffice for CDFsup because the reference CDF is monotone on each plateau.

For normalized age on [0,1], the first and second moment functions have Lipschitz constants 1 and 2. The corresponding mathematical inequalities are |delta mean|≤W1 and |delta second|≤2W1. Converting to physical age multiplies W1 and first moments by T, and second moments by T². The Rust numbers are floating evaluations of these mathematical objects, with ordinary arithmetic and truncation error; they are not machine-checked directed enclosures.

## Underflow and physical population meaning

The module computes diagnostics from actual supplied nodes. It does not inject a photon population. Absolute source/survivor mass, relative/log mass ratio and a normalized shape are separate fields. For a true zero source, normalized shape is undefined. For a mathematically positive survivor measure whose total rounds to zero, a log-shifted conditional shape can remain meaningful and absolute_mass_underflow is true. This retains information about the quadrature distribution without manufacturing positive physical photons. Normalized-weight underflows are counted; moments below the f64 range may round to zero as documented.

The source-mixture study uses a positive unit source only for reuse of a scalar diagnostic and scales the absolute source label masses separately. After the input-contract correction, its CSV interface requires every label mass to be strictly positive. In the actual 4608 emitted/survivor output rows all exact and discrete masses are representable and positive; their minima are about 5.80228e-16 and5.79829e-16 in reference-comoving number density. Label mixtures and exact per-label mass errors remain distinct.

## Resolved issues and preserved evidence

1. **Subnormal quantile conditioning.** The first author test execution found 14 passes and 1 failure: W1=0.29 instead of0.15 for a subnormal-opacity case. Independent preliminary inspection identified the product-underflow mechanism. The factored thin-limit quantile corrected it, and the final independent 15-test execution includes that boundary. This changed only the new diagnostic evaluator.

2. **Zero label in the inventory CLI.** An isolated synthetic two-row input reproduced 12 output shape rows for a label with zero physical source mass in the old example. Root restricted this inventory CLI to positive label masses, while preserving the general zero-source API. The same synthetic input now returns exit code 2 with an explicit input error. The actual 384-label source inventory contains no zero labels, and root verified byte parity of all three scientific source-study CSVs after the correction.

The source had already changed when the reviewer first attempted a pre-fix copy. The old-byte identity gate rejected that copy. Only an external copy was reconstructed by reversing the known small change, and its SHA-256 was required to equal the original 05005cec… hash before compilation. This recovery and both actual probe executions are preserved. The fixture under synthetic_zero_label is explicitly synthetic, separate from native science data.

## Verification and scope

The reviewer ran 15 diagnostic Rust tests at the final seven-file identity: 15 passed, 0 failed, with Rust 1.94.1 and Cargo 1.94.1. The test source and all seven files remained unchanged during the run. Root separately reran the post-review all-target suite: 224 passed, 0 failed; strict Clippy and scoped rustfmt also passed. Those broader results are preserved in implementation receipts and logs, rather than attributed to this reviewer’s scoped test command.

No open blocking code finding remains. This audit approves the reference-measure diagnostic and its stated composition/upper-bound contracts. Applying it as a certified error bound for evolving H/He/D requires the physical response and regularity assumptions in the theory contract. The crossed native data provide finite-grid interaction measurements; complete joint convergence and the full longspan solution remain separate DAG obligations.
