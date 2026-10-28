# n/T generation and decay: frozen short execution contract

**Superseded executable plan:** Full canonical nuclear histories were subsequently recovered. The current executable authority is `NT_SAVED_PROJECTION_CONTRACT.md`, which requires actual saved-history projection and no new response kernel. The formulas and source reasoning below are retained as completed theory; manufactured fixtures and three-point-only extraction below are NOT selected for execution.

Authority: user requested n/T generation/decay research in parallel with the 17-state baseline; root authorizes theory/source intake, while numerical reservation is assigned separately. Scope: preserve and expose actual saved nonzero conditional n/T, then add a small exact supplied-source response check. No new background or nuclear IVP, no old suite replay, no altered original admission. All new files stay under `nt_extension/`; inputs are immutable.

## Immediate executable result

First extract the **three actual saved epochs** from `inputs/c2/NUCLEAR_SAVED_SAMPLE.json` into a compact n/T and source/decay event table. Keep natural logs and applicability labels verbatim. The source is conditional `instantaneously_thermalized_all_bare_nuclei_passive_reservoir_sensitivity`, 82 backgrounds×257 epochs×18 reaction families; this sample contains only case0 and epochs0/128/256. It is a different lineage from ANGTHERM01 and must not be overlaid as its newly evolved n/T.

At saved endpoint256, `ln Y_T=-239.13675018934322`, `ln Y_n=-252.49910981532693`, `t_elapsed=9.74270001421817e16 s`. These are actually saved conditional nonzero populations. Natural-log -Infinity at epoch0 is zero initial n/T, whereas very negative finite logs remain positive even if binary64 exponentiation underflows. Extract only stored rows, never invent the other254 samples. Optionally report log10 by division by ln10 as a presentation transform with its operation recorded. No new rates are needed for this extraction.

Minimum families in the table: `d_d_p`, `d_d_n`, `p_n_gamma`, `n_he3_p`, `d_n_gamma`, `n_beta`, `t_beta`; forward log coefficient, log events/baryon/s and log cumulative events/baryon. Preserve reverse status separately: external-photon support zero differs from absent reverse weak bath. Existing full source may be recovered separately; no reconstruction of missing time points from this sample.

## Exact response function to implement

Implement a pure standard-library function for a single supplied interval, with no IO or solver inside it:

`constant_source_response(y0, produced, duration_s, loss_rates_s_inv)`.

Inputs are finite nonnegative binary64 numbers; duration is positive, `produced` is the **integrated uniform-in-proper-time parent source** [nuclei/baryon], y0 is [nuclei/baryon], and each named loss rate is [s^-1]. Loss channels are unary or pseudo-first-order against a supplied frozen target bath. The caller, not this kernel, establishes physical rate qualification. Limit32 channels. Reject negative/nonfinite inputs, overflowing summed rate, or overflowing k*h. Do not silently rescale units, clamp outputs or overwrite source inputs.

Let `k=sum k_j`, `h=duration`, `x=k*h`, `E=produced`, `phi1(x)=(1-exp(-x))/x`, `phi2(x)=(x+exp(-x)-1)/x^2`. At x=0 use phi1=1 and phi2=1/2. The exact solution of `dy/dt=E/h-k*y` is

`y1=y0*exp(-x)+E*phi1(x)`;

`I=int_0^h y(t)dt=h*(y0*phi1(x)+E*phi2(x))`;

`N_j=k_j*I` and `y1+sum_j N_j=y0+E`.

For stable event counts evaluate `a=-expm1(-x)`, `b=1-phi1=x*phi2`, `L=y0*a+E*b`, and `N_j=(k_j/k)*L` for k>0. For `0<x<=1e-3`, use

`phi2=1/2-x/6+x^2/24-x^3/120+x^4/720`,

whose omitted magnitude is at most `x^5/5040` on this interval by the alternating exponential series. Then b=x*phi2. For x>1e-3, compute phi1 with expm1 and b=1-phi1. k=0 returns y1=y0+E and all loss counts0. The zero-duration case is excluded to avoid conflating finite impulsive production with the uniform source assumption. Returned fields: y1, source count E, channel counts, loss sum, signed abundance-balance residual, and declared constant-source/frozen-hazard scope. The occupancy integral is optional; avoid returning overflow when h*occupancy is unrepresentable.

