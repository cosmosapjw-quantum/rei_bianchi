# BASS_HE: source-owned EXFOR cross sections, measured-inclusive alpha absorption, 1958 integral constraints

**Scope**: source-observation gate and *local* FLRW first-collision coefficients, not full cosmological gamma injection/cascade and not a canonical DAG node. Parent immutable `cosmosapjw-quantum/BASS_HE` Draft PR #133 HEAD `a1a3e1883533abb5dbbafee4259706a12ea920cf`.

## Actual experimental-source outputs

IAEA EXFOR source request **10461**, 2026-10-31, original standard-text SHA-256 `09df36e79f6c050dd7b0c6ae434805a4957bedd2e5a7132479c1c94daa90dd5d`: **84 subentries, 2270 numerical rows**. These are NOT 2270 independent observations: different cross sections, asymmetry, curve digitizations, duplicate archive revisions and derived entries coexist. The reproducible source catalog preserves original ordered columns/units rather than converting every row to a cross section.

Direct source-owned total exclusive cross sections in 150–250 MeV:

| EXFOR | reaction | E (MeV) | sigma | stat | supplied systematic |
|---|---|---:|---:|---:|---|
| M0475003 | 4He(gamma,d)d | 201 | 2.41 nb | 0.32 nb | not reported, NOT zero |
| M0475003 | 4He(gamma,d)d | 225 | 1.29 nb | 0.23 nb | not reported, NOT zero |
| M0484003 | 4He(gamma,p)T | 223 | 3.52 microbarn | 0.24 microbarn | 5% correlated across source energy rows |
| M0484003 | 4He(gamma,p)T | 239 | 3.04 microbarn | 0.22 microbarn | 5% correlated across source energy rows |

`M0475003` is Arends et al., *Phys. Lett. B* **62**, 411 (1976), DOI `10.1016/0370-2693(76)90671-7` (original paper Table 2). `M0484003` is Arends et al., *Nucl. Phys. A* **322**, 253 (1979), DOI `10.1016/0375-9474(79)90425-1` (original Table 3). Both EXFOR raw entries were corrected in 2016; use their present reported fields.

Measured **inclusive nuclear photoabsorption** (do not identify with any exclusive channel) `M0520002`: MacCormick et al., *Phys. Rev. C* **55**, 1033 (1997), DOI `10.1103/PhysRevC.55.1033`; 204: 722 ±2(stat) ±23(sys) microbarn, 216: 879 ±3 ±25, 228: 1010 ±3 ±27, 240: 1139 ±3 ±30. The older `M0546002` represents the *same publication*, not new observations: 53 exact triplet matches; three 1-MeV adjusted energies (723→724, 731→732, 747→748); one additional point at 395 MeV in the 2025-updated `M0520002` (57 vs 56). Use M0520 only.

