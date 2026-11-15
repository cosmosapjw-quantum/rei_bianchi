# AX08 independent incremental decision

**PASS_SCOPED_CONDITIONAL_FIVE_CASE_BASELINE. The original AX08 acceptance is met; admit AX08 as completed at the conditional baseline-family scope.** This decision concerns the original `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1` family over mean redshift 20→4. AX11 convergence, AX12 robustness, AX15 full-goal scientific admission and AX16 release remain separate. They are not prerequisites added to AX08.

The reviewer did not start a native solver and did not repeat the four-case reduction. The frozen four-case review is reused. This incremental review independently processed only the new complete `q_ref=+0.01` native history, checked the composed bytes and final checkpoint, reconstructed source identity, inspected the actual terminal and ledger evidence, and verified the new full normalized and sampled response products. Review independence is methodological and agent-level, not blind: the implementation authors supplied paths and scope. The complete ledger scan was executed once by the geometry agent; this reviewer inspected its exact scanner and outputs and independently recomputed the endpoint inventories rather than repeating its approximately 700-MB scan.

## Original acceptance mapped to actual evidence

| AX08 acceptance | Decision and evidence |
| --- | --- |
| Produce full histories for `q_ref={0,+0.005,-0.005,+0.01,-0.01}`, reuse matching AX07 ZERO, preserve source/IC/provider and solved gas/ne/T | Met. Four frozen histories plus the new 312,238-row exact `SHEAR_PLUS` composition provide 1,561,190 represented native rows. The new source has its original conditional IC and source/provider/numerical formulas. Original whole-source hash differences are confined to resource/output allocation, as independently reconstructed below. |
| Physical-density-fixed primary background, quantitative approximation validity and actual signed responses | Met at the specified diagnostic scope. Native `H²=H_FLRW²+s²`, free-decaying signed `s`, and `Sigma=s/H` checks pass. Five-case forced-background stress and source-defined extra-energy diagnostics remain below the unchanged `1e-4` thresholds. Signed responses are retained for fixed mean redshift and separately for fixed elapsed proper time, with both candidate/reference coordinates. |
| Complete time-ordered baseline H/He/electron abundance rows, correct element fractions, baryon Y, charge and actual proper-time/Tgas semantics | Met. The new full normalized table contains all 312,238 native rows without resampling, including the five ionic/neutral fractions, their baryon number abundances, `Y_e`, `xe`, proper densities, time and temperature, with explicit normalization registry. Its public manifest pins private bytes. The 5,005-row five-case sample is labeled as a sample and does not replace complete histories. Native segment abundance products are also preserved in the recovery evidence. |

The historical original STATE at `fef2baf960f57f37b838004fbb8a7d37b3824852` had AX00–AX07 and AX13 completed: 9/17, with AX08 in progress. Applying this scoped decision to AX08 alone supports **10/17 original workflow nodes**. This is not a full-goal science fraction, and it does not modify the distinct historical 28/88 expansion DAG. The reviewer has not mutated owner STATE; the owner should attach this receipt and record the actual node transition.

## Native endpoint, composition and identity

The native terminal receipt records exit 0 at 2026-11-15T16:09:09Z. The original restored physical state reached `a=0.2`, accepted=312,237. The new continuation used 71,757 accepted steps, 1,513,308 RHS calls and 1,760.78 seconds; its terminal checkpoint save returned `Ok(())`. Original missing predecessor exit information and charged prior work remain explicitly preserved.

The reviewer independently reconstructed the composed byte stream from the three immutable histories. The 200,001 initial rows, 40,480 added supported rows from continuation001 and 71,757 added new rows give 312,238 unique states. Both duplicated boundaries are identical in every byte. Exactly 47 unsupported continuation001 tail rows are excluded, not promoted or deleted. Final physical columns and accepted count match the durable checkpoint.

- Complete history SHA-256: `e1b0c293302ec5ab9a56d525631098227205556e9902db6bf277e8d307460560`.
- Final checkpoint SHA-256: `671f1295428dc652304e9dd7f9d097e3330aaf272aba271fe99cd987acb521a5`.
- Consumed composition manifest SHA-256: `4873f340182b78bc9a3263873136b71bb66aa9a62db8a3a34f9446ed2c2053ef`. Its exact bytes are preserved as `PLUS_COMPLETE_COMPOSITION_MANIFEST_CONSUMED.json`; later source-location enrichment has a separate hash and provenance link, without a science rerun.

Original ZERO/PLUS corpus `d7676b…` and the other three complete signed-case corpora `4de69c…` are not byte-identical. The reviewer applied only the three documented output-budget edits to the original driver component and obtained exactly driver hash `92bc6c…` and complete corpus hash `4de69c…`; the other 16 source components remain byte-identical. This establishes the required shared physical/numerical model while preserving distinct resource provenance. The new wrapper binary also has its own identity rather than being mislabeled as the original binary.