This is exact for the stated constant-source problem, including arbitrarily stiff k*h within finite representable input. It is **not** an exact solution of simultaneous n→T→He3 transfer with the n-generated T source replaced by a constant bin average. Coupled source timing requires the existing coupled fast-system model or its exact matrix propagator. Do not start a new coupled campaign here.

### Targeted verification and actual-source binding

Use independently known cases: zero losses; pure decay at h=ln2/k (half survives); steady state y0=s/k,E=s*h (inventory unchanged, total losses=E); two channels with known 1:3 event-count ratio; composition of two half intervals under the same constant source; tiny x continuity. Check nonnegative finite output and balance. Tolerance: `abs(residual)<=64*epsilon*max(y0+E, smallest_normal)` for valid ordinary-sized fixtures; analytic expected-value comparisons relative1e-12, absolute1e-300. Test tiny underflow behavior separately, without upgrading an underflowed output to physical zero. Input rejection is a few targeted checks, not broad fuzzing.

Actual supplied-source use: at each positive saved C2 epoch, read `ln source DDn` or `ln source DDp` and evaluated decay coefficient directly from that row. Derive `ln Y_ss=ln source-ln lambda`, compare against **the saved** lnYn/lnYT, and report the log residual. This is a decay-dominated conditional source-balance diagnostic, not an assertion that other channels vanish. Do not assert a new history accuracy bound. The endpoint saved n/DDn/beta logs are nearly balanced; report the actual difference once under the controller's bounded reservation.

For a concrete exact interval fixture grounded in saved inputs, choose h=1/lambda and y0=0, source rate equal to the saved endpoint DD forward flux. Tag this as **manufactured constant-source interval from a real saved rate**, not a recovered cosmic segment. It has expected `y1=(source/lambda)*(1-exp(-1))` and beta events `source*h-y1`. Use the neutron and tritium intervals separately. If exponentiation underflows at an earlier epoch, skip this linear-scale fixture there and retain its log values; no floor. A source ledger links DDn production to `-2DII+He3III+n`, DDp production to `-2DII+HII+TII`, beta losses to their daughters/electron. Thus the fixture gives an explicit conserved event response using actual supplied rates without pretending to add a cosmological n/T history.

Execution maximum: one bounded standard-library run that extracts saved rows, performs the targeted checks and writes JSON/text; no plotting required in this unit. Exact CPU/wall allowance comes from root before execution. Stop after one substantive failure and return raw output for one authorized targeted repair. No source or historical test is rerun.

## Physical interpretation and 17-state event routing

The display order is n,H I,H II,D I,D II,T I,T II,3He I,3He II,3He III,4He I,4He II,4He III,7Li I,7Li II,7Li III,7Li IV. Hidden Li6 remains in the original C2 closure; its events cannot be deleted when claiming complete baryon balance of that source.

| Event | Ion-resolved stoichiometry under stated all-bare/spectator assumption |
|---|---|
| neutron beta | n→H II+e−+anti-neutrino |
| neutral tritium beta | T I→3He II+e−+anti-neutrino (spectator bound electron) |
| bare tritium beta | T II→3He III+e−+anti-neutrino |
| n+p capture | n+H II→D II+gamma |
| DD neutron branch | 2D II→3He III+n |
| DD tritium branch | 2D II→T II+H II |
| D photobreakup | D II+gamma→H II+n |
| He4 neutron branch | 4He III+gamma→3He III+n |
| He4 tritium branch | 4He III+gamma→T II+H II |
| neutron conversion | n+3He III→T II+H II |
| D+n capture | n+D II→T II+gamma |
| DT fusion | D II+T II→4He III+n |
| Li7 breakup | 7Li IV+gamma→4He III+T II |

