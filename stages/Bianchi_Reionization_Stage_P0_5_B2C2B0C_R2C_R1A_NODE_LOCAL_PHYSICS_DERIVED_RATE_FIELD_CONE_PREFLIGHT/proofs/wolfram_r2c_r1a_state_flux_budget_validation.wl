(* R2C-R1A exact symbolic validation.  Intended for wolframscript -file. *)
ClearAll[dt, q, n, r, u, x0, t, N0, I0, Sp, Sm, xin, M];
$Assumptions = dt > 0 && q > 1 && n >= 0 && r >= 0 && u >= 0 &&
  0 <= x0 <= 1 && t >= 0 && N0 >= 0 && I0 >= 0 && Sp >= 0 &&
  Sm >= 0 && 0 <= xin <= 1 && M > 0;
A = {{-u, r}, {u, -r}};
columnConservation = Simplify[Total[A, {1}] == {0, 0}];
metzler = Simplify[A[[1, 2]] >= 0 && A[[2, 1]] >= 0];
xeq = Piecewise[{{u/(u + r), u + r > 0}}, x0];
xsol = xeq + (x0 - xeq) Exp[-(u + r) t];
unitInterval = FullSimplify[0 <= xsol <= 1];
Cdt = n/dt + r;
Cref = q n/dt + r;
refinementIdentity = FullSimplify[Cref - Cdt == (q - 1) n/dt];
integratedBudget = FullSimplify[dt Cdt == n + dt r];
a = 1/(1 - Exp[-u dt]);
extrapolation = FullSimplify[u > 0 && a > 1];
transferGenerator = A - (Sm/M) IdentityMatrix[2];
transferMetzler = FullSimplify[
 transferGenerator[[1, 2]] >= 0 && transferGenerator[[2, 1]] >= 0];
sourcePositive = FullSimplify[And @@ Thread[Sp {1 - xin, xin} >= 0]];
result = <|
 "column_conservation" -> columnConservation,
 "metzler" -> metzler,
 "constant_rate_unit_interval" -> unitInterval,
 "capacity_refinement_identity" -> refinementIdentity,
 "integrated_budget_identity" -> integratedBudget,
 "common_equilibrium_is_extrapolation" -> extrapolation,
 "transfer_generator_metzler" -> transferMetzler,
 "transfer_source_positive" -> sourcePositive
|>;
Print[ExportString[result, "RawJSON"]];
If[And @@ Values[result], Exit[0], Exit[1]];
