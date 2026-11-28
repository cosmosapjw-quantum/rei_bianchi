Needs["xAct`xTensor`"];
xAct`xPerm`$xpermQ=False;
$DefInfoQ=False;
DefManifold[HE18C3Man,4,{a,b,c,d}];
DefMetric[-1,g[-a,-b],CD,{";","D"}];
DefTensor[u[a],HE18C3Man];
DefTensor[ray[a],HE18C3Man];
DefTensor[flux[a],HE18C3Man];
Scan[DefConstantSymbol,{cc,nh,fh,xx,yy,zz,DD,AA,st}];
rules=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]&/@{
    {u[a]u[-a],-1},{u[-a]ray[a],-DD},{u[-a]flux[a],0}});
red[x_]:=Simplify[ToCanonical[ToCanonical[ContractMetric[ToCanonical[Expand[x]]]]//.rules]];
ne=nh(xx+fh(yy+2zz));je[i_]:=cc ne u[i]+flux[i];
res=<|
 "X01_rest_current_density"->red[-u[-a]je[a]/cc-ne],
 "X02_ray_electron_column"->red[-ray[-a]je[a]/AA-(cc ne DD-ray[-a]flux[a])/AA],
 "X03_baryon_H_consistency"->red[cc nh(1+4fh)((xx+fh(yy+2zz))/(1+4fh))u[a]-(je[a]-flux[a])],
 "X04_rest_flux_orthogonality"->red[u[-a]flux[a]],
 "X05_single_sigma"->red[-st ray[-a]je[a]/AA+st(ray[-a]je[a]/AA)]|>;
checks=Map[TrueQ[#===0]&,res];
Print["HE18_C3_XACT_VERSION=",xAct`xTensor`$Version];
Print["HE18_C3_TENSOR_RESIDUALS=",InputForm[res]];
Print["HE18_C3_TENSOR_CHECKS=",InputForm[checks]];
If[And@@Values[checks],Exit[0],Exit[2]];
