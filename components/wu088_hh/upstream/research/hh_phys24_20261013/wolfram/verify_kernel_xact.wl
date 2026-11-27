ClearAll["Global`*"];
kernelVersion=System`$Version;
(* Download exactly identified xAct source to this disposable kernel. *)
dir=CreateDirectory[]; arc=FileNameJoin[{dir,"xAct.tgz"}];
URLDownload["https://xact.es/download/xAct_1.3.0.tgz",arc];
archiveHash=FileHash[arc,"SHA256","HexString"];
If[archiveHash=!="7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",Return[<|"status"->"ARCHIVE_HASH_FAILURE"|>]];
ExtractArchive[arc,dir]; xf=First[Select[FileNames["xTensor.m",dir,Infinity],StringEndsQ[#,"/xAct/xTensor/xTensor.m"]&]];
PrependTo[$Path,DirectoryName[xf,3]]; PrependTo[$Path,DirectoryName[xf,2]]; Get[xf];
tensorResult=ToExpression["
$xpermQ=False;
DefManifold[HH24,4,{a24,b24,c24,d24}];
DefMetric[-1,met24[-a24,-b24],CD24];
DefTensor[u24[a24],HH24]; DefTensor[v24[a24],HH24];
DefTensor[nh24[],HH24]; DefTensor[ee24[],HH24];
DefConstantSymbol[mm24]; DefConstantSymbol[cc24];
pt[a24_]:=mm24*cc24*(u24[a24]+v24[a24]);
scheck=ToCanonical[Expand[-pt[a24]pt[-a24]+mm24^2*cc24^2*(u24[a24]u24[-a24]+v24[a24]v24[-a24]+2u24[a24]v24[-a24])]];
ncheck=ToCanonical[Expand[CD24[-a24][nh24[]*ee24[]*u24[a24]]-ee24[]CD24[-a24][nh24[]*u24[a24]]-nh24[]*u24[a24]*CD24[-a24][ee24[]]]];
xcheck=ToCanonical[Expand[u24[a24]*v24[-a24]-v24[a24]*u24[-a24]]];
{scheck,ncheck,xcheck}
"];
ass=mu>0&&theta>0&&en>0;
vrel=Sqrt[2en/mu];
jac=FullSimplify[(4Pi (mu/(2Pi theta))^(3/2)*vv^3*Exp[-mu vv^2/(2theta)]/.vv->vrel)*D[vrel,en],ass];
ant1=-theta*(en+theta)*Exp[-en/theta];
ant2=-theta*(en^2+2theta*en+2theta^2)*Exp[-en/theta];
wt=en*theta^(-3/2)*Exp[-en/theta];
checks={
 FullSimplify[jac-Sqrt[8/(Pi mu)]*wt,ass],
 Simplify[D[ant1,en]-en*Exp[-en/theta]],
 Simplify[D[ant2,en]-en^2*Exp[-en/theta]],
 FullSimplify[D[wt,theta]/wt-(en/theta-3/2)/theta,ass],
 Simplify[((xx*Exp[-xx/theta]*ss[2xx])/.xx->ll/2)/2-ll*Exp[-ll/(2theta)]*ss[ll]/4],
 Simplify[mm/4*(vv1-vv2)^2-(mm vv1^2/2+mm vv2^2/2-mm*(vv1+vv2)^2/4)],
 Simplify[(D[mm cc^2*(Sqrt[2(1+gam)]-2),gam]/.gam->1)-mm cc^2/2],
 Simplify[nn^2*(sigS/4+3sigT/4)*rateV/2-nn^2*(sigS/8+3sigT/8)*rateV],
 FullSimplify[Integrate[en*Exp[-en/theta],{en,ecut,Infinity},Assumptions->theta>0&&ecut>0]-theta*(ecut+theta)*Exp[-ecut/theta],theta>0&&ecut>0]
};
ev=1602176634/10^28; kb=1380649/10^29; mh=167262192369/10^38; redmass=mh/2;
chi=13598434599702/10^12; tlo=4999963846/10^5; thi=5000036154/10^5; t0=50000;
pref[t_]:=50Sqrt[8ev/(Pi redmass)]/(kb*t/ev)^(3/2);
primitive[e_,t_]:=Module[{th=kb*t/ev},th*(e+th)*Exp[-e/th]];
wbin[a_,b_,t_]:=pref[t]*(primitive[a,t]-If[b===Infinity,0,primitive[b,t]]);
edges={chi,16,20,25,2chi,35,50,100,625,Infinity};
rndLo[x_]:=ToString[Floor[SetPrecision[x,Infinity]*10^45]/10^45,InputForm];
rndHi[x_]:=ToString[Ceiling[SetPrecision[x,Infinity]*10^45]/10^45,InputForm];
rows=Table[Module[{il,iu},il=N[wbin[edges[[j]],edges[[j+1]],Interval[{tlo,tlo}]],60];iu=N[wbin[edges[[j]],edges[[j+1]],Interval[{thi,thi}]],60];<|"a_eV"->ToString[edges[[j]],InputForm],"b_eV"->ToString[edges[[j+1]],InputForm],"W_lo_cm_s"->rndLo[Min[il]],"W_hi_cm_s"->rndHi[Max[iu]],"W_mid_cm_s"->N[wbin[edges[[j]],edges[[j+1]],t0],22],"kernel_mass_fraction"->N[wbin[edges[[j]],edges[[j+1]],t0]/wbin[chi,Infinity,t0],22]|>],{j,Length[edges]-1}];
all=Join[tensorResult,checks];
<|"status"->If[And@@(TrueQ[#===0]&/@all),"PASS","FAIL"],"kernel"->kernelVersion,"archive_sha256"->archiveHash,"xTensor_sha256"->FileHash[xf,"SHA256","HexString"],"tensor_residuals"->tensorResult,"scalar_residuals"->checks,"residual_count"->Length[all],"positive_temperature_derivative_domain"->(chi>3kb*thi/(2ev)),"W_total_cm_s"->N[wbin[chi,Infinity,t0],25],"rows"->rows|>
