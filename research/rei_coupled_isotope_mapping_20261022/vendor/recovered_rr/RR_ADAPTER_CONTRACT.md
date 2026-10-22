# Frozen RR kinetic-energy moment adapter

Date 2026-10-22. New additive provider only. Preserve the historical preliminary atomic PASS, all original code/data/results, and 18-family/34-direction conditional nuclear model. No IVP, old checks, NCP run, budget reset, Git, or external writes. Local reconstructed directory has no `.git`; parent owns remote provenance (reported HEAD 5a1e5220b301a1c497f2863d6fd823e605faba80).

## Data and scope

Read `../../rei_isotope_quotient_pilot_20261022/pilot/data/verner_ferland_rr_table1_original.dat` relative to this providers directory's parent-parent as resolved explicitly from repository root. Actual root-relative file is `research/rei_isotope_quotient_pilot_20261022/pilot/data/verner_ferland_rr_table1_original.dat`; SHA256 `2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091`. Select exactly H I, HeI a, HeII, LiI, LiII, LiIII. The source label names the recombined product; input charges are 1,1,2,1,2,3 and output charges one smaller. Reuse elemental rates for H1/D/T, He3/He4, Li6/Li7 under explicit ElementalElectronicEquality; isotope-specific spectroscopy remains unresolved.

Create code and tests only in `providers/code/`, with test outputs there. Copy the selected six numeric input rows to `providers/code/rr_rows.json` including original source hash and URL. No imports of old runner/ODE modules; do not mutate historical inputs. Provider runtime accepts `T_K` in finite inclusive [100,10000] K, six fixed channel keys, optional nonnegative finite `chi_J` for a separate completed-cascade ledger. Raise on unknown channel, nonfinite inputs, out-of-domain T, or negative moment; never clip. This is a conditional derivative-of-fit provider, with no claimed empirical moment error bound.

## Derived formula

For T-independent nonnegative capture cross section and Maxwellian electrons,

`alpha(T)=C T^(-3/2) integral_0^infinity E sigma(E) exp[-E/(k_B T)] dE`.

Differentiating under the integral when the moment exists gives the exact identity

`lambda(T) = <E sigma v> = k_B T alpha(T) [3/2 + d ln alpha/d ln T]`.

For existing Verner–Ferland fit `alpha=a/[x(1+x)^(1-b)(1+y)^(1+b)]`, `x=sqrt(T/T0)`, `y=sqrt(T/T1)`, compute analytically

`slope=-1/2-(1-b)x/[2(1+x)]-(1+b)y/[2(1+y)]`;
`factor=3/2+slope`;
`alpha_m3_s=1e-6 alpha_cm3_s`;
`lambda_J_m3_s=k_B T alpha_m3_s factor`.

Output all four values with explicit unit keys and `status=CONDITIONAL_DERIVATIVE_OF_FIT`. The kinetic electron loss is `-ne ni lambda`; ionization-potential reservoir loses `-ne ni chi alpha`; completed cascade radiation gains `ne ni (lambda+chi alpha)`. Do not classify total cascade energy as free-bound continuum, infer spectral bands, or include emitted photons a second time. The helper may report coefficient ledger `(thermal=-lambda, binding=-chi alpha, completed_cascade=lambda+chi alpha)` in J m3/s. Temperature particle-number term belongs to caller, not lambda.

Primary physical definition: Mao, Kaastra & Badnell, A&A 599 A10 (2017), DOI 10.1051/0004-6361/201629708, https://arxiv.org/pdf/1612.01017, equations (1)–(6). Their explicit energy-loss coefficients do not equal our derivative approximation; no claim of downloading their tabulated moments. Alpha source: Verner & Ferland 1996, DOI 10.1086/192284, https://www.pa.uky.edu/~verner/rec.html. The exact identity is directly derived here. Differentiating a fitted alpha need not preserve its quoted relative accuracy: if alpha_fit=alpha_true(1+delta), the factor error is d ln(1+delta)/d ln T. Keep this uncertainty separate from algorithm error.

## Bounded implementation and tests

One lower-tier worker implements pure Python (NumPy/SciPy available), no service calls. Aggregate test CPU <30 s, wall <60 s; zero IVPs. Record command, wall/process CPU, environment versions, observed failures and C1–C10 outcomes in `code/IMPLEMENTATION_RECORD.json`. Stop for ambiguous physical convention, source mismatch, tolerance failure requiring model change, or budget boundary; return to provider framing agent.

1. Verify source hash and six source-row values and charge mapping.
2. At 100, 1000, 10000 K for all rows compare analytic slope to a symmetric finite difference in ln(T) of the mathematical fit at T*exp(±1e-5). Relative/mixed absolute slope error <=2e-9; finite-difference probe can evaluate fit beyond public boundary only inside test reference.
3. Positivity/finiteness on 257 log T points in [100,10000], six rows; report min/max factors, not clipped values. Unknown channels and invalid T must raise.
4. Independently validate Maxwellian moment identity for manufactured sigma(E)=E^p, p in {-0.5,0,1}, dimensionless k_B=1, T in {0.5,2,10}. Direct SciPy quadrature of alpha integral E^(p+1) exp(-E/T) and moment E^(p+2) exp(-E/T), with independent gamma-function closed forms alpha~T^(p+1/2), lambda/alpha=(p+2)T. Relative error <=2e-10. This checks the identity, not atomic cross sections.
5. Coefficient energy cancellation across six rows and T points with positive synthetic chi, mixed scaled residual <=5e-15. Unit conversion 1 cm3/s=1e-6 m3/s must be asserted independently.

PASS -> return raw receipt and code for fresh independent scientific review. This unit supplies usable scalar RR kinetics/energy interface and no evolved thermal trajectory, band emission, or observational admission.
