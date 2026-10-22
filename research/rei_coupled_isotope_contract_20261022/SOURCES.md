# Source roles for the C1 contract

## Current project authority, read in this turn

- REI PR219, final head `5a1e5220b301a1c497f2863d6fd823e605faba80`:
  https://github.com/cosmosapjw-quantum/rei_bianchi/pull/219 .
  Its dossier NEXT_DAG and FINAL_DELIVERY_ACK make the coupled isotope-native
  contract READY; completed scientific campaigns stay unchanged.
- REI PR220, head `8be7533cc97b3302bf42608699d6e8313ed6af8a`:
  https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220 .
  Its frozen compact map, retained states, source spectrum, and actual atomic
  decay helper were inspected. This is a separate model/cohort from PR219.
- REC119 recovery comment, read for the narrow returned dependency:
  https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119#issuecomment-6327410942 .
  Recovery and REC126 do not validate a merged REI/REC cohort.
- `SOURCE_INTAKE.json` records current observed metadata and the narrower
  coverage of prior-conversation summaries. No complete live cross-thread
  workspace survey is claimed.

## Original physical source and data status

1. R. D. Williams and S. E. Koonin, *Atomic final-state interactions in tritium
   decay*, Phys. Rev. C 27, 1815 (1983),
   https://doi.org/10.1103/PhysRevC.27.1815 . Exa and the publisher abstract
   were read. The abstract discusses residual-ion excited-state probabilities.
   The subscriber full text was not obtained in this turn. No numeric probability
   or new decay correction is used by the contract.
2. A. M. Frolov, *Spectrum of secondary electrons emitted during the nuclear
   beta-minus decay of the tritium atom*,
   https://arxiv.org/abs/1512.04721v2 , related journal DOI
   https://doi.org/10.1134/S0021364016030073 . Exa, SciSpace and the primary
   arXiv abstract independently identify continuum final states with secondary
   electrons. This supports retaining an unresolved daughter-yield provider;
   it does not establish a cosmological charge-yield table.
3. NIST Atomic Spectra Database, ionization energies:
   https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html . The official
   interface was identified as a future binding-energy source. No new isotope
   threshold numbers were extracted or imported in this C1 unit.
4. B. D. Smith et al., *Grackle: a Chemistry and Cooling Library for
   Astrophysics*, https://arxiv.org/abs/1610.09591 , full author HTML
   https://arxiv.org/html/1610.09591v2 . Its H/D/He chemistry, radiation and
   thermal interfaces are reusable context. It is not evidence that all
   H/He/Li isotope-native nuclear branches or fast-product transport exist.

The nuclear mass convention and two tritium constants come from the exact
checked-in project sources, not from newly evaluated physical data.
`fixtures/` preserves the selected source bytes and their identities.
Inherited nuclear low-temperature, neutral/screening and instant-thermalization
limitations remain intact. No physical provider gap is filled with a zero.

## Derived and checked content

Stoichiometry, free/bound electron bookkeeping, neutral/bare energy-reference
conversion, changing-particle EOS, and the source correction to shared charge
fractions are derived in CONTRACT.md. Their finite tests are manufactured
algebra checks, not new rate measurements. The actual Wolfram result and its
undefined-symbol warning are preserved under evidence/. The executable check
does not import or run a cosmological solver.
