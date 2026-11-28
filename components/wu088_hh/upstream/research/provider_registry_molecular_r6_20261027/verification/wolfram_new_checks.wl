(* One bounded, new R6 symbolic/reference call. No R5 projection-suite replay. *)
cpu0 = TimeUsed[];
timed = AbsoluteTiming[
  pi = {p1, p2, 1 - p1 - p2};
  v = {v1, v2, v3}; one = {1, 1, 1};
  K = {{-a-b, c, e}, {a, -c-d, f}, {b, d, -e-f}};
  L = K + Outer[Times, pi, v] - DiagonalMatrix[v];
  A = K + Outer[Times, pi, v-kappa one] - DiagonalMatrix[v-kappa one];
  z = {z1, z2, -z1-z2};
  chain = {{-1,0,0},{1,-1,0},{0,1,0}};
  P = IdentityMatrix[3] + chain;
  S = MatrixExp[t chain];
  R2 = Exp[-1] (IdentityMatrix[3] + P + P.P/2);
  overlap = Min[Flatten[Table[If[j<k,Total[MapThread[Min,{R2[[All,j]],R2[[All,k]]}]],1],{j,1,3},{k,1,3}]]];
  vn[n_] := q^n u0 + cc (1-q^n)/(1-q);
  checks = <|
    "full_A_column_sums" -> Simplify[one.A],
    "common_killing_on_zero_sum" -> Simplify[(L-A+kappa IdentityMatrix[3]).z],
    "positive_path_power" -> Flatten[P.P-{{0,0,0},{0,0,0},{1,1,1}}],
    "chain_propagator_difference" -> Simplify[S[[All,1]]-S[[All,3]]-Exp[-t]{1,t,-1-t}],
    "chain_initial_decay_slope" -> Simplify[D[Exp[-t](1+t),t]/.t->0],
    "degree2_overlap" -> Simplify[overlap-Exp[-1]/2],
    "whole_block_error_integral" -> Simplify[Integrate[u0+gg ss,{ss,0,HH}]-HH u0-gg HH^2/2],
    "zero_killing_integral_limit" -> Simplify[Limit[(1-Exp[-kappa HH])/kappa,kappa->0]-HH],
    "constant_forcing_recurrence" -> FullSimplify[vn[n+1]-q vn[n]-cc,Assumptions->0<q<1 && Element[n,Integers] && n>=0]
  |>;
  zeros = Flatten[Values[checks]];
  <|"checks"->checks,"zero_count"->Length[zeros],"all_zero"->And@@(#===0&/@zeros),
    "chain_rho_exact_H1"->ToString[2/Exp[1],InputForm],
    "claim_scope"->"new common-killing split, forced-block integral, positive-polynomial and analytic chain controls"|>
];
ExportString[Join[timed[[2]],<|"kernel_cpu_seconds"->TimeUsed[]-cpu0,"kernel_wall_seconds"->timed[[1]]|>],"RawJSON"]
