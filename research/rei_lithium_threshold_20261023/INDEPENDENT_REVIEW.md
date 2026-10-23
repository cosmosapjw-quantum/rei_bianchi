# ANGTHERM02 independent review

**Recommendation: PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE.** The controller retains the final admission/publication decision. This recommendation applies to the declared late lithium seed, prescribed thermal/electron bath, retained atomic fits and the stated optically thin reduction. It does not certify the full coupled continuum-angular gas/photon/Einstein calculation.

Reviewer: independent source/theory reviewer; no scientific implementation was written or edited by this reviewer. Actual reconstructed files, preflight evidence, all ten saved case histories, comparisons and all three figures were inspected. The independent saved-array check introduced **zero additional IVPs**.

## Recovery and evidence boundary

Two scratch interruptions occurred before the ten selected conditional cases were executed. Prepared source/theory texts survived in Git commit `1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c`. Earlier unpublished code and check logs were lost. The executable reconstruction is a new reviewed object; byte identity with the lost implementation is not claimed.

The present recommendation is based on the reconstructed actual files and fresh numerical outputs. All ten declared cases completed once. Available current failed-check/analysis logs remain part of the execution history. The original pre-reset failure logs are unavailable; the unknown first execution is conservatively debited at its original 60 CPU/90 wall limits. Later preserved tool-history measurements remain explicitly distinguished from current raw receipts.

## Mathematical contract mapped to actual implementation

The code preserves the fixed covariant directional measure \(d\mu_0\). Its characteristic energy is

\[
E=10e^{-\eta}\sqrt{e^{2b}(1-\mu_0^2)+e^{-4b}\mu_0^2}.
\]

The moving integration support is determined by the physical Li I threshold. Gauss–Legendre weights retain the active interval width; no physical-angle Jacobian or unit-normalization of the restricted weights is introduced. Empty and full support are handled separately. The moving nodes evaluate the explicitly thin coefficient and do not carry fictitious optical-depth histories.

