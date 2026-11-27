Module[{dir, archive, files, xp, pp, base, norm, red, tests},
dir = CreateDirectory[];
archive = FileNameJoin[{dir, "xAct_1.3.0.tgz"}];
URLDownload["https://xact.es/download/xAct_1.3.0.tgz", archive];
files = ExtractArchive[archive, FileNameJoin[{dir, "package"}]];
xp = First[FileNames["xTensor.m", FileNameJoin[{dir, "package"}], Infinity]];
pp = FileNameSplit[xp]; base = FileNameJoin[Take[pp, First[FirstPosition[pp, "xAct"]] - 1]];
PrependTo[$Path, base];
Needs["xAct`xTensor`"];
$DefInfoQ = False;
DefManifold[M4, 4, {a,b,d,e,f,i,j,k,l}];
DefMetric[-1, g[-a,-b], CD, {";","D"}];
DefTensor[uu[a], M4]; DefTensor[ell[a], M4];
DefConstantSymbol[cc]; DefConstantSymbol[ee]; DefConstantSymbol[rr];
norm = Join[MakeRule[{uu[a] uu[-a], -1}, MetricOn->All, ContractMetrics->True], MakeRule[{ell[a] ell[-a], 1}, MetricOn->All, ContractMetrics->True], MakeRule[{uu[a] ell[-a], 0}, MetricOn->All, ContractMetrics->True]];
hp[i_,j_] := g[i,j]+uu[i] uu[j];
red[x_] := ToCanonical[ContractMetric[ToCanonical[Expand[x]]]] //. norm // ToCanonical;
tests = <|"unitTimelike" -> (red[uu[a] uu[-a]] === -1), "projectorOrthogonality" -> (red[hp[a,-b] uu[b]] === 0), "projectorIdempotence" -> (red[hp[a,-b] hp[b,-d]-hp[a,-d]] === 0), "photonNull" -> (red[(uu[a]+ell[a])(uu[-a]+ell[-a])] === 0), "absorptionEnergyProjection" -> (red[-cc uu[-a](ee rr/cc)(uu[a]+ell[a])-ee rr] === 0), "absorptionMomentumProjection" -> (red[hp[a,-b](ee rr/cc)(uu[b]+ell[b])-(ee rr/cc)ell[a]] === 0)|>;
ExportString[<|"kernel"->$Version, "xTensorLoaded"->MemberQ[$Packages,"xAct`xTensor`"], "sourceURL"->"https://xact.es/download/xAct_1.3.0.tgz", "archiveBytes"->FileByteCount[archive], "archiveSHA256"->IntegerString[FileHash[archive,"SHA256"],16,64], "xTensorSHA256"->IntegerString[FileHash[xp,"SHA256"],16,64], "packageVersionSymbols"->Names["xAct`xTensor`*Version*"], "checks"->tests|>,"RawJSON"]
]