# Independent scientific review: HE34-SCR

Scope: `research/he34_sandbox_certified_relaxation_20261022` in BASS_HE. This review does not concern the concurrent HE34 Lorentz unit. Author files were read only. Review scripts and evidence were written under `/tmp/he34_scope_review/`.

Workflow 1.0.0; approval 0.2. Physics review preceded implementation review. The currently completed stages pass within the stated scope. Two driver findings were corrected before the first saved-background mechanical execution. Review of those execution outputs and the rendered figures remains pending at this checkpoint.

## 1. Physics audit

### Exact moment coordinates and cone

Starting from the two expansion-factored eigenpressures gives the independent linear system

\[
X'=(2S-\chi/3)X+(\chi/3)Y,\qquad
Y'=(2\chi/3)X+(-4S-2\chi/3)Y.
\]

Its nonnegative off-diagonal entries preserve nonnegative eigenpressures. With \(p=(2X+Y)/3\), \(q=(Y-X)/3\), the transformations give exactly

\[
r'=4Sr^2-(\chi+2S)r-2S,\qquad u'=-4Sr.
\]

The boundary flows are \(F(-1/2)=\chi/2\) and \(F(1)=-\chi\). Thus \([-1/2,1]\) is invariant for the exact ratio dynamics. The factor \(e^{-5N}\) and the log-pressure variable remove expansion without introducing a second background evolution. The use of \(N\) requires the stated expanding-branch convention.

### Stable root, nonlinear layer, residual, and contraction

The stated rational stable root solves \(F(b)=0\) and has \(F_r(b)=-D\). Differentiation gives \(b'=(4b^2-2b-2)S'/D\). The polynomial \(4b^2-2b-2\) lies in \([-9/4,0]\) on the cone, verifying the derivative bound and the fact that \(b\) decreases with \(S\).

