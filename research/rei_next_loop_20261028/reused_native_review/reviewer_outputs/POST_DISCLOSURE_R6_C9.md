# Post-disclosure native independent assessment — R6 and C9

## Outcome

**The finite caloric algebra, implementation, and preserved frozen-source diagnostic are supported within the declared represented-input scope. One precise correction remains in the written source-temperature relation: the exact relation for separately represented source fields must include the saved temperature-product residual. The implementation already retains that residual, and the released data show that it is nonzero.**

| Stage | Final independent disposition | Scope of admission |
|---|---|---|
| R6 | **PASS_SCOPED_WITH_EXPLICIT_REPRESENTATION_RESTRICTION** | R5 sections 1–7 and the source-bath/weighted-composition derivations are supported. The source addendum's uncorrected ratio equation is admitted only as an unrounded defining relation. For represented fields, the corrected F1 identity below is required. This is not an unrestricted pass of the original ratio wording. |
| C9 | **PASS_SCOPED_REPRESENTED_INPUT_AND_FROZEN_SOURCE_DIAGNOSTIC** | The inspected core and source adapter correspond to the equations; original input identities and saved execution evidence are consistent with the inspected code. No caloric-core implementation repair is indicated. Physical REI output, physical uncertainty, provider accuracy, and thermal-feedback convergence are not admitted. |

The minimum remaining action is a local equation/scope correction documenting F1, or an explicit restriction of the published claim to the corrected relation recorded here. Neither a source-value change nor a new provider execution is warranted. The historical He-branch provenance limitation F2 remains; the narrower inert-He source model is directly supported by the original producer and original transaction.

## Review identity and disclosure boundary

Native task: `/root/finite_thermal_native_blind_review`. Project `cosmosapjw-quantum/rei_bianchi`, unit `finite_thermal_endpoint_20261028`, branch `research/rei-causal-prefix-consumer-20261027`, review pin `b77c7b8d45c48a7e4722e733309430d5ba668b0d`.

Root acknowledged the provisional report and exposure log and explicitly released phase 2 at `2026-10-28 06:19:19 UTC`, as recorded in `PHASE2_RELEASE.json` lines 1–39. The preserved phase-1 hashes remain unchanged:

- `PROVISIONAL_R6_C9.md`: `4f885cc610b08174d466548fe68dbc0bbb491ed6a44460901be6ef6fc59d9b5e`.
- `READ_EXPOSURE_LOG.json`: `3c7943ce2fcfcfcbe6777bb29013106dd7daf9902893de497b425335b205972f`.

The earlier isolation acknowledgement remains applicable: no substantive parent conversation or earlier review was initially visible; the host documents `fork_turns=none`, but hidden context delivery cannot be independently attested. This is a native source-data-blinded review with logged exposure, not cryptographically proven isolation. After release, raw execution statuses and result values were intentionally visible. The final assessment below is based on code, equations, assertions, and selected raw scientific values, not on the number of passing checks.

No test suite, study, source consumer, provider, CAS, or IVP was executed during this assessment. Mechanical operations were source/JSON reading, selection, hashing, and report preservation. Historical unknown costs remain `UNKNOWN_NOT_ZERO`.

For compact references below, `EVIDENCE/` denotes `delivery_prep/preserved_evidence/extracted/` beneath the review directory. The complete read/exposure record is in `PHASE2_READ_EXPOSURE_LOG.json`.

## What changed after disclosure

| Provisional item | Phase-2 evidence | Final treatment |
|---|---|---|
| R5 core equations and static implementation correspondence supported | Pinned fixture source, individual C6 outcomes, original transaction inputs, C7 checker assertions and raw outputs, and two distinct C8 studies agree with the inspected algebra | Supported within the original positive-domain and representation assumptions |
| F1: source-temperature ratio needs a product-residual term for separately represented values | C7's saved bridge contains an explicitly nonzero exact `theta_minus_kBoltz_native_eV` | Confirmed for the actual frozen representation, not merely a generic possibility |
| F2: original-history one-way He transition was not independently verified | Original transaction explicitly describes inert source He; original source clock NH is now directly readable. The named native history/header originals remain absent | Narrow source-bath premise strengthened; broader historical branch claim remains unverified |
| C9 execution/source-data acceptance withheld during phase 1 | Exact source/literal/test identities and corresponding saved run/result evidence are now available | Pending evidence condition closes for the declared caloric diagnostic scope |

