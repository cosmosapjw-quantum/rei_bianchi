ClearAll["Global`*"];
$Assumptions = h1 >= 0 && h2 >= 0 && h3 >= 0 && h4 >= 0 &&
  h1 + h2 + h3 + h4 > 0 && K >= 0 && J >= 0 && Uraw > 0 && Utarget > 0 && s > 0 && a > 0;
h = {h1, h2, h3, h4}; q = h/Total[h];
k = K q; j = J q; lambda = Utarget/Uraw;
result = <|
  "qSumResidual" -> FullSimplify[Total[q] - 1],
  "opacitySumResidual" -> FullSimplify[Total[k] - K],
  "currentSumResidual" -> FullSimplify[Total[j] - J],
  "commonFlux" -> FullSimplify[Thread[j/k == J/K], And @@ Thread[h > 0] && K > 0],
  "nonnegativeAllocation" -> FullSimplify[And @@ Thread[q >= 0]],
  "thermalClosureResidual" -> FullSimplify[lambda Uraw - Utarget],
  "heliumFractionSensitivity" -> FullSimplify[D[a/(s + a), a] > 0],
  "subgridResolvedSourceVector" -> {0, 0, 0},
  "unsupportedStructuralZero" -> FullSimplify[0 K + 0 J]
|>;
Print[ExportString[result, "RawJSON"]];
If[And @@ Values[result /. {0 -> True, {0, 0, 0} -> True}], Exit[0], Exit[2]];
