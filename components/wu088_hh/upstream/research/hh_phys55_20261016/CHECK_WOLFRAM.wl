(* Independent PHYS55 algebra, source B=20 T=27 k=7/10 R=7/10. *)
ClearAll[xx,ell,s,k,rr,cc,dl,exlb,scup,ratio,margin,principal];
rr=27;k=7/10;dl=1/10^12;
exlb=Sum[(193/5)^n/n!,{n,0,30}];
scup=2 (1+10/193)/exlb;
ratio[ell_]=(ell(ell+1)/rr^2-59/100-dl)/(ell+1)^2;
margin=Together[ratio[21]-(9/1000)^2];
principal=FullSimplify[Limit[((ell+1)/rr-((2ell+1)/rr)*Sqrt[1+((-10/7)/(ell+1))^2])/(ell+1),ell->Infinity]];
Print["source screen bound <=1e-12: ",TrueQ[scup<10^-12]];
Print["exact margin ",margin];
Print["all ell ratio derivative positive: ",TrueQ[FullSimplify[D[ratio[xx],xx]>0,Assumptions->xx>=21]]];
Print["central Coulomb derivative recurrence principal limit in r units ",principal];
If[!TrueQ[scup<10^-12 && margin>0 && principal==-1/27 &&
    FullSimplify[D[ratio[xx],xx]>0,Assumptions->xx>=21]],Exit[5]];
Print["PHYS55 Wolfram exact scalar checks PASS"];
Exit[0];
