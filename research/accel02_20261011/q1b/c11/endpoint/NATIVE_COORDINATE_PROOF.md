# Native-only coordinate certificate for the PILOT01 failure

Evidence class: source-derived analytic bound plus a new actual-native local test. This is a value certificate and a numerical implementation change, not a provider replacement, endpoint-closure admission, rigorous whole-solver error bound, or history acceptance.

The preserved PILOT01 failed at cell156, first halfstep ending977363400.0610615s, because the arbitrary-kernel coordinate indicator was1.6553590127107777e-7>1e-7. The cell width was approximately8.43916e-8 of its energy. The unchanged guard must reject a potentially rapidly varying arbitrary kernel. Its use in the native positive-absorption **value** map is overconservative when the actual kernel is smooth and its first two moments have already been matched. This new module changes only that indicator's admissibility rule for a separately bounded native case.

## Exact scope and implementation

`native_coordinate_absorption.prepare_incident(...)` delegates to the unmodified C10 operator whenever its original indicator passes, for every non-native provider, and for empty or endpoint cells. Only a strict-interior cell that fails that indicator and uses the exact native provider identity is eligible for the following alternate certificate.

- The entire declared physical support lies within a single smooth active branch or a strictly subthreshold zero branch for each species. Crossing or touching a threshold is rejected before native evaluation.
- The native binary and controlling AtomicProvider/bridge/wrapper source identities match the previously read pins.
- The old positive64/128 measures, positive moment fit, mean fit1e-12, native evaluation, component comparisons, direct and ABI photoheat, positive attenuation, counters, and pairing implementation are reused without edits.
- Exact rational arithmetic on the actual binary64 inputs establishes node energy sides, physical cap, total mass, and mean defects. Neither a node, time, state, support endpoint, nor mean is shifted.
- The analytical coordinate bound is reserved **inside** the original1e-7 response tolerance. Both incident and attenuated checks use `1e-7 - certificate`, which is more restrictive than the original comparison alone. `absorb` is the exact frozen C10 function and receives that smaller tolerance through its prepared state.

The certificate applies for all finite nonnegative absorber densities and nonnegative step sizes for which the existing arithmetic/domain checks succeed. It does not require preselecting a particular gas state. It provides no N/U Jacobian and does not promote an endpoint.

## Second derivative bound from the pinned fit

Use `D=E d/dE` and the definitions in `TRACE_CONTRACT.md`. The already derived common first logarithmic derivative bound is `|D log sigma|<=8.8`.

For HI and HeII, `y=x=E/E0`, set `s=sqrt(y/ya)`:

\[
D\log\sigma=\frac{2E}{E-E_0}+(p/2-5.5)-\frac p2\frac{s}{1+s},
\]
\[
|D^2\log\sigma|\le\frac{2E_t E_0}{(E_t-E_0)^2}+\frac p{16}<1.
\]

For HeI let `u=x-1>0`, `c=1+y0`, `A=u^2+yw^2`, `r=E/E0=x+y0` and `B=D log y=r*x/(x^2+y1^2)`. The source parameters imply

\[
|D\log A|\le 2+c/y_w,\quad
|D^2\log A|\le 2+c/y_w+2(2+2c^2/y_w^2),
\]
\[
|B|\le1+y_0/(2y_1),\quad |DB|\le1+y_0/(2y_1)+2+2y_0^2/y_1^2.
\]

For `s=sqrt(y/ya)`, with `j=s/(1+s)` in(0,1),

\[
D\log(1+s)=\tfrac12 jB,\quad
|D^2\log(1+s)|\le\tfrac12|DB|+\tfrac1{16}|B|^2.
\]

Multiplying these terms by their actual fit exponents bounds `|D^2 log sigma|` below27. A common conservative value **32** covers all three species. These are calculus bounds on the source-owned analytic fit inside its native domain; the implementation does not evaluate a duplicate fit or evaluate it above50000eV.

## Including arbitrary implicit attenuation

For fixed proper absorber densities and step size, write

\[
d(E)=1+h c\sum_s n_s\sigma_s(E),\qquad d\ge1.
\]

`log d` is a log-sum-exp with a constant1 term. Its first derivative is a positive weighted average of the component log slopes. Its second derivative is the weighted second derivative plus their weighted variance. Thus

\[
|D\log d|\le8.8,\qquad |D^2\log d|\le32+8.8^2.
\]

The native absorption and survivor kernels include `1/d`, `E/d`, `sigma_s/d`, `E sigma_s/d`, and `(E-chi_s) sigma_s/d`. Species counters differ only by nonnegative constants. If the lower physical energy is `A>chi_s`, a common envelope covering every nonzero component is

\[
L=17.6+\max_{s\,\mathrm{active}}\frac{A}{A-\chi_s},\quad
M=64+8.8^2+\max_{s\,\mathrm{active}}\frac{A\chi_s}{(A-\chi_s)^2},
\]
\[
|D\log f|\le L,\quad |D^2\log f|\le M,
\quad |E^2 f''/f|\le K:=M+L^2+L.
\]

