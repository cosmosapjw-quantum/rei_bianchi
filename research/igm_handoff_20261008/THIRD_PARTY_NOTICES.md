# Source reuse

`bridge/vendor/source_transfer.py` is a verbatim 7306-byte copy of the user's
bass_cr R11 source. The source commit, Git blob, path and SHA256 are recorded in
`bridge/vendor/SOURCE_PROVENANCE.json`; recovered archive and selected evidence
hashes are in `inputs/R11_PROVENANCE.json`. This handoff does not invent a new
license grant for an upstream repository with no license identified. Reuse here
follows the user's express cross-repository research instruction and retains
attribution. New code does not replace the pinned production atomic provider.

The selected fixture records preserve exact numerator/denominator strings from
R11's saved results; they are not new observer evaluations. `inputs/receiver_record.rs`
is a pinned source copy for inspecting receiver semantics, not a compiled or
adopted production module. Its origin is rei_bianchi PR86 at
8477bae16accaf3de168669aafd2f31eac2ca811, path
research/accepted_boundary_evidence_20261008/sources/rei-midpoint-record-v1/rei-next-nodes/short-hhe-midpoint/src/record.rs.

Primary external context checked on 2026-10-08:

- Grackle 3.4.1 official integration documentation, Code Units and Comoving
  Coordinates sections: https://grackle.readthedocs.io/en/grackle-3.4.1/Interaction.html
  Supports explicit conversions to proper CGS; not a certificate of this code.
- Smith et al., Grackle chemistry/cooling library, abstract:
  https://arxiv.org/abs/1610.09591 . Context for external microphysics reuse only.
- Oñorbe et al., self-consistent reionization modelling, abstract:
  https://arxiv.org/abs/1607.04218 . Context for consistently specified ionization
  and heating histories; not used as an independent numerical oracle here.

The new equations and conditional-family extrema are derived in THEORY.md;
the original upstream implementation and separate rational toy oracle supply
distinct, explicitly scoped numerical evidence.
