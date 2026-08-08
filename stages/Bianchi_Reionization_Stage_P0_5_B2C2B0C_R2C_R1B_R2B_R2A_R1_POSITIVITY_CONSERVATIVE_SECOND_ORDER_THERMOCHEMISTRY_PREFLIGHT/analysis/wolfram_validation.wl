Module[
 {g = 1 - 1/Sqrt[2], amat, bvec, cvec, direct, sequential, rhs, weights},
 amat = {{g, 0}, {1 - g, g}};
 bvec = {1 - g, g};
 cvec = Total /@ amat;
 direct = {{0, 0, 0}, {0, 0, 0}, {1, 0, 0}};
 sequential = {{0, 0, 0}, {1, 0, 0}, {0, 1, 0}};
 rhs[m_] := Total[m, {2}] - Total[m, {1}];
 weights = {2, 3, 5, 7};
 <|
   "SDIRKOrder1Residual" -> FullSimplify[Total[bvec] - 1],
   "SDIRKOrder2Residual" -> FullSimplify[bvec.cvec - 1/2],
   "SDIRKStiffAccuracyResidual" -> FullSimplify[bvec - Last[amat]],
   "SDIRKStabilityLimit" -> FullSimplify[
     Limit[1 + z bvec.Inverse[IdentityMatrix[2] - z amat].{1, 1}, z -> -Infinity]
   ],
   "OwnerFractionSumResidual" -> FullSimplify[Total[weights/Total[weights]] - 1],
   "OwnerOpacitySumResidual" -> FullSimplify[Total[k weights/Total[weights]] - k],
   "OwnerCurrentSumResidual" -> FullSimplify[Total[j weights/Total[weights]] - j],
   "HydrogenNucleiResidual" -> FullSimplify[(-a + r) + (a - r)],
   "HeliumNucleiResidual" -> FullSimplify[(-a1 + r1) + (a1 - r1 - a2 + r2) + (a2 - r2)],
   "SubgridResolvedSourceVector" -> {0, 0, 0},
   "DirectHeliumRHS" -> rhs[direct],
   "SequentialHeliumRHS" -> rhs[sequential],
   "PDSNetRHSNonunique" -> (rhs[direct] == rhs[sequential] && direct != sequential)
 |>
]
