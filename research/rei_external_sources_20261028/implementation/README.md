# Pointwise external source model

`model.py` implements the frozen contract in `../theory/FROZEN_CONTRACT.md`.
All configured amplitudes and toy cross sections are illustrative and uncalibrated.
The 201 saved ANGTHERM01 epochs supply stable targets and proper reference density;
no old trajectory is modified and no new IVP is solved. The source operator covers
17 thermal states and two separately counted fast reservoirs; hidden Li6 columns
are copied numerically unchanged with zero new coupling.

After controller release, from the repository root, use the actual environment Python:

```
python research/rei_external_sources_20261028/implementation/run_bounded.py tests
python research/rei_external_sources_20261028/implementation/run_bounded.py evaluation
python research/rei_external_sources_20261028/implementation/run_bounded.py plots
```

Each phase is single attempt, marker guarded, with one thread, 3 GiB address-space
ceiling, child CPU/wall limits and observed child/wrapper accounting. Failure returns
to scientific authority before any additional run. No dependencies are installed.

The tests independently check integer baryon/charge columns, scalar energy books,
strict support thresholds, boundary positivity, direct spot rates, external-off,
fast limiting branches and a direct matrix solve of the three thermal QSS states.
Output CSV contains alpha0/1/10 response stocks, baseline and QSS source derivatives,
every new event rate, fast branching, timescales, photon drains and signed energy
books. JSON records exact source/config/contract identities and numerical residuals.
The PNG presents positive outgoing energy channels; signed internal entries stay in
the CSV. Rates are proper-second rates, with no eta-to-time or cumulative integration.

Energy bookkeeping uses excess energy and effective nuclear Q-values, not injected
rest-mass energy. Fast electrons and antineutrinos are separate from heat. The
QSS timescale comparison to real source/background history remains unestablished;
these algebraic stocks are not an evolved abundance prediction. Future operator
assembly must remove old beta ownership before adding these beta columns.
