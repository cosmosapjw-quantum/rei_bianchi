ClearAll[alpha, beta, b00, b10, b01, b11, s, a, b, xHeI, xHeII, xHeIII];
weights = {(1-alpha) (1-beta), alpha (1-beta), (1-alpha) beta, alpha beta};
multiaffine = Total[weights {b00, b10, b01, b11}];
<|
 "CornerWeightSumResidual" -> FullSimplify[Total[weights] - 1],
 "NonnegativeCornerWeightDomain" ->
  Reduce[And @@ Thread[weights >= 0] && 0 <= alpha <= 1 && 0 <= beta <= 1,
   {alpha, beta}, Reals],
 "MultiAffineCornerForm" -> multiaffine,
 "ConstantOrthantSignReversalFeasible" -> FullSimplify[
  Reduce[Element[s, Integers] && s^2 == 1 && a < 0 < b && s a >= 0 && s b >= 0,
   {s, a, b}, Reals]],
 "HydrogenInvariantResidual" -> FullSimplify[-1 + 1],
 "HeliumInvariantResiduals" -> {FullSimplify[-1 + 1 + 0], FullSimplify[0 - 1 + 1]},
 "DirectNeutralConditionalSimplexResidual" -> FullSimplify[
  xHeI + xHeII + xHeIII - 1 /.
   xHeII -> (1 - xHeI) (1 - xHeIII/(1 - xHeI))]
|>
