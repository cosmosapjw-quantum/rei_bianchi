ClearAll["Global`*"];
tau = sigma nH (1-x) R;
area = Pi R^2 (1-Exp[-tau]);
nCloud = kappa a^2 Mpc^2/area;
MCloud = FullSimplify[nCloud (4 Pi R^3 nH/3)];
<|
 "CloudMass" -> MCloud,
 "LimitMassIonized" -> Limit[MCloud,x->1,Direction->"FromBelow"],
 "ScaledLimit" -> FullSimplify[Limit[(1-x)MCloud,x->1,Direction->"FromBelow"],Assumptions->{sigma>0,nH>0,R>0,kappa>0,a>0,Mpc>0}],
 "PhotonPartition" -> FullSimplify[Jdiff+Jsink-Jtot /. Jdiff->Jtot-Jsink],
 "NucleiTransfer" -> FullSimplify[(Nd-dN)+(Ns+dN)-(Nd+Ns)]
|>
