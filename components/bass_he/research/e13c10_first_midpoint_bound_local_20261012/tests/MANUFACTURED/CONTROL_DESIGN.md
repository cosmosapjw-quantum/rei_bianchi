# E13C10 manufactured first-integral controls

Role: control contributor; not the final independent reviewer. Candidate code and admission decisions are owned separately. This is a design and execution contract for short local controls, not a claim that the controls have already run.

## Fixed target and independence

Exercise `first_midpoint.integrate_signed(c, n)` against exact constant-defect and polynomial-forcing models. Candidate arithmetic is the inherited directed Decimal interval module at P60 and the original 17 `local_enclosure.integrands` fields. The reference uses independently derived integrated first-variation equations and a separate P140 directed Decimal evaluator. It does not call the candidate integrator, candidate midpoint weights, Jet2 derivative fields, or numerical quadrature to construct its target.

The already verified E13C9 oracle module is reused only for its separately implemented interval evaluator and elementary closed-form functions. Its pinned SHA-256 is `15806e4758038a788312dfe075f10a364682e3655a0ca35ed0ca602166ea091f`. Its former main/suite is not invoked. Shared dependencies are exact input parameters and the underlying Python Decimal exp implementation. This is independent formula/evaluator validation, not an independent physical coefficient model or a formal proof-assistant result.

## Independent integrated formulas

For constant nonnegative actual rates `lambda_i=lambda_f_i+dl_i`, constant source difference `dq`, frozen rate `L=sum(lambda_f_i)`, and physical redshift `E(u)=e0 exp(-u)`, define the zero-incoming first prefix

`Y' = dq - dL*Pf - L*Y`, `Y(0)=0`, `dL=sum(dl_i)`.

For `L>0`, `Y(u)=a+(b+g*u)exp(-L*u)`, with `a=(dq-dL*qf/L)/L`, `b=-a`, `g=-dL*(f0-qf/L)`. For `L=0`, `Y(u)=(dq-dL*f0)u-dL*qf*u^2/2`. These formulas give the endpoint and moments `I0=int Y`, `IE=int E*Y`. Independently integrate `Pf` to obtain `F0=int Pf` and `FE=int E*Pf`.

Then the 17 first-integral targets are `P1=Y(h)`, `Z=IE`, `QN=dq*h`, `QE=e0*dq*J(1,h)`, `A_i=dl_i*F0+lambda_f_i*I0`, `B_i=dl_i*FE+lambda_f_i*IE`, `H_i=B_i-chi_i*A_i`, their totals, and `P1_energy=E(h)*P1`. This route integrates the differential-system solution and response moments, rather than repeating the original quadrature integrands.

Additional `L=0, dl_i=0` controls use polynomial `dq(u)`. The primitive `Y(u)` is exact rational polynomial arithmetic. Exponentially weighted moments use the independent recurrence `I_n(r,h)=(n*I_(n-1)(r,h)-h^n exp(-r*h))/r`, with `I_0=J` and the exact r=0 limit `h^(n+1)/(n+1)`. Positive and negative quadratic forcing test the sign retained by the Peano term; a centered cubic tests a sign-changing second derivative and cancellation.

## Declared control matrix

Two short resolutions, N8 and N32 at P60, are sufficient to expose cell scaling and curvature-sign mistakes. Each uses 2N manufactured coefficient calls and no captured coefficient calls.

| Case | Concrete risk resolved |
|---|---|
| Exact zero/source off | Zero propagation and exact zero signed outputs. |
| Frozen match with nonzero incoming center/radius | First local integral is independent of carry; analytic gains preserve incoming uncertainty. |
| Positive forcing, L=0 | Explicit zero-rate branch and polynomial first prefix. |
| Positive forcing, L>0 | Attenuation response and varying redshift moments. |
| Positive total opacity defect | Negative first photon correction sign. |
| Negative total opacity defect | Positive first photon correction sign. |
| Opposite nonzero species defects with dL=0 | Photon cancellation while individual species corrections remain nonzero and signed. |
| L=0 with positive opacity defect | Polynomial prefix with nonzero total coupling. |
| Source off with nonzero frozen stock/opacity defect | Source outputs vanish while photon/species corrections remain. |
| Positive quadratic forcing at L=0 | Positive Peano curvature and roundoff-only photon/source integral width. |
| Negative quadratic forcing at L=0 | Negative Peano curvature, no absolute-value replacement. |
| Centered cubic forcing at L=0 | Sign-changing curvature and zero exact photon/source integral. |

For each case and resolution, check all 17 interval containments, number/energy/species heat ledgers, and the expected sign/zero properties. Independently computed gains check the affine first result at incoming error `-eta, 0, +eta` around the declared nonzero center. Because the first response is affine in this scalar error, endpoint containment covers the full incoming uncertainty range. This check does not replace validation of E13C10's new stitched carry or E13C9's Volterra remainder; the captured path runs and independent review cover their integration.

## Evidence and run discipline

The new script writes fresh START, raw control results and a receipt with exact candidate/oracle/contract identities, precision, local work counts, elapsed/CPU time, RSS and actual exit. Preserve the first failure and partial results without automatic retry. Candidate execution is deferred until the root signals that the code/API and contract are locked. The local controls have a 20 CPU-second ceiling; unexpected timeout is retained as a failure. They do not justify a new NCP job, a full-population result or physical/continuum/production/receiver promotion.
