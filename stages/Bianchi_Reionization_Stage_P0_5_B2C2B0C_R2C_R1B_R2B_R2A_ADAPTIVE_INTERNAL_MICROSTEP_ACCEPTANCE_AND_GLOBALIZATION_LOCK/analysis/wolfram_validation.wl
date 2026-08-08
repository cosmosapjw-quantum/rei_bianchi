ClearAll["Global`*"];
q = Table[h[i]/Sum[h[j], {j, 1, 4}], {i, 1, 4}];
hi1 = hi0 - aHI + rH; hii1 = hTot - hi1;
hei1 = hei0 - aHeI + rHeII;
heiii1 = heiii0 + aHeII - rHeIII;
heii1 = heTot - hei1 - heiii1;
result = <|
  "HydrogenNucleiResidual" -> FullSimplify[hi1 + hii1 - hTot],
  "HeliumNucleiResidual" -> FullSimplify[hei1 + heii1 + heiii1 - heTot],
  "OwnerFractionSumResidual" -> FullSimplify[Total[q] - 1],
  "OwnerCurrentSumResidual" -> FullSimplify[Total[J q] - J],
  "UniformSubstepBudgetResidual" -> FullSimplify[n (J dt/n) - J dt,
    Assumptions -> n >= 1 && Element[n, Integers]],
  "DampedPicardConvexIdentity" -> FullSimplify[
    y + lambda (g - y) - ((1 - lambda) y + lambda g)],
  "SubgridResolvedSourceVector" -> {0, 0, 0}
|>;
InputForm[result]
