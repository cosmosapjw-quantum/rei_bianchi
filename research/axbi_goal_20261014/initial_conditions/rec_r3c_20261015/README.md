# REI-AXBI: optional recombination-informed starting state (2026-10-15)

This directory is an **additive, disabled scientific intake**. It neither changes `scenario/SCENARIO_LOCK.json` nor any production Rust driver, source, active resource budget, signed-q history, checkpoint, or private scientific data.

## Where the numbers come from

[REC R3c→REI PR #94](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/94) contains the executable Python source intake, the **unmodified original October-2012 HyRec FULL H+He C** rebuild (source archive SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`), the complete real 8,001-row source run, a 1,581-row z20–1600 reference CSV, result plots, numerical tests, cross-code and two-worker benchmarks. Source C stdout SHA256 is `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400`.

The original REI scenario SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696` uses (x_{HII}=2\times10^{-4}), (x_{HeII}=x_{HeIII}=0), (T_g=8.098143045064857\,\mathrm{K}) at `zbar=20`. Under source-matched REI FLRW expansion (effective original HyRec *massless* radiation (N_{eff}=3.03821934419124)), the real native HyRec FULL result is (x_e=0.000210349192936), (T_m=9.306042400380866\,\mathrm{K}). Those are +5.1746% in free electrons and +14.9158% in gas temperature relative to the selected REI conditional IC. Under REI proper densities, instantaneous `c sigma_T n_e/H` changes +5.1746%, but **no native REI integrated optical depth, abundance history or thermal response** has been computed using this candidate.

HyRec's species output here is **total** (x_e=n_e/n_H), not separate late helium species. The proposed (x_{HII}=x_e,x_{HeII}=x_{HeIII}=0) is conditional on neutral helium at z20. Original source nH0 differs from REI's proton-mass normalization by -0.0541154%, and its helium-number convention 3.97153 versus 4 is recorded in the packet. The REI ionizing-photon initial stock remains its independently declared source-onset zero.

## Physics limits and next executable experiment

The accepted REI prescribed Bianchi I model covers **zbar20→4 only**. Formal backward extrapolation of qref=-0.01 to z600 gives (s/H=-0.81695), (H_\parallel/H=-0.63391), outside the adopted physical range. This is a source-domain warning, not a general no-go theorem. **No primordial signed-q recombination is claimed.**

To *test*, not silently adopt, the candidate: in an isolated new native-REI sensitivity worktree, verify the unchanged scenario/content SHA first; start the model at the same zbar20 coordinate from a **fresh** donor gas state (never resume an earlier AX08 checkpoint with a changed IC); keep the MD14/BB50K source, photons, clock, opacity and radiation conventions fixed; rerun physical native one-step and paired short controls, then a resource-bounded q0 history and eventually signed cases if validated. Measure source H/He/electron charge, gas energy, photon/opacity ledgers, proper-time vs shared-redshift estimands, and solver error. Original AX08 source/initial-state results remain independently valid *for their original conditional scenario*.

**Admission**: q0 original C full recombination reference and an optional donor input packet, plus validated REI local initial-property deltas; not a full R3c independent Python time-history solution, nor a modified native REI science result.

Sources: [Ali-Haïmoud & Hirata (2011)](https://doi.org/10.1103/PhysRevD.83.043513) and [Scott & Moss (2009)](https://doi.org/10.1111/j.1365-2966.2009.14939.x). Numerical authority is the byte-locked original C and REI scenario, not a literature fit.
