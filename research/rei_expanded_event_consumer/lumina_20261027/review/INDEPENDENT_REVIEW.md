# Independent scientific review — REI-LUMINA-20261027

Reviewer: separate `lumina_review` agent. Requested Astra/high; actual runtime model identity unexposed. This reviewer did not author the scientific candidate or implementation and performed no scientific execution or repeated tests. Review date 2026-10-26 UTC.

## Decision

**PASS_SCOPED_SOURCE_CONTRACT_AND_STATIC_IMPLEMENTATION; HOLD_EXECUTION_ADMISSION.** The adopted physical algebra, Table 1 moment transcription, typed reference scope and corrected source adapter are coherent within the frozen contract. The only execution attempt was killed by its CPU timer before returning test outcomes. No implementation-test pass is admitted. Canonical completion remains 29/88, with no newly closed canonical node.

## Evidence actually read

- Primary arXiv v2 HTML, https://arxiv.org/html/2605.15310v2: §§3.1–3.4, Table 1, §4, §§8.1–8.4 and §9.7. Direct publisher open failed in this review lane; no claim of publisher-byte retrieval.
- Exact public HI, HeIII and tau headers and selected source rows; data/DATA_CONTRACT.md and schema evidence.
- theory/FROZEN_CONTRACT.md, source/radiation_moments.json, and raw Wolfram expression/result files.
- implementation/lumina_adapter.py, test_lumina_adapter.py, run_bounded_tests.py and PREEXEC_MANIFEST.json.
- implementation/attempt01/RECEIPT.json and both actual empty log files.
- Restored AGENTS.md and prior six-state derivation/handoff for claim boundaries.

## Independent physics and mathematics assessment

The stoichiometric columns conserve H nuclei, He nuclei and charge under their stated species ordering. Charge neutrality gives xe=xHII+y(xHeII+2xHeIII), y=Yp/[4(1−Yp)], hence 22/19 at complete primordial ionization for Yp=.24. The mass/volume covariance relation is an exact weighted-average identity; subvolume medians supply neither a global mean nor the density–ionization covariance. The temperature equation follows by differentiating u=3nt kB T/2 together with the particle-number balance and reproduces −2HT in the homogeneous adiabatic limit.

All seven numerical moment rows were independently compared to the primary Table 1. Photon-number cross section, absorbed-photon excess and incident mean photon energy use different weightings. Multiplying their defining integrals verifies sigmaE=sigmaN(threshold+excess)/meanEnergy; absorbed energy equals threshold times ionization rate plus primary excess. The explicit exposure is c*n_gamma for isotropic radiation, not net flux magnitude. Proper/comoving and physical/reduced-speed conventions remain distinct.

The observer-defined optical-depth differential is scalar; a Bianchi mean-scale-factor label does not replace observed null-ray redshift. Lumina is an isotropic reference. Its omission of photon redshifting, reduced speed and primary-excess-as-heat prescription do not overwrite the project's native kinetics or stress-energy closure. Missing actual incident radiation, mass-weighted electron history, bath inputs and downstream native energy/ray owners remain named dependencies.

## Findings and disposition