All four native Li fractions are evolved directly. The photoionization/recombination incidence matrix, charge vector \((0,1,2,3)\), bindings \((0,5.392,81.032,203.532)\) eV and five event ledgers match the contract. Case 1 retains the signed optical-depth Jacobian columns and \(\tau'=Y_{\rm Li}k f_{\rm I}\). The primary bath uses the declared original-RHS Hermite slopes for log temperature and log electron abundance; the secondary bath is the declared same-sample log-PCHIP sensitivity control. Diagnostic heat transfer does not update the imposed bath.

The comparison construction has the required qualifications: the attenuation estimate applies to the same bath and seeded state, with an initial optical profile bounded by \(B_\star\). The global envelope begins at \(\eta=0\), and the actual late seed lies below its value at \(\eta_\star\). This does not equate an unknown earlier continuum solution with the retained M16 seed. The extremely small higher-bin count is computed in log space from retained M16 rays; it is not a uniform bound on unobserved continuum directions.

Actual model, preflight, run table, analytic Jacobian, report-grid alignment and analysis were read. No unresolved material mapping defect was found.

## Fresh preflight evidence

The saved preflight has **13/13 checks passing**, with no IVP. Its independent scalar quadrature uses a separately written characteristic expression. The following are finite numerical checks, not interval arithmetic certificates.

| Check | Actual observation |
|---|---:|
| Threshold endpoint times | 0.4541530441897191; 0.7279998916870101 |
| Constant-integrand interval-width defect | \(2.220446049250313\times10^{-16}\) |
| GL8 maximum normalized rate-integral difference | \(5.968134926366885\times10^{-11}\) |
| GL16 maximum normalized rate-integral difference | \(5.417909337147719\times10^{-16}\) |
| GL32 maximum normalized rate-integral difference | \(4.189670418114022\times10^{-16}\) across both integrals |
| Independent constant-coefficient solution versus matrix exponential | \(1.6653345369377348\times10^{-16}\) |
| Thin analytic Jacobian versus centered differences | \(4.4751679412896475\times10^{-13}\) |
| Attenuated analytic Jacobian versus centered differences | \(2.0123612108684666\times10^{-12}\) |

The unsplit four-node support control reaches a normalized defect of 1.0. It supplies a concrete failure of the unsplit coefficient representation near vanishing support, consistent with the later response comparison.

## Independent raw-array review

The reviewer read all ten NPZ histories and receipts, independently specified the charge and binding-energy vectors, and recomputed the mass, charge and event-energy identities from accepted and report states. Every state is finite, accepted times increase strictly, and all eight late report grids match exactly. The independently recomputed residual maxima reproduce the case JSON values exactly. The minimum raw Li fraction is positive, \(7.136066675025076\times10^{-16}\); no positivity repair is needed for these actual outputs.

| Quantity | Maximum over the relevant actual histories | Frozen criterion |
|---|---:|---:|
| Native Li fraction-sum defect | \(2.4424906541753444\times10^{-15}\) | \(2\times10^{-10}\) |
| Charge-event identity defect | \(2.886579864025407\times10^{-15}\) | \(2\times10^{-10}\) |
| Event-energy identity defect | \(1.2434497875801753\times10^{-14}\) eV/Li | \(2\times10^{-9}\) eV/Li |
| Reconstructed attenuated M16 versus retained M16, 190 exact times | \(2.5929480784725456\times10^{-11}\) | \(2\times10^{-7}\) |
| Split GL16 versus split GL32 | \(3.362649048099797\times10^{-11}\) | \(2\times10^{-8}\) |
| Fixed M16 thin versus attenuated | \(2.833488998987832\times10^{-11}\) | \(\operatorname{expm1}(2\times10^{-8})+2\times10^{-9}\) |
| Primary versus secondary bath, split GL16 | \(2.3851890296189282\times10^{-8}\) | \(2\times10^{-7}\) |

The independent check also reproduced the fixed-node discrepancies against split GL32:

| Fixed quadrature | Maximum absolute native-fraction discrepancy |
|---|---:|
| M4 | \(1.98067616514889\times10^{-4}\) |
| M8 | \(1.012636510152598\times10^{-4}\) |
| M16 | \(3.06125673253943\times10^{-5}\) |

The M16 maximum occurs near \(\eta=0.71975\), whereas its endpoint discrepancy is only \(3.581540108932302\times10^{-8}\). Endpoint-only agreement would conceal the threshold-response error resolved by this experiment.

Split GL8–GL16 differs by \(1.0371814518350675\times10^{-11}\), smaller than GL16–GL32. These differences are at the solver/interpolation residual scale and do not support fitting an angular convergence order. The bath comparison is a measured sensitivity to two reconstructions of the retained bath, not a bound relative to the exact coupled bath.

### Attenuation bootstrap

Both bootstrap runs have nonnegative \(F,B\) and increasing accepted \(B\). Their final optical envelopes are

- standard: \(6.032548014052767\times10^{-9}\);
- tight: \(6.032548021438158\times10^{-9}\).

Their difference is \(7.385391109312327\times10^{-18}\), and the larger result plus the declared numerical margin is \(6.132548021438158\times10^{-9}<2\times10^{-8}\). The saved neutral seed \(2.8304718104537275\times10^{-5}\) lies below both \(F_\star\) values. The saved maximum initial depth \(9.086109073274373\times10^{-10}\) lies below both \(B_\star\) values. Thus the finite bootstrap meets every frozen admission condition.

Under the derived same-input comparison assumptions, the corresponding uniform component implication is \(\operatorname{expm1}(2\times10^{-8})=2.00000002\times10^{-8}\). The numerical bootstrap is robust at the stated margin; it is not an interval-verified continuous-time enclosure. The finite fixed-ray attenuation comparison is a useful consistency check, not a replacement for that comparison argument.

## Direct figure inspection

All three images were directly inspected, including the final regenerated Figure 01.

1. **01_rates_support_li.png:** the fixed-ray coefficient steps, shrinking physical support, and Li I/Li II response are visible. The authorized repair computes the bottom-panel vertical ranges from the displayed \(\eta\in[0.44,0.78]\) window with padding. It changes display limits only. The final image has readable axes/legends and the conditional prescribed-bath title.
2. **02_signed_fraction_errors.png:** signs, native Li normalization and the split-GL32 comparison are consistent with the raw data. Fixed-node threshold discrepancies are apparent; the very small higher-charge panels carry their own scientific-notation scales.
3. **03_bootstrap_ledgers.png:** the numerical optical envelope remains visibly below the declared delta. The saved seed, signed event-energy residual and charge/fraction-sum residuals are labeled. “Prescribed-bath transfer identity” correctly describes the diagnostic energy check.

The event-energy plot and the machine-precision ledger identities do not establish conservation of a newly evolved full radiation/gas solution. The diagnostic scope is stated correctly.

## Closed mechanical findings and execution account

The controller-authorized repairs were read in the actual final files: numpy scalar and frozen-Mapping JSON serialization; equivalent tuple-tail source-row comparison; results-directory creation before logs; inherited hard CPU-cap handling in the nested launcher smoke; exact new-unit CASES import via `spec_from_file_location` after donor path insertion; and the Figure 01 display-window vertical limits. Source parameters, tolerances, cases and admission conditions were not changed by these repairs. The explicit case-table import is safe: the imported runner is protected by its module-main guard.

The final saved account at this review is **105.71851917 CPU seconds / 135.995204254 wall seconds charged**, within the declared 120/180 limits. This includes the conservative 60/90 debit and the failed recorded attempts. Known measured usage totals 45.71851917 CPU / 45.995204254 wall seconds; 1.948593 CPU / 1.986869219 wall seconds of that total comes from preserved tool history whose old raw logs were lost. The independent saved-array review contributes 0.07678817 CPU / 0.076808834 wall seconds and zero IVPs. No extra scientific runs are requested.

## Reviewed-object witnesses

The actual input driver SHA-256 is `710ae55ea075ac442a7f52fec24f64cff52a55edad7d5b832c46dbaa73ca6cae`; the retained M16 donor SHA-256 is `87196e8ff76689820c827e0f277ac00fc435df74e53c8c29c05e4d7fbd0399e8`.

Final source witnesses:

| File | SHA-256 |
|---|---|
| code/trace_model.py | `9ce3850b913567d87e51e926fd747832886ce82378f7af99d69804a66be9916f` |
| code/preflight.py | `56c1e0bda9bffc1c12db85c6783cce3995e8c0726c419d6fa0b9ed78ef10330d` |
| code/run_cases.py | `177d373850a375261cfcdd4c1561a8ff95e64d9d9f291da82632fbfdc689df40` |
| code/analyze.py | `6835806596c74faa23397ab74ac5058bcf2dd409a373b9ad50fef57481f1fb24` |
| code/bounded.py | `e3e1aa681fc74517c2886e5da9eaf49d36cfe2eaecf25d1050b30564bed2a094` |
| figures/01_rates_support_li.png | `54b305e40402518ce5f5d15dfb699312e2a5fbd1af1e5c93d692ae8533aebf58` |
| figures/02_signed_fraction_errors.png | `09163f8eea7def11c9045cb7385b2d60a1a7576cec2a4abf19bbdaec2e63060e` |
| figures/03_bootstrap_ledgers.png | `69419c8e99ec5e1dc064fdfc61debf46988dc24899245def34f11c43a643ddf8` |

The complete numerical evidence is in `results/preflight.json`, the ten saved case NPZ/JSON pairs, `results/comparisons.json`, `results/cost_receipts.json` and `results/execution_summary.json`. Source/theory intake is preserved in `sources/SOURCE_ASSESSMENT.md`, `sources/SOURCE_RECEIPTS.json` and `sources/MATH_CONTRACT_REVIEW.md`.

**Final scope:** admit the selected split-GL16 conditional threshold response and its finite controls. Keep the full coupled continuum-angular \(2\times10^{-7}\) goal open; transferring this coefficient treatment into the full system requires its own explicitly selected research unit.
