(* Two blocks below were executed separately in stateless Wolfram tool calls.
   Rust was not compiled. Use Wolfram *^ scientific notation, NOT Python e-16.
   Input digits are existing binary64 source values, not new physical precision. *)
ClearAll[u,x,b,m];
g=Exp[-2 x]((1-m^2)Exp[2 b[x]]+m^2 Exp[-4 b[x]]);
q=m^2 Exp[-4 b[x]]/((1-m^2)Exp[2 b[x]]+m^2 Exp[-4 b[x]]);
identity=FullSimplify[D[g,x]/(2g)+1-b'[x](1-3q),Assumptions->Element[{m,x,b[x],b'[x]},Reals]&&0<m<1];
badB=-2u^2+4u^3/3;badR=D[badB,u];badLogE=-u-2badB;
roots=u/.NSolve[badLogE==-1/50&&0<u<1,u,Reals,WorkingPrecision->40];
Print[<|"identity"->identity,"endpoint_bprime"->{badR/.u->0,badR/.u->1},"interior_min"->MinValue[{badR,0<=u<=1},u],"roots"->N[roots,17],"endpoint_residuals"->{badLogE+1/50/.u->0,badLogE+1/50/.u->1}|>];
ClearAll[herm,z];
rows=Rationalize[{{0.,0.047619047619047616,0.,0.,1.1835693720646417*^-16,-1.183510198034054*^-18,-1.7795494197516895*^-16,291.72150000000016,1.3655461718938338,1.1954044740449822*^-16,1.1598991681039607*^-16},{0.011959037710744356,0.04819194442463355,101956007295789.6,-0.00011851083565535744,1.1624783532484068*^-16,-1.1416116789266804*^-18,-1.7477564709347456*^-16,281.39427494630064,1.2868288294689356,1.1738944700376736*^-16,1.139646119669873*^-16},{0.023918075421488712,0.04877173365596635,205761774071336.25,-0.00023490018039277894,1.1417641287216675*^-16,-1.1011969675791535*^-18,-1.7165335374801974*^-16,271.4336796301782,1.2126382798843705,1.152776098397459*^-16,1.1197401893700844*^-16}},0];
If[!MatrixQ[rows,NumericQ],Print["NONNUMERIC_INPUT"];Abort[]];
herm[y0_,y1_,d0_,d1_,dx_,v_]:=(2v^3-3v^2+1)y0+(v^3-2v^2+v)dx d0+(-2v^3+3v^2)y1+(v^3-v^2)dx d1;
h0=Rationalize[2.1842852410855026*^-18,0];om=Rationalize[0.315,0];rad=Rationalize[0.000092,0];ol=Rationalize[0.6849080000000001,0];fm=1/10;
nodeChecks=Table[With[{a=r[[2]],hh=r[[5]],ss=r[[6]],hp=r[[7]],rho=r[[8]],pp=r[[9]]},{Abs[hh^2-(h0^2(om(1-fm)/a^3+rad/a^4+ol+rho)+ss^2)]/hh^2,Abs[hp-(h0^2(-3om(1-fm)/a^3-4rad/a^4-3(rho+pp))-6ss^2)/(2hh)]/Abs[hp],Abs[(hh-ss)/r[[10]]-1],Abs[(hh+2ss)/r[[11]]-1]}],{r,rows}];
cells=Table[Module[{l=rows[[i]],r=rows[[i+1]],dx,bp,lp,der,candidates,bounds,dt,root,efun},dx=r[[1]]-l[[1]];bp=herm[l[[4]],r[[4]],l[[6]]/l[[5]],r[[6]]/r[[5]],dx,z];lp=herm[Log[l[[5]]],Log[r[[5]]],l[[7]]/l[[5]],r[[7]]/r[[5]],dx,z];der=D[bp,z]/dx;candidates=Join[{0,1},Select[z/.Solve[D[der,z]==0,z],0<#<1&]];bounds={Min[der/.z->#&/@candidates],Max[der/.z->#&/@candidates]};dt=NIntegrate[Evaluate[dx Exp[-lp]],{z,0,1},WorkingPrecision->45,AccuracyGoal->28,PrecisionGoal->28];efun=Exp[-2dx z]((1-4/25)Exp[2(bp-l[[4]])]+(4/25)Exp[-4(bp-l[[4]])]);root=If[i==1,z/.FindRoot[Evaluate[efun==(Rationalize[13.602134599702,0]/Rationalize[13.605,0])^2],{z,1/100},WorkingPrecision->40],0];<|"cell"->i,"bprime_bounds"->N[bounds,17],"strict_expansion_margin"->N[Min[1-bounds[[2]],1+2bounds[[1]]],17],"H_mid_s^-1"->N[Exp[lp/.z->1/2],17],"Sigma_mid"->N[Sqrt[3]Abs[der/.z->1/2],17],"clock_integral_s"->N[dt,17],"clock_relative_vs_producer_increment"->N[(dt-(r[[3]]-l[[3]]))/(r[[3]]-l[[3]]),12],"firstcell_D_crossing_x"->If[i==1,N[dx root,17],Null],"firstcell_D_crossing_proper_s"->If[i==1,N[NIntegrate[Evaluate[dx Exp[-lp]],{z,0,root},WorkingPrecision->40,AccuracyGoal->25,PrecisionGoal->25],17],Null]|>],{i,1,2}];
Print[<|"node_residual_maxima"->N[Max/@Transpose[nodeChecks],12],"cells"->cells|>];
