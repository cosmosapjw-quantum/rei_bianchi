# BASS_HE R10O / R10P

## Scoped result

R10N `NEW_AUTHORITY_NOT_COMPARABLE` is preserved for the exact 5.0 keV/amu H(1s), n=2 cell. The 2024 deposit exists; the returned exact-grid absence is user-reported execution evidence. The four CSVs and the original /tmp reports were not re-retrieved in R10O. No interpolation or source-grid substitution was performed.

R10O derives an exact ground-capture formula for the existing five-crossing, Nmax=3 no-return graph:

    q = p_Q12
    a = 1-p_Q23
    s = 1-p_S23
    w = P_rot[initial_m0,initial_m0]
    P_ground = a*q*(1-q)*(1+s*s*w)

At fixed crossing probabilities, arbitrary nonnegative stochastic rotors within the current united-atom (N,l) blocks obey sigma_ground[w1] <= 2*sigma_ground[w0]. This includes zero-base cases without dividing by a probability. It is not a universal bound on coherent, inter-block, changed-trajectory, or upper-shell-return dynamics.

Wolfram 10x10 symbolic matrix multiplication: identity residual 0, conservation residual 0, factor-two inequality True. Independent SymPy vector-event calculation: 21 symbolic checks and 243 exact-rational gap cases passed. These are new algebra checks, not the prior R10M 21-test replay. No collision solver was called.

The exact source snapshot audit_support.py is 3491 bytes, blob 39d5e923e6e8e779e83f1dc002d80e4c4562e3c2, SHA256 a62978c7637cec519c619aa225b062e18ad71248ec5674f0b392c0708498a970, matching archived MODEL_CONTRACT. Source was read/hashed, not imported or executed.

## Scientific limit and next node

S1 (Stolterfoht et al., PRA81,052704,2010, pp5-6,8) tentatively suggests 2p_sigma -> 2p_pi -> 1s_sigma rotational capture. The current fixed-(N,l) rotor includes the first edge but not the second. Direct Q12 ground capture already exists. Neither source wording nor CAS proves that the missing finite-R matrix element is nonzero or quantitatively explains the roughly 4620-fold S1/model discrepancy.

Next: R10P_FINITE_R_GROUND_ROTATIONAL_MATRIX_ELEMENT_AUDIT. Read the packaged HANDOFF_KO.md. Determine whether <1s_sigma(R)|L_perp|2p_pi(R)> is symmetry-forbidden or actually nonzero in a fixed, explicit finite-R convention. Source/analytic audit only; no new collision implementation, support selection, or retuning. S1 references24/25 are bounded next source leads, not newly reviewed authorities.

## Immutable source identity

PR15 HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c, tree f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8.
PR17 scientific-source HEAD 1a83a67e12de1ddc2aede0ff67168f7071450ab3, tree 230904af1337df1b86976c54a303d41db8ab7d96.
This append-only research note does not change that scientific-source identity.

## Full package and provider acknowledgements

BASS_HE_R10O_N1_TOPOLOGY_AUDIT_20260930_v1.zip
Bytes: 35209
SHA256: f6723d62f8ad84b6633d4d0653635aef0618e455aadf65a7fb840e065f4d23e6
ZIP CRC PASS; 18 members, 17 verified manifest payloads.
Contains report, bounded handoff, source/evidence ledgers, exact symbolic scripts and results. No source PDFs or original 2024 CSVs.

Google Drive object: 13mQwMTwQCukoLPWYiLS0NoH54kPsAGRb
Parent: 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Upload ACK success; metadata size 35209. Provider checksum was not exposed by the metadata wrapper. Raw restore NOT_RUN.

Dropbox object: id:BSpOijBcT10AAAAAADwy-w
Path: /BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_R10O_N1_TOPOLOGY_AUDIT_20260930_v1.zip
Upload completed; returned size 35209. Provider checksum not inspected; raw restore NOT_RUN.

These are upload/identity acknowledgements, not RESTORE_VERIFIED or independent physical review. This GitHub note is a publication subset, not the complete runnable package.

## Frozen gates

CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
