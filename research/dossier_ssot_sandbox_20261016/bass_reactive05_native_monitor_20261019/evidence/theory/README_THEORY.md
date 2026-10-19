# BR05 independent theory and panel evidence

## Deliverables and read-only scope

MONITOR_MATH_CONTRACT.md gives the positive fitted-panel derivation, exact versus bounded measure composition, source/native separation, retained-width interpretation, clock and geometry conditions, and failure/status ownership. PHYS_MATH_AUDIT.json records the corresponding review. The original BR03/BR04 source and evidence were read without modification.

Accepted means local solver success in the fixed-step native driver. The S10 adaptive four-corner controller is unchanged and is not newly monitored. Predictor observations are excluded; future adaptive callers must defer local monitor export until their own outer acceptance.

## Actual independent computations

Wolfram context was requested, then actual symbolic evaluation returned zero for frozen panel mass, emitted mass, emitted first moment, uniform W1 formula difference and affine distance scaling. It returned the explicit second-moment defect d^3(f^2-f+1/6). The first regular-limit request emitted infinity warnings as well as the correct limiting values; those raw results remain in wolfram/PANEL_IDENTITIES_RESPONSE.json. The independent clean series request emitted no messages and gave the constant-opacity mass limit d, conditional mean series 1/2-u/12+u^3/720, and zero GL2 second-moment defect.

The Decimal90 panel study reads 2,806 actual prior BR04 Rust nodes: 30 AP rules, six optical depths {0,1e-8,1,93,1e3,1e12}, five refinements {1,2,4,8,16}, and 1,403 panels. It is a new mathematical/composition analysis, not a new native dynamics run. Its quantile-integral reference is independent of the Rust positive CDF-plateau evaluation.

All declared checks passed. The largest whole-rule relative frozen survivor mass defect was 1.0203094249563813e-16. The largest exact-versus-discrete normalized panel-mass TV was 3.9902750860308611e-17. The explicit unequal-mass and clock examples verify why a width alone does not control a measure with different panel masses, and why a small atom shift bounds W1 without bounding atomic CDFsup.

For tau=93, r=1 and r=8 respectively, normalized frozen W1 is 0.002009860422647117 and 0.0003247366933659375. The corresponding mass-weighted panel-width bounds are 0.01581831777406993 and 0.002537363312353628. These values concern one normalized constant-opacity step. To obtain seconds, multiply by its dt.

Real-arithmetic panel mass exactness must not be confused with uniform relative binary64 accuracy on every extremely old panel. At tau=1e12 the largest local relative defect among all panels is 5.53926051512504e-5; these very old panels carry negligible reference mass. Restricting the report to panels whose normalized reference mass exceeds the explicitly chosen 1e-20 threshold gives maximum local relative defect 3.07972942350344e-15 across the study. All panels remain in the data; the threshold only labels the secondary summary.

The actual implementation sample at Nt=1, T=1e9 s, r=1 was checked separately. Its 48 unique rules, 48 panels, 384 templates and 768 actual newborn/final cohorts passed all 576 local certificate field comparisons, exact replay arithmetic checks, panel composition bounds and actual-clock support checks. The largest local normalized W1 difference from Decimal90 was 1.01798829407316e-14. The final count-weighted panel width is 1e9 s, as expected for this one-panel-per-label sample. This sample is a source-native code observation, but is neither the BR05 long native run nor a longspan convergence result.

The completed SIGNED_MINUS native Nt=16, T=8e12 s, r=8 monitor was then checked as a separate input. Its execution receipt reports COMPLETED, exit 0 and 16/16 output rows. The read-only Decimal analysis took 68.0 s and verified 768 step-rules, 19,664 panels, 39,328 unique rule nodes, 314,624 actual birth/final cohort rows and 235,968 local certificate field comparisons. The 6,144 template records are 16 birth batches of the original 384 source labels.

All local comparisons and mass-TV composition bounds passed. Maximum normalized local W1 and CDFsup differences from Decimal90 were 1.31151008464164e-15 and 2.05791689797461e-16. A separate 0.26 s replay verified every original panel's left/right/weight-width bits and node-pair cardinality: 58,992 boundary-field comparisons. This extra replay is distinct from the independent quantile calculation; no dynamics were rerun.