Subthreshold species contribute exactly zero and have no borrowed error scale. The chemical chi remains distinct from the sigma threshold. The bound for direct heat is on its own kernel, rather than on the larger energy kernel; the separate ABI subtraction check remains unchanged.

## Why rounded probability nodes do not require an arbitrary-kernel guard here

Let the physical support be `[A,B]`, `w=B-A`, and let the ideal normalized closure have mean `m=U/N`. It is positive. Let an actual discrete positive measure have mass `S`, normalized mean `m_d` and all its nodes in the same interval. This argument does not need to assume an accurate probability coordinate or exponent p: it covers **any** positive measure with those moments, including the actual moment-refitted rounded nodes.

Define

\[
\epsilon_N=|S/N-1|,\quad \epsilon_m=|m_d-m|/A,
\quad V=\exp[L\log(B/A)].
\]

Expand each kernel about the common target mean. The constant terms cancel up to the measured mass defect; the linear term depends only on the measured mean defect. Bounding both Taylor remainders gives the conservative relative bound

\[
\epsilon_{\rm shape}\le V\left[\epsilon_N+(1+\epsilon_N)
\left(L\epsilon_m+K(w/A)^2\right)\right].
\]

This explicitly controls changes of weights and node locations as well as the implied closure shape. Matching moments alone would not justify this for an arbitrary kernel; the source-specific curvature bound is essential.

For each actual represented q, compare the exact rational product `R*q` with the actual binary64 native argument `float(R*q)`. Both must remain on the same physical branch. If their maximum relative separation is `epsilon_E`, the extra argument-rounding bound is

\[
\epsilon_{\rm coordinate}\le(1+\epsilon_N)V
\operatorname{expm1}[L\log(1+\epsilon_E)].
\]

The implementation adds conservative arithmetic slack to this analytical envelope and takes twice the maximum64/128 bound. That reserved budget must be no larger than1/16 of the unchanged local tolerance. The remaining tolerance is used by the old native response and heat checks. The source fit's native floating transcendental errors and old attenuation arithmetic are not newly proven by this certificate; the same pinned implementation and existing numerical evidence remain the authority for them.

## Declared physical cap versus rounded support metadata

For the failed cell, `b` is the stored result of `50000/R`. The ordinary binary64 product `R*b` is50000, but its exact rational product exceeds50000 by2.3540237372776163e-12eV. That excess is **not** admitted as physical support or used to evaluate a formula beyond the provider domain.

The new rule additionally requires explicit caller metadata `support_cap_ev=50000`, supplied by `native_step_v3` only on its actual `min(cell_edge_right,50000/R)` cap branch. It also verifies the identifiable cap quotient metadata (`b == 50000/R` and `R*b == 50000`), while the comparison interval uses the declared physical upper endpoint50000eV. It requires the authoritative target mean `U/N` and **every** exact `R*q` and actual native energy to lie strictly inside that physical interval. No stored quantity is changed. The positive-measure bound then compares the numerical measure against the positive mean-matched closure on the declared physical interval. It does not claim that a hypothetical infinite-precision closure on the slightly overshooting metadata endpoint was a physically valid object.

If cap provenance is absent, if any node crosses the physical cap, if a target mean is outside the physical interior, or if any threshold side is ambiguous, the alternate route rejects. The original source-band rule is therefore retained, not widened by an epsilon.

## New evidence

`COORDINATE_CHANGED_CELL.json` records only the exact newly failed PILOT01 input under this changed operator. No old completed trajectory was replayed.

- Original generic indicator:1.6553590127107777e-7.
- Declared physical support:[49999.99578042068,50000]eV.
- Largest exact/native node energy:49999.99999869783eV.
- Total reserved coordinate/shape bound:7.211679232457615e-12.
- Remaining response tolerance:9.999278832076754e-8.
- Exact mass errors:3.78e-18 and1.69e-17.
- Exact mean defect divided by lower energy:2.62e-17.
- Common attenuated relative-curvature bound:506.043.

Four new tests passed: changed failed-cell preparation plus physical and extremely stiff absorption, continued rejection for an arbitrary kernel, continued rejection of a thin threshold-crossing support, and refusal of cap equality without explicit caller provenance. Native2calls/192energies, gas RHS0. The missing-adapter RED and successful first candidate evidence are retained. The numerical candidate now exists for independent review and a changed actual integration attempt; this document itself does not authorize full-history scientific admission.

The first candidate without the explicit caller provenance keyword is preserved as `COORDINATE_V1_AS_RUN.py` and `COORDINATE_CHANGED_CELL_V1.json`; its source and local evidence are not relabeled as the revised API. The final four-test evidence is `COORDINATE_EXPLICIT_CAP_GREEN.log`.