## F1 confirmed: exact correction and minimum remedy

The provisional report identified the represented-input gap in `SOURCE_BATH_DERIVATIONS.md` lines 38–42, corresponding to original source-bath note lines 72–76. `producer_native.py` lines 102–109 forms the product in binary64. `finite_thermal.py` lines 384–388 preserves the independently represented operands and their product residual.

The original C7 stdout, JSON path `/temperature_bridge/theta_minus_kBoltz_native_eV`, contains exactly

`delta_theta = -393372660608921 / 40564819207303340847894502572032 eV`.

Its numerator is nonzero. Therefore the unrestricted displayed equation

`T_a^E / T_native = kBoltz_source * EV_source / k_B_SI`

does not hold for these separately represented fields. The required exact identity is

`T_a^E / T_native = kBoltz_source * EV_source / k_B_SI + delta_theta * EV_source / (k_B_SI * T_native)`.

Equivalently,

`T_a^E - T_native = (kBoltz_source * EV_source / k_B_SI - 1)*T_native + delta_theta*EV_source/k_B_SI`.

This conclusion uses the independently derived formula from phase 1 and the released nonzero raw residual. It does not rest on a prior audit disposition. The adapter already derives `T_a^E` from the supplied `theta_eV`, stores the native temperature separately, and returns both the source-constant factor and the product residual. Its result is not the faulty constant-factor-only substitution.

**Minimum correction:** annotate the original ratio equation as the unrounded source defining relation and add the exact represented-input identity above. Preserve all original source values, existing output fields, and prior raw results. A broad code repair or rerun is unnecessary. If a focused regression check is desired for the corrected published statement, use the existing bridge output or a manufactured nonzero product residual to check the two-term identity; do not rerun the provider. The current review itself has not executed that check.

The existing fixture at `test_finite_thermal.py` lines 170–176 already uses a deliberately inconsistent energy/native-temperature pair and checks the nonzero product residual. It supports preservation of this information, but it is not a test of the corrected two-term ratio wording.

## Original input and code identities

Mechanical read/hash checks obtained the following identities directly from the released bytes:

| Object | Size / identity | Relation to the reviewed implementation |
|---|---|---|
| Original BASS transaction | 3,554,206 bytes; SHA256 `a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac`; Git blob `a9ea559f123da6c8f1fe070139bc80145d4582fc` | Matches `finite_thermal.py` constants and preserved C7 input checks |
| Original literal packet | 8,281 bytes; SHA256 `b77aba9612584ffd74e2cdd951c0b9e2b573113bd7195c04d8cc857354cfe34f`; Git blob `ea4bd58d394a421533407b5d12acf2468b32fdcd` | Matches the immutable literal binding accepted by the adapter |
| `finite_thermal.py` | SHA256 `8482189fb3f7fd66d7b164517d0cce11431d315a5492ed3632643ff5100cf14d` | Matches the initial packet and the C6/C7 recorded implementation identity |
| `run_once.py` | SHA256 `14def6a0c42067e17a19cc638703c2b751ae82f28ba594171391458b577ebe68` | Matches the initial packet and C6/C7 recorded runner identity |
| Pinned fixture source | SHA256 `06aa8e39da065ecd495da30cd0294efaa07522420bcb6a6fe9bc3066ee113379` | Matches C6/C7 recorded test identity |
| C7 scientific stdout | SHA256 `2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948` | Matches the saved-output input pinned by both C8 studies |

The primary C8 script hash matches its process record. The companion script's extracted copy and pinned Git-evidence copy have the same hash. The C6/C7 authorization files also match their consumed-authorization marker hashes. These are proportional reproducibility/identity checks, not a new adversarial-security claim.

The original transaction's `/finite_solution/clock/nH_reference_m3` is `250250485.0551194846630096435546875`, consistent with the supplied original binary64 reference-NH representation; its saved clock `h` is likewise available. The adapter correctly keeps the separate density diagnostic rather than replacing the reference NH with the endpoint density. The original transaction's `gas_thermal_owner` explicitly includes inert source He, and saved initial/final electron fields equal the separately saved continuum stock fields for this producer. This strengthens the narrower source model used in F2.

The full historical `SOURCE_OPERANDS.json`, `TUBE_RESULT.json`, `FINITE_TUBE_INPUT_SLICE.json`, native `history.c`, and `hyrec_params.h` files were not supplied/read. The original literal packet candidly describes its manual transcription and earlier readback limitations. This review admits the pinned declared representation and its consistency with the released transaction; it does not claim an independent reconstruction of every upstream transcription or the entire native history.

