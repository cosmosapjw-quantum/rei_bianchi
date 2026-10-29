# BASS budget와 P19 6-moment가 동시에 주어진 양의 스펙트럼: 조건부 Li I 경계

## Source/geometry/units

Original BASS AtomicNetwork source in PR270: 71 fixed bin centres \(E_j\in[5,200]\) eV, bin-integrated local isotropic photon-number *flux* \(\Phi_j\ge0\) [m^-2 s^-1]. H I, He I, He II per-ion photoionization rates (s^-1), photoheating per target (eV s^-1), and Li I photoionization cross-section \(\ell_j=\sigma_{\rm LiI}(E_j)\) (m^2) follow the original cross-section formulas. **These are prescriptions for a gas-rest-frame optically thin bath, not radiation transfer or a directional Bianchi sky.**

\(M\in\mathbb R^{6\times71}\) has rates \(M_{i j}=\sigma_i(E_j)\) and heating \(M_{i+3,j}=\sigma_i(E_j)(E_j-I_i)\) (the latter vanishes below threshold). Original P19 2019 Table D1 model, PR261 13-knot projection with frozen nominal beta/kappa, supplies \(m(z)=(\Gamma_{HI},\Gamma_{HeI},\Gamma_{HeII},\mathcal H_{HI},\mathcal H_{HeI},\mathcal H_{HeII})\), on seven saved mean-z labels 2.4045...4.70169 only. It does **not** supply a P19 photon number or energy flux. PR270 proved \(M\Phi=m(z)\) is feasible and Li I upper unbounded because 5.392–13.6 eV bins are H/He-blind.

The **new exploratory assumption** is to fix two additional *scalar* flux moments to the exact original BASS source power-law photon budget at the same z label, without fixing the shape:

\[
N_B(z)=\sum_j\Phi^{BASS}_j(z),\quad W_B(z)=\sum_j E_j\Phi^{BASS}_j(z),\quad \Phi^{BASS}_j=Q_B(z)\Phi^{BASS,base}_j,\quad Q_B={1+\tanh[(7-z)/0.8]\over2}.
\]

N [m^-2s^-1]; W [eV m^-2s^-1]. **This is not an observation, not a claimed P19 budget, and does not import the old 300 K REI bath as BASS.** It is a controlled shape-only counterfactual with BASS number/energy budgets. BASS's original spectrum does not itself match all six P19 targets.

## Exact finite-dimensional conditional result

Set \(A=\begin{pmatrix} M\\ \boldsymbol1^{\!T}\\ \boldsymbol E^{\!T}\end{pmatrix}\), \(b=(m,N_B,W_B)\). For each fixed z, \(\mathcal F_z=\{\Phi\in\mathbb R^{71}_{\ge0}:A\Phi=b\}\). Since \(\sum\Phi_j=N_B\), \(\mathcal F_z\subset[0,N_B]^{71}\) is closed and bounded; whenever nonempty it is compact. Thus \(\ell^T\Phi\) attains **both** finite extrema. In fact the number budget alone implies \(\Gamma_{LiI}\le N_B\max_j\ell_j\); the energy budget independently implies \(\Gamma_{LiI}\le W_B\max_j(\ell_j/E_j)\), since \(E_j>0\). Both together can be more restrictive.

Compute the sharp discrete endpoints by paired LPs:

\[
\Gamma_{LiI}^{min}=\min_{\Phi\ge0,A\Phi=b}\ell^T\Phi,\qquad \Gamma_{LiI}^{max}=\max_{\Phi\ge0,A\Phi=b}\ell^T\Phi.
\]

The minimization dual is \(\max_\lambda b^T\lambda\) under \(A^T\lambda\le\ell\); maximization flips the objective sign. Each successful 8-row vertex needs at most 8 nonzero photon bins. The current source matrices actually yield 8 positive basic bins at each of both extrema for all seven labels. HiGHS selects bases; the *represented-binary64* matrices and associated duals are then independently reconstructed from each selected 8x8 basis with 75-digit mpmath. This certification is not a rigorous interval enclosure of the unrounded physical cross-section fits or UVB measurement uncertainties.

At z=3.6030195933, \(N_B=1.9947409\times10^{10}\) m^-2s^-1; \(W_B=2.5296663\times10^{11}\) eV m^-2s^-1. The sharp conditional source-discretized endpoints are \(1.14865279485\times10^{-12}\le\Gamma_{LiI}\le2.37750300760\times10^{-12}\) s^-1. Number-only equality gives [1.58204374698e-13,3.02886037515e-12] s^-1; energy-only gives [1.58204374698e-13,5.71403555712e-12] s^-1. No added budget gives [1.58204374698e-13,+inf). These are four different feasible sets, not contradictory calculations.

Even both scalar budgets do not identify one spectrum: 71 unknown nonnegative fluxes, 8 independent equality rows, typically a high-dimensional feasible polytope. Therefore **finite information diameter is not unique chemical source recovery**. BASS's original Li I photo-rate happens to fall inside the interval, but its six H/He moments do not equal P19. An in-interval observable never licenses full-source equivalence.

## Exact assumptions and physical limits

Freeze original BASS cross sections, photon-bin energies and BASS original N/W (computed from prescribed optical thin UV field), all 7 saved REI labels, and PR261 nominal Table D1 rate+heat interpolation. The H I/He I/He II ionization/heating 6-moment spectral constraints are exactly equalities in the finite bin model. All photon fluxes nonnegative. At real astrophysical resolution, source/UV emissivity, integral quadrature, redshift transport, chemistry/thermal feedback, original REI 300 K bath, Li6 isotope charge, nHref/nb/H/K and the full REI 17×17 Jacobian must be source-bound separately. No new IVP, optical depth, anisotropic angular transport, time-global posterior, or CMB likelihood is computed.

Source literature: Puchwein et al. (2019), *MNRAS*, DOI 10.1093/mnras/stz222, provides non-equilibrium fiducial UVB source, not fixed N/W observation. Grassi et al. (2014), DOI 10.1093/mnras/stu114 discusses chemistry/Jacobians and does not establish this model-specific budget. The finite LP construction and extremal numbers here are directly derived/checked from the pinned project sources.
