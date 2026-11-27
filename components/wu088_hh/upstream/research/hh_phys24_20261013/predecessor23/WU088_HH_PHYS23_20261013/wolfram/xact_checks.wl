(* Standalone PHYS23 xAct check. Load and verify the official package first. *)
ClearAll["Global`*"];
bundleDirectory=CreateDirectory[];archivePath=FileNameJoin[{bundleDirectory,"xAct.tgz"}];
URLDownload["https://xact.es/download/xAct_1.3.0.tgz",archivePath];
expectedHash="7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be";
If[FileHash[archivePath,"SHA256","HexString"]=!=expectedHash,Return["XACT_HASH_FAILURE"]];
ExtractArchive[archivePath,bundleDirectory];
tensorPath=First[Select[FileNames["xTensor.m",bundleDirectory,Infinity],StringEndsQ[#,"/xAct/xTensor/xTensor.m"]&]];
PrependTo[$Path,DirectoryName[tensorPath,3]];PrependTo[$Path,DirectoryName[tensorPath,2]];Get[tensorPath];
(* Parsing tensor calls after loading fixes context resolution. *)
res23=ToExpression["$xpermQ=False;DefManifold[HHSpace23,4,{ia23,ib23,ic23,id23}];DefMetric[-1,metric23[-ia23,-ib23],cov23];DefTensor[norm23[ia23],HHSpace23];DefTensor[vel23[ia23],HHSpace23];DefTensor[ray23[ia23],HHSpace23];DefTensor[gas23[ia23],HHSpace23];DefTensor[density23[],HHSpace23];DefTensor[frac23[],HHSpace23];DefConstantSymbol[lor23];DefConstantSymbol[sigma23];rules23=Join[MakeRule[{norm23[ia23]norm23[-ia23],-1},MetricOn->All,ContractMetrics->True],MakeRule[{norm23[ia23]ray23[-ia23],0},MetricOn->All,ContractMetrics->True],MakeRule[{norm23[ia23]vel23[-ia23],0},MetricOn->All,ContractMetrics->True]];expr23=ToCanonical[ContractMetric[Expand[-lor23(norm23[-ia23]+vel23[-ia23])(norm23[ia23]+ray23[ia23])-lor23(1-vel23[-ia23]ray23[ia23])]]];doppler23=ToCanonical[expr23/.rules23];number23=ToCanonical[Expand[cov23[-ia23][density23[]frac23[]gas23[ia23]]-frac23[]cov23[-ia23][density23[]gas23[ia23]]-density23[]gas23[ia23]cov23[-ia23][frac23[]]]];opacity23=ToCanonical[Expand[sigma23 density23[]frac23[]expr23]/.rules23];{doppler23,number23,opacity23}"];
scalar23={Expand[(src-(kap+dk)(mm+dm))-(src-kap mm)+(kap+dk)dm+dk mm],FullSimplify[Exp[-(ta+dt)](1-Exp[-(om+dom)])-Exp[-ta](1-Exp[-om])-Exp[-ta]((Exp[-dt]-1)(1-Exp[-om])+Exp[-dt-om](1-Exp[-dom]))],Integrate[ss,{ss,0,hh}]-hh^2/2,Together[(1+rr)(1-Exp[-om])-(1-Exp[-(1+rr)om])-(rr-(1+rr)Exp[-om]+Exp[-(1+rr)om])],Together[ct(ww+dw)/(pp+de)-ct ww/pp-(ct dw-(ct ww/pp)de)/(pp+de)],FullSimplify[D[aa tt^p Exp[-th/tt],tt]/(aa tt^p Exp[-th/tt])-(p/tt+th/tt^2)],FullSimplify[Integrate[en Exp[-en/(kb tt)],{en,eb,Infinity},Assumptions->kb>0&&tt>0&&eb>0]-kb tt(eb+kb tt)Exp[-eb/(kb tt)]]};
result=<|"kernel"->System`$Version,"xAct_archive_sha256"->expectedHash,"xTensor_sha256"->FileHash[tensorPath,"SHA256","HexString"],"tensor_residuals"->res23,"scalar_residuals"->scalar23,"all_zero"->And@@(TrueQ[#===0]&/@Join[res23,scalar23])|>;
Print[ExportString[result,"RawJSON"]];If[!TrueQ[result["all_zero"]],Exit[2]];
