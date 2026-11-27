TimeConstrained[
 Module[{xx, zz, ll, uu, ss, aa, left, right, gg, slope, p0, p1, p2, nn, ii, w, ids, residuals, add, poly, tri},
  ids = {}; residuals = {};
  add[name_, value_] := (AppendTo[ids, name]; AppendTo[residuals, Together[Expand[value]]]);
  poly = p0 + p1 uu + p2 uu^2;
  add["quadratic_Bernstein_reconstruction", poly - (p0 (1 - uu/ll)^2 + 2 (p0 + p1 ll/2) (uu/ll) (1 - uu/ll) + (p0 + p1 ll + p2 ll^2) (uu/ll)^2)];
  add["affine_overlap_trapezoid", Integrate[gg + slope (ss - aa), {ss, left, right}] - (right - left) ((gg + slope (left - aa)) + (gg + slope (right - aa)))/2];
  Do[add["beta_moment_" <> ToString[ii] <> "_" <> ToString[nn], Integrate[Binomial[2, ii] xx^ii (1 - xx)^(nn + 2 - ii), {xx, 0, 1}] - Binomial[2, ii] Factorial[ii] Factorial[nn + 2 - ii]/Factorial[nn + 3]], {nn, {0, 1, 5, 96}}, {ii, 0, 2}];
  w = {((zz^2 - 2 zz + 2) Exp[zz] - 2)/zz^3, 2 ((zz - 2) Exp[zz] + zz + 2)/zz^3, (2 Exp[zz] - zz^2 - 2 zz - 2)/zz^3};
  Do[add["signed_reversal_" <> ToString[ii], FullSimplify[w[[ii]] - Exp[zz] (w[[4 - ii]] /. zz -> -zz), Assumptions -> zz != 0]], {ii, 1, 3}];
  Do[add["zero_argument_limit_" <> ToString[ii], Limit[w[[ii]], zz -> 0] - 1/3], {ii, 1, 3}];
  add["weights_sum_phi1", Total[w] - (Exp[zz] - 1)/zz];
  tri = Integrate[ss, {ss, xx - 1, 1}] + Integrate[2 - ss, {ss, 1, xx}];
  add["triangle_polynomial", tri - (3 xx - xx^2 - 3/2)];
  add["triangle_vertex_R", (tri /. xx -> 3/2) - 3/4];
  add["triangle_final_E", Integrate[xx^2/2, {xx, 0, 1}] + Integrate[tri, {xx, 1, 2}] - 5/6];
  add["triangle_vertex_E", Integrate[xx^2/2, {xx, 0, 1}] + Integrate[tri, {xx, 1, 3/2}] - 1/2];
  ExportString[<|"schema" -> "WU_R13_CAS_CHECK_V1", "ids" -> ids, "residuals" -> (ToString[#, InputForm] & /@ residuals), "count" -> Length[residuals], "zero_count" -> Count[residuals, 0], "all_zero" -> And @@ (# === 0 & /@ residuals)|>, "RawJSON"]
 ], 25, "TIME_CONSTRAINT_EXCEEDED"
]
