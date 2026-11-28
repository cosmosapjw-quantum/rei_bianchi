# C1–C5 implementation map — preparation only

Base D is `bec636ffa3014035292c1078a758c7aa1827174d`; canonical central E is `9600a605f6380bc2262d0cfce5ff00290e594a5a`. All files of the old unit are preserved. The new code is confined to this unit and the new operations directory. No science module was imported in preparation.

| Theory | Implementation | Input/output and independent control |
|---|---|---|
| Eq1 I | `nordsieck_i(lambda,qvec,pvec,eta)` | fixed independent eta, principal complex log; mp50/80 and eta0 Fourier transform |
| Eq2 K | `overlap_k(lambda,qvec,pvec,eta)` | fixed-eta derivative; mp80 derivative and separate Eq6 quadrature |
| Eq3/4 | targeted tests | unmatched nuclear identity and plane Fourier transform; no nuclear subtraction omission |
| Eq5 matched K | `matched_overlap(lambda,delta,pvec)` | direct Delta polynomial; exact complex0 at Delta0; mp80 parallel/transverse tiny-transfer relative controls |
| Eq7/8 | `coulomb_normalizer`, `normalized_form_factor` | explicit SciPy loggamma and positive expm1 strength; independent mp gamma; eta=None means matched, explicit eta means generic nuclear subtraction |
| Eq9 TDCS | `direct_tdcs(Ei,EB,ni,nf,nB,model)` | E_h in, a0²/E_h out; lambda1/B.5; independent delta-state coefficient; model cba or plane only |

Core vectors use finite real length-three lists or tuples. Nonzero direction vectors in the TDCS API are normalized and this API convention is explicit in its docstring; energy/channel/transfer values are never clipped. The scalar-kernel input has lambda>0, p>0, eta>=0. TDCS requires EB>0 and Ef=Ei-.5-EB>0; endpoint/zero transfer is refused. Complex or nonfinite inputs and undocumented models are refused.

`FIXTURES.json` fixes nine generic cases, four root-specified moderate Eq6 quadratures,16tiny-transfer cases, seven normalization inputs and73illustrative direct CBA/plane points. Input floats define exact binary64 values; mp imports those values and uses50/80digits. Acceptance is read from the root contract: scaled modulus abs(error)/max(1,abs(reference)), and true relative error for nonzero tiny-transfer reference. Generic cancellation is diagnostic only and has no acceptance retuning.

`run_analysis.py` saves partial data after each generic/quadrature/tiny-transfer/normalization row, final full JSON and illustration CSV. The Eq6 integral is integrated on the four fixed segments0..1,1..4,4..12,12..infinity and is separate from the closed-I derivative. `plot_results.py` imports no kernel and reads only saved successful analysis; zero errors are omitted from the logarithmic axis with explicit receipt records, rather than replaced by artificial values.

Execution order is tests(3CPU/10wall), analysis(10/25), saved-only figure(3/10), within new20CPU/60wall,512MiB,1thread. One4CPU/15wall reserve remains root-controlled and unused. `run_bounded.py` refuses repeat/out-of-order calls and any incomplete/failed earlier START. It preserves START/stdout/stderr/FINISH and cumulative inclusive parent+child CPU plus measured wall; cap overshoots are failures. Historical ledgers/budgets/unknown costs stay distinct. Syntax verification uses AST parsing only. No local scientific import, test, special-function evaluation, numerical execution or render is released until root explicitly gives GO after R6/Wolfram/B1dualACK.
