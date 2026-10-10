# Independent adaptive reference contribution

This is a separately implemented numerical reference, not final independent review or physical-model validation. `reference.py` imports neither the primary `model.py` nor its reaction step. It transcribes the published R15 source and HG97-B rate, present baryon normalization, and the dust+Lambda+shear equation directly, using the declared shared constants.

The state is `(Q,Nrec,Nemit,Nexcess,tau,t)`, with independent adaptive DOP853 integration in x=ln(a/a_i). A terminal event locates Q=1. A second IVP integrates the capped phase, including recombination and nonnegative excess separately. Counter identity is measured afterward; no counter is reconstructed from the identity.

The capped phase is justified for the selected source over z=20→4: S/R is proportional to `(1+z)^0.26/[1+((1+z)/2.59)^5.68]`. Thus d ln(S/R)/dx is `-.26+5.68*u/(1+u)` with `u=((1+z)/2.59)^5.68`. It is bounded below by 5.287716 on this interval. S/R at overlap is 4.19864 (r=0) and 4.19995 (r=.1). S/R therefore remains above one afterward. This verifies absence of release for this source; the reference fails if that condition cannot be established.

Both full histories completed, with 801 log-a output epochs each and photon-ledger residual at most 1.78e-15 photons per H. The rate is alpha_B(20000K)=1.4276758454238053e-13 cm^3/s. The numerical results are:

| Initial s/H | z50 | z90 | z overlap | tau(20→4) |
|---:|---:|---:|---:|---:|
| 0 | 7.328395478218631 | 6.281382662084948 | 6.106684127029477 | 0.03744182110266508 |
| .1 | 7.327717069145448 | 6.280940302005894 | 6.1062748484984315 | 0.037415708853056326 |

Execution receipt includes command, Python/NumPy/SciPy versions, source hashes before and after, output hashes and actual runtime. The tool process returned exit code zero. Original JSON/CSV products preserve all six state channels. The callable `run_reference(config,epochs=...)` additionally accepts an explicit x grid for a direct comparison if interpolation error is material.

Scientific scope remains the stated reduced volume model, fixed ionized-zone temperature, single-He electron closure, prescribed source and dust+Lambda approximation. The optical depth is only the z20→4 segment. CR/RCT/HH and directional photon transport were not computed by this contribution.
