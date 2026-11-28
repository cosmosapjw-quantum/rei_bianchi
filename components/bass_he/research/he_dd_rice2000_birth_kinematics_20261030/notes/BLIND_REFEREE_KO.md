# Same-author adversarial referee for PR126 Rice kinematic atlas

1. Does source actually fix monoenergetic E? NO. The source has two finite photon bins and 6 effective CM angles each. Output is endpoint support at *fixed effective angle*, not 12 direct measured deuteron energies. Labels were checked.
2. Are the 12 cross sections an independent new experimental campaign? NO. One Rice 2000 campaign, 12 direct DA rows, 8 Table II fits and 6 thesis rows not added.
3. Is an angular integral of six samples a measured 4π event cross section? NO. No integration or 2! reuse on Table I row, parent event normalization retained.
4. Are energy-weighted DA bounds unconditional observables? NO. They require same nonnegative experimental weight, fixed effective angle and acceptance; otherwise are conditional inferences. No source thermal history attributed.
5. Is a 1-sigma marginal stat interval a correlated joint confidence interval? NO. 12×12 covariance absent, 7.1/13% systematic separately recorded.
6. Are Ksum, high-low and variance derivations physically conservative? Verified exact two-body four-momentum and mass shell tests; analytic endpoint-monotonic certificate and 21-point per-row interior test. Wolfram representative 220 MeV, CM 63.6°: K+=(113.08029523781035) MeV, K-=(83.07322656218965) MeV, variance 225.10604262585437 MeV².
7. Can PR119 Fermi-LAT IGRB/EGB source be substituted as target He proper photon history? NO, it is a different location/epoch and extrapolations; keep R_event null.
8. Can NIST PSTAR supply D-fast stopping as first-party deuteron data? NO, PSTAR is for protons and ASTAR for helium ions, not deuterons. Do not substitute.
9. Parent Table II low unconstrained P2 8.32 nb vs 2π1.31=8.23097 nb discrepancy remains OPEN in parent, but this atlas depends only on exact Table I blob.
10. Same-author referee only: native distinct-author R06 and C09 NOT_RUN. GitHub CI and cloud readback must be reported from actual receipts, not inferred here.

Finding: no new physics gate violation found within specified conditional scope. Main missing ingredients remain real He alpha-frame MeV photon distribution, target state and D-fast energy deposition. No production promotion.
