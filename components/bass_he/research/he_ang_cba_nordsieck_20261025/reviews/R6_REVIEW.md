# Independent R6 review — HE-ANG-CBA-NORDSIECK

## Decision and method

**R6: PASS.** Equations (1)–(9) and the clarified implementation contract are consistent for the stated fixed-centre, scalar, labelled direct model. Finding R6-01 is closed by the root's explicit residual-metric clarification, reread before release. This review does not admit a physical provider or a full-event distribution.

Reviewer: separate agent `/root/cba_independent_review`; requested model `gpt-6-astra`; observed runtime model identity `NOT_OBSERVABLE`. The reviewer did not author the theory or implementation. Applied `physmath-research-loop`, builtin 1.0.0, R6, with its research-policy and evidence/handoff rules. Method: independent algebra, independent box-state normalization accounting, limiting cases, direct source-text inspection, and visual inspection of the actual source page4/page7 PNGs. No science code, numerical suite, Wolfram call, or remote mutation was executed. Only review artifacts were written.

Read dependencies: `THEORY_KO.md`; `FROZEN_CONTRACT.json`; source intake `heang_next4_source_20261025/SOURCE_REPORT.md`; private `attaourti2004v2.txt` and actual page4/page7 images; HE and central AGENTS snapshots in `heang_next4_survey_20261025`. Source identity is the intake's arXiv:physics/0411013v2, SHA256 `b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1`. No published-version equivalence is inferred. The local BASS_HE directory is a snapshot without a usable `.git` directory; no local HEAD verification is claimed.

## Independent mathematical checks

1. **Parabolic reduction and branch, Eq. (1): PASS.** The Jacobian is `d^3r=(xi+zeta)d xi d zeta d phi/4`, so division by `r=(xi+zeta)/2` gives the stated factor one half. Azimuth integration gives `2*pi*J0`, hence the remaining prefactor pi. With `a=(lambda-i*qz)/2`, `b=(lambda+i*qz)/2`, `d=qperp^2/4`, one obtains `s=a+d/b=A/[2*(lambda+i*qz)]` and `b*s=A/4`. Explicitly `Re(s)=A*lambda/[2*(lambda^2+qz^2)]>0`; subtraction of `i*p` preserves this positive real part. The Laplace transform yields `I=4*pi/A*exp[-i*eta*Log(Bc/A)]`. Since `A>0` and `Im(Bc)=-2*lambda*p<0`, this equals the author's separate logarithms on the entire stated real-input domain. There is no crossing of the negative-real-axis branch cut. The sign of the modulus is correctly `|C|^2=exp(2*eta*Arg(Bc))`.

2. **Fixed-eta derivative, Eqs. (2)–(4): PASS.** Differentiating `log(I)=log(4*pi)+(-1+i*eta)*log(A)-i*eta*Log(Bc)` at fixed `eta,pvec,qvec` gives `-I'/I=2*(1-i*eta)*lambda/A+2*i*eta*(lambda-i*p)/Bc`. Exponential damping at positive lambda dominates the positive-imaginary-ray hypergeometric growth and the extra radial factor, justifying differentiation locally in lambda. At `q=-p`, `Bc=(lambda-i*p)^2` reduces the bracket to `(lambda-eta*p)/A0`, proving (3). At eta zero, direct Fourier-Yukawa and exponential transforms give (4). Substituting `eta=lambda/p` only after differentiation is essential and is specified correctly.

3. **Matched polynomial, Eq. (5): PASS.** The numerator of Eq. (2) over its common denominator is `lambda*(1-i*eta)*Bc+i*eta*(lambda-i*p)*A`. Its coefficient of A is `lambda+eta*p`. With `eta*p=lambda` and `q=Delta-p`, the constant term vanishes and the remaining result is exactly `2*lambda*[Delta^2-(1+i*eta)*Delta.p]`. Multiplication by `2*I/(A*Bc)` gives the stated coefficient `16*pi*lambda`. This avoids subtracting the two nonzero terms that cancel at zero transfer. For `Delta=t*n`, the leading coefficient is proportional to `-(1+i*eta)*n.p`; when `n.p=0`, the exact numerator is t squared. Thus the stated directional orders and exact analytic zero follow. A separate exact-zero implementation branch is appropriate.

4. **Original-integral quadrature, Eq. (6): PASS.** Multiplication of the I measure by `(xi+zeta)/2` and the derivative identity `-partial_b[b^-1*exp(-d*xi/b)]=exp(-d*xi/b)*(b^-2-d*xi*b^-3)` yield the stated prefactor and polynomial. This quadrature integrates the original K integrand after an exact one-coordinate reduction; it is independent of numerical differentiation of the closed form. Its comparison checks the hypergeometric integral numerically, while sharing the explicit coordinate convention.

