# HEANG next4 focused source intake — 2026-10-25

## Result and scope

The restored author preprint fixes the conventions needed for a **direct, fixed-proton Coulomb–Born candidate**. Its printed Eq19 is usable as a source-defined integral identity. The hydrogen 1s overlap, scalar amplitude normalization, branch convention, exchange construction and applicability decisions remain the root's derivation/contract work. This intake executes no science code, numerical special function evaluation, tests, physics run or independent scientific review. Prior PR99 science and delivery files remain unchanged.

Workflow: physmath-research-loop builtin1.0.0, R2 source/reuse. RESEARCH_POLICY, THEORY_LOOP and EVIDENCE_AND_HANDOFF were actually read. Prior next3 SOURCE_REPORT and PR99 unit HANDOFF were read and their established scope and access failures reused.

## Primary identity

Y. Attaourti, S. Taj and B. Manaut, *Exact semi-relativistic model for ionization of atomic hydrogen by electron impact*, arXiv:physics/0411013v2, 2 November2004. Actual read-only download: https://arxiv.org/pdf/physics/0411013 . 326595 bytes, SHA256 `b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1`; exact prior source identity restored. Private PDF and pdftotext extracted text are present. Pages3,4,7 rendered and visually inspected.

Related publication: *Semirelativistic model for ionization of atomic hydrogen by electron impact*, Phys.Rev.A71,062705 (17June2005), https://doi.org/10.1103/PhysRevA.71.062705 . Fresh Exa fulltext request to the publisher PDF returned `CRAWL_HTTP_401`. Prior direct publisher403 is retained as historical access failure. No equation equivalence to the published version, correction or erratum is asserted.

## Exact positions and conventions

The following are transcriptions or compressed descriptions of the preprint, not a claim that every printed intermediate identity is correct.

| Position | Source fact | Use/limit |
|---|---|---|
| p2 Eq1 preceding sentence | Direct channel; exchange effects explicitly neglected | Supplies no exchange amplitude or identical-electron event-count rule |
| p2 Eq2 | `V_d=1/r_12−1/r_1` | Fixed proton coordinates; direct electron-electron plus projectile-proton interaction |
| p2 preceding Eq3 | Projectile plane waves `u(p,s)exp(−ip·x)/sqrt(2EV)` | Source uses volume-normalized Dirac spinors |
| p2 Eqs5–7 | Bound spinor upper radial part `N_D exp(−r)/sqrt(π)`; `N_D=2c/sqrt(4c²+1)` | NR radial factor has no extra1/r |
| p2 Eqs8–9 | Continuum ket prefactor `exp(πη_B/2)Γ(1+iη_B)exp(ip_B·r)`; Coulomb factor `1F1(−iη_B;1;−i[p_Br+p_B·r])`; `η_B=E_B/(c²p_B)` | Sommerfeld–Maue correction included in source; NR identification η=1/p requires the stated limit |
| p3 Eq12 | Same ket plus `i(α·p_B+p_B α·rhat)/(2cp_B) 1F1(1−iη_B;2;−i[p_Br+p_B·r])` | Visually confirmed; unnecessary for a scalar NR-only candidate |
| p3 Eqs13–15 | Bra prefactor `exp(πη_B/2)Γ(1−iη_B)`; bra factor `1F1(iη_B;1;i[p_Br+p_B·r])`; plane factor `exp(−ip_B·r)`; transfer factor `[exp(iΔ·r)−1]` | Δ=p_i−p_f; no finite-proton recoil term |
| p3 Eq13 | Energy delta `δ(E_f+E_B−E_i−ε_b)` and prefactor `8π²/Δ²` with source spinors | Not a standalone scalar NR TDCS normalization |
| p3 Eqs15–17 | `H_1(Δ−p_B)−H_1(−p_B)`; `H_1(q)=∫d³r exp(iq·r)1F1(iη_B;1;i[p_Br+p_B·r])φ^(±)(r)` | The integral definition contains the bound state itself, no separate1/r |
| p4 Eq18 | Upper overlap printed with `exp(−r)/r` | Literal discrepancy with Eqs5–7/16; visually reconfirmed, not OCR-only |
| p4 Eqs20–21 | Angular factors obtained using `−i/r` times q derivatives | Spinor angular manipulations, not permission to insert1/r into NR scalar overlap |
| p4 Eq26 | Incident and target spin averages1/2 each; outgoing spins summed | Direct channel spin prescription; exchange still omitted |
| p4 Eq27 | TDCS in `dE_B dΩ_B dΩ_f`; prefactor `(|p_f||p_B|/|p_i|)exp(πη_B)|Γ(1−iη_B)|²/[64c^6π³Δ^4]` times squared sum of source tilde amplitudes | Requires source spinor amplitude conventions; root must derive normalized NR scalar conversion |