Other scientifically distinct measured inputs in the attachment: 87 `L0138002` neutral-pion-production points at 150–250 MeV (actually concentrated 150–159.9 MeV), 3 `M0384002` 2p2n points, and 13 `G4081002` dimensionless pT angular polarization asymmetry points (120–250 MeV; EXFOR compiler intentionally **negates the authors' convention**). The pion and polarization entries are NOT substitutions for alpha->npD or dd cross sections, and repeated-energy pion entries are not silently independent.

**Original 1958 scan**: Gorbunov and Spiridonov, *Soviet Physics JETP* **7** (1958) p.600–605, ZhETF 34, 866–873 (1958), Table I on printed p.601; exact user PDF SHA-256 `7cb9676493bfc68579e0ff015cc841c4f0d1a8b0c70b1e8b22a0ce90cc36b420`. On **75–170 MeV**, integrated cross sections in MeV mb are `npD=4.6±1.2` and `pT+nHe3=10.0±1.9`, statistical errors only. Independent direct integration of published Cyburt (2003) Appendix A forms over the same interval gives 2.8092605184 and 7.6476467328 MeV mb. These are comparisons of integrals, NOT monochromatic measured high-E σ. The `<75`, `75-170`, `<170` table rows overlap and are *one source*, never treated as independent statistics. For EXFOR M0999002 (same historical source family), `#YEAR=1957` conflicts with the scanned journal source (1958); keep provenance concern, not a changed physics value.

## Direct measured-source versus old model

- pT Cyburt(2003) high-E-extrapolated function: obs/model at 223 MeV **0.9475336396**, at 239 **1.0361561778**. The experimental agreement at two points does not validate the whole high-E excitation function.
- dd Rice(2000) **broad-bin angular-fit source surrogate** (4.34 nb over 190–250 MeV) versus Arends(1976) 201: **0.5552995392**, 225: **0.2972350230**. Different source protocols, wide-bin-to-pointwise usage and unreported systematic uncertainty prevent a simple published-result contradiction claim.
- Polarized G408 compiler-signed near 90 degrees: at 150 MeV −0.8418±0.0495, at 250 −0.3063±0.0495, difference +0.5355 in the compiler sign; the angle differs by 0.918°, source covariance unknown, measured via digitized curve; **not an absolute rate or a formal significance claim**.

## New physical model: source-owned local first hits

Flat homogeneous fully ionized reference FLRW, signature (−,+,+,+), c, hbar, k_B explicitly retained in inherited code. Only for EXACT measured E and selected z=(1e4,1e5,1e6): for measured channel j, Gamma_j = n_alpha(z) c sigma_j^EXFOR(E). All *nonmeasured* rates stay prior-model `BW + KN + BH` plus Cyburt(2003) pT/nHe3/npD and Rice DD as applicable.

For the first, partially measured nuclear variant, the pointwise local hazard

`P_first,j = Gamma_j^measured / (Gamma_BW+Gamma_KN+Gamma_BH+Gamma_alpha_other_model+Gamma_j^measured)`

is a local first-collision branching fraction, NOT full redshift/cascade probability. Since old alpha channels are extremely incomplete, a stronger second variant **substitutes measured total nuclear photoabsorption** for all alpha loss:

`P_first,j^incl = n_alpha c sigma_j^meas / (Gamma_BW+Gamma_KN+Gamma_BH+n_alpha c sigma_abs^interp)`,

where `sigma_abs^interp(E)` is linear interpolation only **inside directly bracketed 204/216/228/240 MeV MacCormick points**; source-cross-experiment interpolation is explicitly a model step, not a measured point. For 223 MeV, interpolated sigma_abs=955.4166667 microbarn and sigma_pT/sigma_abs=0.0036842564. For 225 MeV, interpolated sigma_abs=977.25 microbarn and sigma_dd/sigma_abs=1.3200307e-6. The old four-alpha-channel model sum at these energies is ~1% of measured inclusive total (model-dependent gap ~98.95%–99.28%), with omitted pion and multiparticle nuclear processes. **Do not interpret the residual as a measured particular missing exclusive channel.**

Nuclear absorption timescale is not Hubble heat, no injected gamma source q_gamma(E,z,x,n), no full EM e± inverse Compton regeneration, no 2.2–150 MeV spectral transport, no full nuclear fast-D stopping. `kappa=null`, `R_event=null`, `heat_rate=null`, `L4=false`, `PRODUCTION=HOLD`; Central DAG **28/88**, HE physical DAG **14/18**, canonical physical delta **0**.

## Output provenance and reproducibility

- Source-typed `data/EXFOR_INVENTORY_84.csv` and `EXFOR_CATALOG_2270.csv` are catalogues, **not 2354 admitted independent measured observations**.
- Real measured source tables, inferred source/model comparisons, 12 partially measured local FLRW physics rows and 9 measured-inclusive local FLRW physics rows, 1958 integral comparisons, error/correlation notes, and **five new science plots PNG+SVG**.
- Self-review R06/C09 (same author): test the channel normalization and numerator/denominator identity, no fake distinct-author claim. Native subagents NOT_RUN where host delegation unavailable.
- Full private ZIP contains original EXFOR raw and uploaded Gorbunov PDF with exact SHA-256, preserved original PR133/PR132 Python physics dependencies. Public Git adds only this new unit, **without** public redistribution of the scanned original JETP PDF or browser-exported HTML.

Reproduce from full ZIP root: `python research/he_dd_exfor_measured_20261031/src/generate.py`, followed by `cd research/he_dd_exfor_measured_20261031 && PYTHONPATH=src python -m unittest discover -s tests -v`. `src/generate.py` requires exact attached input in `private_source/`. Git-only checkout needs to restore these from the verified source ZIP; it cannot legitimately regenerate 1958 table claims from an absent original PDF.
