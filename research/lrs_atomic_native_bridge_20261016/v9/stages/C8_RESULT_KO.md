# LRS V9 C8: photon birth / opacity clock factorial isolation

Parent: `rei_bianchi PR168 c02fb3492b99b79c8b2e3bae1a6183510ff1df9b` (read-only). Input and conclusions apply only to independent smooth 0D fixed-energy E=80 eV, threshold=13.6 eV, `X=ln(a/a0)` continuous photon source/absorber experiment. Not an actual Grackle-Case A, not stellar source, not physical EoR, and not native source-on direct execution.

## Executed contract

Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2 in ChatGPT sandbox. `src/birth_opacity_clock.py` evolves photons N, neutral HI M, ionized HII, source births B, absorbed A, binding energy chi*A, excess heat (E-chi)*A. Direct independent continuous SciPy Radau RHS integrates (N,M,B,A). Six alternative clock controls:

1. `mid_mid`: S_mid, opacity_mid, exact pair, symmetric photon source;
2. `source_left`: S_left (opacity_mid);
3. `opacity_left`: k_left (S_mid);
4. `both_left`: both left;
5. `birth_start`: full source at panel start (midpoint S and k);
6. `chem_be`: both midpoint coefficients but BE paired chemistry step.

Five cases x six methods x six grid counts N=8,16,32,64,128,256 = **180 executed case/method/resolution rows**, not 180 independent production histories. Continuous Radau uses rtol=1e-12, atol=1e-14 with max_step=end/150. A separate prescribed-linear-κ problem compares exact integrating-factor SciPy QUAD reference.

## Dynamic HI feedback (both source and opacity vary, t_end=0.8)

| mode | N256 photon absolute error | last log2 error ratio |
|---|---:|---:|
| mid_mid | 4.0867843e-07 | 1.999992 |
| source_left | 1.9614122e-04 | 0.996894 |
| opacity_left | 1.3588696e-04 | 1.005172 |
| both_left | 6.0717332e-05 | 0.989347 |
| birth_start | 4.3077464e-04 | 0.998190 |
| chem_be | 5.4371951e-04 | 0.997587 |

Observed independent photon+HI species/event and frozen-energy ledger max abs across 180 rows: `4.61853e-13` (ledger units mixed, supremum dominated by photon-energy eV bookkeeping), all nonnegative stocks. These are bookkeeping identities by construction, not proof of continuum accuracy. Observed max `k*h*M0` in the bounded stiff probe N=8 is `2.033`; the benchmark does not show uniform stiff-order acceptance.

At identical h, leading 1st-order source and opacity error contributions can **partially cancel**, so `both_left` can numerically outperform either one-lag variant and still exhibit p≈1. A special *prescribed linear opacity* test with `S(x)/κ(x)=const` and affine κ is solved exactly by midpoint because midpoint integrates κ exactly and the particular solution is constant, giving nearly machine-zero error for every N. Initial incorrect generic monotone-error assertion **failed once**, then replaced by a derived exact-case regression; no numerical tolerance weakening.

## Scientific interpretation and next actual owner test

R5 Wolfram formal local defects + measured C8 behavior support a specific method to isolate source birth, opacity and BE chemistry timings with a source-on full **owner-matched** native control matrix. This is **not** measured causal attribution in the owner. Next direct native study on frozen owner PR150 should create opt-in variants only: source on/off, photons on/off, birth midpoint vs source-age chronology, opacity start vs half-state, baseline BE vs RR midpoint; require exact same total-H density, source spectrum, energy/angle quadrature and physical X interval with N refinements; do not confuse optical depth predictor with actual midpoint-neutral state. Full EoR/Case B/signed Bianchi remains HOLD.

Supplementary literature: Jonathan Mackey A&A 539 A147 (2012), second-order photon-conserving time-centred ray tracing; HE25/HE26 source-age + moving-cut research; bass_cr C21B threshold-safe pair control. No novelty claim for midpoint exponential integration.
