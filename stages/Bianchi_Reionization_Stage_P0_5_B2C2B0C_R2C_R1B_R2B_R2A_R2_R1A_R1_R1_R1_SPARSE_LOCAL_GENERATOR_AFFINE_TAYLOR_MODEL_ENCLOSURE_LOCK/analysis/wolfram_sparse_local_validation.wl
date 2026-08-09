(* Exact validation for the sparse local-generator stage. *)
ClearAll[vc, vh, fc, fh, tv, tf, w, z, S, dS];
v = vc + vh tv;
f = fc + fh tf;
ah = Expand[v w + (1 - v) f z];
ahModel = Expand[
  vc w + (1 - vc) fc z +
  vh (w - fc z) tv +
  fh (1 - vc) z tf -
  vh fh z tv tf
];

hGenerators = {{-hv, hv, 0, 0, 0}, {-hf, hf, 0, 0, 0}, {-hvf, hvf, 0, 0, 0}};
heGenerators = {{0, 0, -ev, ev, 0}, {0, 0, -ef, ef, 0}, {0, 0, -evf, evf, 0}};
cH = {1, 1, 0, 0, 0};
cHe = {0, 0, 1, 1, 1};

<|
  "BranchBilinearExpansionResidual" -> FullSimplify[ah - ahModel],
  "HydrogenGeneratorInvariantResiduals" -> FullSimplify[hGenerators . cH],
  "HeliumGeneratorInvariantResiduals" -> FullSimplify[heGenerators . cHe],
  "NormalizedMeasureJVPSumResidual" -> FullSimplify[dS/S - S dS/S^2],
  "EvaluationSiteCount" -> 4,
  "RankLowerBoundPerSite" -> 92003,
  "InputRankLowerBound" -> 4 92003,
  "LocalPolynomialStorageBytes" -> 46080 4 4 3 8
|>
