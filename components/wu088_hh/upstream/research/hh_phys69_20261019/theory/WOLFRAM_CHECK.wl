Clear[j, r, z, n, LL, xx, tt, BB];
kk=7/10; aa=(j-1)/kk; rr=(j+1)/kk;
nu[zz_]:=kk^2+2/zz-j(j+1)/zz^2;
exponent=2*(j(j+1)/aa^2-2/aa)/kk^2;
targetExponent=2+(14j+182)/(49(j-1)^2);
checks=<|
"nu_anchor"->Together[nu[aa]+(7j+91)/(100(j-1)^2)],
"nu_allowed"->Together[nu[rr]-189/(100(j+1))],
"transition_exponent"->Together[exponent-targetExponent],
"exponent_positive_polynomial"->Expand[(49j^2-378j-3591)/.j->20+n]-(49n^2+1582n+8449),
"mode_lower_endpoint"->FullSimplify[aa>=27,Assumptions->j>=20],
"nu_max_half"->FullSimplify[kk^2+1/(j(j+1))<=1/2,Assumptions->j>=20]
|>;
g=xx^(LL+1)/(1-xx); weighted=Expand[xx D[xx D[g,xx]+g,xx]+xx D[g,xx]+g];
closed=xx^(LL+1)*((LL+2)^2/(1-xx)+2(LL+2)xx/(1-xx)^2+xx(1+xx)/(1-xx)^3);
checks["geometric_tail"]=FullSimplify[weighted-closed,Assumptions->{Element[LL,Integers],LL>=0,0<xx<1}];
checks["radial_factor"]=Integrate[Integrate[Exp[-2(tt-BB)],{tt,r,Infinity}]^2,{r,BB,Infinity},Assumptions->Element[BB,Reals]];
terms=60; v=41/20; sum=Sum[v^n/n!,{n,0,terms}]; up=sum+(v^terms/terms!)*v/(terms+1)/(1-v/(terms+2));
checks["exp_rational_upper_below_8"]=TrueQ[up<8];
checks["exp_rational_upper_display"]=N[up,25];
checks["associated_selection_zero"]=Integrate[LegendreP[2,1,xx]*LegendreP[4,1,xx]*xx,{xx,-1,1}];
checks["associated_first_allowed"]=Integrate[LegendreP[2,1,xx]*LegendreP[4,1,xx]*xx^2,{xx,-1,1}];
ExportString[checks,"RawJSON"]
