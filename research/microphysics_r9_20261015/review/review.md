# Independent R9 microphysics review

Core formulas pass review for frozen v1 SHA774ff737 and generic v2 SHA91ba83 as read from the desktop checkout. Production acceptance remains pending full NCP receipts, v2 execution-deck and actual union/three-electron output review.

FCI molecular C2v/A1 selection, explicit spin fixing and S² measurement, original unpenalized-H energy/residual, common canonical AO basis quench, projected dipole moments, twice reorthogonalized Lanczos, Lorentzian window tails, and counterpoise fragment electron counts are consistent with the contract. V2 concatenates element-specific basis shells once and applies identical X/ERI to both nuclear charges; its projection formulas contain no two-electron assumption. Li0→Be+ with spin1 yields Nalpha2,Nbeta1 when specified in the deck.

Initial response acceptance propagation, live resource monitoring and case-table consumption findings were corrected. External simultaneous workloads still require root aggregation. Seven successful smoke NPZ hashes and five full local actual-basis pilot receipts were inspected; all five pilot finite-model gates pass. No full NCP receipt has yet been independently read in this review.

An independent tighter Li cc-pVDZ solve at energy tolerance1e-13 and residual tolerance5e-10 converged at E=-7.432637514964876 Eh, residual1.876e-10 Eh and S²=.7500000000000008. Its energy difference from the original is8.88e-16 Eh. A preliminary residual tolerance1e-10 run stalled and was not counted converged.

The common Li augDZ He→Li+ result P=.4672820372 is independently reproduced by RHF-MO FCI in the identical AO basis; parent E=-2.3128123755 Eh and daughter E=-7.2362308219 Eh. Thus the poor parent description is a contracted-basis limitation, not a canonical-basis implementation error. The augTZ probability.7167028695 changes by.24942,2494 times the1e-4 basis target. The series must be labeled basis-unconverged.

LiHe ccDZ at R=11.5 a0 changes from raw attraction -3.79524e-5 Eh to CP repulsion +5.51091e-6 Eh. A raw-only well claim is unsupported. Li augDZ response32 passes moment/Gram algebra (max errors1.96e-14 and2.08e-15), but TRK=1.11126 versus N=3 shows strong basis incompleteness;64→128 shape convergence remains untested in the inspected receipts. No physical continuum cross section, exclusive channel or low-temperature molecular rate is validated.

V3 exact two-electron backend was subsequently reviewed: H(C)=hC+Chᵀ+Σrs(pr|qs)Crs has correct PySCF Coulomb indexing; sqrt2 off-diagonal packing preserves norm; RDM and S² expressions are correct. Original-H residual uses the actual action. The independent native PySCF random-action/energy/projection test is meaningful but its execution has not yet been witnessed here. No formula blocker found. Actual high-rank results remain subject to residual checks; n>=64 three-electron cases must stay deferred, not use the two-electron backend.

## Actual NCP update

Read all56 v1 NCP receipts:5 pilot successes,16 atomic/quench production successes plus1 expected augQZ bitstring failure, and32 molecular successes plus2 expected LiH ccDZ SCF failures at R20/30. All53 successful NPZ hashes match receipts. Recursive original-H/spin/norm/RDM/orthogonality gates for main states, both quench states and all fragments pass. Maximum residual is4.55e-8 Eh; maximum metric defect4.70e-13. Independently checked saved CI shapes/norms, RDM traces, quench projection/complement, CP/raw identities and all array finiteness; no mismatch. Detailed evidence: actual_ncp_audit.json.

The actual matched-basis Li ionization energies ccD/T/Q are0.1964137691/0.1967155315/0.1973396187 Eh. T→Q difference0.000624087 Eh fails1e-4 target. LiH near R3 has CP values-.0825685768 (DZ) and-.0861078210 (augDZ), a.00353924 Eh sensitivity, also above target. LiHe coarse CP minimum is-3.20999e-7 Eh atR16, much shallower than raw attraction and unsupported by a second-basis convergence series. The original common-Li quench DZ→TZ failure of basis convergence remains.

Read executed NCP logs: exact2e backend1test passed(.060s), microphysics4tests passed(.347s), SCF fallback1test passed(.326s). H-action medians at4/8/12threads are1.37529/.73177/.52285s with action differences below9e-16;12threads is supported for this measured contraction.

V4 fallback is valid because full FCI is invariant under an orthonormal full-space orbital rotation and does not require converged SCF. Invalid initializer orbitals trigger canonical AO-metric orthogonalization per symmetry irrep. Original-H gates remain decisive. V5 verifier correctly uses retained orbital rank and reports rank-changing overlaps unavailable. Neither introduces a formula blocker. No adjacent-geometry overlap summary exists in the copied v1 archive yet; verifier execution and extension receipt review remain required.
