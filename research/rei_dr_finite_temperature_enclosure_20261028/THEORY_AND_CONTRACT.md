# Actual signed DR fits: finite-temperature enclosures and log-temperature remainders

Unit: `rei_dr_finite_temperature_enclosure_20261028`. Author: actual root agent. Status at creation: R1–R5 constructive result, R6 independent review pending. No numerical execution is implied by this document. Original project DAG working33/88, central28/88,88IDs/17edges,delta0.

## R1 — Question, scope and completion contract

Construct finite-interval enclosures of the actual three retained dielectronic-recombination (DR) rate fits and of their selected conditional kinetic-energy loss coefficients. Also construct a uniform first-order Taylor remainder in log temperature. The native pointwise temperature derivatives already exist; they are reused as source definitions, not claimed as a new implementation. This unit supplies a previously missing finite-temperature component using actual coefficients.

The intended functions are real functions whose parameters are the exact binary64 images used when native Python/NumPy converts the pinned JSON numbers and constants. They are not the ideal decimal-lexeme functions, the complete sequence of rounded callback operations, or an uncertainty envelope for atomic physics. Physical fit error, non-Maxwellian corrections, missing channels, RR/Mao loss, photo rates, REI25 integration, and the actual recipient thermal state remain outside this result. Their missing inputs remain missing. Actual recipient T/native25/radii=null; L4_ready=false; global_physical_completion=null.

Completion requires the derivation below, actual independent R6/C9 review, a source-bound implementation with outward arithmetic, one bounded discriminating run preserving raw values, and publication/dual-backup ACKs at each completed stage. Stage counts are local20, separate from the original88-node DAG. No new IVP, old suite replay, whole callback rerun, or owner-source recomputation is authorized by this contract.

## R2 — Fixed source identity and actual source bridge

REI PR237 pin `ee6746ab172f862dddfdec63b59e5e3707b59eaa` supplies the actual constructor, coefficients and conditional loss. The coefficients file is:

`research/rei_expanded_event_consumer/blocker_closure_20261026/intake/rec119/data/atomic_coefficients.json`

