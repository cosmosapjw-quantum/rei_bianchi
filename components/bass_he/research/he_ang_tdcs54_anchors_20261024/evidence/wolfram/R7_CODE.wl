AbsoluteTiming[Timing[
Module[{lo,hi,a,del,x,y,profiles,vs={{183/152,99/124},{129/76,151/124}}},
profiles=Map[Function[v,With[{mn=Min[v],mx=Max[v]},With[{af=(Min[v]+Max[v])/2,ac=Min[27/20,Max[13/20,(Min[v]+Max[v])/2]]},<|"ratios"->v,"freeA"->af,"freeDelta"->(mx-mn)/(mx+mn),"boundedA"->ac,"boundedDelta"->Max[(Abs[#/ac-1]&)/@v],"Q"->v[[1]]/v[[2]],"delta10Interval"->{mx/(11/10),mn/(9/10)}|>]]],vs];
<|
"feasibilityEquivalence"->FullSimplify[Equivalent[Abs[hi/a-1]<=del&&Abs[lo/a-1]<=del,hi/(1+del)<=a<=lo/(1-del)],Assumptions->0<lo<=hi&&a>0&&0<=del<1],
"minimumDeltaEquivalence"->FullSimplify[Equivalent[hi/(1+del)<=lo/(1-del),del>=(hi-lo)/(hi+lo)],Assumptions->0<lo<=hi&&0<=del<1],
"balancedErrors"->FullSimplify[{hi/((hi+lo)/2)-1,1-lo/((hi+lo)/2)}-{(hi-lo)/(hi+lo),(hi-lo)/(hi+lo)},Assumptions->0<lo<=hi],
"signedAngleIdentity"->FullSimplify[-Sin[x] Sin[y]+Cos[x] Cos[y]-Cos[x+y],Assumptions->Element[{x,y},Reals]],
"anchorPairAngleChecks"->FullSimplify[{Cos[214 Degree]-Cos[146 Degree],Cos[220 Degree]-Cos[140 Degree]}],
"experimentalRatio"->38/31,"modelRatios"->{61/33,258/151},
"profilesCDWThenCCC"->profiles,
"nominalRatioVsPrinted"->{91/109,84/100},
"conditionalPrintingOverlap"->Max[(91/100-1/200)/(109/100+1/200),84/100-1/200]<=Min[(91/100+1/200)/(109/100-1/200),84/100+1/200]
|>
]]]
