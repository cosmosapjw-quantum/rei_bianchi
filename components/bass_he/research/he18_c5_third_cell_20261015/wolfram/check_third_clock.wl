Module[{u,mu,dt,shearRate,z,volume,logb,leftSlope,rightSlope,left,right,bfun,
          shear,expected,hermite,checks,out},
 z=2+u;
 logb=Log[Sqrt[Exp[2 bfun[u]](1-mu^2)+Exp[-4 bfun[u]]mu^2]]-Log[volume[z]]/3;
 shear=D[logb,u]/.Derivative[1][bfun][u]->dt shearRate/volume[z];
 expected=dt shearRate/volume[z]*(Exp[2 bfun[u]](1-mu^2)-2 Exp[-4 bfun[u]]mu^2)/
   (Exp[2 bfun[u]](1-mu^2)+Exp[-4 bfun[u]]mu^2)-Derivative[1][volume][z]/(3 volume[z]);
 hermite=left+dt leftSlope u+
   (3(right-left)-dt(2leftSlope+rightSlope))u^2+
   (-2(right-left)+dt(leftSlope+rightSlope))u^3;
 checks=<|
 "T01_full_global_clock"->TrueQ[FullSimplify[shear-expected]==0],
 "T02_parallel_redshift"->TrueQ[FullSimplify[(shear/.mu->1)+Derivative[1][volume][z]/(3volume[z])+2dt shearRate/volume[z]]==0],
 "T03_transverse_redshift"->TrueQ[FullSimplify[(shear/.mu->0)+Derivative[1][volume][z]/(3volume[z])-dt shearRate/volume[z]]==0],
 "T04_hermite_left"->TrueQ[FullSimplify[(hermite/.u->0)-left]==0],
 "T05_hermite_right"->TrueQ[FullSimplify[(hermite/.u->1)-right]==0],
 "T06_hermite_slope_left"->TrueQ[FullSimplify[(D[hermite,u]/.u->0)-dt leftSlope]==0],
 "T07_hermite_slope_right"->TrueQ[FullSimplify[(D[hermite,u]/.u->1)-dt rightSlope]==0],
 "T08_positive_probability_slope"->TrueQ[FullSimplify[D[1-Exp[-u],u]>0,0<=u<1]]
 |>;
 out=<|"schema"->"he18.c5.wolfram_clock.v1","kernel"->$Version,
   "checks"->checks,"expected_count"->8,"actual_count"->Length[checks],
   "all_pass"->Length[checks]==8&&And@@Values[checks],
   "status"->"symbolic-identity-only; no interval method or source IVP executed"|>;
 Print[ExportString[out,"RawJSON"]];
 Exit[If[TrueQ[out["all_pass"]],0,2]]
]