The closed layer solves \(\delta'=-D_0\delta+4S_a\delta^2\). Substitution gives the residual exactly as

\[
\rho=b'+(D-D_0)\delta+4(S_a-S)\delta^2.
\]

The denominator condition \(c<1\) ensures that the layer is nonsingular and moves monotonically toward zero. The stated bounds for \(D\), \(D'\), \(b'\), and \(t e^{-a t}\) imply the interval residual bound. The secant slope satisfies

\[
4S(r+\widehat r)-\chi-2S\le -\chi+6|S|.
\]

This proves the scalar comparison envelope when both states are in the cone and \(\kappa>0\). Its interval extrema occur at its endpoints. Integrating the envelope against \(4\max|S|\) gives the stated log-pressure bound. The tensor-component inequalities follow from adding and subtracting the same \(p(1-\widehat r)\) or \(p(1+2\widehat r)\) term. None of these bounds needs sampled extrema or an empirical safety multiplier.

The implementation uses a valid refinement of the sufficient cone check in the theory note. If \(S\) increases and \(\delta_0\ge0\), both the root and layer decrease; if \(S\) decreases and \(\delta_0\le0\), both increase. Endpoint bounds therefore suffice in these aligned cases. Otherwise, adding the separately monotone root and layer endpoint ranges encloses their sum. Constant-source flow remains between its initial value and stable root.

### Limits and pressure quadrature

For constant \(S\), the candidate is the exact nonlinear ratio solution, including arbitrary admissible initial anisotropy. The additional pressure term is \(\log[1-c(1-e^{-D_0h})]\), with the sign as written. For \(S=0\), the anisotropy decays exponentially and the expansion-factored pressure is constant. The high-\(\chi\) root tends to \(-2S/\chi\), yielding positive stationary shear work \(8S^2/\chi\) at leading order. A temporarily aligned initial stress can give negative transient shear work; the documentation does not claim otherwise.

Rescaling the layer integral with \(x=D_0\tau\) gives the stated tail bound \(4S_m A e^{-C}/D_0\). This tail is separate from the continuum reduction error and from the numerical quadrature estimate. The model does not establish errors in the saved cosmological trajectory, a physical transient collision spectrum, reactive tensor moments, or a self-consistent thermal/metric closure.

### Neutral H/He transport

Wargnier et al., Appendix C.26, C.29–C.30 and C.35–C.38, supports the stated collision-integral ratios, diffusion/pure-viscosity factors, and heavy-species viscosity system. The author PDF was inspected, including the rendered final page:

<https://jbscoggi.github.io/website/assets/pdf/Wargnier2020_A&A.pdf>

Bruno et al., DOI 10.1063/1.3495980, Eq. 11 and Table I, supports the direct dimensional fit with \(\log T\), the four coefficient rows, and the stated temperature range. The author-uploaded text was checked:

<https://www.researchgate.net/publication/234852143_Transport_Properties_of_High-Temperature_Jupiter-Atmosphere_Components>

The pinned Mutation++ files confirm `setFactor(PI)`, angstrom-squared units, the fit evaluation, and the mass/temperature prefactors. The resulting conversion is \(\overline Q=\pi\,10^{-20}F(T)\) in square metres. Source blobs were verified against the actual local bytes; no source PDF was redistributed.

An independent exact-arithmetic check verifies the cancellation of the common \(xy\) factors and

\[
c_Hc_{He}-c_o^2=(12/5)Au^2(r+1/r+2)>0.
\]

The positive rational expression equals the matrix quadratic form for interior compositions and extends continuously to the two pure-species values. Common scaling of number weights leaves the result unchanged. No composition floor is needed. The dimensions are consistent: \(nD\) has units \(\mathrm{m^{-1}s^{-1}}\), \(u=1/[nD(m_H+m_{He})]\) has inverse-viscosity units, \(\eta\) has units Pa s, \(p/\eta\) has units \(\mathrm{s^{-1}}\), and \(\chi\) is dimensionless.

The documentation correctly presents \(\nu_{\pi,\mathrm{match}}=p/\eta\) as hydrodynamic matching. A first-Sonine viscosity does not identify an exact transient Boltzmann eigenvalue. The common-temperature, near-equilibrium neutral subset remains conditional. Electron/ion transport, reactive source moments, other isotopes, and common-state exchange checks remain outside scope.

## 2. Implementation and plumbing audit

The core implementation matches the reviewed continuum construction. Invalid inputs are rejected explicitly; unavailable or excessive certificates retain distinguishable statuses; there is no clipping, hidden change of tolerance, or fallback to another physical model. Small-argument `expm1` and series branches preserve the limiting formulas. The later `_max_t_exp` multiplier and `_propagate_bounds` exact-zero guard avoid avoidable overflow and `0*inf` without changing the mathematical model.

The mechanical driver evolves the independent linear two-eigenpressure system with knot-segmented Radau integration. Its mapping \(S=\texttt{signed_Sigma}/\sqrt6\) agrees with the pinned HE32 definition in `src/compact_transport.py`. The 201-node signed piecewise-linear source is the declared input. The planned execution counts are consistent: four principal references, one tighter reference, one accuracy check of the coarse baseline, and five timed baseline histories give 11 reference histories and 2200 interval solves.

The neutral diagnostic selects exactly `H1_q0` and `He4_q0`. Its density reconstruction is checked against the saved charge census and baryon normalization. The mass-number convention \(m_H=m_u\), \(m_{He}=4m_u\) is explicit and is not presented as precision atomic masses. The neutral \(p/\eta/H\) values remain separate from the prescribed mechanical \(\chi\).

### Findings and dispositions

| ID | Severity | Evidence | Required fix | Minimal discriminating check | Status |
|---|---|---|---|---|---|
| SCR-R1 | Medium | Initial `run_control.py` used continuum acceptance while omitting a convergence/budget gate for the separately computed pressure quadrature. The solver's continuum-only flag was correctly documented. | Record and require approximation availability, quadrature convergence, and finite quadrature estimate plus omitted tail within a declared numerical budget; preserve the continuum flag's meaning. | A finite but nonconverged quadrature result must be rejected; also reject unavailable, over-budget, and nonfinite results. | Resolved before first saved-background run. Independent five-case readback passes at budget \(10^{-9}\). |
| SCR-R2 | Low | Initial benchmark always executed reduced first, Radau second. | Alternate order and retain actual trial order with raw times. | Inspect five-trial order metadata and both timed branches. | Resolved before first saved-background run. |

The transport timing comparison includes preparation, validation, allocations, and all four diagnostic outputs in each lane. The reported 1.29005 ratio over the batched matrix path is a ratio of medians on this host. Raw timing scatter includes a trial where the matrix path is faster, so it must remain a bounded measurement rather than a universal acceleration claim. No additional timing run is required to support that bounded statement.

## 3. Independent evidence generated by this reviewer

- `INDEPENDENT_CHECKS.json`: 48 exact `Fraction` elimination cases; six 80-digit constant-source eigenpressure matrix-exponential checks; four coefficient-row comparisons with the pinned XML and source blob.
- `IMPLEMENTATION_CHECKS.json`: six actual solver calls compared to an independently formed 80-digit eigenpressure exponential; 16 collision-integral calls compared to the direct 80-digit source formula. Maximum observed ratio and log-pressure discrepancies were approximately \(5.10\times10^{-17}\) and \(2.72\times10^{-16}\); maximum collision-integral relative discrepancy was \(2.99\times10^{-15}\).
- `VARYING_SOURCE_CHECKS.json`: two new sign-changing controls with nonzero initial anisotropy, using independent full-eigenpressure Radau references. At 120 sampled evaluations, the errors were enclosed apart from initial binary64 roundoff of \(2.8\times10^{-17}\). Sampled residual-to-bound ratios did not exceed one. Both cases correctly failed the requested \(10^{-6}\) acceptance criterion where their bounds were too large.
- `CONTROL_GUARD_READBACK.json`: independent valid case plus four failure injections for the revised numerical gate.
- `REVIEWED_SOURCE_HASHES_INITIAL.json`: hashes of the originally reviewed theory, data, implementation, driver, and transport evidence. Later tested hashes are embedded in the corresponding check records and will be consolidated after final output review.

No old HE32 background integration or old HE33 suite was run by this reviewer. Finite reference comparisons and binary64 evaluation corroborate the formal continuum argument; they do not provide outward-rounded arithmetic certification. Physical fit error and truncation of the kinetic transport expansion are not included in the \(10^{-6}\) mechanical reduction certificate.

## 4. Pending final readback

The saved-background mechanical result, its receipt/hash consistency, and rendered diagnostic figures will be reviewed when available. This checkpoint does not assert completion of those pending stages.
