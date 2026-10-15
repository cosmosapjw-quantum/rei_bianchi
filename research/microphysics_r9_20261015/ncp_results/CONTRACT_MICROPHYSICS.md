# R9 finite-Gaussian microphysics execution contract

Contract ID: `R9-FCI-BO-QUENCH-RESPONSE-v1`, frozen 2026-10-15. This is an implementation and acceptance specification, not a calculation receipt. Its companion JSON is the machine-readable input deck. The requested eight-job program is broader than this contract: these calculations provide substantive inputs to `li_bound`, `li_continuum`, `molecular_lowT`, and `daughter_correlated`; they do not by themselves close `nuclear_precision`, `atomic_charge_cascade`, `bbn17`, or `full_transport`.

## 1. Hamiltonian and scope

Use atomic units, spherical Gaussian AOs, point nuclei, no ECP, no frozen core, no density fitting, real double precision, all-electron FCI in the explicitly retained orbital space:

H_e(R) = sum_i[-nabla_i^2/2 - sum_A Z_A/|r_i-R_A|] + sum_{i<j}1/r_ij;
E_BO(R) = E_e(R) + sum_{A<B} Z_A Z_B/R_AB.

Nuclei are clamped with infinite mass. Li may be tagged Li7, He tagged He3/He4, and H tagged H1/T3 for downstream bookkeeping, but these tags do not change this electronic Hamiltonian. Finite nuclear mass, mass polarization, recoil, finite nuclear size, relativistic/QED, hyperfine and nonadiabatic effects are absent and remain explicit model errors. No isotope-dependent rate may be inferred merely by changing a label. He→Li+ means a prescribed Z=2→3 two-electron quench; no particular isotope's nuclear decay is asserted. T−→He is the zero-recoil electronic sudden approximation to tritium-anion beta decay, with the above infinite-mass qualification.

Ground states: Li Z=3,N=3,charge=0,2S=1,2S-even; Li+ Z=3,N=2,charge=+1,2S=0,1S-even; He Z=2,N=2,charge=0,2S=0,1S-even; optional H−/T− Z=1,N=2,charge=−1,2S=0,1S-even. Compute <S²>; do not assume fixed M_S alone fixes S. RHF/ROHF may initialize orbitals but final energies and vectors must be FCI. If spin penalties are used, report the energy and residual of the original unpenalized Hamiltonian.

## 2. Atomic bound targets

Required energy series: species-specific built-in PySCF `cc-pvdz`, `cc-pvtz`, `cc-pvqz` for Li, Li+, He, with `aug-cc-pvdz` and `aug-cc-pvtz` for Li/Li+ diffuse-basis and response checks. Record expanded primitive exponents/contractions and their hashes: basis aliases alone are insufficient provenance. Add `cc-pcvdz`/`cc-pcvtz` Li/Li+ only if those aliases load and budget permits; absence does not invalidate the declared valence-basis calculation. All electrons remain correlated even in a cc-pVXZ basis.

For each retained basis write ground E, normalized CI vector, AO overlap spectrum, orthogonalization/MO matrix, nelec tuple, one-particle RDM, trace, <S²>, FCI residual, SCF/FCI flags and resource measurements. Compute I_Li=E(Li+)−E(Li) in matching Li AO bases, never from unmatched cardinalities. Report observed changes between successive bases as empirical basis sensitivity, not a rigorous complete-basis error. Non-nested cardinal basis sets need not give monotone energies.

## 3. Correlated daughter projection

Mandatory He→Li+ calculations at common bases equal to the **Li** `aug-cc-pvdz`, `aug-cc-pvtz`, `aug-cc-pvqz` basis definitions, centered at one common origin and used unchanged at both Z. Optional T−→He uses the concatenated H and He `aug-cc-pvXZ` basis definitions, X=D,T,Q, at the same center. The latter union must be explicitly recorded and conditioned; no hidden parent/daughter reoptimization of the one-particle space.