## Physical and numerical checks on the actual new history

Current-turn Python execution passed. All 12 native-data checks succeeded: complete ordered domain, case identity, finiteness, positivity and provider temperature domain, charge/nuclei/baryon normalizations, radiation moment cone, photon inventory, reflection-even control and background identities. Largest charge and baryon residuals were `2.23e-16`; the relative Hubble-constraint residual was `1.23e-15`. `J0` equals the saved photon-energy inventory exactly and `max |J1|/max(J0,1e-30)=5.8066e-16`.

The source cumulative ledger controls are dimensional residuals divided by declared positive inventory scales. The endpoint energy residual is **7.318674330632213e-8 eV/H**, not a dimensionless error. The reviewer independently reconstructed that exact value from checkpoint thermal/binding terms, active photon energy and the signed source/work/escape/CMB ledger. The injected energy is 90.16154524362464 eV/H, giving normalized residual `8.117290260339365e-10`, below `1e-8`. The independently reconstructed photon-count residual is `-7.691625114603085e-13` per H and its normalized magnitude is `1.7298e-13`.

The single complete three-segment ledger scan retained 27 ledgers at every one of the 312,238 unique times. It removed 54 identical boundary ledger rows and excluded 1,269 ledger rows belonging to the 47 unsupported history states. All three actual controls have 312,238 PASS entries; the other 24 ledgers are informational VALUE entries. Maximum `|residual|/tolerance` is `4.1269e-5` for photon count, `0.2727827395` for augmented energy and `0.0005806584` for J1. Nonfinite values and control failures are both zero. These checks do not establish evolution convergence.

An independent initial-direction GL32 and long-double proper-time trapezoid calculation gives, for the new plus case,

| Quantity | Production | Independent check |
| --- | ---: | ---: |
| max absolute total `delta_s/H` | 1.014434481527696e-5 | 1.0144344815284568e-5 |
| max source extra-energy ratio | 9.682725793760002e-8 | 9.682725793706239e-8 |

The stress difference is `7.61e-18`; both methods locate its native-node maximum at `zbar=4.886481466322657`. Across all five cases, the largest stress and energy ratios remain the previously reviewed minus-case values `1.0210497766163151e-5` and `9.728861295902034e-8`. The calculation holds the saved geometry fixed. It excludes the `-3s delta_H` coupling and distribution feedback of a closed linearized Einstein–matter calculation and supplies no coupled abundance error bound.

## Complete outputs and response interpretation

The complete normalized plus table has SHA-256 `fb9c0821b4180bed9f65d807ddb0e8b39a6e6a35567e8f0235f611512b3c75f6`; its row/column contract and private data hash were checked. Six independently calculated native normalization spot rows match exactly. The original 4,004 sample rows and all four original diagnostic records are unchanged in the combined products.

For every reported species/electron/temperature field, the reviewer verified interpolation of the new native normalized output, the frozen reference/minus arrays, signed subtraction, odd/even decomposition and reported sample extrema. Both coordinate modes retain candidate/reference proper times and mean redshifts. For example, the sample maximum-magnitude H II response is `-2.467175663878329e-6` at fixed mean redshift but `+1.71027169896254e-5` at fixed elapsed proper time. These are different comparison questions; the code does not claim both coordinates match. The reported H II odd part is about `5.52e-15` and remains numerically unresolved. Being above a predeclared response floor would also not establish resolution without AX11.

The first upward native H II crossings of 0.1, 0.5 and 0.9 were independently bracketed and reproduce the producer's rows, proper times and mean redshifts exactly. The optional instantaneous absorption-residence diagnostic was checked at all nine reported peak rows: its rate and dimensionless `|s|/lambda_abs` match exactly. The ratio and its cube remain explanatory estimates under the stated quasi-stationary absorption assumption, not abundance coefficients or error bounds.

Five prepared-consumer unit tests passed once in this review. Actual execution and the checks above then verified the changed output path, rather than inferring success from those unit tests alone. No additional full-history campaign, old-four rerun or private owner stage08 payload publication was performed.

## Disposition

There is no remaining correctness or original-acceptance blocker for conditional baseline AX08 completion. Record the actual owner admission with this review, source manifests, complete output bindings and the five-case products. Retain AX11/AX12 and subsequent full-goal scientific decisions as pending. Preserve the original scientific thresholds and the explicit distinction between complete conditional histories, numerical resolution and physical model accuracy.

Machine-readable decision and reviewed hashes: `AX08_FIVE_CASE_ADMISSION_REVIEW.json`. Supporting executable/evidence files are `ax08_plus_independent.py`, `AX08_PLUS_INDEPENDENT_NUMERICS.json`, `AX08_PLUS_COMPOSITION_CHECK.json`, `ax08_product_checks.py`, `AX08_FIFTH_PRODUCT_CHECKS.json`, and `AX08_SOURCE_IDENTITY_CHECK.json`.
