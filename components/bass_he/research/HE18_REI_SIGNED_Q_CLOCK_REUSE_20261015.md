# BASS_HE -> rei_bianchi signed-q Thomson-depth and photon-quadrupole cross-check
2026-10-15 KST. This is a downstream read-only bridge, not a warm HE18 source-ODE result.

## Exact identities
- Cold source identity for all 5 original signed 200001-row prefixes: d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185.
- New rei_bianchi branch research/bass-he-optical-depth-transfer-20261015 at verified commit 4a370c413d842bc261dc0b3f910010da74ae26e3, with complete code, unit tests, result JSON and SVG.
- Previous existing AX08 analysis signed_prefix_parity.json is reused, matched to all 5 original history SHA256s. Its saved J2 moment is sum N*E*P2(mu_current), not directly CMB polarization.
- Warm HE18 FT03/HM12 16-cell archive source SHA256 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d belongs to a different thermal/helium/photon convention; no warm tau is transplanted.

## New cold numerical finding
- At common mean scale factor a=0.08873654701704167 (zbar=10.269313869), tau_ZERO=0.00307215160948680604.
- E_tau(0.005)=-2.76081465256e-8, E_tau(0.01)=-1.10428864310e-7; ratio 3.99986519225, consistent with a leading q^2 scalar response on the stored histories.
- Tau odd half-differences are ~1e-18 and NOT physical detection.
- A common proper-time decomposition using t*=min_q[t_q(a)] yields for q=0.005 a fixed-time E=-2.64609998416e-9 and endpoint-clock E=-2.49620465414e-8; clock fraction 0.90415510213. This is an algebraic reference-dependent separation, not causal independent microphysics.
- Reused AX08 J2 odd moment endpoint -2.667171197077781e-12 eV/H for q=0.01, -1.3335886533020386e-12 eV/H for q=0.005; about q-linear, while tau is q^2-leading.
- Original AX08 convention ds^2=-c^2dt^2+a^2exp(-2b)(dx^2+dy^2)+a^2exp(4b)dz^2. Any alternate beta notation must explicitly set beta=-b and distinguish reference-covector from current physical ray direction.

## Measured engineering outcome
- 30/30 local Ubuntu tests PASS; 5-input single worker end-to-end source CSV read+SHA+tau 8.0734s, two-worker 4.8837s (1.6531x) with identical case JSON.
- Five original prefix files combined 601988551 bytes; provenance-bound NPZ caches 26389839 bytes (22.8114x smaller). Cache re-read 0.155s vs source scan+parse sum ~7.185s; not a Rust solver speedup.
- Compressed code and cache copied twice to ~/archives/BASS_HE_REI_TRANSFER_20261015_1445KST and Dropbox/BASS_DERIVATION_DOSSIERS_20260912/HE18_REI_TRANSFER_20261015, matched SHA256.

## Scientific admission
Only SOURCE_SCOPED_NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED; original 5 native histories STOPPED_CHECKPOINTED with scientific_admission NOT_ISSUED. No ODE global error bound, no direction-dependent CMB tau or polarized Thomson prediction, no physical shear-detection claim. Source-correct refinement needs native time-step/tolerance convergence and goal-oriented tau uncertainty before any publication-level sign response claim.

Key delivery: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/bass-he-optical-depth-transfer-20261015/research/bass_he16_transfer_20261015

Literature underpinning H/He ionization closure: Friedrich et al. (2012), Radiative transfer of energetic photons: X-rays and helium ionization in C2-Ray, MNRAS 421:2232, https://academic.oup.com/mnras/article/421/3/2232/1077406 .