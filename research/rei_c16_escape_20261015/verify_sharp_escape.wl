(* Fixed-Bianchi angular positive escape pressure theorem extending original C16/PR144.
   Signature (-,+,+,+), comoving intensity massless, d=b(t)-b(t_emit).
   z=mu_emit^2 in [0,1], A=exp(2d)>0, B=exp(-4d)>0.
   P2 current photon angular pressure normalized per emitted positive energy:
      f(z)=(3Bz/sqrt(A+(B-A)z)-sqrt(A+(B-A)z))/2.
   f'(z)>0 for A,B>0, all real d; extremum at transverse z0 or axial z1.
   This is a mathematically exact *fixed-geometry positive light ray* bound.
*)
Clear[aa,bb,zz,dd,rr,ff,der,numerator,ends];
rr=Sqrt[aa+(bb-aa)zz];
ff=(3bb zz/rr-rr)/2;
der=FullSimplify[D[ff,zz]];
numerator=aa(aa+5bb)+(bb-aa)(aa+2bb)zz;
If[!TrueQ[FullSimplify[
  der==numerator/(4 (aa+(bb-aa)zz)^(3/2)),
  Assumptions->aa>0&&bb>0&&0<=zz<=1]],
  Print["FAIL_PR144_SHARP_KILLING_DERIVATIVE"];Exit[3]];
ends=FullSimplify[numerator/.{{zz->0},{zz->1}}];
If[!TrueQ[FullSimplify[ends=={aa(aa+5bb),2bb(2aa+bb)}]],
  Print["FAIL_ALL_ANGULAR_EXTREMAL_POSITIVITY"];Exit[4]];
If[!TrueQ[FullSimplify[
  {ff/.zz->0,ff/.zz->1}=={-Sqrt[aa]/2,Sqrt[bb]},
  Assumptions->aa>0&&bb>0]],
  Print["FAIL_TRANSVERSE_VS_AXIAL_ENVELOPE"];Exit[5]];
If[!TrueQ[FullSimplify[
  ({Sqrt[aa]/2, Sqrt[bb]} /.{aa->Exp[2dd],bb->Exp[-4dd]}) ==
    {Exp[dd]/2,Exp[-2dd]},Assumptions->Element[dd,Reals]]],
  Print["FAIL_ALL_REAL_BIANCHI_REDSHIFT_PROJECTION"];Exit[6]];
(* The homogeneous signed-shear linear response Green kernel is strictly positive. *)
Clear[xx,xo,shear,pressure,HH,kap,yy];
gg=Exp[-3(xo-xx)]*kap/HH;
If[!TrueQ[FullSimplify[gg>0,
    Assumptions->Element[{xx,xo},Reals]&&xx<=xo&&kap>0&&HH>0]],
  Print["FAIL_POSITIVE_LINEAR_SHEAR_GREEN"];Exit[7]];
Print["REI_C16_CASEA_ESCAPE_EXACT_ANGULAR_MONOTONE_AND_GREEN_BOUND_PASS"];
Print["Angle derivative numerator positive at z=0 and z=1; sharp positive source extremizers attained"];
Print["Pressure lower=-U_emit(a_emit/a)e^(delta_b)/2 upper=U_emit(a_emit/a)e^(-2delta_b)"];
Print["Scope: fixed C16 background linearized source response, not complete Einstein stellar reservoir"];
Exit[0];
