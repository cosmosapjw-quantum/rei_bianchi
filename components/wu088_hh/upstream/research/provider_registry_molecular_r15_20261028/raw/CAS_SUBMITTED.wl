(* R15 authored exact-identity batch. NOT EXECUTED by the author.
   Root freezes and submits these exact UTF-8 file bytes, with no extra LF.
   One external call: 45 s wall allowance; internal TimeConstrained: 40 s.
   Expected: 72 scalar zero residuals. No general Integrate calls.
   Actual messages, unresolved expressions and timeout results are retained.
   z=0 is a separate explicit branch; nonzero formulas never receive z=0. *)
Module[
 {u, x, y, z, ll, rr, aa, bb, cc, dd, del, kap,
  d0, d1, s0, s1, s2, s3, v0, v1, v2, v3, v4, e0, e1, e2, e3,
  i, n, m, k, e, f, g, h, ii, jj, bc, sc, ic, src,
  bern3, bern4, blossom3, blossom4, restricted3, restricted4,
  left3, right3, beta, poly01, polyPrimitive, phi,
  primitive, primitivePhysical, momentPowers, basisPowers,
  pRat, pAlg, gRat, gAlg, pIntRat, pIntAlg,
  ids = {}, residuals = {}, add, addNZ, nonzeroAssumptions, report},

 bern3 = Function[{v,t},
   v[[1]] (1-t)^3 + 3 v[[2]] t (1-t)^2 +
   3 v[[3]] t^2 (1-t) + v[[4]] t^3];
 bern4 = Function[{v,t},
   v[[1]] (1-t)^4 + 4 v[[2]] t (1-t)^3 +
   6 v[[3]] t^2 (1-t)^2 + 4 v[[4]] t^3 (1-t) + v[[5]] t^4];
 blossom3 = Function[{v,a,b,c},
   v[[1]] (1-a) (1-b) (1-c) +
   v[[2]] (a (1-b) (1-c) + (1-a) b (1-c) + (1-a) (1-b) c) +
   v[[3]] (a b (1-c) + a (1-b) c + (1-a) b c) + v[[4]] a b c];
 blossom4 = Function[{v,a,b,c,d},
   v[[1]] (1-a) (1-b) (1-c) (1-d) +
   v[[2]] (a (1-b) (1-c) (1-d) + (1-a) b (1-c) (1-d) +
     (1-a) (1-b) c (1-d) + (1-a) (1-b) (1-c) d) +
   v[[3]] (a b (1-c) (1-d) + a (1-b) c (1-d) +
     a (1-b) (1-c) d + (1-a) b c (1-d) +
     (1-a) b (1-c) d + (1-a) (1-b) c d) +
   v[[4]] (a b c (1-d) + a b (1-c) d +
     a (1-b) c d + (1-a) b c d) + v[[5]] a b c d];
 beta = Function[{j,nn}, Switch[j,
   0, 1/(nn+5),
   1, 4/((nn+4) (nn+5)),
   2, 12/((nn+3) (nn+4) (nn+5)),
   3, 24/((nn+2) (nn+3) (nn+4) (nn+5)),
   4, 24/((nn+1) (nn+2) (nn+3) (nn+4) (nn+5))]];
 poly01 = Function[{p,t}, Module[{co},
   co = CoefficientList[Expand[p],t]; Total[co/Range[Length[co]]]]];
 polyPrimitive = Function[{p,t}, Module[{co,kk},
   co = CoefficientList[Expand[p],t];
   Total[Table[co[[kk+1]] t^(kk+1)/(kk+1), {kk,0,Length[co]-1}]]]];
 phi = Function[{j,zz},
   (Exp[zz] - Sum[zz^k/Factorial[k], {k,0,j-1}])/zz^j];
 nonzeroAssumptions = Element[{z,kap,del},Reals] &&
   z != 0 && kap != 0 && del > 0;
 add = Function[{name,expr},
   AppendTo[ids,name]; AppendTo[residuals,Cancel[Together[Expand[expr]]]]];
 addNZ = Function[{name,expr},
   add[name,Simplify[expr,nonzeroAssumptions]]];
 report = Function[{state}, <|
   "status" -> state,
   "expected_identity_count" -> 72,
   "residual_count" -> Length[residuals],
   "residuals" -> MapThread[<|"id" -> #1,"value" -> #2|>&,{ids,residuals}],
   "validity_assumptions" -> <|
     "geometry" -> "Polynomial identities; positive restriction application uses 0<=ll<=rr<=1.",
     "beta" -> "General rational identity applied at integer n>=0; finite polynomial integrals at n=0,1,5 and factorial factors at n=96.",
     "nonzero_phi" -> "Real z!=0, real kap!=0, del>0; explicit Simplify assumptions are used.",
     "zero_phi" -> "Separate polynomial integral and factorial-value branch; no substitution into singular phi quotients.",
     "reflection" -> "Real z and u; includes z=0 without singular quotients."|>,
   "scope" -> "Finite symbolic corroboration. Direct variation inequality, traversal/gap theorem, complete implementation and physical source premises retain separate proof/review evidence.",
   "warning_policy" -> "All actual messages and unresolved residuals are retained. No Quiet, Off, warning-cleaning rerun or CAS repair reserve."
 |>];

 TimeConstrained[
  (* Geometry: 11 identities. *)
  src = Function[{t},aa + bb t + cc t^2 + dd t^3];
  add["SIMPSON_CUBIC",
    aa (rr-ll) + bb (rr^2-ll^2)/2 + cc (rr^3-ll^3)/3 +
    dd (rr^4-ll^4)/4 -
    (rr-ll) (src[ll]+4 src[(ll+rr)/2]+src[rr])/6];
  ic = {d0 s0/6, (3 d0 s1+d1 s0)/24,
    (d0 s2+d1 s1)/12, (d0 s3+3 d1 s2)/24, d1 s3/6};
  add["POSITIVE_B1_TIMES_B3",
    (d0 (1-u)+d1 u) bern3[{s0,s1,s2,s3},u]/6 - bern4[ic,u]];
  add["DEGREE_THREE_TO_FOUR",
    bern3[{e0,e1,e2,e3},u] -
    bern4[{e0,(e0+3 e1)/4,(e1+e2)/2,(3 e2+e3)/4,e3},u]];
  bc = {v0,v1,v2,v3,v4}; sc = {s0,s1,s2,s3};
  add["QUARTIC_DERIVATIVE_BERNSTEIN",
    D[bern4[bc,u],u] - 4 bern3[{v1-v0,v2-v1,v3-v2,v4-v3},u]];
  restricted3 = {blossom3[sc,ll,ll,ll], blossom3[sc,ll,ll,rr],
    blossom3[sc,ll,rr,rr], blossom3[sc,rr,rr,rr]};
  restricted4 = {blossom4[bc,ll,ll,ll,ll], blossom4[bc,ll,ll,ll,rr],
    blossom4[bc,ll,ll,rr,rr], blossom4[bc,ll,rr,rr,rr],
    blossom4[bc,rr,rr,rr,rr]};
  add["CUBIC_RESTRICTION_BLOSSOM",
    bern3[restricted3,y] - bern3[sc,ll+(rr-ll)y]];
  add["QUARTIC_RESTRICTION_BLOSSOM",
    bern4[restricted4,y] - bern4[bc,ll+(rr-ll)y]];
  add["RESTRICTION_DERIVATIVE_CHAIN_FACTOR",
    D[bern4[restricted4,y],y] -
    (rr-ll) (D[bern4[bc,u],u] /. u -> ll+(rr-ll)y)];
  e=(s0+s1)/2; f=(s1+s2)/2; g=(s2+s3)/2;
  h=(e+f)/2; ii=(f+g)/2; jj=(h+ii)/2;
  left3={s0,e,h,jj}; right3={jj,ii,g,s3};
  add["DERIVATIVE_LEFT_MIDPOINT_SUBDIVISION",
    bern3[left3,u] - bern3[sc,u/2]];
  add["DERIVATIVE_RIGHT_MIDPOINT_SUBDIVISION",
    bern3[right3,u] - bern3[sc,(1+u)/2]];
  add["QUARTIC_ENDPOINT_ZERO",bern4[bc,0]-v0];
  add["QUARTIC_ENDPOINT_ONE",bern4[bc,1]-v4];

  (* Beta factors: 5 general rational + 15 polynomial + 5 finite factorial. *)
  Do[
    add["BETA_RATIONAL_i"<>ToString[i],
      Binomial[4,i] Sum[(-1)^k Binomial[i,k]/(n+5-i+k),{k,0,i}]-beta[i,n]],
    {i,0,4}];
  Do[
    add["BETA_POLYNOMIAL_n"<>ToString[n]<>"_i"<>ToString[i],
      poly01[Binomial[4,i] u^i (1-u)^(n+4-i),u]-beta[i,n]],
    {n,{0,1,5}},{i,0,4}];
  Do[
    add["BETA_FACTORIAL_n96_i"<>ToString[i],
      Binomial[4,i] Factorial[i] Factorial[100-i]/Factorial[101]-beta[i,96]],
    {i,0,4}];

  (* Reflection: 5 identities. *)
  Do[
    add["SIGNED_WEIGHT_REFLECTION_i"<>ToString[i],
      Simplify[
        Exp[z u] Binomial[4,i] (1-u)^i u^(4-i) -
        Exp[z] Exp[-z (1-u)] Binomial[4,4-i] u^(4-i) (1-u)^i,
        Element[{z,u},Reals]]],
    {i,0,4}];

  (* Build symbolic primitives before endpoint substitution, avoiding 0^0. *)
  primitive = Table[-Exp[z (1-u)]
    Sum[Factorial[m]/Factorial[m-k]*u^(m-k)/z^(k+1),{k,0,m}],{m,0,4}];
  primitivePhysical = Table[-Exp[kap (del-x)]
    Sum[Factorial[m]/Factorial[m-k]*x^(m-k)/kap^(k+1),{k,0,m}],{m,0,4}];
  Do[
    addNZ["PHI_NONZERO_PRIMITIVE_m"<>ToString[m],
      D[primitive[[m+1]],u]-Exp[z (1-u)] u^m],
    {m,0,4}];
  Do[
    addNZ["PHI_NONZERO_NORMALIZED_m"<>ToString[m],
      (primitive[[m+1]] /. u->1) - (primitive[[m+1]] /. u->0) -
      Factorial[m]*phi[m+1,z]],
    {m,0,4}];
  Do[
    addNZ["PHI_NONZERO_PHYSICAL_SCALE_m"<>ToString[m],
      (primitivePhysical[[m+1]] /. x->del) -
      (primitivePhysical[[m+1]] /. x->0) -
      Factorial[m]*del^(m+1)*phi[m+1,kap del]],
    {m,0,4}];
  Do[
    add["PHI_ZERO_SEPARATE_BRANCH_m"<>ToString[m],
      poly01[u^m,u]-Factorial[m]/Factorial[m+1]],
    {m,0,4}];
  momentPowers=Table[Factorial[m]*phi[m+1,z],{m,0,4}];
  basisPowers=Table[CoefficientList[Expand[Binomial[4,i] u^i (1-u)^(4-i)],u],{i,0,4}];
  addNZ["B4_MOMENT_SUM_TO_PHI1",
    Total[Table[basisPowers[[i+1]].momentPowers,{i,0,4}]]-phi[1,z]];

  (* Original-source substitution and exact representative controls: 10. *)
  add["ORIGINAL_CUBIC_BINOMIAL_SUBSTITUTION",
    src[x-u] - (aa+bb x+cc x^2+dd x^3 -
      (bb+2 cc x+3 dd x^2) u + (cc+3 dd x) u^2 - dd u^3)];
  add["CUBIC_SOURCE_R_CONTROL",poly01[u^3,u]-1/4];
  add["CUBIC_SOURCE_E_CONTROL",poly01[u^4/4,u]-1/20];
  pRat=-(u-1/4) (u-1/2) (u-3/4);
  pAlg=-(u-1/4) ((u-1/2)^2-1/8);
  gRat={35/32,83/96,109/96,29/32};
  gAlg={33/32,29/32,115/96,29/32};
  pIntRat=1+polyPrimitive[pRat,u]; pIntAlg=1+polyPrimitive[pAlg,u];
  add["MOVING_RATIONAL_SOURCE_FACTOR",bern3[gRat,u]-1-pRat];
  add["MOVING_RATIONAL_R_FINAL",(pIntRat /. u->1)-1];
  add["MOVING_RATIONAL_E_FINAL",3/2+poly01[(1-u) pRat,u]-1447/960];
  add["MOVING_RATIONAL_MAX_VALUE",(pIntRat /. u->1/4)-1033/1024];
  add["MOVING_ALGEBRAIC_SOURCE_FACTOR",bern3[gAlg,u]-1-pAlg];
  add["MOVING_ALGEBRAIC_R_FINAL",(pIntAlg /. u->1)-97/96];
  add["MOVING_ALGEBRAIC_E_FINAL",3/2+poly01[(1-u) pAlg,u]-1447/960];

  report[If[Length[residuals]==72 &&
    (And @@ (SameQ[#,0]& /@ residuals)),
    "ALL_RESIDUALS_ZERO","NONZERO_OR_UNRESOLVED"]],
  40,report["TIME_LIMIT"]
 ]
]
