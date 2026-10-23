# Source intake and independent symbolic checks

Read date: 2026-10-22. These sources support the numerical construction; the
actual implementation, finite residuals and timing are separate evidence.

## Preserved project sources

* PR221 head actually read as 42e44494bd0956756d8c610e75da5b1cafe20d3c,
  draft/open, base 6a12f3865d9ea427c1391c41caed8bb7cb7ec00d.
* [C1 contract at the pinned head](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/42e44494bd0956756d8c610e75da5b1cafe20d3c/research/rei_coupled_isotope_contract_20261022/CONTRACT.md)
  was fetched in full: absolute abundances, resolved events, factorial symmetry,
  neutral-atom energy reference, all-thermal EOS, single beta owner.
* Adjacent C2 RESUME.md, THEORY.md, CODE_MAP.md, BINDINGS.json, source manifest,
  atomic_network.py and the saved three-knot NPZ were read. The new unit reuses
  C2's 214-check scoped result and does not rerun that diagnostic.
* Root AGENTS.md was read. Local .git is absent. The remote head above is not
  falsely reported as an observed local checkout HEAD.
* User-attached Adaptive CMB Code Development Protocol and DAG-Governed
  Development executor informed contract reconstruction, paired physics/code
  review and plot inspection. The two figure-audit attachments were read for
  semantic, label, clipping and legibility checks. Cosmological geometry and
  Boltzmann hierarchy are outside this local-source change.

## Primary numerical literature

1. S. Blanes, A. Iserles and S. Macnamara, *Positivity-preserving methods for
   ordinary differential equations*, arXiv:2102.08242v2 (2022),
   [full text](https://arxiv.org/html/2102.08242v2).
   Section 3.3, equation (3.8), gives exactly the exponential midpoint selected
   here. The graph-Laplacian structure preserves nonnegative populations and
   linear conservation laws. Our contribution in this unit is its explicit
   application to the preserved isotope blocks, with an executable source
   adapter and measured cost. We make no novelty claim for this integrator.
2. G. Li and H. Rabitz, *A general analysis of exact lumping in chemical
   kinetics*, Chemical Engineering Science 44 (1989), 1413–1430,
   [DOI](https://doi.org/10.1016/0009-2509(89)85014-6),
   [author-institution record](https://collaborate.princeton.edu/en/publications/a-general-analysis-of-exact-lumping-in-chemical-kinetics/).
   The abstract relates exact lumping to fixed invariant Jacobian subspaces.
   This is context for our direct block proof, not a substitute for proving
   the actual donor's electronic-equality assumption. All isotope slots remain
   in the new implementation; a shared factorization is not a fixed abundance
   lift and does not require zero n/T inventories.
3. [SciPy 1.17.0 solve_ivp](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html)
   and [solve](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.linalg.solve.html).
   Version matches installed SciPy1.17.0. The solver's local estimate uses
   atol+rtol*abs(y); vector absolute tolerances are supported. This directly
   motivates explicit trace scaling and componentwise checks. Radau and dense
   linear solves are numeric oracles, not a proof of universal accuracy.

SciSpace returned ten candidate papers for positivity/conservation of chemical
production–destruction systems. Exa's one five-result search identified the
Li–Rabitz record and modern exact-reduction work; only the primary sources
above are relied upon. Exa additionally fetched the version-matched SciPy
pages and the Blanes–Iserles–Macnamara abstract. The full integrator paper was
then opened and equation (3.8) inspected. Other candidate papers were not
adopted as evidence. No unverified external cross section or rate was imported.

## Wolfram: actually evaluated algebra

Two stateless Wolfram Language evaluations complemented the general derivation.
No isotope numerical data from Wolfram were used. Main simulations run locally.

### Two-state Jacobian and inverse update

```wolfram
Clear[a,b,n,h,y0,y1,r0,r1];
G0={{-a,0},{a,0}}; G1={{0,b},{0,-b}};
y={y0,y1}; q={0,1}; B=G0+n(q.y)G1; f=B.y;
jac=Table[D[f[[i]],y[[j]]],{i,2},{j,2}];
u=n G1.y;
rankOne=FullSimplify[jac-B-Outer[Times,u,q]];
m=IdentityMatrix[2]-h B; rhs={r0,r1};
z=Inverse[m].rhs; w=Inverse[m].u;
sol=z+h w (q.z)/(1-h q.w);
solveResidual=FullSimplify[(IdentityMatrix[2]-h jac).sol-rhs];
<|"JacobianResidual"->rankOne,"SolveResidual"->solveResidual,
  "Conservation"->Simplify[{1,1}.f]|>
```

Observed output:

```text
<|"JacobianResidual" -> {{0, 0}, {0, 0}},
  "SolveResidual" -> {0, 0}, "Conservation" -> 0|>
```

The service also emitted `Symbol::undefined2` and `General::messages` for
global names G0/G1/B despite producing the above exact result. Preserve this
warning; the symbolic identity is additionally justified by the general
derivation and will be compared with finite dense linear algebra locally.

### EOS and interpolation remainder

```wolfram
Clear[t,c,k,q,ht,temp,dc,dt,f,x,x0,x1,m];
temperatureRate=-2 ht temp+(2 q/(3 k)-temp dc)/c;
eos=FullSimplify[(3/2)k(c temperatureRate+temp dc)
                +3 ht k temp c-q];
ff[x_]=m x^2/2;
linear[x_]=ff[x0]+(ff[x1]-ff[x0]) (x-x0)/(x1-x0);
interpolation=FullSimplify[ff[(x0+x1)/2]-linear[(x0+x1)/2]];
<|"EOSResidual"->eos,"QuadraticMidpointLogError"->interpolation|>
```

Observed output:

```text
<|"EOSResidual" -> 0,
  "QuadraticMidpointLogError" -> -1/8*(m*(x0 - x1)^2)|>
```

The quadratic check saturates the stated |f''| interpolation bound at the
midpoint. It does not supply a curvature bound for a physical nuclear table.

## Claim status and no-go policy

The new results are constructive identities, a numerical implementation and
finite comparisons. No new strong no-go theorem is proposed or admitted.
Invalid controls test exact implementation obligations and do not establish
general impossibility of other reductions, coordinates or physical closures.
