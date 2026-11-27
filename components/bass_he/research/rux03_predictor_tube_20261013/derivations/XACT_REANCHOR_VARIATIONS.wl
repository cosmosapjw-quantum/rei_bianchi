(* THEORY07: new moving-anchor and mixed-variation current projections.
   Parse only after xTensor is loaded. Free and dummy indices are explicit.
   No previous source, primitive or tensor check suite is rerun. *)
Module[{rules,red,check,current,dStress,moving,movingExpected,mixedAG,
 star,eos,anchorA,anchorB,curLab,bTaylor,cTaylor,normMixed,
 h,h1,h2,h12,k,mixedPhoto,mixedEscape,currentFixedAnchor,
 checks=<||>,residuals=<||>,allR,coef12},
 $xpermQ=False;$DefInfoQ=False;
 DefManifold[ReanchorM,4,{a,b,d,e,f,i,j,l,m}];
 DefMetric[-1,g[-a,-b],CD,{";","D"}];
 Scan[(DefTensor[#[a],ReanchorM])&,
   {nObs,uGas,uAnchor,vGas,vAnchor,vOne,vTwo,wMixed,eRay,
    aVel,bVel,momLab,curC,curC1,curC2,curC12}];
 Scan[DefConstantSymbol,
   {ga,gb,rel,gd,gbd,ra,rg,rag,vay,gb12,rho,p,drho,dp,
    nh,eps,a0,da0,ww,dww,energy,rate,drate,loss,dloss,
    gaStar,gbStar,labEnergy,sOne,sTwo}];
 rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]& /@ {
  {nObs[a]nObs[-a],-1},{uGas[a]uGas[-a],-1},
  {uAnchor[a]uAnchor[-a],-1},
  {nObs[a]uGas[-a],-ga},{nObs[a]uAnchor[-a],-gb},
  {uAnchor[a]uGas[-a],-rel},{uGas[a]vGas[-a],0},
  {uAnchor[a]vAnchor[-a],0},
  {nObs[a]vGas[-a],-gd},{nObs[a]vAnchor[-a],-gbd},
  {uGas[a]vAnchor[-a],-ra},{uAnchor[a]vGas[-a],-rg},
  {vAnchor[a]vGas[-a],-rag},
  {eRay[a]eRay[-a],1},{nObs[a]eRay[-a],0},
  {vAnchor[a]eRay[-a],vay},
  {uAnchor[a]vOne[-a],0},{uAnchor[a]vTwo[-a],0},
  {uAnchor[a]wMixed[-a],-vOne[a]vTwo[-a]},
  {nObs[a]wMixed[-a],-gb12},
  {nObs[a]aVel[-a],0},{nObs[a]bVel[-a],0},
  {nObs[a]momLab[-a],0}});
 red[x_]:=Module[{y},
  y=ToCanonical[ContractMetric[ToCanonical[Expand[x]]]];
  y=ToCanonical[y //. rules];Simplify[Together[y]]];
 check[name_,exprs_List]:=Module[{out},out=red /@ exprs;
  AssociateTo[checks,name->And@@(TrueQ[#===0]& /@ out)];
  AssociateTo[residuals,name->(ToString[InputForm[#]]& /@ out)]];
 coef12[x_]:=Coefficient[Coefficient[Expand[x],sOne,1],sTwo,1];
 current[i_]:=(rho+p)ga uGas[i]-p nObs[i];
 dStress[i_,j_]:=(drho+dp)uGas[i]uGas[j]+
   (rho+p)(vGas[i]uGas[j]+uGas[i]vGas[j])+dp g[i,j];
 anchorA[i_]:=gaStar(nObs[i]+aVel[i]);
 anchorB[i_]:=gbStar(nObs[i]+bVel[i]);
 curLab[i_]:=labEnergy nObs[i]+momLab[i];
 check["XA01_finite_two_anchor_current_projection",{
  -anchorB[-a]curLab[a]+(gbStar/gaStar)anchorA[-a]curLab[a]
   -gbStar(aVel[-a]-bVel[-a])momLab[a]}];
 moving=-vAnchor[-a]current[a]+uAnchor[-a]dStress[a,b]nObs[-b];
 movingExpected=(drho+dp)ga rel+(rho+p)gd rel+
   (rho+p)ga(ra+rg)-dp gb-p gbd;
 check["XA02_total_moving_anchor_stress_current_variation",{
  moving-movingExpected}];
 mixedAG=vAnchor[-a]dStress[a,b]nObs[-b];
 check["XA03_mixed_anchor_gas_current_projection",{
  mixedAG-((drho+dp)ga ra+(rho+p)gd ra+
     (rho+p)ga rag-dp gbd)}];
 star={uAnchor->uGas,vAnchor->vGas,gb->ga,gbd->gd,
   rel->1,ra->0,rg->0};
 eos={rho->nh eps(a0+ww),p->2 nh eps ww/3,
   drho->nh eps(da0+dww)-nh eps(a0+ww)gd/ga};
 check["XA04_old_state_moving_anchor_thermal_cancellation",{
  -vGas[-a]current[a]+p gd,
  ((moving/.star)/.eos)-ga nh eps(da0+dww)}];
 bTaylor[i_]:=uAnchor[i]+sOne vOne[i]+sTwo vTwo[i]+
   sOne sTwo wMixed[i];
 cTaylor[i_]:=curC[i]+sOne curC1[i]+sTwo curC2[i]+
   sOne sTwo curC12[i];
 normMixed=coef12[bTaylor[-a]bTaylor[a]];
 check["XA05_full_mixed_projection_and_normalization",{
  coef12[-bTaylor[-a]cTaylor[a]]+
   wMixed[-a]curC[a]+vOne[-a]curC2[a]+
   vTwo[-a]curC1[a]+uAnchor[-a]curC12[a],
  normMixed}];
 h[i_,j_]:=g[i,j]+uAnchor[i]uAnchor[j];
 h1[i_,j_]:=vOne[i]uAnchor[j]+uAnchor[i]vOne[j];
 h2[i_,j_]:=vTwo[i]uAnchor[j]+uAnchor[i]vTwo[j];
 h12[i_,j_]:=wMixed[i]uAnchor[j]+uAnchor[i]wMixed[j]+
   vOne[i]vTwo[j]+vTwo[i]vOne[j];
 check["XA06_mixed_anchor_projector_differential",{
  h12[a,-b]uAnchor[b]+h1[a,-b]vTwo[b]+
   h2[a,-b]vOne[b]+h[a,-b]wMixed[b],
  h12[a,-b]h[b,-d]+h1[a,-b]h2[b,-d]+
   h2[a,-b]h1[b,-d]+h[a,-b]h12[b,-d]-h12[a,-d]}];
 k[i_]:=nObs[i]+eRay[i];
 mixedPhoto=coef12[-(uAnchor[-a]+sOne vAnchor[-a])eps energy
   (rate+sTwo drate)k[a]];
 check["XA07_mixed_photo_anchor_rate_variation",{
  mixedPhoto-eps energy drate(gbd-vay)}];
 mixedEscape=coef12[(uAnchor[-a]+sOne vAnchor[-a])eps
   (loss+sTwo dloss)(uGas[a]+sTwo vGas[a])];
 check["XA08_mixed_escape_anchor_gas_variation",{
  mixedEscape+eps(dloss ra+loss rag)}];
 currentFixedAnchor[i_]:=(rho+p)gb uAnchor[i]-p nObs[i];
 check["XA09_mixed_anchor_curvature_in_fixed_current_energy",{
  -wMixed[-a]currentFixedAnchor[a]-
   ((rho+p)gb vOne[-a]vTwo[a]-p gb12)}];
 allR=Flatten[Values[residuals]];
 ExportString[<|"schema"->"theory07-xact-reanchor-variations-v1",
  "unit"->"HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07",
  "kernel"->System`$Version,"system_id"->$SystemID,
  "xTensorLoaded"->MemberQ[$Packages,"xAct`xTensor`"],
  "xTensorVersion"->ToString[InputForm[xAct`xTensor`$Version]],
  "xPermExternalBackend"->$xpermQ,"declaredTensor"->xTensorQ[uAnchor],
  "named_groups"->Length[checks],"residual_count"->Length[allR],
  "checks"->checks,"residuals"->residuals,"all_pass"->And@@Values[checks],
  "scope"->"New finite/moving-anchor and mixed current/projection identities with differentiated unit normalization. Fixed-gas initial parameter family, no native source, stage solve or ODE."|>,"RawJSON"]
]
