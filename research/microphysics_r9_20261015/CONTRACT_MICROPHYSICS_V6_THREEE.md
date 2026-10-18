# V6 occupation-list three-electron FCI extension

Frozen ID R9-FCI-BO-QUENCH-RESPONSE-v6-threeelectron-occupation-list. This supersedes the blanket >=64-orbital deferral ONLY for the nonsymmetric common-basis three-electron (Nalpha,Nbeta)=(2,1) charge-quench calculation. No Hamiltonian, basis, overlap convention or numerical acceptance gate changes.

Primary PySCF source inspected on2026-10-15 establishes that make_strings uses occupation lists at>=64 orbitals and number-conserving excitation links support them. The ordinary direct_spin1 Hamiltonian diagonal/contraction route can use these links. The incompatible path is the spin-penalty creation/destruction machinery; a restricted pspace is also unnecessary here.

Use unpenalized direct_spin1.FCI, pspace_size=0, davidson_only=True, lowest root in fixed Ms=1/2. Retain the entire shared union basis and original-Hamiltonian residual checks. After solving, obtain spin-separated1/2RDMs and compute spin_square_general with identity orbital coefficients and overlap1. Require S²=.75±1e-6. The lowest root is accepted as the target doublet only after this check. Avoid fix_spin_, contract_ss, spin_square0 and the solver object's spin_square method. The module-level spin_op.spin_square is acceptable if installed source confirms its RDM route.

Account explicitly for three n^4 float64 spin-resolved2RDM arrays plus transient copies; release them after obtaining spin and the summed1RDM. Cached compressed Hamiltonian links and uncompressed RDM links must not be confused. Existing CPU/RAM/wall and determinant guards stay active.

Validate against the existing penalized solver on the same actual small-basis Li→Be+ quench: energies within1e-9Eh, ground projection within1e-8 and spin within1e-6. Then execute the full union-aug-TZ case with>=64 orbitals under the retained resource limits. Record installed PySCF/source/backend identities and actual retained rank. Preserve the old backend-deferred receipt. A failed spin check remains a failure, not permission to relabel a higher-spin state.

Official source references: https://pyscf.org/_modules/pyscf/fci/cistring.html ; https://pyscf.org/_modules/pyscf/fci/direct_spin1.html ; https://pyscf.org/_modules/pyscf/fci/spin_op.html ; https://pyscf.org/_modules/pyscf/fci/rdm.html . This is a source-supported implementation contract; actual runtime compatibility is established by the specified tests.