## C6: meaningful checks and limits

The complete pinned `test_finite_thermal.py` lines 1–272 was read before the execution outcomes. The caloric tests include fixed rational expected answers for zero events, positive/negative heat with changing particle counts, one application of geometry work, and a nonzero initial-EOS mismatch separated from interval balance. The mixed JVP is checked with the cross-multiplied caloric identity; normalized and proper-coordinate JVPs retain their non-cancelled individual derivatives. Count tests use independent electron and fine-stock defects. The helium tangent test varies both NH and fHe. Segment tests include the reference-volume product term and associativity. The interval fixture reaches an actual worst corner of the supplied error bound. Unknown radii remain unknown.

The typed-decoding fixture distinguishes the exact dyadic representation of `0.1` from exact decimal `1/10`, checks the hexadecimal form, and rejects invalid encodings. Gas ownership tests use distinct values in all five slots, so selecting the wrong slot would be observable. Authorization and outcome-classification tests are explicitly pure logic fixtures; they do not claim to test real signal delivery or launch failures.

The original `C6_RAW/attempt_01/stderr.txt` lines 1–32 records each corresponding test outcome and a completed unittest run. Its result file has exit code zero, no recorded resource overrun, no automatic retry, and no scientific admission from the runner itself. The individual assertions and the phase-1 algebra are the basis for acceptance; the printed count is not a substitute for either.

## C7: original source adapter result and residual interpretation

The checker at `C7/verify_saved.py` lines 22–68 rereads the original source and literal bytes, reconstructs the count and energy operands without importing `finite_thermal`, and compares them with the preserved stdout. Its alternate literal path uses `Decimal.from_float` before conversion to Fraction. Its scientific formulas reproduce the specified construction, including the independently saved `Ua`, full bath count, distinct residuals, and gas-slot ownership. It explicitly identifies itself as same-author evidence, not an independent-author verdict.

The original source stocks, independently saved electron fields, all five energy/work vectors, volume ratio, source residual lexemes, and physical-radii fields were read directly. The C7 exact numerator/denominator records and selected scalar fields agree in sign, role, and representation with the inspected construction. The following decimal strings are display values preserved in `C7/evidence/SAVED_SOURCE_CHECKS.json` lines 305–332; the exact records at lines 195–303 remain authoritative:

| Saved diagnostic | Preserved display value |
|---|---:|
| Initial source-energy temperature | 3003.7512272777059096076544 K |
| Initial native driver | 3003.7478329491555086860899 K |
| Right native driver | 3003.4927947892815609520767 K |
| Saved source-caloric endpoint | 3003.4174822862768217324805 K |
| Saved minus reconstructed endpoint | −6.2972569110885162919256541 × 10⁻⁶⁷ K |
| Saved endpoint minus right driver | −0.075312503004739219596232061 K |
| Initial energy/native convention gap | +0.0033943285504009215645300543 K |
| Inert He per reference volume | 1.9898242985643963183841759 × 10⁷ |
| Initial EOS residual `r0` | +1.0934456573772629960420588 × 10⁻⁸¹ J per V0 |
| Interval balance residual | −8.2823 × 10⁻⁸¹ J per V0 |
| Aggregate energy residual `rE` | −7.1888543426227370039579412 × 10⁻⁸¹ J per V0 |
| Count residual `rN` | −5.1329999999999358678 × 10⁻⁶² per V0 |

The exact direct temperature discrepancy and residual-identity discrepancy are identical saved numerator/denominator objects. The output retains nonzero stock, electron, energy, and volume-encoding defects. Those defects are not clipped or relabelled as physical errors.

The saved negative controls are also informative: using an H-only denominator with the full source gas energy gives approximately 3211.99937131 K, a positive relative bias of about 0.06944818; applying work twice shifts the result by about −0.51003522 K. These are deliberately incorrect counterfactual formulas evaluated in the preserved evidence. They support the source-bath and single-work interpretation, without changing the actual source result.

The six-term saved driver-gap decomposition follows algebraically by adding and subtracting the initial driver, initial energy temperature, and reconstructed endpoint. The inspected `decompose_saved.py` lines 6–25 and saved exact zero decomposition residual do not add new physics or independent source data. The driver gap cannot be attributed to representation roundoff alone, and none of this establishes a self-consistent thermal-feedback trajectory.

