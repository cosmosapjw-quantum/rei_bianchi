# Frozen-characteristic positive tail

Executed source: see ORACLE_RESULT.json and EXECUTION_RECEIPT.json. This is an additive research kernel, not a production or coupled-history replacement. No panel shape is inferred from tail count/energy logs.

For s=ln(a), h=Delta s, E(s)=E0 exp(-s), fixed lambda_i>=0, lambda=sum_i lambda_i, fixed source q>=0 and initial f>=0,

    N(h) = f exp(-lambda h) + q J(lambda,h),
    J(k,h) = integral_0^h exp(-k s) ds.

The integrated count and energy along this same characteristic are

    C = f J(lambda,h) + q [h-J(lambda,h)]/lambda,
    K = epsilon_eV E0 { f J(lambda+1,h)
                       + q [J(1,h)-J(lambda+1,h)]/lambda }.

The zero-lambda source limits are q h^2/2 and q[1-(1+h)exp(-h)], respectively. The zero-time limit preserves initial N/U and produces no integrated events. Owners are A_i=lambda_i C, B_i=lambda_i K, redshift work=K, Q_N=qh and Q_E=epsilon_eV E0 q J(1,h). N and U=epsilon_eV E0 exp(-h)N are retained. Each contribution is independently nonnegative. Number and energy identities are diagnostics, never used to assign a residual to an owner.

Admission requires initial E in [13.6,50000] eV and endpoint still at/above 13.6; each active species requires endpoint above its own Verner cutoff. The generic API rejects unsplit crossings. Inputs are fixed per segment, source fronts and atomic cutoffs are caller-owned. A characteristic is not a reconstructed panel and no spectrum-shape widening occurs.

Every finite authoritative log represents a positive amplitude, while (-infinity,0) is exact empty. The log is a compensated pair; callers MUST preserve both values returned by log_parts(), and restore using from_log_parts(). log_value() is a rounded display/readout. In particular an optical depth of one million exposes the insufficiency of a single f64 log even when the linear readout is zero. The retained first failure had 2.08e-11 relative error against exact input arithmetic, above the unchanged 3e-12 gate. FMA product remainders and compensated log addition repair this representation; the final comparison uses Decimal(hi)+Decimal(lo).

LogPositive::add and TailOwners::add report a positive omitted-addend bound when the stored compensated sum equals its larger addend. This bound is restricted to the wholly omitted addend. It is not a total arithmetic error certificate. Readout zero carries the represented positive amplitude as its zero-readout bound. Nonzero subnormal conversion has a deliberately loose bound of 16*f64::MIN_POSITIVE on the admitted log branch; this bounds conversion of the represented log, not prior numerical error. Loss owners remain separate and are never put into physical owners to make a budget close.

The actual source/initial contributions are combined only after independent analytic integration. The source energy divided difference is evaluated with a small optical-depth series of positive incomplete moments, or a well-separated analytic phi difference. No backward-Euler attenuation is used. export() moves existing N/U into exported N/E before setting inventory to exact empty; callers must first terminate at the true physical cutoff. It does not move an endpoint or supply an event location.

Validation: 10 native tests and 86 Decimal800 fixtures, 1118 owner checks. 586 exact-zero owners remain exact empty; 249 strictly positive owners have zero binary64 readouts while their logs remain finite. All positive owners use abs(exp(candidate_log-reference_log)-1)<=3e-12, with no absolute tail floor; maximum observed error 5.109726091704207e-14. The unchanged threshold is in the parent CONTRACT.json. This finite matrix does not prove arbitrary-log uniform accuracy, global IVP stability or continuous quadrature accuracy.

Two failures are preserved separately: the scalar-log implementation failure and a Decimal100 reference cancellation at h=1e-300. The latter was repaired by using Decimal800 for the full reference context, including the injected-energy primitive; candidate arithmetic and the target were unchanged. Historical source/outputs are under first_failure/ and oracle_cancellation_failure/.

Portable commands (from crate root; compiler available on PATH):

    mkdir -p target
    rustc --edition 2021 --test src/tail.rs -o target/tail_tests
    target/tail_tests
    rustc --edition 2021 scripts/tail_probe.rs -o target/tail_probe
    python scripts/check_tail.py --probe target/tail_probe --output evidence/tail-replay

No third-party Python dependencies are used by the final oracle. Numerical execution was single-threaded; the final portable run used 10.105 CPU seconds, approximately 14.3 MiB peak Python RSS. Two successful oracle runs plus earlier short failures were below the component's 120 CPU-second cap. Compilation is separate. This is not a global all-roundoff or rigorous interval certificate.
