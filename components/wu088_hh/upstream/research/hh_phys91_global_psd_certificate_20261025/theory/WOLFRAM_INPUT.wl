Module[{s, f, w, y, h, support, trace, fullSupport, separateSupport, g, padding, vec, gramIdentity, checks, a, b, c, d, u, v, x1, x2},
s = {{0, 1, 0, -1}, {1, 0, 1, 0}, {0, 1, 0, 1}, {-1, 0, 1, 0}};
f = IdentityMatrix[4] + s; w = IdentityMatrix[4] - s; y = w.Transpose[w];
h = Table[If[i == j || Abs[s[[i,j]]] == 1, 1/10, 1], {i,4}, {j,4}];
support[z_] := Total[Flatten[h Abs[z]]];
trace = Tr[f.y]; fullSupport = support[y];
separateSupport = Total[Table[support[Outer[Times,w[[All,k]],w[[All,k]]]],{k,4}]];
g = {{a,b},{c,d}}; padding = DiagonalMatrix[{u,v}]; vec = {x1,x2};
gramIdentity = Expand[vec.(g.Transpose[g]+padding).vec - ((Transpose[g].vec).(Transpose[g].vec)+u x1^2+v x2^2)];
checks = Join[Flatten[s.s-2 IdentityMatrix[4]], Flatten[w.f+IdentityMatrix[4]], Flatten[y-(3 IdentityMatrix[4]-2s)], {trace+4,fullSupport-14/5,separateSupport-54/5,-trace/fullSupport-10/7,trace+fullSupport+6/5,gramIdentity,Det[w]-1}];
<|"scalar_count"->Length[checks], "residuals"->checks, "all_zero"->AllTrue[checks,TrueQ[#==0]&], "trace"->trace, "full_support"->fullSupport, "separate_rank_one_support"->separateSupport, "beta"->-trace/fullSupport, "B1_signed_upper"->trace+fullSupport, "W_determinant"->Det[w], "scope"->"NEW_MANUFACTURED_EXACT_ALGEBRA_ONLY; ACTUAL153_B1_NOT_EVALUATED"|>
]

