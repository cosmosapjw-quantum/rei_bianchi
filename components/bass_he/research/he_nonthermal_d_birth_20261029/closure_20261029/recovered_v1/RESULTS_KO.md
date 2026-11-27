# BASS_HE: HE-NONTHERMAL-D-BIRTH-01 (2026-10-29)

## Source pins and evidence
- Main repo: https://github.com/cosmosapjw-quantum/BASS_HE
- Parent HEAD: `research/he-pair-count15-20261029` @ `ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce`.
- Upstream exact daughter source 15 rows SHA256 `1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264`, inherited, not replayed.
- Historical PAIR-COUNT15: old Python 19 PASS, Wolfram 6 zeros, distinct R6/C9 HOLD, local physical DAG 14/18.
- Central rei_bianchi/BASS_HE physical DAG: 28/88 (not advanced); physical completion unknown.
- PR103: draft/open/unmerged, preserving nuclear species registry, 621 NULL process cells, and conditional event records.
- PR102: draft/open/unmerged; conditional finite-mass source, no production admission; HE101 C8 partial export.
- This scoped unit's new GitHub branch: `research/he-nonthermal-d-birth-20261029`, created from exact HEAD. Only `STAGE_01_THEORY.md` was written to GitHub, commit `9044ef53762f1985eb0be1aaa4127cc11dfc094c`.
- Subsequent GitHub source/report uploads: blocked by connector safety checks, NOT published; no claim of GitHub code parity.

## Physics and numerical verification
Target-rest `4He + gamma(330 MeV) -> D_fast + D_fast`. Fixed mass energies A=3727.3794118 MeV; m_D=1875.612945 MeV; 1 MeV=1.602176634e-13 J; c=299792458 m/s.

Exact per-event pair kinetic: `2K0=306.1535218 MeV`, `K0=(A+330)/2-m_D=153.0767609 MeV`. Rest-mass deficit `2*m_D-A=23.8464782 MeV`.

Conditional exclusive event density rate R [m^-3 s^-1], if a future qualified provider supplies it:
```
S_nHe = -R          [m^-3 s^-1]
S_nDfast = +2R      [m^-3 s^-1]
S_ngamma = -R       [m^-3 s^-1]
S_Urest = (2*m_D-A)*R * MeV_to_J       [J m^-3 s^-1]
S_Ufast_kin = 2*K0*R * MeV_to_J       [J m^-3 s^-1]
S_Ugamma = -330*R * MeV_to_J          [J m^-3 s^-1]
S_Utotal = 0 EXACT
S_pD_total = (330*R*MeV_to_J/c)*n     [N m^-3]
S_pgamma = -S_pD_total               [N m^-3]
S_baryon = 4*(-R)+2*(+2R) = 0
S_charge = 2*(-R)+1*(+2R) = 0
```
A one-direction momentum source is only defined when photon unit direction is explicitly supplied. This is a manufactured source ledger, not any measured 330 MeV rate, thermalization, spatial source, cosmic IVP or electron collision operator. Fast-to-thermal number and energy exchanges remain separate NULL process inputs.

Current fresh-session exact Wolfram 6 zeros: energy, baryon, charge, count-cov determinant, daughter-energy, and source residual; full witness Fano threshold 0.0552803185541635028. Current Python 28/28 PASS, 0 fail, fast standalone tests only, `python -m unittest discover -s tests -p test_*.py -v`. 31 manufactured rates in [0,3] have exact zero conservation residual; reversed photon sign breaks conservation, plot read directly. No production numerical IVP, native Rust/Fortran build, independent R6 or C9 reviewer, actual rate/flux, H-Li network integration, or full BASS_HE test suite was executed.

## Audits and claim gates
- R6/C9: independent native model review NOT_RUN because native dispatch was not exposed.
- Source-only fail-closed tests passed for missing rate, negative rates, floats, wrong source class, wrong frame, wrong or absent photon direction, inactive physical switches.
- Plot is a mathematical diagnostic generated from manufactured rates, not a cosmological prediction.
- Physical provider, actual source `R_event`, cross-section at 330 MeV, photon bath/history, target-motion frame adapter, f_D phase-space distribution, thermalization/stopping, radiation/escape, and C_v are unresolved.
- `physical_activation=false`, `L4=false`, `production=HOLD`, `physical_D_pool=NOT_ADMITTED`, physical count delta = 0.
- Rice et al., Phys Rev C 61, 064612 (2000), DOI 10.1103/PhysRevC.61.064612 only covers 150–250 MeV and cannot be used as a 330 MeV event-rate normalization.

## DAG tracking
- Central BASS_HE/REI physical: 28/88 unchanged. Prior PAIR-COUNT15 local scientific: 14/18 unchanged.
- New scoped R1–R10/C1–C10: 17/20 accepted **as source-only work products**, C8 partial numerical maturity, R6/C9 independent review not performed. Not 17/20 physical acceptance.
- GitHub backup: new branch + first theory checkpoint only. No full source GitHub push; Google Drive and Dropbox external new backup mutations also blocked by tool safety checks. GitHub branch and one checkpoint commit only, local ZIP is complete.
- Local exact source package includes code, tests, math report, plot, stdout log, ledger, machine-readable manifest, and next-thread handoff.

## Recommended one next node
`HE_NAMED_NONTHERMAL_BIRTH_POOL_NEXT`: first establish source-qualified *exclusive* 330 MeV event differential kernel + incident photon distribution/target-rest frame with error and identity, then bind the f_D source and independently study stopping and heating. Do not mix moment covariance/Poisson toy, mass-energy source identity and rate provenance.

## Additional theorem and implementation: pressure trace partial identification

The independent new mathematical result is a universal Jensen-secant enclosure of the *event-level* finite-mass pressure-trace moment using only the frozen second angular moment. A full angular distribution is not inferred. For original FULL witness m2=24377/71485, trace [588.113334807457, 588.113999573142] MeV/event, width 6.64765685910e-4 MeV/event. The bounds are sharp over arbitrary even angular measures, but not established sharp in the prior finite sextic family.

New source: `src/conditional_pressure_trace.py`, test group: `tests/test_conditional_pressure_trace.py` (8 PASS), source plot: `results/pressure_trace_moment_gap.png`. Wolfram f'' and gap identities checked exactly. Total Python tests now 28 PASS, full suite NOT_RUN. No new physical rate/IVP, production claim or original DAG advancement.
