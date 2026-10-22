# Independent provider review

Decision: **PASS_SCOPED_SCALAR_PROVIDERS**, 2026-10-22. Reviewer `/root/thermal_contract` had no role in the provider contract or implementation. Requested review role: Astra authority; runtime model identity was not separately attested. Review was read-only except these review artifacts. No implementation repair or numerical rerun was needed.

Accepted scope is the restored six-channel RR scalar rate and conditional derivative-of-fit kinetic moment, plus numerical evaluation of three selected ground-target DR fits over inclusive 100–10000 K. This permits retaining and using the additive research interfaces under their explicit statuses. Coupled trajectories, production defaults and full atomic/nuclear admission are unchanged.

## Evidence actually reviewed

Read PROVIDER_IMPLEMENTATION_CONTRACT.md, RR_ADAPTER_CONTRACT.md, both adapters, both test modules, both row files, run_current_tests.py, historical IMPLEMENTATION_RECORD.json, current receipt and stdout/stderr. Direct local SHA checks matched RR adapter fddb3b3d…99718, rows66e2f497…21fba, historical receipt007dd975…da69b, original RR source2382f689…f5091 and raw DR sourcea43736b3…186e9. These are immutable-source and exact unchanged historical-evidence bindings. The old RR execution is reused, not represented as a new run. The current source test binds the actual restored source path and all six numeric rows.

Primary sources opened independently on 2026-10-22: [Badnell definition and table description](https://amdpp.phys.strath.ac.uk/tamoc/DR/), [Badnell Kelvin coefficient table](https://amdpp.phys.strath.ac.uk/tamoc/DR/clist_K), [Verner RR description](https://www.pa.uky.edu/~verner/rec.html), and [Verner Table 1](https://www.pa.uky.edu/~verner/dima/rec//table1.dat). The saved Verner schema was read locally. Primary table rows agree with selected local entries, including negative DR coefficients and both C/E blocks with matching Z,N,M,W. Current primary DR header is20230512; no replacement rate archive or physical accuracy study is inferred.

## Scientific and numerical findings

RR source labels denote recombined products, giving input/output charges (1,0),(1,0),(2,1),(1,0),(2,1),(3,2). The implemented analytic logarithmic slope follows by differentiating the three fit denominator factors. Multiplication by k_B T alpha(3/2+slope) gives the conditional kinetic moment; its SI conversion is correct. The Maxwellian identity requires a temperature-independent capture cross section/fixed target weighting and a differentiable convergent moment. Differentiation of a rate fit preserves no empirical derivative-error guarantee. The status and contract retain that uncertainty. Its coefficient ledger assigns kinetic, stored-ionization and complete-cascade energy once, leaving particle-count temperature work to the caller.

Historical1542 positivity and1542 ledger cases,18 slopes and9 manufactured quadratures remain applicable because the RR implementation/rows/receipt are byte-identical. Their reported extrema and residuals satisfy their original tolerances. Current execution rechecks immutable source binding and12 boundary/charge cases. The chosen interval lies inside the declared Verner domains, including the narrower HeI a interval.

DR N counts incident-target electrons and M=1 selects ground targets. The code maps q=Z-N to q-1, with He3/He4 and Li6/Li7 under explicit ElementalElectronicEquality. H and fully stripped unsupported requests raise. This isotope approximation does not claim isotope-resolved spectroscopy or nuclear daughter injection.

For DR, factoring exp(-E*/T) gives exactly the implemented log expression; fsum retains signed coefficients. Independent positive lower bounds on shifted sums are0.00139515 (He q1),0.0000286347 (Li q1) and0.0001451 (Li q2). Thus positivity is justified throughout the interval, beyond sampled checks. This specific signed sum has no near-zero cancellation requiring an additional numerical scheme. SI logs add ln(1e-6) once. Floating underflow is returned with finite log rate and FLOAT_UNDERFLOW, distinguishable from an unavailable channel. No clipping or absent-rate zero filling occurs.

The independent Decimal reference uses the original unshifted signed formula,90-digit arithmetic and enlarged exponent range rather than reusing the production transformation. Current receipt records27 comparisons: maximum absolute log error1.8189894035458565e-12 and normal relative error5.3753063766749275e-14, both below2e-11. Its771 grid cases compare representability to Decimal conversion, with365 underflows and406 representable cases;13 invalid inputs are rejected. There are14 normal and13 underflow cases in the sparse accuracy set. The grid establishes the requested status checks; a universal optimal-rounding guarantee at every exact underflow transition is not claimed.

The current runner exited0, stderr is empty, wall2.204961515s and process CPU3.862304441s. A pretest cwd/path mistake consumed reported wall0.268279498s and was repaired without changing physics; its CPU was not separately measured and remains recorded as unknown. This is not a numerical failure or reason to repeat successful tests. No IVPs,83 reruns or NCP runs occurred.

## Boundaries and next action

The primary DR grid covers the selected temperatures for residual charges1 and2, but grid coverage and accurate fit evaluation do not establish physical fit accuracy at low temperature. That accuracy/source-archive comparison remains open. DR thermal moments, cascade spectra and closed DR energy allocation remain absent. CI remains unsupported across the pilot interval; CX remains unavailable. No inferred CI/CX zeros or extrapolations were introduced. Existing photo support, Li K-shell exclusion below60eV and conditional nuclear scope remain unchanged.

There are no blocking findings and no authorized code repairs. PASS leads to integration of these scalar research artifacts and preservation of their receipts. Any subsequent coupled calculation requires its own supplied energy/spectral providers and existing claim-admission rules; this review creates no new run allowance.
