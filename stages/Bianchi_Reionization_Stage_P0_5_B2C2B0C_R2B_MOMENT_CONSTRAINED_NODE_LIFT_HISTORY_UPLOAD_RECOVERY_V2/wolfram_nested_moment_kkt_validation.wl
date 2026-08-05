(* R2B symbolic KKT and sampled moment validation. *)
ClearAll[q, mu, lam, s, c, x, rowSum, lambdaStar, rel, toNumber];
args = Rest[$ScriptCommandLine];
If[Length[args] < 1, Print["usage: wolframscript -file wolfram_nested_moment_kkt_validation.wl STAGE_DIR"]; Exit[2]];
stage = First[args];
toNumber[str_String] := ToExpression[StringReplace[str, RegularExpression["[eE]\\+?"] -> "*^"]];
sample = Import[FileNameJoin[{stage, "data", "wolfram_sample_input.json"}], "RawJSON"];
pairs = AssociationMap[{toNumber[#actual], toNumber[#target]} &, sample["pairs"]];

x = q Exp[-mu-lam];
stationarity = FullSimplify[Log[x/q] + mu + lam == 0,
  Assumptions -> {q > 0, Element[{mu, lam}, Reals]}];
activeRow = FullSimplify[s Exp[-Log[s/c]] == c, Assumptions -> {s > c > 0}];
inactiveRow = FullSimplify[s <= c, Assumptions -> {0 < s <= c}];
lambdaStar = Piecewise[{{Log[s/c], s > c}}, 0];
rowSum = s Exp[-lambdaStar];
complementarity = FullSimplify[lambdaStar (c-rowSum) == 0, Assumptions -> {s > 0, c > 0}];
rel[a_, b_] := Abs[a-b]/Max[Abs[a], Abs[b], 10^-300];
residuals = Map[rel[#[[1]], #[[2]]] &, pairs];
result = <|
  "symbolic" -> <|
    "stationarity" -> stationarity,
    "activeRow" -> activeRow,
    "inactiveRow" -> inactiveRow,
    "complementarity" -> complementarity|>,
  "residuals" -> residuals,
  "maxResidual" -> Max[Values[residuals]],
  "passAt1e-11" -> And @@ Map[# <= 10^-11 &, Values[residuals]]|>;
Export[FileNameJoin[{stage, "data", "wolfram_native_result.json"}], result, "RawJSON"];
Print[InputForm[result]];
If[TrueQ[result["passAt1e-11"]] && And @@ Values[result["symbolic"]], Exit[0], Exit[1]];
