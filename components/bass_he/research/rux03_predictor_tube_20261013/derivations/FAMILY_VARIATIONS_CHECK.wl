(* THEORY07 only: finite reanchoring, moving-coordinate chains and new uniform bounds.
   The full source/tube result is reused by immutable literal references below.
   No rate, chemical RHS, corrector or ODE evaluation occurs. *)
Module[{checks=<||>,residuals=<||>,zero,truth,ga,gb,ba,bb,bc,mu0,
  sz,st,sm,hs,hi,amat,pMatrix,pinvMatrix,z,xa,xi,gv,zc,pnow,pinv,
  change,zb,jrow,s,gbf,bbf,pp,pip,dpExpected,xPath,xiPath,nu,xbFixed,
  offsetPath,xaFixed,dropWitness,eta,brad,lg,lb,gbar,mcap,lpRaw,
  lpVar,qCube,incBound,invBound,kcond,moveSens,checksOut,elapsed},
 elapsed=AbsoluteTiming[
 zero[name_,values_List]:=Module[{out},
   out=Simplify[Together[#]]& /@ Flatten[values];
   AssociateTo[checks,name->And@@(TrueQ[#===0]& /@ out)];
   AssociateTo[residuals,name->(ToString[InputForm[#]]& /@ out)]];
 truth[name_,values_List]:=(
   AssociateTo[checks,name->And@@(TrueQ /@ values)];
   AssociateTo[residuals,name->(ToString[InputForm[#]]& /@ values)]);
 ba=Array[baC,3];bb=Array[bbC,3];bc=Array[bChi,3];
 z=Array[zC,7];xa=Array[xaC,7];xi=Array[xiC,7];gv=Array[gC,7];
 zc=Array[zcC,7];nu=Array[nuC,7];
 hs=DiagonalMatrix[{sz,sz,sz,st,sm,sm,sm}];
 hi=DiagonalMatrix[{1/sz,1/sz,1/sz,1/st,1/sm,1/sm,1/sm}];
 amat[gg_,vv_List]:=ReplacePart[IdentityMatrix[7],
  4->Join[(gg/ga-1)bc,{gg/ga},gg(ba-vv)]];
 change[zz_List,gg_,vv_List]:=ReplacePart[zz,
  4->(gg/ga)zz[[4]]+(gg/ga-1)(mu0+bc.zz[[1;;3]])
     +gg(ba-vv).zz[[5;;7]]];
 pMatrix[gg_,vv_List]:=hi.amat[gg,vv].hs;
 pinvMatrix[pp0_]:=ReplacePart[IdentityMatrix[7],
   4->Join[-pp0[[4,1;;3]]/pp0[[4,4]],
     {1/pp0[[4,4]]},-pp0[[4,5;;7]]/pp0[[4,4]]]];
 pnow=pMatrix[gb,bb];pinv=pinvMatrix[pnow];
 zero["FV01_finite_anchor_energy_row",{
  change[z,gb,bb][[4]]-
   (gb*((z[[4]]+mu0+bc.z[[1;;3]])/ga
      +(ba-bb).z[[5;;7]])-mu0-bc.z[[1;;3]])}];
 zb=hi.change[zc+hs.xa,gb,bb];
 jrow=Table[D[zb[[4]],xa[[j]]],{j,7}];
 zero["FV02_scaled_thermal_row_and_determinant",{
  jrow-pnow[[4]],Det[pnow]-gb/ga}];
 zero["FV03_old_state_centered_finite_map",{
  hi.(change[zc+hs.xa,gb,bb]-change[zc+hs.xi,gb,bb])
   -pnow.(xa-xi)}];
 zero["FV04_shared_source_residual_equivalence",{
  pnow.(xa-xi)-h pnow.gv-pnow.(xa-xi-h gv)}];
 zero["FV05_explicit_inverse_nontrivial_row",{
  (pinv.pnow-IdentityMatrix[7])[[4]],
  (pnow.pinv-IdentityMatrix[7])[[4]]}];
 gbf=gbFun[s];bbf={bxFun[s],byFun[s],bzFun[s]};
 pp=pMatrix[gbf,bbf];pip=pinvMatrix[pp];
 dpExpected=Join[
  (sz/st)bc D[gbf,s]/ga,
  {D[gbf,s]/ga},
  (sm/st)((ba-bbf)D[gbf,s]-gbf D[bbf,s])];
 zero["FV06_anchor_parameter_DP_row",{
  D[pp[[4]],s]-dpExpected}];
 xPath=Table[xFun[j][s],{j,7}];xiPath=xi+s nu;
 zero["FV07_full_old_family_derivative_including_DP",{
  D[pp.(xPath-xiPath),s]-
   (D[pp,s].(xPath-xiPath)+pp.(D[xPath,s]-nu))}];
 xbFixed=Array[xbC,7];offsetPath=Table[dFun[j][s],{j,7}];
 xaFixed=pip.(xbFixed-offsetPath);
 zero["FV08_fixed_new_coordinate_parameter_chain",{
  D[xaFixed,s]+pip.(D[pp,s].xaFixed+D[offsetPath,s])}];
 dropWitness=ReplacePart[ConstantArray[0,{7,7}],{4,5}->1].UnitVector[7,5];
 truth["FV09_omitting_DP_is_detected_by_a_nonzero_jet",{
  dropWitness===UnitVector[7,4],dropWitness=!=ConstantArray[0,7]}];
 eta=1/100;brad=59/500;lg=1/5000000;lb=3/1000000;
 gbar=501/500;mcap=1501;
 lpRaw=(1+4brad)lg+4mcap(7/4)(lg lb eta+gbar lb);
 truth["FV10_uniform_fixed_scale_DP_and_near_identity",{
  lpRaw>0,lpRaw<1/30,eta lpRaw<1/3000}];
 lpVar=(1+1/10^11)lpRaw+(2/10^10)(3001/3000);
 truth["FV11_old_composition_scale_derivative_bounds",{
  brad eta/10^9<1/10^11,
  (1500000000+9)brad/(10^9)^2<2/10^10,
  lpVar<1/30}];
 (* These q/inverse/increment inputs were already proved in TUBE_CERTIFICATE_RESULT.json.
    Only their new reanchored-norm consequences are tested here. *)
 qCube=22546206219/500000000000;
 incBound=22546206219/477453793781;
 invBound=500000000000/477453793781;
 kcond=3001/2999;
 moveSens=(1/30)(87/100)+(3001/3000)incBound;
 truth["FV12_reanchored_family_norm_corollaries",{
  kcond qCube<1/20,kcond invBound<21/20,moveSens<2/25}];
 ][[1]];
 checksOut=<|"schema"->"theory07-family-variations-v1",
   "unit"->"HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07",
   "parent_manifest_sha256"->"9f223a9663ecec8da1edf90ee896d3aeabbf4f4c5bdd111df3e4f08b838c3192",
   "reused_tube_q"->"22546206219/500000000000",
   "kernel"->System`$Version,"system_id"->$SystemID,"kernel_seconds"->elapsed,
   "named_groups"->Length[checks],"checks"->checks,"all_pass"->And@@Values[checks],
   "residual_count"->Total[Length /@ Values[residuals]],
   "residuals"->residuals,
   "bounds"-><|"eta"->"1/100","LP_raw_exact"->ToString[InputForm[lpRaw]],
     "LP_raw_display"->N[lpRaw,18],"LP_adopted"->"1/30",
     "P_minus_I"->"1/3000","P_norm"->"3001/3000",
     "P_inverse_norm"->"3000/2999","P_condition_number"->"3001/2999",
     "LP_optional_scale_raw_exact"->ToString[InputForm[lpVar]],
     "reanchored_family_derivative_exact"->ToString[InputForm[moveSens]],
     "reanchored_family_derivative_display"->N[moveSens,18],
     "reanchored_family_derivative_adopted"->"2/25",
     "reanchored_contraction_adopted"->"1/20",
     "reanchored_inverse_adopted"->"21/20"|>,
   "scope"->"New exact affine/parameter identities and rational bounds. The nonzero DP jet is an algebraic discriminator, not a physical source solve. Existing full-rate and tube computations are reused; no native RHS or ODE."|>;
 ExportString[checksOut,"RawJSON"]
]
