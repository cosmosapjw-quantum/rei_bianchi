(* Exact local-angle free-streamed massless-radiation expansion.
   Uses physical local mu, b=0 initially, LRS Bianchi I (-,+,+,+).
   It is NOT a new coupled reionization RHS or observational signal. *)
Clear[bb,mm,dd,p2,series,mono,quad,expected0,expected2];
dd=(1-mm^2) Exp[-2 bb]+mm^2 Exp[4 bb];
p2=(3 mm^2-1)/2;
series=Normal[Series[dd^(-2),{bb,0,6}]];
mono=Table[FullSimplify[Integrate[Coefficient[series,bb,k],{mm,-1,1}]/2],{k,0,6}];
quad=Table[FullSimplify[Integrate[p2 Coefficient[series,bb,k],{mm,-1,1}]/2],{k,0,6}];
expected0={1,0,8/5,-16/21,8/35,16/231,4528/32175};
expected2={0,-8/5,8/7,-16/35,-40/231,-4528/10725,1328/2145};
If[mono=!=expected0 || quad=!=expected2,
 Print["FAIL_6TH_ORDER_EXACT_RATIONAL_COEFFICIENTS"];
 Print[mono];Print[quad];Exit[2]];
Print["WOLFRAM15_EXACT_BIANCHI_I_MOMENTS_PASS"];
Print["ENERGY_0_TO_6=", InputForm[mono]];
Print["QUAD_0_TO_6=",InputForm[quad]];
Print["ODD_SIGNED_ENERGY_DIFF_B_MINUS_MINUS_B=", InputForm[-32 bb^3/21+32 bb^5/231]];
Print["ODD_SIGNED_QUAD_DIFF_B_MINUS_MINUS_B=", InputForm[-16 bb/5-32 bb^3/35-9056 bb^5/10725]];
Exit[0];
