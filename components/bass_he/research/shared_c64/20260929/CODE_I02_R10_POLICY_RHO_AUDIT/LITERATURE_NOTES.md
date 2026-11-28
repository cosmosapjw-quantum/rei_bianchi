# R10 literature notes: impact-parameter dependence and claim ceiling

SciSpace semantic searches were run specifically for hidden-crossing / advanced-adiabatic impact-parameter dependence.

1. Grozdanov & Solov'ev, Phys. Rev. A 90, 032706 (2014), DOI 10.1103/PhysRevA.90.032706.
   The indexed abstract explicitly studies branch-point evolution as a function of
   omega=rho v. This supports treating impact-parameter dependence as structural.

2. Janev, Pop-Jordanov & Solov'ev, J. Phys. B 30 (1997), DOI 10.1088/0953-4075/30/10/005.
   The indexed abstract states that impact-parameter dependence of transition probability
   is calculated within the advanced adiabatic method.

3. Richter & Solov'ev, Phys. Rev. A 48, 432 (1993), DOI 10.1103/PhysRevA.48.432.
   Advanced-adiabatic hidden-crossing lineage. R8/R9 primary-source work established
   factor-two support from this paper.

4. Krstic et al., Phys. Rev. A 63, 032103 (2001), DOI 10.1103/PhysRevA.63.032103.
   Reexamines whether complex branch-point topology alone captures the strict adiabatic
   limit. This is a claim-ceiling warning: source/author-code normalization agreement
   does not itself imply universal physical validity.

SciSpace add-column returned no methodology/conclusion expansions for the selected
records, so the synthesis is limited to indexed metadata/abstracts plus the directly
audited CPC and author source.

## R10 implication

The factor-two exponent and rho-dependence are logically separate:
- normalization: CPC Eq.(55), author code, and upstream theory support factor two;
- impact dependence: CPC Eq.(56), Eq.(54), and literature require a rho-dependent object;
- R9 author implementation: factor two is used, but the first stored Delta sample is
  reused for all rho in SECTION.

Thus author Appendix-A output is an implementation benchmark, not by itself a physical
gold standard for a rho-dependent clean-room calculation.
