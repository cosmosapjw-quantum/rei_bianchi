ClearAll["Global`*"]; kernelBefore=System`$Version;
url="https://raw.githubusercontent.com/cosmosapjw-quantum/WU088_HH/0f976b842fbf847a6c94a0c16a487077e4a26b17/research/hh_phys22_20261013/results/interval_result_v3.json";
p=FileNameJoin[{CreateDirectory[],"HH22.json"}];URLDownload[url,p];sha=FileHash[p,"SHA256","HexString"];
If[sha=!="9b6b44acee637ac8adde1ca114e258c38747d48b3a750146614742786d8444ed",Return[<|"status"->"INPUT_HASH_FAIL","actual"->sha|>]];
r=Import[p,"RawJSON"]; rat[s_String]:=FromDigits[First[StringSplit[s,"/"]]]/If[StringContainsQ[s,"/"],FromDigits[Last[StringSplit[s,"/"]]],1];
pp=Map[rat,r["gain_upper"],{2}];ql=rat[r["qHH_box"][[1]]];qu=rat[r["qHH_box"][[2]]];tb=rat/@r["temperature_box"];pb=rat/@r["particle_box"];nb=rat/@r["nH_box"];rad=rat/@r["gas_radii"];pbound=rat/@r["tube_picard_upper"];
h=10^11;f=3/38;ct=2(1602176634/10^21)/(3(1380649/10^22));chi=13598434599702/10^12;ell={1,f,2f,0};absnu={1,0,0,chi};
z=Inverse[IdentityMatrix[4]-pp].absnu;v=pp.z;zeta=ell.v;err=ct v[[4]]+tb[[2]]zeta;ge={1-zeta,1+zeta};gt={(ct chi+tb[[1]]-err)/pb[[2]],(ct chi+tb[[2]]+err)/pb[[1]]};cap=Min[Table[If[absnu[[i]]==0,Infinity,1+(rad[[i]]-pbound[[i]])/(h absnu[[i]]qu)],{i,4}]];
Tbox=N[Interval[tb],60]; massRatio=Interval[{0,1/1000}];
ratios=<|"LCS91"->Interval[{1,1}],"HM89"->(17000/12) Tbox^(-7/10) Exp[8800/Tbox],"HM79"->(9800/12)Tbox^(-7/10),"KS91_G15"->(465/1200000)Tbox^(3/10),"D69_G15"->(15700/12)Tbox^(-7/10)(1+2Tbox/157800)/(1+(2massRatio Tbox/157800)^2)|>;
down[x_]:=Floor[SetPrecision[x,Infinity]10^14]/10^14;up[x_]:=Ceiling[SetPrecision[x,Infinity]10^14]/10^14;
rb=AssociationMap[{down[Min[ratios[#]]],up[Max[ratios[#]]]}&,Keys[ratios]];
cs=29979245800;sig=66524587/10^32;rrb=cs sig nb;
baseTau=rrb*(pb-1-f)*h;
make[ab_]:=<|"ratio_rational"->(ToString[#,InputForm]&/@ab),"ratio"->N[ab,18],"T_interval_K"->N[{-gt[[2]]h qu ab[[2]],-gt[[1]]h ql ab[[1]]},18],"electron_interval_perH"->N[{ge[[1]]h ql ab[[1]],ge[[2]]h qu ab[[2]]},18],"depth_interval"->N[{rrb[[1]]ge[[1]]ql ab[[1]]h^2/2,rrb[[2]]ge[[2]]qu ab[[2]]h^2/2},18]|>;
family={Min[Values[rb][[All,1]]],Max[Values[rb][[All,2]]]};out=AssociationMap[make[rb[#]]&,Keys[rb]];
ceilA=11/10;newTube=pbound+(ceilA-1)h absnu qu;
structural=<|"z"->N[z,18],"v"->N[v,18],"zeta"->N[zeta,18],"electron_per_exposure"->N[ge,18],"temperature_magnitude_per_exposure_K"->N[gt,18],"tube_amplitude_cap"->N[cap,18],"tube_ratios_at_1p1"->N[newTube/rad,18],"base_depth_box"->N[baseTau,18]|>;
<|"status"->If[And[0<zeta<1,Min[gt]>0,Max[family]<=ceilA,Max[newTube/rad]<1],"PASS","FAIL"],"kernel"->kernelBefore,"input_sha256"->sha,"structural"->structural,"rates"->out,"family"->make[family],"ratio_span"->N[family[[2]]/family[[1]],18],"algebra_only_receiver_constants"-><|"sigma_cm2"->ToString[sig,InputForm],"c_cm_s"->cs|>|>
