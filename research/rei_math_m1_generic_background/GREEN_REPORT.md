# REI-MATH-M1 Generic Spatial Curvature — GREEN candidate

## Derivation path

The executable oracle derives, rather than inserts, the spatial connection and
curvature in the locked oriented orthonormal frame:

```text
C^c_ab
  -> Koszul Gamma^c_{b a}
  -> R^d_{c a b}
  -> Ricci_ab and Ricci scalar
  -> residual reduction modulo n^{ab} a_b = 0
```

The candidate formulas are

```math
{}^{(3)}R_{ab}
=2n_{ac}n_b{}^c-(\operatorname{tr}n)n_{ab}
-2\epsilon_{cd(a}n_{b)}{}^c a^d
+\left[-2a^2-n_{cd}n^{cd}
+\frac12(\operatorname{tr}n)^2\right]h_{ab},
```

```math
{}^{(3)}R=-6a^2-n_{ab}n^{ab}
+\frac12(\operatorname{tr}n)^2.
```

For a homogeneous constant symmetric trace-free spatial tensor `s_ab`, the
same connection gives

```math
D_b s^{ab}=-3a_bs^{ab}-\epsilon^{abc}n_b{}^d s_{cd}.
```

The Einstein momentum/Codazzi sign remains deferred until the project's
positive expansion tensor `K_ab=Hh_ab+sigma_ab` is reconciled with the exact
spacetime Riemann and stress-energy conventions. This avoids silently importing
an ADM convention with the opposite extrinsic-curvature sign.

## Required symbolic evidence

- all nine Ricci-tensor residuals reduce to zero modulo the Jacobi ideal;
- the scalar residual reduces to zero;
- all three homogeneous-divergence residuals vanish identically;
- Bianchi I, V/open-FLRW and IX/closed-FLRW sentinels match;
- no runtime, provider or numerical-evolution claim is promoted.

## Dimensions and limits

```text
[a_a] = [n_ab] = L^-1
[3R_ab] = [3R] = L^-2
```

```text
I:  a=0, n=0              -> 3R_ab=0
V:  n=0                    -> 3R_ab=-2a^2 h_ab
IX: a=0, n=N h             -> 3R_ab=(N^2/2) h_ab
```

## Next mathematics node after GREEN

```text
REI-MATH-M1B-SPACETIME-GAUSS-CODAZZI-CONSTRAINT-SIGN
```

It must derive the Hamiltonian and momentum constraints from the same
four-dimensional convention and prove constraint propagation before any
background numerical admission.
