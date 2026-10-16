# Source-qualified scope

- SOURCE: rei_bianchi PR104 `f66929c23ea3fa6e39dd4808e5b27d136c568a03`, RUN002/rp01_n16384/preview.csv original Git blob `90b29d17bfb87debf58b62143e61246c7e462129`, flrw_n16384/preview.csv blob `6a074b9824349d46838c876f369d9c0589163f16`.
- TRANSFORM: original CSV header and saved CSV line indices 1,129,257, decimal values and order preserved. This 3-row projection is **not byte-identical** with original 257-row preview and does not rerun the 16384-step computation.
- MEAN_VOLUME: identical x/z samples, not identical proper-time epochs. FLRW and Bianchi t_s differ. Angular-only isotropized matched-a comparison is not a new physical Einstein-FLRW solution.
- GEOMETRY: non-tilted diagonal LRS Bianchi-I, metric (-,+,+,+); a_perp=a exp(-b), a_parallel=a exp(2b), b_i=0. Observer tetrad direction mu. Conservation of spatial covariant momentum p_i.
- WEAK_LIMIT: delta log(E_emit/E_obs) = 2 Delta b P2(mu) + O((Delta b)^2). The PR104 initial s/H = +0.1 is COUNTERFACTUAL, not a CMB-admitted free-decay shear.
- OWNERSHIP: reduced Q is HII volume-filling fraction, n_e is closure-conditioned volume average, not a UV/CMB emissivity spectrum. The reported PR104 segment tau is z=20 to z=4 **only**.
- IONIZING_SPECTRUM_MISSING: PR104 supplies only an integrated ionizing-photon count source. Physical directional I_E, spectral heating, Thomson-scattered temperature/polarization, observer-total optical depth, and observed sky constraints are **null / NOT_RUN**.
- CLAIM: PASS_SCOPED_SAVED_GEOMETRY_KILLING_REDSHIFT only; no native production EoR or chemical convergence admission.
