# SciSpace literature-role lock — runtime handoff rebind

This node changes no physical equation.  Literature is admitted only to check
the execution/provenance design, never to own REI source bytes or scientific
claims.

## Admitted methodological references

1. U. Kulisch, *Mathematics and Speed for Interval Arithmetic: A Complement to
   IEEE 1788*, ACM Transactions on Mathematical Software 45 (2019),
   DOI `10.1145/3264448`.

   Role: supports explicit rounded-arithmetic semantics and the importance of
   directed rounding and inclusion properties.  It does not certify this
   repository's Rust/MPFR implementation.

2. P. Ivie and D. Thain, *PRUNE: A Preserving Run Environment for Reproducible
   Scientific Computing*, IEEE eScience (2016),
   DOI `10.1109/ESCIENCE.2016.7870886`.

   Role: supports strict task/environment binding, immutable derived-data
   provenance and reproducible execution records.  It does not require or
   justify any REI scientific promotion.

3. A. Dhruv, A. Dubey, L. A. Barba and S. Gesing, *Managing Software
   Provenance to Enhance Reproducibility in Computational Research*, Computing
   in Science & Engineering (2023), DOI `10.1109/MCSE.2023.3314288`.

   Role: supports recording exact software, environment and execution
   provenance for HPC scientific studies.

4. N. Revol et al., *Numerical reproducibility in HPC: issues in interval
   arithmetic* (2013).

   Role: supports separating bitwise repeatability from the interval inclusion
   property.  The present handoff therefore keeps deterministic artifact
   identity and mathematical inclusion claims as distinct evidence classes.

## Project boundary

The references support the following design choices only:

```text
exact environment and input pins
immutable/append-only evidence
one material delta per rerun
explicit directed-rounding policy
separation of byte identity, numerical inclusion and scientific validity
```

They do not establish:

```text
native runtime PASS
first canonical interval
REI provider admission
generic Bianchi reionization transport
BASS/REC compatibility
science or publication validity
```
