# Same-source positive two-face moment assembly

The actual stopped full-history interval is t0=11419941379473.664 s to t1=11498309373145.336 s, attempt42. All53 checkpoint-bound dependency bytes matched before diagnosis. The original error came before any native opacity/gas call: the endpoint source moment in cell158 was one binary64 ULP below a*N. This is a numerical assembly defect; it is not evidence of negative physical emissivity.

The saved hard event is the 50000 eV upper source-band boundary crossing q_left=50049.629458596486 eV. The provider R agrees bitwise with the source's R. The rounded product R*a equals50000, while the rational product of those binary64 operands is smaller by1.3439883198058135e-12 eV. Independent MP80 background arithmetic gives a physical left edge smaller by2.209082333413627e-12 eV. Thus neither a rounded endpoint equality nor the scheduled crossing warrants zeroing the tiny positive source.

## Derived formula and numerical representation

For the fixed comoving cell [a,b], write the nonnegative photon-number source measure as dM. The same pinned interpolation gives

N = integral dM,
D = integral (q-a)dM >=0,
E = integral (b-q)dM >=0,
Q = a*N+D = b*N-E.

C11 already evaluates N and D through analytic positive segment moments, but independently rounds the direct Q formula. At the observed endpoint this creates Q<a*N by1.044048714879764e-53 in source-rate energy units, even though the separately integrated D=1.0728764545916971e-54 is positive. Candidate1 used a*N+D everywhere. The required new-band-endpoint check then exposed3 upper-face cancellation/rounding failures at10 eV exits. Its executed bytes and failed56-endpoint report remain preserved as `source_precision_v2_attempt01.py` and `SOURCE_BAND_ENDPOINTS_ATTEMPT01.json`.

The final candidate uses the nearer-face representation: a*N+D when D<=(b-a)*N/2, and b*N-E otherwise. E is integrated directly, never obtained as b*N-Q. N, the existing D, R, bands, source data and quadrature nodes are untouched. U=R*Q remains paired. This is a change of arithmetic expression for the same moment; it does not project a failed Q onto a bound.

To derive E on a native interpolation segment x=ln(q/a) in[x_l,x_r], let L=ln(b/a), d=x_r-x_l and y=(x_r-x)/d. With f(y)=f1*(1-y)+f0*y,

E_segment = d*b*[(1-exp(x_r-L))*(f0+f1)/2
              +exp(x_r-L)*(f1*V0(d)+f0*V1(d))],

V0(d)=integral_0^1(1-y)*(1-exp(-d*y))dy,
V1(d)=integral_0^1 y*(1-exp(-d*y))dy.

All mathematical terms are nonnegative on the retained support. Stable expm1 evaluates the first factor. The new helper evaluates the convergent alternating series

V0=sum_{k>=1}(-1)^(k+1)*d^k/[k!*(k+1)*(k+2)],
V1=sum_{k>=1}(-1)^(k+1)*d^k/[k!*(k+2)],

through k=24 on the unchanged0<=d<0.5 domain. Alternating remainders are bounded by the first omitted term; floating-point evaluation is checked against independent80-digit positive quadrature. The source cell offsets use existing binary64 grid/logarithmic coordinates. This is not a claim that every intermediate floating number equals the exact-real provider moment.

The unchanged source cone comparisons Q>=a*N and Q<=b*N are enforced on the represented binary64 moment at every candidate call. Both faces remain failclosed. The independent direct-Q formula must agree within the existing1e-12 pairing tolerance; its observed discrepancy is recorded. No endpoint shift, nextafter, clipping, floor, seed, changed threshold, provider substitution or new checkpoint-state component is introduced. D/E are temporary source arithmetic only.

## Actual new verification and limits

- Two targeted new source tests pass: the exact failed endpoint with unchanged positive N/D/R, and the exact failed interval's unchanged16/32 time-quadrature plus source pairing criteria.
- On the repaired interval, maximum per-cell time-quadrature relative error is2.92989515660409e-15 against1e-10; source pairing remains below1e-12. The endpoint's new-born cell contributes exactlyzero integrated dN over this preceding interval, as its quadrature nodes are before birth.
- The final candidate passes all56 source-band hard endpoints in the already saved full target schedule under the original binary64 cone/zero-pair checks. These are changed-candidate endpoint checks, not a repeat of the old129-source acceptance campaign or a trajectory replay.
- Six independentMP80 positive-basis quadrature cases give maximum relative error5.407187968804175e-16 against1e-12.
- **MP80 endpoint source-amplitude accuracy is not claimed.** N_binary=9.691888456345966e-43 versus N_MP80=9.680100564515765e-43 differ by approximately0.001218 relative to this infinitesimal endpoint rate. This is the conditioning of the nearzero band-intersection width. The positive assembly does not repair or conceal it. The required time-integrated source gate on the actual failed interval passed independently of this diagnostic distinction.
- No native gas/opacity calls, completed trajectory replay or full-history admission occurs in this stage. The unchanged incident reconstruction/moment-fit, absorption and gas gates must still run in the subsequent repaired attempt; no pass is inferred here.

Implementation API stays `StableCellSource`, `provider_event_times`, `integrate_source`, `advance_source`. Root must declare a new source identity and append the candidate dependency to a new run; old53 dependency files and failed attempt42 remain immutable.
