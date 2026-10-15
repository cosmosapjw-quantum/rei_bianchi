# Final extension independent review

This bounded review covers the new NCP extension, response, core-QZ and conditioning results, plus V6/V7 source changes. Unit1 was not re-reviewed. The export contains24 successful new receipts, one earlier large-three-electron backend deferral, and two rejected full-rank union-QZ trials. The pending large-three-electron augTZ run has no completed receipt in this export.

All24 successful NPZ hashes match. Saved arrays are finite; CI norms, one-body RDM traces, quench projection/complement identities and recursive parent/daughter numerical gates pass. Maximum accepted original-H residual is4.08345e-8 Eh and maximum metric defect1.23169e-10. No formula blocker or acceptance mislabel was found.

V6 uses the unpenalized physical Hamiltonian with occupied-list contraction links, pspace disabled, and explicit spin-resolved RDMs for posterior S² validation. It retains the original-H residual gate. V7 applies the same route to nonsymmetric atomic(2,1) states and includes spin-RDM memory estimates. The actual84-orbital core-QZ Li result has E=-7.47637286991729 Eh and S²=.7500000000000053. Li+ gives E=-7.278331078482658 Eh. Thus I_Q=.198041791434632 Eh; the core T→Q difference is.00034997082 Eh, exceeding the1e-4 target. The executed three-electron backend comparison log was read and is retained in the JSON evidence.

Balanced He+Li union probabilities are.70867427094/.70894073956/.70866828022 for augmented D/T/Q. The T→Q change.00027245935 exceeds1e-4, so the basis target is not met. For Q,126 raw AOs become124 retained orbitals: savedX has shape(126,124), and both1e-7 and1e-6 cutoffs select that same space. Parent/daughter energies are-2.90273212428737/-7.27709543375322 Eh, with metric defect6.58249e-11 and residuals<=8.91e-12 Eh. Equality between these two cutoff results is within the identical124-orbital model; it does not establish closure or convergence of the rejected126-orbital model. The full-rank trials correctly fail metric/residual gates and remain excluded.

Li→Be+ D and augmented-D results use three electrons(2,1), verify S²=.75, and give probabilities.57591977823 and.57564925529. The augTZ result remains pending; no completed higher-basis result is inferred.

Both Li response calculations meet the finite-model64→128 shape target at all three broadenings. Saved spectra were independently reconstructed from saved Ritz energies/weights, and moments were checked against recorded direct moments. TRK is1.11125914 in augDZ and1.65647443 in augTZ, versus complete-space3. Krylov convergence does not establish basis completeness or physical continuum boundary conditions.

The two LiH long-range SCF failures are repaired with finite-model FCI gates passing while SCF convergence remains explicitly false. New molecular CP values and complete scalar audit evidence are retained in FINAL_EXTENSION_REVIEW.json. No converged molecular rate, continuum cross section, or complete-basis precision is accepted by this review.

Molecular basis targets also remain unmet: atR3, LiH CP changes by.00738361 Eh between ccDZ and ccTZ, above1e-4. AtR11.5, LiHe CP changes from+5.51091e-6 Eh(ccDZ) to-3.79286e-6 Eh(augDZ), a9.30377e-6 Eh shift above1e-6. The augmented calculation supports attraction within its model but does not establish the physical well depth.
