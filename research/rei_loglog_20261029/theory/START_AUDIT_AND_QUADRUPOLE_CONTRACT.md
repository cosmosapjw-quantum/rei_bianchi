# Curve origins and anisotropic rate response

Source identity: rei_bianchi PR259 HEAD `045118543c266f164c4bd177ac0194ee1ba22096`; recovered archive SHA256 `da54085272c582a71199d8ab8a8745a4bea0e1fd5f80d490b7a8e37ef469e52c` (recovery identity supplied by parent). Directly inspected the unchanged `research/rei_figure_set_20261029/outputs/raw_saved_arrays.csv`, `figures/FIGURE_METADATA.json`, `figure/build_figures.py`, and prior theory contracts. Workflow 1.0.0 and its research-policy, theory-loop, evidence/handoff references read. No numerical tests, solver runs, or renders executed in this task.

## Why some curves appear to begin late

All 17 stocks have the same initial epoch, elapsed proper time 0 and mean redshift 20. The first positive-time saved row is 0.08238295318127252 seconds = 2.610558254787199e-15 Myr. Every ON_refined stock is positive at that row. The following values are transcribed directly from those two rows; omitted-positive counts are transcribed from existing overview metadata, not recomputed.

| State | Initial abundance / Href | First positive-time abundance / Href | Positive points below overview y window |
|---|---:|---:|---:|
| n | 0 | 8.577146578238272e-29 | 0 |
| H I | 0.9998 | 0.9997999999975826 | 0 |
| H II | 1.9999999999999998e-4 | 2.0000000241743738e-4 | 0 |
| D I | 2.4995e-5 | 2.4994999999939566e-5 | 0 |
| D II | 5e-9 | 5.000000060435936e-9 | 0 |
| T I | 0 | 2.059573829380461e-30 | 57 |
| T II | 0 | 6.1787215222136814e-30 | 48 |
| He3 I | 1e-5 | 9.999999999999574e-6 | 0 |
| He3 II | 0 | 4.2573903467630726e-19 | 84 |
| He3 III | 0 | 6.590969630265232e-27 | 155 |
| He4 I | 0.082 | 0.0819999999999965 | 0 |
| He4 II | 0 | 3.4910600708349154e-15 | 79 |
| He4 III | 0 | 2.0271460761199386e-30 | 150 |
| Li7 I | 0 | 4.920438507603728e-29 | 160 |
| Li7 II | 5e-10 | 4.999999999999999e-10 | 0 |
| Li7 III | 0 | 1.4248492748458336e-25 | 106 |
| Li7 IV | 0 | 4.1191476590762784e-32 | 160 |

The overview multiplies abundances by n:1e22, H:1, D:1e4, T:1e18, He3:1e4, He4:10, Li7:1e9 and displays 1e-8 through 2. Nine initially zero species therefore also lose positive early vertices below this window. The neutron starts at zero but its first positive scaled value is already above the window bottom. Grouped plots use raw abundances but derive y limits only from positive samples with elapsed time >=1 Myr (`build_figures.py`, window construction); their early positive tails can also fall below those limits. Their linear x axes additionally compress subsecond evolution into the left boundary.

These are four separate facts: zero initial stock; positive stock below a display limit; log(elapsed time) undefined at the common initial time; and early redshift rounded to the same value. A first visible point is not a species creation epoch. OFF n/T remain identically zero under the frozen source-free configuration and should be listed as zero histories, not supplied artificial log floors.

For a full-history log-log rendering, use saved strictly positive times and positive abundance vertices, choose y limits from that whole retained interval, keep zero values in the source table, and show the t=0 initial-value table separately. All-positive masking must split paths at excluded/nonfinite vertices. If lines connect existing samples, label them as connections of saved samples. No positive epsilon can represent the actual zero initial stock or time without changing its meaning. The complete shared range to approximately 3087.32 Myr spans about 18 decades in elapsed time; grouping is needed for legibility even when all values are retained.

