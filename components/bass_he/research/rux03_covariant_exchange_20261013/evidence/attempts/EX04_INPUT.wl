Module[{dir, archive, files, xp, pp, base, norm, red, tests, msgfile, msgstream, rr1, rr2, rr3, rr4, rr5},
dir = CreateDirectory[];
archive = FileNameJoin[{dir, "xAct_1.3.0.tgz"}];
URLDownload["https://xact.es/download/xAct_1.3.0.tgz", archive];
files = ExtractArchive[archive, FileNameJoin[{dir, "package"}]];
xp = First[FileNames["xTensor.m", FileNameJoin[{dir, "package"}], Infinity]];
pp = FileNameSplit[xp]; base = FileNameJoin[Take[pp, First[FirstPosition[pp, "xAct"]] - 1]];
PrependTo[$Path, base];
Needs["xAct`xTensor`"];
msgfile=FileNameJoin[{dir,"messages.txt"}]; msgstream=OpenWrite[msgfile];
Block[{$Messages={msgstream}},
rr1=Catch[xAct`xTensor`DefManifold[M4,4,{a,b,d,e,f,i,j,k,l}],_,Function[{v,t},{"THROWN",v,t}]];
rr2=Catch[xAct`xTensor`DefMetric[-1,g[-a,-b],CD,{";","D"}],_,Function[{v,t},{"THROWN",v,t}]];
rr3=Catch[xAct`xTensor`DefTensor[uu[a],M4],_,Function[{v,t},{"THROWN",v,t}]];
rr4=Catch[xAct`xTensor`ToCanonical[uu[a]],_,Function[{v,t},{"THROWN",v,t}]];
rr5=Catch[xAct`xTensor`ToCanonical[uu[a]uu[-a]],_,Function[{v,t},{"THROWN",v,t}]];
];Close[msgstream];
ExportString[<|"stages"->ToString[InputForm[{rr1,rr2,rr3,rr4,rr5}]],
"messages"->Import[msgfile,"Text"],
"tensorDeclared"->xAct`xTensor`xTensorQ[uu],
"indexQ"->{xAct`xTensor`AbstractIndexQ[a],xAct`xTensor`AbstractIndexQ[-a]},
"metricList"->ToString[InputForm[xAct`xTensor`$Metrics]],
"xpermSettings"->Names["xAct`xPerm`*$*"],
"canonicalOptions"->ToString[InputForm[Options[xAct`xTensor`ToCanonical]]]|>,"RawJSON"]
]