The independently summed final photon count is 1.0038697310449620e-8 reference-comoving m^-3. All 314,624 original retained cohort records remain present: 292,972 have positive represented counts and 21,652 have zero represented counts. No initial cohort lacks a birth-panel ID in this run. Actual final clocks all lie in their recorded panels, with maximum final age-subtraction roundoff 4.8828125e-4 s.

The final actual retained-count-weighted nominal birth-panel width is 3.5656037103422471e9 s; the corresponding represented-width statistic is 3.5656037103422448e9 s. They differ by about 2.25e-6 s from floating representation. These are resolution indicators. They bound only a comparator with the specified same panel masses and support, not the unknown nonlinear gas/radiation solution.

The full input hashes, field errors and actual counts are in native_full/NATIVE_PANEL_VERIFICATION.json. Exact panel replay is in native_full/NATIVE_PANEL_REPLAY_VERIFICATION.json. The small sample and full history are distinct observations and must not be counted twice as full native runs.

## Reproduction

The panel study is self contained. Run with explicit read-only input and a fresh output directory:

    python3 verify_panel_math.py \
      --nodes inputs/BR04_PANEL_RULE_ACTUAL_NODES.csv \
      --out-dir /absolute/new/output/panel_math

For actual monitor outputs, keep verify_native_panels.py beside verify_panel_math.py and run:

    python3 verify_native_panels.py \
      --monitor-dir /absolute/path/to/monitor \
      --out-dir /absolute/new/output/native_panels

The native checker reads MONITOR_RULES, MONITOR_PANELS, MONITOR_BIRTHS, MONITOR_STEPS and MONITOR_FINAL_COHORTS CSV files. It verifies local references and panel/clock/count structure; the root's separate audit owns Verner/MD14/source/Killing-ray reconstruction. It does not execute Rust/native dynamics. Inputs are hashed before and after the read-only analysis.

The fast exact-recurrence gate is reproduced separately with the same monitor input:

    python3 verify_panel_replay.py \
      --monitor-dir /absolute/path/to/monitor \
      --out-dir /absolute/new/output/native_panels

This script also imports its unchanged sibling verify_panel_math.py.

The first successful native sample receipt is native_sample/NATIVE_PANEL_VERIFICATION.json. After explicitly adding the Decimal optical-depth-domain check and the one-subnormal absolute mass tolerance, the same sample was verified with the finalized checker in native_sample_final_checker/NATIVE_PANEL_VERIFICATION.json. Both computations passed; neither is an added physical history. Finalized-checker output is the reproducible evidence for its present script identity.

All reference computations are finite-precision numerical verification of exact mathematical formulas, not interval arithmetic. The Decimal tail cutoff exp(-1800) has a declared conservative normalized omitted-mass bound below 1e-768 for the studied tau <= 1e12 domain.

## Primary-source identity

PRIMARY_SOURCE_RECEIPTS.json preserves actual SciSpace/Exa queries, web URLs and access/version status without bundling external full papers. The selected mathematical references are De Angelis and Gray, arXiv:2111.03570v1, and Hamm and Khurana, arXiv:2310.09149v2. The latter is explicitly version pinned because the search result, default PDF and latest abstract initially referred to different revisions.

Mackey 2012 supplies the bounded photoionization-conservation/accuracy context; Fleury, Pitrou and Uzan supplies the Bianchi-I propagation context. Neither establishes this code's native convergence. Verner et al. 1996 Table 1 supplies only the three H/He fit rows copied as numerical data into VERNER_1996_H_HE_PARAMETERS.csv. The DI gate and H-equality model remain project-owned inputs.

## Bounded conclusion

A source-labelled native panel monitor is constructive and verifiable while leaving physical owners and retained cohorts intact. The verified frozen references and actual retained widths are useful read-only diagnostics. Without an additional bound for varying source, path-dependent opacity and the coupled gas response, they do not admit a longspan absolute solution or a universal second-order claim.

