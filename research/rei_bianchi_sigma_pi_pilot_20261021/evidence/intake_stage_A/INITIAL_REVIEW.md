# Initial independent review — PASS

Reviewer: `/root/pilot_independent_review`, nonimplementing. Requested Astra role; developer context identifies GPT-6 Astra Pro, with no additional runtime-model telemetry. Reviewed the frozen contract, local AGENTS policy, actual original canonical FV / species / angular source, cosmology lock, and source verification receipt. Independently recomputed the canonical source SHA256; it matches `91c1641b…344cc5`.

**PASS permits intake/contract publication and bounded exploratory execution.** It does not admit production results. The one local wording correction below has a fixed interpretation and does not require another process cycle before execution.

## One bounded clarification — resolved

Validation item 4 uses `v` in the directional energy identity, but the solver defines `v=s/Href`. Use `w=db/dx=Href*v/H`, and test

`[rho(x+h,b+w*h)-rho(x-h,b-w*h)]/(2h) = -3(rho+pbar)-6*w*pi_s`.

For prescribed arbitrary directions, call the direction `w`. Source physics and the reduced RHS are already correct. The controller corrected the contract to use `w`; the reviewer verified the updated text and changed no contract or solver.

## Independent physics findings

The half-contraction norm gives `|sigma|=sqrt(3)|s|` and `|pi|=sqrt(3)|p|`. With energy density in J/m³ and proper seconds, `K=8*pi*G/c²` and `K*rhocrit=3H0²`. Consequently signed dimensionless Pi is `3*sqrt(3)*H0²*p_norm/H²`. The specified pressure difference divided by three and the physical-axis coefficient are consistent.

Let `C=3H²-K*rho-Lambda*c²-3s²`. Substitution of the stated H, energy and shear equations gives `dC/dt=0`: the energy-work term `-6*s*p` cancels the shear work. The massive canonical weights remain fixed; differentiating their redshifted mass-shell energy yields exactly the directional identity above. Radiation gives `E0'=-2*(s/H)*E2`, the corresponding energy-work law.

Identical collisionless gamma/nu vectors remain equal. Reflection parity preserves the even energy block. Number moments do not feed energy or gravity, and the thermal variable remains zero. These properties justify eight states at L8: three metric/clock states plus five even energy moments. The original numerical matrix has roundoff-sized odd/even leakage, so comparison is numerical rather than bitwise.

For the specified quadrature the initial massive energy is `0.9999999999999999`, with pressure difference approximately `-8.67e-19`; this is negligible but the required actual-field axis check correctly handles it. The maximum ideal required `|k|=0.4736657615275149`, below `0.5`. The positive canonical minimum cell population is `1.491026203638869e-30`.

Three source-only directional finite-difference checks at interior x, using h=1e-5, have relative residuals `1.46e-10` to `1.54e-10`, comfortably below `1e-7`. The source energy-monopole matrix residual is `7.60e-14`, number-monopole row `5.49e-14`, and odd/even leakage `4.44e-16`. Full parameters are in INITIAL_REVIEW.json.

## Validation and claim ceiling

The frozen six reference comparisons, axis checks, two L8/L12 corners, tightened-tolerance corner and isotropic control are sufficient gates for this preliminary bounded slice. An algebraically imposed Hamiltonian residual is a consistency diagnostic; the reference, closure and tolerance comparisons supply the additional accuracy evidence. Sampled angular brightness and fixed Gauss3 quadrature do not establish global positivity or complete phase-space convergence. The historical background lock uses `Sigma=s/H` in its own metadata; the pilot explicitly uses the source canonical half-contraction convention and must keep physical plot columns consistent with that convention.

No detailed benchmark is required. No future general-Bianchi or H/He physics completion blocks this authorized pilot. Final scoped review must inspect the actual implementation and raw validation/sweep outputs. No reduced solver or target sweep has yet been reviewed here, and no production, NCP or speedup claim is granted.

Additional derived identity for final read-only validation: since `b'=s/H` and `E'=(s/H)*M_even*E` with constant source matrix, `E(x)=exp(b(x)*M_even)*E(0)` for b(0)=0. This identity holds even through shear turning points and is a verification relation, not a new solver implementation.