Diagonalize S=U s U^T once. Retain s_j>1e-10*s_max, use X=U_ret diag(s_ret^−1/2), and transform h(Z), ERI with the same X for both nuclear charges. Check X^T S X=I. A shared further orthogonal rotation is allowed if recorded; separately optimized MO coefficients cannot be directly dotted. CI tensors use identical alpha/beta determinant ordering, N_alpha=N_beta=1. A cross-orbital determinant-overlap calculation is a secondary check, not an excuse to drop the common-space guarantee.

A0=<Psi_f0|Psi_i0>=vdot(C_f0,C_i0), P0=|A0|². Define q=C_i0−A0*C_f0. Verify <C_f0,q>=0 and P0+||q||²=1. The complement is unresolved daughter excitation **including bound excited states**; it is not an ionization probability. Compute <H_f>, <H_f²> and variance from repeated original-Hamiltonian action. Repeating the S cutoff at 1e-9 on the smallest common basis measures conditioning sensitivity. When both parents are valid normalized ground states, this is a correlated two-electron result, not an independent-electron determinant model. Save both CI tensors and the common orbital matrix.

For T− require E(T−)<E(H in the same retained basis) before describing a numerically bound anion. If it fails, retain the result as an inadequate-basis diagnostic and do not promote its overlap to accepted T− physics. The optional union cannot displace mandatory He→Li+ work under a budget limit.

## 4. Actual molecular BO curves

LiH: neutral, four electrons, singlet X1Sigma+, atoms (Li,0,0,−R/2),(H,0,0,+R/2), R in a0. Required R grid: [2.0,2.5,3.0,3.2,3.5,4.0,5.0,6.0,8.0,12.0,20.0,30.0]. Required bases cc-pvdz and aug-cc-pvdz; cc-pvtz is a budget-gated extension at [2.5,3.0,3.2,4.0,8.0,20.0]. Ground spin-pure root suffices. The optional excited root is separately tracked and does not define the ground-state PES by root index continuity.

LiHe: neutral, five electrons, doublet X2Sigma+, same axial geometry, R grid [4.0,6.0,8.0,10.0,11.5,13.0,16.0,20.0,30.0,40.0]. Required cc-pvdz pilot and production; aug-cc-pvdz follows only measured resource feasibility. The extremely shallow long-range attraction makes basis/BSSE convergence important; do not infer a scattering length or near-threshold bound level from an unconverged curve.

For both species, compute isolated-fragment energies in their own bases, and counterpoise fragments with the other nucleus replaced by a zero-charge ghost retaining its basis. Use correct fragment electron number and spin: Li(3e,doublet), H(1e,doublet), He(2e,singlet). Save E_AB, E_A^A, E_B^B, E_A^AB(R), E_B^AB(R), V_raw=E_AB−E_A^A−E_B^B and V_CP=E_AB−E_A^AB−E_B^AB. E_AB includes nuclear repulsion; ghost fragments have no spurious cross nuclear repulsion. Report raw and CP potentials and their difference. No BSSE value may be silently subtracted twice.

Save at least the ground CI vector and orbital matrix at every calculated geometry, dipole vector including nuclear contribution, <S²>, original-H residual, and adjacent-geometry overlaps computed with cross-AO overlaps. The recovered R8 generator is a useful donor but requires adaptation: it currently assumes a uniform grid, at least two roots, tracks roots by overlap, lacks counterpoise and does not export explicit residual checks. Do not mutate the donor. Its actual recovered path is `recovered_r8/reionization_R8_20261014/local_codex/vendor_r6/code/lowt/generate_molecular_inputs.py`.

No low-temperature reaction/capture/charge-exchange rate follows from these single ground-state BO curves alone. Next physical inputs are channel-specific excited/ionic curves, nonadiabatic/radiative couplings, long-range matching and a converged radial scattering calculation. The contract produces real finite-basis PES inputs to that next calculation.

## 5. Inclusive Li dipole response

Use normalized Li ground states in aug-cc-pvdz and aug-cc-pvtz. Let P be the retained many-electron FCI space, D_a=P sum_i r_i,a P, b_a=(D_a−<D_a>)C0, K=H−E0. This explicitly specifies the **projected** dipole; <C0|D_a²|C0> computed using the unprojected coordinate-square AO integral is not automatically equal to ||b_a||² in a finite basis.