Git blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`; SHA256 `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc`. Read ranges: whole file, particularly DR rows218–280 and runtime domain282–285. Exact bytes are preserved as `source/atomic_coefficients.json`.

The same coefficient and atomic-network blobs occur in the BASS source underlying the VigilODE PR95/REI PR241 fixed-rate chemical polynomial. Atomic-network blob `e3a0603176304f64b953c0b2faf898d6b75eceb5`; model blob `73285c1585f8edca92487effe95e68448f3163b8`. This proves shared parameter/function input identity, not equivalence of the surrounding thermal, density or clock conventions. The source intake manifest preserves full paths and pins.

Actual `recombination_moments.py` lines55–80 convert the DR rows to float arrays; lines95–101 enforce the common runtime domain; lines132–142 define DR rates/losses/first log derivatives; lines143–152 validate totals and distinguish a present numerical zero from structural absence. The source module explicitly calls its Maxwellian energy moment conditional and says number-fit accuracy does not bound derivative accuracy. These original evaluative statements are preserved in the source copy and are visible to reviewers.

The PR237 constructor selects `rr_closure="mao2017"`. That replaces RR loss by a hybrid native-rate/Mao-factor expression and leaves the DR expression studied here intact. We do not replace that closure. The adjacent saved background T=14919.863839279506 K is only a labeled interpolation of saved states, with continuum error null; it is a useful source-calibration point, not an actual recipient temperature determination.

Badnell's primary data page states the DR fit and its units: https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/ . SciSpace/Exa intake supplies primary fit/closure evidence; Python Decimal primary documentation supplies arithmetic semantics. Full original source copies are source evidence, not external-literature quotations.

## R3 — Definitions, encoding, units and domain

Let s=Float64(1e-6), k=Float64(1.380649e-23), regarded thereafter as exact real numbers. Every c_j and E_j is likewise the exact real image of the pinned JSON-to-binary64 conversion. Store both the binary64 hex representation and exact decimal/rational image. Do not replace c_j E_j by a separately rounded product: the selected real formula multiplies these exact images in real arithmetic.

For T in kelvin and 100 <= T <= 1e6, define

    g_E(T) = T^(-3/2) exp(-E/T),
    alpha(T) = s sum_j c_j g_Ej(T),
    L(T) = k s sum_j c_j E_j g_Ej(T).

alpha has units m^3 s^-1. L has units J m^3 s^-1 and n_e n_ion L is proper-volume kinetic cooling in W m^-3. Binding-energy transfer is a separate reservoir. The coefficient units c_j are cm^3 s^-1 K^(3/2), E_j is K. The represented numerical conversion factors differ minutely from ideal exact-decimal constants; this encoding fact is explicitly retained.

Actual rows, shown as original decimal lexemes (the implementation freezes their binary64 images):

| Key | c_j | E_j/K |
|---|---|---|
| 2:1 (He+) | 0.001417, 0.0002235, -2.185e-05 | 463300,553200,888700 |
| 3:1 (Li+) | 2.941e-05,6.068e-05,-7.753e-07 | 634500,702400,827100 |
| 3:2 (Li2+) | 0.0001451,0.005789,1.889e-05 | 852900,1056000,11700000 |

For this source all E_j>0. A valid source species with no DR row is structurally absent in this retained model and has identically zero DR fields. An unknown species/key is an input error, not inferred absence. Inputs must be finite real values with ordered closed intervals wholly inside the runtime domain; booleans/complex/NaN/infinity are refused. Integer, decimal and float input encodings must be explicit. Float endpoints mean their exact binary64 images, not printed decimal approximations.

## R4 — Chosen finite construction and discriminating alternatives

Grid sampling cannot by itself bound the interval. An endpoint-only maximum also fails when a single exponential term has an interior maximum. We therefore use analytic term extrema, signed interval summation and a separate source-specific positivity argument. This preserves negative fit components without treating them as negative physical channels or clipping them away.

The small tests will distinguish: an interior peak from endpoint-only bounds; signed-fit values from clipped-fit values; exact positive support from underflowed binary64 zero; finite Taylor remainder from pointwise derivative agreement; and genuine structural absence from an unknown key.

## R5 — Constructive derivation

### D1: term range on a finite temperature interval

For T>0 and E>0,

    d g_E/dT = (g_E/T)(E/T - 3/2).

Thus g_E increases until T*=2E/3 and decreases thereafter. For I=[a,b], define

    m_E = min(g_E(a),g_E(b)),
    M_E = max(g_E(a),g_E(b),g_E(2E/3) if 2E/3 in I).

Then the exact image is [m_E,M_E]. The endpoint minima are valid even when the maximum is interior. Peak membership is decided by exact comparisons 3a<=2E<=3b, avoiding rounded peak classification. If peak evaluation uses an interval enclosing 2E/3, interval evaluation contains its exact value.

For signed w_j define lo_j=w_j m_j and hi_j=w_j M_j when w_j>=0, and lo_j=w_j M_j, hi_j=w_j m_j otherwise. Summing gives a rigorous (possibly non-tight) range of sum w_j g_j. The same construction applies to alpha with weights s c_j and to L with weights k s c_j E_j. Term extrema need not coincide, so no claim of an exact total image is made.

### D2: actual total positivity, including below binary64 underflow

For the two signed rows let c_0>0,c_1>0,c_2<0 and E_2>=E_0. For every T>0, g_E2(T)<=g_E0(T). Therefore

    c_0 g_E0 + c_1 g_E1 + c_2 g_E2
      >= (c_0-|c_2|)g_E0 + c_1 g_E1 > 0,

provided c_0>|c_2|. For the loss replace c_j by c_j E_j. The required margin is c_0 E_0 > |c_2| E_2. Both inequalities hold for the exact binary64 images of both actual rows and will be checked with exact rational arithmetic. The third row has all-positive coefficients and positive energies. Hence all three represented alpha and L functions are strictly positive for all T>0, including the entire supported runtime domain. This is a property of the selected fits/conditional closure, not proof of physical adequacy outside that domain.

The same inequalities give a computable positive lower bound on any compact I: use the positive rewritten weights and each kernel's positive minimum. Take the maximum of that valid lower bound and D1's generic signed lower bound, retaining D1's upper bound. This strengthens the range without changing the function. For absent retained DR rows the exact value remains zero. Binary64 exponential underflow in a present row does not contradict strict positivity; structural and numerical masks must remain distinct.

Clipping c_2 to zero changes alpha by s|c_2|g_E2(T)>0 and L by ks|c_2|E_2g_E2(T)>0. These are exact expressions for the bias at every T>0 and supply a source-specific counterexample to clipping.

### D3: first and second derivatives in log temperature

Put ell=ln(T/K), x=E/T, D=T d/dT. Since D x=-x,

    D g_E = (x-3/2) g_E,
    D^2 g_E = ((x-3/2)^2-x)g_E
            = (x^2-4x+9/4)g_E.

Termwise differentiation is legitimate for a finite sum of smooth functions. The same two derivative formulas apply to both alpha and L by their constant weights. These reproduce the native first derivatives without replaying the native array callback.

For x in [E/b,E/a], q2(x)=x^2-4x+9/4 has derivative2x-4. Thus max|q2| occurs among the two endpoints and x=2 if included. Let Q_j bound that maximum outward, and let M_j be D1's kernel maximum. Then

    B2(F,I) = sum_j |w_j| M_j Q_j
    >= sup_{T in I}|D^2 F(T)|.

The product of separate maxima is conservative; correlations are not assumed.

### D4: uniform finite-step Taylor remainder

If T0 and T0 exp(h) and the whole intervening log segment lie in I, Taylor's integral remainder gives

    F(T0 exp(h)) = F(T0) + D F(T0) h + R,
    |R| <= B2(F,I) h^2/2.

Indeed R=integral_0^h (h-u) D^2F(T0 exp(u)) du for h>=0; reversing the limits yields the same absolute bound for h<0. Because log is monotone, endpoint membership in the closed temperature interval suffices for the whole segment. For two endpoints one may enclose h=ln(T/T0) with outward log arithmetic. The implementation must include the uncertainty in F(T0), D F(T0), h and the bound when forming an actual enclosure; evaluating a rounded linearization and adding only the analytic remainder would omit arithmetic error.

### D5: conditional DR energy identity

With the selected Maxwellian/kernel assumptions, L=kT(3alpha/2+Dalpha). Substituting D3 cancels the 3/2 term exactly and gives

    kT s sum c_j[(3/2)+(E_j/T-3/2)]g_j
      = ks sum c_j E_j g_j,

which is the direct native DR loss expression. The cancellation is an algebraic statement about the selected real formula. Native floating operation order can differ; the interval result does not certify its full rounding path. The empirical number-rate fit alone supplies no independent uncertainty bound for this energy moment. No RR closure is inferred from D5.

## Implementation and verification contract (R9/C1–C5)

Read the pinned coefficient bytes and verify their SHA256. Preserve original inputs, source identity and exact parameter images. A small stdlib-only API shall expose source row loading, finite interval alpha/L enclosures, exact positivity certificates, first log derivative enclosures, and D4 linearization enclosures. Valid absent species have a structural-absence result; invalid species/domain/encoding fail explicitly. Only the three source rows and declared retained absent species are admitted.

Use Decimal precision at least50 digits (nominal60), directed ROUND_FLOOR/ROUND_CEILING for basic arithmetic, and outward neighbours around correctly rounded exp/sqrt/ln results. Do not assume transcendental functions obey the context's directed rounding: Decimal exp/ln are specified correctly rounded in ROUND_HALF_EVEN. Monotonicity plus next_minus/next_plus at the same precision provides outward endpoint bounds. Exact unary signs use copy_negate/copy_abs, avoiding default-context rounding. Enforce an exponent range sufficient for exp(-117000) and trap overflow/invalid/division errors; decimal underflow/subnormal must not silently create a support certificate. Document the trusted arithmetic library and version; no hardware/libm callback rounding claim.

Tests use a separately written >=90-digit direct formula oracle plus exact rational positivity checks, not only the implementation's interval routine. Finite oracle samples are diagnostic; interval correctness comes from D1–D5 and arithmetic review. Record actual scalar results for all cases, not only test counts. Required cases:

1. All three source rows on [100,101], [14000,16000], [300000,400000], [900000,1000000], and [100,1000000]; source-specific positivity margins and interval endpoints. Include interior peak of the He+ first term at2*463300/3.
2. He+/Li+ at T=1e6: signed vs clipped direct values and positive bias; no coefficient clipping in the implementation.
3. Present rows at T=100: mathematical positive interval/direct value and a separately labeled binary64 scalar-formula zero if observed. Compare a valid absent DR key1:1; unknown9:9 must be refused.
4. At T0=the exact binary64 image of14919.863839279506, use h=+/-1/128,+/-1/256,+/-1/512 within [14000,16000]. For alpha and L show actual direct residuals, outward remainder bounds and containment. Preserve the interpolation-only origin of this T0.
5. Refuse nonfinite/complex/bool/out-of-domain/reversed intervals and source-hash mismatch. A small precision comparison (e.g.50 vs70) resolves outward arithmetic stability, not a broad resolution sweep.

One bounded worker performs these selected cases once. A saved-result figure may plot signed DR response/finite remainder data with explicit axes/units and source scope; it must not rerun functions. Single scientific repair pass only on actual findings, with changed-source identity and targeted verification. No blanket suite.

## Resources, publication and continuation

Current approved absolute cumulative ceilings are planning20/presentation60 CPU-s. PR243 inherited charges17.295332885/54.561494494 are counted once. PR245 disjoint closed increments1.909208/1.655837 (including preserved tail reserves1/0.5), plus the directional unit's disjoint0.134826177/1.865714814, yield19.339367062/58.083046308 before this unit. Do not reopen PR245's30/65 approval or transfer its allowance. Keep its separate published branch view. Unknown administrative/runtime tails remain UNKNOWN_NOT_ZERO; no whole-session budget PASS.

New preparation targets: one stdlib worker<=0.4 CPU-s; one small saved-data figure<=1.5 CPU-s; a single bounded symbolic identity check only if it fits its separately reserved small allocation. Freeze actual reservations and watchdog command before execution. Remaining observed headroom0.660632938/1.916953692 is not a claim of zero unknown overhead. Main595.225063/600 NO_MORE_IVPs is unchanged. After this bounded requested continuation, restore original planning10/presentation30 while retaining all charges and closed reservations.

R6/C9 require actual native reviewer returns with read files/ranges, concrete findings/counterexamples, scoped impact, minimal correction and separate verdicts. This new review is independent but not advertised as blind: the existing reviewer has source-census context and a shared filesystem. Original finite-thermal blind audit remains separately preserved; CAS is not its replacement.

Every actual completed stage is posted and dual-backed with real provider ACK, retaining pending states until delivery. Next root decision is based on returned findings and the changed-source census, never a thumbs-up or count alone. No global DAG/physical admission follows automatically from this component's local completion.
