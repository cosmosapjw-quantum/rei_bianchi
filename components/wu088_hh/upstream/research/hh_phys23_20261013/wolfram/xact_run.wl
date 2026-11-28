ClearAll["Global`*"]; kernel23=System`$Version;
dir23=CreateDirectory[];arc23=FileNameJoin[{dir23,"xAct.tgz"}];URLDownload["https://xact.es/download/xAct_1.3.0.tgz",arc23];ah23=FileHash[arc23,"SHA256","HexString"];
If[ah23=!="7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be",Return[<|"status"->"ARCHIVE_HASH_FAIL","actual"->ah23|>]];
ExtractArchive[arc23,dir23];xf23=First[Select[FileNames["xTensor.m",dir23,Infinity],StringEndsQ[#,"/xAct/xTensor/xTensor.m"]&]];PrependTo[$Path,DirectoryName[xf23,3]];PrependTo[$Path,DirectoryName[xf23,2]];Get[xf23];
tensorResult23=ToExpression["
$xpermQ=False;
DefManifold[M23,4,{a23,b23,c23,d23}];DefMetric[-1,met23[-a23,-b23],CD23];
DefTensor[u23[a23],M23];DefTensor[l23[a23],M23];DefTensor[nH23[],M23];DefTensor[eA23[],M23];DefTensor[eB23[],M23];DefTensor[I23[],M23];DefTensor[eps23[],M23];
DefConstantSymbol[cs23];DefConstantSymbol[st23];
canon23[x_]:=ToCanonical[ContractMetric[Expand[x]]];
cur23=canon23[CD23[-a23][nH23[] eA23[] u23[a23]]-CD23[-a23][nH23[] eB23[] u23[a23]]-(eA23[]-eB23[]) CD23[-a23][nH23[] u23[a23]]-nH23[] u23[a23] CD23[-a23][eA23[]-eB23[]]];
ray23=canon23[-cs23 st23 nH23[] eA23[] u23[-a23] l23[a23]+cs23 st23 nH23[] eB23[] u23[-a23] l23[a23]+cs23 st23 nH23[] (eA23[]-eB23[])u23[-a23]l23[a23]];
exp23=canon23[u23[a23] CD23[-a23][I23[]+eps23[]]-u23[a23] CD23[-a23][I23[]]-u23[a23] CD23[-a23][eps23[]]];
{cur23,ray23,exp23}
"];
scalar23={Together[ct23 (w23+dw23)/(p23+de23)-ct23 w23/p23-(ct23 dw23-(ct23 w23/p23)de23)/(p23+de23)],Together[Integrate[s23,{s23,0,h23}]-h23^2/2],Together[(b23-a23)(a23+b23)/2-(b23^2-a23^2)/2],FullSimplify[Exp[-(tr23+dr23)](1-Exp[-(d23+dx23)])-Exp[-tr23](1-Exp[-d23])-Exp[-tr23]((Exp[-dr23]-1)(1-Exp[-d23])+Exp[-dr23-d23](1-Exp[-dx23]))],FullSimplify[Exp[-(tr23+tail23)](1-Exp[-d23])-Exp[-tail23]Exp[-tr23](1-Exp[-d23])],Together[(1-zz23)ii23-(ii23-zz23 ii23)]};
checks23=Join[tensorResult23,scalar23];
<|"status"->If[And@@(TrueQ[#===0]&/@checks23),"PASS","FAIL"],"kernel"->kernel23,"archive_sha256"->ah23,"xTensor_sha256"->FileHash[xf23,"SHA256","HexString"],"xTensor_checks"->tensorResult23,"scalar_checks"->scalar23,"residual_count"->Length[checks23],"zero_residuals"->Count[checks23,0],"external_xperm_used"->False|>
