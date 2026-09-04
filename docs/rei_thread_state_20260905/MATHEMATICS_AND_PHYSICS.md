# Mathematics and physics state

## Conventions

```text
metric signature          (-,+,+,+)
spatial orientation       epsilon_123=+1
speed of light            explicit
commutator convention     [e_a,e_b]=C^c_ab e_c
structure decomposition   C^c_ab=epsilon_abd n^(dc)+a^B_a delta^c_b-a^B_b delta^c_a
n^{ab}                    symmetric
Jacobi condition          n^{ab} a^B_b=0
```

The Bianchi commutator vector `a^B_a` is not the physical four-acceleration of the normal congruence. The temporal triad rotation is not normal-congruence vorticity. The photon propagation direction `e^a` is distinct from the outward observer-sky direction `n_sky^a=-e^a`.

## M1 exact spatial-curvature result

Starting from the locked commutator and the Koszul formula, PR #62 constructs the spatial Levi-Civita connection, then the spatial Riemann and Ricci tensors, and reduces candidate residuals modulo the Jacobi ideal.

The exact formula is

```math
{}^{(3)}R_{ab}
=2n_{ac}n_b{}^c-(\operatorname{tr}n)n_{ab}
-2\epsilon_{cd(a}n_{b)}{}^c a^d
+\left[-2a^2-n_{cd}n^{cd}+\frac12(\operatorname{tr}n)^2\right]h_{ab}.
```

Its trace is

```math
{}^{(3)}R=-6a^2-n_{ab}n^{ab}+\frac12(\operatorname{tr}n)^2.
```

For a homogeneous constant symmetric trace-free spatial tensor `s_ab`, the same connection gives

```math
D_b s^{ab}=-3a_b s^{ab}-\epsilon^{abc}n_b{}^d s_{cd}.
```

### Exact-head evidence

```text
former RED suite                          8/8 PASS
Ricci tensor residuals modulo Jacobi      9/9 exact zero
Ricci scalar residual modulo Jacobi       exact zero
homogeneous STF-divergence residuals      3/3 exact zero
Bianchi I sentinel                        PASS
Bianchi V/open-FLRW spatial sentinel      PASS
Bianchi IX/closed-FLRW spatial sentinel   PASS
```

```text
workflow 33870832194  SUCCESS
verify   33870832204  SUCCESS
```

## Sentinel limits

### Bianchi I

```math
a^B_a=0,\qquad n_{ab}=0
```

implies

```math
{}^{(3)}R_{ab}=0,\qquad {}^{(3)}R=0.
```

### Bianchi V / open-FLRW spatial locus

```math
n_{ab}=0,\qquad a^2=A^2
```

implies

```math
{}^{(3)}R_{ab}=-2A^2h_{ab},\qquad {}^{(3)}R=-6A^2.
```

### Bianchi IX isotropic spatial locus

```math
a^B_a=0,\qquad n_{ab}=Nh_{ab}
```

implies

```math
{}^{(3)}R_{ab}=\frac12N^2h_{ab},\qquad {}^{(3)}R=\frac32N^2.
```

## Plot-driven class-B adversarial result

Eight deterministic Jacobi-admissible samples were used:

```text
four class-A controls with a^B=0
four class-B samples with an active epsilon*n*a channel
```

The locked expression has exact-zero residual in all eight. Reversing only the mixed-term sign remains invisible in all four class-A controls, as it must, and is detected in all four class-B samples.

```text
samples                              8
Jacobi exact zeros                   8/8
locked Ricci residual exact zeros    8/8
class-A mutation zeros               4/4
class-B mutation detections          4/4
artifact ID                          9935814901
artifact ZIP SHA-256                 8baa464690d239aa448b183bf42cbd98c1873eefdc79b757a52753f18556a038
```

This is numerical adversarial regression. The generic authority remains the symbolic reduction modulo the Jacobi ideal.

## Positive-expansion convention and the open spacetime sign gate

The project uses the positive expansion tensor

