# Exact two-electron singlet backend addendum V3
Frozen ID R9-FCI-BO-QUENCH-RESPONSE-v3-twoelectron-backend. Inherits V1/V2 physical model and numerical/resource gates. This changes an implementation backend, not the physical Hamiltonian.

For normalized two-electron Ms=0 coefficients C_ij in orthonormal orbitals, the singlet spatial coefficient matrix is symmetric C=C.T with Frobenius norm1. With chemist integrals eri[a,b,c,d]=(ab|cd), exact full finite-space Coulomb action is HC=h@C+C@h.T+einsum('prqs,rs->pq',eri,C). The integral index order is essential; compare arbitrary small symmetric vectors with PySCF action.

Use an orthonormal packed symmetric basis of dimension n(n+1)/2: Cii=vii and Cij=Cji=vij/sqrt(2), i<j. Pack output as diagonal HCii and sqrt(2)*HCij. A SciPy LinearOperator with eigsh(which='SA') solves the singlet ground state without PySCF's >=64-orbital cistring limitation. The operator is exactly FCI on the complete retained singlet space. No dense many-body Hamiltonian is needed.

The spin-summed 1RDM is gamma=C C† + C.T C*, trace2. For normalized C, spin²=1−Re(vdot(C,C.T)); symmetry gives zero. Overlaps are Frobenius vdot or equivalent packed inner products. Residual is ||HC−E C||F. Daughter H moments use repeated actions. Nuclear repulsion, if present in another application, is an explicitly added scalar; these one-center quench applications have none.

Before promotion verify against standard small-basis PySCF: ground energy difference<=1e-9Eh, quench P difference<=1e-8, arbitrary symmetric-vector H actions relative difference<=1e-10. Require the V1 norm/residual gates and the target two-electron residual1e-9Eh. Parent and daughter use the same exact orbital/CI ordering. This fallback does not authorize orbital truncation or a three-electron approximation; the separate three-electron backend remains unchanged.
