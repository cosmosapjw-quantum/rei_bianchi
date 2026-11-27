# PR126 research note: Rice 2000 measured-angular birth kinetic atlas

## Source and identity

Parent BASS_HE PR125 HEAD b7a3f7e7f3eb2461ff75039797c085296e575acb, PR124 HEAD 9696297205c2560bd8bdfc8d72b8b80b86fae8d3. Original Table I source is one Rice et al. (2000) experiment at 6 effective CM angles × 2 incident photon energy bins, 12 measured absolute DA values and statistical SD; two systematic fractions 7.1% and 13%. Source JSON Git blob 9cdec4449b22bdba2797bbdfb815e98901b85636 (exact) and SHA256 dd29c7b492162b257b6b9674792c2db5cf65c98921cbea088a9283ea641bc03a. DOI 10.1103/PhysRevC.61.064612. Alternative 8 Table II fits and 6 thesis preliminary rows are NOT additional independent experiments. Source-internal discrepancy in Table II unconstrained P2 150-190 MeV preserved in parent; not used to compute this atlas.

## Exact relativistic derivation

Metric signature (-,+,+,+); photon energy E=E_gamma measured in the alpha nucleus rest frame; 4-velocity U_alpha·U_alpha=-c²; E_gamma=-U_alpha·p_gamma. Frozen nuclear rest energies \(\mathcal M=M_\alpha c^2=3727.3794118\,\mathrm{MeV}\) and \(\mathfrak m=m_d c^2=1875.61294500\,\mathrm{MeV}\). In MeV-rest-energy notation \(s_E=\mathcal M^2+2\mathcal M E\) is the squared COM rest energy; \(q_*c=\frac12\sqrt{s_E-4\mathfrak m^2}\), \(\beta=E/(\mathcal M+E)\), \(\gamma=(\mathcal M+E)/\sqrt{s_E}\). Define \(Q=2\mathfrak m-\mathcal M=23.84647820\,\mathrm{MeV}\), \(\mu=\cos\theta_{\rm CM}\), and \(\Delta(E)=E q_*c/\sqrt{s_E}=(E/2)\sqrt{1-4\mathfrak m^2/s_E}\).

A back-to-back pair with CM four-energies \(\sqrt{s_E}/2\) has alpha-frame kinetic energies

\[
K_\pm(E,\mu) = (E-Q)/2\;\pm\;\Delta(E)\mu.
\]

Thus exact pair kinetic sum \(K_++K_-=E-Q\), unordered high/low energies \(K_{\mathrm{high/low}}=(E-Q)/2\pm\Delta|\mu|\), and the two-daughter *population variance* around the mean is \(V_K=\Delta^2\mu^2\). This variance is the variance among two birth energies for ONE event at one E and one CM angle: it is not the variance of Rice's photon ensemble or of deposited thermal energy. Four-momentum conservation and daughter mass shells are tested in code using \(p_zc=\gamma(\pm q_*c\mu+\beta\sqrt{s_E}/2)\) and \(p_\perp c=q_*c\sqrt{1-\mu^2}\).

For source bins 150–190 and 190–250 MeV, all high/low daughter kinetic-energy extrema at a *fixed* effective CM angle are the two energy endpoints. A sufficient analytic certificate is

\[
2\Delta'(E)=r(E)+\frac{4\mathfrak m^2\mathcal M E}{s_E^2 r(E)},\quad
r(E)=\sqrt{1-4\mathfrak m^2/s_E},\quad
2\Delta'(E)\le r(E_{\max})+\frac{4\mathfrak m^2\mathcal M E_{\max}}{s_{E_{\min}}^2r(E_{\min})}<1.
\]

Therefore both \(K_{\rm high}\) and \(K_{\rm low}\) increase with E within either bin; the pair variance is nondecreasing. Since the published \(\theta_{\rm CM}\) values are effective *bin* angles and underlying energy-angle acceptance is unavailable, the certified intervals are **conditional on fixed reported effective angle** and are NOT claims about a measured event-level angular distribution.

## A source-conditioned first-moment constraint

If the experiment's reported \(\bar D_i\) truly equals \(\int_{B_i}w_i(E)D(E,\theta_i)dE\), with \(w_i(E)\ge0\) normalized and the same angle/acceptance in both expressions, then

\[
\bar D_i (E_{\min}-Q)\le\int_{B_i}w_i(E)D(E,\theta_i)(E-Q)\,dE\le \bar D_i(E_{\max}-Q).
\]

The numerical bounds have units nb MeV/sr and are **not measured heating cross sections**. The separate 1-sigma statistics envelopes are illustrative independent input bounds, not any multi-row confidence region; the true 12×12 covariance is unknown. If Rice's acceptance or energy weights are angle/E dependent in a different manner, this inequality cannot be transferred to other photon environments without an explicit forward-folding response.

The full-sphere identical daughter convention is unchanged: \(\sigma_{\rm event}(E)=\frac12\int_{4\pi}(d\sigma_{\rm photo}^{\rm ordered}/d\Omega_{\rm CM})\,d\Omega_{\rm CM}\). The 12 angles are not sufficient to perform a model-free integral over 4π. Rice Table II reports alternative model fits, which are kept separate. No extra 1/2 is inserted in individual Table I DA rows.

## Missing physical history and correct observer contraction

For scalar photon distribution f_gamma(x,p), the alpha-comoving photon energy \(E_\alpha=-U_{\alpha\mu}p^\mu\) and its local number density spectrum \(n_\gamma^{(\alpha)}(x,E,\Omega)\) are required. With unpolarized and isotropic target response, \(R_{\rm event}/V=n_\alpha c\int dE\,d\Omega\;n_\gamma^{(\alpha)}\sigma_{\rm event}(E)\); this is unpopulated because the relevant alpha-frame 150–250 MeV history, target \(n_\alpha/U_\alpha\), and exclusive energy dependent \(\sigma(E)\) are not source-qualified. Photon frequency shifts, geometric time samples and angular acceptance cannot be replaced by Fermi-LAT IGRB observed at a different epoch. Nonthermal D-fast stopping, inelastic losses, escape and the medium heat capacity remain separately unpopulated, hence heat_rate=null and L4=false.

## Literature and source limitations

- Rice et al., *Phys. Rev. C* **61** (2000) 064612, DOI 10.1103/PhysRevC.61.064612, one direct coincidence experiment.
- R. J. Protheroe, T. Stanev, V. S. Berezinsky, *Phys. Rev. D* **51** (1995) 4134, DOI 10.1103/PhysRevD.51.4134: EM cascade calculations in the early universe; not a BASS_HE model-specific photon history.
- V. Poulin and P. D. Serpico, *Phys. Rev. D* **91** (2015) 103007, DOI 10.1103/PhysRevD.91.103007: energy dependent nonuniversal BBN photon cascades; no observed BASS_HE source spectrum.
- S. K. Acharya and R. Khatri, *Phys. Rev. D* **99** (2019) 043520, DOI 10.1103/PhysRevD.99.043520: nonthermal electromagnetic energy deposition; not a source-specific fast-deuteron stopping kernel.
- NIST ESTAR/PSTAR/ASTAR database (DOI 10.18434/T4NC7P) tabulates electrons/protons/helium ions, *not deuterons*. It must not be silently used as a deuteron stopping source.

Decision: new Rice-measured-source-conditioned 12-row high-energy fast-D atlas is a real derived physics product. This is an auxiliary physical-data bridge, not completion of the canonical source-qualified spectrum × He photon history node. Its status is **PARTIAL**, canonical central 28/88 and HE physical 14/18 unchanged, kappa/R_event/heat_rate=null, L4=false, production HOLD.
