# Native age32 result | 2026-10-20

The frozen mode age32-block-max-diagnostics ran at q=0, age32/source8/n_mu8/transport16/time1, block-max/binary64, diagnostics ON, transport48, with 1,800 s case and total caps. Native physics 35d9747a0bbedcafdb568467ce7c1e7a25f965b6, prepared computational base 78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620, and B1 binary 89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4 matched the completed age64 base. Python3.12.3/NumPy2.3.5/SciPy1.17.0. Solver exit 0, wall 248.816 s, 11,786 solver calls, peak RSS 122,884 KiB.

Source-jump diagnosis has 32/32 birth coverage with no missing, duplicate, or invalid events. Nonbirth, gas, and ledger coordinate bits were preserved at all births. The diagnostic exact_invariant_unchanged flag was false at all 32 events and is retained as observed. The stored photon-ledger fixed gate passed with normalized residual 1.13746143275e-10 against 1e-8. Separate paired source-jump observations are MISSING_DATA, and age64 source jumps remain MISSING_DATA.

The same computational source binding was compared at 18 common age32/age64 observations. The selected 0.5% finite-neighbor endpoint target was not met. This closes only the scoped native run and finite comparison; native age convergence, native time continuum, nonlinear tube, full EoR, and production scientific admission remain open. PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.

The first launcher call selected system Python and failed to import NumPy before native execution. Its stderr and failure result are preserved. The verified venv was added to PATH and the one native case ran once in a separate scratch directory.