Use `eta=ln(a/a0)` and `z_mean=21 exp(-eta)-1`. At the first positive sample eta=9.978766240739514e-18, while stored z_mean is exactly 20.0. Distinct proper times can share rounded redshift. Retain an upper annotation 'mean z approximately 20' in early panels; avoid an inverse interpolation over a flat rounded-z array. If a tiny difference is useful, compute the separately named quantity `20-z_mean=21[-expm1(-eta)]`, not a fabricated absolute cosmic age.

## Symmetry, invariants, observables

With signature (-,+,+,+), Bianchi I can be written `ds²=-c²dt²+sum_i a_i² dx_i²`, `a_i=a exp(beta_i)`, `sum beta_i=0`. Then `H_i=H+sigma_i`, `sigma_i=dot beta_i`, and `sum sigma_i=0`. The three spatial principal axes label expansion eigenvectors, not three species histories. Constant coordinate rescalings shift beta_i constants and do not change H_i. Spatial rotations change tensor components but leave scalar stocks, sigma_ab sigma^ab, and sigma_ab pi^ab invariant. A proper-time origin shift leaves elapsed intervals invariant. Mean expansion redshift labels the background; a photon's directional redshift requires its direction and the anisotropic null propagation.

The inherited axisymmetric convention is sigma_ab=s diag(-1,-1,2); hence sigma²=(1/2)sigma_ab sigma^ab=3s² and the Frobenius norm is sqrt(6)|s|. Preserve the open-system baryon and charge ledgers, matched initial stocks and clocks, and frozen scale definitions. Number abundances/Href are scalar outputs; line intensities, polarization and directional redshift require additional transfer and atomic information. The saved ON-minus-OFF includes source and escape switches, so it cannot isolate the effect of shear.

## Derived scalar-rate selection and its useful next coupling

Assume weak incoherent one-photon absorption by an isotropic, unpolarized atomic target at rest in the chosen local tetrad; sum over outgoing electron directions and unresolved magnetic substates. Its total cross section sigma_i(nu) is direction independent. Write specific intensity

`I_nu(n)=J_nu+Q_ab(nu)n^a n^b+...`, with `Q_ab=Q_ba`, `Q_a^a=0` and `J_nu=(1/4pi) integral I_nu dOmega`.

The photoionization rate per target atom is

`Gamma_i = integral_(nu_i)^infty [sigma_i(nu)/(h nu)] integral I_nu(n) dOmega dnu = 4pi integral sigma_i J_nu/(h nu) dnu`, where `h=2pi hbar`.

Indeed `integral n^a n^b dOmega=(4pi/3)delta^ab`, so the quadrupole term integrates to zero. The same orthogonality removes every higher harmonic in this linear rate functional. At a *fixed spectral monopole*, changing a prescribed quadrupole alone leaves this scalar rate unchanged exactly, not merely through first order. It is not a new impossibility theorem: it is the selection rule of this stated scalar closure. Anisotropy can change the spectral monopole through propagation or produce atomic alignment that changes the target response.

For an explicit controlled path, let the homogeneous collisionless photon occupation be `f(t,E,n)=F(t,E)+Q_ab(t,E)n^a n^b+...` (this Q is an occupation quadrupole, distinct in units from the intensity Q above). In a comoving orthonormal Bianchi I frame,

`dot E=-E(H+S)`, `S=sigma_ab n^a n^b`, and `dot n=-sigma.n+S n`.

The angular velocity is `v=-grad_S2(S)/2`; because S is an l=2 spherical harmonic, `div_S2(v)=3S`. Angle-average the Liouville equation and integrate its angular advection by parts. Using `average(n_a n_b n_c n_d)=(delta_ab delta_cd+delta_ac delta_bd+delta_ad delta_bc)/15`, obtain

`(partial_t-H E partial_E)F = (2/15) sigma_ab (E partial_E+3)Q^ab + C_0`.

Here C_0 is the collision/source monopole. Higher multipoles do not enter this instantaneous monopole projection directly but affect quadrupole evolution. At first order about an isotropic background, its quadrupole satisfies

