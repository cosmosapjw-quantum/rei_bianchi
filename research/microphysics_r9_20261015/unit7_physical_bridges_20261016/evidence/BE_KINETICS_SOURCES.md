# Lane B source record

Requested authority: Astra. Observed model identity: UNKNOWN. Accessed 2026-10-16.

1. R. Khatri and R. A. Sunyaev, *Time of primordial 7Be conversion into 7Li, energy release and doublet of narrow cosmological neutrino lines*, arXiv:1009.3932v2 (31 May 2011), primary PDF: https://wwwmpa.mpa-garching.mpg.de/mpa/publications/preprints/pp2011/MPA3083.pdf . Equations 5–9 on PDF pages 8–9 establish the adopted rate model; section 2 gives the statistical-hyperfine half-life. Section 3 explains the ground-state channel. Read as equations; figures are not numerical inputs. Search retrieval turn472view0.

2. NIST Atomic Spectra Database, ionization energies for beryllium: https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=1&biblio=1&e_out=0&el_name_out=1&ion_charge_out=1&spectra=beryllium&unc_out=1&units=1 . Be charge +3 has listed threshold 217.71858459 eV. The computation deliberately uses 217.7 eV and does not assign the tabulated isotope-unspecified precision to Be7. Search retrieval turn477search2.

3. D. A. Verner and G. J. Ferland, *Atomic data for astrophysics. I. Radiative recombination rates for H-like, He-like, Li-like, and Na-like ions over a broad range of temperature*, primary preprint https://arxiv.org/pdf/astro-ph/9509083 . The discussion following equation 6 identifies the incorrect high-temperature asymptote of the Pequignot et al. hydrogenic fit. This is a scope caveat, not a replacement rate used here. Search retrieval turn477search3.

4. Actual BBN donor: /workspace/scratch/37bc4acea758/r9_unit6_parallel_20261016/inputs/laneC/R5_DONOR_BBN.json , SHA256 47f93645a4c4fbcba0a6c3d1a9f8290adf847f011ab04d29b448633ec8525417, source commit 4bf97d5082eee54b9df50d88f43182bb651fea80. File was read directly. It supplies cosmology, baryon normalization, all nuclear abundances and the bare-Be endpoint. The source paper's abundances and cosmology are not substituted.

All propagator formulas, early-tail inequality, trace-electron accounting, convergence policy, and donor-normalized interface in the theory contract are derived for this task. No published plot values are acceptance targets. Rate-model approximation error remains separate from numerical integration error.
