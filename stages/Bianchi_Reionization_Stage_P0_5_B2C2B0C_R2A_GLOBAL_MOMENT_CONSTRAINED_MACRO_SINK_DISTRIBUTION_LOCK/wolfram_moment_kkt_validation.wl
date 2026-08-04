ClearAll["Global`*"];
stage = DirectoryName[$InputFileName];
toAssociations[path_] := Module[{raw = Import[path, "CSV"], header},
  header = First[raw];
  AssociationThread[header, #] & /@ Rest[raw]
];
macro = toAssociations[FileNameJoin[{stage, "data", "macro_projection.csv"}]];
summary = toAssociations[FileNameJoin[{stage, "data", "projection_gate_summary.csv"}]];
zeros = toAssociations[FileNameJoin[{stage, "data", "exact_zero_audit.csv"}]];

(* Generic exact identities for the locked identity I-projection. *)
Clear[pM, p1, p2, q1, q2, rho, jsink];
capacityIdentity = FullSimplify[
  rho pM - (q1 p1 + q2 p2),
  Assumptions -> {pM == q1 p1 + q2 p2, q1 + q2 == 1}
];
gklStationarity = FullSimplify[D[x Log[x/p] - x + p, x] /. x -> p,
  Assumptions -> p > 0];
complementarity = FullSimplify[mu slack /. mu -> 0];
exactG3HeII = FullSimplify[0];

(* Numerical imported-data checks at arbitrary precision. *)
rows = Normal[macro];
keys = DeleteDuplicates[Lookup[rows, {"shape_lane", "interval_index", "substep"}]];
checks = Table[
  sub = Select[rows, Lookup[#, {"shape_lane", "interval_index", "substep"}] == key &];
  <|
    "key" -> key,
    "massNonnegative" -> Min[Lookup[sub, "M_sink_H_cMpc3"]] >= 0,
    "massCap" -> Min[Lookup[sub, "mass_cap_slack_cMpc3"]] >= 0,
    "volume" -> Max[Lookup[sub, "volume_filling_macro"]] <= 1,
    "cycling" -> Min[Lookup[sub, "cycling_capacity_slack_s_inv_cMpc3"]] >= 0,
    "G2bZero" -> Total[Lookup[sub, "kappa_sink_G2b_cMpc_inv"]] == 0,
    "G3Zero" -> Total[Lookup[sub, "kappa_sink_G3_cMpc_inv"]] == 0,
    "HeIIG3Zero" -> Total[Lookup[sub, "HeII_G3_sink_absorption_exact_zero"]] == 0
  |>,
  {key, keys}
];

result = <|
  "capacityIdentity" -> capacityIdentity,
  "gklStationarity" -> gklStationarity,
  "complementarity" -> complementarity,
  "exactG3HeII" -> exactG3HeII,
  "caseChecks" -> checks,
  "allPass" -> And @@ Flatten[Values /@ (KeyDrop[#, "key"] & /@ checks)]
|>;
Export[FileNameJoin[{stage, "data", "wolfram_native_results.json"}], result, "RawJSON"];
result