1. **HeIII source-label inconsistency — contained, source semantics unresolved.** At z=2.992408, declared p15.87=.994614769 exceeds median=.993331657 and p84.13=.990400757; declared minimum=.995683316 exceeds maximum=.954207656. The contract preserves raw bytes/labels, suppresses intervals and admits the median separately. Figure 22's complemented helium quantity suggests an origin but does not prove the export procedure.
2. **Missing-helium shortcut — closed in contract.** Early public values give xHII approximately 1e−6 and xHeIII=1.26666667e−5, so xHeII=xHII−xHeIII is negative. Code requires an independent valid helium simplex instead of manufacturing an electron history.
3. **Mean excess mistaken for kinetic support — closed statically; execution check pending.** The 100–200 eV row reaches 186.4 eV for HI and 175.41 eV for HeI although their mean excesses are below 150 eV; its HeII endpoint is 145.58 eV. The late HeII bin reaches 1945.58 eV despite mean excess 13.5 eV. Contract and kinetic_support now use full upper support. Aggregate moment evaluation is independently valid and is not rejected solely by the kinetic grid limit.
4. **Late active-species index bug — repaired before execution.** The loader initially indexed excess[0] while checking sole active HeII. It now uses SPECIES.index(s) for both cross section and excess. Static reinspection closes the defect; runtime regression remains unestablished.
5. **Raw label loss — closed statically.** Original fraction-column labels now survive parsing rather than being replaced by generic labels. Source bytes remain unchanged.
6. **Numeric speed/label mismatch — closed statically.** Proper-energy conversion now binds numeric c_rate to the declared true-c or 0.2c convention. The targeted test rejects the previous approximate 3e10 value under an exact true-c declaration.
7. **Energy partner — confirmed.** The code uses threshold+absorption-weighted excess, exposes sigmaE and leaves late inactive HI/HeI routes None. Tests cover the energy-density/absorption equivalence and inactive ownership.

## Execution outcome and limits

Attempt01 exited −27 (SIGPROF), child CPU .061393 s, child wall .062644139 s. stdout.log and stderr.log are both zero bytes; neither TEST_RESULTS.json nor BENCHMARK_PANELS.json was returned. The logs do not establish how many tests began or completed. Input hashes match the pre-run bindings.

Measured child CPU plus wrapper .032188525 s and reserved receipt tail .01 s gives debit .103581525 s, exceeding the .1 s reservation; cumulative planning debit is 9.978508078/10 s. This is a resource-limited execution failure, not evidence that the equations or tests failed. No automatic retry or budget reset is justified by this review. A resumed check needs an explicit adequately sized execution allowance and must retain this attempt's debit and raw record.

## Source-data figure review

**PASS_SCOPED_SOURCE_DATA_VISUALIZATION.** The reviewer opened the final delivery/lumina_public_benchmarks.png after the targeted HeIII label repair and read delivery/RENDER_REPAIR_RECEIPT.json. Its final PNG SHA-256 is 88736897ed0d42887f597df48f68cab401b0c29eeab07017948a7cac61343e15. The four panels visibly preserve native redshift ranges: HI with labelled spatial quantile band, HeIII median only with the unresolved 203-row quantile warning, SFRD with comoving-volume units, and cumulative tau with a separately labelled paper-reported total Planck constraint. The HeIII annotation is clear of the plotted curve after repair. The z=4.75 markers are identified as a model switch, not a measured reionization epoch. No inferred electron history, HII-complement execution or current-project physical trajectory is presented.

The receipt explicitly identifies direct source-data presentation, with no adapter runtime established. This rendering therefore supports the figure's source-data interpretation and does not replace the absent implementation-test outcomes. Its separately recorded presentation cost is not a new scientific execution allowance.

## Prepared recovery

**PASS_SCOPED_PREPARATION; NOT_RUN.** The reviewer statically read implementation/resume_validation.py, RESUME_NOT_RUN.json and RESOURCE_CLOSEOUT.json without import, AST execution or a test run. The preserved source contains 13 deterministic test methods; their outcomes remain unestablished. The proposed one-shot attempt02 requires explicit owner approval to raise the campaign cap from 10 to 11 CPU seconds and a subsequent root RUN_GO. It retains planning debit 9.978508078 s and child ledger 8.912366 s, reserves .7 s, applies a .5 s child timer, 2 s wall cap and 128 MiB address-space cap, and requires all 13 tests plus the panel export before success. This review approves the preparation's scope and does not grant the proposed resource allowance.

No new strong no-go theorem is claimed or admitted. The work advances the external source contract and moment adapter while the original canonical gate definitions and 29/88 completion count remain unchanged.