Compute m_k=sum_a <b_a|K^k|b_a>, k=0,1,2, directly by H actions. Construct Lanczos chains for each nonzero b_a with full/selective reorthogonalization and record Gram defect. Lengths 32,64,128 (256 only if needed and affordable). For each tridiagonal T and initial norm beta, compute nonnegative Ritz weights w_j=beta² |v_1j|² and excitation energies omega_j. For eta=[0.02,0.01,0.005] Eh and omega=0..2 Eh with step0.002 Eh, export S_eta(omega)=sum_{a,j} w_aj eta/[pi((omega−omega_aj)²+eta²)]. A finite window does not integrate to the full norm; account for Lorentzian tails analytically or report missing-window weight.

Validate zeroth/first/second moments against direct H actions. Report TRK diagnostic (2/3)*m1, whose complete nonrelativistic-space value is N=3; its finite-basis discrepancy is a model-completeness diagnostic, not an implementation failure by itself. Report positive-frequency/negative Ritz-weight diagnostics; do not clip substantial negative excitations. A moment calculation is useful even if the plotted response is not converged.

Output labels must say `finite_Gaussian_projected_dipole_response` and `pseudostate`. An above-threshold Ritz root is not an energy-normalized Coulomb scattering state. No physical photoionization cross section, exclusive ionization channel, angular spectrum, double-ionization probability, recombination rate, or radiative transfer opacity is accepted from this calculation alone. The constructive next step is a declared CCC/R-matrix/ECS driven provider with correct outgoing Coulomb boundary conditions, channel thresholds, exchange, normalization and continuum convergence. Physical continuum status stays `missing_provider_or_boundary_validation` until those checks are actually supplied.

## 6. Numerical acceptance and reporting

Required finite-model gates: |norm−1|<=1e-10; ||X^T S X−I||_inf<=1e-8; RDM trace error<=1e-8; |<S²>−S(S+1)|<=1e-6; original-H residual norm<=1e-7 Eh (target1e-9 for two-electron states); |P0+||q||²−1|<=1e-10 and |<Cf,q>|<=1e-10. FCI energy tolerance1e-11 Eh, max_cycle200, maximum Davidson space40. Recompute representative accepted energies with a tighter solver tolerance; difference<=1e-9 Eh. These thresholds target numerical errors comfortably below millihartree basis changes and the ~microhartree LiHe interaction scale; they are not claims of physical precision.

Lanczos internal moment agreement: absolute error <=1e-8*max(1,|m_k|) in atomic units for k=0,1,2; Gram defect<=1e-8. At fixed eta, 64→128 chain response relative L1 change<=1e-3 is an empirical Krylov convergence target. Failure means unconverged response with useful exact finite-space moments retained. Basis targets: atomic I change<=1e-4 Eh, quench P0 change<=1e-4, LiH near-minimum V_CP change<=1e-4 Eh, and LiHe well-region change<=1e-6 Eh. These are explicitly **targets**, not guaranteed acceptance budgets or rigorous error bars. If missed, publish the actual series as basis-unconverged; do not hide the data or silently relax the target. State every remaining systematic separately.

Every result has separate fields: implementation_checked, finite_model_numerics_passed, basis_target_met, physical_scope, remaining_dependencies. Never collapse them to one global success boolean.

## 7. NCP execution and stop rules

Assumed host inventory supplied by root: 64 logical CPUs, approximately125 GiB RAM. Confirm at preflight. Total additive worker allocation for this program is at most48 logical CPUs and96 GiB RSS, including parent processes and native-library allocations. Respect any smaller root/scheduler quota. PySCF max_memory is advisory, not an OS memory guarantee. Preserve at least~29 GiB host headroom and16 logical CPUs outside the allocation.

