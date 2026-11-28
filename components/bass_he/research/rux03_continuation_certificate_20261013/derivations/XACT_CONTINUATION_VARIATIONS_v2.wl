(* New THEORY06 tensor variations and the fixed-anchor thermal coordinate.
   Parsed only after xTensor has loaded. Derivative vectors are declared
   with the differentiated normalization constraints. No THEORY05 suite rerun. *)
Module[{rules,red,check,h,dh,k,dop,ds,q,dq,dCurrent,dStress,star,
  energySubs,checks=<||>,residuals=<||>,proj,dN,allR},
 $xpermQ=False;$DefInfoQ=False;
 DefManifold[ContinueM,4,{a,b,d,e,f,i,j,l,m}];
 DefMetric[-1,g[-a,-b],CD,{";","D"}];
 Scan[(DefTensor[#[a],ContinueM])&,{nObs,uGas,uStar,eRay,vGas,aGas}];
 Scan[DefConstantSymbol,{ga,gs,rel,gdot,reldot,mu,mus,vdotray,nh,rho,p,drho,dp,
  rr,drr,ww,dww,eps,energy,rate,drate,loss,dloss}];
 rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]& /@ {
  {nObs[a]nObs[-a],-1},{uGas[a]uGas[-a],-1},{uStar[a]uStar[-a],-1},
  {eRay[a]eRay[-a],1},{nObs[a]eRay[-a],0},
  {nObs[a]uGas[-a],-ga},{nObs[a]uStar[-a],-gs},
  {uGas[a]uStar[-a],-rel},{uGas[a]eRay[-a],ga mu},
  {uStar[a]eRay[-a],gs mus},{uGas[a]vGas[-a],0},
  {nObs[a]vGas[-a],-gdot},{uStar[a]vGas[-a],-reldot},
  {vGas[a]eRay[-a],vdotray},
  {uGas[a]aGas[-a],-vGas[a]vGas[-a]}});
 red[x_]:=Module[{y},y=ToCanonical[ContractMetric[ToCanonical[Expand[x]]]];
  y=ToCanonical[y //. rules];Simplify[Together[y]]];
 check[name_,exprs_List]:=Module[{out},Print["THEORY06_CHECK: ",name];out=red /@ exprs;
  AssociateTo[checks,name->And@@(TrueQ[#===0]& /@ out)];
  AssociateTo[residuals,name->(ToString[InputForm[#]]& /@ out)]];
 h[i_,j_]:=g[i,j]+uGas[i]uGas[j];
 dh[i_,j_]:=vGas[i]uGas[j]+uGas[i]vGas[j];
 k[i_]:=nObs[i]+eRay[i];dop=ga(1-mu);ds=gdot-vdotray;
 q[i_]:=k[i]/dop-uGas[i];
 dq[i_]:=-k[i]ds/dop^2-vGas[i];
 check["C1_tangent_projector_variation",{
   h[a,-b]vGas[b]-vGas[a],
   dh[a,-b]uGas[b]+h[a,-b]vGas[b],
   dh[a,-b]h[b,-d]+h[a,-b]dh[b,-d]-dh[a,-d]}];
 check["C2_rest_photon_direction_differential",{
   -vGas[-a]k[a]-ds,
   uGas[-a]dq[a]+vGas[-a]q[a],
   q[-a]dq[a],
   ds(uGas[a]+q[a])+dop(vGas[a]+dq[a])}];
 dN[i_]:=nh vGas[i]-nh gdot uGas[i]/ga;
 check["C1_fixed_Eulerian_hydrogen_variation",{-nObs[-a]dN[a]}];
 dCurrent[i_]:=(drho+dp)ga uGas[i]+(rho+p)gdot uGas[i]
   +(rho+p)ga vGas[i]-dp nObs[i];
 dStress[i_,j_]:=(drho+dp)uGas[i]uGas[j]
   +(rho+p)(vGas[i]uGas[j]+uGas[i]vGas[j])+dp g[i,j];
 check["C1_current_differential_from_stress",{-dStress[a,b]nObs[-b]-dCurrent[a]}];
 proj=-uStar[-a]dCurrent[a];
 star={uStar->uGas,gs->ga,rel->1,reldot->0};
 energySubs={rho->nh(rr+eps ww),p->2 nh eps ww/3,
   drho->-nh(rr+eps ww)gdot/ga+nh(drr+eps dww)};
 check["C1_anchor_projection_thermal_differential",{
   proj-((drho+dp)ga rel+(rho+p)gdot rel+(rho+p)ga reldot-dp gs),
   ((proj/.star)/.energySubs)-ga nh drr-ga nh eps(dww+2 ww gdot/(3 ga))}];
 check["C3_fixed_anchor_photo_weights",{
   -uStar[-a](eps energy rate k[a])-eps energy rate gs(1-mus),
   -uStar[-a](eps energy drate k[a])-eps energy drate gs(1-mus)}];
 check["C3_escape_weight_differential",{
   -uStar[-a](-eps loss uGas[a])+eps rel loss,
   -uStar[-a](-eps(dloss uGas[a]+loss vGas[a]))+eps(rel dloss+reldot loss)}];
 check["C3_relative_gamma_anchor_quadratic_onset",{
   (-uStar[-a]vGas[a])/.star,
   ((-uStar[-a]aGas[a])/.star)-vGas[-a]vGas[a]}];
 allR=Flatten[Values[residuals]];
 ExportString[<|"schema"->"theory06_xact_variations_v1",
   "kernel"->System`$Version,"xTensorLoaded"->MemberQ[$Packages,"xAct`xTensor`"],
   "xTensorVersion"->ToString[InputForm[xAct`xTensor`$Version]],
   "xPermExternalBackend"->$xpermQ,"declaredTensor"->xTensorQ[uGas],
   "named_groups"->Length[checks],"residual_count"->Length[allR],
   "checks"->checks,"residuals"->residuals,"all_pass"->And@@Values[checks]|>,"RawJSON"]
]