`(partial_t-H E partial_E)Q_ab = E partial_E F sigma_ab + C_<ab> + O(epsilon²)`.

Thus if shear and the induced quadrupole are both O(epsilon), the scalar spectral correction is O(epsilon²). Integrating the monopole equation with E³ and vanishing endpoint E⁴Q gives `dot rho_gamma+4H rho_gamma=-sigma_ab pi^ab+energy_source`, with `rho_gamma=4pi K integral E³F dE` and `pi_ab=(8pi K/15) integral E³Q_ab dE`; K is the fixed phase-space normalization containing the required hbar and c factors. The coefficient and sign agree by integration by parts: `integral E³(E Q'+3Q)dE=-integral E³Q dE`. Integrating the first-order quadrupole gives `dot pi_ab+4H pi_ab=-(8/15)rho_gamma sigma_ab+...`. These checks are analytical and were not executed as numerical tests.

If an independent finite Q is already present, shear variation can affect F at first order in shear, so the second-order statement requires the stated near-isotropic ordering. Likewise a polarized/aligned target admits an anisotropic cross section `sigma(n)=sigma0+A_ab n^a n^b`; its angular average includes `(2/15)A_ab Q^ab`. A density-matrix/atomic-alignment closure is then needed. Neither that closure nor collisionless photon evolution is implemented by the saved scalar prescribed-bath histories.

## Literature and remaining implementation obligations

Search date: 2026-10-29. Exa primary-paper search and SciSpace metadata search were used; tool service cost is unknown, not recorded as zero. No remote symbolic computation was needed.

1. Maartens, Ellis and Stoeger, *Limits on anisotropy and inhomogeneity from the cosmic background radiation*, Phys. Rev. D 51, 1525 (1995), https://arxiv.org/pdf/astro-ph/9501016 and https://doi.org/10.1103/PhysRevD.51.1525. Retrieved primary-paper excerpt gives STF occupation harmonics, pi_ab normalization, and linearized quadrupole equation with +(8/15)rho sigma on the left. It supports the normalization and first-order comparison; the nonlinear spectral monopole above is derived here from the stated Liouville equation.
2. Yan and Lazarian, *Polarization of Absorption Lines as a Diagnostics of Circumstellar, Interstellar, and Intergalactic Magnetic Fields: Fine-Structure Atoms*, ApJ (2006), https://doi.org/10.1086/508704. Retrieved abstract establishes anisotropic pumping changes ground-state sublevel populations and produces alignment. It identifies the physical boundary of a scalar isotropic-target model, not a proof that alignment is significant in these particular frozen species.
3. SciSpace returned Fano and Dill, *Angular momentum transfer in the theory of angular distributions*, Phys. Rev. A 6, 185 (1972), https://doi.org/10.1103/PhysRevA.6.185, and Busssert/Klar, *Production of polarized ions by photoionisation* (1983), https://doi.org/10.1007/BF01414058. Abstract-level contextual support only; full texts were not inspected and no numerical coefficients were adopted from them.

Next implementation contract: hold mean H(t), density, scalar atomic initial stocks, scalar source/escape parameters, spectral initial monopole, and error criteria fixed; specify shear initial data and photon quadrupole initial data separately. Evolve Q and its induced monopole correction consistently to the chosen perturbative order, then project the resulting J_nu through each threshold/cross section and drive the chemistry response. Fixing *the entire J_nu(t)* instead defines a useful null comparison with no scalar-rate response from Q alone. A self-consistent Einstein comparison would also change mean H at second order; label fixed-H work as a prescribed-background controlled experiment.

Remaining obligations are concrete: choose collisional Q damping/atomic polarization closure, bind the donor spectrum and units, inspect the actual angular transport implementation, implement frequency-boundary terms, and execute permitted convergence/conservation/rotation tests. The displayed scalar cancellation and spectral coupling are derived local results; no global DAG counts, physical-fast gates, new solver trajectory or novelty claim are promoted by this document.