One representative pilot per workload family: Li aug-cc-pvtz; He→Li+ common aug-cc-pvtz; LiH aug-cc-pvdz R=3.2; LiHe cc-pvdz R=11.5; Li aug-cc-pvdz response32. Start each at4 threads,16 GiB, wall limit1800s, sequentially unless root approves disjoint budgets. Compare one representative expensive H action at4/8/12 threads; use the measured efficient count, not all48 by default. Production default12 threads/24 GiB per job, at most4 concurrent jobs; LiHe aug-DZ may use12 threads/32 GiB with at most3 such jobs. Sum CPU/RAM caps across all simultaneous atomic/molecular/response work. Set OMP_NUM_THREADS to allocated threads, OPENBLAS_NUM_THREADS=1, MKL_NUM_THREADS=1 and use pyscf.lib.num_threads explicitly. Record actual runtime thread pools.

Estimate D=binom(norb,Nalpha)*binom(norb,Nbeta), ERI bytes and all stored CI/work vectors before starting. Stop before allocation if D>10,000,000, dense ERI>8 GiB, estimated RSS>75% of per-job limit, or aggregate cap would be exceeded; write `resource_deferred` with estimates. No dense D-by-D Hamiltonian. Use contraction-based Davidson/Lanczos. Default per production geometry/state wall cap7200s and job-family cap21600s, configurable downward by root. On cap, checkpoint completed units and mark the rest deferred. Stop on nonfinite values, failed convergence/spin/residual gates, repeated stagnation, measured aggregate RSS>96 GiB, per-job hard cap, or host headroom<20 GiB. Do not retry indefinitely. Basis extensions are lower priority than completing mandatory coarse curves and quench pairs.

Required new driver interface (to be implemented; these commands are **not evidence of execution**):

```bash
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 microphysics_driver.py preflight --contract CONTRACT_MICROPHYSICS.json --out runs
python3 microphysics_driver.py pilot --contract CONTRACT_MICROPHYSICS.json --threads 4 --memory-gib 16 --out runs
python3 microphysics_driver.py run --contract CONTRACT_MICROPHYSICS.json --workers 4 --threads 12 --memory-gib 24 --cpu-cap 48 --memory-cap-gib 96 --out runs
python3 microphysics_driver.py verify --contract CONTRACT_MICROPHYSICS.json --out runs
```

The implementer may use its established CLI instead if the frozen deck is consumed without semantic changes and the exact executed command is recorded. No result may be claimed from a merely prepared command. Snapshot source SHA, input SHA, PySCF/NumPy/SciPy/BLAS/Python versions, kernel/CPU, elapsed time, child-inclusive peak RSS, exit code, stdout/stderr, CI/RDM/curve data and checksums after every independent unit. Preserve originals, work additively, and hand each completed unit to root for authorized external backup; no main merge.

## 8. Sources and reuse

Primary implementation documentation read: PySCF CI manual https://pyscf.org/user/ci.html ; FCI source https://pyscf.org/_modules/pyscf/fci/direct_spin1.html ; Gaussian integral API https://pyscf.org/pyscf_api_docs/pyscf.gto.html . These establish available all-determinant FCI and integral interfaces, not accuracy of a particular run.

Primary physics located through Exa: *Final-State Spectrum of 3He after beta− Decay of Tritium Anions T−*, https://arxiv.org/abs/1001.0120 (full text https://ar5iv.labs.arxiv.org/html/1001.0120). It supplies a directly relevant precedent for correlated FCI sudden overlaps, common-basis closure and a separately constructed complex-scaled continuum. The present finite real-Gaussian response does not reproduce that paper's complex-scaled continuum calculation. *Accurate ab initio determination of the van der Waals interaction in the X2Sigma+ ground state of LiHe*, https://doi.org/10.1007/s004600050118 , and *Ab Initio Investigation of the LiHe X2Sigma+, A2Pi, and B States: A Basis Set Study*, author-hosted https://jupiter.chem.uoa.gr/pchem/pubs/pdf/JPCA_104(2000)408.pdf , motivate the shallow-interaction, diffuse/core-basis and BSSE cautions; no table from those articles is silently substituted for newly computed PES data.

Read R8 `local_codex/AVAILABLE_CODE_AND_INPUTS.md` and `local_codex/LOCAL_CODEX_HANDOFF.md`. Their provider/readiness distinctions remain in force. Reuse original matrix kernels/generator logic where suitable, but fixtures are not physical input, a passed finite-space identity is not continuum convergence, and a new independent calculation is not recovery of historical unpublished coefficients.
