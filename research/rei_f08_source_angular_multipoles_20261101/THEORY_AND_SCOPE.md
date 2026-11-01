# REI Physical Fast F08 | Original-source photoionization/photoheat angular PSTF

Date 2026-11-01. REI owner base PR #359 head 2b44b1cbedd5ad2fd17e5f47cb32d95d967d14de, immutable for this branch. Donor BASS PR #323 head c0e965ba21892346feef9ecb2389932c34f3fc82, CI 41316296033 SUCCESS. Existing F08 source has 3840 direction/event records, 30 sampled histories, 15 times, two matched source backgrounds (S0_BI and S0_FLRW), 128 original midpoint rays per time. Original H/He matter and proper time are frozen. No native new IVP.

## New physical object

Let q_d be the original source 8 x 16 unit directions. X_d is the ORIGINAL per-direction source contribution to one of the following: H I photoionization rate (per H per s), photoelectron excess heating rate (eV per H per s), cumulative H I absorbed photon count (per H), or cumulative excess heat (eV per H). Sum_d X_d is the original source all-ray physical quantity; do not treat X_d itself as per-steradian intensity.

Define the original-grid matrix m_ij=(1/128) sum_d q_di q_dj and the normalized trace-free source response Q_ij[X] = sum_d X_d (q_di q_dj - m_ij)/sum_d X_d. The original finite angular quadrature has m_xx=m_yy=0.3359375 and m_zz=0.328125, not 1/3 for each component. Therefore use the EXACT discrete-grid centering above rather than delta_ij/3 to avoid fake isotropic quadrupole. The Qxx-Qyy component diagnoses x/y expansion response; Q_xy and trace are independent falsification checks. FLRW on the same grid should have zero Q within source precision.

Under prescribed Bianchi I ds² = -c²dt² + sum_i a_i(t)² dx_i² and H=(1.01,0.99,1)e-14 s^-1, E(q,t) = E0 sqrt(sum_i q_i² exp(-2 H_i t)), with initial E0=13.7 eV. Write H_i = Hbar + (s,-s,0), s=1e-16 s^-1. At the first original step t=6.25e8 s and fixed initial photon occupation, F(E)=sigma_HI(E) for ionization and F(E)=sigma_HI(E)(E-chi_HI) for excess heat. The leading quadrupole is Qxx-Qyy = -s*t*K*(d ln F/d ln E) plus source/absorption corrections, with K=< (qx²-qy²)² >_grid = 2185/8192 exactly. Verner 1996 H I analytic fit yields d ln sigma/d ln E = -2.6887263918990483 and d ln [sigma(E)(E-chi)]/d ln E = +132.1997293204128 at E0, chi=13.598434599702 eV. Wolfram checked predicted first-step ionization Qdiff=+4.482167943038498e-8 and heat Qdiff=-2.2037995038231047e-6.

Pre-block read-only independent source calculation on original BASS 3840 rows (not yet durable standalone replay): first original t=6.25e8s BI Qdiff(rate)=+4.4795698e-8, Qdiff(heat)=-2.2056383e-6. At BI tick800 (t=5e11s), rate Qdiff=+2.362868e-5 and heat=-4.828666e-3; at BI tick1600 (t=1e12s), rate Qdiff=-1.422110e-3 and heat=-1.887186e-3. These are sampled points, NOT a uniquely resolved continuous sign-crossing. A fixed H/He history is NOT a solved new chemical/thermal history. No CMB, Stokes, Thomson observer sky or Einstein-solved Bianchi claim.

## Provenance, owner gate, drift

BASS source angular gzip SHA256 370abc5b57c25497d8adfb2931428d04fcc84ff29a8621a8348e01d90a9c6a54, 3840 rows. Original time-history gzip SHA256 df1acb1bf78f2fc0e6d3a852cdfacedf1bc44e0909b870bebbacf8ce1cb302c4, 30 rows. Both are donor source artifacts, not reproduced in this Git branch before external readback. Their SHA must be checked on fetch before an authoritative full 120-row recomputation.

Current scoped owner decision: accept BASS #323 frozen-original-HHe angular photoionization/photoheat as a conditional donor; not original photon solver replacement, official F05 tick161, native full-Rust/26-event worker, or production. Original F05 official 160/131072. REI Central 28/88, Working 33/88 nonadditive, Physical Fast 4/7, canonical delta0. Production HOLD, F09 provider BLOCKED. Distinct-author referee and native subagent NOT_RUN; same-author analytic adversarial check detects 8x16 grid offset, sign convention, source/clock boundaries. Do not count source rows/CI as canonical nodes. Next critical action is native full F08 photon/HHe/OTS/thermal source-ownership closure or F05 authoritative 0→64 parity.

Literature: Verner et al. 1996, ApJ 465, 487 DOI 10.1086/177435; Fleury, Pitrou & Uzan 2015, PRD 91, 043511 DOI 10.1103/PhysRevD.91.043511.
