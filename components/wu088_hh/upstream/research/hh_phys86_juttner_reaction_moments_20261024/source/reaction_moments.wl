(* Constructed finite exponential family. Energies in epsilon0 units.
   No physical nuclear cross sections, continuum quadrature or Bessel numerics. *)
ClearAll[PHYS86ExactQ,PHYS86Fail,PHYS86Moments,PHYS86TemperatureSource];
PHYS86ExactQ[x_]:=IntegerQ[x]||Head[x]===Rational;
PHYS86Fail[tag_]:=Failure[tag,<|"scope"->"constructed finite exponential-family interface"|>];
PHYS86Moments[q_,ea_,eb_,wa_,wb_,kernel_,h_,kc_]:=Module[
 {na,nb,a,b,zA,zB,event,s,n,meanA,meanB,varA,varB,meanS,varS,meanH,joint,covHKcS,obs},
 If[!PHYS86ExactQ[q]||!TrueQ[0<q<1],Return[PHYS86Fail["INVALID_Q"]]];
 If[!ListQ[ea]||!ListQ[eb]||Length[ea]==0||Length[eb]==0,Return[PHYS86Fail["INVALID_ENERGY_ARRAYS"]]];
 {na,nb}={Length[ea],Length[eb]};
 If[!AllTrue[Join[ea,eb],IntegerQ[#]&&#>0&],Return[PHYS86Fail["INVALID_POSITIVE_INTEGER_ENERGIES"]]];
 If[!ListQ[wa]||!ListQ[wb]||Length[wa]!=na||Length[wb]!=nb||!AllTrue[Join[wa,wb],PHYS86ExactQ[#]&&#>0&],Return[PHYS86Fail["INVALID_POSITIVE_WEIGHTS"]]];
 If[Dimensions[kernel]=!={na,nb}||!AllTrue[Flatten[kernel],PHYS86ExactQ[#]&&#>=0&],Return[PHYS86Fail["INVALID_KERNEL"]]];
 If[Dimensions[h]=!={na,nb}||!AllTrue[Flatten[h],MemberQ[{0,1},#]&],Return[PHYS86Fail["INVALID_MEMBERSHIP"]]];
 If[Dimensions[kc]=!={na,nb}||!AllTrue[Flatten[kc],PHYS86ExactQ[#]&&#>=0&],Return[PHYS86Fail["INVALID_DAUGHTER_KINETIC"]]];
 a=MapThread[#1*q^#2&,{wa,ea}];b=MapThread[#1*q^#2&,{wb,eb}];zA=Total[a];zB=Total[b];
 event=Table[a[[i]]*b[[j]]*kernel[[i,j]],{i,na},{j,nb}];s=Outer[Plus,ea,eb];n=Total[Flatten[event]];
 If[n===0,Return[<|"status"->"ZERO_RATE","rate_coefficient"->0,"normalized_moments"->"UNDEFINED","source"->0,"N"->0,"Za"->zA,"Zb"->zB|>]];
 meanA=Total[a*ea]/zA;meanB=Total[b*eb]/zB;
 varA=Total[a*(ea-meanA)^2]/zA;varB=Total[b*(eb-meanB)^2]/zB;
 obs[x_]:=Total[Flatten[event*x]]/n;
 meanS=obs[s];varS=obs[(s-meanS)^2];meanH=obs[h];joint=obs[h*kc];
 covHKcS=obs[h*kc*s]-joint*meanS;
 <|"status"->"POSITIVE_RATE","N"->n,"Za"->zA,"Zb"->zB,"rate_coefficient"->n/(zA*zB),
 "meanA"->meanA,"meanB"->meanB,"varA"->varA,"varB"->varB,"meanS"->meanS,"varS"->varS,
 "selection"->meanS-meanA-meanB,"curvature"->varS-varA-varB,"meanH"->meanH,"jointHKc"->joint,
 "covHKcS"->covHKcS,"source_coefficients"->{-meanS+meanA+meanB+joint,-meanH}|>
];
(* R,uC,Cv are formal independent variables in verification. Numerical Cv<=0
   and R<0 rejected. R=0 is processed before undefined normalized moments. *)
PHYS86TemperatureSource[m_,uC_,rate_,cv_]:=Module[{c},
 If[TrueQ[cv<=0],Return[PHYS86Fail["NONPOSITIVE_CV"]]];
 If[TrueQ[rate<0],Return[PHYS86Fail["NEGATIVE_RATE"]]];
 If[TrueQ[rate==0],Return[0]];
 If[!AssociationQ[m],Return[PHYS86Fail["INVALID_MOMENT_OBJECT"]]];
 If[Lookup[m,"status",""]==="ZERO_RATE",Return[0]];
 If[!KeyExistsQ[m,"source_coefficients"],Return[PHYS86Fail["UNDEFINED_NORMALIZED_MOMENTS"]]];
 c=m["source_coefficients"];rate*(c[[1]]+c[[2]]*uC)/cv
];
