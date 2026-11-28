Module[{ta, tb, thetaa, thetab, n32a, n32b, n64a, n64b,
  decomposition, closure, levelCancellation, candidates, corners, coherent},
 decomposition = Expand[(thetab-thetaa) + (tb-thetab) - (ta-thetaa)];
 closure = Expand[decomposition - (tb-ta)];
 levelCancellation = Expand[((n64b-thetab)-(n64a-thetaa)) -
   ((n32b-thetab)-(n32a-thetaa)) - ((n64b-n64a)-(n32b-n32a))];
 candidates = {{1, 2}, {11, 12}};
 corners = (#[[2]]-#[[1]]) & /@ Tuples[candidates];
 coherent = (#[[2]]-#[[1]]) & /@ Transpose[candidates];
 ExportString[<|"scope" -> "symbolic_signed_decomposition_and_manufactured_finite_candidates",
   "signedClosure" -> closure, "sharedReferenceLevelCancellation" -> levelCancellation,
   "productHull" -> {Min[corners], Max[corners]},
   "coherentHull" -> {Min[coherent], Max[coherent]},
   "productChoices" -> Length[corners], "coherentChoices" -> Length[coherent],
   "nativeCalls" -> 0, "trueSolutionErrorBound" -> False|>, "RawJSON"]
]
