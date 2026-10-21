# H/He/Li implementation preparation — awaiting scientific contract

The package was assembled without importing its physical model or launching any integration. Active donor is the exact HE32 `CompactTransport`, BASS_HE commit `e8bb035d31f59e34734947b9082bdbd60128b799`; code SHA256 `0fa826025836a0126fac580de98e3b45c9dcc750e1e243afe933c249ae8e4b6c`. The earlier 40-state REC wrapper remains an unselected historical snapshot and is not copied into this active package.

## Relocatable layout and dependencies

- `code/compact_transport.py`: unchanged donor bytes. Its `UNIT` resolves to this pilot directory.
- `vendor/`: unchanged `canonical_fv.py`, `species_hierarchy.py`, `lrs_boltzmann.py`, `prepared_moments.py`, background lock, and original license.
- `evidence/BASELINE_MANIFEST.json`: unchanged donor baseline guard; every listed local vendor SHA256 was checked without importing it.
- `data/verner_photo_full_original.dat`: exact full source photo table.
- `data/verner_photo_Z1_Z2_Z3.dat`: six exact source lines in original order, covering H I, He I, He II, Li I, Li II and Li III photo parents.
- `data/verner_ferland_rr_table1_original.dat`: exact full RR source table. The H/He/Li rows remain unaltered, including both He I a and He I b alternatives; the root must select the intended branch.
- `evidence/PREPARATION_SOURCE_MANIFEST.json`: per-file source/destination, size, SHA256, identity relation and static import lists.

External Python dependencies are NumPy and SciPy, plus standard-library modules. Matplotlib will be needed for later plots. No neighboring source paths, network access, Rust bootstrap, native compilation or new package installation are required to import this donor layout in a fresh process. The donor's module-shadowing guards require a process without differently sourced `canonical_fv`, `species_hierarchy`, `lrs_boltzmann` or `prepared_moments` already loaded.

## Existing transport interface

At ellmax=8, `CompactTransport.size` is 23: three geometry variables plus four five-component even radiation energy/number towers. Constructor controls are normalized initial Sigma, signed matter stress and signed radiation stress, with explicit quadrature configuration and positivity/domain checks.

`rhs(x, y, ne_cm3, with_geometry=True)` computes one geometry/momentum evaluation and returns the 23 transport derivatives plus the same geometry tuple `(a, H, s, pm, pg, pn, towers, moments)`. The dynamic proper electron density controls the photon Thomson damping; neutrino towers remain collisionless. The new atomic owner can calculate charge closure, pass `ne_cm3`, and reuse returned H for its own x derivatives without editing this donor or repeating its moment evaluation.

Twenty-one census populations and an optional optical-depth state belong to the new application, outside the unchanged 23-state donor. Including both would give 45 joint entries. This is a technical layout observation, not a choice of rates or physical closure.

## Items the pending contract must bind

The 21 census entries, isotope abundances and normalization, any neutron/tritium decay treatment, isotope electronic-rate approximation, RR row selection, initial ion fractions, UV spectrum/support/amplitude/history, prescribed temperature history, test-fluid versus energy-backreaction scope, exact Sigma/P_m/P_r sweep, solver/tolerances, budget and acceptance criteria must be fixed by the root. No rate, coefficient extrapolation, nuclear process or source history has been selected by this worker.

The root's preliminary UV support 5–60 eV and T=100–1e4 K proposals were recorded as proposals only. In particular, no low-temperature lithium collisional-ionization extension has been implemented. All scientific IVPs remain unlaunched pending the frozen contract.
