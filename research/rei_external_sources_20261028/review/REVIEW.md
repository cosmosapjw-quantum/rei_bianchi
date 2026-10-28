# Independent scoped review — PASS_SCOPED

2026-10-28. Requested review tier: Astra. Actual runtime model identity: UNKNOWN; no model identity is inferred from the request or role. This fresh lane authored neither the contract nor implementation. It performed one read-only R6/C9 pass over the equations, actual code, raw outputs, test logs and rendered figure. It ran no scientific tests, rate evaluations, IVPs or plots. Artifact reads and identity checks are not an independent numerical rerun.

## Decision and admitted result

**PASS_SCOPED** for the illustrative, uncalibrated finite external-source operator and its frozen-epoch fast/thermal n/T QSS response on the same 201 saved ANGTHERM01 epochs. The delivered code and outputs satisfy this bounded construction. No blocking defect was found. One nonblocking metadata representation issue was corrected and closed by selective readback. Proceed to authorized delivery/publication of this scoped result.

This closes the phenomenological source-model subobligation only. It does not complete historical physical F4, increase original DAG counts, or produce a jointly evolved 17-state trajectory. Working33/88, central28/88 and fast4/7 remain the inherited counters. No new IVP was executed. Calibration is not a prerequisite for admitting the explicitly conditional model.

## Materials and independence

Read AGENTS.md; physmath-research-loop 1.3.0 SKILL, POLICY_INTEGRATION, R6 and C9 definitions; final FROZEN_CONTRACT.md including the saved-density amendment; DERIVATION_AND_DECISION.md; model.py, config.json, test_model.py, evaluate.py, plot.py and implementation README. Inspected TESTS/EVALUATION/PLOTS receipts and stdout/stderr, the 201-row/252-column CSV including rows0/100/200, the accompanying JSON, and the actual PNG through the image viewer. Prior 17-state projection and separate 257-epoch nuclear projection were read for closure and ownership context. Figure templates07/08 informed semantic and legibility checks, without converting this delivery into a journal-submission requirement.

The independent contribution is equation-to-code inspection, conservation/ownership reasoning and actual artifact inspection. The seven executed tests and residual maxima below are producer evidence, not reviewer reruns. CAS results in theory documentation are supporting author evidence. No independent physical calibration is asserted.

## Scientific checks

| Object | Observation and conclusion |
|---|---|
| Units and normalization | Stocks are particles/Href; event rates are events/Href/proper-second. Flux times cm² cross section gives s⁻¹. Capture uses cm⁻³ times cm³/s. The matching saved nHref is positive, spans 0.0017668803778189406 to 5.151254745827818e-6 cm⁻³, and is aligned to the 201 CSV epochs within the contracted serialization tolerance. Href is not relabeled evolving total baryon density. |
| Registry and hidden closure | The implemented 17 thermal entries match n, H1, D, T, He3, He4, Li7 with Li7 IV present. Four Li6 baseline columns are copied directly; their new derivatives are exactly zero and no new event targets them. Two fast entries are separate species for accounting. |
| Nuclear/CR baryons | Each photodisintegration column conserves A including the fast daughter. CR columns have internal ΔA=+1, balanced by one external proton debit. The retained projectile is included in final HII rather than also counted as a separate source. Injection/escape use open-boundary mass-number entries. |
| Charge and electrons | Atomic ionization produces one free electron. Nuclear stripping produces Z−q spectators. CR adds those spectators plus one compensating external electron. Ion injection/escape supplies/removes q electrons. Beta produces one electron and routes n→HII, TI→He3II, TII→He3III; fast T is bare and produces He3III. Capture preserves the H/D charge stage. |
| Effective energy | Photon/CR incoming energy splits into nuclear Q/binding, atomic stripping, and kinetic excess. Fast kinetic power shares particle branching and is removed once through slowing, escape or beta retention. Beta debits nuclear internal energy and separately credits electron and antineutrino channels. Capture/recombination have matching internal-energy debits and escaping radiation. These are effective-Q/excess-energy books, excluding injected/escaped matter rest mass; they are not a complete stress-energy or thermal-evolution validation. |
| Thresholds and positivity | Atomic and nuclear formulas have exact zero at/below their declared support thresholds; CR uses its explicitly phenomenological cutoff and rejects negative admitted kinetic excess. Nonnegative source rates, target-proportional losses and nonnegative transfers support component-boundary positivity. No explicit time-step positivity or calibrated cross-section claim follows. |
| Fast/thermal ownership | Nuclear and CR n/T daughters enter fast stocks only; thermal deposition is ks B only. Direct thermal injection is separate. The two source calculations compute the same source once for QSS construction and once for derivative assembly; they are not added twice to stocks. The old operator is not evaluated or modified. Future assembly must remove its beta columns before adding the new ones, as documented. |
| QSS algebra | Fast B=S/(ks+ke+λ/γ), n=S/(λ+kcap+kesc), and the two T expressions match the inverse positive loss matrix. Their sum is (S0+S1)/(λT+kesc). Code preserves original baseline values, replaces only n/T in a separate state, and reports stable daughter derivatives rather than evolved abundances. |
| External-off and sensitivity | Producer tests disable external amplitudes and escape for the complete external-only derivative-off check. Alpha0 thermal n/T stocks are exact zero. Alpha1/10 are sensitivity settings, not an uncertainty distribution. Gamma and total T scale as contracted; ion fractions can respond separately. |

