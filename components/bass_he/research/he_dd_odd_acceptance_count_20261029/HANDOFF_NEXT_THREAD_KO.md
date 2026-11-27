# BASS_HE | HE-DD arm-labelled odd-acceptance and count-covariance next-thread handoff

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=111
PARENT_HEAD=0e643121b62a65dd821ea563051c59722a828a8f
BRANCH=research/he-dd-odd-acceptance-count-20261029
CURRENT_HEAD=READ_ACTUAL_REMOTE_SHA
ROOT=research/he_dd_odd_acceptance_count_20261029

CENTRAL_DAG=28/88
HE_DAG=14/18
PR110_FEM=1/2
PR111_RESPONSE=1/2
NEW_SCOPED_DAG=1/2
PHYSICAL_DELTA=0
THEORY_SCOPED=9/10
CODING_SCOPED=9/10
STAGE_PUBLICATION=20/20
DISTINCT_AUTHOR_R6_C9=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN

kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

## Restore in this order
1. Check latest GitHub Draft PR HEAD and immutable parent PR111 `0e643121...`, verify current HEAD not assumed equal to the older commit. No parent/production/source overwrite.
2. Read ROOT/`THEORY_KO.md`, `REPORT_KO.md`, `RESULTS.json`, `IMPLEMENTATION_CONTRACT.json`, `STAGE_LEDGER.json`, `TEST_EVIDENCE.md`, `PLOT_ADVERSARIAL_AUDIT.md`, `DELIVERY_RECEIPT.md`, `src/odd_acceptance_count.py`, `tests/test_odd_acceptance_count.py`, `tests/independent_cpp_rational.cpp`, `src/plot_from_results.py`.
3. Source PR110 exact Fraction `RESULTS.json` Git blob `8eec0e162e5ded507a3af1259e60361ed474c376`. PR111 detector response is conditional. Sibling `research/he-pair-count15-20261029` HEAD `ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce` is **law-of-total-covariance donor ONLY** (its sextic angular function differs from PR110's L-Lipschitz class). EXFOR original commit `939a14d7bba1ddce51975cb5e8711ce96b3b0871`, blob `c49433293921dbb012d7f1b0387745732a598efa`.
4. Verify exact staged Google Drive/Dropbox rows: Google Doc `1Wir0wn2c10wFzvC2n_fEyEpgGhuRl-QCWTtZepWYjPk`, Dropbox Paper `id:BSpOijBcT10AAAAAAEHVsA`. 20/20 rows equal at time of handoff. Text backups are not ZIP byte-restoration.
5. Run only target verification: `cd ROOT && PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -q` (historical 20/20), `python -O -m unittest discover -s tests -q` (historical 20/20), `g++ -std=c++20 -O2 -Wall -Wextra -pedantic tests/independent_cpp_rational.cpp -o /tmp/odd_oracle && /tmp/odd_oracle` (historical exact 1089), `python src/plot_from_results.py --results RESULTS.json --out-dir figures`. The Git implementation's exact Fraction helper rejects float inputs.

## New conditional theorem
For even source angular p(mu)=p(-mu), q>0 bounded ratio qmax/qmin<=r and eta=(r-1)/(r+1): `|E_q mu|<=eta sqrt(E_q mu²)`.
Under parent-certified `b in [a,u]`, `bq in [a/(a+r(1-a)),ru/(1-u+ru)]`, `Delta²(1-eta²)B-<=Var_q(K+)<=Delta² B+`. Source-frozen K0=153.0767609 MeV, Delta²=12834742575893748070725/3378807374235230161 MeV². Hypothetical delta=5% L1/700 gives labelled daughter mean offset<=1.957610462571 MeV and variance outer [986.482704593021,1532.895489267560] MeV². These are NOT experimental systematic errors, physical birth variance or heat.

**Indistinguishable-daughters:** unordered event acceptance must respect daughter exchange. Therefore effective q EVEN implies m_q=0. Nonzero m_q describes artificial arm-labelled selection/ordering, not intrinsic nuclear odd anisotropy. Do not map detector selection to emitted physical state without a separately verified response equation.

For random integer count N independent of iid tagged marks Y=(K0+Delta mu,K0-Delta mu), lambda=E N, nu=Var N, `Cov(sum Y)=lambda*Delta²(bq-mq²)[[1,-1],[-1,1]]+nu*ybar*ybarT`. Integer N also requires `nu>=frac(lambda)(1-frac(lambda))`. Hypothetical Poisson yields a signed cross covariance different from fixed N; not source evidence. Exact rational physical Delta itself is irrational unless Delta² square, so prefer certified Delta² bounds rather than rounded Delta in exact code.

## What remains actionable
Find the **full original** Arends (1976, DOI 10.1016/0370-2693(76)90671-7) and Silverman (1984, DOI 10.1103/PhysRevC.29.35) detector efficiency, coincidence/acceptance, polarization, event/particle differential conventions, and measured inverse DA near exactly matching invariant s, with uncertainty. EXFOR M0475002 330MeV 4 angular statistical rows and M0475003 320/359 SIG are **not** a measured 330MeV event SIG. Silverman Td376 MeV corresponds E_gamma 213.1255 MeV, **not** 330. Then separately source-qualify true 330 MeV photon phase-space in He rest frame, exclusive event rate, correlated D fast stopping/redistribution/deposition and C_V.

Do not rerun historical IVPs/science suite or whole 4501-node LP merely for reassurance. Do not merge Draft PRs, force push, claim dual-binary archive restore from text logs, or activate any physical RHS without qualified inputs. Run genuine different-author R6/C9 only when actual native delegation exists, otherwise retain NOT_RUN.
