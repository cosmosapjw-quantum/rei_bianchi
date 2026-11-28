(* New R14 frozen symbolic corroboration; actual messages are preserved. *)
TimeConstrained[
(* R14 authored corroboration draft. No execution by its author.
   Root must freeze this file and the actual submitted string before one allowed CAS call.
   Polynomial definitions avoid Piecewise BernsteinBasis domain conventions.
   Expected 32 exact zero residuals; messages and unresolved expressions must be preserved. *)
Module[
 {u, x, y, z, ll, rr, aa, bb, cc, d0, d1, s0, s1, s2,
  b0, b1, b2, b3, e0, e1, e2, bern2, bern3, blossom, beta,
  src, bc, restricted, ic, residuals = {}, ids = {}, add,
  i, n, pc1, pc2, root1, root2a, root2b},
 bern2 = Function[{v, t}, v[[1]] (1-t)^2 + 2 v[[2]] t (1-t) + v[[3]] t^2];
 bern3 = Function[{v, t}, v[[1]] (1-t)^3 + 3 v[[2]] t (1-t)^2 +
   3 v[[3]] t^2 (1-t) + v[[4]] t^3];
 blossom = Function[{v, a, b, c},
   v[[1]] (1-a) (1-b) (1-c) +
   v[[2]] (a (1-b) (1-c) + (1-a) b (1-c) + (1-a) (1-b) c) +
   v[[3]] (a b (1-c) + a (1-b) c + (1-a) b c) + v[[4]] a b c];
 beta = Function[{ii, nn}, Switch[ii,
   0, 1/(nn+4),
   1, 3/((nn+3) (nn+4)),
   2, 6/((nn+2) (nn+3) (nn+4)),
   3, 6/((nn+1) (nn+2) (nn+3) (nn+4))]];
 add = Function[{name, expr},
   AppendTo[ids, name]; AppendTo[residuals, Simplify[expr]]];
 Do[
   add["BETA_i" <> ToString[i] <> "_n" <> ToString[n],
     Binomial[3,i] Factorial[i] Factorial[n+3-i]/Factorial[n+4] - beta[i,n]],
   {n, {0,1,5,96}}, {i,0,3}];
 src = Function[{t}, aa + bb t + cc t^2];
 add["SIMPSON_QUADRATIC",
   Expand[aa (rr-ll) + bb (rr^2-ll^2)/2 + cc (rr^3-ll^3)/3 -
     (rr-ll) (src[ll] + 4 src[(ll+rr)/2] + src[rr])/6]];
 ic = {d0 s0/6, (2 d0 s1+d1 s0)/18,
   (d0 s2+2 d1 s1)/18, d1 s2/6};
 add["POSITIVE_LINEAR_TIMES_QUADRATIC",
   Expand[(d0 (1-x)+d1 x) bern2[{s0,s1,s2},x]/6 - bern3[ic,x]]];
 add["DEGREE_TWO_TO_THREE",
   Expand[bern2[{e0,e1,e2},x] -
     bern3[{e0,(e0+2 e1)/3,(2 e1+e2)/3,e2},x]]];
 bc = {b0,b1,b2,b3};
 add["CUBIC_DERIVATIVE_BERNSTEIN",
   Expand[D[bern3[bc,x],x] - 3 bern2[{b1-b0,b2-b1,b3-b2},x]]];
 restricted = {blossom[bc,ll,ll,ll], blossom[bc,ll,ll,rr],
   blossom[bc,ll,rr,rr], blossom[bc,rr,rr,rr]};
 add["EXACT_RESTRICTION_BLOSSOM",
   Expand[bern3[restricted,y] - bern3[bc,ll+(rr-ll)y]]];
 add["RESTRICTION_DERIVATIVE_CHAIN_FACTOR",
   Expand[D[bern3[restricted,y],y] -
     (rr-ll) (D[bern3[bc,x],x] /. x -> ll+(rr-ll)y)]];
 Do[
   add["NEGATIVE_WEIGHT_REVERSAL_i" <> ToString[i],
     Exp[z u] Binomial[3,i] (1-u)^i u^(3-i) -
     Exp[z] Exp[-z (1-u)] Binomial[3,3-i] u^(3-i) (1-u)^i],
   {i,0,3}];
 add["QUADRATIC_SOURCE_R",
   Integrate[u^2,{u,0,x}] - x^3/3];
 add["QUADRATIC_SOURCE_E",
   Integrate[u^3/3,{u,0,x}] - x^4/12];
 pc1 = Function[{t}, 1/3 + t/2 - t^3/3];
 root1 = 1/Sqrt[2];
 add["ONE_IRRATIONAL_CRITICAL",
   (D[pc1[x],x] /. x -> root1)];
 add["ONE_IRRATIONAL_SUPREMUM",
   pc1[root1] - (1/3+Sqrt[2]/6)];
 pc2 = Function[{t}, 2+t/8-t^2/2+t^3/3];
 root2a = (1-1/Sqrt[2])/2;
 root2b = (1+1/Sqrt[2])/2;
 add["TWO_IRRATIONAL_DERIVATIVE_FACTORIZATION",
   Expand[(x-root2a)(x-root2b) - (x^2-x+1/8)]];
 add["TWO_IRRATIONAL_MAXIMUM",
   pc2[root2a] - (95+Sqrt[2])/48];
 <|
   "status" -> If[And @@ (SameQ[#,0]& /@ residuals),
     "ALL_RESIDUALS_ZERO", "NONZERO_OR_UNRESOLVED"],
   "residual_count" -> Length[residuals],
   "residuals" -> MapThread[<|"id" -> #1, "value" -> #2|>&, {ids,residuals}],
   "scope" -> "Finite symbolic corroboration only; not independent proof, code execution, physical closure, or a proof of the complete root-isolation implementation."
 |>
]
,25,<|"status"->"TIME_LIMIT","residual_count"->Null|>]
