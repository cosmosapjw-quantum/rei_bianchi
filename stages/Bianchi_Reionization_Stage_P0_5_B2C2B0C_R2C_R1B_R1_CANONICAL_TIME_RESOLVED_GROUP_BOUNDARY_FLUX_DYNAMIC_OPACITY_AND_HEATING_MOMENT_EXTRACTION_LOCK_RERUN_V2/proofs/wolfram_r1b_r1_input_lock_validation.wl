(* R1B-R1 conditional disintegration and heating-kernel identities. *)
ClearAll[h1,h2,h3,Ktot,Jtot,c,tau,sig];
ass = h1 >= 0 && h2 >= 0 && h3 >= 0 && h1+h2+h3 > 0 && Ktot > 0 && Jtot >= 0;
h = {h1,h2,h3};
csol = FullSimplify[Solve[c Total[h] == 1,c],ass];
q = FullSimplify[c h /. First[csol],ass];
kap = FullSimplify[Ktot q,ass];
phi = Jtot/Ktot;
cur = FullSimplify[phi kap,ass];
result = <|
 "UniqueDensityConstant" -> csol,
 "QSum" -> FullSimplify[Total[q],ass],
 "KappaSum" -> FullSimplify[Total[kap],ass],
 "CurrentSum" -> FullSimplify[Total[cur],ass],
 "CommonFluxOnPositiveSupport" -> FullSimplify[cur/kap,ass && h1>0 && h2>0 && h3>0],
 "NonnegativeQ" -> FullSimplify[And@@Thread[q>=0],ass],
 "ThinKernelLimit" -> FullSimplify[Limit[(1-Exp[-tau sig])/tau,tau->0,Direction->"FromAbove"],sig>=0],
 "ThickKernelLimit" -> FullSimplify[Limit[1-Exp[-tau sig],tau->Infinity],sig>0],
 "ExactZeroSupport" -> FullSimplify[1-Exp[-tau 0]]
 |>;
Print[ExportString[result,"RawJSON"]];
If[result["QSum"] =!= 1 || result["KappaSum"] =!= Ktot ||
   result["CurrentSum"] =!= Jtot || result["NonnegativeQ"] =!= True ||
   result["ThinKernelLimit"] =!= sig || result["ThickKernelLimit"] =!= 1 ||
   result["ExactZeroSupport"] =!= 0, Exit[1], Exit[0]];