Source/transport limitations are correctly carried into the result: replenished local photon flux is not transported emissivity; old nuclear histories are not spliced; inverse weak is NOT_INCLUDED_BY_MODEL rather than measured zero; finite slowing/escape hazards and gamma=1 are adopted approximations. Lumina discussion of source forms is not evidence that a Lumina simulation table was imported.

## Actual numerical evidence

All seven producer tests passed in one attempt. The actual 201-row evaluation completed with the following maxima, all below the frozen 1e-12 relative criterion:

| Residual | Observed maximum |
|---|---:|
| Baryon balance | 2.0140978615294592e-16 |
| Charge/electron balance | 8.176402321968768e-16 |
| Effective-energy balance | 3.55698090318821e-16 |
| Thermal n/T QSS equation residual | 8.52600529408672e-17 |

At z=20, nominal thermal stocks are n=7.324651248144967e-23, TI=1.401558545162758e-20 and TII=4.503363492469801e-19 perHref. The separate fast stocks are n=8.2386284701104e-24 and T=7.284178016194928e-20 perHref. Rows100/200 retain the same interpretation. Nearly horizontal curves are consistent with fixed source amplitudes and dominant direct injection; they are not evidence of an evolved stationary universe.

Fast relaxation times are 82.38295318127251 s for n and 72547723.48991832 s for T; thermal times are approximately 878.4 s and 560528677.4268198 s. Their comparison to a physical coefficient/source history has not been established and is not silently inferred from the algebraic residual.

Actual child CPU costs recorded by the producer are tests0.348972 s, evaluation0.5466209999999999 s and plots1.152358 s, each within its allocated phase limit. Receipts report zero retries and no new IVP. Controller retains responsibility for cumulative ledger restoration; this review does not reset or transfer any cost.

## Figure review

The four panels show source-family rates, thermal n/T QSS, fast slowing/escape/beta fractions and positive energy output channels. Axes agree with CSV units and mean redshift; the title/caption explicitly say illustrative, uncalibrated and frozen-epoch QSS rather than time evolution. Alpha0 exact-zero behavior is annotated instead of fabricated on log axes. Signed internal energy entries remain available in the CSV and are not misrepresented as positive heat.

The actual PNG has no blocking clipping or label collision at delivered screen size. Legends distinguish n/T, branches and alpha1/10. The upper-right legend covers a short segment of the top curve, but that curve remains visible across most of the domain; this is nonblocking. At a future single-column print width the legend/caption would be the first legibility risk; no publication-print suitability is claimed. Current layout is adequate for this deliverable; no render repair is requested.

## Exact remaining obligations and stop

Closed representation finding: the original `eta_exact_alignment=true` label overstated the actual `allclose(rtol=0, atol=5e-15)` check. The reviewer authorized one metadata-only correction to `eta_serialization_alignment_pass=true` with `eta_atol=5e-15`. The coder changed only emitted labels/current JSON, preserved the original JSON under `outputs/before_metadata_label/` and left raw stdout untouched. Selective reviewer readback confirmed the corrected fields; CSV/PNG hashes match the originally reviewed artifacts. The repair receipt records unchanged normalized JSON content and protected raw logs. No scientific/test/plot rerun was needed or performed; this was not a new scientific review cycle.

No obligation remains for the admitted pointwise phenomenological implementation. For a physical prediction, separately calibrate spectra, cross sections/yields and charge probabilities; justify transport hazards/retention and source history; compare relaxation to background/source variation; and authorize/validate any later coupled evolution. A later full operator must assign beta ownership once. None of these is grounds to withhold the current scoped result or to start another review cycle.

Final disposition: **PASS_SCOPED**. Required repair: none. Positive next action: controller integrates the decision and publishes/backups the authorized artifacts with the stated scope.
