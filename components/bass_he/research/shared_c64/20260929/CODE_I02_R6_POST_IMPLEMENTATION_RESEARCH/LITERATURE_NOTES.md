# R6 literature notes

SciSpace semantic searches were run on numerical reproducibility, interval certification, certified homotopy, and higher-order automatic differentiation.

## Numerical reproducibility

1. Demmel & Nguyen, "Numerical Reproducibility and Accuracy at ExaScale," ARITH 2013, DOI 10.1109/ARITH.2013.43.
   Floating-point non-associativity and changing reduction order make bitwise reproducibility difficult on heterogeneous/parallel systems.

2. Collange et al., "Numerical reproducibility for the parallel reduction on multi- and many-core architectures," Parallel Computing 49 (2015), DOI 10.1016/J.PARCO.2015.09.001.
   Develops correctly rounded/reproducible reductions and treats reproducibility as a property requiring special algorithms.

3. ExBLAS reproducible BLAS work.
   Addresses bitwise reproducibility of basic linear algebra operations across executions and architectures.

4. Revol & Theveny, "Numerical Reproducibility and Parallel Computations: Issues for Interval Algorithms," IEEE TC / arXiv:1312.3300.
   Distinguishes bitwise reproducibility from the interval inclusion property required for rigorous validity.

## Rigorous nonlinear root / continuation certification

5. Krawczyk-like nonlinear system algorithms, SIAM J. Numerical Analysis 1985, DOI 10.1137/0722048.

6. "Efficient numerical validation of solutions of nonlinear systems," SIAM J. Numerical Analysis 1994, DOI 10.1137/0731013.

7. Breiding, Rose & Timme, "Certifying Zeros of Polynomial Systems Using Interval Arithmetic," ACM TOMS 2023, DOI 10.1145/3580277.

8. "Certified homotopy tracking using the Krawczyk method," arXiv:2402.07053.
   A parametric Krawczyk method for certified solution-path tracking, relevant to future BASS_HE named-sheet continuation.

9. "Deflation and certified isolation of singular zeros of polynomial systems," ISSAC 2011, DOI 10.1145/1993886.1993925.

## Higher-order differentiation and bifurcation

10. "Towards a full higher order AD-based continuation and bifurcation framework," Optimization Methods & Software (2018), DOI 10.1080/10556788.2018.1428604.

11. "Rigorous verification of Hopf bifurcations via desingularization and continuation," SIAM JADS 2021, DOI 10.1137/20M1343464.

## Evidence limitation

SciSpace add_column did not return additional methodology/conclusion fields for the selected reproducibility/Krawczyk papers. The synthesis is therefore limited to indexed metadata/abstracts plus the derivations in the R6 report.
