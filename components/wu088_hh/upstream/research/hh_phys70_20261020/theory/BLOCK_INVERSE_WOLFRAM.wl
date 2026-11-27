(* Exact query executed through the Wolfram evaluator on 2026-10-20.
   Result: all thirteen rational residuals zero. No numerical ODE run. *)
n = 3; ff = Array[f, n]; gg = Array[g, n]; aa = Array[a, n]; bb = Array[b, n];
qq = Array[q, n]; ca = Array[c, n]; cb = Array[d, n];
bf = Array[rf, n]; bg = Array[rg, n]; ba = Array[ra, n]; bbb = Array[rb, n];
vars = Join[ff, gg, aa, bb, {z}];
fun = Join[-gg, qq ff, ca ff[[1]] ff, cb ff[[2]] ff,
  {Sum[aa[[j]] bb[[j]]/ff[[j]]^2, {j, n}]}];
jac = D[fun, {vars}];
xf = (bf - s bg)/(1 + s^2 qq); xg = bg + s qq xf;
xa = ba + s ca (ff[[1]] xf + ff xf[[1]]);
xb = bbb + s cb (ff[[2]] xf + ff xf[[2]]);
xz = rz + s Sum[bb[[j]] xa[[j]]/ff[[j]]^2 + aa[[j]] xb[[j]]/ff[[j]]^2
  - 2 aa[[j]] bb[[j]] xf[[j]]/ff[[j]]^3, {j, n}];
answer = Join[xf, xg, xa, xb, {xz}];
residual = Together[(IdentityMatrix[4 n + 1] - s jac).answer
  - Join[bf, bg, ba, bbb, {rz}]];
<|"dimension_complex" -> Length[vars], "shared_external_channels" -> {1, 2},
  "exact_residual" -> residual, "all_zero" -> And @@ Thread[residual == 0],
  "q_lower_coarse_L64" -> (49/100 - 64*65/27^2)|>
