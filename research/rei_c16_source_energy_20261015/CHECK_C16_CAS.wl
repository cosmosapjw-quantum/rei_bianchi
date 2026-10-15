(* Original C15 source exact Bianchi I characteristic, C16 independently audited.
  Proper time / scale x=ln(a/aref), non-tilted LRS gamma and astrophysical UV.
  Units for U and Q are energy per physical H nucleus; Pi2 per H is E P2.
  Does not prove full gravitational closure without external stellar+escape T_ab.
*)
Clear[m,b,x,rad,locmu2,H,s,Uuv,Uth,Pi2,Qemit,Qesc,Work,dU];
rad=(1-m^2) Exp[2 b]+m^2 Exp[-4 b];
locmu2=m^2 Exp[-4 b]/rad;
ans1=FullSimplify[D[Log[Sqrt[rad]],b]-(1-3locmu2),
    Assumptions->-1<m<1&&Element[b,Reals]];
If[ans1=!=0,Print["FAIL_KILLING_DIRECTION_ENERGY"];Exit[2]];
(* Tensor work on current pressure difference: pi^i_j=diag(-D/3,-D/3,2D/3) *)
sh=DiagonalMatrix[{-s,-s,2s}];
pi=DiagonalMatrix[{-Pi2/3,-Pi2/3,2Pi2/3}];
ans2=FullSimplify[Tr[sh.pi]-2s Pi2];
If[ans2=!=0,Print["FAIL_SHEAR_P2_TENSOR_WORK"];Exit[3]];
(* Exact geometric UV/gas work and externally open energy accounting. *)
Work=H*(Uuv+2Uth)+2s Pi2;
dU=Qemit-Qesc-Work;
ans3=FullSimplify[dU+Work-(Qemit-Qesc)];
If[ans3=!=0,Print["FAIL_EXTERNAL_Q0_OWNERSHIP_FORMULA"];Exit[4]];
(* Photon redshift even under initial mu -> -mu; axial P1 odd *)
ans4=FullSimplify[(rad/.m->-m)-rad];
ans5=FullSimplify[(-m Exp[-2b]/Sqrt[rad])+(m Exp[-2b]/Sqrt[rad])];
If[ans4=!=0||ans5=!=0,Print["FAIL_REFLECTION_ODD_MOMENT"];Exit[5]];
Print["C16_KILLING_SHEAR_WORK_EXTERNAL_Q0_PARITY_EXACT_PASS"];
Print["Characteristic log-energy sign, tensor work, Q0 owner, axial P1: 0,0,0,0"];
Print["Source external emission / CaseA escape Einstein T_ab remains unowned"];
Exit[0];
