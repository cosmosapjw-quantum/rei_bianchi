# BASS_HE PR135 | Measured coherent π⁰ two-photon reinjection and 1958 fastD bounds

## Immutable lineage
Parent PR134 HEAD `241d8e90607ff7ff28ca643a8e39ae189bde3d19`; source-only, add-only exploratory comparison. No merge, no force push, no production activation.

The **binary ZIP in `archive/` is the byte-exact complete scientific artifact**: original readable Python source, EXFOR source catalogue inherited from PR134, 128 source-owned measurement/table rows, 826 derived conditional model rows, 20 fully detailed R/C stages, 5 PNG + 5 SVG science figures, test evidence, manifest and a runnable reproduction script. The 20 `stage_index/` files in this PR are **provenance index entries**, not claimed byte-identical clones of the detailed files in ZIP.

## Source-owned nuclear physics

Rambo et al., *Nucl. Phys. A* 660 (1999) 69–83, DOI 10.1016/S0375-9474(99)00383-8: EXFOR M0752019 measured coherent γ+⁴He→⁴He+π⁰ absolute cross section, 17 experimental rows; M0752002–M0752005 angular dσ/dΩ 101 measured rows over **partial** CM support. M0752001 reports common 7% systematic; measured E=206/216/229/241 MeV cross sections [150.0,174.5,212.6,260.3] μb with statistical errors [0.8,0.8,0.9,1.0] μb. Their numerical ratios to MacCormick1997 interpolated inclusive He4 photoabsorption are 0.20049/0.19852/0.20828/0.22648. **Cross-experiment inclusive detector coverage for fully coherent π⁰ NOT independently established:** conditional opacity interpretation only, not a proven partition.

TAGX M0384002 original four-nucleon fragmentation includes 8 measured rows and is not the coherent channel (155 MeV 0 ±26.3 μb is not proof of exact zero). JETP Gorbunov and Spiridonov (1958), *Sov. Phys. JETP* 7 (4) 600–605, Table II gives *mean three-body deuteron momentum* p_D=124,190 MeV/c in bremsstrahlung bins 25.9–75 and 75–170 MeV, respectively, not 220MeV DD. Convexity of relativistic kinetic energy gives Jensen floors ⟨K_D⟩≥4.094458 and9.598958 MeV, respectively.

## Kinematic calculation (local stationary He4)

Let μ_A=M_A c², μ_π=m_π c². (s=μ_A²+2μ_AE_γ), (E^*_{π}=(s+μ_π²-μ_A²)/(2√s)), (p^*c=√(E^{*2}_π-μ_π²)). At production CM angle cosθ=u, pion laboratory energy (E_{π}(u)=γ_{CM}(E^*_{π}+β_{CM} p^*c u)); alpha recoil (T_α=E_γ-E_π). Conditional on π⁰→γγ (PDG B=0.98823), daughter energy is uniform in [((E_π-p_π c)/2,(E_π+p_π c)/2)] and two daughters sum to E_π. 

Use measured angular support only for source-conditioned (K_π(ε|E_γ)=2B int_{m support} w(u),{f1}_{ε∈[ε_-,ε_+]}/(ε_+-ε_-),du), where w is explicitly normalized over the measured angular interval rather than a fabricated full-sky distribution. The local first-collision injection (mathcal J_γ^{(1)}=P_π^{(1)}K_π) uses (P_π^{(1)}=c n_α σ_π/(Gamma_{BW}+Gamma_{BH}+Gamma_{KN}+c n_α σ^{EXFOR}_{abs})). This fraction is conditional on inclusive coherent coverage. No follow-up collisions, plasma heat or full cosmological emissivity.

At 216 MeV, z=10⁴, P_π^(1)=0.000948075067; exact all-angle kinematic expected number of E>150 MeV daughters per produced π⁰ lies in [0.29913913,0.49302702]. Their first-hit production per injected photon therefore lies in [0.000283606,0.000467427], and measured-support angular proxy is 0.000399873. All E<150 MeV daughters remain **untracked photons**, NOT heat. E_gamma (incident) is shared between pion rest/motion and surviving alpha recoil.

## Evidence and limitations
Measured source rows 128 (17 pion total +101 angular +8 2p2n +2 JETP momentum bins) are original-source observations already in PR134 provenance, not freshly performed experiments. 826 new derived conditional physical rows (200 daughter spectra,600 local first-hit spectra,26 auxiliary), five original PNG/SVG pairs. Python new 23/23 normal and 23/23 -O, PR134 17/17, manifest 62/62, fresh ZIP restore same tests, generated outputs 21/21 byte-identical. A same-author adversarial audit is included; true independent author R6/C9 and native subagents NOT_RUN. Browser extension unavailable due originating browser context, GitHub and published source tools used directly.

## Hold
Central DAG **28/88**; HE Physical **14/18**; scoped micro **1/1**, canonical physical delta **0**; `kappa=null;R_event=null;heat_rate=null;L4=false;PRODUCTION=HOLD;NO_MERGE=true;NO_FORCE_PUSH=true;AUTO_NEXT_NODE=false`. Rice-Schiff normalization and last-row SD remain CONCERN. Need true source-owned gamma emissivity, measured full-angle pion distributions and inclusive acceptance matching, photons 2.2–150MeV, e±/IC cascade, deuteron full ion/nuclear slowing and heat.

## Recovery
Download exact archive binary and verify ZIP SHA-256 `04eb168f9a275450a559c6c18090fc2890cfdf36ba6bfbdd60272962fb157d52`, then run `cd research/he_dd_pi0_reinjection_20261031 && bash REPRODUCE.sh`. Detailed stage files are inside ZIP under `stages/`.

References: https://arxiv.org/abs/nucl-ex/9907020 ; https://doi.org/10.1016/S0375-9474(99)00383-8 ; https://doi.org/10.1103/PhysRevC.55.1033 ; https://pdg.lbl.gov/2025/tables/rpp2025-sum-mesons.pdf .