### Integral authority

Preprint p4 Eq19, repeated p7 EqA9:

\[
I(\lambda;\mathbf q,\mathbf p)=\int d^3r\,e^{i\mathbf q\cdot\mathbf r}\frac{e^{-\lambda r}}r
{}_1F_1(i\eta;1;i[pr+\mathbf p\cdot\mathbf r])
=\frac{4\pi}{q^2+\lambda^2}\exp\!\left[i\eta\ln\frac{q^2+\lambda^2}{q^2+\lambda^2+2\mathbf q\cdot\mathbf p-2i\lambda p}\right].
\]

The source uses a logarithm but supplies no explicit global branch algorithm. For a bound overlap without1/r, differentiating with respect to λ is a root derivation obligation. Call the derivative overlap K or F: **the paper's J already means another integral**, p4 Eq28/p7 EqA10, with hypergeometric parameters `(iη+1;2)` and a `2F1` expression. Equating source J with `−∂λI` would miscite it.

### Bibliographic and appendix corrections

The actual reference attached to Eq19 is **[16] H.S.W. Massey and C.B.O. Mohr, Proc.Roy.Soc.A140,613 (1933)**, printed p8. It is not Nordsieck1954. The source Appendix p7 A1–A9 reproduces Eq19 using parabolic-coordinate and Laplace-integral manipulations and cites [20] Landau/Lifchitz. The appendix has a literal intermediate sign issue: A1 prints `exp(+iQ·r)exp(−ip_B·r)`, while A7 prints `−Q=q+p_B`. These exponent conventions do not algebraically identify the same q as written. Preserve the Eq19/A9 endpoint identity and derive its conventions independently; do not assert all appendix steps were verified.

Exa primary APS metadata independently identifies A. Nordsieck, *Reduction of an Integral in the Theory of Bremsstrahlung*, Phys.Rev.93,785–787 (1954), DOI https://doi.org/10.1103/PhysRev.93.785 . Its stated object is a two-Coulomb bremsstrahlung/pair-production matrix integral reduced to an ordinary hypergeometric function. Fresh Exa PDF fetch returned `CRAWL_HTTP_401`; its equations were not read. A probed RoyalSociety DOI ending1933.0093 was a query lead, not an established identity for Massey–Mohr; fetch timed out and no formula or bibliography is adopted from it. The original Massey–Mohr fulltext is not acquired here. Secondary bibliography search was used only to disambiguate the reference title, not as equation authority.

## New joint-source discovery result

Fresh SciSpace search1 returned leads including Kadyrov et al.PRA70,062703(2004), Roy/Roy/Sil JPhysB13(1980), Berakdar PRA56,370(1997), and Coulomb Born-series papers. Search2 explicitly asked for20,54.4,413.6eV spin/exchange/normalization coverage; the results included the same Kadyrov formulation, coupled-channel elastic/excitation results, proton/antiproton FDCS, near-threshold total ionization, and hyperspherical/eikonal papers. Index abstracts and titles are discovery evidence only. No new source body or joint event/amplitude table at those three energies was acquired. This bounded result leaves the full-support spin/exchange/recoil-consistent physical provider open and supplies no no-go claim.

The Attaourti preprint's inspected discussion explicitly uses250eV incident/5eV ejected/3degree scattered asymmetric geometry and contrasts first Born with higher-order Eikonal–Born. These figures do not supply a calibrated domain-wide adequacy statement for20/54.4/413.6eV. No curves were digitized.

## Attachments and admission

Metadata-only inventories of `project_sources/18-literatures.zip` (7members) and `19-papers.zip` (8members) are in ARCHIVE_INVENTORY.json. Filename pattern `attaourti|nordsieck|ioniz|coulomb|hydrogen|bray|weigold|childers` found no candidate. Generic paper filenames were not extracted/read. Root handles provided framework/report material. No archive-wide content absence is asserted.

Admitted for preparation: exact author-preprint convention/identity, Eq19/A9 endpoint, source omissions, documented discrepancies and bibliography correction. Pending root work: actual NR overlap derivation and branch choice; zero-transfer/bound-continuum orthogonality; flux/Fourier/TDCS conversion; exchange/count policy; any finite-M specialization and physical validity decision. Source bodies/pages/raw provider text remain private and must be excluded from public redistribution.