5. **Normalized form factor and Sommerfeld factor, Eqs. (7)–(8): PASS.** The source bra has `Gamma(1-i*eta)`, `exp(-i*p.r)` and `M(i*eta;1;i*(p*r+p.r))`. The delta-normalized scalar convention supplies `(2*pi)^(-3/2)`. The bound factor is `(lambda^3/pi)^(1/2)` without an additional inverse radius. The transfer operator is `exp(i*Delta.r)-1`, giving precisely the difference of K values. Gamma conjugation and `|Gamma(1+i*eta)|^2=pi*eta/sinh(pi*eta)` give the positive factor in (8), including its continuous eta-zero limit. The matched subtraction vanishes by (3); retaining it in the eta-zero control is necessary.

6. **Absolute direct TDCS, Eq. (9): PASS.** Let `G=(lambda^3/pi)^(1/2)*exp(pi*eta/2)*Gamma(1-i*eta)*K_difference`, so `G=(2*pi)^(3/2)*F_D`. From `T_box=V^(-3/2)*(4*pi/Delta^2)*G`, golden rule, two final-state densities, and projectile flux give `2*pi*(16*pi^2)/(2*pi)^6*|G|^2/(p_i*Delta^4)=4*|F_D|^2/(p_i*Delta^4)` before the final radial phase-space factors. These factors are `p_f*p`, with a unit energy-delta Jacobian. This reproduces (9). Independently, `(2*pi)^4*|(4*pi)/(2*pi)^3|^2=4`, proving the delta-T conversion. The direct spin matrix has two conserved spin labels: its four allowed final/initial combinations cancel the initial average one quarter. No symmetry factor or exchange term is implied for this labelled direct quantity. The specified physical units `a0^2/E_h`, momentum-state conversion `p0^(-3/2)`, and division by the nominal eV/Hartree factor for per-eV TDCS are consistent.

## Source correspondence and scope

The private source's Eqs. (5)–(7) and (16) have the exponential bound state without an extra inverse radius, while Eq. (18) visibly has that factor. Eq. (19) and Appendix Eq. (A9) agree with I, not K. The private page7 image confirms the A1 exponent and A7 minus-Q assignment do not identify the same q as written. The root independently derives its q convention rather than adopting those incompatible intermediate signs. The source's Eq. (28)/A10 J uses different hypergeometric parameters and is correctly kept distinct. Reference [16] in the source text is Massey–Mohr (1933). No equation-level Nordsieck-1954 authority is needed for the adopted endpoint identity. These source discrepancies are recorded with the right scope.

The continuum normalization and scalar flux derivation are explicitly the root's nonrelativistic construction, rather than an unsupported direct copy of the source's spinor Eq. (27). Source Eq. (26)'s averages and the neglected exchange channel are consistent with the stated direct spin accounting. The 250/5 eV, 3-degree geometry is an illustration; it does not calibrate the 20/54.4/413.6 eV provider domain.

The positive-lambda, positive-p, finite-real-vector kernel domain keeps A and Bc nonzero. Strict positive outgoing energies exclude threshold endpoints; positive energy transfer makes physical Delta zero inaccessible. Small-transfer tests are appropriately mathematical conditioning fixtures. The four moderate quadrature fixtures and 50/80-digit comparisons support finite numerical checks only. The tolerances are acceptance targets awaiting execution, not pre-established achieved accuracy. No new strong no-go, novelty claim, finite-mass coupling, full-event count law, or domain-wide accuracy theorem is asserted.

## Closed finding R6-01 — exact comparison metric

**Target:** `FROZEN_CONTRACT.json` acceptance keys `binary64_scaled_complex` and `*_relative_or_abs_scaled`.

**Observed issue:** numerical tolerance values are fixed, but the exact denominator in the scaled residual is not written. In particular, `max(1,abs(reference))` and a pure relative comparison differ materially for near-zero overlaps.

**Impact:** this does not affect Eqs. (1)–(9), but the lower-tier agent should not choose a scientific acceptance metric implicitly.

**Minimal correction and closure:** root added `scaled_metric = abs(value-reference)/max(1,abs(reference))`, with complex absolute value the modulus, and `tiny_transfer_metric = abs(value-reference)/abs(reference)` for nonzero mp80 reference, with exactly zero reference subject to the exact-zero contract. The reviewer reread the actual acceptance line and verified these additions. All numerical tolerances are unchanged. This closes R6-01 before implementation execution; no additional suite is requested.

## Stopping rule and next action

The algebra/source/normalization review and its single narrow finding are closed. Proceed with the already contracted implementation and bounded runs. C9 will inspect the changed code, raw outputs and actual figures; it need not repeat unchanged source or algebra checks. Overall HE-ANG remains `SOURCE_INPUT_PENDING` with `physical_provider_admitted=false`.
