# HE-DD PR124: source-owned Pitts (1989) absolute capture and corrected reciprocity

## Original source and evidence grain

Pitts et al., Physical Review C **39**, 1679 (1989); DOI https://doi.org/10.1103/PhysRevC.39.1679. Frozen IAEA-NDS/exfor_master commit 939a14d7bba1ddce51975cb5e8711ce96b3b0871, exforall/C06/C0621.x4: 3269 bytes, SHA-256 9c3b49e979e9bb389b2e046e33dec3eb95ebbbed9772a3a47391d5529aaac2ea, Git blob ddeb728a59905ca669b3408e9338b8d300d5c96e. EXFOR author-approved. Incident deuteron T_lab=95 MeV on a stationary deuteron.

Three source-owned subentries: C0621002 has 8 absolute unpolarized capture differential cross sections (NB/SR), C0621003 8 dimensionless vector analyzing powers (Ay), C0621004 8 dimensionless tensor analyzing powers (Ayy). These are 24 measured experimental rows in one experiment, not 24 experiments. C0621002 DATA-ERR includes some statistical and systematic uncertainties but excludes an additional 4% common normalization uncertainty. The full residual angular covariance, correlation between polarimetry and DA, and detector acceptance are unavailable. Keep the scales distinct.

Original capture C0621002 (theta_cm, DA, DATA-ERR) in (degrees, nb/sr, nb/sr):
(55,2.02,0.14);(70,0.98,0.08);(90,0.21,0.02);(99,0.36,0.04);(116,1.26,0.10);(126,2.13,0.15);(140,2.40,0.18);(149,2.44,0.17).
These are eight sparse angles, not a full 4π measurement.

## Kinematics, units, and angular conventions

Metric (-,+,+,+), c retained. Freeze PR104 rest energies m_d*c^2 = m = 1875.61294500 MeV and M_alpha*c^2 = M = 3727.3794118 MeV. Positive invariant energy squared:
s = 4 m^2 + 2 m T_d = M^2 + 2 M E_gamma^(alpha-rest).
Thus E_gamma^(alpha-rest) = (s-M^2)/(2M) = 71.72664743398931181 MeV. Q = 2m - M = 23.84647820 MeV.
The center-of-mass momentum-times-c values (both MeV):
q^2 = (s-4 m^2)/4; k^2 = (s-M^2)^2/(4s).
q = 298.4821852096034 MeV, k = 70.38500277159159 MeV, both positive above threshold.

## Detailed-balance direction correction: specific upstream defect

Assume unpolarized d+d and gamma+alpha states, time-reversal invariant spin-summed transition amplitude S, correctly time-reversed CM angles, deuteron spin multiplicity 3 and photon helicity multiplicity 2. Let C=1/(64*pi^2*s), with the common physical unit factor restored for actual cross sections. For dd->alpha+gamma capture:
f = C (k/q) (S/9).
For gamma+alpha->d+d ordered/outgoing-inclusive-D differential density:
r_ord = C (q/k) (S/2).
Therefore r_ord/f = (9/2)*(q/k)^2 = 80.92618747566492416. The reciprocal f/r_ord = (2/9)*(k/q)^2 = 0.01235693946784169289.

BASS_HE PR107 THEORY_KO.md presents the same definitions of f and r_ord but calls the latter reciprocal f/r_ord factor an inverse/forward factor. Its function conditional_inverse_DA applies f/r_ord to already measured forward photonuclear M0475 data; that is a CONDITIONAL CAPTURE predictor in the stated conventions, not newly measured inverse. Do not relabel upstream measurements. No upstream PR was edited by this study.

If the ordered/inclusive-D full-sphere angular density is converted to an event-counted density for two identical outgoing D particles, use one distinct final-state 1/2!: r_event,full = r_ord/2; hence r_event,full/f = (9/4)(q/k)^2 = 40.46309373783246208. An initial identical d+d homogeneous collision pair-rate factor 1/2 is separate; never double apply. Actual detector event/inclusive count convention remains unverified; expose both conditional branches.

## Source-owned covariance and daughter energy

For eight source values y_i, one correlated four-percent scale component is C_norm,ij = (0.04)^2 y_i y_j in (nb/sr)^2, subject to its interpretation as a common experimental scale. Residual covariance UNKNOWN; no diagonal fill assumption. The common component cancels in DA(90)/DA(149)=21/244, but complete ratio uncertainty remains unknown.

Conditional 55-degree ordered photonuclear DA is 2.02*80.9261874756649 = 163.470898700843 nb/sr, and event full-sphere density 81.735449350422 nb/sr. At 90 degrees these are 16.994499369890 and 8.497249684945 nb/sr. These are source-derived time-reversal predictions, NOT measured Rice DD photodisintegration data.

For an alpha target initially at rest, two daughter kinetic energies at correctly related CM angle mu are
K_plus/minus = (E_gamma-Q)/2 +/- (E_gamma*q/sqrt(s))*mu.
The sum E_gamma-Q = 47.88016923398931181 MeV is exact. Eight evaluated pairs respect exchange symmetry and this sum; no physical energy deposition follows without gamma phase-space density and nonthermal stopping.

## Claim gate

SOURCE ORIGINAL: 24 measured rows, one campaign, author-approved EXFOR. DERIVED: exact matched s, spin phase-space ratio, 8 conditional photonuclear DA pairs and 8x8 common-normalization covariance component. NUMERIC CHECK: Python targeted 16/16; Wolfram exact invariant and detailed-balance reciprocal identities. NOT VERIFIED: Rice original 12 numeric photodisintegration DA, experimental event convention, full angular covariance, detector response, source-owned gamma field, D_fast stopping/deposition, actual thermal heat. Central 28/88; HE physical 14/18; source-only scoped 2/2; physical delta 0; kappa=null; R_event=null; heat_rate=null; L4=false; production=HOLD. Distinct-author R6/C9 NOT_RUN.
