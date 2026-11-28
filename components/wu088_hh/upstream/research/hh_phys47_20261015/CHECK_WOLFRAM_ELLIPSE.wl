(* PHYS47 exact source geometry and angular momentum selection checks. *)
ClearAll["Global`*"];
B=20; R=7/10; rho=18;
chi=(rho+1/rho)/2;
d=2(R/B)chi+(R/B)^2;
g=30283269124863/50000000000000;
Dshift=814075000000000/103221346017681;
checks={FullSimplify[d-227941/360000],
 FullSimplify[Dshift-(2 R chi+R^2/B)/(1+g)]};
Print["PHYS47_EXACT_RATIONAL_ZEROS=",checks];
Print["PHYS47_BRANCH_AND_RADIUS=",{TrueQ[d<1],TrueQ[g^2<=1-d],TrueQ[Dshift<B]}];
