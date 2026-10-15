(* Exact rational small-shear radiation angular moment coefficients.
   Wolfram Engine15, stateless scalar CAS; no source-collision/Thomson coupling. *)
Clear[bb, k, dd, s0, s2, m0, m2, expected0, expected2];
dd=Exp[-6 bb]-1;
s0=Sum[Binomial[1/2,k] dd^k/(2 k+1),{k,0,14}];
s2=Sum[Binomial[-1/2,k] dd^k/(2 k+3),{k,0,14}];
m0=Normal[Series[Exp[bb]s0,{bb,0,14}]];
m2=Normal[Series[Exp[bb]/2(3 Exp[-6 bb]s2-s0),{bb,0,14}]];
expected0={
 1,0,8/5,-16/21,8/35,16/231,4528/32175,
 -2656/15015,-254248/3828825,25107568/183324141,
 10458544/195859125,-644335456/5547967425,
 -732698224/17375502375,4574816/46334673,
 1570056394912/45853950767625};
expected2={
 0,-8/5,8/7,-16/35,-40/231,-4528/10725,1328/2145,
 1016992/3828825,-12553784/20369349,-10458544/39171825,
 322167728/504360675,1465396448/5791834125,
 -29736304/46334673,-1570056394912/6550564395375,
 13886441783391392/21890676096464175};
If[Table[Coefficient[m0,bb,k],{k,0,14}]=!=expected0 ||
   Table[Coefficient[m2,bb,k],{k,0,14}]=!=expected2,
  Print["FAIL_TAYLOR14_RATIONAL_MOMENTS"];
  Exit[3]
];
r=2/5;
eta=(1/40)/r;
eBound=Exp[4r]eta^15/(1-eta);
qBound=(Exp[r]/2)(Exp[9r]/Sqrt[Cos[3r]]+Exp[3r]) eta^15/(1-eta);
If[!(0<eBound<6/10^18 && 0<qBound<5/10^17),
  Print["FAIL_CONSERVATIVE_CAUCHY_BOUND"];Exit[4]];
Print["WOLFRAM15_14TH_ORDER_ANALYTIC_PASS"];
Print["energy_bound=",N[eBound,18]];
Print["quadrupole_bound=",N[qBound,18]];
Print["energy_coefficient_14=",Last[expected0]];
Print["quad_coefficient_14=",Last[expected2]];
Exit[0];
