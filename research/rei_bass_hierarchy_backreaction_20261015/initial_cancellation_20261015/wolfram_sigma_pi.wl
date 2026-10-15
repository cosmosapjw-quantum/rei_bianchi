ClearAll[ssP,ppP,qSigned,HFsource,Gnew,cLight,ARtt,SShear,HHubble,PiPhysical,timeVar,kR,muAx];
matS=DiagonalMatrix[{-ssP,-ssP,2 ssP}];
matPi=DiagonalMatrix[{-ppP,-ppP,2 ppP}];
res0=FullSimplify[Tr[matS]];
res1=FullSimplify[Tr[matPi]];
res2=FullSimplify[Tr[matS.matS]/2-3 ssP^2];
res3=FullSimplify[Tr[matS.matPi]-6 ssP ppP];
res4=FullSimplify[(D[ARtt[timeVar]^3 SShear[timeVar],timeVar]/.
 {Derivative[1][ARtt][timeVar]->ARtt[timeVar] HHubble[timeVar],
 Derivative[1][SShear][timeVar]->-3 HHubble[timeVar] SShear[timeVar]
 +(8 Pi Gnew/cLight^2)PiPhysical[timeVar]})
 -(8 Pi Gnew/cLight^2) ARtt[timeVar]^3 PiPhysical[timeVar]];
res5=FullSimplify[Integrate[(1+kR (3 muAx^2-1)/2)*(3 muAx^2-1)/2,{muAx,-1,1}]/2-kR/5];
res6=FullSimplify[Sqrt[3]Abs[qSigned]/Sqrt[1+qSigned^2]
 -Sqrt[3]Abs[qSigned HFsource]/Sqrt[HFsource^2+(qSigned HFsource)^2],
 Assumptions->HFsource>0&&Element[qSigned,Reals]];
all={res0,res1,res2,res3,res4,res5,res6};
out=<|"schema"->"rei.axbi.massive_gamma_nu_initial_pi.wolfram.v1",
 "Wolfram_kernel"->System`$Version,
 "metric_signature"->"(-,+,+,+)",
 "shear_matrix"->"diag(-s,-s,2s)",
 "pi_matrix"->"diag(-pi_s,-pi_s,2pi_s)",
 "source_checks"->AssociationThread[
 {"tracefree_shear","tracefree_pi","sigma_norm_squared_over2",
 "sigma_pi_stress_work","Green_a3shear_identity","positive_P2_initial_pi",
 "signed_q_vs_unsigned_Sigma"},Map[ToString[#,InputForm]&,all]],
 "all_zero"->And@@Map[TrueQ[#===0]&,all],
 "scientific_scope"->"source Einstein tensor algebra and positive initial l2 distribution, not full Einstein-Boltzmann chemical admission"|>;
Export["/home/cosmosapjw/rec_theory_runs/REI_SIGMA_PI_INITIAL_CANCELLATION_20261015/checkout/research/rei_bass_hierarchy_backreaction_20261015/initial_cancellation_20261015/evidence/WOLFRAM_SOURCE_CHECKS.json",out,"RawJSON"];
Print[ExportString[out,"RawJSON"]];
If[TrueQ[out["all_zero"]],Exit[0],Exit[1]];