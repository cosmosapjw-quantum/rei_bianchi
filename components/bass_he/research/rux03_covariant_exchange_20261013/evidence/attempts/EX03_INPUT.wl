Module[{dir, archive, files, xp, pp, base, norm, red, tests, msglog},
dir = CreateDirectory[];
archive = FileNameJoin[{dir, "xAct_1.3.0.tgz"}];
URLDownload["https://xact.es/download/xAct_1.3.0.tgz", archive];
files = ExtractArchive[archive, FileNameJoin[{dir, "package"}]];
xp = First[FileNames["xTensor.m", FileNameJoin[{dir, "package"}], Infinity]];
pp = FileNameSplit[xp]; base = FileNameJoin[Take[pp, First[FirstPosition[pp, "xAct"]] - 1]];
PrependTo[$Path, base];
Needs["xAct`xTensor`"];
Print["LOAD_OK"];
Print["symbol contexts ", Context[xAct`xTensor`DefManifold], " definitions ", Length[DownValues[xAct`xTensor`DefManifold]]];
xAct`xTensor`DefManifold[M4, 4, {a,b,d,e,f,i,j,k,l}];
Print["MANIFOLD_OK ", xAct`xTensor`ManifoldQ[M4]];
xAct`xTensor`DefMetric[-1, g[-a,-b], CD, {";","D"}];
Print["METRIC_OK ", xAct`xTensor`MetricQ[g]];
xAct`xTensor`DefTensor[uu[a], M4];
Print["VECTOR_OK ", xAct`xTensor`xTensorQ[uu]];
xAct`xTensor`DefTensor[ell[a], M4];
Print["SECOND_VECTOR_OK"];
xAct`xTensor`DefConstantSymbol[cc];
Print["CONSTANT_OK"];
norm = xAct`xTensor`MakeRule[{uu[a] uu[-a], -1}, xAct`xTensor`MetricOn->All, xAct`xTensor`ContractMetrics->True];
Print["NORM_RULE ", InputForm[norm]];
Print["CONTRACT ",InputForm[xAct`xTensor`ToCanonical[uu[a]uu[-a]] //. norm]];
"DIAGNOSTIC_COMPLETE"
]