Each row has `A·nu=0`; adding emitted electron charge gives `q·nu-heavy - N_e=0`. Total electron charge includes fast and thermal electrons; beta electrons are initially a source into the designated fast-electron channel unless thermalization is explicitly assumed. Recombination H II+e→H I is a separate event requiring its rate and plasma state, so neutron decay does not automatically form neutral H. Source production must include reactant depletion and co-products in the ledger even when reservoir abundances remain frozen for coefficient evaluation. That makes a signed diagnostic ledger, not a newly self-consistent composition.

Do not turn the all-bare isotope totals into physical 17-state ionic histories. Neutral-target nuclear branches, shake-off, bound-state beta, stopping, and transfer of secondary particles to thermal species remain qualified inputs. The equations above are a transparent illustrative closure where named; they do not erase original `CHARGE_BRANCH_UNRESOLVED` labels.

Energy owner: nuclear Q or absorbed photon energy is divided once among daughter kinetic/recoil, fast electrons, retained/escaping gamma, neutrinos, excitation/ionization and eventual heat. Count beta once: the C2 binding assigns it to evaluated nuclear decay and omits atomic donor D when assembling the coupled atomic operator. Do not deposit full Q as heat while also retaining gamma/electron energy. This kernel reports event counts only; no unsupported thermal partition is assigned.

## Source qualification and timescales

Use the frozen recovered decay values: mean neutron lifetime878.4±0.5s; tritium half-life12.312±0.025y with year365.24219878d. Sources are `inputs/localflow/inputs/EVALUATED_DECAY_INPUTS.json`; do not silently replace these with the old atomic donor's12.32 Julian-year convention. Free-neutron decay hazard is1/tau_n; T hazard isln2/t_half. A moving fast neutron requires proper lifetime/time-dilation handling and transport; the stored all-thermalized closure is explicit.

At constant bath, neutron capture hazard is `kcap=n_p<sigma v>+...`; capture/decay branching probabilities are kcap/(lambda_n+kcap) and lambda_n/(lambda_n+kcap). The capture timescale is environmental, not a property of the free neutron. C2's1/v thermal continuation and DD-produced MeV neutrons are connected only by its instantaneous-thermalization assumption. Their physical connection requires a stopping kernel. A no-source relic follows `Y(t)=Y0 exp[-int lambda_eff dt]`; sustained late n/T requires ongoing production or exceptional propagation/time dilation, not survival inferred from primordial inventory alone.

Actual C2 photons are5–60eV, below nuclear thresholds, so its external photodisintegration is support-zero **for that field**. Primary ACROPOLIS table gives D→p+n about2.22MeV; He4→T+p19.81MeV; He4→He3+n20.58MeV; Li7→He4+T2.47MeV. High-energy photons or cosmic-ray fragmentation can supply n/T, but no such matched source history has been acquired for this baseline. Weak inverse channels require a specified lepton bath; anti-nu_e+p→n+e+ threshold is1.806MeV, and electron capture p+e−→n+nu_e needs sufficient electron kinetic energy (about0.783MeV for a stationary free proton, with recoil). A threshold is not a rate. Reverse beta three-body absorption is distinct from these two-body crossing channels. No inverse weak source is set to a fake known zero merely because its bath is absent.

## Status and axes

Symmetry/gauge: source proper-time and baryon normalization; outer x=ln(a/a_ref) conversion divides physical rates by H once; integrated event counts do not acquire another1/H. Invariants: exact integer A/charge event identities, positive constant-hazard solution and source-count balance. Observables: saved conditional lnYn/lnYT plus independent event production/decay counts; these remain separate from baseline atomic fractions.

R1–R5 constructive work is embodied here; Wolfram returned zero ODE/integral/balance residuals and the stated k→0 limits/series, with intermediate singular-expression warnings preserved in raw evidence. R6 independent review and R7 bounded execution are pending. This contract creates no completed global DAG node. Working33/88 and central28/88 remain inherited. **F4 stays open for a source-qualified physical n/T transport/charge/energy coupling**, even if this exact conditional response passes. Main NO_MORE_IVPs remains unchanged.
