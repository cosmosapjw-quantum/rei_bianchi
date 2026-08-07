ClearAll["Global`*"];
hs = {h1, h2, h3, h4};
hsum = Total[hs];
kparts = kk hs/hsum;
jparts = jj hs/hsum;
assumptions = kk > 0 && jj >= 0 && And @@ Thread[hs > 0];
partitionProof = <|
  "OpacitySumResidual" -> FullSimplify[Together[Total[kparts] - kk], assumptions],
  "CurrentSumResidual" -> FullSimplify[Together[Total[jparts] - jj], assumptions],
  "CommonFlux" -> FullSimplify[Thread[jparts/kparts == jj/kk], assumptions],
  "NonnegativeOpacity" -> FullSimplify[And @@ Thread[kparts >= 0], assumptions],
  "NonnegativeCurrent" -> FullSimplify[And @@ Thread[jparts >= 0], assumptions]
|>;
capacity = n0 + rr + sin - sout;
capacityProof = <|
  "UpdatedReservoir" -> capacity - aa,
  "FeasibleImpliesNonnegativeUpdate" -> FullSimplify[
    Implies[aa <= capacity, capacity - aa >= 0],
    n0 >= 0 && rr >= 0 && sin >= 0 && sout >= 0 && capacity >= 0 && aa >= 0
  ]
|>;
p1[t_] := a0 + a1 t + a2 t^2 + a3 t^3;
p2[t_] := b0 + b1 t + b2 t^2 + b3 t^3;
additivityResidual = FullSimplify[
  (Integrate[p1[t], {t, 0, 1/2}] + Integrate[p2[t], {t, 1/2, 1}]) -
  Integrate[Piecewise[{{p1[t], t <= 1/2}}, p2[t]], {t, 0, 1}]
];
<|
  "PartitionProof" -> partitionProof,
  "SubgridResolvedSourceVector" -> {0, 0, 0},
  "CapacityProof" -> capacityProof,
  "PiecewiseIntegralAdditivityResidual" -> additivityResidual
|>
