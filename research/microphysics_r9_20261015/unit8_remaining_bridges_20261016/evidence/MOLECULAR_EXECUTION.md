# Unit8 lane B observed execution

Frozen MOLECULAR_THEORY/CONTRACT and independent MOLECULAR_THEORY_REVIEW PASS, including portable compact extraction amendment, were read before numerical execution. `code/laneB/molecular.py` implements the specified tridiagonal nuclear Hamiltonian and selected E1 sums on actual sparse CP curves and signed dipoles, plus actual CLT states/transitions LTE sums. No electronic calculation, product code, Unit7 result, H action or external NCP run was changed/executed.

Commands:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests/laneB -v > results/laneB/raw/tests_stdout.txt 2> results/laneB/raw/tests_stderr.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/laneB/molecular.py > results/laneB/raw/run_stdout.json 2> results/laneB/raw/run_stderr.txt
```

Requested executor gpt-6.1-sol, observed UNKNOWN; authority requested Astra, observed UNKNOWN. Python3.12.14, NumPy2.3.5, SciPy1.17.0. OMP/OpenBLAS/MKL/NumExpr set to one thread. Three focused tests pass (rotational angular normalization/forbidden line, global dipole sign, mass convention). One complete numerical run took 0.202363869001s against30s; test process0.407172177s and numerical process0.461304255s. No test/production failure, repeated production run, tolerance adjustment or solver/model repair occurred. Full raw stdout/stderr preserved.

All20 original receipt/data identities and molecule/basis/R/orientation fields passed; extraction identities are recorded in `inputs/laneB/lih_curve_extraction.json`. No large CI arrays were copied. Exact compact table and recorded original hashes support later source-absent reproduction with explicit NOT_AVAILABLE original recheck. Available mismatched originals fail rather than falling back. All five public CLT files matched frozen hashes. Original20 validated-source mode was used here.

The solver completed11 specified basis/interpolant/grid/domain/mass runs,99 level rows and132 allowed E1 rows. Maximum Euclidean eigenpair residual 6.19183375e-14Eh; orthonormality residual 1.11022302e-15. Maximum fine/coarse energy change4.14111e-7Eh; maximum relative E1A change3.46509e-4. All16 numerical gates pass pending independent implementation review. Full eigenvectors and radial meshes are retained in `evidence/lih_bound_wavefunctions.npz`; finite-domain shifts and edge probabilities are in result JSON, with no state erased.

For both bases, allv0/v1 states overJ0,1,2 pass the finite-curve localized-candidate diagnostics. Allv2 states are DOMAIN_SENSITIVE because the left edge probability exceeds1e-5; their eigenvalues and line strengths are finite-box results, not admitted localized physical predictions. Boundary energy shifts alone are small and do not override that edge-probability failure. Sparse PCHIP/cubic, basis and mass sensitivity results are stored separately. No precision physical molecular constant, complete-basis extrapolation, unknown short-range continuation or physical bound-state count is inferred.

Aug-DZ primary spacings E(v1,J0)-E00=1319.634778cm^-1 and E(v0,J1)-E00=14.251829cm^-1 differ from CLT1360.4770 and14.8251cm^-1 without forced matching. Model low-space lifetimes and reference all-list lifetimes have explicit distinct columns. J2 model lifetimes are null because initialJ2 is outside the prescribed lifetime sum; they are not labeled dark. Only the true ground state among modeled initial levels has zero rate and dark_state=true.

CLT parsing retained1086 unique states and18982 transitions, used state-energy gaps, and checked degeneracy8(2J+1). Max partition-reference residual=3.93068166e-05at10K; max cooling-table formatting residual=0.00947003345at10.9K; independent line/grouped power sums differ by at most4.4408921e-16. The actual level maximum25822.962cm^-1 is retained despite the definition metadata maximum20000. At5000K, E>15000cm^-1 contributes9.92526% of partition population and21.9803% of spontaneous power; these finite-list diagnostics are not a rigorous omitted-state bound.

Cooling is optically thin all-direction LTE spontaneous power per prescribed bound molecule: no4pi multiplier and no collider/abundance/formation/pumping/escape model. It is a literature-conditioned quantity, separately labeled from the finite electronic-basis curves. Physical reaction rates and cosmological LTE validity remain outside scope. Numerical success remains subject to independent review.
