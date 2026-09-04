# REI-MATH-M1 — Generic homogeneous spatial curvature, intentional RED

## Exact parent

```text
repository  cosmosapjw-quantum/rei_bianchi
parent PR   #57
parent head ab1ea23fd8e3ebe17f46d13d5496bb1db3eba08b
parent tree 779c06d1e4bf9c54292ad22030cb1b47906af988
```

This research node is independent of the one-attempt runtime-recovery lane. It
must not create an attempt ref, lease, Section-0 receipt, native result or
provider/science claim.

## Locked convention

```math
[e_a,e_b]=C^c{}_{ab}e_c,
```

```math
C^c{}_{ab}=\epsilon_{abd}n^{dc}
+a^B_a\delta^c_b-a^B_b\delta^c_a,
\qquad n^{ab}=n^{ba},
\qquad n^{ab}a^B_b=0.
```

The oriented spatial frame has `epsilon_123=+1`. The spacetime metric signature
is `(-,+,+,+)` and `c` remains explicit. The spatial Levi-Civita connection is
derived from the Koszul formula; the curvature convention is

```math
R(X,Y)Z=\nabla_X\nabla_YZ-\nabla_Y\nabla_XZ-\nabla_{[X,Y]}Z.
```

## Candidate formulas to prove, not assume

The symbolic oracle must derive and polynomially reduce the residuals modulo
the Jacobi ideal `n^{ab}a_b=0`.

```math
{}^{(3)}R_{ab}
=2n_{ac}n_b{}^c-(\operatorname{tr}n)n_{ab}
-2\epsilon_{cd(a}n_{b)}{}^c a^d
+\left[-2a_ca^c-n_{cd}n^{cd}
+\frac12(\operatorname{tr}n)^2\right]h_{ab},
```

```math
{}^{(3)}R
=-6a_ca^c-n_{cd}n^{cd}
+\frac12(\operatorname{tr}n)^2.
```

The homogeneous divergence identity for a constant symmetric trace-free
spatial tensor `s_ab` must be derived from the same connection, not imported:

```math
D_b s^{ab}
=-3a_b s^{ab}
-\epsilon^{abc}n_b{}^d s_{cd}.
```

The later Einstein momentum/Codazzi sign is **not** promoted in this RED; it
will be fixed only after reconciling the project's positive expansion tensor
`K_ab=H h_ab+sigma_ab` with its spacetime Riemann/Einstein convention.

## Sentinels

```text
Bianchi I
  a=0, n=0
  3R_ab=0, 3R=0

Bianchi V / open-FLRW spatial locus
  a=(A,0,0), n=0
  3R_ab=-2 A^2 h_ab, 3R=-6 A^2

Bianchi IX / closed-FLRW spatial locus
  a=0, n=N identity
  3R_ab=(N^2/2) h_ab, 3R=3N^2/2
```

## Expected RED

The implementation path

```text
research/rei_math_m1_generic_background/derive_spatial_curvature.py
```

is intentionally absent. Eight tests must fail by assertion with zero errors.
The next GREEN may use SymPy polynomial/Groebner reduction, but finite sentinels
cannot replace the generic residual proof.
