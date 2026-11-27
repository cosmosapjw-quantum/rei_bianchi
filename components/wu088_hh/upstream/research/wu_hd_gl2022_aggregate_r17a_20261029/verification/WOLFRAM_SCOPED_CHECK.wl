Module[{nu = {-1,-1,1,1}, totals, experimental, halfwidth, w, K, a, b, checks, gam, amp},
 totals = {121/100,221/100}; experimental = {11/10,17/10}; halfwidth={1/5,1/5};
 w={1/4,3/4};K=121/100;
 a={K/w[[1]],0};b={0,K/w[[2]]};
 checks = { totals[[1]]-experimental[[1]] == 11/100,
  totals[[2]]-experimental[[2]] == 51/100,
  (totals[[1]]-experimental[[1]])/halfwidth[[1]] == 11/20,
  (totals[[2]]-experimental[[2]])/halfwidth[[2]] == 51/20,
  Dot[{1,1,0,2},nu] == 0,Dot[{0,1,1,0},nu]==0,Dot[{1,0,1,0},nu]==0,
  totals[[1]]/10^16==121/10^18,totals[[2]]/10^16==221/10^18,
  w.a==K,w.b==K,a!=b,Total[w]==1};
 gam=N[Log[221/121]/(1/205-1/295),45];amp=N[(121/100)Exp[gam/205],45];
 <|"count"->Length[checks],"allTrue"->And@@checks,"failedIndices"->Flatten@Position[checks,False],
 "gammaFromTwoPrintedPoints_K"->gam,"alphaFromTwoPrintedPoints_in_1e-10_cm3_s"->amp,
 "authorPrintedGamma_K"->405,"sourceStatesRecovered"->0|>
]
