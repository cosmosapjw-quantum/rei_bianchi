Needs["xAct`xTensor`"];
xAct`xPerm`$xpermQ=False;
$DefInfoQ=False;
DefManifold[WarmRayM,4,{a,b,d,f,i,j,k,l}];
DefMetric[-1,gg[-a,-b],CD,{";","D"}];
DefTensor[uu[a],WarmRayM];DefTensor[ee[a],WarmRayM];DefTensor[ax[a],WarmRayM];
DefConstantSymbol[sig];DefConstantSymbol[mu];DefConstantSymbol[HH];
ClearAll[sh,proj,ray,red,put];
proj[i_,j_]:=gg[i,j]+uu[i]uu[j];
sh[i_,j_]:=sig(3 ax[i]ax[j]-proj[i,j]);
ray[i_]:=uu[i]+ee[i];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]& /@ {
 {uu[a]uu[-a],-1},{uu[a]ee[-a],0},{uu[a]ax[-a],0},
 {ee[a]ee[-a],1},{ax[a]ax[-a],1},{ax[a]ee[-a],mu}});
red[x_]:=Simplify[ToCanonical[ToCanonical[ContractMetric[ToCanonical[Expand[x]]]]//.rules]];
checks=<||>;residuals=<||>;
put[name_,xs_List]:=Module[{r=red/@xs},
 AssociateTo[checks,name->And@@(TrueQ[#===0]&/@r)];
 AssociateTo[residuals,name->(ToString[InputForm[#]]&/@r)]];
put["X01_null_photon",{ray[a]ray[-a]}];
put["X02_spatial_projector",{proj[-a,-b]uu[b],gg[a,b]proj[-a,-b]-3}];
put["X03_shear_spatial",{sh[-a,-b]uu[b]}];
put["X04_shear_trace",{gg[a,b]sh[-a,-b]}];
put["X05_shear_direction",{sh[-a,-b]ee[a]ee[b]-sig(3mu^2-1)}];
put["X06_null_shear_equals_spatial",{sh[-a,-b]ray[a]ray[b]-sig(3mu^2-1)}];
put["X07_geometric_redshift",{HH+sh[-a,-b]ee[a]ee[b]-(HH+sig(3mu^2-1))}];
put["X08_ray_energy_normalization",{-uu[-a]ray[a]-1}];
DefConstantSymbol[nHyd];DefConstantSymbol[nHel];
DefConstantSymbol[fHion];DefConstantSymbol[fHeion];DefConstantSymbol[fHepp];
ClearAll[hCurrent,heCurrent,eCurrent];
hCurrent[i_]:=nHyd uu[i];
heCurrent[i_]:=nHel uu[i];
eCurrent[i_]:=(nHyd fHion+nHel(fHeion+2 fHepp))uu[i];
put["X09_species_nucleus_4currents",{
  -uu[-a]hCurrent[a]-nHyd,
  -uu[-a]heCurrent[a]-nHel}];
put["X10_electron_charge_4current",{
  -uu[-a]eCurrent[a]-(nHyd fHion+nHel(fHeion+2 fHepp))}];
put["X11_no_spatial_charge_flux_in_nontilted_gas",{
  proj[-a,-b] eCurrent[b]}];

output=<|"schema"->"rei.axbi.clock_charge_xact.v1",
 "kernel"->System`$Version,
 "xTensor_loaded"->MemberQ[$Packages,"xAct`xTensor`"],
 "xTensor_version"->ToString[InputForm[xAct`xTensor`$Version]],
 "pure_Wolfram_xPerm"->(!xAct`xPerm`$xpermQ),
 "expected_checks"->11,"actual_checks"->Length[checks],
 "checks"->checks,"residuals"->residuals,
 "zero_residual_count"->Length[Flatten[Values[residuals]]],
 "all_pass"->(Length[checks]==11&&And@@Values[checks]),
 "scope"->"Exact LRS kinematic redshift and null-screen projections; not an interval-library proof."|>;
Print[ExportString[output,"RawJSON"]];
Exit[If[TrueQ[output["all_pass"]],0,2]];