```math
K^+_{ab}=Hh_{ab}+\sigma_{ab},\qquad \sigma^a{}_a=0.
```

Therefore

```math
K^+=3H,
```

```math
K^+_{ab}K_+^{ab}=3H^2+\sigma_{ab}\sigma^{ab},
```

and

```math
(K^+)^2-K^+_{ab}K_+^{ab}
=6H^2-\sigma_{ab}\sigma^{ab}.
```

If `sigma^2=(1/2)sigma_ab sigma^ab`, this is `6H^2-2 sigma^2`.

This quadratic combination is even under `K_ab -> -K_ab`. The momentum/Codazzi combination

```math
D_b(K^{ab}-h^{ab}K)
```

is odd. Consequently the Hamiltonian extrinsic term does not by itself determine the ADM-sign adapter, while the momentum constraint requires the extrinsic-curvature and stress-energy momentum signs to be fixed together.

The following remain unproved in the active REI line:

```text
actual four-dimensional xTensor E_ab construction
positive-K versus ADM-K adapter
Hamiltonian projection from the locked spacetime Riemann convention
momentum/Codazzi projection with the locked matter momentum sign
constraint-propagation matrix
background numerical admission
```

The next formula node is therefore

```text
REI-MATH-M1B-SPACETIME-GAUSS-CODAZZI-CONSTRAINT-SIGN
```

It must not infer a sign from a textbook ADM convention without an explicit adapter.

## Photon-transport authority boundary

The available formula SSOT covers exact homogeneous polarized photon transport for cold, non-tilted electrons at rest in the normal frame. It includes distribution, PSTF, tetrad, and project-spin/Wigner formula layers and literal eleven-branch specializations. It explicitly excludes:

```text
finite electron tilt
thermal Comptonization
recoil and Klein-Nishina corrections
recombination and reionization microphysics
hierarchy truncation
line-of-sight integration
solver construction
numerical evolution
likelihood and inference
```

Therefore REI may consume the common BASS photon formulas, but it may not relabel the cold normal-frame Thomson block as a finite-electron-tilt reionization collision theorem.

## REI grouped-redshift and thermochemistry scope

The current REI grouped-redshift checks are FLRW/exactly-isotropic-angular controls. They are not generic Bianchi photon transport. In an anisotropic radiation field, shear couples to angular moments; a scalar grouped-redshift surrogate cannot replace the BASS transport operator without a declared closure.

The REI-owned physics surfaces remain:

```text
late reionization history
opacity and thermochemistry values
finite-optical-depth transmission and species allocation
H/He event stoichiometry
OTS event graph
first-canonical-interval evidence
provider export after admission
```

No current formula result establishes the first interval or provider.

## Kinetic representation dependency

For a general frequency-dependent source, the frequency-preserving primary representation pair is

```math
f(q,e)\longleftrightarrow F_{A_\ell}(q).
```

Integrated states such as

```math
J^{(i)}_{A_\ell},\qquad G(e)
```

require source projection or a spectral-closure certificate. A scalar effective opacity cannot generally close a frequency-dependent source on `G(e)` alone.

This is a BASS/REC dependency rule that REI must preserve when consuming primordial and transport providers; it is not a claim that REI owns the common representation compiler.

## Dimensional checks

```text
[a^B_a] = [n_ab] = [H] = [sigma_ab] = L^-1
[3R_ab] = [3R] = L^-2
[K_ab] = L^-1
[(K)^2-K_ab K^ab] = L^-2
```

The formulas are dimensionally consistent. No natural-unit suppression is used in this package.

## Current formula verdict

```text
generic homogeneous spatial curvature     PASS
homogeneous STF divergence                 PASS
class-B mixed-sign mutation sensitivity   PASS
spacetime Gauss-Codazzi sign               DEFERRED
constraint propagation                     NOT_RUN
background solver readiness                NOT_CLAIMED
finite-electron-tilt collision              NOT_IMPLEMENTED
provider/science readiness                  NOT_CLAIMED
```