## C8 primary and companion: distinct evidence, one stage

Both original scripts and their selected raw result arrays were read. They use the same pinned C7 stdout but perform different saved-data analyses. Their preserved 81-check and 158-check labels describe two different evidence sets within C8. They are not combined into another stage or counted as independent physical datasets.

The primary study at `C8_PRIMARY/code/study.py` lines 88–190 develops relative residual transport, exact box corners, common-scale cancellation, Taylor remainder, precision sensitivity, and a binary64 comparison. For `u=rE/E` and `n=rN/D`, the exact relative discrepancy `(u-n)/(1+n)` and remainder `n*(n-u)/(1+n)` are correct. The extreme count-margin rows are expressly synthetic. They demonstrate growth of an absolute-radius bound near a vanishing denominator margin, not a physical trajectory or global impossibility theorem.

The companion study at `C8_COMPANION/code/c8_conditioning.py` lines 99–202 also separates aggregate-variable and primitive-input condition numbers. Its primitive `cv` sensitivity correctly contains the cancellation `P-1=-(Q+W)/E`. Its fixed-cv and variable-cv box corner formulas use positive denominators and include the cross term when cv varies. For the direction `deltaE=2E`, `deltaD=3D`, the central-difference relative error `9h^2/(1-9h^2)` follows directly from the quotient; the saved sequence is consistent with that exact expression.

The critical numerical distinction is preserved explicitly by the companion's lines 125–129:

- Direct subtraction of rounded temperatures loses the tiny discrepancy.
- Reconstructing `rE` and `rN` from the same rounded endpoints cannot restore the information already lost.
- Rounding residuals that were retained exactly beforehand uses a different information set and preserves the discrepancy in this experiment.

The saved primary precision rows show direct discrepancy zero at precisions 16 through 64, `−1e−66` at precision 70, and increasing recovery at higher precision. The retained-residual route at precision 16 already gives `−6.297256911088514e−67`. The companion's rounded-endpoint residual route is zero at precisions 16, 24, 40, and 60, while its independently retained residual route is nonzero. Binary64 direct subtraction is also zero in both studies. These raw outcomes accord with the large subtraction condition number, approximately `9.5388e69`, and the much smaller retained residual-numerator condition number, approximately `2.5979`.

The decoder-only counterfactuals remain labelled as consumer re-encoding contrasts with unchanged provider energy ports. They do not claim a coherently recomputed alternative source. The primary convention-adjusted right-driver comparison uses a declared comparator rescaling; it must not be presented as the independently saved right energy-temperature field. That field was not supplied. The original source-caloric output and all physical-null fields remain unchanged.

## Execution observations and evidence limits

The preserved raw process records show zero exit codes for C6, C7, and each distinct C8 study. The inspected stderr files are empty apart from the expected C6 unittest progress on stderr. The external inclusive CPU figures are 0.148771 s for the C6 command and 0.124835 s for the C7 source command; the distinct C8 child-process records are about 0.061126 s and 0.059376 s. These observations describe their recorded command boundaries only. Observer, preparation, preservation, and other historical costs are not silently folded into those measurements or declared zero. Child CPU is not added again to an already inclusive external total.

This review did not rerun the recorded computations and does not attest to unrecorded runtime events. It also did not use prior prose reports, prior audit conclusions, CAS submissions/observations, or plots to decide the science. It inspected original code and raw selected values sufficient for the scoped claims. JSON parsing of a large file is not represented as a review of every semantic field; exact selected paths are recorded in the companion log.

## Claim ceiling and bounded next action

The admitted result is the conditional finite common-volume caloric map, its residual/JVP/enclosure/composition algebra, and a faithful diagnostic for the pinned declared BASS representation. General-EOS inversion and affine-polytope extremization remain theoretical results on their stated assumptions. Weighted fractional-power evaluation remains outside the Fraction implementation.

Actual REI recipient bath, recipient baryon normalization, native25, temperature update, physical radii, and global physical completion remain unresolved; `full_state_update` and `L4_ready` remain false. No amount of arithmetic agreement converts the represented residual into a physical error radius.

The bounded action arising from this review is to correct or explicitly restrict the F1 source-temperature equation. No source provider change, caloric-core repair, broad test rerun, new IVP, or new review framework is indicated. After that local statement is made precise, the current scoped R6/C9 evidence supports continuation according to the controller's existing authorized next action, while `AUTO_NEXT_NODE=false` remains in force for this reviewer.
