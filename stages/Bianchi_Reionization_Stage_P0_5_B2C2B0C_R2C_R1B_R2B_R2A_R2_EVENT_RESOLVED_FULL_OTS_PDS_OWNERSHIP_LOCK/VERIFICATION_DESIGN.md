# Verification design

- Run `analysis/run_event_theory_lock.py` from the committed tree.
- Require exact symbolic vector and invariant residuals.
- Require maximum 46,080-node replay residual `<1e-13` in all three lanes.
- Require no negative branch multiplicity on the declared domain.
- Require zero duplicate event IDs, zero unowned event records, and zero direct He I to He III events.
- Require exact-zero `EFFECTIVE_HI_SUBGRID` resolved H/He/thermal source by inherited owner contract.
- Require Wolfram parity for vectors, invariants, branch counts, and augmented energy identities.
- Require Decimal/SymPy replay independently of Wolfram.
- Preserve the expected negative result: source-identical `v/f` and resolved OTS heating must remain false.
- Repository closeout requires verifier, stage tests, SHA-256 audit, compact ZIP CRC, `git diff --check`, and `git fsck --full`.
